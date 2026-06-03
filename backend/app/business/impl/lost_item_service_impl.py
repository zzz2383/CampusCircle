"""失物招领业务逻辑实现"""
from datetime import datetime, timezone, timedelta
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.business.interfaces.lost_item_service import ILostItemService
from app.data_access.sqlite_dao.lost_item_dao import ILostItemDAO
from app.data_access.sqlite_dao.user_dao import IUserDAO
from app.data_access.sqlite_dao.user_dao_impl import UserDAOImpl
from app.data_access.redis_repo.lost_item_repo import ILostItemRepository
from app.infrastructure.exceptions import AppException
from app.infrastructure.logger import get_logger
from app.models.domain import LostItem
from app.models.dto import LostItemCreateRequest, LostItemDTO

logger = get_logger(__name__)

LOST_ITEM_TTL_SECONDS = 604800  # 7 天


class LostItemServiceImpl(ILostItemService):
    """失物招领服务实现

    实现逻辑：
        1. 创建失物招领时，写入 SQLite 持久化 + Redis SETEX 自动过期
        2. 查询列表时仅返回未过期的条目（Redis EXISTS 过滤）
        3. 标记已找回时更新 SQLite + 清除 Redis 过期标记
    """

    def __init__(
        self,
        lost_item_dao: ILostItemDAO,
        lost_item_repo: ILostItemRepository,
        db_session: AsyncSession,
        user_dao: Optional[IUserDAO] = None,
    ):
        self.dao = lost_item_dao
        self.repo = lost_item_repo
        self.db_session = db_session
        self.user_dao = user_dao or UserDAOImpl(db_session)

    async def create_item(self, user_id: int, request: LostItemCreateRequest) -> LostItemDTO:
        """发布失物/拾物信息

        实现逻辑：
            1. 构建 LostItem ORM 对象（设置 expires_at = now + 7 天）
            2. 调用 DAO.insert() 写入 SQLite
            3. 调用 Redis Repository.set_expiry() 设置 7 天自动过期
            4. 提交数据库事务
            5. 返回 LostItemDTO

        参数：
            user_id: 发布者 ID
            request: 失物招领创建请求

        返回值：
            LostItemDTO

        异常：
            - 无（数据库写入失败由基础设施层处理）

        测试用例：
            - test_create_item_success
        """
        now = datetime.now(timezone.utc)
        item = LostItem(
            user_id=user_id,
            title=request.title,
            description=request.description,
            image_url=request.image_url,
            location=request.location,
            contact=request.contact,
            is_lost=request.is_lost,
            is_found=False,
            expires_at=now + timedelta(seconds=LOST_ITEM_TTL_SECONDS),
        )
        item_id = await self.dao.insert(item)
        await self.repo.set_expiry(item_id, LOST_ITEM_TTL_SECONDS)
        await self.db_session.commit()
        logger.info(f"LostItem created: id={item_id}, title={request.title}")

        created = await self.dao.get_by_id(item_id)
        return await self._to_dto(created)

    async def get_item_by_id(self, item_id: int) -> Optional[LostItemDTO]:
        """根据 ID 获取失物招领详情

        实现逻辑：
            1. 调用 DAO.get_by_id() 查询 SQLite
            2. 检查 Redis EXISTS 验证是否未过期
            3. 若已过期或不存在返回 None
            4. 返回 LostItemDTO

        参数：
            item_id: 失物招领条目 ID

        返回值：
            Optional[LostItemDTO]
        """
        item = await self.dao.get_by_id(item_id)
        if item is None:
            return None
        if not await self.repo.exists(item_id):
            return None
        return await self._to_dto(item)

    async def list_items(
        self, is_lost: Optional[bool] = None, offset: int = 0, limit: int = 20
    ) -> List[LostItemDTO]:
        """获取失物招领列表

        实现逻辑：
            1. 调用 DAO.list_items() 从 SQLite 分页查询
            2. 对每个条目检查 Redis EXISTS 过滤已过期的
            3. 返回有效的 LostItemDTO 列表

        参数：
            is_lost: 可选，True=丢失, False=拾到, None=全部
            offset: 分页偏移
            limit: 每页数量

        返回值：
            List[LostItemDTO]
        """
        items = await self.dao.list_items(
            is_lost=is_lost, offset=offset, limit=limit
        )
        result = []
        for item in items:
            if await self.repo.exists(item.id):
                result.append(await self._to_dto(item))
        return result

    async def mark_as_found(self, item_id: int, user_id: int) -> bool:
        """标记失物已找回

        实现逻辑：
            1. 查询条目是否存在（调用 DAO.get_by_id()）
            2. 验证当前用户是否为发布者
            3. 更新 is_found = True
            4. 清除 Redis 过期标记
            5. 提交事务

        参数：
            item_id: 失物招领条目 ID
            user_id: 当前用户 ID

        返回值：
            bool 是否成功

        异常：
            - AppException 404: 条目不存在
            - AppException 403: 无权操作（非发布者）

        测试用例：
            - test_mark_as_found_success
            - test_mark_as_found_not_owner
            - test_mark_as_found_not_found
        """
        item = await self.dao.get_by_id(item_id)
        if item is None:
            return False
        if item.user_id != user_id:
            raise AppException(
                status_code=403,
                code="FORBIDDEN",
                message="只有发布者才能标记为已找回",
            )
        result = await self.dao.mark_as_found(item_id)
        if result:
            await self.repo.remove_expiry(item_id)
            await self.db_session.commit()
            return True
        return False

    async def _to_dto(self, item: LostItem) -> LostItemDTO:
        """内部：将 LostItem ORM 转为 DTO"""
        author_nickname = None
        if item.user_id:
            user = await self.user_dao.get_by_id(item.user_id)
            if user:
                author_nickname = user.nickname
        return LostItemDTO(
            id=item.id,
            user_id=item.user_id,
            title=item.title,
            description=item.description,
            image_url=item.image_url,
            location=item.location,
            contact=item.contact,
            is_found=item.is_found,
            is_lost=item.is_lost,
            expires_at=item.expires_at,
            created_at=item.created_at,
            author_nickname=author_nickname,
        )
