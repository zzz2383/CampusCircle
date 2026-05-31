"""
功能：LikeService 单元测试

测试策略：
    - Mock 掉 ILikeRepository、IRankRepository、IPostDAO
    - 覆盖正常路径 + 异常路径

测试用例：
    - test_like_post_success: 点赞成功
    - test_like_post_twice_idempotent: 重复点赞幂等
    - test_like_post_not_found: 帖子不存在抛异常
    - test_unlike_post_success: 取消点赞成功
    - test_unlike_post_not_liked: 取消未点赞的帖子
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.business.impl.like_service_impl import LikeServiceImpl
from app.data_access.redis_repo.like_repo import ILikeRepository
from app.data_access.redis_repo.rank_repo import IRankRepository
from app.data_access.sqlite_dao.post_dao import IPostDAO
from app.models.domain import Post, User
from app.models.enums import UserRole
from app.infrastructure.exceptions import PostNotFoundError


@pytest.fixture
def mock_like_repo() -> MagicMock:
    return AsyncMock(spec=ILikeRepository)


@pytest.fixture
def mock_rank_repo() -> MagicMock:
    return AsyncMock(spec=IRankRepository)


@pytest.fixture
def mock_post_dao() -> MagicMock:
    return AsyncMock(spec=IPostDAO)


@pytest.fixture
def service(mock_like_repo, mock_rank_repo, mock_post_dao) -> LikeServiceImpl:
    return LikeServiceImpl(
        like_repo=mock_like_repo,
        rank_repo=mock_rank_repo,
        post_dao=mock_post_dao,
    )


def make_post(post_id: int = 1, tags: str = "课程") -> Post:
    """辅助：创建测试帖子"""
    author = User(
        id=1, student_id="2024001", email="a@campus.edu",
        nickname="作者", password_hash="h", role=UserRole.STUDENT,
    )
    return Post(
        id=post_id, user_id=1, title="测试", content="内容",
        tags=tags, author=author, is_active=True,
    )


@pytest.mark.asyncio
async def test_like_post_success(service, mock_like_repo, mock_rank_repo, mock_post_dao):
    """测试点赞成功"""
    # Arrange
    mock_post_dao.get_by_id.return_value = make_post(post_id=1, tags="课程")
    mock_like_repo.add_like.return_value = 3  # 当前总赞数

    # Act
    result = await service.like_post(user_id=5, post_id=1)

    # Assert
    assert result.is_liked is True
    assert result.like_count == 3
    mock_like_repo.add_like.assert_awaited_once_with(1, 5)
    # 验证热榜加分（全站榜 + 标签榜各一次）
    assert mock_rank_repo.increment_score.await_count == 2
    mock_rank_repo.increment_score.assert_any_call("hot:posts:day:all", "1", 2)
    mock_rank_repo.increment_score.assert_any_call("hot:posts:day:课程", "1", 2)


@pytest.mark.asyncio
async def test_like_post_twice_idempotent(service, mock_like_repo, mock_rank_repo, mock_post_dao):
    """测试重复点赞幂等"""
    # Arrange
    mock_post_dao.get_by_id.return_value = make_post(post_id=1)
    # 第一次点赞返回 1，再次点赞因为 SADD 幂等仍返回 1
    mock_like_repo.add_like.side_effect = [1, 1]

    # Act - 第一次点赞
    r1 = await service.like_post(user_id=5, post_id=1)
    assert r1.like_count == 1

    # Act - 再次点赞
    r2 = await service.like_post(user_id=5, post_id=1)
    assert r2.like_count == 1  # 仍然只有 1 人点赞

    # 每次点赞都会触发热榜加分（全站 + 标签各一次）
    assert mock_rank_repo.increment_score.await_count == 4


@pytest.mark.asyncio
async def test_like_post_not_found(service, mock_like_repo, mock_rank_repo, mock_post_dao):
    """测试帖子不存在抛出异常"""
    # Arrange
    mock_post_dao.get_by_id.return_value = None

    # Act & Assert
    with pytest.raises(PostNotFoundError):
        await service.like_post(user_id=5, post_id=999)
    mock_like_repo.add_like.assert_not_awaited()


@pytest.mark.asyncio
async def test_unlike_post_success(service, mock_like_repo, mock_rank_repo, mock_post_dao):
    """测试取消点赞成功"""
    # Arrange
    mock_post_dao.get_by_id.return_value = make_post(post_id=1)
    mock_like_repo.remove_like.return_value = 2  # 取消后还剩 2 人

    # Act
    result = await service.unlike_post(user_id=5, post_id=1)

    # Assert
    assert result.is_liked is False
    assert result.like_count == 2
    mock_like_repo.remove_like.assert_awaited_once_with(1, 5)


@pytest.mark.asyncio
async def test_unlike_post_not_liked(service, mock_like_repo, mock_rank_repo, mock_post_dao):
    """测试取消未点赞的帖子（幂等）"""
    # Arrange
    mock_post_dao.get_by_id.return_value = make_post(post_id=1)
    mock_like_repo.remove_like.return_value = 0  # 没点过赞

    # Act
    result = await service.unlike_post(user_id=5, post_id=1)

    # Assert
    assert result.is_liked is False
    assert result.like_count == 0
