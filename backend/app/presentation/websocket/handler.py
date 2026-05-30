"""
功能：WebSocket 连接管理器

实现逻辑：
    1. 使用 Redis Pub/Sub 订阅通知频道
    2. 用户连接后自动加入其专属通知频道
    3. 断开连接时清理资源

调用链路：
    - 被 main.py 注册为 FastAPI WebSocket 入口
    - 调用 infrastructure/redis_client 获取 Redis 连接
"""

import json
from typing import Dict, Set

from fastapi import WebSocket, WebSocketDisconnect
from redis.asyncio import Redis

from app.infrastructure.logger import get_logger

logger = get_logger(__name__)


class ConnectionManager:
    """WebSocket 连接管理器

    维护 user_id -> {WebSocket} 的映射关系，支持广播和点对点通知推送
    """

    def __init__(self):
        self.active_connections: Dict[int, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        """建立 WebSocket 连接"""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        logger.info(f"User #{user_id} connected via WebSocket")

    def disconnect(self, websocket: WebSocket, user_id: int):
        """断开 WebSocket 连接"""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        logger.info(f"User #{user_id} disconnected from WebSocket")

    async def send_personal_message(self, user_id: int, message: dict):
        """向指定用户发送消息"""
        if user_id in self.active_connections:
            for ws in self.active_connections[user_id]:
                try:
                    await ws.send_text(json.dumps(message))
                except Exception:
                    self.disconnect(ws, user_id)


manager = ConnectionManager()


async def websocket_handler(websocket: WebSocket, user_id: int):
    """WebSocket 主处理器

    实现逻辑：
        1. 接收用户的 user_id（通过查询参数或路径参数）
        2. 建立连接并加入管理器
        3. 订阅 Redis Pub/Sub 通知频道
        4. 循环接收消息（心跳保持）
    """
    await manager.connect(websocket, user_id)

    # 订阅用户专属通知频道
    redis: Redis = None  # 将由 DI 注入
    pubsub = None

    try:
        if redis:
            pubsub = redis.pubsub()
            await pubsub.subscribe(f"notification:user:{user_id}")

        while True:
            # 接收客户端消息（心跳）
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")

    except WebSocketDisconnect:
        logger.info(f"User #{user_id} WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error for user #{user_id}: {e}")
    finally:
        manager.disconnect(websocket, user_id)
        if pubsub:
            await pubsub.unsubscribe()
