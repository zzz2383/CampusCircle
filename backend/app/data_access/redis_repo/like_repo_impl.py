"""
功能：点赞 Repository 实现（Redis）

实现逻辑：
    1. 使用 Redis Set（post:like:set:{post_id}）存储点赞用户集合
    2. add_like: SADD 添加用户，SCARD 返回当前总数
    3. remove_like: SREM 移除用户，SCARD 返回当前总数
    4. is_liked: SISMEMBER 判断是否已点赞
    5. get_like_count: SCARD 获取集合基数

调用链路：
    - 被业务层的 LikeServiceImpl 通过 ILikeRepository 接口调用
    - 依赖 infrastructure/redis_client.py 提供的 Redis 客户端

参数说明：
    redis: 通过构造函数注入的 Redis 异步客户端

Key 命名规范：
    post:like:set:{post_id} — 帖子 {post_id} 的点赞用户集合

测试用例：
    - tests/unit/data_access/test_like_repo.py
"""

from typing import Optional

from redis.asyncio import Redis

from app.data_access.redis_repo.like_repo import ILikeRepository


class LikeRepositoryImpl(ILikeRepository):
    """点赞数据访问实现（Redis）"""

    # Key 模板
    LIKE_SET_KEY = "post:like:set:{}"

    def __init__(self, redis: Redis):
        self.redis = redis

    async def add_like(self, post_id: int, user_id: int) -> int:
        """添加点赞

        实现逻辑：
            1. SADD post:like:set:{post_id} user_id — 将用户加入集合（幂等）
            2. SCARD post:like:set:{post_id} — 返回当前总数

        参数：
            post_id: 帖子 ID
            user_id: 用户 ID

        返回值：
            当前总点赞数
        """
        key = self.LIKE_SET_KEY.format(post_id)
        await self.redis.sadd(key, user_id)
        return await self.redis.scard(key)

    async def remove_like(self, post_id: int, user_id: int) -> int:
        """取消点赞

        实现逻辑：
            1. SREM post:like:set:{post_id} user_id — 从集合移除用户
            2. SCARD post:like:set:{post_id} — 返回当前总数

        参数：
            post_id: 帖子 ID
            user_id: 用户 ID

        返回值：
            当前总点赞数
        """
        key = self.LIKE_SET_KEY.format(post_id)
        await self.redis.srem(key, user_id)
        return await self.redis.scard(key)

    async def is_liked(self, post_id: int, user_id: int) -> bool:
        """检查用户是否已点赞

        实现逻辑：
            SISMEMBER post:like:set:{post_id} user_id（Redis 返回 1/0，转为 bool）

        参数：
            post_id: 帖子 ID
            user_id: 用户 ID

        返回值：
            True 如果已点赞，False 否则
        """
        key = self.LIKE_SET_KEY.format(post_id)
        result = await self.redis.sismember(key, str(user_id))
        return bool(result)

    async def get_like_count(self, post_id: int) -> int:
        """获取帖子点赞总数

        实现逻辑：
            SCARD post:like:set:{post_id}

        参数：
            post_id: 帖子 ID

        返回值：
            点赞总数
        """
        key = self.LIKE_SET_KEY.format(post_id)
        return await self.redis.scard(key)
