"""
功能：通知相关路由

实现逻辑：
    1. GET /api/notifications/unread-count — 获取未读通知数（需登录）

调用链路：
    - 调用 INotificationService 接口
"""

from fastapi import APIRouter, Depends

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
