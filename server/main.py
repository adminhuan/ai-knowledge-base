from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import os

from app.core.config import settings
from app.core.database import init_db
from app.core.redis import redis_client
from app.core.security_middleware import SecurityMiddleware
from app.api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时
    await redis_client.connect()
    await init_db()
    print("✅ 数据库和Redis连接成功")
    print("🛡️ 安全防护已启用")
    yield
    # 关闭时
    await redis_client.close()
    print("👋 服务已关闭")


app = FastAPI(
    title=settings.APP_NAME,
    description="知识库API - 支持AI对话、知识检索、智能总结",
    version="1.0.0",
    lifespan=lifespan
)

# 安全中间件（放在 CORS 之前）
app.add_middleware(SecurityMiddleware)

# CORS配置（生产环境请配置具体域名）
ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', '*').split(',')
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS if ALLOWED_ORIGINS != ['*'] else ["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# 验证错误处理器（打印详细错误）
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print(f"[VALIDATION ERROR] URL: {request.url}")
    print(f"[VALIDATION ERROR] Errors: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )

# 注册路由
app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=3000, reload=True)
