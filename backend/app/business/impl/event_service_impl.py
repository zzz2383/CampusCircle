"""事件业务逻辑实现"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.business.interfaces.event_service import IEventService
from app.data_access.sqlite_dao.event_dao import IEventDAO
from app.data_access.sqlite_dao.event_participant_dao import IEventParticipantDAO
from app.data_access.sqlite_dao.user_dao import IUserDAO
from app.data_access.sqlite_dao.user_dao_impl import UserDAOImpl
from app.data_access.redis_repo.event_registration_repo import IEventRegistrationRepo
from app.infrastructure.exceptions import AppException
from app.infrastructure.logger import get_logger
from app.models.domain import Event, EventParticipant
from app.models.dto import EventCreateRequest, EventUpdateRequest, EventDTO, EventParticipantDTO

logger = get_logger(__name__)


class EventServiceImpl(IEventService):
    def __init__(
        self,
        event_dao: IEventDAO,
        db_session: AsyncSession,
        participant_dao: Optional[IEventParticipantDAO] = None,
        registration_repo: Optional[IEventRegistrationRepo] = None,
        user_dao: Optional[IUserDAO] = None,
    ):
        self.event_dao = event_dao
        self.db_session = db_session
        self.participant_dao = participant_dao
        self.registration_repo = registration_repo
        self.user_dao = user_dao or UserDAOImpl(db_session)

    async def _to_dto(self, event: Event, current_user_id: Optional[int] = None) -> EventDTO:
        count = 0
        is_registered = False
        if self.registration_repo:
            count = await self.registration_repo.get_participant_count(event.id)
            if current_user_id:
                is_registered = await self.registration_repo.is_registered(event.id, current_user_id)
        return EventDTO(
            id=event.id,
            title=event.title,
            description=event.description,
            location=event.location,
            max_participants=event.max_participants,
            club_id=event.club_id,
            participant_count=count,
            is_registered=is_registered,
            start_time=event.start_time,
            end_time=event.end_time,
            created_at=event.created_at,
        )

    async def create_event(self, request: EventCreateRequest) -> EventDTO:
        event = Event(
            title=request.title, description=request.description,
            location=request.location, max_participants=request.max_participants,
            club_id=request.club_id, start_time=request.start_time, end_time=request.end_time,
        )
        eid = await self.event_dao.insert(event)
        await self.db_session.commit()
        logger.info(f"Event created: id={eid}, title={request.title}")
        created = await self.event_dao.get_by_id(eid)
        return await self._to_dto(created)

    async def get_event_by_id(self, event_id: int, current_user_id: Optional[int] = None) -> Optional[EventDTO]:
        event = await self.event_dao.get_by_id(event_id)
        if event is None:
            return None
        return await self._to_dto(event, current_user_id=current_user_id)

    async def list_events(self, offset: int = 0, limit: int = 20, club_id: Optional[int] = None,
                         current_user_id: Optional[int] = None) -> List[EventDTO]:
        events = await self.event_dao.list_events(offset=offset, limit=limit, club_id=club_id)
        return [await self._to_dto(e, current_user_id=current_user_id) for e in events]

    async def update_event(self, event_id: int, request: EventUpdateRequest) -> Optional[EventDTO]:
        event = await self.event_dao.get_by_id(event_id)
        if event is None:
            return None
        update_data = request.model_dump(exclude_none=True)
        if not update_data:
            return await self._to_dto(event)
        for key, value in update_data.items():
            setattr(event, key, value)
        await self.db_session.commit()
        logger.info(f"Event updated: id={event_id}, fields={list(update_data.keys())}")
        updated = await self.event_dao.get_by_id(event_id)
        return await self._to_dto(updated)

    async def delete_event(self, event_id: int) -> bool:
        event = await self.event_dao.get_by_id(event_id)
        if event is None:
            return False
        await self.db_session.delete(event)
        await self.db_session.commit()
        logger.info(f"Event deleted: id={event_id}")
        return True

    async def register_event(self, user_id: int, event_id: int) -> bool:
        event = await self.event_dao.get_by_id(event_id)
        if event is None:
            raise AppException(status_code=404, code="EVENT_NOT_FOUND", message="活动不存在")
        if event.max_participants and self.registration_repo:
            count = await self.registration_repo.get_participant_count(event_id)
            if count >= event.max_participants:
                raise AppException(status_code=400, code="EVENT_FULL", message="活动人数已满")

        # Redis (real-time count + dedup)
        if self.registration_repo:
            already = await self.registration_repo.is_registered(event_id, user_id)
            if already:
                return True  # 幂等
            await self.registration_repo.add_participant(event_id, user_id)

        # SQLite (persistent record)
        if self.participant_dao:
            p = EventParticipant(user_id=user_id, event_id=event_id)
            await self.participant_dao.add(p)
        await self.db_session.commit()
        logger.info(f"User #{user_id} registered for event #{event_id}")
        return True

    async def cancel_registration(self, user_id: int, event_id: int) -> bool:
        if self.registration_repo:
            await self.registration_repo.remove_participant(event_id, user_id)
        if self.participant_dao:
            result = await self.participant_dao.remove(user_id, event_id)
            await self.db_session.commit()
            return result
        return False

    async def get_participants(self, event_id: int) -> List[EventParticipantDTO]:
        if not self.participant_dao:
            return []
        participants = await self.participant_dao.list_participants(event_id)
        result = []
        for p in participants:
            user = await self.user_dao.get_by_id(p.user_id)
            result.append(EventParticipantDTO(
                id=p.id, user_id=p.user_id, event_id=p.event_id,
                user_nickname=user.nickname if user else None,
                user_avatar=user.avatar_url if user else None, created_at=p.created_at,
            ))
        return result

    async def get_participant_count(self, event_id: int) -> int:
        if self.registration_repo:
            return await self.registration_repo.get_participant_count(event_id)
        return 0
