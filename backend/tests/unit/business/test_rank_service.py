"""
功能：RankService 单元测试

测试策略：
    - Mock 掉 IRankRepository、ILikeRepository、IPostDAO、IClubDAO
    - 覆盖正常路径 + 空数据路径

测试用例：
    - test_get_hot_posts: 热帖榜返回正确排序的 PostDTO
    - test_get_hot_posts_empty: 空榜返回空列表
    - test_get_hot_posts_with_tag: 按标签筛选热帖
    - test_get_club_rank: 社团活跃榜排序正确
    - test_get_club_rank_empty: 空社团榜返回空列表
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.business.impl.rank_service_impl import RankServiceImpl
from app.data_access.redis_repo.rank_repo import IRankRepository
from app.data_access.redis_repo.like_repo import ILikeRepository
from app.data_access.sqlite_dao.post_dao import IPostDAO
from app.data_access.sqlite_dao.club_dao import IClubDAO
from app.models.domain import Post, User, Club
from app.models.enums import UserRole


@pytest.fixture
def mock_rank_repo() -> MagicMock:
    return AsyncMock(spec=IRankRepository)


@pytest.fixture
def mock_like_repo() -> MagicMock:
    return AsyncMock(spec=ILikeRepository)


@pytest.fixture
def mock_post_dao() -> MagicMock:
    return AsyncMock(spec=IPostDAO)


@pytest.fixture
def mock_club_dao() -> MagicMock:
    return AsyncMock(spec=IClubDAO)


@pytest.fixture
def service(mock_rank_repo, mock_like_repo, mock_post_dao, mock_club_dao) -> RankServiceImpl:
    return RankServiceImpl(
        rank_repo=mock_rank_repo,
        like_repo=mock_like_repo,
        post_dao=mock_post_dao,
        club_dao=mock_club_dao,
    )


def make_post(post_id: int) -> Post:
    author = User(id=1, student_id="S1", email="a@c.edu", nickname="作者",
                  password_hash="h", role=UserRole.STUDENT)
    return Post(id=post_id, user_id=1, title=f"帖子{post_id}",
                content="内容", tags="课程", author=author,
                is_active=True, view_count=0)


@pytest.mark.asyncio
async def test_get_hot_posts(service, mock_rank_repo, mock_like_repo,
                              mock_post_dao, mock_club_dao):
    """测试热帖榜返回正确排序的 PostDTO"""
    # Arrange
    mock_rank_repo.get_top_members.return_value = [
        ("3", 100.0), ("1", 80.0), ("2", 60.0),
    ]
    mock_post_dao.get_by_id.side_effect = [
        make_post(3), make_post(1), make_post(2),
    ]
    mock_like_repo.get_like_count.side_effect = [30, 20, 10]

    # Act
    result = await service.get_hot_posts(limit=3)

    # Assert
    assert len(result) == 3
    assert result[0].id == 3  # 热度最高
    assert result[1].id == 1
    assert result[2].id == 2
    assert result[0].like_count == 30
    mock_rank_repo.get_top_members.assert_awaited_once_with(
        "hot:posts:day:all", limit=3
    )


@pytest.mark.asyncio
async def test_get_hot_posts_empty(service, mock_rank_repo, mock_like_repo,
                                    mock_post_dao, mock_club_dao):
    """测试空热帖榜"""
    mock_rank_repo.get_top_members.return_value = []

    result = await service.get_hot_posts(limit=10)

    assert len(result) == 0


@pytest.mark.asyncio
async def test_get_hot_posts_with_tag(service, mock_rank_repo, mock_like_repo,
                                       mock_post_dao, mock_club_dao):
    """测试按标签筛选热帖"""
    mock_rank_repo.get_top_members.return_value = [("1", 50.0)]
    mock_post_dao.get_by_id.return_value = make_post(1)
    mock_like_repo.get_like_count.return_value = 10

    result = await service.get_hot_posts(limit=5, tag="课程")

    assert len(result) == 1
    mock_rank_repo.get_top_members.assert_awaited_once_with(
        "hot:posts:day:课程", limit=5
    )


@pytest.mark.asyncio
async def test_get_club_rank(service, mock_rank_repo, mock_like_repo,
                              mock_post_dao, mock_club_dao):
    """测试社团活跃榜"""
    # Arrange
    mock_rank_repo.get_top_members.return_value = [
        ("1", 50.0), ("2", 30.0),
    ]
    mock_club_dao.get_by_id.side_effect = [
        Club(id=1, name="计算机协会"),
        Club(id=2, name="英语社"),
    ]

    # Act
    result = await service.get_club_rank(limit=5)

    # Assert
    assert len(result) == 2
    assert result[0].club_name == "计算机协会"
    assert result[0].post_count == 50
    assert result[0].rank == 1
    assert result[1].club_name == "英语社"
    assert result[1].post_count == 30
    assert result[1].rank == 2


@pytest.mark.asyncio
async def test_get_club_rank_empty(service, mock_rank_repo, mock_like_repo,
                                    mock_post_dao, mock_club_dao):
    """测试空社团榜"""
    mock_rank_repo.get_top_members.return_value = []

    result = await service.get_club_rank(limit=5)

    assert len(result) == 0
