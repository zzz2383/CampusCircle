"""社团成员数据访问接口"""
from abc import ABC, abstractmethod
from typing import List, Optional
from app.models.domain import ClubMember


class IClubMemberDAO(ABC):
    @abstractmethod
    async def add(self, member: ClubMember) -> int: ...

    @abstractmethod
    async def remove(self, user_id: int, club_id: int) -> bool: ...

    @abstractmethod
    async def is_member(self, user_id: int, club_id: int) -> bool: ...

    @abstractmethod
    async def get_members(self, club_id: int) -> List[ClubMember]: ...

    @abstractmethod
    async def get_by_user_and_club(self, user_id: int, club_id: int) -> Optional[ClubMember]: ...
