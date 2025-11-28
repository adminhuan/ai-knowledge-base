from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token, get_current_user_id
from app.core.security_middleware import record_login_attempt, get_client_ip
from app.models.user import User
from app.models.knowledge import Knowledge
from app.models.conversation import Conversation, Message

router = APIRouter()


class UserCreate(BaseModel):
    username: str
    password: str
    nickname: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    username: str
    nickname: Optional[str]
    avatar: Optional[str]
    
    class Config:
        from_attributes = True


class StatsResponse(BaseModel):
    knowledge: int
    conversation: int
    aiCalls: int


class AIConfigUpdate(BaseModel):
    # 聊天AI
    chat_provider: Optional[str] = None
    chat_base_url: Optional[str] = None
    chat_api_key: Optional[str] = None
    chat_model: Optional[str] = None
    # 联网搜索AI
    search_provider: Optional[str] = None
    search_base_url: Optional[str] = None
    search_api_key: Optional[str] = None
    search_model: Optional[str] = None
    # Embedding
    embedding_provider: Optional[str] = None
    embedding_base_url: Optional[str] = None
    embedding_api_key: Optional[str] = None
    embedding_model: Optional[str] = None
    embedding_dimension: Optional[int] = 1024
    # 文件解析AI (qwen-doc-turbo)
    file_provider: Optional[str] = None
    file_base_url: Optional[str] = None
    file_api_key: Optional[str] = None
    file_model: Optional[str] = None
    # 视觉/图片识别AI (GLM-4V-Flash / GLM-4.1V-Thinking-Flash)
    vision_provider: Optional[str] = None
    vision_base_url: Optional[str] = None
    vision_api_key: Optional[str] = None
    vision_models: Optional[str] = None  # 逗号分隔的模型列表，用于轮换
    # 通用设置
    system_prompt: Optional[str] = None
    enable_rag: Optional[bool] = True


