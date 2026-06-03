"""帖子业务逻辑接口"""
from abc import ABC, abstractmethod
from typing import List, Optional
from app.models.dto import PostCreateRequest, PostDTO, PostListResponse


class IPostService(ABC):
    @abstractmethod
    async def create_post(self, user_id: int, request: PostCreateRequest) -> PostDTO: ...

    @abstractmethod
    async def get_post_by_id(self, post_id: int, current_user_id: Optional[int] = None) -> Optional[PostDTO]: ...

    @abstractmethod
    async def delete_post(self, post_id: int, user_id: int) -> bool: ...

    @abstractmethod
    async def list_posts(
        self, offset: int = 0, limit: int = 20, tag: Optional[str] = None,
        club_id: Optional[int] = None,
    ) -> PostListResponse: ...

    @abstractmethod
    async def increment_view_count(self, post_id: int) -> int: ...

    @abstractmethod
    async def get_user_posts(
        self, user_id: int, offset: int = 0, limit: int = 20
    ) -> PostListResponse: ...
