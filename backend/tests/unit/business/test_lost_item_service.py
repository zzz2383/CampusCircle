"""LostItemService 单元测试"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.business.impl.lost_item_service_impl import LostItemServiceImpl
from app.data_access.sqlite_dao.lost_item_dao import ILostItemDAO
from app.data_access.sqlite_dao.user_dao import IUserDAO
from app.data_access.redis_repo.lost_item_repo import ILostItemRepository
from app.infrastructure.exceptions import AppException
from app.models.dto import LostItemCreateRequest
from datetime import datetime, timezone


@pytest.fixture
def mock_dao() -> MagicMock:
    return AsyncMock(spec=ILostItemDAO)


@pytest.fixture
def mock_repo() -> MagicMock:
    return AsyncMock(spec=ILostItemRepository)


@pytest.fixture
def mock_user_dao() -> MagicMock:
    return AsyncMock(spec=IUserDAO)


@pytest.fixture
def mock_session() -> MagicMock:
    s = AsyncMock()
    s.commit = AsyncMock()
    return s


@pytest.fixture
def service(mock_dao, mock_repo, mock_session, mock_user_dao) -> LostItemServiceImpl:
    return LostItemServiceImpl(
        lost_item_dao=mock_dao,
        lost_item_repo=mock_repo,
        db_session=mock_session,
        user_dao=mock_user_dao,
    )


@pytest.mark.asyncio
async def test_create_item_success(service, mock_dao, mock_repo, mock_session, mock_user_dao):
    from app.models.domain import LostItem
    now = datetime.now(timezone.utc)
    mock_dao.insert.return_value = 1
    mock_dao.get_by_id.return_value = LostItem(
        id=1, user_id=1, title="丢失钱包", description="黑色钱包",
        location="食堂", contact="10086", is_lost=True, is_found=False,
        expires_at=now, created_at=now)
    mock_user_dao.get_by_id.return_value = MagicMock(nickname="张三")

    req = LostItemCreateRequest(title="丢失钱包", description="黑色钱包",
                                 location="食堂", contact="10086")
    result = await service.create_item(user_id=1, request=req)

    assert result.id == 1
    assert result.title == "丢失钱包"
    assert result.author_nickname == "张三"
    mock_dao.insert.assert_awaited_once()
    mock_repo.set_expiry.assert_awaited_once_with(1, 604800)
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_item_by_id_found(service, mock_dao, mock_repo, mock_user_dao):
    from app.models.domain import LostItem
    now = datetime.now(timezone.utc)
    mock_dao.get_by_id.return_value = LostItem(
        id=1, user_id=1, title="钥匙", description="一串钥匙",
        is_lost=False, is_found=False, expires_at=now, created_at=now)
    mock_repo.exists.return_value = True
    mock_user_dao.get_by_id.return_value = MagicMock(nickname="李四")

    result = await service.get_item_by_id(1)
    assert result is not None
    assert result.title == "钥匙"


@pytest.mark.asyncio
async def test_get_item_by_id_expired(service, mock_dao, mock_repo):
    from app.models.domain import LostItem
    now = datetime.now(timezone.utc)
    mock_dao.get_by_id.return_value = LostItem(
        id=1, user_id=1, title="过期物品", description="x",
        is_lost=True, is_found=False, expires_at=now, created_at=now)
    mock_repo.exists.return_value = False

    result = await service.get_item_by_id(1)
    assert result is None


@pytest.mark.asyncio
async def test_get_item_by_id_not_found(service, mock_dao, mock_repo):
    mock_dao.get_by_id.return_value = None
    assert await service.get_item_by_id(999) is None
    mock_repo.exists.assert_not_called()


@pytest.mark.asyncio
async def test_list_items(service, mock_dao, mock_repo, mock_user_dao):
    from app.models.domain import LostItem
    now = datetime.now(timezone.utc)
    items = [
        LostItem(id=1, user_id=1, title="A", description="x", is_lost=True, is_found=False, created_at=now),
        LostItem(id=2, user_id=1, title="B", description="x", is_lost=True, is_found=False, created_at=now),
    ]
    mock_dao.list_items.return_value = items
    mock_repo.exists.side_effect = [True, True]
    mock_user_dao.get_by_id.return_value = MagicMock(nickname="王五")

    result = await service.list_items()
    assert len(result) == 2


@pytest.mark.asyncio
async def test_list_items_filters_expired(service, mock_dao, mock_repo, mock_user_dao):
    from app.models.domain import LostItem
    now = datetime.now(timezone.utc)
    items = [
        LostItem(id=1, user_id=1, title="有效", description="x", is_lost=True, is_found=False, created_at=now),
        LostItem(id=2, user_id=1, title="过期", description="x", is_lost=True, is_found=False, created_at=now),
    ]
    mock_dao.list_items.return_value = items
    mock_repo.exists.side_effect = [True, False]
    mock_user_dao.get_by_id.return_value = MagicMock(nickname="王五")

    result = await service.list_items()
    assert len(result) == 1
    assert result[0].title == "有效"


@pytest.mark.asyncio
async def test_mark_as_found_success(service, mock_dao, mock_repo, mock_session):
    from app.models.domain import LostItem
    now = datetime.now(timezone.utc)
    mock_dao.get_by_id.return_value = LostItem(
        id=1, user_id=1, title="物品", description="x", is_lost=True, created_at=now)
    mock_dao.mark_as_found.return_value = True

    result = await service.mark_as_found(item_id=1, user_id=1)
    assert result is True
    mock_repo.remove_expiry.assert_awaited_once_with(1)
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_mark_as_found_not_owner(service, mock_dao, mock_repo):
    from app.models.domain import LostItem
    now = datetime.now(timezone.utc)
    mock_dao.get_by_id.return_value = LostItem(
        id=1, user_id=1, title="物品", description="x", is_lost=True, created_at=now)

    with pytest.raises(AppException) as exc:
        await service.mark_as_found(item_id=1, user_id=2)
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_mark_as_found_not_found(service, mock_dao, mock_repo):
    mock_dao.get_by_id.return_value = None
    result = await service.mark_as_found(item_id=999, user_id=1)
    assert result is False
