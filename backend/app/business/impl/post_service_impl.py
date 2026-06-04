"""帖子业务逻辑实现"""
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.business.interfaces.post_service import IPostService
from app.business.interfaces.rank_service import IRankService
from app.data_access.sqlite_dao.post_dao import IPostDAO
from app.data_access.sqlite_dao.club_dao import IClubDAO
from app.data_access.redis_repo.like_repo import ILikeRepository
from app.infrastructure.exceptions import PostNotFoundError, BusinessError
from app.infrastructure.logger import get_logger
from app.models.domain import Post
from app.models.dto import (
    PostCreateRequest,
    PostUpdateRequest,
    PostDTO,
    PostListResponse,
)

logger = get_logger(__name__)


class PostServiceImpl(IPostService):
    """帖子服务实现"""

    def __init__(
        self,
        post_dao: IPostDAO,
        db_session: AsyncSession,
        like_repo: Optional[ILikeRepository] = None,
        club_dao: Optional[IClubDAO] = None,
        rank_service: Optional[IRankService] = None,
    ):
        self.post_dao = post_dao
        self.db_session = db_session
        self.like_repo = like_repo
        self.club_dao = club_dao
        self.rank_service = rank_service

    async def create_post(self, user_id: int, request: PostCreateRequest) -> PostDTO:
        post = Post(
            user_id=user_id,
            title=request.title,
            content=request.content,
            tags=request.tags,
            club_id=request.club_id,
        )
        post_id = await self.post_dao.insert(post)
        await self.db_session.commit()

        if request.club_id and self.rank_service:
            await self.rank_service.increment_club_score(request.club_id, increment=1)

        logger.info(f"Post created: id={post_id}, user_id={user_id}")
        created = await self.post_dao.get_by_id(post_id)
        return await self._to_dto(created)

    async def get_post_by_id(
        self, post_id: int, current_user_id: Optional[int] = None
    ) -> Optional[PostDTO]:
        post = await self.post_dao.get_by_id(post_id)
        if post is None:
            raise PostNotFoundError(post_id)
        return await self._to_dto(post, current_user_id=current_user_id)

    async def update_post(self, post_id: int, user_id: int, request: PostUpdateRequest) -> Optional[PostDTO]:
        post = await self.post_dao.get_by_id(post_id)
        if post is None:
            raise PostNotFoundError(post_id)
        if post.user_id != user_id:
            raise BusinessError(code="PERMISSION_DENIED", message="只有作者才能编辑帖子")
        update_data = request.model_dump(exclude_none=True)
        if not update_data:
            return await self._to_dto(post)
        for key, value in update_data.items():
            setattr(post, key, value)
        await self.db_session.commit()
        logger.info(f"Post updated: id={post_id}")
        updated = await self.post_dao.get_by_id(post_id)
        return await self._to_dto(updated)

    async def delete_post(self, post_id: int, user_id: int) -> bool:
        post = await self.post_dao.get_by_id(post_id)
        if post is None:
            raise PostNotFoundError(post_id)
        if post.user_id != user_id:
            raise BusinessError(
                code="PERMISSION_DENIED",
                message="只有作者才能删除帖子",
            )
        result = await self.post_dao.delete(post_id)
        await self.db_session.commit()
        logger.info(f"Post deleted: id={post_id}, user_id={user_id}")
        return result

    async def list_posts(
        self, offset: int = 0, limit: int = 20, tag: Optional[str] = None,
        club_id: Optional[int] = None,
    ) -> PostListResponse:
        posts = await self.post_dao.list_latest(
            offset=offset, limit=limit, tag=tag, club_id=club_id,
        )
        total = await self.post_dao.count_latest(tag=tag, club_id=club_id)
        items = [await self._to_dto(p) for p in posts]
        return PostListResponse(
            items=items, total=total, offset=offset, limit=limit,
        )

    async def get_user_posts(
        self, user_id: int, offset: int = 0, limit: int = 20
    ) -> PostListResponse:
        posts = await self.post_dao.list_by_user(
            user_id=user_id, offset=offset, limit=limit
        )
        items = [await self._to_dto(p) for p in posts]
        return PostListResponse(
            items=items, total=len(items), offset=offset, limit=limit,
        )

    async def search_posts(
        self, keyword: str, offset: int = 0, limit: int = 20
    ) -> PostListResponse:
        """搜索帖子"""
        posts = await self.post_dao.search(keyword=keyword, offset=offset, limit=limit)
        items = [await self._to_dto(p) for p in posts]
        return PostListResponse(
            items=items, total=len(items), offset=offset, limit=limit,
        )

    async def increment_view_count(self, post_id: int) -> int:
        count = await self.post_dao.increment_view_count(post_id)
        await self.db_session.commit()
        return count

    async def _to_dto(self, post, current_user_id: Optional[int] = None) -> PostDTO:
        comment_count = await self.post_dao.count_comments(post.id)
        like_count = 0
        is_liked = False
        if self.like_repo:
            like_count = await self.like_repo.get_like_count(post.id)
            if current_user_id:
                is_liked = await self.like_repo.is_liked(post.id, current_user_id)
        club_name = None
        if post.club_id and self.club_dao:
            club = await self.club_dao.get_by_id(post.club_id)
            club_name = club.name if club else None
        return PostDTO(
            id=post.id,
            user_id=post.user_id,
            title=post.title,
            content=post.content,
            tags=post.tags,
            club_id=post.club_id,
            club_name=club_name,
            author_nickname=post.author.nickname if post.author else None,
            author_avatar=post.author.avatar_url if post.author else None,
            like_count=like_count,
            comment_count=comment_count,
            view_count=post.view_count,
            is_liked=is_liked,
            created_at=post.created_at,
            updated_at=post.updated_at,
        )
