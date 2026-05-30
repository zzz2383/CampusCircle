"""
功能：点赞相关路由

实现逻辑：
    1. POST /api/posts/{id}/like — 点赞帖子
    2. DELETE /api/posts/{id}/like — 取消点赞

调用链路：
    - 调用 ILikeService 接口
"""

from fastapi import APIRouter, Depends, Path

from app.business.interfaces import ILikeService
from app.models.dto import LikeResultDTO

router = APIRouter(prefix="/api/posts", tags=["点赞"])


@router.post("/{post_id}/like", response_model=LikeResultDTO)
async def like_post(
    post_id: int = Path(..., description="帖子 ID"),
    current_user=Depends(),
    like_service: ILikeService = Depends(),
):
    """点赞帖子"""
    return await like_service.like_post(user_id=current_user.id, post_id=post_id)


@router.delete("/{post_id}/like", response_model=LikeResultDTO)
async def unlike_post(
    post_id: int = Path(..., description="帖子 ID"),
    current_user=Depends(),
    like_service: ILikeService = Depends(),
):
    """取消点赞"""
    return await like_service.unlike_post(user_id=current_user.id, post_id=post_id)
