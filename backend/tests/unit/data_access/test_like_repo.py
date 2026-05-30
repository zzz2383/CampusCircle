"""
功能：LikeRepository 单元测试

测试策略：
    - 使用 fakeredis（fake_redis fixture）模拟 Redis
    - 每个测试独立 fakeredis 实例
    - 覆盖正常路径 + 边界路径

测试用例：
    - test_add_like: SADD 添加点赞，返回当前总数
    - test_add_like_duplicate: 重复点赞幂等
    - test_remove_like: SREM 取消点赞
    - test_is_liked_true: 已点赞返回 True
    - test_is_liked_false: 未点赞返回 False
    - test_get_like_count: 获取点赞总数
    - test_like_count_after_add_remove: 添加/取消后计数正确
"""

import pytest

from app.data_access.redis_repo.like_repo_impl import LikeRepositoryImpl


@pytest.mark.asyncio
async def test_add_like(fake_redis):
    """测试添加点赞，返回当前总数"""
    repo = LikeRepositoryImpl(fake_redis)
    count = await repo.add_like(post_id=100, user_id=1)
    assert count == 1

    count = await repo.add_like(post_id=100, user_id=2)
    assert count == 2


@pytest.mark.asyncio
async def test_add_like_duplicate(fake_redis):
    """测试重复点赞，set 幂等返回相同计数"""
    repo = LikeRepositoryImpl(fake_redis)
    count1 = await repo.add_like(post_id=100, user_id=1)
    count2 = await repo.add_like(post_id=100, user_id=1)
    # 同一个用户只算 1 次
    assert count1 == 1
    assert count2 == 1  # 幂等


@pytest.mark.asyncio
async def test_remove_like(fake_redis):
    """测试取消点赞"""
    repo = LikeRepositoryImpl(fake_redis)
    await repo.add_like(post_id=100, user_id=1)
    await repo.add_like(post_id=100, user_id=2)

    count = await repo.remove_like(post_id=100, user_id=1)
    assert count == 1  # 只剩 user 2


@pytest.mark.asyncio
async def test_is_liked_true(fake_redis):
    """测试已点赞返回 True"""
    repo = LikeRepositoryImpl(fake_redis)
    await repo.add_like(post_id=100, user_id=1)

    assert await repo.is_liked(post_id=100, user_id=1) is True


@pytest.mark.asyncio
async def test_is_liked_false(fake_redis):
    """测试未点赞返回 False"""
    repo = LikeRepositoryImpl(fake_redis)
    assert await repo.is_liked(post_id=100, user_id=1) is False


@pytest.mark.asyncio
async def test_get_like_count(fake_redis):
    """测试获取点赞总数"""
    repo = LikeRepositoryImpl(fake_redis)
    assert await repo.get_like_count(post_id=100) == 0

    await repo.add_like(post_id=100, user_id=1)
    await repo.add_like(post_id=100, user_id=2)
    await repo.add_like(post_id=100, user_id=3)

    assert await repo.get_like_count(post_id=100) == 3


@pytest.mark.asyncio
async def test_like_count_after_add_remove(fake_redis):
    """测试添加/取消后计数正确"""
    repo = LikeRepositoryImpl(fake_redis)

    await repo.add_like(post_id=100, user_id=1)
    await repo.add_like(post_id=100, user_id=2)
    assert await repo.get_like_count(post_id=100) == 2

    await repo.remove_like(post_id=100, user_id=1)
    assert await repo.get_like_count(post_id=100) == 1

    await repo.remove_like(post_id=100, user_id=2)
    assert await repo.get_like_count(post_id=100) == 0
