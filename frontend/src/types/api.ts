// ===== 用户相关 =====
export interface UserRegisterRequest {
  student_id: string
  email: string
  password: string
  nickname: string
}

export interface UserLoginRequest {
  student_id: string
  password: string
}

export interface UserDTO {
  id: number
  student_id: string
  email: string
  nickname: string
  role: string
  department?: string
  grade?: string
  avatar_url?: string
  is_online: boolean
  created_at?: string
}

export interface TokenDTO {
  access_token: string
  token_type: string
  user: UserDTO
}

// ===== 帖子相关 =====
export interface PostCreateRequest {
  title: string
  content: string
  tags?: string
}

export interface PostDTO {
  id: number
  user_id: number
  title: string
  content: string
  tags?: string
  author_nickname?: string
  like_count: number
  comment_count: number
  view_count: number
  is_liked: boolean
  created_at?: string
  updated_at?: string
}

export interface PostListResponse {
  items: PostDTO[]
  total: number
  offset: number
  limit: number
}

// ===== 点赞相关 =====
export interface LikeResultDTO {
  is_liked: boolean
  like_count: number
}

// ===== 排行榜相关 =====
export interface ClubRankDTO {
  club_id: number
  club_name: string
  post_count: number
  rank: number
}
