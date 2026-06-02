"""
功能：社团相关路由

实现逻辑：
    1. POST /api/clubs — 创建社团（需登录）
    2. GET /api/clubs — 获取社团列表
    3. GET /api/clubs/{id} — 获取社团详情
"""

from fastapi import APIRouter, Depends, Path, status

from app.business.interfaces import IClubService
from app.models.dto import ClubCreateRequest, ClubDTO, UserDTO
from app.presentation.dependencies import get_club_service, get_current_user

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
