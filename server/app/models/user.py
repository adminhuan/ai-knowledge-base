from sqlalchemy import Column, Integer, String, DateTime, SmallInteger, Text
from sqlalchemy.sql import func
from app.core.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    nickname = Column(String(64))
    avatar = Column(String(255))
    phone = Column(String(20), index=True)
    email = Column(String(100))
    settings = Column(Text)  # JSON 格式存储用户设置（包括 AI 配置）
    status = Column(SmallInteger, default=1)  # 1:正常 0:禁用
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
