"""
功能：帖子业务逻辑实现

实现逻辑：
    1. create_post: 创建帖子 → 写入 DB → 返回 PostDTO
    2. get_post_by_id: 查询帖子 → 返回 PostDTO（含作者昵称、真实评论数）
    3. delete_post: 校验作者身份 → 软删除
    4. list_posts: 分页查询 → 返回 PostListResponse
    5. increment_view_count: 增加浏览量 → 返回新值

调用链路：
    - 被表现层 posts 路由通过 IPostService 接口调用
    - 调用数据访问层 IPostDAO 接口
    - _to_dto 中通过 count_comments 获取真实评论数
"""

from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.business.interfaces.post_service import IPostService
from app.data_access.sqlite_dao.post_dao import IPostDAO
from app.infrastructure.exceptions import PostNotFoundError, BusinessError
from app.infrastructure.logger import get_logger
from app.models.domain import Post
from app.models.dto import (
    PostCreateRequest,
    PostDTO,
    PostListResponse,
)

logger = get_logger(__name__)


class PostServiceImpl(IPostService):
    """帖子服务实现"""

    def __init__(self, post_dao: IPostDAO, db_session: AsyncSession):
        self.post_dao = post_dao
        self.db_session = db_session

    async def create_post(self, user_id: int, request: PostCreateRequest) -> PostDTO:
        post = Post(
            user_id=user_id,
            title=request.title,
            content=request.content,
            tags=request.tags,
        )

        post_id = await self.post_dao.insert(post)
        await self.db_session.commit()

        logger.info(f"Post created: id={post_id}, user_id={user_id}")

        created = await self.post_dao.get_by_id(post_id)
        return await self._to_dto(created)

    async def get_post_by_id(self, post_id: int) -> Optional[PostDTO]:
        post = await self.post_dao.get_by_id(post_id)
        if post is None:
            raise PostNotFoundError(post_id)
        return await self._to_dto(post)

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
        self, offset: int = 0, limit: int = 20, tag: Optional[str] = None
    ) -> PostListResponse:
        posts = await self.post_dao.list_latest(
            offset=offset, limit=limit, tag=tag
        )
        items = [await self._to_dto(p) for p in posts]

        return PostListResponse(
            items=items,
            total=len(items),
            offset=offset,
            limit=limit,
        )

    async def increment_view_count(self, post_id: int) -> int:
        """增加帖子浏览量

        调用 PostDAO.increment_view_count() 更新数据库，
        提交事务后返回新浏览量。
        """
        count = await self.post_dao.increment_view_count(post_id)
        await self.db_session.commit()
        return count

    async def _to_dto(self, post: Post) -> PostDTO:
        """将 Post ORM 对象转换为 PostDTO

        从数据库获取真实评论数，从 Redis 获取点赞数（暂为 0）。
        """
        comment_count = await self.post_dao.count_comments(post.id)
        return PostDTO(
            id=post.id,
            user_id=post.user_id,
            title=post.title,
            content=post.content,
            tags=post.tags,
            author_nickname=post.author.nickname if post.author else None,
            like_count=0,
            comment_count=comment_count,
            view_count=post.view_count,
            is_liked=False,
            created_at=post.created_at,
            updated_at=post.updated_at,
        )
