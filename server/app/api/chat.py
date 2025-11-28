from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from pydantic import BaseModel
from typing import Optional, List
import re

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.models.conversation import Conversation, Message
from app.models.knowledge import Knowledge
from app.services.ai_service import ai_service

# 保存指令（必须是短消息且主要是保存意图）
SAVE_COMMANDS = [
    '保存', '存一下', '存下', '记一下', '记下', '收藏', '入库', 
    '帮我存', '帮我保存', '帮忙保存', '帮忙存', '存到知识库', 
    '保存到知识库', '存入知识库', '这个保存', '保存这个',
    '记录一下', '记录下来', '存下来', '保存下来'
]

router = APIRouter()


class ConversationCreate(BaseModel):
    title: Optional[str] = "新对话"


class ChatMessage(BaseModel):
    conversationId: Optional[int] = None
    message: str
    webSearch: Optional[bool] = False
    saveOnly: Optional[bool] = False  # 只保存到上下文，不调用AI
    aiReply: Optional[str] = None  # 文件解析时，同时保存AI回复
    fileUrl: Optional[str] = None  # 文件/图片的 COS URL
    fileType: Optional[str] = None  # 文件类型：image/document


class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    created_at: str


@router.get("/conversations")
async def get_conversations(
    user_id: int = Depends(get_current_user_id), 
    db: AsyncSession = Depends(get_db)
):
    """获取会话列表"""
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == user_id, Conversation.status == 1)
        .order_by(Conversation.updated_at.desc())
        .limit(50)
    )
    conversations = result.scalars().all()
    
    return {
        "code": 0,
        "data": [
            {
                "id": c.id,
                "title": c.title,
                "lastMessage": c.last_message or "",
                "updatedAt": c.updated_at.isoformat() if c.updated_at else None
            }
            for c in conversations
        ]
    }


@router.post("/conversations")
async def create_conversation(
    data: ConversationCreate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """创建会话"""
    conversation = Conversation(
        user_id=user_id,
        title=data.title
    )
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)
    
    return {"code": 0, "data": {"id": conversation.id}}


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """删除会话"""
    await db.execute(
        update(Conversation)
        .where(Conversation.id == conversation_id, Conversation.user_id == user_id)
        .values(status=0)
    )
    await db.commit()
    
    return {"code": 0, "message": "删除成功"}


