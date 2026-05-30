"""
功能：用户认证路由（注册 / 登录 / 获取当前用户）

实现逻辑：
    1. POST /api/auth/register — 注册新用户，返回 UserDTO
    2. POST /api/auth/login — 用户登录，返回 JWT Token + UserDTO
    3. GET /api/auth/me — 获取当前登录用户信息（需 Bearer Token）

调用链路：
    - 调用 IUserService 接口（通过依赖注入）
    - get_current_user 依赖从 JWT 解析用户身份

注意事项：
    - 直接返回 Pydantic 模型（FastAPI 自动处理 datetime 序列化）
    - 不要用 JSONResponse(content=model_dump())，会导致 datetime 序列化错误
"""

from fastapi import APIRouter, Depends, status

from app.business.interfaces import IUserService
from app.models.dto import UserRegisterRequest, UserLoginRequest, UserDTO, TokenDTO
from app.presentation.dependencies import get_user_service, get_current_user

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/register", response_model=UserDTO, status_code=status.HTTP_201_CREATED)
async def register(
    request: UserRegisterRequest,
    user_service: IUserService = Depends(get_user_service),
):
    """
    用户注册

    - 使用学号/工号和校园邮箱注册
    - 密码经过 bcrypt 哈希存储
    - 返回用户信息（不含密码）
    """
    return await user_service.register(request)


@router.post("/login", response_model=TokenDTO)
async def login(
    request: UserLoginRequest,
    user_service: IUserService = Depends(get_user_service),
):
    """
    用户登录

    - 使用学号 + 密码登录
    - 验证通过后返回 JWT Token
    - Token 默认 24 小时有效
    """
    return await user_service.login(request)


@router.get("/me", response_model=UserDTO)
async def get_current_user_info(
    current_user: UserDTO = Depends(get_current_user),
):
    """
    获取当前登录用户信息

    - 需要在请求头中携带 Authorization: Bearer <token>
    - 返回当前用户的详细信息
    """
    return current_user
