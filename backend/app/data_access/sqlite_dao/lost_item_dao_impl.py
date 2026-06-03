"""失物招领数据访问实现"""
from typing import List, Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.data_access.sqlite_dao.lost_item_dao import ILostItemDAO
from app.models.domain import LostItem


class LostItemDAOImpl(ILostItemDAO):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def insert(self, item: LostItem) -> int:
        self.session.add(item)
        await self.session.flush()
        return item.id

    async def get_by_id(self, item_id: int) -> Optional[LostItem]:
        result = await self.session.execute(
            select(LostItem).where(LostItem.id == item_id))
        return result.scalar_one_or_none()

    async def list_items(
        self, is_lost: Optional[bool] = None, offset: int = 0, limit: int = 20
    ) -> List[LostItem]:
        query = select(LostItem).order_by(LostItem.created_at.desc())
        if is_lost is not None:
            query = query.where(LostItem.is_lost == is_lost)
        result = await self.session.execute(query.offset(offset).limit(limit))
        return result.scalars().all()

    async def mark_as_found(self, item_id: int) -> bool:
        result = await self.session.execute(
            update(LostItem).where(LostItem.id == item_id).values(is_found=True))
        return result.rowcount > 0

    async def delete(self, item_id: int) -> bool:
        from sqlalchemy import delete as sa_delete
        result = await self.session.execute(
            sa_delete(LostItem).where(LostItem.id == item_id))
        return result.rowcount > 0

    async def count_all(self) -> int:
        from sqlalchemy import func
        result = await self.session.execute(
            select(func.count()).select_from(LostItem))
        return result.scalar() or 0
