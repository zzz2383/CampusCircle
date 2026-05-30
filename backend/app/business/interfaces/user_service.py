"""
功能：用户业务逻辑接口

实现逻辑：
    定义用户注册、登录、在线状态管理等业务操作抽象接口

调用链路：
    - 被表现层的 auth 路由调用
    - 调用数据访问层的 UserDAO
"""

from abc import ABC, abstractmethod
from typing import Optional

from app.models.dto import UserRegisterRequest, UserLoginRequest, UserDTO, TokenDTO


class IUserService(ABC):
    """用户服务接口"""

    @abstractmethod
    async def register(self, request: UserRegisterRequest) -> UserDTO:
        """校园邮箱注册

        实现逻辑：
            1. 校验学号/工号是否已注册
            2. 校验校园邮箱格式
            3. 密码哈希处理
            4. 写入 SQLite

        参数：
            request: 注册请求（student_id, email, password, nickname）

        返回值：
            UserDTO: 用户信息（不含密码）

        异常：
            DuplicateError: 学号或邮箱已注册

        测试用例：
            - test_register_success
            - test_register_duplicate_student_id
        """
        ...

    @abstractmethod
    async def login(self, request: UserLoginRequest) -> TokenDTO:
        """用户登录

        实现逻辑：
            1. 根据学号查找用户
            2. 验证密码
            3. 生成 JWT Token
            4. Redis 设置在线状态

        参数：
            request: 登录请求（student_id, password）

        返回值：
            TokenDTO: 包含 access_token, token_type, user 信息

        异常：
            AuthError: 学号或密码错误

        测试用例：
            - test_login_success
            - test_login_wrong_password
        """
        ...

    @abstractmethod
    async def get_user_by_id(self, user_id: int) -> Optional[UserDTO]:
        """获取用户信息"""
        ...
