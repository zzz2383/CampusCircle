"""
功能：异步数据库引擎与会话管理（支持 MySQL 和 SQLite）

实现逻辑：
    1. 基于 SQLAlchemy 异步引擎创建数据库连接
    2. 自动识别 SQLite（aiosqlite）和 MySQL（aiomysql）驱动，设置对应参数
    3. 使用 async_session_factory 创建异步会话
    4. get_db() 作为 FastAPI 依赖注入的上下文管理器

调用链路：
    - 被 data_access 层获取数据库会话
    - 被 main.py 中的 lifespan 事件调用初始化/关闭

参数说明：
    settings.DATABASE_URL: 数据库异步连接字符串（支持 mysql+aiomysql 或 sqlite+aiosqlite）

返回值：
    get_db(): AsyncGenerator[AsyncSession, None]
"""

from typing import AsyncGenerator

from sqlalchemy import make_url, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.infrastructure.config import settings
from app.infrastructure.logger import get_logger

logger = get_logger(__name__)


def _create_engine():
    """根据 DATABASE_URL 自动选择驱动并创建引擎

    实现逻辑：
        1. 使用 make_url 解析连接字符串，避免字符串硬编码替换
        2. 若为 SQLite（+aiosqlite），设置 check_same_thread=False
        3. 若为 MySQL（+aiomysql），配置连接池参数
    """
    url = make_url(settings.DATABASE_URL)
    connect_args = {}

    if "aiosqlite" in url.drivername:
        connect_args["check_same_thread"] = False
        return create_async_engine(
            settings.DATABASE_URL,
            echo=settings.DEBUG,
            connect_args=connect_args,
        )
    else:
        return create_async_engine(
            settings.DATABASE_URL,
            echo=settings.DEBUG,
            pool_size=settings.MYSQL_POOL_SIZE,
            max_overflow=settings.MYSQL_MAX_OVERFLOW,
            pool_recycle=settings.MYSQL_POOL_RECYCLE,
            pool_pre_ping=True,
            connect_args=connect_args,
        )


# 异步引擎
async_engine = _create_engine()

# 会话工厂
async_session_factory = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI 依赖注入：获取数据库会话

    实现逻辑：
        1. 从 async_session_factory 创建新会话
        2. 请求完成后自动关闭会话

    调用链路：
        - 被 FastAPI 路由的 Depends() 使用
        - 被 DAO 层通过参数注入使用

    测试用例：
        - test_get_db_success
    """
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


async def ensure_database_exists():
    """确保 MySQL 数据库已存在，若不存在则自动创建

    实现逻辑：
        1. 解析 DATABASE_URL 提取数据库名
        2. 连接 MySQL（不指定具体数据库，连接 mysql 系统库）
        3. 执行 CREATE DATABASE IF NOT EXISTS
        4. 仅对 MySQL 生效，SQLite 跳过

    调用链路：
        - 被 init_db() 在创建引擎连接前调用
    """
    url = make_url(settings.DATABASE_URL)

    # 仅对 MySQL 生效
    if "aiomysql" not in url.drivername:
        return

    db_name = url.database
    # 构建不含数据库名的 URL，连接 mysql 系统库
    admin_url = (
        f"{url.drivername}://{url.username}:{url.password}"
        f"@{url.host}:{url.port or 3306}/mysql?charset=utf8mb4"
    )

    try:
        engine = create_async_engine(admin_url, echo=False)
        async with engine.connect() as conn:
            await conn.execute(
                text(
                    f"CREATE DATABASE IF NOT EXISTS `{db_name}` "
                    f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
                )
            )
            await conn.commit()
        await engine.dispose()
        logger.info(f"MySQL database '{db_name}' ensured")
    except Exception as e:
        logger.warning(f"Could not auto-create database '{db_name}': {e}")


async def init_db():
    """初始化数据库：创建所有表并插入种子数据

    实现逻辑：
        1. 若为 MySQL，先确保数据库已存在（自动建库）
        2. 导入所有 ORM 模型以确保它们被 Base 元数据注册
        3. 调用 Base.metadata.create_all() 创建表
        4. 调用 seed_default_admin() 插入默认管理员账号
        5. 调用 seed_demo_data() 插入演示数据（用户/社团/帖子等）

    调用链路：
        - 被 main.py lifespan 事件调用
    """
    await ensure_database_exists()

    from app.models.domain import Base

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created successfully")

    await seed_default_admin()

    from app.infrastructure.seed_data import seed_demo_data

    await seed_demo_data()


async def seed_default_admin():
    """种子数据：插入默认管理员账号

    实现逻辑：
        1. 检查是否已存在学号为 123456 的管理员
        2. 若不存在，创建一个 admin 角色用户（学号 123456，密码 123456）
        3. 若已存在，跳过不做任何操作

    测试用例：
        - test_seed_default_admin_created (见 tests/test_smoke.py)
        - test_seed_default_admin_idempotent
    """
    from sqlalchemy import select
    from app.models.domain import User
    from app.models.enums import UserRole
    from app.business.impl.auth_utils import hash_password

    async with async_session_factory() as session:
        try:
            # 1. 检查是否已存在
            result = await session.execute(
                select(User).where(User.student_id == "123456")
            )
            existing = result.scalar_one_or_none()
            if existing:
                logger.info("Default admin already exists, skipping seed")
                return

            # 2. 创建默认管理员
            admin = User(
                student_id="123456",
                email="admin@campus.edu",
                nickname="系统管理员",
                password_hash=hash_password("123456"),
                role=UserRole.ADMIN,
                is_active=True,
            )
            session.add(admin)
            await session.commit()
            logger.info("Default admin created: student_id=123456, password=123456")
        except Exception as e:
            await session.rollback()
            logger.error(f"Failed to seed default admin: {e}")
            raise
        finally:
            await session.close()


async def close_db():
    """关闭数据库引擎"""
    await async_engine.dispose()
    logger.info("Database engine disposed")
