import request from './request'
import type { AdminStats, User, AdminComment, BannedUser } from '@/types'

// 统计
export const getAdminStats = () => {
    return request.get<never, AdminStats>('/admin/stats')
}

// 删除内容
export const deletePostByAdmin = (postId: number) => {
    return request.delete(`/admin/posts/${postId}`)
}
export const deleteCommentByAdmin = (commentId: number) => {
    return request.delete(`/admin/comments/${commentId}`)
}
export const deleteEventByAdmin = (eventId: number) => {
    return request.delete(`/admin/events/${eventId}`)
}
export const deleteLostItemByAdmin = (itemId: number) => {
    return request.delete(`/admin/lost-items/${itemId}`)
}
export const deleteClubByAdmin = (clubId: number) => {
    return request.delete(`/admin/clubs/${clubId}`)
}

// 用户管理
export const getAdminUsers = (params?: { offset?: number; limit?: number; keyword?: string }) => {
    return request.get<never, { items: User[]; total: number; offset: number; limit: number }>('/admin/users', { params })
}
export const getUserDetail = (userId: number) => {
    return request.get<never, User>(`/admin/users/${userId}`)
}
export const getBannedUsers = () => {
    return request.get<never, BannedUser[]>('/admin/users/banned')
}
export const updateUserRole = (userId: number, role: 'student' | 'teacher' | 'admin') => {
    return request.put<never, { success: boolean }>(`/admin/users/${userId}/role`, { role })
}
export const banUser = (userId: number, durationHours?: number) => {
    return request.post<never, { success: boolean; message: string }>(`/admin/users/${userId}/ban`, { duration_hours: durationHours || 24 })
}
export const unbanUser = (userId: number) => {
    return request.post<never, { success: boolean; message: string }>(`/admin/users/${userId}/unban`)
}

// 评论列表（管理用）
export const getAdminComments = (params?: { offset?: number; limit?: number }) => {
    return request.get<never, { items: AdminComment[]; total: number; offset: number; limit: number }>('/admin/comments', { params })
}