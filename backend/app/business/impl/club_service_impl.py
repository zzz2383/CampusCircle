"""
功能：社团业务逻辑实现
"""

from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.business.interfaces.club_service import IClubService
from app.data_access.sqlite_dao.club_dao import IClubDAO
from app.infrastructure.logger import get_logger
from app.models.domain import Club
from app.models.dto import ClubCreateRequest, ClubDTO

logger = get_logger(__name__)


class ClubServiceImpl(IClubService):
    """社团服务实现"""

    def __init__(self, club_dao: IClubDAO, db_session: AsyncSession):
        self.club_dao = club_dao
        self.db_session = db_session

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
