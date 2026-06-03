"""黑名单 Redis Repository 接口

Key 命名规范：
    blacklist:user:{user_id} — 被封禁用户，value=封禁时间戳，TTL=封禁时长
"""
from abc import ABC, abstractmethod


class IBlacklistRepo(ABC):
    @abstractmethod
    async def ban(self, user_id: int, duration_hours: int = 24) -> None: ...
    @abstractmethod
    async def unban(self, user_id: int) -> None: ...
    @abstractmethod
    async def is_banned(self, user_id: int) -> bool: ...
    @abstractmethod
    async def list_banned(self) -> list[dict]: ...
