"""活动报名 Redis Repository 接口

Key 命名规范：
    event:participants:{event_id} — 活动报名的用户 ID 集合（Set）
"""
from abc import ABC, abstractmethod


class IEventRegistrationRepo(ABC):
    @abstractmethod
    async def add_participant(self, event_id: int, user_id: int) -> int: ...

    @abstractmethod
    async def remove_participant(self, event_id: int, user_id: int) -> int: ...

    @abstractmethod
    async def is_registered(self, event_id: int, user_id: int) -> bool: ...

    @abstractmethod
    async def get_participant_count(self, event_id: int) -> int: ...
