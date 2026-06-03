"""事件业务逻辑实现"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.business.interfaces.event_service import IEventService
from app.data_access.sqlite_dao.event_dao import IEventDAO
from app.infrastructure.logger import get_logger
from app.models.domain import Event
from app.models.dto import EventCreateRequest, EventDTO

logger = get_logger(__name__)


class EventServiceImpl(IEventService):
    def __init__(self, event_dao: IEventDAO, db_session: AsyncSession):
        self.event_dao = event_dao
        self.db_session = db_session

    async def create_event(self, request: EventCreateRequest) -> EventDTO:
        event = Event(
            title=request.title,
            description=request.description,
            location=request.location,
            max_participants=request.max_participants,
            club_id=request.club_id,
            start_time=request.start_time,
            end_time=request.end_time,
        )
        eid = await self.event_dao.insert(event)
        await self.db_session.commit()
        logger.info(f"Event created: id={eid}, title={request.title}")
        created = await self.event_dao.get_by_id(eid)
        return EventDTO.model_validate(created)

    async def get_event_by_id(self, event_id: int) -> Optional[EventDTO]:
        event = await self.event_dao.get_by_id(event_id)
        return EventDTO.model_validate(event) if event else None

    async def list_events(self, offset: int = 0, limit: int = 20, club_id: Optional[int] = None) -> List[EventDTO]:
        events = await self.event_dao.list_events(offset=offset, limit=limit, club_id=club_id)
        return [EventDTO.model_validate(e) for e in events]
