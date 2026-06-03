"""活动相关路由"""
from typing import Optional
from fastapi import APIRouter, Depends, Path, Query, status
from app.business.interfaces import IEventService
from app.models.dto import EventCreateRequest, EventDTO, UserDTO
from app.presentation.dependencies import get_event_service, get_current_user

router = APIRouter(prefix="/api/events", tags=["活动"])


@router.post("", response_model=EventDTO, status_code=status.HTTP_201_CREATED)
async def create_event(
    request: EventCreateRequest,
    current_user: UserDTO = Depends(get_current_user),
    event_service: IEventService = Depends(get_event_service),
):
    return await event_service.create_event(request)


@router.get("", response_model=list[EventDTO])
async def list_events(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    club_id: Optional[int] = Query(None, description="按社团筛选"),
    event_service: IEventService = Depends(get_event_service),
):
    return await event_service.list_events(offset=offset, limit=limit, club_id=club_id)


@router.get("/{event_id}", response_model=EventDTO)
async def get_event(
    event_id: int = Path(...),
    event_service: IEventService = Depends(get_event_service),
):
    result = await event_service.get_event_by_id(event_id)
    if result is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="活动不存在")
    return result
