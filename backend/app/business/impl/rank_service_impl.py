"""
功能：排行榜业务逻辑实现

实现逻辑：
    1. get_hot_posts: 从 Redis Sorted Set 读取 top post_ids → 回查 SQLite → 填充点赞数 → 返回
    2. get_club_rank: 从 Redis Sorted Set 读取 club_ids → 回查 SQLite → 返回

调用链路：
    - 被表现层 rank 路由通过 IRankService 接口调用
    - 调用 IRankRepository（Redis Sorted Set 读取）
    - 调用 ILikeRepository（Redis 获取点赞数）
    - 调用 IPostDAO（SQLite 回查帖子详情）
    - 调用 IClubDAO（SQLite 回查社团详情）

参数说明：
    rank_repo: IRankRepository 实例
    like_repo: ILikeRepository 实例
    post_dao: IPostDAO 实例
    club_dao: IClubDAO 实例

测试用例：
    - tests/unit/business/test_rank_service.py
"""

from typing import List, Optional

from app.business.interfaces.rank_service import IRankService
from app.data_access.redis_repo.rank_repo import IRankRepository
from app.data_access.redis_repo.like_repo import ILikeRepository
from app.data_access.sqlite_dao.post_dao import IPostDAO
from app.data_access.sqlite_dao.club_dao import IClubDAO
from app.models.dto import PostDTO, ClubRankDTO

HOT_POSTS_KEY_PREFIX = "hot:posts:day:"
CLUB_RANK_KEY = "club:active"


class RankServiceImpl(IRankService):
    """排行榜服务实现"""

    def __init__(
        self,
        rank_repo: IRankRepository,
        like_repo: ILikeRepository,
        post_dao: IPostDAO,
        club_dao: IClubDAO,
    ):
        self.rank_repo = rank_repo
        self.like_repo = like_repo
        self.post_dao = post_dao
        self.club_dao = club_dao

    async def get_hot_posts(
        self, limit: int = 10, tag: Optional[str] = None
    ) -> List[PostDTO]:
        """
        获取热帖排行榜

        实现逻辑：
            1. 构建 Redis key: hot:posts:day:{tag or "all"}
            2. ZREVRANGE 获取分数最高的 N 个帖子 (post_id, hot_score)
            3. 遍历结果，对每个 post_id 回查 SQLite 获取帖子详情
            4. 从 Redis 获取每个帖子的点赞数
            5. 按热度分降序返回 PostDTO 列表

        参数：
            limit: 返回前 N 条（默认 10）
            tag: 话题标签筛选（如 "课程"，None 表示全站）

        返回值：
            PostDTO 列表（按热度分降序，含 like_count）
        """
        key = f"{HOT_POSTS_KEY_PREFIX}{tag or 'all'}"
        top_members = await self.rank_repo.get_top_members(key, limit=limit)

        results: List[PostDTO] = []
        for member, score in top_members:
            post_id = int(member)
            post = await self.post_dao.get_by_id(post_id)
            if post is None:
                continue

            like_count = await self.like_repo.get_like_count(post_id)

            results.append(PostDTO(
                id=post.id,
                user_id=post.user_id,
                title=post.title,
                content=post.content,
                tags=post.tags,
                author_nickname=post.author.nickname if post.author else None,
                like_count=like_count,
                comment_count=0,
                view_count=post.view_count,
                is_liked=False,
                created_at=post.created_at,
                updated_at=post.updated_at,
            ))

        return results

    async def increment_hot_score(self, post_id: int, tag: str, increment: int = 1) -> None:
        """
        增加帖子热度分

        实现逻辑：
            ZINCRBY hot:posts:day:{tag} {increment} {post_id}

        参数：
            post_id: 帖子 ID
            tag: 话题标签
            increment: 增加分数（默认 1）
        """
        key = f"{HOT_POSTS_KEY_PREFIX}{tag}"
        await self.rank_repo.increment_score(key, str(post_id), increment)

    async def increment_club_score(self, club_id: int, increment: int = 1) -> None:
        """增加社团活跃度分"""
        await self.rank_repo.increment_score(CLUB_RANK_KEY, str(club_id), increment)

    async def get_club_rank(self, limit: int = 10) -> List[ClubRankDTO]:
        """
        获取社团活跃榜

        实现逻辑：
            1. ZREVRANGE club:active 0 limit-1 获取社团排名
            2. 对每个 club_id 回查 SQLite 获取社团名称
            3. 返回 ClubRankDTO 列表（含排名）

        参数：
            limit: 返回前 N 条（默认 10）

        返回值：
            ClubRankDTO 列表（按活跃度降序）
        """
        top_members = await self.rank_repo.get_top_members(CLUB_RANK_KEY, limit=limit)

        results: List[ClubRankDTO] = []
        for rank, (member, score) in enumerate(top_members, start=1):
            club_id = int(member)
            club = await self.club_dao.get_by_id(club_id)
            if club is None:
                continue

            results.append(ClubRankDTO(
                club_id=club_id,
                club_name=club.name,
                post_count=int(score),
                rank=rank,
            ))

        return results
