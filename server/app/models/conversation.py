from sqlalchemy import Column, Integer, String, Text, DateTime, SmallInteger, ForeignKey, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(255), default="新对话")
    last_message = Column(Text)
    message_count = Column(Integer, default=0)
    status = Column(SmallInteger, default=1)  # 1:正常 0:已删除
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String(20), nullable=False)  # user/assistant/system
    content = Column(Text, nullable=False)
    tokens_used = Column(Integer, default=0)
    input_tokens = Column(Integer, default=0)  # 输入token
    output_tokens = Column(Integer, default=0)  # 输出token
    cached_tokens = Column(Integer, default=0)  # 缓存命中token
    model_name = Column(String(100))  # 使用的模型名称
    provider = Column(String(50))  # 服务商（zhipu/qwen/deepseek等）
    cost = Column(Integer, default=0)  # 成本（单位：0.0001元，即万分之一元）
    extra_data = Column(JSON)  # 扩展字段（引用的知识ID、AI模型信息等）
    created_at = Column(DateTime, server_default=func.now(), index=True)
