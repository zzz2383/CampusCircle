"""
功能：评论数据访问对象接口
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from app.models.domain import Comment


class ICommentDAO(ABC):
    """评论数据访问接口"""

    @abstractmethod
    async def insert(self, comment: Comment) -> int:
        """创建评论"""
        ...

    @abstractmethod
    async def get_by_id(self, comment_id: int) -> Optional[Comment]:
        """根据 ID 查询评论"""
        ...

    @abstractmethod
    async def list_by_post(
        self, post_id: int, offset: int = 0, limit: int = 20,
        parent_id: Optional[int] = None,
    ) -> List[Comment]:
        """获取帖子评论列表（支持 parent_id 筛选楼中楼）"""
        ...

    @abstractmethod
    async def delete(self, comment_id: int) -> bool:
        """软删除评论"""
        ...

    @abstractmethod
    async def list_all(self, offset: int = 0, limit: int = 20) -> List[Comment]:
        """获取所有评论列表（管理员用）"""
        ...
