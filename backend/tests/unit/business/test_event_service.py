"""EventService 单元测试"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.business.impl.event_service_impl import EventServiceImpl
from app.data_access.sqlite_dao.event_dao import IEventDAO
from app.models.dto import EventCreateRequest
from datetime import datetime, timezone


@pytest.fixture
def mock_dao() -> MagicMock:
    return AsyncMock(spec=IEventDAO)


@pytest.fixture
def mock_session() -> MagicMock:
    s = AsyncMock()
    s.commit = AsyncMock()
    return s


@pytest.fixture
def service(mock_dao, mock_session) -> EventServiceImpl:
    return EventServiceImpl(event_dao=mock_dao, db_session=mock_session)


@pytest.mark.asyncio
async def test_create_event(service, mock_dao, mock_session):
    from app.models.domain import Event
    now = datetime.now(timezone.utc)
    mock_dao.insert.return_value = 1
    mock_dao.get_by_id.return_value = Event(
        id=1, title="讲座", description="AI 讲座",
        start_time=now, end_time=now)
    req = EventCreateRequest(title="讲座", description="AI 讲座",
                              start_time=now, end_time=now)
    result = await service.create_event(req)
    assert result.id == 1
    assert result.title == "讲座"
    mock_dao.insert.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_event_by_id_found(service, mock_dao, mock_session):
    from app.models.domain import Event
    now = datetime.now(timezone.utc)
    mock_dao.get_by_id.return_value = Event(
        id=1, title="活动", description="x", start_time=now, end_time=now)
    result = await service.get_event_by_id(1)
    assert result.title == "活动"


@pytest.mark.asyncio
async def test_get_event_by_id_not_found(service, mock_dao, mock_session):
    mock_dao.get_by_id.return_value = None
    assert await service.get_event_by_id(999) is None


@pytest.mark.asyncio
async def test_list_events(service, mock_dao, mock_session):
    from app.models.domain import Event
    now = datetime.now(timezone.utc)
    mock_dao.list_events.return_value = [
        Event(id=1, title="A", description="x", start_time=now, end_time=now),
        Event(id=2, title="B", description="x", start_time=now, end_time=now),
    ]
    result = await service.list_events()
    assert len(result) == 2
