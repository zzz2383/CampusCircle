"""
功能：WebSocket 连接管理器

实现逻辑：
    1. 用户通过 ws://host:port/ws?token=JWT 连接
    2. JWT 解码后获取 user_id，建立连接
    3. 订阅 Redis Pub/Sub 通知频道
    4. 收到通知后实时推送给用户
    5. 断开连接时清理资源

调用链路：
    - 被 main.py 注册为 FastAPI WebSocket 入口
    - 调用 infrastructure/redis_client 获取 Redis 连接
"""

import json
from typing import Any, Dict, Set

from fastapi import WebSocket, WebSocketDisconnect
from redis.asyncio import Redis

from app.infrastructure.logger import get_logger
from app.business.impl.auth_utils import decode_access_token

logger = get_logger(__name__)


class ConnectionManager:
    """WebSocket 连接管理器"""

    def __init__(self):
        self.active_connections: Dict[int, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        logger.info(f"User #{user_id} connected via WebSocket")

    def disconnect(self, websocket: WebSocket, user_id: int):
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        logger.info(f"User #{user_id} disconnected from WebSocket")

    async def send_personal_message(self, user_id: int, message: dict):
        if user_id in self.active_connections:
            for ws in self.active_connections[user_id]:
                try:
                    await ws.send_text(json.dumps(message))
                except Exception:
                    self.disconnect(ws, user_id)


manager = ConnectionManager()


async def websocket_handler(websocket: WebSocket, token: str = ""):
    """WebSocket 主处理器

    通过查询参数 token 传递 JWT，解码后获取 user_id
    订阅 Redis 通知频道，实时推送通知给客户端
    """
    # JWT 认证
    payload = decode_access_token(token)
    if payload is None:
        await websocket.close(code=4001, reason="无效的令牌")
        return

    user_id = int(payload.get("sub") or 0)
    await manager.connect(websocket, user_id)

    # 尝试连接 Redis 订阅通知
    redis: Redis = Redis.from_url("redis://...")
    pubsub = None
    try:
        from app.infrastructure.redis_client import get_redis
        redis = await get_redis()
        pubsub = redis.pubsub()
        await pubsub.subscribe(f"notification:user:{user_id}")
        logger.info(f"User #{user_id} subscribed to notification channel")
    except Exception as e:
        logger.warning(f"Redis PubSub not available for user #{user_id}: {e}")

    try:
        import asyncio
        while True:
            # 用 wait_for 同时监听 WebSocket 消息和 Redis 消息
            receive_task = asyncio.create_task(websocket.receive_text())
            redis_task = None
            if pubsub:
                redis_task = asyncio.create_task(
                    pubsub.get_message(ignore_subscribe_messages=True, timeout=30)
                )

            tasks: list[asyncio.Task[Any]] = [receive_task]   # 明确列表可以包含任意返回类型的任务
            if redis_task:
                tasks.append(redis_task)

            done, _ = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

            if receive_task in done:
                data = receive_task.result()
                if data == "ping":
                    await websocket.send_text("pong")

            if redis_task and redis_task in done:
                msg = redis_task.result()
                if msg and msg.get("data"):
                    # 转发 Redis 通知到 WebSocket
                    await websocket.send_text(msg["data"])

            # 取消未完成的任务
            for t in tasks:
                if not t.done():
                    t.cancel()

    except WebSocketDisconnect:
        logger.info(f"User #{user_id} WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error for user #{user_id}: {e}")
    finally:
        manager.disconnect(websocket, user_id)
        if pubsub:
            await pubsub.unsubscribe()
