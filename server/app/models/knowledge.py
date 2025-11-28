from sqlalchemy import Column, Integer, String, Text, DateTime, SmallInteger, ForeignKey, JSON
from sqlalchemy.sql import func
from app.core.database import Base
from app.core.config import settings

# pgvector 向量类型
from pgvector.sqlalchemy import Vector
VECTOR_TYPE = Vector(settings.EMBEDDING_DIMENSION)


class Knowledge(Base):
    __tablename__ = "knowledge"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text)
    source = Column(String(50), default="manual", index=True)  # chat/manual/import
    source_id = Column(String(100))
    tags = Column(JSON, default=[])
    embedding = Column(VECTOR_TYPE)  # 向量（需要 pgvector 扩展）
    token_count = Column(Integer, default=0)
    view_count = Column(Integer, default=0)
    is_favorite = Column(SmallInteger, default=0)  # 收藏
    status = Column(SmallInteger, default=1)  # 1:正常 0:已删除
    created_at = Column(DateTime, server_default=func.now(), index=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(50), nullable=False)
    icon = Column(String(20), default="folder")
    color = Column(String(20), default="#07C160")
    count = Column(Integer, default=0)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())


class Tag(Base):
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(50), nullable=False)
    count = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
