"""社团业务逻辑接口"""
from abc import ABC, abstractmethod
from typing import List, Optional

from app.models.dto import ClubCreateRequest, ClubDTO, ClubMemberDTO


class IClubService(ABC):
    """社团服务接口"""

    @abstractmethod
    async def create_club(self, request: ClubCreateRequest) -> ClubDTO:
        """创建社团"""
        ...

    @abstractmethod
    async def get_club_by_id(self, club_id: int) -> Optional[ClubDTO]:
        """获取社团详情"""
        ...

    @abstractmethod
    async def list_clubs(self) -> List[ClubDTO]:
        """获取所有社团"""
        ...

    @abstractmethod
    async def join_club(self, user_id: int, club_id: int) -> bool:
        """加入社团"""
        ...

    @abstractmethod
    async def leave_club(self, user_id: int, club_id: int) -> bool:
        """退出社团"""
        ...

    @abstractmethod
    async def get_members(self, club_id: int) -> List[ClubMemberDTO]:
        """获取社团成员列表"""
        ...

    @abstractmethod
    async def is_member(self, user_id: int, club_id: int) -> bool:
        """检查用户是否已加入社团"""
        ...
