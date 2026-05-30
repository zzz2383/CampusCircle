"""
功能：pytest 全局 fixtures 配置

实现逻辑：
    1. 提供测试用的异步数据库会话（内存 SQLite）
    2. 提供测试用的异步 Redis 客户端（fakeredis）
    3. 提供 FastAPI TestClient 用于端到端测试
    4. 每个测试函数自动清理数据
"""

import asyncio
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from fakeredis import FakeServer
from fakeredis.aioredis import FakeRedis
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.infrastructure.db import get_db
from app.models.domain import Base


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环（session 级）"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """创建测试用的内存 SQLite 会话

    每个测试函数独立数据库，测试结束后自动销毁表
    """
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with session_factory() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def fake_redis() -> AsyncGenerator[FakeRedis, None]:
    """创建测试用的 fake Redis 客户端"""
    fake_server = FakeServer()
    redis = FakeRedis(server=fake_server, decode_responses=True)
    yield redis
    await redis.aclose()


@pytest_asyncio.fixture
async def test_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """创建 FastAPI 测试客户端"""
    from app.main import create_app

    app = create_app()

    # 重写数据库依赖
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
