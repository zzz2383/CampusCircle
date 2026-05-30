"""
功能：排行榜 Repository 接口

实现逻辑：
    定义排行榜相关的 Redis 操作抽象接口
    使用 Redis Sorted Set 存储不同维度的排行榜数据

调用链路：
    - 被 business 层的 RankService 调用
    - 由 redis_repo 目录下的具体实现类实现
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple


class IRankRepository(ABC):
    """排行榜数据访问接口（Redis Sorted Set）"""

    @abstractmethod
    async def increment_score(self, key: str, member: str, increment: int = 1) -> float:
        """增加成员分数（ZINCRBY）

        参数：
            key: Sorted Set 的 key
            member: 成员标识（如 post_id, club_id）
            increment: 增加分数

        返回值：
            更新后的分数
        """
        ...

    @abstractmethod
    async def get_top_members(
        self, key: str, limit: int = 10, with_scores: bool = True
    ) -> List[Tuple[str, float]]:
        """获取排行榜前 N 名（ZREVRANGE）

        参数：
            key: Sorted Set 的 key
            limit: 返回前 N 名
            with_scores: 是否返回分数

        返回值：
            (成员标识, 分数) 元组列表
        """
        ...

    @abstractmethod
    async def get_member_score(self, key: str, member: str) -> Optional[float]:
        """获取成员分数（ZSCORE）

        参数：
            key: Sorted Set 的 key
            member: 成员标识

        返回值：
            分数，如果成员不存在则返回 None
        """
        ...

    @abstractmethod
    async def reset_rank(self, key: str) -> bool:
        """重置排行榜（DEL）

        参数：
            key: Sorted Set 的 key

        返回值：
            是否删除成功
        """
        ...
