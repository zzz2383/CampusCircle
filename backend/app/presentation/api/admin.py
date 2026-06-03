"""管理后台路由（所有端点需 admin 权限）"""
from fastapi import APIRouter, Depends, Path, Query, status, Body

from app.business.interfaces import IAdminService
from app.models.dto import UserDTO
from app.presentation.dependencies import (
    get_admin_service, get_current_admin_user,
)

router = APIRouter(prefix="/api/admin", tags=["管理后台"])


# ========== 内容管理 ==========

@router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_post(
    post_id: int = Path(...),
    _admin: UserDTO = Depends(get_current_admin_user),
    admin_service: IAdminService = Depends(get_admin_service),
):
    await admin_service.delete_post(post_id)


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_comment(
    comment_id: int = Path(...),
    _admin: UserDTO = Depends(get_current_admin_user),
    admin_service: IAdminService = Depends(get_admin_service),
):
    await admin_service.delete_comment(comment_id)


@router.delete("/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_event(
    event_id: int = Path(...),
    _admin: UserDTO = Depends(get_current_admin_user),
    admin_service: IAdminService = Depends(get_admin_service),
):
    await admin_service.delete_event(event_id)


@router.delete("/lost-items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_lost_item(
    item_id: int = Path(...),
    _admin: UserDTO = Depends(get_current_admin_user),
    admin_service: IAdminService = Depends(get_admin_service),
):
    await admin_service.delete_lost_item(item_id)


@router.delete("/clubs/{club_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_club(
    club_id: int = Path(...),
    _admin: UserDTO = Depends(get_current_admin_user),
    admin_service: IAdminService = Depends(get_admin_service),
):
    await admin_service.delete_club(club_id)


@router.get("/comments")
async def admin_list_comments(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    _admin: UserDTO = Depends(get_current_admin_user),
    admin_service: IAdminService = Depends(get_admin_service),
):
    """获取所有评论列表（管理员）"""
    return await admin_service.list_all_comments(offset=offset, limit=limit)


# ========== 用户管理 ==========

@router.get("/users")
async def admin_list_users(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    keyword: str | None = Query(None, description="搜索昵称或学号"),
    _admin: UserDTO = Depends(get_current_admin_user),
    admin_service: IAdminService = Depends(get_admin_service),
):
    return await admin_service.list_users(offset=offset, limit=limit, keyword=keyword)


@router.get("/users/banned")
async def admin_list_banned(
    _admin: UserDTO = Depends(get_current_admin_user),
    admin_service: IAdminService = Depends(get_admin_service),
):
    return await admin_service.list_banned()


@router.get("/users/{user_id}", response_model=UserDTO)
async def admin_get_user(
    user_id: int = Path(...),
    _admin: UserDTO = Depends(get_current_admin_user),
    admin_service: IAdminService = Depends(get_admin_service),
):
    result = await admin_service.get_user(user_id)
    if result is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="用户不存在")
    return result


@router.put("/users/{user_id}/role", response_model=UserDTO)
async def admin_set_role(
    user_id: int = Path(...),
    role: str = Body(..., embed=True, description="角色: student/teacher/admin"),
    _admin: UserDTO = Depends(get_current_admin_user),
    admin_service: IAdminService = Depends(get_admin_service),
):
    result = await admin_service.set_role(user_id, role, current_user_id=_admin.id)
    if result is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="用户不存在")
    return result


@router.post("/users/{user_id}/ban")
async def admin_ban_user(
    user_id: int = Path(...),
    duration_hours: int = Body(24, embed=True, description="封禁时长（小时）"),
    _admin: UserDTO = Depends(get_current_admin_user),
    admin_service: IAdminService = Depends(get_admin_service),
):
    await admin_service.ban_user(user_id, duration_hours)
    return {"success": True, "message": f"用户已封禁（{duration_hours}小时）"}


@router.post("/users/{user_id}/unban")
async def admin_unban_user(
    user_id: int = Path(...),
    _admin: UserDTO = Depends(get_current_admin_user),
    admin_service: IAdminService = Depends(get_admin_service),
):
    await admin_service.unban_user(user_id)
    return {"success": True, "message": "用户已解封"}


# ========== 数据统计 ==========

@router.get("/stats")
async def admin_get_stats(
    _admin: UserDTO = Depends(get_current_admin_user),
    admin_service: IAdminService = Depends(get_admin_service),
):
    return await admin_service.get_stats()