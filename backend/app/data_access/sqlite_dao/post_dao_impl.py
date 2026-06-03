"""帖子数据访问实现（SQLite）"""
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from sqlalchemy import select, update, func
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from app.data_access.sqlite_dao.post_dao import IPostDAO
from app.models.domain import Post, Comment


class PostDAOImpl(IPostDAO):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def insert(self, post: Post) -> int:
        self.session.add(post)
        await self.session.flush()
        return post.id

    async def get_by_id(self, post_id: int) -> Optional[Post]:
        result = await self.session.execute(
            select(Post).options(joinedload(Post.author))
            .where(Post.id == post_id, Post.is_active.is_(True)))
        return result.unique().scalar_one_or_none()

    async def delete(self, post_id: int) -> bool:
        result = await self.session.execute(
            update(Post).where(Post.id == post_id).values(is_active=False))
        return result.rowcount > 0

    async def list_latest(self, offset: int = 0, limit: int = 20, tag: Optional[str] = None,
                          club_id: Optional[int] = None) -> List[Post]:
        query = (select(Post).options(joinedload(Post.author))
                 .where(Post.is_active.is_(True))
                 .order_by(Post.created_at.desc()).offset(offset).limit(limit))
        if tag:
            query = query.where(Post.tags.like(f"%{tag}%"))
        if club_id is not None:
            query = query.where(Post.club_id == club_id)
        result = await self.session.execute(query)
        return result.unique().scalars().all()

    async def search(self, keyword: str, offset: int = 0, limit: int = 20) -> List[Post]:
        pattern = f"%{keyword}%"
        result = await self.session.execute(
            select(Post).options(joinedload(Post.author))
            .where(Post.is_active.is_(True), (Post.title.like(pattern) | Post.content.like(pattern)))
            .order_by(Post.created_at.desc()).offset(offset).limit(limit))
        return result.unique().scalars().all()

    async def increment_view_count(self, post_id: int) -> int:
        result = await self.session.execute(
            update(Post).where(Post.id == post_id).values(view_count=Post.view_count + 1))
        if result.rowcount == 0:
            return 0
        updated = await self.session.execute(select(Post.view_count).where(Post.id == post_id))
        return updated.scalar() or 0

    async def count_comments(self, post_id: int) -> int:
        result = await self.session.execute(
            select(func.count()).select_from(Comment)
            .where(Comment.post_id == post_id, Comment.is_active.is_(True)))
        return result.scalar() or 0

    async def count_all(self) -> int:
        result = await self.session.execute(
            select(func.count()).select_from(Post).where(Post.is_active.is_(True)))
        return result.scalar() or 0

    async def count_latest(self, tag: Optional[str] = None, club_id: Optional[int] = None) -> int:
        query = select(func.count()).select_from(Post).where(Post.is_active.is_(True))
        if tag:
            query = query.where(Post.tags.like(f"%{tag}%"))
        if club_id is not None:
            query = query.where(Post.club_id == club_id)
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def get_post_trend(self, days: int = 7) -> list:
        since = datetime.now(timezone.utc) - timedelta(days=days)
        from sqlalchemy import cast, Date
        result = await self.session.execute(
            select(cast(Post.created_at, Date).label("date"), func.count().label("count"))
            .where(Post.created_at >= since, Post.is_active.is_(True))
            .group_by(cast(Post.created_at, Date))
            .order_by(cast(Post.created_at, Date)))
        return [{"date": str(row[0]), "count": row[1]} for row in result]

    async def list_by_user(self, user_id: int, offset: int = 0, limit: int = 20) -> List[Post]:
        result = await self.session.execute(
            select(Post).options(joinedload(Post.author))
            .where(Post.user_id == user_id, Post.is_active.is_(True))
            .order_by(Post.created_at.desc()).offset(offset).limit(limit))
        return result.unique().scalars().all()
