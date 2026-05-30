"""
功能：通知相关路由

实现逻辑：
    1. GET /api/notifications/unread-count — 获取未读通知数

调用链路：
    - 调用 INotificationService 接口
"""

from fastapi import APIRouter, Depends

from app.business.interfaces import INotificationService

router = APIRouter(prefix="/api/notifications", tags=["通知"])


@router.get("/unread-count")
async def get_unread_count(
    current_user=Depends(),
    notification_service: INotificationService = Depends(),
):
    """获取未读通知数"""
    count = await notification_service.get_unread_count(user_id=current_user.id)
    return {"unread_count": count}
