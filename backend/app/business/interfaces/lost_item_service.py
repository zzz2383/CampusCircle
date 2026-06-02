"""失物招领业务逻辑接口"""
from abc import ABC, abstractmethod
from typing import List, Optional
from app.models.dto import LostItemCreateRequest, LostItemDTO


class ILostItemService(ABC):
    @abstractmethod
    async def create_item(self, user_id: int, request: LostItemCreateRequest) -> LostItemDTO: ...

    @abstractmethod
    async def get_item_by_id(self, item_id: int) -> Optional[LostItemDTO]: ...

    @abstractmethod
    async def list_items(
        self, is_lost: Optional[bool] = None, offset: int = 0, limit: int = 20
    ) -> List[LostItemDTO]: ...

    @abstractmethod
    async def mark_as_found(self, item_id: int, user_id: int) -> bool: ...
