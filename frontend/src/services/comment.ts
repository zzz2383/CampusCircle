import request from './request'
import type { CommentDTO } from '@/types'

export const getComments = (postId: number, params?: { offset?: number; limit?: number }) => {
    return request.get<never, { items: CommentDTO[]; total: number }>(`/posts/${postId}/comments`, { params })
}

export const createComment = (postId: number, data: { content: string; parent_id?: number }) => {
    return request.post<never, CommentDTO>(`/posts/${postId}/comments`, data)
}

export const deleteComment = (commentId: number) => {
    return request.delete(`/comments/${commentId}`)
}