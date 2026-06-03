"""活动报名 Redis Repository 实现"""
from redis.asyncio import Redis
from app.data_access.redis_repo.event_registration_repo import IEventRegistrationRepo


class EventRegistrationRepoImpl(IEventRegistrationRepo):
    PARTICIPANT_SET_KEY = "event:participants:{}"

    def __init__(self, redis: Redis):
        self.redis = redis

    async def add_participant(self, event_id: int, user_id: int) -> int:
        key = self.PARTICIPANT_SET_KEY.format(event_id)
        await self.redis.sadd(key, user_id)
        return await self.redis.scard(key)

    async def remove_participant(self, event_id: int, user_id: int) -> int:
        key = self.PARTICIPANT_SET_KEY.format(event_id)
        await self.redis.srem(key, user_id)
        return await self.redis.scard(key)

    async def is_registered(self, event_id: int, user_id: int) -> bool:
        key = self.PARTICIPANT_SET_KEY.format(event_id)
        result = await self.redis.sismember(key, user_id)
        return bool(result)

    async def get_participant_count(self, event_id: int) -> int:
        key = self.PARTICIPANT_SET_KEY.format(event_id)
        return await self.redis.scard(key)
