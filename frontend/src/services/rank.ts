import request from './request'
import type { PostDTO, ClubRank } from '@/types'

/**
 * 获取热帖排行榜
 * GET /api/rank/hot-posts?limit=10&tag=课程
 */
export const getHotRank = (params?: { limit?: number; tag?: string }) => {
    return request.get<never, PostDTO[]>('/rank/hot-posts', { params })
}

/**
 * 获取社团活跃榜
 * GET /api/rank/clubs?limit=10
 */
export const getClubRank = (params?: { limit?: number }) => {
    return request.get<never, ClubRank[]>('/rank/clubs', { params })
}