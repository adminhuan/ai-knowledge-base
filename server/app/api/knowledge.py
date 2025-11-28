from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, or_, text
from pydantic import BaseModel
from typing import Optional, List

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.models.knowledge import Knowledge, Category
from app.services.ai_service import ai_service

router = APIRouter()


class KnowledgeCreate(BaseModel):
    title: str
    content: str
    summary: Optional[str] = None
    source: Optional[str] = "manual"
    tags: Optional[List[str]] = []
    category_id: Optional[int] = None


class KnowledgeUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    tags: Optional[List[str]] = None
    category_id: Optional[int] = None


class SearchRequest(BaseModel):
    query: Optional[str] = None
    keyword: Optional[str] = None
    type: Optional[str] = "semantic"  # semantic / keyword


@router.get("")
async def get_knowledge_list(
    category: Optional[str] = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """获取知识列表"""
    query = select(Knowledge).where(Knowledge.user_id == user_id, Knowledge.status == 1)
    
    if category and category != "all":
        if category == "favorites":
            query = query.where(Knowledge.is_favorite == 1)
        elif category == "uncategorized":
            query = query.where(Knowledge.category_id.is_(None))
        elif category.isdigit():
            query = query.where(Knowledge.category_id == int(category))
        else:
            query = query.where(Knowledge.source == category)
    
    query = query.order_by(Knowledge.created_at.desc()).offset((page - 1) * size).limit(size)
    
    result = await db.execute(query)
    items = result.scalars().all()
    
    return {
        "code": 0,
        "data": [
            {
                "id": k.id,
                "title": k.title,
                "summary": k.summary or (k.content[:100] + "..." if len(k.content) > 100 else k.content),
                "source": k.source,
                "tags": k.tags or [],
                "createdAt": k.created_at.isoformat() if k.created_at else None
            }
            for k in items
        ]
    }


@router.get("/{knowledge_id}")
async def get_knowledge_detail(
    knowledge_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """获取知识详情"""
    result = await db.execute(
        select(Knowledge).where(
            Knowledge.id == knowledge_id,
            Knowledge.user_id == user_id,
            Knowledge.status == 1
        )
    )
    knowledge = result.scalar_one_or_none()
    
    if not knowledge:
        raise HTTPException(status_code=404, detail="知识不存在")
    
    # 更新浏览次数
    await db.execute(
        update(Knowledge).where(Knowledge.id == knowledge_id).values(view_count=Knowledge.view_count + 1)
    )
    await db.commit()
    
    return {
        "code": 0,
        "data": {
            "id": knowledge.id,
            "title": knowledge.title,
            "content": knowledge.content,
            "summary": knowledge.summary,
            "source": knowledge.source,
            "tags": knowledge.tags or [],
            "is_favorite": knowledge.is_favorite,
            "createdAt": knowledge.created_at.strftime("%Y-%m-%d") if knowledge.created_at else None
        }
    }


@router.post("")
async def create_knowledge(
    data: KnowledgeCreate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """创建知识"""
    # 生成向量
    embedding = await ai_service.get_embedding(data.title + " " + data.content)
    
    knowledge = Knowledge(
        user_id=user_id,
        title=data.title,
        content=data.content,
        summary=data.summary,
        source=data.source,
        tags=data.tags,
        category_id=data.category_id,
        embedding=embedding,
        token_count=len(data.content)
    )
    db.add(knowledge)
    await db.commit()
    await db.refresh(knowledge)
    
    return {"code": 0, "data": {"id": knowledge.id}, "message": "创建成功"}


@router.put("/{knowledge_id}")
async def update_knowledge(
    knowledge_id: int,
    data: KnowledgeUpdate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """更新知识"""
    update_data = data.dict(exclude_unset=True)
    
    # 如果内容变化，重新生成向量
    if "content" in update_data or "title" in update_data:
        result = await db.execute(select(Knowledge).where(Knowledge.id == knowledge_id))
        knowledge = result.scalar_one_or_none()
        if knowledge:
            new_title = update_data.get("title", knowledge.title)
            new_content = update_data.get("content", knowledge.content)
            update_data["embedding"] = await ai_service.get_embedding(new_title + " " + new_content)
    
    await db.execute(
        update(Knowledge)
        .where(Knowledge.id == knowledge_id, Knowledge.user_id == user_id)
        .values(**update_data)
    )
    await db.commit()
    
    return {"code": 0, "message": "更新成功"}


@router.delete("/{knowledge_id}")
async def delete_knowledge(
    knowledge_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """删除知识"""
    await db.execute(
        update(Knowledge)
        .where(Knowledge.id == knowledge_id, Knowledge.user_id == user_id)
        .values(status=0)
    )
    await db.commit()
    
    return {"code": 0, "message": "删除成功"}


@router.post("/search")
async def search_knowledge(
    data: SearchRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """搜索知识"""
    keyword = data.query or data.keyword
    if not keyword:
        return {"code": 0, "data": []}
    
    # 直接搜索（向量 + 关键词）
    results = await ai_service.search_knowledge(db, user_id, keyword, limit=10)
    
    return {
        "code": 0,
        "data": [
            {
                "id": r["id"],
                "title": r["title"],
                "content": r["content"],
                "similarity": r.get("similarity", 0)
            }
            for r in results
        ]
    }


@router.post("/{knowledge_id}/favorite")
async def toggle_favorite(
    knowledge_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """收藏/取消收藏"""
    result = await db.execute(
        select(Knowledge).where(Knowledge.id == knowledge_id, Knowledge.user_id == user_id)
    )
    knowledge = result.scalar_one_or_none()
    
    if not knowledge:
        raise HTTPException(status_code=404, detail="知识不存在")
    
    new_status = 0 if knowledge.is_favorite else 1
    await db.execute(
        update(Knowledge).where(Knowledge.id == knowledge_id).values(is_favorite=new_status)
    )
    await db.commit()
    
    return {"code": 0, "data": {"is_favorite": new_status}}


@router.post("/from-chat")
async def create_from_chat(
    data: KnowledgeCreate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """从聊天创建知识"""
    data.source = "chat"
    return await create_knowledge(data, user_id, db)
