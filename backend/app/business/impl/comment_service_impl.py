"""
功能：评论业务逻辑实现

调用链路：
    - 被表现层 comments 路由调用
    - 调用 ICommentDAO + IPostDAO
"""

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.business.interfaces.comment_service import ICommentService
from app.data_access.sqlite_dao.comment_dao import ICommentDAO
from app.data_access.sqlite_dao.post_dao import IPostDAO
from app.infrastructure.exceptions import PostNotFoundError, BusinessError
from app.infrastructure.logger import get_logger
from app.models.domain import Comment
from app.models.dto import CommentCreateRequest, CommentDTO, CommentListResponse

logger = get_logger(__name__)


class CommentServiceImpl(ICommentService):
    """评论服务实现"""

    def __init__(
        self,
        comment_dao: ICommentDAO,
        post_dao: IPostDAO,
        db_session: AsyncSession,
    ):
        self.comment_dao = comment_dao
        self.post_dao = post_dao
        self.db_session = db_session

    async def create_comment(
        self, post_id: int, user_id: int, request: CommentCreateRequest
    ) -> CommentDTO:
        """发表评论

        实现逻辑：
            1. 校验帖子是否存在
            2. 创建 Comment ORM 对象
            3. 写入数据库
            4. 提交事务
            5. 重新查询返回完整 DTO（含作者昵称）
        """
        post = await self.post_dao.get_by_id(post_id)
        if post is None:
            raise PostNotFoundError(post_id)

        comment = Comment(
            post_id=post_id,
            user_id=user_id,
            content=request.content,
            parent_id=request.parent_id,
        )
        cid = await self.comment_dao.insert(comment)
        await self.db_session.commit()

        logger.info(f"Comment created: id={cid}, post_id={post_id}, user_id={user_id}")

        created = await self.comment_dao.get_by_id(cid)
        return self._to_dto(created)

    async def get_comments(
        self, post_id: int, offset: int = 0, limit: int = 20
    ) -> CommentListResponse:
        """获取帖子评论列表"""
        comments = await self.comment_dao.list_by_post(post_id, offset=offset, limit=limit)
        items = [self._to_dto(c) for c in comments]
        return CommentListResponse(items=items, total=len(items))

    async def delete_comment(self, comment_id: int, user_id: int) -> bool:
        """删除评论（仅作者）

        实现逻辑：
            1. 查询评论是否存在
            2. 校验是否为评论作者
            3. 执行软删除
        """
        comment = await self.comment_dao.get_by_id(comment_id)
        if comment is None:
            raise BusinessError(code="COMMENT_NOT_FOUND", message="评论不存在")

        if comment.user_id != user_id:
            raise BusinessError(code="PERMISSION_DENIED", message="只有作者才能删除评论")

        result = await self.comment_dao.delete(comment_id)
        await self.db_session.commit()
        logger.info(f"Comment deleted: id={comment_id}, user_id={user_id}")
        return result

    def _to_dto(self, comment: Comment) -> CommentDTO:
        return CommentDTO(
            id=comment.id,
            post_id=comment.post_id,
            user_id=comment.user_id,
            author_nickname=comment.author.nickname if comment.author else None,
            content=comment.content,
            parent_id=comment.parent_id,
            created_at=comment.created_at,
        )
