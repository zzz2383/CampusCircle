"""
功能：用户数据访问对象接口

实现逻辑：
    定义用户相关的 SQLite 数据库操作抽象接口

调用链路：
    - 被 business 层的 UserService 调用
    - 由 sqlite_dao 目录下的具体实现类实现
"""

from abc import ABC, abstractmethod
from typing import Optional, List

from app.models.domain import User


class IUserDAO(ABC):
    """用户数据访问接口"""

    @abstractmethod
    async def insert(self, user: User) -> int:
        """创建用户

        参数：
            user: User ORM 对象（不含 id）

        返回值：
            新用户的 id

        异常：
            无（数据库约束异常由上层处理）
        """
        ...

    @abstractmethod
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """根据 ID 获取用户

        参数：
            user_id: 用户 ID

        返回值：
            User ORM 对象或 None
        """
        ...

    @abstractmethod
    async def get_by_student_id(self, student_id: str) -> Optional[User]:
        """根据学号获取用户

        参数：
            student_id: 学号/工号

        返回值：
            User ORM 对象或 None
        """
        ...

    @abstractmethod
    async def update_online_status(self, user_id: int, is_online: bool) -> None:
        """更新用户在线状态

        参数：
            user_id: 用户 ID
            is_online: 是否在线
        """
        ...
