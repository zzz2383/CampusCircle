"""
功能：帖子相关路由

实现逻辑：
    1. POST /api/posts — 发布帖子
    2. GET /api/posts — 获取帖子列表（分页 + 标签筛选）
    3. GET /api/posts/{id} — 获取帖子详情
    4. DELETE /api/posts/{id} — 删除帖子

调用链路：
    - 调用 IPostService 接口
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.business.interfaces import IPostService
from app.models.dto import PostCreateRequest, PostUpdateRequest, PostDTO, PostListResponse

router = APIRouter(prefix="/api/posts", tags=["帖子"])


@router.post("", response_model=PostDTO, status_code=201)
async def create_post(
    request: PostCreateRequest,
    current_user=Depends(),
    post_service: IPostService = Depends(),
):
    """发布帖子"""
    return await post_service.create_post(user_id=current_user.id, request=request)


@router.get("", response_model=PostListResponse)
async def list_posts(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    tag: Optional[str] = Query(None),
    post_service: IPostService = Depends(),
):
    """获取帖子列表"""
    return await post_service.list_posts(offset=offset, limit=limit, tag=tag)


@router.get("/{post_id}", response_model=PostDTO)
async def get_post(
    post_id: int,
    post_service: IPostService = Depends(),
):
    """获取帖子详情"""
    return await post_service.get_post_by_id(post_id=post_id)


@router.delete("/{post_id}", status_code=204)
async def delete_post(
    post_id: int,
    current_user=Depends(),
    post_service: IPostService = Depends(),
):
    """删除帖子"""
    await post_service.delete_post(post_id=post_id, user_id=current_user.id)
