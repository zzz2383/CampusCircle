"""
功能：UserService 单元测试

测试策略：
    - Mock 掉 IUserDAO 的依赖，不涉及真实数据库
    - 使用 passlib 真实哈希（但只验证逻辑，不测试哈希性能）
    - 覆盖正常路径 + 异常路径

测试用例：
    - test_register_success: 注册成功返回 UserDTO
    - test_register_duplicate_student_id: 学号重复抛 DuplicateError
    - test_login_success: 登录成功返回 TokenDTO
    - test_login_wrong_password: 密码错误抛 AuthError
    - test_login_user_not_found: 学号不存在抛 AuthError
    - test_get_user_by_id_found: 查询存在的用户
    - test_get_user_by_id_not_found: 查询不存在的用户返回 None
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from app.business.impl.user_service_impl import UserServiceImpl
from app.business.impl.auth_utils import hash_password
from app.data_access.sqlite_dao.user_dao import IUserDAO
from app.models.domain import User
from app.models.dto import UserRegisterRequest, UserLoginRequest, UserProfileUpdateRequest
from app.models.enums import UserRole
from app.infrastructure.exceptions import DuplicateError, AuthError


@pytest.fixture
def mock_dao() -> MagicMock:
    """创建 mock UserDAO"""
    return AsyncMock(spec=IUserDAO)


@pytest.fixture
def mock_session() -> MagicMock:
    """创建 mock AsyncSession"""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def service(mock_dao, mock_session) -> UserServiceImpl:
    """创建 UserServiceImpl 实例"""
    return UserServiceImpl(user_dao=mock_dao, db_session=mock_session)


def create_sample_user(user_id: int = 1) -> User:
    """辅助函数：创建测试用户对象"""
    return User(
        id=user_id,
        student_id="2024001",
        email="test@campus.edu",
        nickname="测试用户",
        password_hash=hash_password("password123"),
        role=UserRole.STUDENT,
        is_online=False,
    )


# ========== 注册测试 ==========


@pytest.mark.asyncio
async def test_register_success(service, mock_dao, mock_session):
    """测试注册成功"""
    # Arrange
    mock_dao.get_by_student_id.return_value = None
    mock_dao.insert.return_value = 1
    # get_by_id 在 register 内部被二次调用以获取完整数据
    mock_dao.get_by_id.return_value = User(
        id=1,
        student_id="2024001",
        email="test@campus.edu",
        nickname="测试用户",
        password_hash=hash_password("password123"),
        role=UserRole.STUDENT,
        is_online=False,
    )
    request = UserRegisterRequest(
        student_id="2024001",
        email="test@campus.edu",
        password="password123",
        nickname="测试用户",
    )

    # Act
    result = await service.register(request)

    # Assert
    assert result.id == 1
    assert result.student_id == "2024001"
    assert result.nickname == "测试用户"
    assert result.email == "test@campus.edu"
    # 密码不应返回
    assert not hasattr(result, "password_hash")
    # 验证查重调用
    mock_dao.get_by_student_id.assert_awaited_once_with("2024001")
    # 验证 insert 调用
    mock_dao.insert.assert_awaited_once()
    # 验证事务提交
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_register_duplicate_student_id(service, mock_dao, mock_session):
    """测试学号重复时抛出 DuplicateError"""
    # Arrange
    mock_dao.get_by_student_id.return_value = create_sample_user()
    request = UserRegisterRequest(
        student_id="2024001",
        email="another@campus.edu",
        password="password123",
        nickname="另一个用户",
    )

    # Act & Assert
    with pytest.raises(DuplicateError) as exc:
        await service.register(request)
    assert "学号" in str(exc.value.message) or "已注册" in str(exc.value.message)

    # 验证 insert 未被调用
    mock_dao.insert.assert_not_awaited()
    mock_session.commit.assert_not_awaited()


# ========== 登录测试 ==========


@pytest.mark.asyncio
async def test_login_success(service, mock_dao, mock_session):
    """测试登录成功"""
    # Arrange
    user = create_sample_user()
    mock_dao.get_by_student_id.return_value = user
    request = UserLoginRequest(
        student_id="2024001",
        password="password123",
    )

    # Act
    result = await service.login(request)

    # Assert
    assert result.access_token is not None
    assert result.token_type == "bearer"
    assert result.user.id == 1
    assert result.user.nickname == "测试用户"
    # 验证在线状态更新
    mock_dao.update_online_status.assert_awaited_once_with(1, True)


@pytest.mark.asyncio
async def test_login_wrong_password(service, mock_dao, mock_session):
    """测试密码错误时抛出 AuthError"""
    # Arrange
    user = create_sample_user()
    mock_dao.get_by_student_id.return_value = user
    request = UserLoginRequest(
        student_id="2024001",
        password="wrong_password",
    )

    # Act & Assert
    with pytest.raises(AuthError) as exc:
        await service.login(request)
    assert "密码" in str(exc.value.message) or "错误" in str(exc.value.message)


@pytest.mark.asyncio
async def test_login_user_not_found(service, mock_dao, mock_session):
    """测试学号不存在时抛出 AuthError"""
    # Arrange
    mock_dao.get_by_student_id.return_value = None
    request = UserLoginRequest(
        student_id="NONEXIST",
        password="password123",
    )

    # Act & Assert
    with pytest.raises(AuthError) as exc:
        await service.login(request)
    assert "学号" in str(exc.value.message) or "错误" in str(exc.value.message)


# ========== 获取用户测试 ==========


@pytest.mark.asyncio
async def test_get_user_by_id_found(service, mock_dao, mock_session):
    """测试查询存在的用户"""
    # Arrange
    user = create_sample_user()
    mock_dao.get_by_id.return_value = user

    # Act
    result = await service.get_user_by_id(1)

    # Assert
    assert result is not None
    assert result.id == 1
    assert result.nickname == "测试用户"
    mock_dao.get_by_id.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_get_user_by_id_not_found(service, mock_dao, mock_session):
    """测试查询不存在的用户返回 None"""
    # Arrange
    mock_dao.get_by_id.return_value = None

    # Act
    result = await service.get_user_by_id(999)

    # Assert
    assert result is None


# ========== 更新个人资料测试 ==========


@pytest.mark.asyncio
async def test_update_profile_success(service, mock_dao, mock_session):
    """测试更新个人资料成功"""
    user = create_sample_user()
    mock_dao.get_by_id.return_value = user
    request = UserProfileUpdateRequest(
        nickname="新昵称",
        department="计算机学院",
    )

    result = await service.update_profile(user_id=1, request=request)

    assert result is not None
    mock_dao.update_profile.assert_awaited_once_with(1, nickname="新昵称", department="计算机学院")
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_profile_all_fields(service, mock_dao, mock_session):
    """测试更新所有可选字段"""
    from app.models.enums import Gender
    user = create_sample_user()
    mock_dao.get_by_id.return_value = user
    request = UserProfileUpdateRequest(
        nickname="新昵称",
        department="计算机学院",
        grade="2024级",
        gender=Gender.MALE,
        avatar_url="http://example.com/avatar.jpg",
    )

    result = await service.update_profile(user_id=1, request=request)

    assert result is not None
    mock_dao.update_profile.assert_awaited_once_with(
        1, nickname="新昵称", department="计算机学院",
        grade="2024级", gender=Gender.MALE,
        avatar_url="http://example.com/avatar.jpg",
    )


@pytest.mark.asyncio
async def test_update_profile_empty_request(service, mock_dao, mock_session):
    """测试空请求（所有字段为 None），不应调用 update_profile"""
    user = create_sample_user()
    mock_dao.get_by_id.return_value = user
    request = UserProfileUpdateRequest()

    result = await service.update_profile(user_id=1, request=request)

    assert result is not None
    mock_dao.update_profile.assert_not_awaited()
    mock_session.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_update_profile_user_not_found(service, mock_dao, mock_session):
    """测试更新不存在的用户"""
    mock_dao.get_by_id.return_value = None
    request = UserProfileUpdateRequest(nickname="新昵称")

    result = await service.update_profile(user_id=999, request=request)

    assert result is None
    mock_dao.update_profile.assert_not_awaited()
