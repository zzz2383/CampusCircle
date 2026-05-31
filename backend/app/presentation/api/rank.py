"""
功能：排行榜相关路由

实现逻辑：
    1. GET /api/rank/hot-posts — 热帖排行榜（支持按标签筛选）
    2. GET /api/rank/clubs — 社团活跃榜

调用链路：
    - 调用 IRankService 接口（通过依赖注入）
    - 数据来源：Redis Sorted Set（热度分）+ SQLite（详情）
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.business.interfaces import IRankService
from app.models.dto import PostDTO, ClubRankDTO
from app.presentation.dependencies import get_rank_service

router = APIRouter(prefix="/api/rank", tags=["排行榜"])


@router.get("/hot-posts")
async def get_hot_posts(
    limit: int = Query(10, ge=1, le=50, description="返回数量"),
    tag: Optional[str] = Query(None, description="话题标签筛选"),
    rank_service: IRankService = Depends(get_rank_service),
):
    """获取热帖排行榜（按热度分降序，支持按标签筛选）"""
    return await rank_service.get_hot_posts(limit=limit, tag=tag)


@router.get("/clubs")
async def get_club_rank(
    limit: int = Query(10, ge=1, le=50, description="返回数量"),
    rank_service: IRankService = Depends(get_rank_service),
):
    """获取社团活跃榜"""
    return await rank_service.get_club_rank(limit=limit)
