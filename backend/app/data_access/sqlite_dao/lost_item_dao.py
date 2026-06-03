"""失物招领数据访问接口"""
from abc import ABC, abstractmethod
from typing import List, Optional
from app.models.domain import LostItem


class ILostItemDAO(ABC):
    @abstractmethod
    async def insert(self, item: LostItem) -> int: ...
    @abstractmethod
    async def get_by_id(self, item_id: int) -> Optional[LostItem]: ...
    @abstractmethod
    async def list_items(
        self, is_lost: Optional[bool] = None, offset: int = 0, limit: int = 20
    ) -> List[LostItem]: ...
    @abstractmethod
    async def mark_as_found(self, item_id: int) -> bool: ...
    @abstractmethod
    async def delete(self, item_id: int) -> bool: ...
    @abstractmethod
    async def count_all(self) -> int: ...
