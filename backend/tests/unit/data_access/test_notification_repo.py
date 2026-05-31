"""
功能：NotificationRepository 单元测试

测试用例：
    - test_publish: PUBLISH 发布消息
    - test_add_unread: LPUSH 添加未读通知
    - test_get_unread_count: LLEN 获取未读数
"""

import json
import pytest

from app.data_access.redis_repo.notification_repo_impl import NotificationRepositoryImpl


@pytest.mark.asyncio
async def test_publish(fake_redis):
    """测试 PUBLISH 发布消息"""
    repo = NotificationRepositoryImpl(fake_redis)
    msg = {"type": "like", "content": "有人赞了你的帖子"}
    count = await repo.publish("notification:user:1", msg)
    # 没有订阅者，返回 0
    assert count == 0


@pytest.mark.asyncio
async def test_add_unread(fake_redis):
    """测试 LPUSH 添加未读通知"""
    repo = NotificationRepositoryImpl(fake_redis)
    count = await repo.add_unread(1, "notif_abc")
    assert count == 1

    count = await repo.add_unread(1, "notif_def")
    assert count == 2


@pytest.mark.asyncio
async def test_get_unread_count(fake_redis):
    """测试 LLEN 获取未读数"""
    repo = NotificationRepositoryImpl(fake_redis)
    assert await repo.get_unread_count(1) == 0

    await repo.add_unread(1, "notif_a")
    await repo.add_unread(1, "notif_b")
    await repo.add_unread(1, "notif_c")

    assert await repo.get_unread_count(1) == 3
