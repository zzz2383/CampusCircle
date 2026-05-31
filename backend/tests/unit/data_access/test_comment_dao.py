"""
功能：CommentDAO 单元测试

测试用例：
    - test_insert_comment: 创建评论
    - test_get_by_id_found: 按 ID 查询（含作者昵称）
    - test_get_by_id_not_found: 不存在的评论
    - test_list_by_post: 获取帖子的评论列表
    - test_list_by_post_empty: 无评论时返回空列表
    - test_delete_soft: 软删除评论
    - test_list_replies: 获取楼中楼回复
"""

import pytest
import pytest_asyncio
from sqlalchemy import select

from app.data_access.sqlite_dao.comment_dao_impl import CommentDAOImpl
from app.models.domain import Comment, Post, User
from app.models.enums import UserRole


@pytest_asyncio.fixture
async def sample_user(db_session) -> User:
    user = User(student_id="C001", email="c@c.edu", nickname="评论者",
                password_hash="h", role=UserRole.STUDENT)
    db_session.add(user)
    await db_session.flush()
    return user


@pytest_asyncio.fixture
async def sample_post(db_session, sample_user) -> Post:
    post = Post(user_id=sample_user.id, title="测试帖", content="内容")
    db_session.add(post)
    await db_session.flush()
    return post


@pytest.mark.asyncio
async def test_insert_comment(db_session, sample_post, sample_user):
    """测试创建评论"""
    dao = CommentDAOImpl(db_session)
    comment = Comment(post_id=sample_post.id, user_id=sample_user.id, content="好帖！")
    cid = await dao.insert(comment)

    assert cid > 0
    result = await db_session.execute(select(Comment).where(Comment.id == cid))
    saved = result.scalar_one()
    assert saved.content == "好帖！"


@pytest.mark.asyncio
async def test_get_by_id_found(db_session, sample_post, sample_user):
    """测试按 ID 查询（含作者昵称）"""
    dao = CommentDAOImpl(db_session)
    comment = Comment(post_id=sample_post.id, user_id=sample_user.id, content="赞")
    cid = await dao.insert(comment)

    found = await dao.get_by_id(cid)
    assert found is not None
    assert found.content == "赞"
    assert found.author.nickname == "评论者"


@pytest.mark.asyncio
async def test_get_by_id_not_found(db_session):
    """测试不存在的评论"""
    dao = CommentDAOImpl(db_session)
    assert await dao.get_by_id(99999) is None


@pytest.mark.asyncio
async def test_list_by_post(db_session, sample_post, sample_user):
    """测试获取帖子的评论列表"""
    dao = CommentDAOImpl(db_session)
    for i in range(3):
        c = Comment(post_id=sample_post.id, user_id=sample_user.id, content=f"评论{i}")
        await dao.insert(c)

    comments = await dao.list_by_post(sample_post.id, offset=0, limit=10)
    assert len(comments) == 3
    assert comments[0].author.nickname == "评论者"


@pytest.mark.asyncio
async def test_list_by_post_empty(db_session, sample_post):
    """测试无评论"""
    dao = CommentDAOImpl(db_session)
    comments = await dao.list_by_post(sample_post.id, offset=0, limit=10)
    assert len(comments) == 0


@pytest.mark.asyncio
async def test_delete_soft(db_session, sample_post, sample_user):
    """测试软删除评论"""
    dao = CommentDAOImpl(db_session)
    c = Comment(post_id=sample_post.id, user_id=sample_user.id, content="待删除")
    cid = await dao.insert(c)

    result = await dao.delete(cid)
    assert result is True

    # 软删除后不应被查询到
    assert await dao.get_by_id(cid) is None


@pytest.mark.asyncio
async def test_list_replies(db_session, sample_post, sample_user):
    """测试获取楼中楼回复"""
    dao = CommentDAOImpl(db_session)
    parent = Comment(post_id=sample_post.id, user_id=sample_user.id, content="父评论")
    pid = await dao.insert(parent)

    for i in range(2):
        r = Comment(post_id=sample_post.id, user_id=sample_user.id,
                     content=f"回复{i}", parent_id=pid)
        await dao.insert(r)

    # 父评论在普通列表中
    all_c = await dao.list_by_post(sample_post.id, offset=0, limit=10)
    assert len(all_c) == 3

    # 子评论可以通过 parent_id 筛选
    replies = await dao.list_by_post(sample_post.id, offset=0, limit=10, parent_id=pid)
    assert len(replies) == 2
