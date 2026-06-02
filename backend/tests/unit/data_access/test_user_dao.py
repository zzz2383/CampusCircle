"""
功能：UserDAO 单元测试

测试策略：
    - 使用内存 SQLite（db_session fixture）确保测试隔离
    - 每个测试函数独立数据库，测试结束自动清理
    - 覆盖正常路径 + 边界路径

测试用例：
    - test_insert_user: 创建用户，验证返回 ID
    - test_get_by_id_found: 根据 ID 查询存在的用户
    - test_get_by_id_not_found: 查询不存在的用户返回 None
    - test_get_by_student_id_found: 根据学号查询
    - test_get_by_student_id_not_found: 查询不存在的学号返回 None
    - test_update_online_status: 更新在线状态
"""

import pytest
from sqlalchemy import select

from app.data_access.sqlite_dao.user_dao_impl import UserDAOImpl
from app.models.domain import User
from app.models.enums import UserRole, Gender


@pytest.mark.asyncio
async def test_insert_user(db_session):
    """测试创建用户，应返回自增 ID"""
    dao = UserDAOImpl(db_session)
    user = User(
        student_id="2024001",
        email="test@campus.edu",
        nickname="测试用户",
        password_hash="hashed_password",
        role=UserRole.STUDENT,
    )
    user_id = await dao.insert(user)

    assert user_id > 0
    # 验证数据库中确实存在
    result = await db_session.execute(select(User).where(User.id == user_id))
    saved = result.scalar_one()
    assert saved.student_id == "2024001"
    assert saved.nickname == "测试用户"


@pytest.mark.asyncio
async def test_get_by_id_found(db_session):
    """测试根据 ID 查询存在的用户"""
    dao = UserDAOImpl(db_session)
    user = User(
        student_id="2024002",
        email="test2@campus.edu",
        nickname="用户2",
        password_hash="hash2",
        role=UserRole.STUDENT,
    )
    user_id = await dao.insert(user)

    found = await dao.get_by_id(user_id)
    assert found is not None
    assert found.student_id == "2024002"
    assert found.nickname == "用户2"


@pytest.mark.asyncio
async def test_get_by_id_not_found(db_session):
    """测试查询不存在的用户，应返回 None"""
    dao = UserDAOImpl(db_session)
    result = await dao.get_by_id(99999)
    assert result is None


@pytest.mark.asyncio
async def test_get_by_student_id_found(db_session):
    """测试根据学号查询用户"""
    dao = UserDAOImpl(db_session)
    user = User(
        student_id="S2024003",
        email="test3@campus.edu",
        nickname="用户3",
        password_hash="hash3",
        role=UserRole.TEACHER,
    )
    await dao.insert(user)

    found = await dao.get_by_student_id("S2024003")
    assert found is not None
    assert found.email == "test3@campus.edu"
    assert found.role == UserRole.TEACHER


@pytest.mark.asyncio
async def test_get_by_student_id_not_found(db_session):
    """测试查询不存在的学号，应返回 None"""
    dao = UserDAOImpl(db_session)
    result = await dao.get_by_student_id("NONEXIST")
    assert result is None


@pytest.mark.asyncio
async def test_update_online_status(db_session):
    """测试更新在线状态"""
    dao = UserDAOImpl(db_session)
    user = User(
        student_id="2024004",
        email="test4@campus.edu",
        nickname="用户4",
        password_hash="hash4",
    )
    user_id = await dao.insert(user)

    # 更新为在线
    await dao.update_online_status(user_id, True)
    found = await dao.get_by_id(user_id)
    assert found is not None
    assert found.is_online is True

    # 更新为离线
    await dao.update_online_status(user_id, False)
    found = await dao.get_by_id(user_id)
    assert found is not None
    assert found.is_online is False


@pytest.mark.asyncio
async def test_update_profile(db_session):
    """测试更新个人资料"""
    dao = UserDAOImpl(db_session)
    user = User(
        student_id="2024005",
        email="test5@campus.edu",
        nickname="旧昵称",
        password_hash="hash5",
    )
    user_id = await dao.insert(user)

    # 更新昵称和院系
    await dao.update_profile(user_id, nickname="新昵称", department="计算机学院")

    found = await dao.get_by_id(user_id)
    assert found.nickname == "新昵称"
    assert found.department == "计算机学院"


@pytest.mark.asyncio
async def test_update_profile_partial(db_session):
    """测试只更新部分字段，其他字段不受影响"""
    dao = UserDAOImpl(db_session)
    user = User(
        student_id="2024006",
        email="test6@campus.edu",
        nickname="用户6",
        password_hash="hash6",
        department="原院系",
        grade="2024级",
    )
    user_id = await dao.insert(user)

    # 只更新年级
    await dao.update_profile(user_id, grade="2025级")

    found = await dao.get_by_id(user_id)
    assert found.grade == "2025级"
    assert found.nickname == "用户6"  # 不应变化
    assert found.department == "原院系"  # 不应变化


@pytest.mark.asyncio
async def test_update_profile_with_gender(db_session):
    """测试更新性别字段"""
    dao = UserDAOImpl(db_session)
    user = User(
        student_id="2024007",
        email="test7@campus.edu",
        nickname="用户7",
        password_hash="hash7",
    )
    user_id = await dao.insert(user)

    await dao.update_profile(user_id, gender=Gender.MALE)

    found = await dao.get_by_id(user_id)
    assert found.gender == Gender.MALE
