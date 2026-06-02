"""失物招领相关路由"""
from fastapi import APIRouter, Depends, Path, Query, status
from app.business.interfaces import ILostItemService
from app.models.dto import LostItemCreateRequest, LostItemDTO, UserDTO
from app.presentation.dependencies import get_lost_item_service, get_current_user

router = APIRouter(prefix="/api/lost-items", tags=["失物招领"])


@router.post("", response_model=LostItemDTO, status_code=status.HTTP_201_CREATED)
async def create_lost_item(
    request: LostItemCreateRequest,
    current_user: UserDTO = Depends(get_current_user),
    lost_item_service: ILostItemService = Depends(get_lost_item_service),
):
    """发布失物/拾物信息（需要登录）"""
    return await lost_item_service.create_item(
        user_id=current_user.id, request=request
    )


@router.get("", response_model=list[LostItemDTO])
async def list_lost_items(
    is_lost: bool | None = Query(None, description="True=丢失, False=拾到, None=全部"),
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    lost_item_service: ILostItemService = Depends(get_lost_item_service),
):
    """获取失物招领列表（不需要登录）"""
    return await lost_item_service.list_items(
        is_lost=is_lost, offset=offset, limit=limit
    )


@router.get("/{item_id}", response_model=LostItemDTO)
async def get_lost_item(
    item_id: int = Path(...),
    lost_item_service: ILostItemService = Depends(get_lost_item_service),
):
    """获取失物招领详情（不需要登录）"""
    result = await lost_item_service.get_item_by_id(item_id)
    if result is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="物品不存在或已过期")
    return result


@router.post("/{item_id}/found", response_model=dict)
async def mark_as_found(
    item_id: int = Path(...),
    current_user: UserDTO = Depends(get_current_user),
    lost_item_service: ILostItemService = Depends(get_lost_item_service),
):
    """标记失物已找回（需要登录，仅发布者可操作）"""
    result = await lost_item_service.mark_as_found(
        item_id=item_id, user_id=current_user.id
    )
    if not result:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="物品不存在")
    return {"success": True, "message": "已标记为已找回"}
