"""
功能：FastAPI 依赖注入集中管理

实现逻辑：
    1. get_user_service: UserDAOImpl → UserServiceImpl
    2. get_current_user: JWT 解码 → 查用户 → UserDTO
    3. get_post_service: PostDAOImpl → PostServiceImpl
    4. get_redis_client: Redis 异步客户端单例
    5. get_like_service: LikeRepositoryImpl + RankRepositoryImpl → LikeServiceImpl

调用链路：
    - 被 presentation/api/*.py 路由通过 Depends() 调用
    - 调用 infrastructure/db.py / redis_client.py 获取连接
    - 调用 business/impl 的具体实现类
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.business.interfaces.user_service import IUserService
from app.business.interfaces.post_service import IPostService
from app.business.interfaces.like_service import ILikeService
from app.business.interfaces.rank_service import IRankService
from app.business.impl.user_service_impl import UserServiceImpl
from app.business.impl.post_service_impl import PostServiceImpl
from app.business.impl.like_service_impl import LikeServiceImpl
from app.business.impl.rank_service_impl import RankServiceImpl
from app.business.impl.auth_utils import decode_access_token
from app.data_access.sqlite_dao.user_dao_impl import UserDAOImpl
from app.data_access.sqlite_dao.post_dao_impl import PostDAOImpl
from app.data_access.sqlite_dao.club_dao_impl import ClubDAOImpl
from app.data_access.redis_repo.like_repo_impl import LikeRepositoryImpl
from app.data_access.redis_repo.rank_repo_impl import RankRepositoryImpl
from app.infrastructure.db import get_db
from app.infrastructure.redis_client import get_redis
from app.models.dto import UserDTO

security = HTTPBearer()


async def get_user_service(db: AsyncSession = Depends(get_db)) -> IUserService:
    """依赖注入：获取 UserService 实例"""
    user_dao = UserDAOImpl(db)
    return UserServiceImpl(user_dao=user_dao, db_session=db)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user_service: IUserService = Depends(get_user_service),
) -> UserDTO:
    """依赖注入：获取当前登录用户（JWT 认证）"""
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


async def get_post_service(db: AsyncSession = Depends(get_db)) -> IPostService:
    """依赖注入：获取 PostService 实例"""
    post_dao = PostDAOImpl(db)
    return PostServiceImpl(post_dao=post_dao, db_session=db)


async def get_redis_client():
    """依赖注入：获取 Redis 异步客户端

    实现逻辑：
        1. 尝试获取 Redis 连接
        2. 如果 Redis 不可用，抛出 503 错误（清晰提示而非 500）

    Redis 连接在 main.py lifespan 中初始化，此处获取单例
    """
    try:
        return await get_redis()
    except ConnectionError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Redis 服务不可用，该功能需要 Redis。请执行 docker compose up -d 启动 Redis。",
        )


async def get_like_service(
    redis=Depends(get_redis_client),
    db: AsyncSession = Depends(get_db),
) -> ILikeService:
    """依赖注入：获取 LikeService 实例

    实现逻辑：
        1. 创建 LikeRepositoryImpl（注入 Redis）
        2. 创建 RankRepositoryImpl（注入 Redis）
        3. 创建 PostDAOImpl（注入 SQLite session，用于校验帖子存在）
        4. 创建 LikeServiceImpl（注入 like_repo + rank_repo + post_dao）
    """
    like_repo = LikeRepositoryImpl(redis)
    rank_repo = RankRepositoryImpl(redis)
    post_dao = PostDAOImpl(db)
    return LikeServiceImpl(
        like_repo=like_repo,
        rank_repo=rank_repo,
        post_dao=post_dao,
    )


async def get_rank_service(
    redis=Depends(get_redis_client),
    db: AsyncSession = Depends(get_db),
) -> IRankService:
    """依赖注入：获取 RankService 实例

    实现逻辑：
        1. 创建 Redis Repository 实例
        2. 创建 SQLite DAO 实例
        3. 创建 RankServiceImpl（注入所有依赖）
    """
    rank_repo = RankRepositoryImpl(redis)
    like_repo = LikeRepositoryImpl(redis)
    post_dao = PostDAOImpl(db)
    club_dao = ClubDAOImpl(db)
    return RankServiceImpl(
        rank_repo=rank_repo,
        like_repo=like_repo,
        post_dao=post_dao,
        club_dao=club_dao,
    )
