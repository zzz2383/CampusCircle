import request from './request'
import type { LostItem, CreateLostItemPayload } from '@/types'

/**
 * 发布失物/拾物
 * POST /api/lost-items
 */
export const createLostItem = (data: CreateLostItemPayload) => {
    return request.post<never, LostItem>('/lost-items', data)
}

/**
 * 获取失物招领列表
 * GET /api/lost-items?is_lost=&offset=0&limit=20
 */
export const getLostItems = async (params?: { is_lost?: boolean; offset?: number; limit?: number }) => {
    const data = await request.get<never, LostItem[]>('/lost-items', { params })
    // 包装成分页结构
    return {
        items: data,
        total: data.length,
        offset: params?.offset || 0,
        limit: params?.limit || 20,
    }
}

/**
 * 获取单个物品详情
 * GET /api/lost-items/{id}
 */
export const getLostItemById = (id: number) => {
    return request.get<never, LostItem>(`/lost-items/${id}`)
}

/**
 * 标记为已找回
 * POST /api/lost-items/{id}/found
 */
export const markAsFound = (id: number) => {
    return request.post<never, { success: boolean; message: string }>(`/lost-items/${id}/found`)
}