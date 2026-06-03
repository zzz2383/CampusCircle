"""评论数据访问实现（SQLite）"""
from typing import List, Optional
from sqlalchemy import select, update
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from app.data_access.sqlite_dao.comment_dao import ICommentDAO
from app.models.domain import Comment


class CommentDAOImpl(ICommentDAO):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def insert(self, comment: Comment) -> int:
        self.session.add(comment)
        await self.session.flush()
        return comment.id

    async def get_by_id(self, comment_id: int) -> Optional[Comment]:
        result = await self.session.execute(
            select(Comment).options(joinedload(Comment.author))
            .where(Comment.id == comment_id, Comment.is_active.is_(True))
        )
        return result.unique().scalar_one_or_none()

    async def list_by_post(self, post_id: int, offset: int = 0, limit: int = 20,
                           parent_id: Optional[int] = None) -> List[Comment]:
        query = (select(Comment).options(joinedload(Comment.author))
                 .where(Comment.post_id == post_id, Comment.is_active.is_(True))
                 .order_by(Comment.created_at.asc()).offset(offset).limit(limit))
        if parent_id is not None:
            query = query.where(Comment.parent_id == parent_id)
        result = await self.session.execute(query)
        return result.unique().scalars().all()

    async def delete(self, comment_id: int) -> bool:
        result = await self.session.execute(
            update(Comment).where(Comment.id == comment_id).values(is_active=False))
        return result.rowcount > 0

    async def list_all(self, offset: int = 0, limit: int = 20) -> List[Comment]:
        result = await self.session.execute(
            select(Comment).options(joinedload(Comment.author))
            .order_by(Comment.created_at.desc()).offset(offset).limit(limit))
        return result.unique().scalars().all()
