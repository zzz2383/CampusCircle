"""
功能：用户认证路由（注册 / 登录）

实现逻辑：
    1. POST /api/auth/register — 注册新用户
    2. POST /api/auth/login — 用户登录，返回 JWT Token
    3. GET /api/auth/me — 获取当前登录用户信息

调用链路：
    - 调用 IUserService 接口
"""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.business.interfaces import IUserService
from app.models.dto import UserRegisterRequest, UserLoginRequest, UserDTO, TokenDTO

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/register", response_model=UserDTO)
async def register(
    request: UserRegisterRequest,
    user_service: IUserService = Depends(),
):
    """用户注册"""
    result = await user_service.register(request)
    return JSONResponse(content=result.model_dump(), status_code=201)


@router.post("/login", response_model=TokenDTO)
async def login(
    request: UserLoginRequest,
    user_service: IUserService = Depends(),
):
    """用户登录"""
    result = await user_service.login(request)
    return JSONResponse(content=result.model_dump())


@router.get("/me", response_model=UserDTO)
async def get_current_user(
    current_user: UserDTO = Depends(),
):
    """获取当前用户信息"""
    return current_user
