"""管理后台业务逻辑实现"""
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.business.interfaces.admin_service import IAdminService
from app.data_access.sqlite_dao.user_dao import IUserDAO
from app.data_access.sqlite_dao.post_dao import IPostDAO
from app.data_access.sqlite_dao.comment_dao import ICommentDAO
from app.data_access.sqlite_dao.club_dao import IClubDAO
from app.data_access.sqlite_dao.event_dao import IEventDAO
from app.data_access.sqlite_dao.lost_item_dao import ILostItemDAO
from app.data_access.redis_repo.blacklist_repo import IBlacklistRepo
from app.infrastructure.exceptions import BusinessError, ForbiddenError
from app.infrastructure.logger import get_logger
from app.models.dto import UserDTO, CommentDTO

logger = get_logger(__name__)


class AdminServiceImpl(IAdminService):
    def __init__(
        self,
        user_dao: IUserDAO, post_dao: IPostDAO, comment_dao: ICommentDAO,
        club_dao: IClubDAO, event_dao: IEventDAO, lost_item_dao: ILostItemDAO,
        blacklist_repo: IBlacklistRepo, db_session: AsyncSession,
    ):
        self.user_dao = user_dao
        self.post_dao = post_dao
        self.comment_dao = comment_dao
        self.club_dao = club_dao
        self.event_dao = event_dao
        self.lost_item_dao = lost_item_dao
        self.blacklist_repo = blacklist_repo
        self.db_session = db_session

    # ========== 内容管理 ==========

    async def delete_post(self, post_id: int) -> bool:
        result = await self.post_dao.delete(post_id)
        await self.db_session.commit()
        logger.info(f"Admin deleted post #{post_id}")
        return result

    async def delete_comment(self, comment_id: int) -> bool:
        result = await self.comment_dao.delete(comment_id)
        await self.db_session.commit()
        return result

    async def delete_event(self, event_id: int) -> bool:
        result = await self.event_dao.delete(event_id)
        await self.db_session.commit()
        return result

    async def delete_lost_item(self, item_id: int) -> bool:
        result = await self.lost_item_dao.delete(item_id)
        await self.db_session.commit()
        return result

    async def delete_club(self, club_id: int) -> bool:
        result = await self.club_dao.delete(club_id)
        await self.db_session.commit()
        return result

    async def list_all_comments(self, offset: int = 0, limit: int = 20) -> dict:
        comments = await self.comment_dao.list_all(offset=offset, limit=limit)
        items = []
        for c in comments:
            items.append(CommentDTO(
                id=c.id, post_id=c.post_id, user_id=c.user_id,
                author_nickname=c.author.nickname if c.author else None,
                content=c.content, parent_id=c.parent_id, created_at=c.created_at,
            ))
        return {"items": items, "total": len(items), "offset": offset, "limit": limit}

    # ========== 用户管理 ==========

    async def list_users(self, offset: int = 0, limit: int = 20, keyword: Optional[str] = None) -> dict:
        users = await self.user_dao.list_all(offset=offset, limit=limit, keyword=keyword)
        total = await self.user_dao.count_all()
        items = [UserDTO.model_validate(u) for u in users]
        return {"items": items, "total": total, "offset": offset, "limit": limit}

    async def get_user(self, user_id: int) -> Optional[UserDTO]:
        user = await self.user_dao.get_by_id(user_id)
        if user is None:
            return None
        return UserDTO.model_validate(user)

    VALID_ROLES = {"student", "teacher"}

    async def set_role(self, user_id: int, role: str, current_user_id: int) -> Optional[UserDTO]:
        if user_id == current_user_id:
            raise ForbiddenError(code="SELF_ROLE_CHANGE", message="不能修改自己的角色")
        if role not in self.VALID_ROLES:
            raise BusinessError(code="INVALID_ROLE", message=f"无效的角色值: {role}，仅支持 student/teacher")
        user = await self.user_dao.get_by_id(user_id)
        if user is None:
            return None
        await self.user_dao.update_role(user_id, role)
        await self.db_session.commit()
        updated = await self.user_dao.get_by_id(user_id)
        return UserDTO.model_validate(updated)

    async def ban_user(self, user_id: int, duration_hours: int = 24) -> None:
        await self.blacklist_repo.ban(user_id, duration_hours)

    async def unban_user(self, user_id: int) -> None:
        await self.blacklist_repo.unban(user_id)

    async def list_banned(self) -> List[Dict[str, Any]]:
        return await self.blacklist_repo.list_banned()

    async def get_stats(self) -> Dict[str, int]:
        return {
            "total_users": await self.user_dao.count_all(),
            "total_posts": await self.post_dao.count_all(),
            "total_clubs": await self.club_dao.count_all(),
            "total_events": await self.event_dao.count_all(),
            "total_lost_items": await self.lost_item_dao.count_all(),
        }
