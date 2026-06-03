"""
功能：通知业务逻辑接口

实现逻辑：
    定义实时通知的发送和管理等业务操作抽象接口

调用链路：
    - 被表现层的 notifications 路由调用
    - 被其他 Service（LikeService 等）在事件触发时调用
    - 调用数据访问层的 NotificationRepository
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class INotificationService(ABC):
    """通知服务接口"""

    @abstractmethod
    async def send_notification(
        self, user_id: int, data: Dict[str, Any]
    ) -> None:
        """发送实时通知

        实现逻辑：
            1. 构建通知消息体（类型、内容、时间戳）
            2. 通过 Redis Pub/Sub 发布到通知频道
            3. 将通知 ID LPUSH 到用户未读通知列表

        参数：
            user_id: 目标用户 ID
            data: 通知数据（type, content, sender_id, post_id 等）

        测试用例：
            - test_send_notification_success
        """
        ...

    @abstractmethod
    async def get_unread_count(self, user_id: int) -> int:
        """获取未读通知数"""
        ...

    @abstractmethod
    async def get_notifications(self, user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """获取未读通知列表

        参数：
            user_id: 用户 ID
            limit: 返回条数

        返回值：
            通知字典列表
        """
        ...

    @abstractmethod
    async def mark_as_read(self, user_id: int) -> None:
        """标记所有通知为已读（清空未读列表）

        参数：
            user_id: 用户 ID
        """
        ...
