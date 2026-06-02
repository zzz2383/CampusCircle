"""EventDAO 单元测试"""
import pytest
from sqlalchemy import select
from app.data_access.sqlite_dao.event_dao_impl import EventDAOImpl
from app.models.domain import Event
from datetime import datetime, timezone


@pytest.mark.asyncio
async def test_insert_event(db_session):
    dao = EventDAOImpl(db_session)
    now = datetime.now(timezone.utc)
    e = Event(title="讲座", description="AI 讲座", location="A101",
              start_time=now, end_time=now)
    eid = await dao.insert(e)
    assert eid > 0

    result = await db_session.execute(select(Event).where(Event.id == eid))
    assert result.scalar_one().title == "讲座"


@pytest.mark.asyncio
async def test_get_by_id_found(db_session):
    dao = EventDAOImpl(db_session)
    now = datetime.now(timezone.utc)
    e = Event(title="测试活动", description="测试", start_time=now, end_time=now)
    eid = await dao.insert(e)

    found = await dao.get_by_id(eid)
    assert found is not None
    assert found.title == "测试活动"


@pytest.mark.asyncio
async def test_get_by_id_not_found(db_session):
    dao = EventDAOImpl(db_session)
    assert await dao.get_by_id(999) is None


@pytest.mark.asyncio
async def test_list_events(db_session):
    dao = EventDAOImpl(db_session)
    now = datetime.now(timezone.utc)
    for i in range(3):
        await dao.insert(Event(title=f"活动{i}", description="x",
                                start_time=now, end_time=now))

    events = await dao.list_events(offset=0, limit=10)
    assert len(events) == 3
