"""LostItemDAO 单元测试"""
import pytest
from sqlalchemy import select
from app.data_access.sqlite_dao.lost_item_dao_impl import LostItemDAOImpl
from app.models.domain import LostItem


@pytest.mark.asyncio
async def test_insert_item(db_session):
    dao = LostItemDAOImpl(db_session)
    item = LostItem(user_id=1, title="丢失钱包", description="黑色钱包",
                    location="食堂", contact="10086", is_lost=True)
    iid = await dao.insert(item)
    assert iid > 0

    result = await db_session.execute(select(LostItem).where(LostItem.id == iid))
    assert result.scalar_one().title == "丢失钱包"


@pytest.mark.asyncio
async def test_get_by_id_found(db_session):
    dao = LostItemDAOImpl(db_session)
    item = LostItem(user_id=1, title="捡到钥匙", description="一串钥匙",
                    location="图书馆", is_lost=False)
    iid = await dao.insert(item)

    found = await dao.get_by_id(iid)
    assert found is not None
    assert found.title == "捡到钥匙"


@pytest.mark.asyncio
async def test_get_by_id_not_found(db_session):
    dao = LostItemDAOImpl(db_session)
    assert await dao.get_by_id(999) is None


@pytest.mark.asyncio
async def test_list_items_all(db_session):
    dao = LostItemDAOImpl(db_session)
    for i in range(3):
        await dao.insert(LostItem(user_id=1, title=f"物品{i}", description="x",
                                   is_lost=True))
    items = await dao.list_items(offset=0, limit=10)
    assert len(items) == 3


@pytest.mark.asyncio
async def test_list_items_filter_lost(db_session):
    dao = LostItemDAOImpl(db_session)
    await dao.insert(LostItem(user_id=1, title="丢失", description="x", is_lost=True))
    await dao.insert(LostItem(user_id=1, title="拾到", description="x", is_lost=False))

    lost = await dao.list_items(is_lost=True)
    found = await dao.list_items(is_lost=False)
    assert len(lost) == 1
    assert lost[0].title == "丢失"
    assert len(found) == 1
    assert found[0].title == "拾到"


@pytest.mark.asyncio
async def test_mark_as_found(db_session):
    dao = LostItemDAOImpl(db_session)
    iid = await dao.insert(LostItem(user_id=1, title="丢失", description="x", is_lost=True))

    result = await dao.mark_as_found(iid)
    assert result is True

    item = await dao.get_by_id(iid)
    assert item.is_found is True


@pytest.mark.asyncio
async def test_mark_as_found_not_exist(db_session):
    dao = LostItemDAOImpl(db_session)
    result = await dao.mark_as_found(999)
    assert result is False
