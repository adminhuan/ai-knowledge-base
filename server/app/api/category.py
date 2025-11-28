from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from pydantic import BaseModel
from typing import Optional

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.models.knowledge import Category, Knowledge

router = APIRouter()


class CategoryCreate(BaseModel):
    name: str
    icon: Optional[str] = "folder"
    color: Optional[str] = "#07C160"
    sort_order: Optional[int] = 0


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    sort_order: Optional[int] = None


@router.get("")
async def list_categories(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """获取分类列表"""
    count_result = await db.execute(
        select(Knowledge.category_id, func.count().label("cnt"))
        .where(Knowledge.user_id == user_id, Knowledge.status == 1)
        .group_by(Knowledge.category_id)
    )
    count_map = {row[0]: row[1] for row in count_result.all() if row[0] is not None}

    result = await db.execute(
        select(Category)
        .where(Category.user_id == user_id)
        .order_by(Category.sort_order.desc(), Category.created_at.desc())
    )
    items = result.scalars().all()
    return {
        "code": 0,
        "data": [
            {
                "id": c.id,
            "name": c.name,
            "icon": c.icon,
            "color": c.color,
            "sortOrder": c.sort_order or 0,
            "count": count_map.get(c.id, c.count or 0),
        }
        for c in items
    ],
    }


@router.post("")
async def create_category(
    data: CategoryCreate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """创建分类"""
    category = Category(
        user_id=user_id,
        name=data.name,
        icon=data.icon or "folder",
        color=data.color or "#07C160",
        sort_order=data.sort_order or 0,
    )
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return {"code": 0, "data": {"id": category.id}}


@router.put("/{category_id}")
async def update_category(
    category_id: int,
    data: CategoryUpdate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """更新分类"""
    result = await db.execute(
        select(Category).where(Category.id == category_id, Category.user_id == user_id)
    )
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")

    update_data = data.dict(exclude_unset=True)
    await db.execute(
        update(Category)
        .where(Category.id == category_id, Category.user_id == user_id)
        .values(
            name=update_data.get("name", category.name),
            icon=update_data.get("icon", category.icon),
            color=update_data.get("color", category.color),
            sort_order=update_data.get("sort_order", category.sort_order),
        )
    )
    await db.commit()
    return {"code": 0, "message": "更新成功"}


@router.delete("/{category_id}")
async def delete_category(
    category_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """删除分类"""
    result = await db.execute(
        select(Category).where(Category.id == category_id, Category.user_id == user_id)
    )
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")

    await db.execute(
        update(Category)
        .where(Category.id == category_id, Category.user_id == user_id)
        .values(name=f"{category.name}-已删除", sort_order=-1)
    )
    await db.commit()
    return {"code": 0, "message": "删除成功"}
