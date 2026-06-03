"""社团数据访问实现（SQLite）"""
from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.data_access.sqlite_dao.club_dao import IClubDAO
from app.models.domain import Club


class ClubDAOImpl(IClubDAO):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def insert(self, club: Club) -> int:
        self.session.add(club)
        await self.session.flush()
        return club.id

    async def get_by_id(self, club_id: int) -> Optional[Club]:
        result = await self.session.execute(select(Club).where(Club.id == club_id))
        return result.scalar_one_or_none()

    async def get_all(self) -> List[Club]:
        result = await self.session.execute(select(Club))
        return result.scalars().all()

    async def delete(self, club_id: int) -> bool:
        from sqlalchemy import delete as sa_delete
        result = await self.session.execute(sa_delete(Club).where(Club.id == club_id))
        return result.rowcount > 0

    async def count_all(self) -> int:
        result = await self.session.execute(select(func.count()).select_from(Club))
        return result.scalar() or 0

    async def get_post_counts(self) -> list:
        from app.models.domain import Post
        result = await self.session.execute(
            select(Club.id, Club.name, func.count(Post.id).label("post_count"))
            .outerjoin(Post, Post.club_id == Club.id)
            .group_by(Club.id)
            .order_by(func.count(Post.id).desc()))
        return [{"club_id": row[0], "club_name": row[1], "post_count": row[2]} for row in result]
