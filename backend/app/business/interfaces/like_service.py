"""
功能：点赞业务逻辑接口

实现逻辑：
    定义点赞/取消点赞等业务操作抽象接口

调用链路：
    - 被表现层的 likes 路由调用
    - 调用数据访问层的 LikeRepository + RankRepository + NotificationService
"""

from abc import ABC, abstractmethod

from app.models.dto import LikeResultDTO


class ILikeService(ABC):
    """点赞服务接口"""

    @abstractmethod
    async def like_post(self, user_id: int, post_id: int) -> LikeResultDTO:
        """点赞帖子

        实现逻辑：
            1. 校验帖子是否存在
            2. 调用 LikeRepository.add_like()（Redis SADD）
            3. 若首次点赞，INCR 计数 + ZINCRBY 热帖榜加分
            4. 发送 Pub/Sub 通知帖子作者

        参数：
            user_id: 点赞者 ID
            post_id: 帖子 ID

        返回值：
            LikeResultDTO: 包含 is_liked, like_count

        异常：
            PostNotFoundError: 帖子不存在

        测试用例：
            - test_like_post_success
            - test_like_post_twice_idempotent
        """
        ...

    @abstractmethod
    async def unlike_post(self, user_id: int, post_id: int) -> LikeResultDTO:
        """取消点赞"""
        ...
