"""FastAPI 依赖注入集中管理"""

from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.business.interfaces.user_service import IUserService
from app.business.interfaces.post_service import IPostService
from app.business.interfaces.like_service import ILikeService
from app.business.interfaces.rank_service import IRankService
from app.business.interfaces.comment_service import ICommentService
from app.business.interfaces.notification_service import INotificationService
from app.business.interfaces.club_service import IClubService
from app.business.interfaces.event_service import IEventService
from app.business.interfaces.lost_item_service import ILostItemService
from app.business.interfaces.admin_service import IAdminService
from app.business.impl.user_service_impl import UserServiceImpl
from app.business.impl.post_service_impl import PostServiceImpl
from app.business.impl.like_service_impl import LikeServiceImpl
from app.business.impl.rank_service_impl import RankServiceImpl
from app.business.impl.comment_service_impl import CommentServiceImpl
from app.business.impl.notification_service_impl import NotificationServiceImpl
from app.business.impl.club_service_impl import ClubServiceImpl
from app.business.impl.event_service_impl import EventServiceImpl
from app.business.impl.lost_item_service_impl import LostItemServiceImpl
from app.business.impl.admin_service_impl import AdminServiceImpl
from app.business.impl.auth_utils import decode_access_token
from app.data_access.sqlite_dao.user_dao_impl import UserDAOImpl
from app.data_access.sqlite_dao.post_dao_impl import PostDAOImpl
from app.data_access.sqlite_dao.club_dao_impl import ClubDAOImpl
from app.data_access.sqlite_dao.comment_dao_impl import CommentDAOImpl
from app.data_access.sqlite_dao.event_dao_impl import EventDAOImpl
from app.data_access.sqlite_dao.event_participant_dao_impl import EventParticipantDAOImpl
from app.data_access.redis_repo.event_registration_repo_impl import EventRegistrationRepoImpl
from app.data_access.sqlite_dao.lost_item_dao_impl import LostItemDAOImpl
from app.data_access.sqlite_dao.club_member_dao_impl import ClubMemberDAOImpl
from app.data_access.redis_repo.like_repo_impl import LikeRepositoryImpl
from app.data_access.redis_repo.rank_repo_impl import RankRepositoryImpl
from app.data_access.redis_repo.notification_repo_impl import NotificationRepositoryImpl
from app.data_access.redis_repo.lost_item_repo_impl import LostItemRepositoryImpl
from app.data_access.redis_repo.blacklist_repo_impl import BlacklistRepoImpl
from app.infrastructure.db import get_db
from app.infrastructure.redis_client import get_redis
from app.infrastructure.exceptions import ForbiddenError
from app.models.dto import UserDTO

security = HTTPBearer(auto_error=False)
security_required = HTTPBearer(auto_error=True)


async def get_user_service(db: AsyncSession = Depends(get_db)) -> IUserService:
    user_dao = UserDAOImpl(db)
    return UserServiceImpl(user_dao=user_dao, db_session=db)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_required),
    user_service: IUserService = Depends(get_user_service),
) -> UserDTO:
    token = credentials.credentials
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="无效的访问令牌", headers={"WWW-Authenticate": "Bearer"})
    user_id_str = payload.get("sub")
    if user_id_str is None:
        raise HTTPException(status_code=401, detail="令牌 payload 无效", headers={"WWW-Authenticate": "Bearer"})
    user = await user_service.get_user_by_id(int(user_id_str))
    if user is None:
        raise HTTPException(status_code=401, detail="用户不存在", headers={"WWW-Authenticate": "Bearer"})
    return user


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    user_service: IUserService = Depends(get_user_service),
) -> Optional[UserDTO]:
    if credentials is None:
        return None
    payload = decode_access_token(credentials.credentials)
    if payload is None:
        return None
    user_id_str = payload.get("sub")
    if user_id_str is None:
        return None
    try:
        return await user_service.get_user_by_id(int(user_id_str))
    except Exception:
        return None


async def get_redis_client():
    try:
        return await get_redis()
    except ConnectionError:
        raise HTTPException(status_code=503, detail="Redis 服务不可用")


async def get_current_admin_user(
    current_user: UserDTO = Depends(get_current_user),
) -> UserDTO:
    if current_user.role != "admin":
        raise ForbiddenError(code="ADMIN_REQUIRED", message="需要管理员权限")
    return current_user


