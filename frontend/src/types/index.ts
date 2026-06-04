// src/types/index.ts
// 追加性别枚举
export type Gender = 'male' | 'female'

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
    author_avatar: string | null
    like_count: number
    comment_count: number
    view_count: number
    is_liked: boolean
    created_at: string
    updated_at: string
    club_id?: number | null
    club_name?: string | null
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
    author_avatar: string | null
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
    club_id?: number | null
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

export interface LostItem {
    id: number
    user_id: number
    title: string
    description: string
    location: string | null
    contact: string | null
    is_found: boolean
    is_lost: boolean           // true=丢失，false=拾到
    expires_at: string         // 过期时间 ISO 字符串
    created_at: string
    author_nickname: string
    // 前端计算字段
    is_expired?: boolean
    image_url?: string | null

}

export interface CreateLostItemPayload {
    title: string
    description: string
    location?: string
    contact?: string
    is_lost: boolean
    image_url?: string | null   // 新增此行
}

export interface LostItemListResponse {
    items: LostItem[]
    total: number
    offset: number
    limit: number
}

// 社团相关类型
export interface Club {
    id: number
    name: string
    description: string | null
    logo_url: string | null
    created_at: string
    member_count?: number  // 前端计算或后端返回
}

export interface ClubMember {
    id: number
    user_id: number
    club_id: number
    role: 'member' | 'admin' | 'founder'
    joined_at: string
    user_nickname: string
}

export interface CreateClubPayload {
    name: string
    description?: string
}

export interface EventDTO {
    id: number
    title: string
    description: string
    location: string | null
    max_participants: number | null
    start_time: string
    end_time: string
    club_id?: number | null
    club_name?: string | null
    created_at: string
}

// 活动相关类型
export interface Event {
    id: number
    title: string
    description: string
    location: string | null
    max_participants: number | null
    participant_count: number
    is_registered: boolean
    club_id: number | null
    club_name?: string | null
    start_time: string
    end_time: string
    created_at: string
}

export interface CreateEventPayload {
    title: string
    description: string
    location?: string
    max_participants?: number | null
    club_id?: number | null
    start_time: string
    end_time: string
}

export interface UpdateEventPayload {
    title?: string
    description?: string
    location?: string | null
    max_participants?: number | null
    club_id?: number | null
    start_time?: string
    end_time?: string
}

export interface EventParticipant {
    id: number
    user_id: number
    event_id: number
    user_nickname: string
    created_at: string
}

// 追加管理员统计数据类型
export interface AdminStats {
    total_users: number
    total_posts: number
    total_clubs: number
    total_events: number
    total_lost_items: number
}

// 管理员用户列表项（与UserDTO一致，可直接复用）
export interface AdminUser extends User { }

// 被封禁用户信息
export interface BannedUser {
    user_id: number
    banned_at: string
    remaining_seconds: number
}

// 评论管理项
export interface AdminComment {
    id: number
    post_id: number
    user_id: number
    author_nickname: string
    content: string
    parent_id: number | null
    created_at: string
}