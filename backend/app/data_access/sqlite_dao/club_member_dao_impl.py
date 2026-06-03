"""社团成员数据访问实现"""
from typing import List, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.data_access.sqlite_dao.club_member_dao import IClubMemberDAO
from app.models.domain import ClubMember


class ClubMemberDAOImpl(IClubMemberDAO):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, member: ClubMember) -> int:
        self.session.add(member)
        await self.session.flush()
        return member.id

    async def remove(self, user_id: int, club_id: int) -> bool:
        result = await self.session.execute(
            delete(ClubMember).where(
                ClubMember.user_id == user_id,
                ClubMember.club_id == club_id,
            )
        )
        return result.rowcount > 0

    async def is_member(self, user_id: int, club_id: int) -> bool:
        result = await self.session.execute(
            select(ClubMember).where(
                ClubMember.user_id == user_id,
                ClubMember.club_id == club_id,
            )
        )
        return result.scalar_one_or_none() is not None

    async def get_members(self, club_id: int) -> List[ClubMember]:
        result = await self.session.execute(
            select(ClubMember).where(ClubMember.club_id == club_id)
        )
        return result.scalars().all()

    async def get_by_user_and_club(self, user_id: int, club_id: int) -> Optional[ClubMember]:
        result = await self.session.execute(
            select(ClubMember).where(
                ClubMember.user_id == user_id,
                ClubMember.club_id == club_id,
            )
        )
        return result.scalar_one_or_none()
