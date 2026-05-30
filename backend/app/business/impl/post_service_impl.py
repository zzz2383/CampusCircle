"""
功能：帖子业务逻辑实现

实现逻辑：
    1. create_post: 创建帖子 → 写入 DB → 返回 PostDTO
    2. get_post_by_id: 查询帖子 → 返回 PostDTO（含作者昵称）
    3. delete_post: 校验作者身份 → 软删除
    4. list_posts: 分页查询 → 返回 PostListResponse

调用链路：
    - 被表现层 posts 路由通过 IPostService 接口调用
    - 调用数据访问层 IPostDAO 接口
    - 使用 UserService 校验用户存在

参数说明：
    post_dao: IPostDAO 实例（通过 DI 注入）
    db_session: AsyncSession 实例（通过 DI 注入）

异常说明：
    PostNotFoundError: 帖子不存在
    BusinessError: 无权限删除

测试用例：
    - tests/unit/business/test_post_service.py
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
    PostUpdateRequest,
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
        """
        发布校园帖

        实现逻辑：
            1. 创建 Post ORM 对象，关联作者 user_id
            2. 调用 PostDAO.insert() 写入数据库
            3. 提交事务
            4. 重新查询获取完整信息（含作者昵称）

        参数：
            user_id: 作者 ID
            request: 帖子创建请求（title, content, tags）

        返回值：
            PostDTO: 帖子信息（含作者昵称）

        测试用例：
            - test_create_post_success
        """
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
        return self._to_dto(created)

    async def get_post_by_id(self, post_id: int) -> Optional[PostDTO]:
        """
        根据 ID 获取帖子详情

        实现逻辑：
            1. 调用 PostDAO.get_by_id() 查询
            2. 若不存在则抛出 PostNotFoundError
            3. 转换为 PostDTO（含作者昵称和统计信息）

        参数：
            post_id: 帖子 ID

        返回值：
            PostDTO

        异常：
            PostNotFoundError: 帖子不存在

        测试用例：
            - test_get_post_by_id_found
            - test_get_post_by_id_not_found
        """
        post = await self.post_dao.get_by_id(post_id)
        if post is None:
            raise PostNotFoundError(post_id)
        return self._to_dto(post)

    async def delete_post(self, post_id: int, user_id: int) -> bool:
        """
        删除帖子（仅作者可删）

        实现逻辑：
            1. 查询帖子是否存在
            2. 校验当前用户是否为作者
            3. 执行软删除
            4. 提交事务

        参数：
            post_id: 帖子 ID
            user_id: 请求删除的用户 ID

        返回值：
            True 删除成功

        异常：
            PostNotFoundError: 帖子不存在
            BusinessError: 非作者尝试删除

        测试用例：
            - test_delete_post_success
            - test_delete_post_not_owner
        """
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
        """
        获取帖子列表（支持分页和标签筛选）

        实现逻辑：
            1. 调用 PostDAO.list_latest() 分页查询
            2. 将 ORM 对象列表转换为 DTO 列表
            3. 返回 PostListResponse（含总数、偏移、分页大小）

        参数：
            offset: 分页偏移量
            limit: 每页数量（默认 20）
            tag: 可选的话题标签筛选

        返回值：
            PostListResponse: 包含 items, total, offset, limit
        """
        posts = await self.post_dao.list_latest(
            offset=offset, limit=limit, tag=tag
        )
        items = [self._to_dto(p) for p in posts]

        # TODO: 后续实现真实 total 计数
        return PostListResponse(
            items=items,
            total=len(items),
            offset=offset,
            limit=limit,
        )

    def _to_dto(self, post: Post) -> PostDTO:
        """将 Post ORM 对象转换为 PostDTO

        实现逻辑：
            1. 从 post.author 关系中提取昵称
            2. 点赞数/评论数暂为 0（后续接入 Redis 后实现）
        """
        return PostDTO(
            id=post.id,
            user_id=post.user_id,
            title=post.title,
            content=post.content,
            tags=post.tags,
            author_nickname=post.author.nickname if post.author else None,
            like_count=0,
            comment_count=0,
            view_count=post.view_count,
            is_liked=False,
            created_at=post.created_at,
            updated_at=post.updated_at,
        )
