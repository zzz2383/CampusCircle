"""
功能：社团数据访问实现（SQLite）

调用链路：
    - 被 RankServiceImpl 通过 IClubDAO 接口调用
"""

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.data_access.sqlite_dao.club_dao import IClubDAO
from app.models.domain import Club


class ClubDAOImpl(IClubDAO):
    """社团数据访问实现"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, club_id: int) -> Optional[Club]:
        result = await self.session.execute(
            select(Club).where(Club.id == club_id)
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> List[Club]:
        result = await self.session.execute(select(Club))
        return result.scalars().all()
