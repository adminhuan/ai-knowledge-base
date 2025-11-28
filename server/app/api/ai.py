from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.services.ai_service import ai_service

router = APIRouter()


class ContentRequest(BaseModel):
    content: str


class SearchRequest(BaseModel):
    query: str


@router.post("/summarize")
async def summarize(
    data: ContentRequest,
    user_id: int = Depends(get_current_user_id)
):
    """AI总结内容"""
    result = await ai_service.summarize(data.content)
    return {"code": 0, "data": result}


@router.post("/generate-tags")
async def generate_tags(
    data: ContentRequest,
    user_id: int = Depends(get_current_user_id)
):
    """AI生成标签"""
    tags = await ai_service.generate_tags(data.content)
    return {"code": 0, "data": {"tags": tags}}


@router.post("/search")
async def ai_search(
    data: SearchRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """AI语义搜索"""
    results = await ai_service.search_knowledge(db, user_id, data.query)
    return {"code": 0, "data": results}
