"""
功能：点赞相关路由

实现逻辑：
    1. POST /api/posts/{id}/like — 点赞帖子（需登录）
    2. DELETE /api/posts/{id}/like — 取消点赞（需登录）

调用链路：
    - 调用 ILikeService 接口（通过依赖注入）
    - 依赖 Redis 存储点赞数据
    - 认证依赖：get_current_user（JWT Bearer Token）
"""

from fastapi import APIRouter, Depends, Path

from app.business.interfaces import ILikeService
from app.models.dto import LikeResultDTO, UserDTO
from app.presentation.dependencies import get_like_service, get_current_user

router = APIRouter(prefix="/api/posts", tags=["点赞"])


@router.post("/{post_id}/like", response_model=LikeResultDTO)
async def like_post(
    post_id: int = Path(..., description="帖子 ID"),
    current_user: UserDTO = Depends(get_current_user),
    like_service: ILikeService = Depends(get_like_service),
):
    """点赞帖子（需要登录）"""
    return await like_service.like_post(user_id=current_user.id, post_id=post_id)


@router.delete("/{post_id}/like", response_model=LikeResultDTO)
async def unlike_post(
    post_id: int = Path(..., description="帖子 ID"),
    current_user: UserDTO = Depends(get_current_user),
    like_service: ILikeService = Depends(get_like_service),
):
    """取消点赞（需要登录）"""
    return await like_service.unlike_post(user_id=current_user.id, post_id=post_id)
