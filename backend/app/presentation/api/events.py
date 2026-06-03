"""活动相关路由"""
from typing import Optional
from fastapi import APIRouter, Depends, Path, Query, status
from app.business.interfaces import IEventService
from app.models.dto import EventCreateRequest, EventUpdateRequest, EventDTO, EventParticipantDTO, UserDTO
from app.presentation.dependencies import (
    get_event_service, get_current_user, get_current_user_optional,
)

router = APIRouter(prefix="/api/events", tags=["活动"])


@router.post("", response_model=EventDTO, status_code=status.HTTP_201_CREATED)
async def create_event(
    request: EventCreateRequest,
    current_user: UserDTO = Depends(get_current_user),
    event_service: IEventService = Depends(get_event_service),
):
    """创建活动（需要登录）"""
    return await event_service.create_event(request)


@router.get("", response_model=list[EventDTO])
async def list_events(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    club_id: Optional[int] = Query(None, description="按社团筛选"),
    current_user: Optional[UserDTO] = Depends(get_current_user_optional),
    event_service: IEventService = Depends(get_event_service),
):
    """活动列表（如果登录，返回报名状态）"""
    uid = current_user.id if current_user else None
    return await event_service.list_events(
        offset=offset, limit=limit, club_id=club_id, current_user_id=uid)


@router.get("/{event_id}", response_model=EventDTO)
async def get_event(
    event_id: int = Path(...),
    current_user: Optional[UserDTO] = Depends(get_current_user_optional),
    event_service: IEventService = Depends(get_event_service),
):
    """活动详情（如果登录，返回报名状态）"""
    uid = current_user.id if current_user else None
    result = await event_service.get_event_by_id(event_id, current_user_id=uid)
    if result is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="活动不存在")
    return result


@router.put("/{event_id}", response_model=EventDTO)
async def update_event(
    event_id: int = Path(...),
    request: EventUpdateRequest = ...,
    current_user: UserDTO = Depends(get_current_user),
    event_service: IEventService = Depends(get_event_service),
):
    """编辑活动（需要登录）"""
    result = await event_service.update_event(event_id, request)
    if result is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="活动不存在")
    return result


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(
    event_id: int = Path(...),
    current_user: UserDTO = Depends(get_current_user),
    event_service: IEventService = Depends(get_event_service),
):
    """删除活动（需要登录）"""
    result = await event_service.delete_event(event_id)
    if not result:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="活动不存在")


# ========== 报名相关 ==========

@router.post("/{event_id}/register")
async def register_event(
    event_id: int = Path(...),
    current_user: UserDTO = Depends(get_current_user),
    event_service: IEventService = Depends(get_event_service),
):
    """报名活动（需要登录）"""
    await event_service.register_event(user_id=current_user.id, event_id=event_id)
    return {"success": True, "message": "报名成功"}


@router.delete("/{event_id}/register")
async def cancel_registration(
    event_id: int = Path(...),
    current_user: UserDTO = Depends(get_current_user),
    event_service: IEventService = Depends(get_event_service),
):
    """取消报名（需要登录）"""
    await event_service.cancel_registration(user_id=current_user.id, event_id=event_id)
    return {"success": True, "message": "已取消报名"}


@router.get("/{event_id}/participants", response_model=list[EventParticipantDTO])
async def get_participants(
    event_id: int = Path(...),
    event_service: IEventService = Depends(get_event_service),
):
    """获取活动参与成员列表"""
    return await event_service.get_participants(event_id)


@router.get("/{event_id}/participant-count")
async def get_participant_count(
    event_id: int = Path(...),
    event_service: IEventService = Depends(get_event_service),
):
    """获取活动实时报名人数"""
    count = await event_service.get_participant_count(event_id)
    return {"participant_count": count}
