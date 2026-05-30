"""
功能：FastAPI 依赖注入集中管理

实现逻辑：
    1. get_user_service: 创建 UserDAOImpl → 注入 UserServiceImpl → 返回 IUserService
    2. get_current_user: 从 HTTP Authorization Header 提取 JWT → 解码 → 查用户 → 返回 UserDTO

调用链路：
    - 被 presentation/api/*.py 路由通过 Depends() 调用
    - 调用 infrastructure/db.py 的 get_db 获取数据库会话
    - 调用 business/impl 的具体实现类
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.business.interfaces.user_service import IUserService
from app.business.impl.user_service_impl import UserServiceImpl
from app.business.impl.auth_utils import decode_access_token
from app.data_access.sqlite_dao.user_dao_impl import UserDAOImpl
from app.infrastructure.db import get_db
from app.models.dto import UserDTO

security = HTTPBearer()


async def get_user_service(db: AsyncSession = Depends(get_db)) -> IUserService:
    """依赖注入：获取 UserService 实例

    实现逻辑：
        1. 通过 get_db 获取数据库会话
        2. 创建 UserDAOImpl（注入 db session）
        3. 创建 UserServiceImpl（注入 user_dao + db session）

    参数：
        db: 由 FastAPI 自动注入的 AsyncSession

    返回值：
        IUserService 实例
    """
    user_dao = UserDAOImpl(db)
    return UserServiceImpl(user_dao=user_dao, db_session=db)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user_service: IUserService = Depends(get_user_service),
) -> UserDTO:
    """依赖注入：获取当前登录用户

    实现逻辑：
        1. 从 Authorization Header 提取 Bearer Token
        2. 解码 JWT 获取 payload（包含 user_id）
        3. 根据 user_id 查询用户
        4. 用户不存在或令牌无效则返回 401

    参数：
        credentials: 由 FastAPI HTTPBearer 自动提取的凭证
        user_service: 由 get_user_service 注入的 UserService

    返回值：
        UserDTO: 当前登录用户信息

    异常：
        HTTPException 401: 令牌无效或用户不存在
    """
    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的访问令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id_str: str = payload.get("sub")
    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌 payload 无效",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await user_service.get_user_by_id(int(user_id_str))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user
