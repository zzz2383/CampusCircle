"""
功能：排行榜业务逻辑接口

实现逻辑：
    定义热帖榜、社团活跃榜等排行榜业务操作抽象接口

调用链路：
    - 被表现层的 rank 路由调用
    - 调用数据访问层的 RankRepository + PostDAO
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from app.models.dto import PostDTO, ClubRankDTO


class IRankService(ABC):
    """排行榜服务接口"""

    @abstractmethod
    async def get_hot_posts(
        self, limit: int = 10, tag: Optional[str] = None
    ) -> List[PostDTO]:
        """获取热帖排行榜

        实现逻辑：
            1. 从 Redis Sorted Set 读取热度分最高的帖子
            2. 根据 tag 选择不同的 Sorted Set 分片
            3. 回查 SQLite 获取帖子详细信息

        参数：
            limit: 返回前 N 条
            tag: 可选的话题标签（如 "课程"、"社团"）

        返回值：
            PostDTO 列表（按热度分降序）

        测试用例：
            - test_get_hot_posts
            - test_get_hot_posts_with_tag
        """
        ...

    @abstractmethod
    async def increment_hot_score(self, post_id: int, tag: str, increment: int = 1) -> None:
        """增加帖子热度分（由 LikeService 在点赞时触发）"""
        ...

    @abstractmethod
    async def get_club_rank(self, limit: int = 10) -> List[ClubRankDTO]:
        """获取社团活跃榜"""
        ...

    @abstractmethod
    async def increment_club_score(self, club_id: int, increment: int = 1) -> None:
        """增加社团活跃度分（由 PostService 在发帖时触发）"""
        ...
