"""
功能：通知业务逻辑实现

实现逻辑：
    1. send_notification: 构建通知 → UUID → PUBLISH → LPUSH
    2. get_unread_count: LLEN 获取未读列表长度

调用链路：
    - 被 LikeService / CommentService 在事件触发时调用
    - 调用 INotificationRepository（Redis Pub/Sub + List）
"""

import uuid
from typing import Any, Dict

from app.business.interfaces.notification_service import INotificationService
from app.data_access.redis_repo.notification_repo import INotificationRepository
from app.infrastructure.logger import get_logger

logger = get_logger(__name__)


class NotificationServiceImpl(INotificationService):
    """通知服务实现"""

    def __init__(self, notification_repo: INotificationRepository):
        self.notification_repo = notification_repo

    async def send_notification(
        self, user_id: int, data: Dict[str, Any]
    ) -> None:
        """发送实时通知

        实现逻辑：
            1. 生成唯一通知 ID（UUID）
            2. 构建完整通知消息（含 id + 时间戳）
            3. 通过 Redis PUBLISH 推送到用户通知频道
            4. 通过 LPUSH 将通知 ID 存入用户未读列表

        参数：
            user_id: 目标用户 ID
            data: 通知数据（type, content, sender_id, post_id 等）
        """
        from datetime import datetime, timezone

        notification_id = str(uuid.uuid4())
        notification = {
            "id": notification_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **data,
        }

        channel = f"notification:user:{user_id}"
        subscribers = await self.notification_repo.publish(channel, notification)
        await self.notification_repo.add_unread(user_id, notification_id)

        logger.info(
            f"Notification sent to user #{user_id}: type={data.get('type')}, "
            f"subscribers={subscribers}"
        )

    async def get_unread_count(self, user_id: int) -> int:
        """获取未读通知数"""
        return await self.notification_repo.get_unread_count(user_id)
