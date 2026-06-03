"""
功能：通知 Repository 接口

实现逻辑：
    定义实时通知相关的 Redis 操作抽象接口
    使用 Redis Pub/Sub 推送实时通知

调用链路：
    - 被 business 层的 NotificationService 调用
    - 由 redis_repo 目录下的具体实现类实现
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class INotificationRepository(ABC):
    """通知数据访问接口（Redis Pub/Sub + List）"""

    @abstractmethod
    async def publish(self, channel: str, message: Dict[str, Any]) -> int:
        """发布通知消息到频道（PUBLISH）

        参数：
            channel: 频道名称（如 "notification:user:{user_id}"）
            message: 消息内容字典（会被序列化为 JSON）

        返回值：
            接收该消息的订阅者数量
        """
        ...

    @abstractmethod
    async def subscribe(self, channel: str):
        """订阅通知频道（SUBSCRIBE）

        参数：
            channel: 频道名称

        返回值：
            异步迭代器，逐条产出消息
        """
        ...

    @abstractmethod
    async def add_unread(self, user_id: int, notification: Dict[str, Any]) -> int:
        """存储未读通知（LPUSH + JSON）

        参数：
            user_id: 用户 ID
            notification: 完整的通知字典（含 id, type, content, timestamp 等）

        返回值：
            当前未读通知数
        """
        ...

    @abstractmethod
    async def get_unread_count(self, user_id: int) -> int:
        """获取未读通知数（LLEN）

        参数：
            user_id: 用户 ID

        返回值：
            未读通知数量
        """
        ...

    @abstractmethod
    async def list_notifications(self, user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """获取未读通知列表（LRANGE）

        参数：
            user_id: 用户 ID
            limit: 返回条数

        返回值：
            通知字典列表
        """
        ...

    @abstractmethod
    async def clear_unread(self, user_id: int) -> None:
        """清空未读通知列表（DEL）

        参数：
            user_id: 用户 ID
        """
        ...
