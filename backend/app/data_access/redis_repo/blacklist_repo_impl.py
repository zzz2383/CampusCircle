"""黑名单 Redis Repository 实现"""
from datetime import datetime, timezone
from typing import Any

from redis.asyncio import Redis

from app.data_access.redis_repo.blacklist_repo import IBlacklistRepo


class BlacklistRepoImpl(IBlacklistRepo):
    BLACKLIST_KEY = "blacklist:user:{}"

    def __init__(self, redis: Redis):
        self.redis = redis

    async def ban(self, user_id: int, duration_hours: int = 24) -> None:
        key = self.BLACKLIST_KEY.format(user_id)
        await self.redis.setex(key, duration_hours * 3600, datetime.now(timezone.utc).isoformat())

    async def unban(self, user_id: int) -> None:
        key = self.BLACKLIST_KEY.format(user_id)
        await self.redis.delete(key)

    async def is_banned(self, user_id: int) -> bool:
        key = self.BLACKLIST_KEY.format(user_id)
        result = await self.redis.exists(key)
        return bool(result)

    async def list_banned(self) -> list[dict]:
        keys = await self.redis.keys("blacklist:user:*")
        result = []
        for key in keys:
            user_id = int(key.split(":")[-1])
            ttl = await self.redis.ttl(key)
            banned_at = await self.redis.get(key)
            result.append({
                "user_id": user_id,
                "banned_at": banned_at,
                "remaining_seconds": ttl,
            })
        return result
