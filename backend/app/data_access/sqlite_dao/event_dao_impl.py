"""事件数据访问实现"""
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.data_access.sqlite_dao.event_dao import IEventDAO
from app.models.domain import Event


class EventDAOImpl(IEventDAO):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def insert(self, event: Event) -> int:
        self.session.add(event)
        await self.session.flush()
        return event.id

    async def get_by_id(self, event_id: int) -> Optional[Event]:
        result = await self.session.execute(
            select(Event).where(Event.id == event_id))
        return result.scalar_one_or_none()

    async def list_events(self, offset: int = 0, limit: int = 20, club_id: Optional[int] = None) -> List[Event]:
        query = select(Event).order_by(Event.created_at.desc())
        if club_id is not None:
            query = query.where(Event.club_id == club_id)
        result = await self.session.execute(query.offset(offset).limit(limit))
        return result.scalars().all()

    async def delete(self, event_id: int) -> bool:
        from sqlalchemy import delete as sa_delete
        result = await self.session.execute(
            sa_delete(Event).where(Event.id == event_id))
        return result.rowcount > 0

    async def count_all(self) -> int:
        from sqlalchemy import func
        result = await self.session.execute(
            select(func.count()).select_from(Event))
        return result.scalar() or 0
