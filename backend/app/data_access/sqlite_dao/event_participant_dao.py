"""活动报名数据访问接口"""
from abc import ABC, abstractmethod
from typing import List, Optional
from app.models.domain import EventParticipant


class IEventParticipantDAO(ABC):
    @abstractmethod
    async def add(self, participant: EventParticipant) -> int: ...

    @abstractmethod
    async def remove(self, user_id: int, event_id: int) -> bool: ...

    @abstractmethod
    async def is_participant(self, user_id: int, event_id: int) -> bool: ...

    @abstractmethod
    async def count(self, event_id: int) -> int: ...

    @abstractmethod
    async def list_participants(self, event_id: int) -> List[EventParticipant]: ...
