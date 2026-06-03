"""通知相关路由"""
from fastapi import APIRouter, Depends, Query

from app.business.interfaces import INotificationService
from app.models.dto import UserDTO
from app.presentation.dependencies import get_notification_service, get_current_user

router = APIRouter(prefix="/api/notifications", tags=["通知"])


@router.get("/unread-count")
async def get_unread_count(
    current_user: UserDTO = Depends(get_current_user),
    notification_service: INotificationService = Depends(get_notification_service),
):
    """获取未读通知数（需要登录）"""
    count = await notification_service.get_unread_count(user_id=current_user.id)
    return {"unread_count": count}


@router.get("")
async def get_notifications(
    limit: int = Query(20, ge=1, le=100, description="返回条数"),
    current_user: UserDTO = Depends(get_current_user),
    notification_service: INotificationService = Depends(get_notification_service),
):
    """获取未读通知列表（需要登录）"""
    notifications = await notification_service.get_notifications(
        user_id=current_user.id, limit=limit
    )
    return {"notifications": notifications, "count": len(notifications)}


@router.post("/read")
async def mark_as_read(
    current_user: UserDTO = Depends(get_current_user),
    notification_service: INotificationService = Depends(get_notification_service),
):
    """标记所有通知为已读（需要登录）"""
    await notification_service.mark_as_read(user_id=current_user.id)
    return {"success": True, "message": "已标记为已读"}