async def check_not_banned(
    current_user: UserDTO = Depends(get_current_user),
    redis=Depends(get_redis_client),
) -> UserDTO:
    repo = BlacklistRepoImpl(redis)
    if await repo.is_banned(current_user.id):
        raise ForbiddenError(code="BANNED_USER", message="账号已被封禁")
    return current_user


async def get_post_service(
    redis=Depends(get_redis_client),
    db: AsyncSession = Depends(get_db),
) -> IPostService:
    post_dao = PostDAOImpl(db)
    club_dao = ClubDAOImpl(db)
    like_repo = LikeRepositoryImpl(redis) if redis else None
    rank_repo = RankRepositoryImpl(redis)
    rank_service = RankServiceImpl(rank_repo=rank_repo, like_repo=like_repo, post_dao=post_dao, club_dao=club_dao)
    return PostServiceImpl(post_dao=post_dao, db_session=db, like_repo=like_repo, club_dao=club_dao, rank_service=rank_service)


async def get_notification_service(
    redis=Depends(get_redis_client),
) -> INotificationService:
    notification_repo = NotificationRepositoryImpl(redis)
    return NotificationServiceImpl(notification_repo=notification_repo)


async def get_like_service(
    redis=Depends(get_redis_client),
    db: AsyncSession = Depends(get_db),
) -> ILikeService:
    like_repo = LikeRepositoryImpl(redis)
    rank_repo = RankRepositoryImpl(redis)
    post_dao = PostDAOImpl(db)
    return LikeServiceImpl(
        like_repo=like_repo, rank_repo=rank_repo, post_dao=post_dao,
        notification_service=await get_notification_service(redis=redis),
    )


async def get_rank_service(
    redis=Depends(get_redis_client),
    db: AsyncSession = Depends(get_db),
) -> IRankService:
    rank_repo = RankRepositoryImpl(redis)
    like_repo = LikeRepositoryImpl(redis)
    post_dao = PostDAOImpl(db)
    club_dao = ClubDAOImpl(db)
    return RankServiceImpl(rank_repo=rank_repo, like_repo=like_repo, post_dao=post_dao, club_dao=club_dao)


async def get_event_service(
    redis=Depends(get_redis_client),
    db: AsyncSession = Depends(get_db),
) -> IEventService:
    event_dao = EventDAOImpl(db)
    participant_dao = EventParticipantDAOImpl(db)
    registration_repo = EventRegistrationRepoImpl(redis)
    return EventServiceImpl(event_dao=event_dao, db_session=db, participant_dao=participant_dao, registration_repo=registration_repo)


async def get_club_service(
    db: AsyncSession = Depends(get_db),
) -> IClubService:
    club_dao = ClubDAOImpl(db)
    club_member_dao = ClubMemberDAOImpl(db)
    return ClubServiceImpl(club_dao=club_dao, db_session=db, club_member_dao=club_member_dao)


async def get_lost_item_service(
    redis=Depends(get_redis_client),
    db: AsyncSession = Depends(get_db),
) -> ILostItemService:
    dao = LostItemDAOImpl(db)
    repo = LostItemRepositoryImpl(redis)
    return LostItemServiceImpl(lost_item_dao=dao, lost_item_repo=repo, db_session=db)


async def get_comment_service(
    redis=Depends(get_redis_client),
    db: AsyncSession = Depends(get_db),
) -> ICommentService:
    comment_dao = CommentDAOImpl(db)
    post_dao = PostDAOImpl(db)
    return CommentServiceImpl(
        comment_dao=comment_dao, post_dao=post_dao, db_session=db,
        notification_service=await get_notification_service(redis=redis),
    )


async def get_admin_service(
    redis=Depends(get_redis_client),
    db: AsyncSession = Depends(get_db),
) -> IAdminService:
    return AdminServiceImpl(
        user_dao=UserDAOImpl(db),
        post_dao=PostDAOImpl(db),
        comment_dao=CommentDAOImpl(db),
        club_dao=ClubDAOImpl(db),
        event_dao=EventDAOImpl(db),
        lost_item_dao=LostItemDAOImpl(db),
        blacklist_repo=BlacklistRepoImpl(redis),
        db_session=db,
    )
