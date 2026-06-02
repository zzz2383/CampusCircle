"""事件数据访问接口"""
from abc import ABC, abstractmethod
from typing import List, Optional
from app.models.domain import Event


class IEventDAO(ABC):
    @abstractmethod
    async def insert(self, event: Event) -> int: ...
    @abstractmethod
    async def get_by_id(self, event_id: int) -> Optional[Event]: ...
    @abstractmethod
    async def list_events(self, offset: int = 0, limit: int = 20) -> List[Event]: ...
