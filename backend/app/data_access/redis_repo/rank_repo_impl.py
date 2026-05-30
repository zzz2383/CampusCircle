"""
功能：排行榜 Repository 实现（Redis Sorted Set）

实现逻辑：
    1. 使用 Redis Sorted Set 存储排行榜数据
    2. increment_score: ZINCRBY 原子增加分数
    3. get_top_members: ZREVRANGE 获取前 N 名（降序）
    4. get_member_score: ZSCORE 获取单个成员分数
    5. reset_rank: DEL 删除整个排行榜

调用链路：
    - 被业务层的 LikeService / RankService 调用
    - 依赖 infrastructure/redis_client.py 提供的 Redis 客户端

参数说明：
    redis: 通过构造函数注入的 Redis 异步客户端

Key 命名规范：
    hot:posts:day:{tag} — 某标签下的日榜
    club:active — 社团活跃度排名

测试用例：
    - tests/unit/data_access/test_rank_repo.py
"""

from typing import List, Optional, Tuple

from redis.asyncio import Redis

from app.data_access.redis_repo.rank_repo import IRankRepository


class RankRepositoryImpl(IRankRepository):
    """排行榜数据访问实现（Redis Sorted Set）"""

    def __init__(self, redis: Redis):
        self.redis = redis

    async def increment_score(self, key: str, member: str, increment: int = 1) -> float:
        """增加成员分数

        实现逻辑：
            ZINCRBY key increment member — 原子增加分数（成员不存在则创建）

        参数：
            key: Sorted Set 的 key
            member: 成员标识
            increment: 增加分数（默认 1）

        返回值：
            更新后的分数
        """
        return await self.redis.zincrby(key, increment, member)

    async def get_top_members(
        self, key: str, limit: int = 10, with_scores: bool = True
    ) -> List[Tuple[str, float]]:
        """获取排行榜前 N 名

        实现逻辑：
            ZREVRANGE key 0 limit-1 — 按分数降序获取

        参数：
            key: Sorted Set 的 key
            limit: 返回前 N 名（默认 10）
            with_scores: 是否返回分数（默认 True）

        返回值：
            with_scores=True 时返回 [(member, score), ...]
            with_scores=False 时返回 [(member,), ...]
        """
        if with_scores:
            result = await self.redis.zrevrange(key, 0, limit - 1, withscores=True)
            return [(member, score) for member, score in result]
        else:
            members = await self.redis.zrevrange(key, 0, limit - 1)
            return [(m,) for m in members]

    async def get_member_score(self, key: str, member: str) -> Optional[float]:
        """获取成员分数

        实现逻辑：
            ZSCORE key member — 获取分数，不存在返回 None

        参数：
            key: Sorted Set 的 key
            member: 成员标识

        返回值：
            分数（float）或 None
        """
        score = await self.redis.zscore(key, member)
        return float(score) if score is not None else None

    async def reset_rank(self, key: str) -> bool:
        """重置排行榜

        实现逻辑：
            DEL key — 删除整个 Sorted Set

        参数：
            key: Sorted Set 的 key

        返回值：
            True 如果 key 存在并被删除，False 如果 key 不存在
        """
        result = await self.redis.delete(key)
        return result > 0
