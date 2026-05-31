"""
功能：评论相关路由

实现逻辑：
    1. POST /api/posts/{post_id}/comments — 发表评论（需登录）
    2. GET /api/posts/{post_id}/comments — 获取评论列表
    3. DELETE /api/comments/{comment_id} — 删除评论（仅作者）

调用链路：
    - 调用 ICommentService 接口
    - 认证依赖：get_current_user
"""

from fastapi import APIRouter, Depends, Query, Path, status, Body

from app.business.interfaces import ICommentService
from app.models.dto import CommentCreateRequest, CommentDTO, CommentListResponse, UserDTO
from app.presentation.dependencies import get_comment_service, get_current_user

router = APIRouter(tags=["评论"])


@router.post(
    "/api/posts/{post_id}/comments",
    response_model=CommentDTO,
    status_code=status.HTTP_201_CREATED,
)
async def create_comment(
    post_id: int = Path(..., description="帖子 ID"),
    request: CommentCreateRequest = Body(...),
    current_user: UserDTO = Depends(get_current_user),
    comment_service: ICommentService = Depends(get_comment_service),
):
    """发表评论（需要登录）"""
    return await comment_service.create_comment(
        post_id=post_id, user_id=current_user.id, request=request,
    )


@router.get("/api/posts/{post_id}/comments", response_model=CommentListResponse)
async def list_comments(
    post_id: int = Path(..., description="帖子 ID"),
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    comment_service: ICommentService = Depends(get_comment_service),
):
    """获取帖子的评论列表"""
    return await comment_service.get_comments(
        post_id=post_id, offset=offset, limit=limit,
    )


@router.delete("/api/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int = Path(..., description="评论 ID"),
    current_user: UserDTO = Depends(get_current_user),
    comment_service: ICommentService = Depends(get_comment_service),
):
    """删除评论（仅作者，需要登录）"""
    await comment_service.delete_comment(
        comment_id=comment_id, user_id=current_user.id,
    )
