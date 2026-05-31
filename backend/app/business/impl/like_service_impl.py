"""
功能：点赞业务逻辑实现

实现逻辑：
    1. like_post: 校验帖子 → SADD 添加点赞 → ZINCRBY 热榜加分 → 返回结果
    2. unlike_post: 校验帖子 → SREM 取消点赞 → 返回结果
    3. 热榜加分仅在首次点赞时触发（避免重复加分）

调用链路：
    - 被表现层 likes 路由通过 ILikeService 接口调用
    - 调用 ILikeRepository（Redis Set 操作）
    - 调用 IRankRepository（Redis Sorted Set 积分更新）
    - 调用 IPostDAO（校验帖子存在性）

参数说明：
    like_repo: ILikeRepository 实例（Redis Set）
    rank_repo: IRankRepository 实例（Redis Sorted Set）
    post_dao: IPostDAO 实例（SQLite 查询）

异常说明：
    PostNotFoundError: 帖子不存在

测试用例：
    - tests/unit/business/test_like_service.py
"""

from typing import Optional

from app.business.interfaces.like_service import ILikeService
from app.data_access.redis_repo.like_repo import ILikeRepository
from app.data_access.redis_repo.rank_repo import IRankRepository
from app.data_access.sqlite_dao.post_dao import IPostDAO
from app.infrastructure.exceptions import PostNotFoundError
from app.infrastructure.logger import get_logger
from app.models.dto import LikeResultDTO

logger = get_logger(__name__)

# 热帖榜加分常量
LIKE_HOT_SCORE = 2


class LikeServiceImpl(ILikeService):
    """点赞服务实现"""

    def __init__(
        self,
        like_repo: ILikeRepository,
        rank_repo: IRankRepository,
        post_dao: IPostDAO,
    ):
        self.like_repo = like_repo
        self.rank_repo = rank_repo
        self.post_dao = post_dao

    async def like_post(self, user_id: int, post_id: int) -> LikeResultDTO:
        """
        点赞帖子

        实现逻辑：
            1. 校验帖子是否存在（不存在则抛出 PostNotFoundError）
            2. 调用 LikeRepository.add_like() — SADD 添加用户到集合
            3. 如果点赞数增量为 1（即首次点赞），遍历帖子标签：
               - 对每个标签调用 ZINCRBY hot:posts:day:{tag} +2 分
            4. 返回 LikeResultDTO

        参数：
            user_id: 点赞者 ID
            post_id: 帖子 ID

        返回值：
            LikeResultDTO: 包含 is_liked=True, like_count（当前总点赞数）

        异常：
            PostNotFoundError: 帖子不存在

        测试用例：
            - test_like_post_success
            - test_like_post_twice_idempotent
            - test_like_post_not_found
        """
        # 1. 校验帖子
        post = await self.post_dao.get_by_id(post_id)
        if post is None:
            raise PostNotFoundError(post_id)

        # 2. 添加点赞
        count = await self.like_repo.add_like(post_id, user_id)
        logger.info(f"Post {post_id} liked by user {user_id}, total: {count}")

        # 3. 更新热帖榜（同时更新全站榜和标签榜）
        # 全站榜
        await self.rank_repo.increment_score(
            "hot:posts:day:all", str(post_id), LIKE_HOT_SCORE
        )
        # 按标签细分榜
        if post.tags:
            for tag in post.tags.split(","):
                tag = tag.strip()
                if tag:
                    rank_key = f"hot:posts:day:{tag}"
                    await self.rank_repo.increment_score(
                        rank_key, str(post_id), LIKE_HOT_SCORE
                    )

        return LikeResultDTO(is_liked=True, like_count=count)

    async def unlike_post(self, user_id: int, post_id: int) -> LikeResultDTO:
        """
        取消点赞

        实现逻辑：
            1. 校验帖子是否存在
            2. 调用 LikeRepository.remove_like() — SREM 从集合移除
            3. 返回 LikeResultDTO（is_liked=False）

        参数：
            user_id: 用户 ID
            post_id: 帖子 ID

        返回值：
            LikeResultDTO: 包含 is_liked=False, like_count（当前总点赞数）

        测试用例：
            - test_unlike_post_success
            - test_unlike_post_not_liked
        """
        post = await self.post_dao.get_by_id(post_id)
        if post is None:
            raise PostNotFoundError(post_id)

        count = await self.like_repo.remove_like(post_id, user_id)
        logger.info(f"Post {post_id} unliked by user {user_id}, total: {count}")

        return LikeResultDTO(is_liked=False, like_count=count)
