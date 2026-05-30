"""
功能：点赞 Repository 接口

实现逻辑：
    定义点赞相关的 Redis 操作抽象接口
    使用 Redis Set 存储点赞用户集合，String 存储计数

调用链路：
    - 被 business 层的 LikeService 调用
    - 由 redis_repo 目录下的具体实现类实现
"""

from abc import ABC, abstractmethod


class ILikeRepository(ABC):
    """点赞数据访问接口（Redis）"""

    @abstractmethod
    async def add_like(self, post_id: int, user_id: int) -> int:
        """添加点赞（SADD + INCR）

        参数：
            post_id: 帖子 ID
            user_id: 用户 ID

        返回值：
            当前总点赞数（INCR 后的值）

        测试用例：
            - test_add_like_success
            - test_add_like_duplicate
        """
        ...

    @abstractmethod
    async def remove_like(self, post_id: int, user_id: int) -> int:
        """取消点赞（SREM + DECR）

        参数：
            post_id: 帖子 ID
            user_id: 用户 ID

        返回值：
            当前总点赞数
        """
        ...

    @abstractmethod
    async def is_liked(self, post_id: int, user_id: int) -> bool:
        """检查用户是否已点赞（SISMEMBER）

        参数：
            post_id: 帖子 ID
            user_id: 用户 ID

        返回值：
            是否已点赞
        """
        ...

    @abstractmethod
    async def get_like_count(self, post_id: int) -> int:
        """获取帖子点赞总数（GET）

        参数：
            post_id: 帖子 ID

        返回值：
            点赞总数
        """
        ...
