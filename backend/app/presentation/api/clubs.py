"""社团相关路由"""
from fastapi import APIRouter, Depends, Path, Query, status

from app.business.interfaces import IClubService, IPostService, IEventService
from app.models.dto import ClubCreateRequest, ClubDTO, ClubMemberDTO, UserDTO, PostListResponse
from app.presentation.dependencies import (
    get_club_service, get_post_service, get_event_service,
    get_current_user, get_current_user_optional,
)

router = APIRouter(prefix="/api/clubs", tags=["社团"])


@router.post("", response_model=ClubDTO, status_code=status.HTTP_201_CREATED)
async def create_club(
    request: ClubCreateRequest,
    current_user: UserDTO = Depends(get_current_user),
    club_service: IClubService = Depends(get_club_service),
):
    """创建社团（需要登录）"""
    return await club_service.create_club(request)


@router.get("", response_model=list[ClubDTO])
async def list_clubs(
    club_service: IClubService = Depends(get_club_service),
):
    """获取所有社团"""
    return await club_service.list_clubs()


@router.get("/{club_id}", response_model=ClubDTO)
async def get_club(
    club_id: int = Path(..., description="社团 ID"),
    club_service: IClubService = Depends(get_club_service),
):
    """获取社团详情"""
    result = await club_service.get_club_by_id(club_id)
    if result is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="社团不存在")
    return result


# ========== 社团成员 ==========

@router.post("/{club_id}/members")
async def join_club(
    club_id: int = Path(...),
    current_user: UserDTO = Depends(get_current_user),
    club_service: IClubService = Depends(get_club_service),
):
    """加入社团（需要登录）"""
    await club_service.join_club(user_id=current_user.id, club_id=club_id)
    return {"success": True, "message": "已加入社团"}


@router.delete("/{club_id}/members")
async def leave_club(
    club_id: int = Path(...),
    current_user: UserDTO = Depends(get_current_user),
    club_service: IClubService = Depends(get_club_service),
):
    """退出社团（需要登录）"""
    result = await club_service.leave_club(user_id=current_user.id, club_id=club_id)
    if not result:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="未加入该社团")
    return {"success": True, "message": "已退出社团"}


@router.get("/{club_id}/members", response_model=list[ClubMemberDTO])
async def get_club_members(
    club_id: int = Path(...),
    club_service: IClubService = Depends(get_club_service),
):
    """获取社团成员列表"""
    return await club_service.get_members(club_id)


@router.get("/{club_id}/members/me")
async def check_membership(
    club_id: int = Path(...),
    current_user: UserDTO = Depends(get_current_user),
    club_service: IClubService = Depends(get_club_service),
):
    """检查当前用户是否已加入社团"""
    is_member = await club_service.is_member(user_id=current_user.id, club_id=club_id)
    return {"is_member": is_member}


# ========== 社团帖子 ==========

@router.get("/{club_id}/posts", response_model=PostListResponse)
async def get_club_posts(
    club_id: int = Path(...),
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    post_service: IPostService = Depends(get_post_service),
):
    """获取社团的帖子列表"""
    return await post_service.list_posts(offset=offset, limit=limit, club_id=club_id)


# ========== 社团活动 ==========

@router.get("/{club_id}/events")
async def get_club_events(
    club_id: int = Path(...),
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    event_service: IEventService = Depends(get_event_service),
):
    """获取社团的活动列表"""
    from app.models.dto import EventDTO
    events = await event_service.list_events(offset=offset, limit=limit, club_id=club_id)
    return events
