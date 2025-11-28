from fastapi import APIRouter
from .user import router as user_router
from .chat import router as chat_router
from .knowledge import router as knowledge_router
from .ai import router as ai_router
from .category import router as category_router
from .monitor import router as monitor_router
from .upload import router as upload_router

api_router = APIRouter()

api_router.include_router(user_router, prefix="/user", tags=["用户"])
api_router.include_router(chat_router, prefix="/chat", tags=["对话"])
api_router.include_router(knowledge_router, prefix="/knowledge", tags=["知识库"])
api_router.include_router(ai_router, prefix="/ai", tags=["AI"])
api_router.include_router(category_router, prefix="/categories", tags=["分类"])
api_router.include_router(monitor_router, prefix="/monitor", tags=["监控"])
api_router.include_router(upload_router, prefix="/upload", tags=["上传"])
