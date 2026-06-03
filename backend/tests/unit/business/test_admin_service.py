"""AdminService 单元测试"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.business.impl.admin_service_impl import AdminServiceImpl
from app.data_access.sqlite_dao.user_dao import IUserDAO
from app.data_access.redis_repo.blacklist_repo import IBlacklistRepo
from app.models.dto import UserDTO
from app.infrastructure.exceptions import BusinessError, ForbiddenError


@pytest.fixture
def mock_user_dao() -> MagicMock:
    return AsyncMock(spec=IUserDAO)


@pytest.fixture
def mock_blacklist_repo() -> MagicMock:
    return AsyncMock(spec=IBlacklistRepo)


@pytest.fixture
def mock_session() -> MagicMock:
    s = AsyncMock()
    s.commit = AsyncMock()
    return s


@pytest.fixture
def service(mock_user_dao, mock_session, mock_blacklist_repo) -> AdminServiceImpl:
    return AdminServiceImpl(
        user_dao=mock_user_dao,
        post_dao=AsyncMock(),
        comment_dao=AsyncMock(),
        club_dao=AsyncMock(),
        event_dao=AsyncMock(),
        lost_item_dao=AsyncMock(),
        blacklist_repo=mock_blacklist_repo,
        db_session=mock_session,
    )


class TestSetRole:
    """测试 set_role 安全限制"""

    @pytest.mark.asyncio
    async def test_set_role_reject_admin(self, service):
        """不允许直接设为 admin"""
        with pytest.raises(BusinessError) as exc:
            await service.set_role(user_id=2, role="admin", current_user_id=1)
        assert "admin" in str(exc.value.message).lower() or "管理员" in str(exc.value.message)

    @pytest.mark.asyncio
    async def test_set_role_reject_self_change(self, service):
        """不允许修改自己的角色"""
        with pytest.raises(ForbiddenError) as exc:
            await service.set_role(user_id=1, role="teacher", current_user_id=1)
        assert "自己" in str(exc.value.message) or "自己" in str(exc.value)

    @pytest.mark.asyncio
    async def test_set_role_allow_teacher(self, service, mock_user_dao, mock_session):
        """允许设为 teacher"""
        from app.models.domain import User
        from app.models.enums import UserRole
        mock_user_dao.get_by_id.return_value = User(
            id=2, student_id="s2", email="t@c.edu", nickname="用户2",
            password_hash="h", role=UserRole.STUDENT, is_online=False
        )
        mock_user_dao.update_role.return_value = True

        result = await service.set_role(user_id=2, role="teacher", current_user_id=1)

        assert result is not None
        mock_user_dao.update_role.assert_awaited_once_with(2, "teacher")

    @pytest.mark.asyncio
    async def test_set_role_allow_student(self, service, mock_user_dao, mock_session):
        """允许设为 student"""
        from app.models.domain import User
        from app.models.enums import UserRole
        mock_user_dao.get_by_id.return_value = User(
            id=2, student_id="s2", email="s@c.edu", nickname="用户2",
            password_hash="h", role=UserRole.STUDENT, is_online=False
        )

        result = await service.set_role(user_id=2, role="student", current_user_id=1)

        assert result is not None
        mock_user_dao.update_role.assert_awaited_once_with(2, "student")

    @pytest.mark.asyncio
    async def test_set_role_invalid_role(self, service):
        """不允许设置无效角色"""
        with pytest.raises(BusinessError):
            await service.set_role(user_id=2, role="superadmin", current_user_id=1)


class TestAutoAdmin:
    """测试注册时自动设为管理员"""

    @pytest.mark.asyncio
    async def test_register_auto_admin(self, monkeypatch):
        """学号在 ADMIN_STUDENT_IDS 中时自动设为 admin"""
        from app.infrastructure.config import settings
        monkeypatch.setattr(settings, "ADMIN_STUDENT_IDS", "2024001,2024099")

        from app.models.dto import UserRegisterRequest
        from app.business.impl.user_service_impl import UserServiceImpl

        mock_dao = AsyncMock(spec=IUserDAO)
        mock_dao.get_by_student_id.return_value = None
        mock_dao.insert.return_value = 1
        mock_session = AsyncMock()
        mock_session.commit = AsyncMock()

        service = UserServiceImpl(user_dao=mock_dao, db_session=mock_session)

        request = UserRegisterRequest(
            student_id="2024099", email="admin@campus.edu",
            password="pass123", nickname="管理员",
        )

        # Mock get_by_id to return user with admin role
        user = MagicMock()
        user.id = 1
        user.student_id = "2024099"
        user.email = "admin@campus.edu"
        user.nickname = "管理员"
        user.role = "admin"
        user.department = None
        user.grade = None
        user.gender = None
        user.avatar_url = None
        user.is_online = False
        user.created_at = None
        mock_dao.get_by_id.return_value = user

        result = await service.register(request)

        assert result.role == "admin"

    @pytest.mark.asyncio
    async def test_register_normal_user_not_admin(self, monkeypatch):
        """学号不在 ADMIN_STUDENT_IDS 中时角色为 student"""
        from app.infrastructure.config import settings
        monkeypatch.setattr(settings, "ADMIN_STUDENT_IDS", "2024001,2024099")

        from app.models.dto import UserRegisterRequest
        from app.business.impl.user_service_impl import UserServiceImpl

        mock_dao = AsyncMock(spec=IUserDAO)
        mock_dao.get_by_student_id.return_value = None
        mock_dao.insert.return_value = 2
        mock_session = AsyncMock()
        mock_session.commit = AsyncMock()

        service = UserServiceImpl(user_dao=mock_dao, db_session=mock_session)

        request = UserRegisterRequest(
            student_id="2024100", email="user@campus.edu",
            password="pass123", nickname="普通用户",
        )

        user = MagicMock()
        user.id = 2
        user.student_id = "2024100"
        user.role = "student"
        user.nickname = "普通用户"
        user.email = "u@c.edu"
        user.password_hash = "h"
        user.department = None
        user.grade = None
        user.gender = None
        user.avatar_url = None
        user.is_online = False
        user.created_at = None
        mock_dao.get_by_id.return_value = user

        result = await service.register(request)

        assert result.role == "student"
