"""
功能：NotificationService 单元测试

测试用例：
    - test_send_notification: 发送通知 → PUBLISH + LPUSH（完整 JSON）
    - test_get_unread_count: 获取未读数
    - test_get_notifications: 获取通知列表
    - test_mark_as_read: 标记已读
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.business.impl.notification_service_impl import NotificationServiceImpl
from app.data_access.redis_repo.notification_repo import INotificationRepository


@pytest.fixture
def mock_notification_repo() -> MagicMock:
    return AsyncMock(spec=INotificationRepository)


@pytest.fixture
def service(mock_notification_repo) -> NotificationServiceImpl:
    return NotificationServiceImpl(notification_repo=mock_notification_repo)


@pytest.mark.asyncio
async def test_send_notification(service, mock_notification_repo):
    """测试发送通知"""
    mock_notification_repo.publish.return_value = 1
    mock_notification_repo.add_unread.return_value = 1

    await service.send_notification(
        user_id=2,
        data={
            "type": "like",
            "content": "用户1 赞了你的帖子",
            "sender_id": 1,
            "post_id": 100,
        },
    )

    # 验证 publish 调用
    publish_call = mock_notification_repo.publish.await_args
    assert publish_call is not None
    channel = publish_call[0][0]
    assert channel == "notification:user:2"

    # 验证 add_unread 调用 — 存储的是完整通知字典
    mock_notification_repo.add_unread.assert_awaited_once()
    add_call = mock_notification_repo.add_unread.await_args
    assert add_call[0][0] == 2  # user_id
    notif_dict = add_call[0][1]  # 通知字典
    assert isinstance(notif_dict, dict)
    assert notif_dict["type"] == "like"
    assert "id" in notif_dict
    assert "timestamp" in notif_dict


@pytest.mark.asyncio
async def test_get_unread_count(service, mock_notification_repo):
    """测试获取未读数"""
    mock_notification_repo.get_unread_count.return_value = 5

    count = await service.get_unread_count(user_id=1)
    assert count == 5
    mock_notification_repo.get_unread_count.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_get_notifications(service, mock_notification_repo):
    """测试获取通知列表"""
    expected = [
        {"id": "n1", "type": "like", "content": "赞"},
        {"id": "n2", "type": "comment", "content": "评论"},
    ]
    mock_notification_repo.list_notifications.return_value = expected

    result = await service.get_notifications(user_id=1, limit=10)

    assert len(result) == 2
    assert result[0]["type"] == "like"
    mock_notification_repo.list_notifications.assert_awaited_once_with(1, limit=10)


@pytest.mark.asyncio
async def test_mark_as_read(service, mock_notification_repo):
    """测试标记已读"""
    await service.mark_as_read(user_id=1)
    mock_notification_repo.clear_unread.assert_awaited_once_with(1)
