"""
功能：ClubService 单元测试

测试用例：
    - test_create_club: 创建社团
    - test_get_club_by_id_found: 按 ID 查询
    - test_get_club_by_id_not_found: 不存在的社团
    - test_list_clubs: 获取所有社团
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.business.impl.club_service_impl import ClubServiceImpl
from app.data_access.sqlite_dao.club_dao import IClubDAO
from app.models.domain import Club
from app.models.dto import ClubCreateRequest


@pytest.fixture
def mock_club_dao() -> MagicMock:
    return AsyncMock(spec=IClubDAO)


@pytest.fixture
def mock_session() -> MagicMock:
    s = AsyncMock()
    s.commit = AsyncMock()
    return s


@pytest.fixture
def service(mock_club_dao, mock_session) -> ClubServiceImpl:
    return ClubServiceImpl(club_dao=mock_club_dao, db_session=mock_session)


@pytest.mark.asyncio
async def test_create_club(service, mock_club_dao, mock_session):
    """测试创建社团"""
    mock_club_dao.insert.return_value = 1
    mock_club_dao.get_by_id.return_value = Club(
        id=1, name="计算机协会", description="编程爱好者聚集地"
    )

    request = ClubCreateRequest(name="计算机协会", description="编程爱好者聚集地")
    result = await service.create_club(request)

    assert result.id == 1
    assert result.name == "计算机协会"
    assert result.description == "编程爱好者聚集地"
    mock_club_dao.insert.assert_awaited_once()
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_club_by_id_found(service, mock_club_dao, mock_session):
    """测试按 ID 查询"""
    mock_club_dao.get_by_id.return_value = Club(
        id=1, name="英语社", description="英语学习交流"
    )

    result = await service.get_club_by_id(1)

    assert result is not None
    assert result.name == "英语社"
    mock_club_dao.get_by_id.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_get_club_by_id_not_found(service, mock_club_dao, mock_session):
    """测试不存在的社团"""
    mock_club_dao.get_by_id.return_value = None
    result = await service.get_club_by_id(999)
    assert result is None


@pytest.mark.asyncio
async def test_list_clubs(service, mock_club_dao, mock_session):
    """测试获取所有社团"""
    mock_club_dao.get_all.return_value = [
        Club(id=1, name="计算机协会"),
        Club(id=2, name="英语社"),
    ]

    result = await service.list_clubs()

    assert len(result) == 2
    assert result[0].name == "计算机协会"
    assert result[1].name == "英语社"
