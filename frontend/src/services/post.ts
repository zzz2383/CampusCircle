import request from './request'
import type { PostDTO, PostListResponse, CreatePostPayload, LikeResponse } from '@/types'

/**
 * 获取帖子列表
 * GET /api/posts?offset=0&limit=20&tag=课程
 */
export const getPosts = (params?: {
    offset?: number;
    limit?: number;
    tag?: string;
    club_id?: number;
    keyword?: string
}) => {
    return request.get<never, PostListResponse>('/posts', { params })
}

/**
 * 获取单个帖子详情
 */
export const getPostById = (id: number) => {
    return request.get<never, PostDTO>(`/posts/${id}`)
}

/**
 * 创建帖子 (需要认证)
 */
export const createPost = (data: CreatePostPayload) => {
    return request.post<never, PostDTO>('/posts', data)
}

/**
 * 删除帖子 (需要认证，仅作者或管理员)
 */
export const deletePost = (id: number) => {
    return request.delete(`/posts/${id}`)
}

/**
 * 点赞帖子
 */
export const likePost = (postId: number) => {
    return request.post<never, LikeResponse>(`/posts/${postId}/like`)
}

/**
 * 取消点赞
 */
export const unlikePost = (postId: number) => {
    return request.delete<never, LikeResponse>(`/posts/${postId}/like`)
}

/**
 * 获取当前用户的帖子列表
 * GET /api/users/me/posts?offset=0&limit=20
 */
export const getMyPosts = (params?: { offset?: number; limit?: number }) => {
    return request.get<never, PostListResponse>('/users/me/posts', { params })
}