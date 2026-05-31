"""
功能：CommentService 单元测试

测试用例：
    - test_create_comment_success: 发表评论成功
    - test_create_comment_post_not_found: 帖子不存在抛异常
    - test_get_comments: 获取评论列表
    - test_delete_comment_success: 作者删除评论
    - test_delete_comment_not_owner: 非作者抛异常
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.business.impl.comment_service_impl import CommentServiceImpl
from app.data_access.sqlite_dao.comment_dao import ICommentDAO
from app.data_access.sqlite_dao.post_dao import IPostDAO
from app.models.domain import Comment, Post, User
from app.models.dto import CommentCreateRequest
from app.models.enums import UserRole
from app.infrastructure.exceptions import PostNotFoundError, BusinessError


@pytest.fixture
def mock_comment_dao() -> MagicMock:
    return AsyncMock(spec=ICommentDAO)


@pytest.fixture
def mock_post_dao() -> MagicMock:
    return AsyncMock(spec=IPostDAO)


@pytest.fixture
def mock_session() -> MagicMock:
    s = AsyncMock()
    s.commit = AsyncMock()
    return s


@pytest.fixture
def service(mock_comment_dao, mock_post_dao, mock_session) -> CommentServiceImpl:
    return CommentServiceImpl(
        comment_dao=mock_comment_dao,
        post_dao=mock_post_dao,
        db_session=mock_session,
    )


def make_post(post_id: int = 1) -> Post:
    author = User(id=1, student_id="S1", email="a@c.edu", nickname="作者",
                  password_hash="h", role=UserRole.STUDENT)
    return Post(id=post_id, user_id=1, title="测试", content="内容",
                tags="课程", author=author, is_active=True, view_count=0)


def make_comment(cid: int = 1, post_id: int = 1, uid: int = 2) -> Comment:
    author = User(id=uid, student_id="S2", email="b@c.edu", nickname="评论者",
                  password_hash="h", role=UserRole.STUDENT)
    return Comment(id=cid, post_id=post_id, user_id=uid,
                   content="好帖！", author=author, is_active=True)


@pytest.mark.asyncio
async def test_create_comment_success(service, mock_comment_dao, mock_post_dao, mock_session):
    """测试发表评论成功"""
    mock_post_dao.get_by_id.return_value = make_post()
    mock_comment_dao.insert.return_value = 1
    mock_comment_dao.get_by_id.return_value = make_comment()

    request = CommentCreateRequest(content="好帖！")
    result = await service.create_comment(post_id=1, user_id=2, request=request)

    assert result.id == 1
    assert result.content == "好帖！"
    assert result.author_nickname == "评论者"
    mock_comment_dao.insert.assert_awaited_once()
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_comment_post_not_found(service, mock_comment_dao, mock_post_dao, mock_session):
    """测试帖子不存在抛异常"""
    mock_post_dao.get_by_id.return_value = None
    request = CommentCreateRequest(content="内容")

    with pytest.raises(PostNotFoundError):
        await service.create_comment(post_id=999, user_id=1, request=request)
    mock_comment_dao.insert.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_comments(service, mock_comment_dao, mock_post_dao, mock_session):
    """测试获取评论列表"""
    mock_comment_dao.list_by_post.return_value = [
        make_comment(cid=3, post_id=1), make_comment(cid=2, post_id=1),
    ]

    result = await service.get_comments(post_id=1, offset=0, limit=20)

    assert len(result.items) == 2
    assert result.total == 2
    mock_comment_dao.list_by_post.assert_awaited_once_with(1, offset=0, limit=20)


@pytest.mark.asyncio
async def test_delete_comment_success(service, mock_comment_dao, mock_post_dao, mock_session):
    """测试作者删除评论"""
    mock_comment_dao.get_by_id.return_value = make_comment(cid=1, uid=2)
    mock_comment_dao.delete.return_value = True

    result = await service.delete_comment(comment_id=1, user_id=2)
    assert result is True
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_comment_not_owner(service, mock_comment_dao, mock_post_dao, mock_session):
    """测试非作者删除抛异常"""
    mock_comment_dao.get_by_id.return_value = make_comment(cid=1, uid=2)

    with pytest.raises(BusinessError):
        await service.delete_comment(comment_id=1, user_id=3)
    mock_comment_dao.delete.assert_not_awaited()
