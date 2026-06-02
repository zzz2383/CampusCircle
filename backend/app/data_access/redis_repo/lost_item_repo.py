"""失物招领 Redis Repository 接口

实现逻辑：
    使用 Redis SETEX 实现失物招领条目自动过期
    Key 命名：lost:item:{id} → value 为 item_id 的字符串

调用链路：
    - 被 business 层的 LostItemService 调用
    - 由 redis_repo 目录下的具体实现类实现
"""
from abc import ABC, abstractmethod


class ILostItemRepository(ABC):
    """失物招领 Redis 数据访问接口"""

    @abstractmethod
    async def set_expiry(self, item_id: int, ttl_seconds: int = 604800) -> None:
        """设置失物招领过期时间（SETEX）

        实现逻辑：
            用 SETEX lost:item:{id} ttl_seconds id 设置自动过期
            默认 7 天（604800 秒），与 domain 模型中 expires_at 一致

        参数：
            item_id: 失物招领条目 ID
            ttl_seconds: 过期时间（秒），默认 7 天

        测试用例：
            - test_set_expiry_success
            - test_set_expiry_custom_ttl
        """
        ...

    @abstractmethod
    async def exists(self, item_id: int) -> bool:
        """检查失物招领条目是否未过期（EXISTS）

        实现逻辑：
            EXISTS lost:item:{id} — Redis 自动删除过期 key，
            返回 0 表示已过期或不存在

        参数：
            item_id: 失物招领条目 ID

        返回值：
            True 还在有效期，False 已过期或不存在

        测试用例：
            - test_exists_active_item
            - test_exists_expired_item
        """
        ...

    @abstractmethod
    async def remove_expiry(self, item_id: int) -> None:
        """手动移除过期标记（DEL）

        实现逻辑：
            DEL lost:item:{id} — 用于标记已找回时清除过期

        参数：
            item_id: 失物招领条目 ID
        """
        ...
