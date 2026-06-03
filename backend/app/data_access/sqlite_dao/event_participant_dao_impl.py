"""活动报名数据访问实现"""
from typing import List, Optional
from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.data_access.sqlite_dao.event_participant_dao import IEventParticipantDAO
from app.models.domain import EventParticipant


class EventParticipantDAOImpl(IEventParticipantDAO):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, participant: EventParticipant) -> int:
        self.session.add(participant)
        await self.session.flush()
        return participant.id

    async def remove(self, user_id: int, event_id: int) -> bool:
        result = await self.session.execute(
            delete(EventParticipant).where(
                EventParticipant.user_id == user_id,
                EventParticipant.event_id == event_id,
            )
        )
        return result.rowcount > 0

    async def is_participant(self, user_id: int, event_id: int) -> bool:
        result = await self.session.execute(
            select(EventParticipant).where(
                EventParticipant.user_id == user_id,
                EventParticipant.event_id == event_id,
            )
        )
        return result.scalar_one_or_none() is not None

    async def count(self, event_id: int) -> int:
        result = await self.session.execute(
            select(func.count()).select_from(EventParticipant).where(
                EventParticipant.event_id == event_id)
        )
        return result.scalar() or 0

    async def list_participants(self, event_id: int) -> List[EventParticipant]:
        result = await self.session.execute(
            select(EventParticipant).where(EventParticipant.event_id == event_id)
        )
        return result.scalars().all()
