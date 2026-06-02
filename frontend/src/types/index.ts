// src/types/index.ts
// 追加性别枚举
export type Gender = 'male' | 'female' | 'other'

// 更新 UserDTO（后端已补 gender）
export interface User {
    id: number
    student_id: string
    email: string
    nickname: string
    role: 'student' | 'teacher' | 'admin'
    department: string | null
    grade: string | null
    gender: Gender | null
    avatar_url: string | null
    is_online: boolean
    created_at: string
}

export interface TokenDTO {
    access_token: string
    token_type: string
    user: User
}

export interface LoginPayload {
    student_id: string   // 注意字段名改为 student_id
    password: string
}

// 注册请求体（扩充）
export interface RegisterPayload {
    student_id: string
    email: string
    password: string
    nickname?: string
    department?: string
    grade?: string
    gender?: Gender
}


export interface PostDTO {
    id: number
    user_id: number
    title: string
    content: string
    tags: string | null
    author_nickname: string
    like_count: number
    comment_count: number
    view_count: number
    is_liked: boolean
    created_at: string
    updated_at: string
}

export interface PostListResponse {
    items: PostDTO[]
    total: number
    offset: number
    limit: number
}

export interface LikeResponse {
    is_liked: boolean
    like_count: number
}

export interface FavoriteResponse {
    is_favorited: boolean
    favorite_count: number
}

export interface CommentDTO {
    id: number
    post_id: number
    user_id: number
    author_nickname: string
    content: string
    parent_id: number | null
    created_at: string
}

export interface ClubRankDTO {
    club_id: number
    club_name: string
    post_count: number
}

export interface CreatePostPayload {
    title: string
    content: string
    tags?: string   // 逗号分隔的标签字符串
}

export interface LikeResponse {
    is_liked: boolean
    like_count: number
}

export interface ClubRank {
    club_id: number
    club_name: string
    post_count: number
    rank?: number   // 后端可能返回排名
}

// 更新个人资料请求体（全部可选）
export interface UpdateProfilePayload {
    nickname?: string
    department?: string
    grade?: string
    gender?: Gender
    avatar_url?: string
}