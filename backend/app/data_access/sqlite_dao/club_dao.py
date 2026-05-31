"""
功能：社团数据访问对象接口

调用链路：
    - 被业务层的 RankService 调用
    - 由 club_dao_impl.py 实现
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from app.models.domain import Club


class IClubDAO(ABC):
    """社团数据访问接口"""

    @abstractmethod
    async def get_by_id(self, club_id: int) -> Optional[Club]:
        """根据 ID 查询社团"""
        ...

    @abstractmethod
    async def get_all(self) -> List[Club]:
        """获取所有社团"""
        ...
