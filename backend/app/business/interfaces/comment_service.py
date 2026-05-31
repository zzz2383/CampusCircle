"""
功能：评论业务逻辑接口

调用链路：
    - 被表现层 comments 路由调用
    - 调用数据访问层 CommentDAO
"""

from abc import ABC, abstractmethod
from typing import Optional

from app.models.dto import CommentCreateRequest, CommentDTO, CommentListResponse


class ICommentService(ABC):
    """评论服务接口"""

    @abstractmethod
    async def create_comment(
        self, post_id: int, user_id: int, request: CommentCreateRequest
    ) -> CommentDTO:
        """发表评论"""
        ...

    @abstractmethod
    async def get_comments(
        self, post_id: int, offset: int = 0, limit: int = 20
    ) -> CommentListResponse:
        """获取帖子评论列表"""
        ...

    @abstractmethod
    async def delete_comment(self, comment_id: int, user_id: int) -> bool:
        """删除评论（仅作者）"""
        ...
