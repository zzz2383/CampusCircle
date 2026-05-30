"""
功能：RankRepository 单元测试

测试策略：
    - 使用 fakeredis 模拟 Redis Sorted Set 操作
    - 覆盖正常路径 + 边界路径

测试用例：
    - test_increment_score: ZINCRBY 增加分数
    - test_get_top_members: ZREVRANGE 获取排行榜
    - test_get_top_members_without_scores: 不返回分数
    - test_get_member_score: ZSCORE 获取成员分数
    - test_get_member_score_not_found: 不存在的成员返回 None
    - test_reset_rank: DEL 重置排行榜
    - test_multiple_increments: 多次加分后排榜正确
"""

import pytest

from app.data_access.redis_repo.rank_repo_impl import RankRepositoryImpl


@pytest.mark.asyncio
async def test_increment_score(fake_redis):
    """测试 ZINCRBY 增加分数"""
    repo = RankRepositoryImpl(fake_redis)
    score = await repo.increment_score("hot:posts:day:test", "post:1", 10)
    assert score == 10.0

    score = await repo.increment_score("hot:posts:day:test", "post:1", 5)
    assert score == 15.0


@pytest.mark.asyncio
async def test_get_top_members(fake_redis):
    """测试 ZREVRANGE 获取排行榜"""
    repo = RankRepositoryImpl(fake_redis)

    await repo.increment_score("rank:test", "post:A", 30)
    await repo.increment_score("rank:test", "post:B", 50)
    await repo.increment_score("rank:test", "post:C", 10)

    top = await repo.get_top_members("rank:test", limit=2)
    assert len(top) == 2
    assert top[0] == ("post:B", 50.0)
    assert top[1] == ("post:A", 30.0)


@pytest.mark.asyncio
async def test_get_top_members_without_scores(fake_redis):
    """测试 ZREVRANGE 不返回分数"""
    repo = RankRepositoryImpl(fake_redis)

    await repo.increment_score("rank:test", "post:A", 30)
    result = await repo.get_top_members("rank:test", limit=10, with_scores=False)

    assert len(result) == 1
    assert result[0] == ("post:A",)  # 只有成员名


@pytest.mark.asyncio
async def test_get_member_score(fake_redis):
    """测试 ZSCORE 获取成员分数"""
    repo = RankRepositoryImpl(fake_redis)
    await repo.increment_score("rank:test", "post:A", 42)

    score = await repo.get_member_score("rank:test", "post:A")
    assert score == 42.0


@pytest.mark.asyncio
async def test_get_member_score_not_found(fake_redis):
    """测试不存在的成员返回 None"""
    repo = RankRepositoryImpl(fake_redis)
    score = await repo.get_member_score("rank:test", "nonexist")
    assert score is None


@pytest.mark.asyncio
async def test_reset_rank(fake_redis):
    """测试 DEL 重置排行榜"""
    repo = RankRepositoryImpl(fake_redis)
    await repo.increment_score("rank:test", "post:A", 10)

    deleted = await repo.reset_rank("rank:test")
    assert deleted is True

    top = await repo.get_top_members("rank:test", limit=10)
    assert len(top) == 0


@pytest.mark.asyncio
async def test_multiple_increments(fake_redis):
    """测试多次加分后排榜正确"""
    repo = RankRepositoryImpl(fake_redis)

    await repo.increment_score("rank:test", "post:A", 10)
    await repo.increment_score("rank:test", "post:B", 20)
    await repo.increment_score("rank:test", "post:C", 30)

    # 给 B 再加 15 分，B 应该超过 C
    await repo.increment_score("rank:test", "post:B", 15)

    top = await repo.get_top_members("rank:test", limit=3)
    assert top[0] == ("post:B", 35.0)  # 20+15
    assert top[1] == ("post:C", 30.0)
    assert top[2] == ("post:A", 10.0)
