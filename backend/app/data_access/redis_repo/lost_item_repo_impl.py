"""失物招领 Redis Repository 实现"""
from redis.asyncio import Redis
from app.data_access.redis_repo.lost_item_repo import ILostItemRepository


class LostItemRepositoryImpl(ILostItemRepository):
    """失物招领 Redis 数据访问实现"""

    LOST_ITEM_KEY = "lost:item:{}"

    def __init__(self, redis: Redis):
        self.redis = redis

    async def set_expiry(self, item_id: int, ttl_seconds: int = 604800) -> None:
        """设置失物招领过期时间

        实现逻辑：
            SETEX lost:item:{id} ttl_seconds item_id
            — 原子操作：SET + EXPIRE，7 天自动过期

        参数：
            item_id: 失物招领条目 ID
            ttl_seconds: 过期时间（秒），默认 604800（7 天）
        """
        key = self.LOST_ITEM_KEY.format(item_id)
        await self.redis.set(key, str(item_id), ex=ttl_seconds)

    async def exists(self, item_id: int) -> bool:
        """检查失物招领条目是否未过期

        实现逻辑：
            EXISTS lost:item:{id} — Redis 自动过期删除 key

        参数：
            item_id: 失物招领条目 ID

        返回值：
            True 表示未过期
        """
        key = self.LOST_ITEM_KEY.format(item_id)
        result = await self.redis.exists(key)
        return bool(result)

    async def remove_expiry(self, item_id: int) -> None:
        """手动移除过期标记

        实现逻辑：
            DEL lost:item:{id} — 标记已找回时清除
        """
        key = self.LOST_ITEM_KEY.format(item_id)
        await self.redis.delete(key)
