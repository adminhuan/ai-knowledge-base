from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "知识库API"
    DEBUG: bool = True
    
    # 数据库
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/knowledge_db"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # JWT
    SECRET_KEY: str = "your-secret-key-change-this"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # 智谱AI (聊天 + Embedding + 视觉) - 免费模型
    ZHIPU_API_KEY: str = ""
    ZHIPU_BASE_URL: str = "https://open.bigmodel.cn/api/paas/v4"
    CHAT_MODEL: str = "glm-4.5-flash"
    EMBEDDING_MODEL: str = "embedding-2"
    EMBEDDING_DIMENSION: int = 1024
    VISION_MODELS: str = "glm-4v-flash"
    
    # 通义千问 (联网搜索 + 文件解析)
    QWEN_API_KEY: str = ""
    QWEN_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    QWEN_CHAT_MODEL: str = "qwen-turbo"
    QWEN_DOC_MODEL: str = "qwen-doc-turbo"
    
    # 腾讯云 COS (文件存储)
    COS_SECRET_ID: str = ""
    COS_SECRET_KEY: str = ""
    COS_BUCKET: str = ""
    COS_REGION: str = "ap-guangzhou"
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()
