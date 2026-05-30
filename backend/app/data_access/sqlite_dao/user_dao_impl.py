"""
功能：用户数据访问对象实现（SQLite）

实现逻辑：
    1. 基于 SQLAlchemy 异步会话实现 IUserDAO 接口
    2. insert 使用 session.add + flush 获取自增 ID
    3. 查询使用 select() 语句 + scalar_one_or_none
    4. 更新使用 update() 语句

调用链路：
    - 被业务层的 UserServiceImpl 通过 IUserDAO 接口调用
    - 依赖 infrastructure/db.py 提供的 AsyncSession

参数说明：
    session: 通过构造函数注入的 AsyncSession 实例

测试用例：
    - tests/unit/data_access/test_user_dao.py
"""

from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.data_access.sqlite_dao.user_dao import IUserDAO
from app.models.domain import User


class UserDAOImpl(IUserDAO):
    """用户数据访问实现"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def insert(self, user: User) -> int:
        """创建用户

        实现逻辑：
            1. session.add(user) 将对象加入会话
            2. session.flush() 触发 INSERT，获取自增 ID
            3. 不 commit，由上层 Service 控制事务

        参数：
            user: User ORM 对象（不含 id）

        返回值：
            新用户的 id
        """
        self.session.add(user)
        await self.session.flush()
        return user.id

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """根据 ID 获取用户

        实现逻辑：
            1. 执行 SELECT * FROM users WHERE id = :user_id
            2. scalar_one_or_none 返回 User 或 None

        参数：
            user_id: 用户 ID

        返回值：
            User ORM 对象或 None
        """
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_student_id(self, student_id: str) -> Optional[User]:
        """根据学号获取用户

        实现逻辑：
            1. 执行 SELECT * FROM users WHERE student_id = :student_id

        参数：
            student_id: 学号/工号

        返回值：
            User ORM 对象或 None
        """
        result = await self.session.execute(
            select(User).where(User.student_id == student_id)
        )
        return result.scalar_one_or_none()

    async def update_online_status(self, user_id: int, is_online: bool) -> None:
        """更新用户在线状态

        实现逻辑：
            1. 执行 UPDATE users SET is_online = :is_online WHERE id = :user_id

        参数：
            user_id: 用户 ID
            is_online: 是否在线
        """
        await self.session.execute(
            update(User)
            .where(User.id == user_id)
            .values(is_online=is_online)
        )
