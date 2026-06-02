"""
功能：用户业务逻辑实现

实现逻辑：
    1. register: 查重 → 密码哈希 → 写入 DB → 提交事务 → 返回 UserDTO
    2. login: 查用户 → 验密码 → 生成 JWT → 更新在线状态 → 返回 TokenDTO
    3. get_user_by_id: 查询 → 返回 UserDTO 或 None

调用链路：
    - 被表现层 auth 路由通过 IUserService 接口调用
    - 调用数据访问层 IUserDAO 接口
    - 使用 auth_utils 的密码哈希和 JWT 工具

参数说明：
    user_dao: IUserDAO 实例（通过 DI 注入）
    db_session: AsyncSession 实例（通过 DI 注入）

异常说明：
    DuplicateError: 学号或邮箱已注册
    AuthError: 登录凭证无效

测试用例：
    - tests/unit/business/test_user_service.py
"""

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.business.interfaces.user_service import IUserService
from app.business.impl.auth_utils import hash_password, verify_password, create_access_token
from app.data_access.sqlite_dao.user_dao import IUserDAO
from app.infrastructure.exceptions import DuplicateError, AuthError
from app.infrastructure.logger import get_logger
from app.models.domain import User
from app.models.dto import (
    UserRegisterRequest,
    UserLoginRequest,
    UserDTO,
    TokenDTO,
    UserProfileUpdateRequest,
)

logger = get_logger(__name__)


class UserServiceImpl(IUserService):
    """用户服务实现"""

    def __init__(self, user_dao: IUserDAO, db_session: AsyncSession):
        self.user_dao = user_dao
        self.db_session = db_session

    async def register(self, request: UserRegisterRequest) -> UserDTO:
        """
        校园邮箱注册

        实现逻辑：
            1. 根据学号查重，若已存在则抛出 DuplicateError
            2. 使用 bcrypt 对密码进行哈希
            3. 创建 User ORM 对象并写入数据库
            4. 提交事务，返回 UserDTO

        参数：
            request: 注册请求（student_id, email, password, nickname）

        返回值：
            UserDTO: 用户信息（不含密码）

        异常：
            DuplicateError: 学号已注册

        测试用例：
            - test_register_success
            - test_register_duplicate_student_id
        """
        # 1. 查重
        existing = await self.user_dao.get_by_student_id(request.student_id)
        if existing:
            raise DuplicateError(
                code="STUDENT_ID_EXISTS",
                message=f"学号 {request.student_id} 已注册",
            )

        # 2. 密码哈希
        password_hash = hash_password(request.password)

        # 3. 创建用户
        user = User(
            student_id=request.student_id,
            email=request.email,
            nickname=request.nickname,
            password_hash=password_hash,
            department=request.department,
            grade=request.grade,
            gender=request.gender,
        )

        # 4. 写入数据库
        user_id = await self.user_dao.insert(user)
        await self.db_session.commit()

        logger.info(f"User registered: id={user_id}, student_id={request.student_id}")

        # 5. 返回 DTO（重新查询以获取完整数据）
        created_user = await self.user_dao.get_by_id(user_id)
        return UserDTO.model_validate(created_user)

    async def login(self, request: UserLoginRequest) -> TokenDTO:
        """
        用户登录

        实现逻辑：
            1. 根据学号查找用户
            2. 若用户不存在，抛出 AuthError
            3. 校验密码，若不匹配，抛出 AuthError
            4. 生成 JWT Token（payload 包含用户 ID）
            5. 更新用户在线状态为 True
            6. 返回 TokenDTO（含 access_token 和用户信息）

        参数：
            request: 登录请求（student_id, password）

        返回值：
            TokenDTO: 包含 access_token, token_type, user 信息

        异常：
            AuthError: 学号不存在或密码错误

        测试用例：
            - test_login_success
            - test_login_wrong_password
            - test_login_user_not_found
        """
        # 1. 查找用户
        user = await self.user_dao.get_by_student_id(request.student_id)
        if user is None:
            raise AuthError(
                code="INVALID_CREDENTIALS",
                message="学号或密码错误",
            )

        # 2. 校验密码
        if not verify_password(request.password, user.password_hash):
            raise AuthError(
                code="INVALID_CREDENTIALS",
                message="学号或密码错误",
            )

        # 3. 生成 JWT
        access_token = create_access_token({"sub": str(user.id)})

        # 4. 更新在线状态
        await self.user_dao.update_online_status(user.id, True)
        await self.db_session.commit()

        logger.info(f"User logged in: id={user.id}")

        # 5. 返回 TokenDTO
        return TokenDTO(
            access_token=access_token,
            token_type="bearer",
            user=UserDTO.model_validate(user),
        )

    async def get_user_by_id(self, user_id: int) -> Optional[UserDTO]:
        """
        根据 ID 获取用户信息

        参数：
            user_id: 用户 ID

        返回值：
            UserDTO 或 None（用户不存在）
        """
        user = await self.user_dao.get_by_id(user_id)
        if user is None:
            return None
        return UserDTO.model_validate(user)

    async def update_profile(self, user_id: int, request: UserProfileUpdateRequest) -> UserDTO:
        """
        更新个人资料

        实现逻辑：
            1. 检查用户是否存在
            2. 调用 DAO.update_profile 更新非空字段
            3. 提交事务
            4. 返回更新后的 UserDTO

        参数：
            user_id: 用户 ID
            request: 个人资料更新请求

        返回值：
            UserDTO: 更新后的用户信息

        异常：
            - 用户不存在时由 get_by_id 返回 None，由表现层处理
        """
        # 1. 检查用户是否存在
        existing = await self.user_dao.get_by_id(user_id)
        if existing is None:
            return None

        # 2. 更新资料（只更新非 None 字段）
        update_data = request.model_dump(exclude_none=True)
        if not update_data:
            return UserDTO.model_validate(existing)

        await self.user_dao.update_profile(user_id, **update_data)
        await self.db_session.commit()

        logger.info(f"User profile updated: id={user_id}, fields={list(update_data.keys())}")

        # 3. 返回更新后的用户信息
        updated = await self.user_dao.get_by_id(user_id)
        return UserDTO.model_validate(updated)
