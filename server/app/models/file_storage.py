"""文件存储模型"""
from sqlalchemy import Column, Integer, String, Text, DateTime, SmallInteger, ForeignKey, BigInteger
from sqlalchemy.sql import func
from app.core.database import Base


class FileStorage(Base):
    """文件存储表 - 记录上传到 COS 的文件"""
    __tablename__ = "file_storage"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # 文件信息
    filename = Column(String(255), nullable=False)  # 原始文件名
    file_type = Column(String(20), nullable=False)  # image/document/other
    file_ext = Column(String(10))  # 扩展名
    file_size = Column(BigInteger, default=0)  # 文件大小(字节)
    
    # COS 存储信息
    cos_key = Column(String(500), nullable=False, unique=True)  # COS 对象键
    cos_url = Column(String(1000), nullable=False)  # 访问 URL
    
    # 关联信息
    message_id = Column(Integer, nullable=True)  # 关联的消息ID
    knowledge_id = Column(Integer, ForeignKey("knowledge.id"), nullable=True)  # 关联的知识ID
    
    # 状态
    status = Column(SmallInteger, default=1)  # 1:正常 0:已删除
    is_permanent = Column(SmallInteger, default=1)  # 1:永久 0:临时(3天清理)
    
    # 描述(AI解析结果)
    description = Column(Text)
    
    created_at = Column(DateTime, server_default=func.now(), index=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
