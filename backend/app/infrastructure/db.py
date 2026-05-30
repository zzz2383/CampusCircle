"""
功能：SQLite 异步数据库引擎与会话管理

实现逻辑：
    1. 基于 SQLAlchemy 异步引擎（aiosqlite 驱动）创建数据库连接
    2. 使用 async_session_factory 创建异步会话
    3. get_db() 作为 FastAPI 依赖注入的上下文管理器
    4. 自动创建数据目录（如果不存在）

调用链路：
    - 被 data_access/sqlite_dao 层获取数据库会话
    - 被 main.py 中的 lifespan 事件调用初始化/关闭

参数说明：
    settings.DATABASE_URL: SQLite 异步连接字符串

返回值：
    get_db(): AsyncGenerator[AsyncSession, None]
"""

import os
from pathlib import Path
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.infrastructure.config import settings
from app.infrastructure.logger import get_logger

logger = get_logger(__name__)

# 确保数据目录存在
_db_path = settings.DATABASE_URL.replace("sqlite+aiosqlite:///", "")
_db_dir = Path(_db_path).parent
if not _db_dir.exists():
    os.makedirs(_db_dir, exist_ok=True)
    logger.info(f"Created database directory: {_db_dir}")

# 异步引擎
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    connect_args={"check_same_thread": False},
)

# 会话工厂
async_session_factory = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI 依赖注入：获取数据库会话

    实现逻辑：
        1. 从 async_session_factory 创建新会话
        2. 请求完成后自动关闭会话

    调用链路：
        - 被 FastAPI 路由的 Depends() 使用
        - 被 DAO 层通过参数注入使用

    测试用例：
        - test_get_db_success
    """
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """初始化数据库：创建所有表

    实现逻辑：
        1. 导入所有 ORM 模型以确保它们被 Base 元数据注册
        2. 调用 Base.metadata.create_all() 创建表

    调用链路：
        - 被 main.py lifespan 事件调用
    """
    from app.models.domain import Base

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created successfully")


async def close_db():
    """关闭数据库引擎"""
    await async_engine.dispose()
    logger.info("Database engine disposed")
