"""社团业务逻辑实现"""
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.business.interfaces.club_service import IClubService
from app.data_access.sqlite_dao.club_dao import IClubDAO
from app.data_access.sqlite_dao.club_member_dao import IClubMemberDAO
from app.data_access.sqlite_dao.user_dao import IUserDAO
from app.data_access.sqlite_dao.user_dao_impl import UserDAOImpl
from app.infrastructure.exceptions import AppException
from app.infrastructure.logger import get_logger
from app.models.domain import Club, ClubMember
from app.models.dto import ClubCreateRequest, ClubDTO, ClubMemberDTO

logger = get_logger(__name__)


class ClubServiceImpl(IClubService):
    """社团服务实现"""

    def __init__(
        self,
        club_dao: IClubDAO,
        db_session: AsyncSession,
        club_member_dao: Optional[IClubMemberDAO] = None,
        user_dao: Optional[IUserDAO] = None,
    ):
        self.club_dao = club_dao
        self.db_session = db_session
        self.club_member_dao = club_member_dao
        self.user_dao = user_dao or UserDAOImpl(db_session)

    async def create_club(self, request: ClubCreateRequest) -> ClubDTO:
        club = Club(name=request.name, description=request.description)
        club_id = await self.club_dao.insert(club)
        await self.db_session.commit()
        logger.info(f"Club created: id={club_id}, name={request.name}")
        created = await self.club_dao.get_by_id(club_id)
        return ClubDTO.model_validate(created)

    async def get_club_by_id(self, club_id: int) -> Optional[ClubDTO]:
        club = await self.club_dao.get_by_id(club_id)
        if club is None:
            return None
        return ClubDTO.model_validate(club)

    async def list_clubs(self) -> List[ClubDTO]:
        clubs = await self.club_dao.get_all()
        return [ClubDTO.model_validate(c) for c in clubs]

    async def join_club(self, user_id: int, club_id: int) -> bool:
        """加入社团"""
        club = await self.club_dao.get_by_id(club_id)
        if club is None:
            raise AppException(status_code=404, code="CLUB_NOT_FOUND", message="社团不存在")
        if self.club_member_dao:
            existing = await self.club_member_dao.is_member(user_id, club_id)
            if existing:
                return True
            member = ClubMember(user_id=user_id, club_id=club_id)
            await self.club_member_dao.add(member)
            await self.db_session.commit()
            logger.info(f"User #{user_id} joined club #{club_id}")
        return True

    async def leave_club(self, user_id: int, club_id: int) -> bool:
        """退出社团"""
        if self.club_member_dao:
            result = await self.club_member_dao.remove(user_id, club_id)
            await self.db_session.commit()
            return result
        return False

    async def get_members(self, club_id: int) -> List[ClubMemberDTO]:
        """获取社团成员列表"""
        if not self.club_member_dao:
            return []
        members = await self.club_member_dao.get_members(club_id)
        result = []
        for m in members:
            user = await self.user_dao.get_by_id(m.user_id)
            result.append(ClubMemberDTO(
                id=m.id,
                user_id=m.user_id,
                club_id=m.club_id,
                role=m.role,
                joined_at=m.joined_at,
                user_nickname=user.nickname if user else None,
                user_avatar=user.avatar_url if user else None,
            ))
        return result

    async def is_member(self, user_id: int, club_id: int) -> bool:
        """检查用户是否已加入社团"""
        if not self.club_member_dao:
            return False
        return await self.club_member_dao.is_member(user_id, club_id)
