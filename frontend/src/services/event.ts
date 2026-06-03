import request from './request'
import type { Event, CreateEventPayload, UpdateEventPayload, EventParticipant } from '@/types'

/**
 * 创建活动
 */
export const createEvent = (data: CreateEventPayload) => {
    return request.post<never, Event>('/events', data)
}

/**
 * 获取活动列表（后端直接返回数组）
 */
export const getEvents = async (params?: { offset?: number; limit?: number; club_id?: number }) => {
    const data = await request.get<never, Event[]>('/events', { params })
    // 包装成分页结构以保持一致性
    return {
        items: data,
        total: data.length,
        offset: params?.offset || 0,
        limit: params?.limit || 20,
    }
}

/**
 * 获取活动详情
 */
export const getEventById = (eventId: number) => {
    return request.get<never, Event>(`/events/${eventId}`)
}

/**
 * 编辑活动
 */
export const updateEvent = (eventId: number, data: UpdateEventPayload) => {
    return request.put<never, Event>(`/events/${eventId}`, data)
}

/**
 * 删除活动
 */
export const deleteEvent = (eventId: number) => {
    return request.delete(`/events/${eventId}`)
}

/**
 * 报名活动
 */
export const registerEvent = (eventId: number) => {
    return request.post<never, { success: boolean; message: string }>(`/events/${eventId}/register`)
}

/**
 * 取消报名
 */
export const cancelRegister = (eventId: number) => {
    return request.delete<never, { success: boolean; message: string }>(`/events/${eventId}/register`)
}

/**
 * 获取参与成员列表
 */
export const getParticipants = (eventId: number) => {
    return request.get<never, EventParticipant[]>(`/events/${eventId}/participants`)
}

/**
 * 获取实时报名人数
 */
export const getParticipantCount = (eventId: number) => {
    return request.get<never, { participant_count: number }>(`/events/${eventId}/participant-count`)
}