@router.post("/register")
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """用户注册"""
    # 检查用户名是否存在
    result = await db.execute(select(User).where(User.username == user.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    new_user = User(
        username=user.username,
        password_hash=get_password_hash(user.password),
        nickname=user.nickname or user.username
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return {"code": 0, "message": "注册成功", "data": {"id": new_user.id}}


@router.post("/login")
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """用户登录"""
    ip = get_client_ip(request)
    
    result = await db.execute(select(User).where(User.username == form_data.username))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(form_data.password, user.password_hash):
        # 记录登录失败
        record_login_attempt(ip, success=False)
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    if user.status != 1:
        raise HTTPException(status_code=403, detail="账号已被禁用")
    
    # 登录成功，清除失败记录
    record_login_attempt(ip, success=True)
    
    token = create_access_token(data={"sub": str(user.id)})
    
    return {
        "code": 0,
        "data": {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "username": user.username,
                "nickname": user.nickname
            }
        }
    }


@router.get("/info")
async def get_user_info(user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    """获取用户信息"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 获取知识数量
    knowledge_count = await db.scalar(
        select(func.count()).select_from(Knowledge).where(Knowledge.user_id == user_id, Knowledge.status == 1)
    )
    
    return {
        "code": 0,
        "data": {
            "id": user.id,
            "username": user.username,
            "name": user.nickname or user.username,
            "nickname": user.nickname,
            "avatar": user.avatar,
            "desc": f"累计收集 {knowledge_count} 条知识"
        }
    }


@router.get("/stats")
async def get_stats(user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    """获取统计数据"""
    knowledge_count = await db.scalar(
        select(func.count()).select_from(Knowledge).where(Knowledge.user_id == user_id, Knowledge.status == 1)
    )
    
    conversation_count = await db.scalar(
        select(func.count()).select_from(Conversation).where(Conversation.user_id == user_id, Conversation.status == 1)
    )
    
    message_count = await db.scalar(
        select(func.count()).select_from(Message).where(Message.user_id == user_id, Message.role == "assistant")
    )
    
    return {
        "code": 0,
        "data": {
            "knowledge": knowledge_count or 0,
            "conversation": conversation_count or 0,
            "aiCalls": message_count or 0
        }
    }


@router.post("/ai-config")
async def save_ai_config(config: AIConfigUpdate, user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    """保存用户 AI 配置"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 保存到用户的 settings 字段
    import json
    current_settings = {}
    if user.settings:
        try:
            current_settings = json.loads(user.settings) if isinstance(user.settings, str) else user.settings
        except:
            current_settings = {}
    
    current_settings['ai_config'] = config.dict()
    user.settings = json.dumps(current_settings)
    
    await db.commit()
    
    return {"code": 0, "message": "配置已保存"}


@router.get("/ai-config")
async def get_ai_config(user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    """获取用户 AI 配置"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    import json
    ai_config = {}
    if user.settings:
        try:
            settings = json.loads(user.settings) if isinstance(user.settings, str) else user.settings
            ai_config = settings.get('ai_config', {})
        except:
            pass
    
    return {"code": 0, "data": ai_config}


@router.get("/ai-usage")
async def get_ai_usage(
    days: int = 1,
    user_id: int = Depends(get_current_user_id), 
    db: AsyncSession = Depends(get_db)
):
    """获取AI调用使用情况（支持查询多天）"""
    # 计算时间范围（naive datetime，与数据库一致）
    now = datetime.utcnow()
    start_date = (now - timedelta(days=days-1)).replace(hour=0, minute=0, second=0, microsecond=0)
    
    # 总体统计
    total_result = await db.execute(
        select(
            func.count().label("calls"),
            func.coalesce(func.sum(Message.tokens_used), 0).label("tokens"),
            func.coalesce(func.sum(Message.input_tokens), 0).label("input_tokens"),
            func.coalesce(func.sum(Message.output_tokens), 0).label("output_tokens"),
            func.coalesce(func.sum(Message.cached_tokens), 0).label("cached_tokens"),
            func.coalesce(func.sum(Message.cost), 0).label("cost")
        )
        .where(
            Message.user_id == user_id,
            Message.role == "assistant",
            Message.created_at >= start_date
        )
    )
    total_row = total_result.first()
    
    # 按模型分组统计
    model_result = await db.execute(
        select(
            Message.model_name,
            Message.provider,
            func.count().label("calls"),
            func.coalesce(func.sum(Message.tokens_used), 0).label("tokens"),
            func.coalesce(func.sum(Message.input_tokens), 0).label("input_tokens"),
            func.coalesce(func.sum(Message.output_tokens), 0).label("output_tokens"),
            func.coalesce(func.sum(Message.cached_tokens), 0).label("cached_tokens"),
            func.coalesce(func.sum(Message.cost), 0).label("cost")
        )
        .where(
            Message.user_id == user_id,
            Message.role == "assistant",
            Message.created_at >= start_date
        )
        .group_by(Message.model_name, Message.provider)
        .order_by(func.count().desc())
    )
    model_rows = model_result.fetchall()
    
    # 构建模型列表
    models = []
    for row in model_rows:
        model_name = row.model_name or "未知模型"
        provider = row.provider or "unknown"
        models.append({
            "model": model_name,
            "provider": provider,
            "calls": row.calls or 0,
            "tokens": row.tokens or 0,
            "inputTokens": row.input_tokens or 0,
            "outputTokens": row.output_tokens or 0,
            "cachedTokens": row.cached_tokens or 0,
            "cost": round((row.cost or 0) / 10000, 4)  # 转换为元
        })
    
    # 如果没有数据，添加默认空项
    if not models:
        models = []
    
    return {
        "code": 0,
        "data": {
            "period": f"近{days}天" if days > 1 else "今日",
            "summary": {
                "calls": total_row.calls or 0,
                "tokens": total_row.tokens or 0,
                "inputTokens": total_row.input_tokens or 0,
                "outputTokens": total_row.output_tokens or 0,
                "cachedTokens": total_row.cached_tokens or 0,
                "cost": round((total_row.cost or 0) / 10000, 4)  # 转换为元
            },
            "models": models
        }
    }


class UpdateProfile(BaseModel):
    username: Optional[str] = None
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    
    class Config:
        extra = 'ignore'  # 忽略额外字段


class ChangePassword(BaseModel):
    old_password: str
    new_password: str
    
    class Config:
        extra = 'ignore'


@router.post("/profile")
async def update_profile(
    data: UpdateProfile,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """更新用户资料（用户名、昵称、头像）"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 修改用户名需要检查是否重复
    if data.username is not None and data.username != user.username:
        existing = await db.execute(select(User).where(User.username == data.username))
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="用户名已存在")
        user.username = data.username
    
    if data.nickname is not None:
        user.nickname = data.nickname
    if data.avatar is not None:
        user.avatar = data.avatar
    
    await db.commit()
    
    return {
        "code": 0,
        "message": "更新成功",
        "data": {
            "nickname": user.nickname,
            "avatar": user.avatar
        }
    }


@router.post("/password")
async def change_password(data: ChangePassword, user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    """修改密码"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 验证旧密码
    if not verify_password(data.old_password, user.password_hash):
        raise HTTPException(status_code=400, detail="原密码错误")
    
    # 检查新密码长度
    if len(data.new_password) < 6:
        raise HTTPException(status_code=400, detail="新密码长度至少6位")
    
    # 更新密码
    user.password_hash = get_password_hash(data.new_password)
    await db.commit()
    
    return {"code": 0, "message": "密码修改成功"}
