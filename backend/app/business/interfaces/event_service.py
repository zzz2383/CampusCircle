"""事件业务逻辑接口"""
from abc import ABC, abstractmethod
from typing import List, Optional
from app.models.dto import EventCreateRequest, EventDTO


class IEventService(ABC):
    @abstractmethod
    async def create_event(self, request: EventCreateRequest) -> EventDTO: ...
    @abstractmethod
    async def get_event_by_id(self, event_id: int) -> Optional[EventDTO]: ...
    @abstractmethod
    async def list_events(self, offset: int = 0, limit: int = 20, club_id: Optional[int] = None) -> List[EventDTO]: ...
