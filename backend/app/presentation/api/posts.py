"""
功能：帖子相关路由

实现逻辑：
    1. POST /api/posts — 发布帖子（需登录）
    2. GET /api/posts — 获取帖子列表（分页 + 标签筛选）
    3. GET /api/posts/{id} — 获取帖子详情（如果登录，返回点赞状态）
    4. POST /api/posts/{id}/view — 增加浏览量
    5. DELETE /api/posts/{id} — 删除帖子（仅作者）
"""

from typing import Optional

from fastapi import APIRouter, Depends, Path, Query, status

from app.business.interfaces import IPostService
from app.models.dto import PostCreateRequest, PostDTO, PostListResponse
from app.models.dto import UserDTO
from app.presentation.dependencies import (
    get_post_service,
    get_current_user,
    get_current_user_optional,
)

router = APIRouter(prefix="/api/posts", tags=["帖子"])
user_post_router = APIRouter(tags=["帖子"])


@router.post("", response_model=PostDTO, status_code=status.HTTP_201_CREATED)
async def create_post(
    request: PostCreateRequest,
    current_user: UserDTO = Depends(get_current_user),
    post_service: IPostService = Depends(get_post_service),
):
    """发布帖子（需要登录）"""
    return await post_service.create_post(user_id=current_user.id, request=request)


@router.get("", response_model=PostListResponse)
async def list_posts(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    tag: Optional[str] = Query(None, description="按话题标签筛选"),
    post_service: IPostService = Depends(get_post_service),
):
    """获取帖子列表（支持分页和标签筛选）"""
    return await post_service.list_posts(offset=offset, limit=limit, tag=tag)


@router.get("/{post_id}", response_model=PostDTO)
async def get_post(
    post_id: int,
    post_service: IPostService = Depends(get_post_service),
    current_user: Optional[UserDTO] = Depends(get_current_user_optional),
):
    """获取帖子详情（如果已登录，返回真实的点赞状态）"""
    uid = current_user.id if current_user else None
    return await post_service.get_post_by_id(post_id=post_id, current_user_id=uid)


@user_post_router.get("/api/users/me/posts", response_model=PostListResponse)
async def get_my_posts(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: UserDTO = Depends(get_current_user),
    post_service: IPostService = Depends(get_post_service),
):
    """获取当前用户的帖子列表（需要登录）"""
    return await post_service.get_user_posts(
        user_id=current_user.id, offset=offset, limit=limit
    )


@router.post("/{post_id}/view")
async def view_post(
    post_id: int = Path(..., description="帖子 ID"),
    post_service: IPostService = Depends(get_post_service),
):
    """增加帖子浏览量"""
    count = await post_service.increment_view_count(post_id=post_id)
    return {"view_count": count}


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    current_user: UserDTO = Depends(get_current_user),
    post_service: IPostService = Depends(get_post_service),
):
    """删除帖子（仅作者可删除，需要登录）"""
    await post_service.delete_post(post_id=post_id, user_id=current_user.id)
