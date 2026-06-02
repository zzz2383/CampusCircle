"""
功能：PostDAO 单元测试

测试策略：
    - 使用内存 SQLite（db_session fixture）
    - 每个测试独立数据库，测试结束自动清理
    - 创建用户作为帖子作者的前置条件

测试用例：
    - test_insert_post: 创建帖子返回 ID
    - test_get_by_id_found: 根据 ID 查询帖子（含作者昵称）
    - test_get_by_id_not_found: 查询不存在的帖子
    - test_delete_soft: 软删除帖子
    - test_list_latest: 分页列表
    - test_list_latest_with_tag: 按标签筛选
    - test_search: 关键词搜索
"""

import pytest
import pytest_asyncio
from sqlalchemy import select

from app.data_access.sqlite_dao.post_dao_impl import PostDAOImpl
from app.models.domain import Post, User
from app.models.enums import UserRole


@pytest_asyncio.fixture
async def sample_user(db_session) -> User:
    """创建测试用户（flush 以确保 ID 可用）"""
    user = User(
        student_id="2024001",
        email="author@campus.edu",
        nickname="作者小明",
        password_hash="hashed",
        role=UserRole.STUDENT,
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest.mark.asyncio
async def test_insert_post(db_session, sample_user):
    """测试创建帖子，应返回自增 ID"""
    dao = PostDAOImpl(db_session)
    post = Post(
        user_id=sample_user.id,
        title="测试标题",
        content="测试正文内容",
        tags="课程,求助",
    )
    post_id = await dao.insert(post)

    assert post_id > 0
    # 验证数据库中存在
    result = await db_session.execute(select(Post).where(Post.id == post_id))
    saved = result.scalar_one()
    assert saved.title == "测试标题"
    assert saved.tags == "课程,求助"


@pytest.mark.asyncio
async def test_get_by_id_found(db_session, sample_user):
    """测试根据 ID 查询帖子（含作者信息）"""
    dao = PostDAOImpl(db_session)
    post = Post(
        user_id=sample_user.id,
        title="查询测试",
        content="查询正文",
    )
    post_id = await dao.insert(post)

    found = await dao.get_by_id(post_id)
    assert found is not None
    assert found.title == "查询测试"
    assert found.author.nickname == "作者小明"


@pytest.mark.asyncio
async def test_get_by_id_not_found(db_session):
    """测试查询不存在的帖子返回 None"""
    dao = PostDAOImpl(db_session)
    result = await dao.get_by_id(99999)
    assert result is None


@pytest.mark.asyncio
async def test_delete_soft(db_session, sample_user):
    """测试软删除帖子"""
    dao = PostDAOImpl(db_session)
    post = Post(user_id=sample_user.id, title="待删除", content="将被软删除")
    post_id = await dao.insert(post)

    result = await dao.delete(post_id)
    assert result is True

    # 软删除后 get_by_id 应返回 None（过滤了 is_active=False）
    found = await dao.get_by_id(post_id)
    assert found is None

    # 直接查数据库验证 is_active 确实为 False
    result = await db_session.execute(select(Post).where(Post.id == post_id))
    db_post = result.scalar_one()
    assert db_post.is_active is False


@pytest.mark.asyncio
async def test_list_latest(db_session, sample_user):
    """测试获取最新帖子列表"""
    dao = PostDAOImpl(db_session)

    # 创建 3 个帖子
    for i in range(3):
        post = Post(
            user_id=sample_user.id,
            title=f"帖子 {i}",
            content=f"正文 {i}",
        )
        await dao.insert(post)

    posts = await dao.list_latest(offset=0, limit=2)
    assert len(posts) == 2
    # 验证总数和标题正确（顺序与插入顺序一致，因时间戳精度相同）
    titles = [p.title for p in posts]
    assert "帖子 0" in titles
    assert "帖子 1" in titles
    assert len(titles) == 2

    posts_all = await dao.list_latest(offset=0, limit=10)
    assert len(posts_all) == 3


@pytest.mark.asyncio
async def test_list_latest_with_tag(db_session, sample_user):
    """测试按标签筛选帖子"""
    dao = PostDAOImpl(db_session)

    posts_data = [
        Post(user_id=sample_user.id, title="课程帖", content="c1", tags="课程"),
        Post(user_id=sample_user.id, title="社团帖", content="c2", tags="社团"),
        Post(user_id=sample_user.id, title="综合帖", content="c3", tags="综合"),
        Post(user_id=sample_user.id, title="课程帖2", content="c4", tags="课程"),
    ]
    for p in posts_data:
        await dao.insert(p)

    # 筛选课程标签
    course_posts = await dao.list_latest(offset=0, limit=10, tag="课程")
    assert len(course_posts) == 2
    for p in course_posts:
        assert "课程" in p.tags

    # 筛选社团标签
    club_posts = await dao.list_latest(offset=0, limit=10, tag="社团")
    assert len(club_posts) == 1
    assert club_posts[0].title == "社团帖"


@pytest.mark.asyncio
async def test_search(db_session, sample_user):
    """测试关键词搜索"""
    dao = PostDAOImpl(db_session)

    posts_data = [
        Post(user_id=sample_user.id, title="Python 教程", content="学习 Python 编程"),
        Post(user_id=sample_user.id, title="Java 入门", content="Java 基础教程"),
        Post(user_id=sample_user.id, title="数据结构", content="Python 实现"),
    ]
    for p in posts_data:
        await dao.insert(p)

    # 搜索 Python
    results = await dao.search("Python", offset=0, limit=10)
    assert len(results) == 2  # 标题和正文都匹配

    # 搜索 入门
    results = await dao.search("入门", offset=0, limit=10)
    assert len(results) == 1
    assert results[0].title == "Java 入门"

    # 搜索不存在的
    results = await dao.search("不存在", offset=0, limit=10)
    assert len(results) == 0


@pytest.mark.asyncio
async def test_increment_view_count(db_session, sample_user):
    """测试增加浏览量"""
    dao = PostDAOImpl(db_session)
    post = Post(user_id=sample_user.id, title="浏览量测试", content="测试")
    post_id = await dao.insert(post)

    # 初始为 0
    found = await dao.get_by_id(post_id)
    assert found.view_count == 0

    # 增加 1 次
    new_count = await dao.increment_view_count(post_id)
    assert new_count == 1

    # 再增加 2 次
    await dao.increment_view_count(post_id)
    new_count = await dao.increment_view_count(post_id)
    assert new_count == 3


@pytest.mark.asyncio
async def test_count_comments(db_session, sample_user):
    """测试获取评论数"""
    from app.models.domain import Comment

    dao = PostDAOImpl(db_session)
    post = Post(user_id=sample_user.id, title="评论计数测试", content="测试")
    post_id = await dao.insert(post)

    # 初始为 0
    count = await dao.count_comments(post_id)
    assert count == 0

    # 添加 2 条评论
    for i in range(2):
        c = Comment(post_id=post_id, user_id=sample_user.id, content=f"评论{i}")
        db_session.add(c)
    await db_session.flush()

    count = await dao.count_comments(post_id)
    assert count == 2
