"""
功能：Redis 异步客户端单例管理

实现逻辑：
    1. 基于 redis.asyncio 创建异步 Redis 连接
    2. get_redis() 返回全局单例 Redis 客户端（首次调用时创建连接）
    3. close_redis() 在应用关闭时释放连接
    4. 连接参数从 settings 读取

调用链路：
    - 被 data_access/redis_repo 层用于执行 Redis 命令
    - 被 presentation/websocket 用于订阅 Pub/Sub
    - 被 main.py 中的 lifespan 事件调用初始化/关闭

参数说明：
    settings.redis_url: 自动构建的 Redis 连接 URL

返回值：
    get_redis(): Redis 异步客户端实例

测试用例：
    - test_get_redis_singleton
"""

from typing import Optional

from redis.asyncio import Redis

from app.infrastructure.config import settings
from app.infrastructure.logger import get_logger

logger = get_logger(__name__)

_redis_client: Optional[Redis] = None


async def get_redis() -> Redis:
    """获取全局 Redis 客户端单例

    实现逻辑：
        1. 如果 _redis_client 尚未创建，则创建新连接
        2. 如果连接已存在且可用，直接返回
        3. 使用 decode_responses=True 确保返回字符串而非字节

    返回值：
        Redis 异步客户端实例
    """
    global _redis_client

    if _redis_client is None:
        _redis_client = Redis.from_url(
            settings.redis_url,
            decode_responses=True,
        )
        await _redis_client.ping()
        logger.info(f"Redis connected at {settings.REDIS_HOST}:{settings.REDIS_PORT}")

    return _redis_client


async def close_redis():
    """关闭 Redis 连接

    实现逻辑：
        1. 关闭 Redis 连接池
        2. 将全局变量置为 None
    """
    global _redis_client

    if _redis_client is not None:
        await _redis_client.aclose()
        _redis_client = None
        logger.info("Redis connection closed")
