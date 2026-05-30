"""
功能：帖子数据访问对象接口

实现逻辑：
    定义帖子相关的 SQLite 数据库操作抽象接口

调用链路：
    - 被 business 层的 PostService 调用
    - 由 sqlite_dao 目录下的具体实现类实现
"""

from abc import ABC, abstractmethod
from typing import Optional, List

from app.models.domain import Post


class IPostDAO(ABC):
    """帖子数据访问接口"""

    @abstractmethod
    async def insert(self, post: Post) -> int:
        """创建帖子

        参数：
            post: Post ORM 对象（不含 id）

        返回值：
            新帖子的 id
        """
        ...

    @abstractmethod
    async def get_by_id(self, post_id: int) -> Optional[Post]:
        """根据 ID 获取帖子

        参数：
            post_id: 帖子 ID

        返回值：
            Post ORM 对象或 None
        """
        ...

    @abstractmethod
    async def delete(self, post_id: int) -> bool:
        """删除帖子（软删除）

        参数：
            post_id: 帖子 ID

        返回值：
            是否删除成功
        """
        ...

    @abstractmethod
    async def list_latest(
        self, offset: int = 0, limit: int = 20, tag: Optional[str] = None
    ) -> List[Post]:
        """获取最新帖子列表（支持按标签筛选）

        参数：
            offset: 分页偏移量
            limit: 每页数量（默认 20）
            tag: 可选的话题标签筛选

        返回值：
            Post ORM 对象列表
        """
        ...

    @abstractmethod
    async def search(self, keyword: str, offset: int = 0, limit: int = 20) -> List[Post]:
        """全文搜索帖子

        参数：
            keyword: 搜索关键词
            offset: 分页偏移量
            limit: 每页数量

        返回值：
            匹配的 Post ORM 对象列表
        """
        ...
