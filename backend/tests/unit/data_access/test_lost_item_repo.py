"""LostItemRepository 单元测试"""
import pytest
from app.data_access.redis_repo.lost_item_repo_impl import LostItemRepositoryImpl


@pytest.mark.asyncio
async def test_set_expiry_success(fake_redis):
    repo = LostItemRepositoryImpl(fake_redis)
    await repo.set_expiry(item_id=1)
    key = "lost:item:1"
    ttl = await fake_redis.ttl(key)
    assert 0 < ttl <= 604800
    val = await fake_redis.get(key)
    assert val == "1"


@pytest.mark.asyncio
async def test_set_expiry_custom_ttl(fake_redis):
    repo = LostItemRepositoryImpl(fake_redis)
    await repo.set_expiry(item_id=2, ttl_seconds=3600)
    key = "lost:item:2"
    ttl = await fake_redis.ttl(key)
    assert 0 < ttl <= 3600


@pytest.mark.asyncio
async def test_exists_active_item(fake_redis):
    repo = LostItemRepositoryImpl(fake_redis)
    await repo.set_expiry(item_id=3)
    assert await repo.exists(3) is True


@pytest.mark.asyncio
async def test_exists_expired_item(fake_redis):
    repo = LostItemRepositoryImpl(fake_redis)
    assert await repo.exists(999) is False


@pytest.mark.asyncio
async def test_remove_expiry(fake_redis):
    repo = LostItemRepositoryImpl(fake_redis)
    await repo.set_expiry(item_id=5)
    assert await repo.exists(5) is True
    await repo.remove_expiry(5)
    assert await repo.exists(5) is False
