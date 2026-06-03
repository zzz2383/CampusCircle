"""
功能：NotificationRepository 单元测试

测试用例：
    - test_publish: PUBLISH 发布消息
    - test_add_unread: LPUSH 存储完整通知 JSON
    - test_get_unread_count: LLEN 获取未读数
    - test_list_notifications: LRANGE 获取通知列表
    - test_clear_unread: DEL 清空未读列表
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
    assert count == 0


@pytest.mark.asyncio
async def test_add_unread(fake_redis):
    """测试 LPUSH 存储完整通知 JSON"""
    repo = NotificationRepositoryImpl(fake_redis)
    notif = {"id": "n1", "type": "like", "content": "赞了你的帖子"}
    count = await repo.add_unread(1, notif)
    assert count == 1

    notif2 = {"id": "n2", "type": "comment", "content": "评论了你的帖子"}
    count = await repo.add_unread(1, notif2)
    assert count == 2

    # 验证存储的是 JSON 而非 ID
    key = "notification:list:1"
    raw = await fake_redis.lrange(key, 0, -1)
    assert len(raw) == 2
    first = json.loads(raw[0])
    assert first["id"] == "n2"
    assert first["type"] == "comment"


@pytest.mark.asyncio
async def test_get_unread_count(fake_redis):
    """测试 LLEN 获取未读数"""
    repo = NotificationRepositoryImpl(fake_redis)
    assert await repo.get_unread_count(1) == 0

    await repo.add_unread(1, {"id": "a", "type": "like"})
    await repo.add_unread(1, {"id": "b", "type": "comment"})
    await repo.add_unread(1, {"id": "c", "type": "follow"})

    assert await repo.get_unread_count(1) == 3


@pytest.mark.asyncio
async def test_list_notifications(fake_redis):
    """测试 LRANGE 获取通知列表"""
    repo = NotificationRepositoryImpl(fake_redis)
    notifs = [
        {"id": "n1", "type": "like", "content": "赞"},
        {"id": "n2", "type": "comment", "content": "评论"},
        {"id": "n3", "type": "follow", "content": "关注"},
    ]
    for n in notifs:
        await repo.add_unread(1, n)

    result = await repo.list_notifications(1, limit=2)
    assert len(result) == 2
    # 最新在前（LPUSH 后 LRANGE 最新在前）
    assert result[0]["id"] == "n3"
    assert result[1]["id"] == "n2"


@pytest.mark.asyncio
async def test_clear_unread(fake_redis):
    """测试 DEL 清空未读列表"""
    repo = NotificationRepositoryImpl(fake_redis)
    await repo.add_unread(1, {"id": "n1", "type": "like"})
    await repo.add_unread(1, {"id": "n2", "type": "comment"})
    assert await repo.get_unread_count(1) == 2

    await repo.clear_unread(1)
    assert await repo.get_unread_count(1) == 0
