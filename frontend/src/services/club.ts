import request from './request'
import type { Club, ClubMember, CreateClubPayload, PostListResponse } from '@/types'

export const getClubs = () => {
    return request.get<never, Club[]>('/clubs')
}

export const getClubById = (clubId: number) => {
    return request.get<never, Club>(`/clubs/${clubId}`)
}

export const createClub = (data: CreateClubPayload) => {
    return request.post<never, Club>('/clubs', data)
}

export const joinClub = (clubId: number) => {
    return request.post<never, { success: boolean; message: string }>(`/clubs/${clubId}/members`)
}

export const leaveClub = (clubId: number) => {
    return request.delete<never, { success: boolean; message: string }>(`/clubs/${clubId}/members`)
}

export const getClubMembers = (clubId: number) => {
    return request.get<never, ClubMember[]>(`/clubs/${clubId}/members`)
}

export const checkIsMember = (clubId: number) => {
    return request.get<never, { is_member: boolean }>(`/clubs/${clubId}/members/me`)
}

export const getClubPosts = (clubId: number, params?: { offset?: number; limit?: number }) => {
    return request.get<never, PostListResponse>(`/clubs/${clubId}/posts`, { params })
}

// 社团活动列表（如有需要）
export const getClubEvents = (clubId: number, params?: { offset?: number; limit?: number }) => {
    return request.get<never, any[]>(`/clubs/${clubId}/events`, { params })
}