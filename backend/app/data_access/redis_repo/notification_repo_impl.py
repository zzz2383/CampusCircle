"""
功能：通知 Repository 实现（Redis Pub/Sub + List）

实现逻辑：
    1. publish: PUBLISH 到通知频道（JSON 序列化消息体）
    2. add_unread: LPUSH 完整通知 JSON 到用户未读列表
    3. get_unread_count: LLEN 获取列表长度
    4. list_notifications: LRANGE 获取未读通知列表
    5. clear_unread: DEL 清空未读列表

Key 命名规范：
    notification:list:{user_id} — 用户未读通知列表（完整 JSON）
    notification:user:{user_id} — 用户 Pub/Sub 频道

测试用例：
    - tests/unit/data_access/test_notification_repo.py
"""

import json
from typing import Any, Dict, List

from redis.asyncio import Redis

from app.data_access.redis_repo.notification_repo import INotificationRepository


class NotificationRepositoryImpl(INotificationRepository):
    """通知数据访问实现（Redis）"""

    NOTIFICATION_LIST_KEY = "notification:list:{}"

    def __init__(self, redis: Redis):
        self.redis = redis

    async def publish(self, channel: str, message: Dict[str, Any]) -> int:
        """发布通知消息到频道

        PUBLISH channel json_message
        """
        return await self.redis.publish(channel, json.dumps(message))

    async def subscribe(self, channel: str):
        """订阅通知频道"""
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(channel)
        return pubsub

    async def add_unread(self, user_id: int, notification: Dict[str, Any]) -> int:
        """存储未读通知

        LPUSH notification:list:{user_id} json_notification
        """
        key = self.NOTIFICATION_LIST_KEY.format(user_id)
        return await self.redis.lpush(key, json.dumps(notification))

    async def get_unread_count(self, user_id: int) -> int:
        """获取未读通知数

        LLEN notification:list:{user_id}
        """
        key = self.NOTIFICATION_LIST_KEY.format(user_id)
        return await self.redis.llen(key)

    async def list_notifications(self, user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """获取未读通知列表

        LRANGE notification:list:{user_id} 0 limit-1
        """
        key = self.NOTIFICATION_LIST_KEY.format(user_id)
        raw_list = await self.redis.lrange(key, 0, limit - 1)
        result = []
        for raw in raw_list:
            try:
                result.append(json.loads(raw))
            except (json.JSONDecodeError, TypeError):
                continue
        return result

    async def clear_unread(self, user_id: int) -> None:
        """清空未读通知列表

        DEL notification:list:{user_id}
        """
        key = self.NOTIFICATION_LIST_KEY.format(user_id)
        await self.redis.delete(key)
