"""
功能：帖子数据访问对象实现（SQLite）

实现逻辑：
    1. 基于 SQLAlchemy 异步会话实现 IPostDAO 接口
    2. insert 使用 session.add + flush 获取自增 ID
    3. 查询使用 select() + joinedload(author) 预加载作者信息
    4. 删除使用软删除（设置 is_active=False）
    5. 列表查询按 created_at 降序排列
    6. 搜索使用 LIKE 匹配 title 和 content

调用链路：
    - 被业务层的 PostServiceImpl 通过 IPostDAO 接口调用
    - 依赖 infrastructure/db.py 提供的 AsyncSession

测试用例：
    - tests/unit/data_access/test_post_dao.py
"""

from typing import List, Optional

from sqlalchemy import select, update, func
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from app.data_access.sqlite_dao.post_dao import IPostDAO
from app.models.domain import Post, Comment


class PostDAOImpl(IPostDAO):
    """帖子数据访问实现"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def insert(self, post: Post) -> int:
        """创建帖子

        实现逻辑：
            1. session.add(post) 将对象加入会话
            2. session.flush() 触发 INSERT，获取自增 ID

        参数：
            post: Post ORM 对象（不含 id）

        返回值：
            新帖子的 id
        """
        self.session.add(post)
        await self.session.flush()
        return post.id

    async def get_by_id(self, post_id: int) -> Optional[Post]:
        """根据 ID 获取帖子（含作者信息）

        实现逻辑：
            1. 使用 joinedload 预加载 author 关系
            2. 查询未软删除的帖子（is_active=True）

        参数：
            post_id: 帖子 ID

        返回值：
            Post ORM 对象或 None
        """
        result = await self.session.execute(
            select(Post)
            .options(joinedload(Post.author))
            .where(Post.id == post_id, Post.is_active.is_(True))
        )
        return result.unique().scalar_one_or_none()

    async def delete(self, post_id: int) -> bool:
        """软删除帖子

        实现逻辑：
            1. 执行 UPDATE posts SET is_active = False WHERE id = :post_id
            2. 返回是否成功删除

        参数：
            post_id: 帖子 ID

        返回值：
            True 如果删除成功，False 如果帖子不存在
        """
        result = await self.session.execute(
            update(Post)
            .where(Post.id == post_id)
            .values(is_active=False)
        )
        return result.rowcount > 0

    async def list_latest(
        self, offset: int = 0, limit: int = 20, tag: Optional[str] = None
    ) -> List[Post]:
        """获取最新帖子列表（支持按标签筛选）

        实现逻辑：
            1. 如果提供了 tag，使用 LIKE %tag% 筛选
            2. 按 created_at 降序排列
            3. 使用 joinedload 预加载作者信息
            4. 只返回未软删除的帖子

        参数：
            offset: 分页偏移量
            limit: 每页数量（默认 20）
            tag: 可选的话题标签筛选

        返回值：
            Post ORM 对象列表
        """
        query = (
            select(Post)
            .options(joinedload(Post.author))
            .where(Post.is_active.is_(True))
            .order_by(Post.created_at.desc())
            .offset(offset)
            .limit(limit)
        )

        if tag:
            query = query.where(Post.tags.like(f"%{tag}%"))

        result = await self.session.execute(query)
        return result.unique().scalars().all()

    async def search(self, keyword: str, offset: int = 0, limit: int = 20) -> List[Post]:
        """全文搜索帖子

        实现逻辑：
            1. 使用 LIKE %keyword% 匹配 title 或 content
            2. 按 created_at 降序排列
            3. 只返回未软删除的帖子

        参数：
            keyword: 搜索关键词
            offset: 分页偏移量
            limit: 每页数量

        返回值：
            匹配的 Post ORM 对象列表
        """
        pattern = f"%{keyword}%"
        result = await self.session.execute(
            select(Post)
            .options(joinedload(Post.author))
            .where(
                Post.is_active.is_(True),
                (
                    Post.title.like(pattern) | Post.content.like(pattern)
                ),
            )
            .order_by(Post.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return result.unique().scalars().all()

    async def increment_view_count(self, post_id: int) -> int:
        """增加帖子浏览量

        UPDATE posts SET view_count = view_count + 1 WHERE id = :post_id
        返回更新后的值
        """
        result = await self.session.execute(
            update(Post)
            .where(Post.id == post_id)
            .values(view_count=Post.view_count + 1)
        )
        if result.rowcount == 0:
            return 0
        # 重新查询获取最新值
        updated = await self.session.execute(
            select(Post.view_count).where(Post.id == post_id)
        )
        return updated.scalar() or 0

    async def count_comments(self, post_id: int) -> int:
        """获取帖子评论数

        SELECT COUNT(*) FROM comments WHERE post_id = :post_id AND is_active = True
        """
        result = await self.session.execute(
            select(func.count())
            .select_from(Comment)
            .where(Comment.post_id == post_id, Comment.is_active.is_(True))
        )
        return result.scalar() or 0