@router.delete("/messages/{message_id}")
async def delete_message(
    message_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """删除单条消息"""
    from sqlalchemy import delete
    result = await db.execute(
        delete(Message)
        .where(Message.id == message_id, Message.user_id == user_id)
    )
    await db.commit()
    
    if result.rowcount > 0:
        return {"code": 0, "message": "删除成功"}
    else:
        return {"code": -1, "message": "消息不存在或无权限"}


class UpdateMessageFile(BaseModel):
    fileUrl: str
    fileType: str = "image"


@router.put("/messages/{message_id}/file")
async def update_message_file(
    message_id: int,
    data: UpdateMessageFile,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """更新消息的文件URL（上传云端后调用）"""
    result = await db.execute(
        select(Message).where(Message.id == message_id, Message.user_id == user_id)
    )
    message = result.scalar_one_or_none()
    
    if not message:
        return {"code": -1, "message": "消息不存在"}
    
    # 更新 extra_data
    extra_data = message.extra_data or {}
    extra_data["fileUrl"] = data.fileUrl
    extra_data["fileType"] = data.fileType
    message.extra_data = extra_data
    
    await db.commit()
    return {"code": 0, "message": "更新成功"}


@router.get("/conversations/{conversation_id}/messages")
async def get_messages(
    conversation_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """获取会话消息（分页，按时间升序返回）"""
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
    )
    rows = result.scalars().all()

    messages = list(reversed(rows))  # 转为时间升序

    return {
        "code": 0,
        "data": [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "references": m.extra_data.get("references", []) if m.extra_data else [],
                "fileUrl": m.extra_data.get("fileUrl") if m.extra_data else None,
                "fileType": m.extra_data.get("fileType") if m.extra_data else None
            }
            for m in messages
        ],
        "hasMore": len(rows) == size  # 可能还有更多
    }


def check_save_intent(message: str) -> dict:
    """
    检查消息是否是保存指令，返回解析结果
    返回: {"is_save": bool, "type": str, "content": str}
    - type: "specific" (有具体内容), "vague" (模糊指令), "last_reply" (保存上一条)
    """
    import re
    msg = message.strip()
    
    # 检查是否包含保存关键词
    save_keywords = ['保存', '记录', '记住', '存一下', '存下', '储存']
    has_save_keyword = any(kw in msg for kw in save_keywords)
    
    if not has_save_keyword:
        return {"is_save": False, "type": None, "content": None}
    
    # 包含查询相关词，不是保存指令
    query_words = ['查', '找', '搜', '问', '什么', '怎么', '如何', '哪', '吗', '？', '?']
    if any(word in msg for word in query_words):
        return {"is_save": False, "type": None, "content": None}
    
    # 模式1: "帮我保存：xxx" 或 "保存：xxx" - 有具体内容
    match = re.search(r'(?:帮我)?(?:保存|记录|记住|储存)[：:]\s*(.+)', msg, re.DOTALL)
    if match:
        content = match.group(1).strip()
        if content and len(content) > 2:  # 内容足够长
            return {"is_save": True, "type": "specific", "content": content}
    
    # 模式2: 模糊指令 - "保存以上内容"、"帮我记录这个"、"把这个存下"
    vague_patterns = ['以上', '这个', '这些', '那个', '上面', '刚才', '这段']
    if any(p in msg for p in vague_patterns):
        return {"is_save": True, "type": "vague", "content": None}
    
    # 模式3: 简单保存指令 - "保存"、"帮我保存"、"保存上条"
    last_reply_cmds = ['保存上条', '保存上一条', '存上条', '存上一条']
    if any(cmd in msg for cmd in last_reply_cmds):
        return {"is_save": True, "type": "last_reply", "content": None}
    
    if len(msg) <= 15:
        for cmd in SAVE_COMMANDS:
            if cmd in msg:
                return {"is_save": True, "type": "last_reply", "content": None}
    
    return {"is_save": False, "type": None, "content": None}


@router.post("")
async def chat(
    data: ChatMessage,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """发送消息（AI对话）"""
    conversation_id = data.conversationId
    
    # 如果没有会话ID，创建新会话
    if not conversation_id:
        conversation = Conversation(user_id=user_id, title="新对话")
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)
        conversation_id = conversation.id
    
    # 检查是否是保存指令
    save_intent = check_save_intent(data.message)
    if save_intent["is_save"]:
        content_to_save = None
        save_title = None
        reply = None
        
        if save_intent["type"] == "specific":
            # 有具体内容，直接保存
            content_to_save = save_intent["content"]
            save_title = content_to_save[:50] + "..." if len(content_to_save) > 50 else content_to_save
            
        elif save_intent["type"] == "vague":
            # 模糊指令，询问用户
            reply = """请问您要保存什么内容？
1. 上一条 AI 回复 - 回复"保存上条"
2. 选择聊天记录 - 长按消息进入多选，选好后点"存知识库"
3. 指定内容 - 回复"保存：你要保存的具体内容"

请告诉我您的选择~"""
            
        elif save_intent["type"] == "last_reply":
            # 保存上一条 AI 回复
            result = await db.execute(
                select(Message)
                .where(
                    Message.conversation_id == conversation_id,
                    Message.role == "assistant"
                )
                .order_by(Message.created_at.desc())
                .limit(1)
            )
            last_ai_message = result.scalar_one_or_none()
            if last_ai_message:
                content_to_save = last_ai_message.content
                save_title = content_to_save[:50] + "..." if len(content_to_save) > 50 else content_to_save
            else:
                reply = "没有找到可保存的内容，请先和我聊天~"
        
        # 如果是询问用户，直接返回
        if reply and not content_to_save:
            user_message = Message(conversation_id=conversation_id, user_id=user_id, role="user", content=data.message)
            ai_message = Message(conversation_id=conversation_id, user_id=user_id, role="assistant", content=reply)
            db.add(user_message)
            db.add(ai_message)
            await db.commit()
            return {"code": 0, "data": {"conversationId": conversation_id, "reply": reply, "references": []}}
        
        # 保存到知识库
        if content_to_save:
            try:
                embedding = await ai_service.get_embedding(content_to_save[:1000])
                knowledge = Knowledge(
                    user_id=user_id,
                    title=save_title,
                    content=content_to_save,
                    source="chat",
                    tags=["AI对话"],
                    embedding=embedding
                )
                db.add(knowledge)
                
                user_message = Message(conversation_id=conversation_id, user_id=user_id, role="user", content=data.message)
                reply = f"已保存到知识库！\n内容：{save_title}"
                ai_message = Message(conversation_id=conversation_id, user_id=user_id, role="assistant", content=reply)
                db.add(user_message)
                db.add(ai_message)
                await db.commit()
                
                return {"code": 0, "data": {"conversationId": conversation_id, "reply": reply, "references": []}}
            except Exception as e:
                print(f"保存知识库失败: {e}")
        
        # 如果没有上一条消息，提示用户
        reply = "没有找到可保存的内容"
        user_message = Message(
            conversation_id=conversation_id,
            user_id=user_id,
            role="user",
            content=data.message
        )
        db.add(user_message)
        ai_message = Message(
            conversation_id=conversation_id,
            user_id=user_id,
            role="assistant",
            content=reply
        )
        db.add(ai_message)
        await db.commit()
        
        return {
            "code": 0,
            "data": {
                "conversationId": conversation_id,
                "reply": reply,
                "references": []
            }
        }
    
    # 保存用户消息（如果有文件，存到 extra_data）
    extra_data = None
    if data.fileUrl:
        extra_data = {
            "fileUrl": data.fileUrl,
            "fileType": data.fileType or "image"
        }
    
    user_message = Message(
        conversation_id=conversation_id,
        user_id=user_id,
        role="user",
        content=data.message,
        extra_data=extra_data
    )
    db.add(user_message)
    
    # 如果只保存（用于文件解析记录），不调用AI
    if data.saveOnly:
        # 保存到 Redis 上下文
        from app.core.redis import redis_client
        await redis_client.add_chat_message(user_id, conversation_id, {
            "role": "user",
            "content": data.message
        })
        
        # 如果有AI回复，也保存AI消息
        if data.aiReply:
            ai_message = Message(
                conversation_id=conversation_id,
                user_id=user_id,
                role="assistant",
                content=data.aiReply
            )
            db.add(ai_message)
            await redis_client.add_chat_message(user_id, conversation_id, {
                "role": "assistant",
                "content": data.aiReply
            })
        
        # 同时保存到数据库（这样页面刷新后消息不会丢失）
        await db.flush()  # 获取消息ID
        user_msg_id = user_message.id
        await db.commit()
        
        return {
            "code": 0,
            "data": {
                "conversationId": conversation_id,
                "userMessageId": user_msg_id,
                "reply": data.aiReply or "",
                "references": []
            }
        }
    
    # 调用AI服务
    ai_response = await ai_service.chat(
        db=db,
        user_id=user_id,
        conversation_id=conversation_id,
        message=data.message,
        web_search=data.webSearch or False
    )
    
    # 保存AI回复（含详细统计）
    ai_message = Message(
        conversation_id=conversation_id,
        user_id=user_id,
        role="assistant",
        content=ai_response["reply"],
        tokens_used=ai_response.get("tokens_used", 0),
        input_tokens=ai_response.get("input_tokens", 0),
        output_tokens=ai_response.get("output_tokens", 0),
        cached_tokens=ai_response.get("cached_tokens", 0),
        model_name=ai_response.get("model_name", ""),
        provider=ai_response.get("provider", ""),
        cost=ai_response.get("cost", 0),
        extra_data={"references": ai_response.get("references", [])}
    )
    db.add(ai_message)
    
    # 更新会话
    await db.execute(
        update(Conversation)
        .where(Conversation.id == conversation_id)
        .values(
            last_message=ai_response["reply"][:100],
            message_count=Conversation.message_count + 2
        )
    )
    
    await db.commit()
    
    return {
        "code": 0,
        "data": {
            "conversationId": conversation_id,
            "reply": ai_response["reply"],
            "references": ai_response.get("references", [])
        }
    }
