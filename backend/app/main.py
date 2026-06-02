"""
功能：FastAPI 应用入口

实现逻辑：
    1. 使用应用工厂函数 create_app() 创建 FastAPI 实例
    2. 注册 CORS 中间件（支持前端跨域请求）
    3. 注册所有路由
    4. 注册全局异常处理器（统一错误响应格式）
    5. lifespan 事件管理数据库和 Redis 连接生命周期

调用链路：
    - uvicorn 启动入口：uvicorn app.main:app --reload
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.infrastructure.config import settings
from app.infrastructure.exceptions import AppException
from app.infrastructure.logger import get_logger
from app.infrastructure.db import init_db, close_db
from app.infrastructure.redis_client import get_redis, close_redis
from app.presentation.api import auth, posts, likes, rank, notifications, comments, clubs, events
from app.presentation.websocket.handler import websocket_handler

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """应用生命周期管理

    启动时：
        1. 初始化数据库（建表）
        2. 建立 Redis 连接

    关闭时：
        1. 关闭 Redis 连接
        2. 关闭数据库引擎
    """
    logger.info(f"Starting {settings.APP_NAME}...")
    await init_db()
    logger.info("Database initialized")

    try:
        redis = await get_redis()
        await redis.ping()
        logger.info("Redis connected")
    except Exception as e:
        logger.warning(f"Redis not available: {e}")

    yield

    await close_redis()
    await close_db()
    logger.info(f"{settings.APP_NAME} shutdown complete")


def create_app() -> FastAPI:
    """应用工厂函数"""
    app = FastAPI(
        title=settings.APP_NAME,
        description="校园实时论坛系统 API",
        version="0.1.0",
        lifespan=lifespan,
    )

    # CORS 配置
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册路由
    app.include_router(auth.router)
    app.include_router(posts.router)
    app.include_router(likes.router)
    app.include_router(rank.router)
    app.include_router(notifications.router)
    app.include_router(comments.router)
    app.include_router(clubs.router)
    app.include_router(events.router)

    # WebSocket
    from fastapi import Query
    @app.websocket("/ws")
    async def ws_endpoint(websocket, token: str = Query(...)):
        await websocket_handler(websocket, token=token)

    # 全局异常处理器
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": exc.code,
                "message": exc.message,
                "detail": None,
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.exception(f"Unhandled exception: {exc}")
        return JSONResponse(
            status_code=500,
            content={
                "code": "INTERNAL_ERROR",
                "message": "服务器内部错误",
                "detail": str(exc) if settings.DEBUG else None,
            },
        )

    # 根路径
    @app.get("/")
    async def root():
        return {
            "name": settings.APP_NAME,
            "version": "0.1.0",
            "docs": "/docs",
        }

    return app


app = create_app()
