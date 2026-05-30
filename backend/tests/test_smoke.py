"""
冒烟测试：验证项目基础设施可正常运行
"""

import pytest
from sqlalchemy import text


@pytest.mark.asyncio
async def test_db_session_works(db_session):
    """验证数据库会话可正常执行查询"""
    result = await db_session.execute(text("SELECT 1"))
    assert result.scalar() == 1


@pytest.mark.asyncio
async def test_fake_redis_works(fake_redis):
    """验证 fake Redis 可正常操作"""
    await fake_redis.set("test_key", "test_value")
    value = await fake_redis.get("test_key")
    assert value == "test_value"


@pytest.mark.asyncio
async def test_config_loaded():
    """验证配置加载正常"""
    from app.infrastructure.config import settings

    assert settings.APP_NAME == "CampusCircle"
    assert settings.DEBUG is True
