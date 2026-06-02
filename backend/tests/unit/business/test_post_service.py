"""
功能：PostService 单元测试

测试策略：
    - Mock 掉 IPostDAO 依赖
    - Mock 掉 IUserService 依赖（用于校验用户存在）
    - 覆盖正常路径 + 异常路径

测试用例：
    - test_create_post_success: 发布成功
    - test_delete_post_success: 作者删除帖子
    - test_delete_post_not_owner: 非作者删除抛异常
    - test_get_post_by_id_found: 查询存在的帖子
    - test_get_post_by_id_not_found: 查询不存在的帖子
    - test_list_posts: 分页列表
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.business.impl.post_service_impl import PostServiceImpl
from app.data_access.sqlite_dao.post_dao import IPostDAO
from app.models.domain import Post, User
from app.models.dto import PostCreateRequest
from app.models.enums import UserRole
from app.infrastructure.exceptions import PostNotFoundError, BusinessError


@pytest.fixture
def mock_post_dao() -> MagicMock:
    return AsyncMock(spec=IPostDAO)


@pytest.fixture
def mock_session() -> MagicMock:
    session = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    return session


@pytest.fixture
def service(mock_post_dao, mock_session) -> PostServiceImpl:
    return PostServiceImpl(post_dao=mock_post_dao, db_session=mock_session)


def make_post(post_id: int = 1, user_id: int = 1, title: str = "测试帖子") -> Post:
    """辅助：创建测试 Post ORM 对象"""
    author = User(
        id=user_id, student_id="2024001", email="a@campus.edu",
        nickname="作者", password_hash="h", role=UserRole.STUDENT,
    )
    return Post(
        id=post_id, user_id=user_id, title=title,
        content="测试内容", tags="课程", author=author,
        is_active=True, view_count=0,
    )


@pytest.mark.asyncio
async def test_create_post_success(service, mock_post_dao, mock_session):
    """测试发布帖子成功"""
    # Arrange
    mock_post_dao.insert.return_value = 1
    mock_post_dao.get_by_id.return_value = make_post(
        post_id=1, user_id=1, title="新帖子"
    )
    request = PostCreateRequest(title="新帖子", content="正文内容", tags="课程")

    # Act
    result = await service.create_post(user_id=1, request=request)

    # Assert
    assert result.id == 1
    assert result.title == "新帖子"
    assert result.tags == "课程"
    mock_post_dao.insert.assert_awaited_once()
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_post_by_id_found(service, mock_post_dao, mock_session):
    """测试查询存在的帖子"""
    # Arrange
    mock_post_dao.get_by_id.return_value = make_post(post_id=1)

    # Act
    result = await service.get_post_by_id(1)

    # Assert
    assert result is not None
    assert result.id == 1
    assert result.title == "测试帖子"
    assert result.author_nickname == "作者"
    mock_post_dao.get_by_id.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_get_post_by_id_not_found(service, mock_post_dao, mock_session):
    """测试查询不存在的帖子抛出 PostNotFoundError"""
    # Arrange
    mock_post_dao.get_by_id.return_value = None

    # Act & Assert
    with pytest.raises(PostNotFoundError):
        await service.get_post_by_id(999)


@pytest.mark.asyncio
async def test_delete_post_success(service, mock_post_dao, mock_session):
    """测试作者删除帖子成功"""
    # Arrange
    mock_post_dao.get_by_id.return_value = make_post(post_id=1, user_id=1)
    mock_post_dao.delete.return_value = True

    # Act
    result = await service.delete_post(post_id=1, user_id=1)

    # Assert
    assert result is True
    mock_post_dao.delete.assert_awaited_once_with(1)
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_post_not_owner(service, mock_post_dao, mock_session):
    """测试非作者删除帖子抛 BusinessError"""
    # Arrange
    mock_post_dao.get_by_id.return_value = make_post(post_id=1, user_id=1)

    # Act & Assert
    with pytest.raises(BusinessError) as exc:
        await service.delete_post(post_id=1, user_id=2)
    assert "权限" in str(exc.value.message) or "作者" in str(exc.value.message)
    mock_post_dao.delete.assert_not_awaited()


@pytest.mark.asyncio
async def test_list_posts(service, mock_post_dao, mock_session):
    """测试分页列表"""
    # Arrange
    mock_post_dao.list_latest.return_value = [
        make_post(post_id=3, user_id=1),
        make_post(post_id=2, user_id=1),
    ]

    # Act
    result = await service.list_posts(offset=0, limit=10)

    # Assert
    assert len(result.items) == 2
    assert result.total >= 0
    assert result.offset == 0
    assert result.limit == 10
    mock_post_dao.list_latest.assert_awaited_once_with(offset=0, limit=10, tag=None)


@pytest.mark.asyncio
async def test_increment_view_count_success(service, mock_post_dao, mock_session):
    """测试增加浏览量"""
    mock_post_dao.increment_view_count.return_value = 5

    result = await service.increment_view_count(post_id=1)

    assert result == 5
    mock_post_dao.increment_view_count.assert_awaited_once_with(1)
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_post_dto_has_real_comment_count(service, mock_post_dao, mock_session):
    """测试 PostDTO 的 comment_count 来自数据库"""
    post = make_post(post_id=1, user_id=1)
    mock_post_dao.get_by_id.return_value = post
    mock_post_dao.count_comments.return_value = 5

    result = await service.get_post_by_id(post_id=1)

    assert result.comment_count == 5
    mock_post_dao.count_comments.assert_awaited_once_with(1)
