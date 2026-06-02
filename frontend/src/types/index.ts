// src/types/index.ts
export interface User {
    id: number
    student_id: string          // snake_case 匹配后端
    email: string
    nickname: string
    role: 'student' | 'teacher' | 'admin'
    department: string | null
    grade: string | null
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

export interface RegisterPayload {
    student_id: string
    email: string
    password: string
    nickname?: string
    department?: string   // 可选，后端接受但可能暂时忽略
    grade?: string
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