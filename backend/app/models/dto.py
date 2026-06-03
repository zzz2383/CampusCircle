"""
功能：Pydantic DTO 模型定义（请求/响应模型）

实现逻辑：
    1. 请求模型（*Request）：用于 API 请求体校验
    2. 响应模型（*DTO/*Response）：用于 API 响应序列化
    3. 使用 Pydantic v2 的 model_validator 做字段校验
"""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, EmailStr

from app.models.enums import Gender


# ========== 用户相关 ==========

class UserRegisterRequest(BaseModel):
    """用户注册请求"""
    student_id: str = Field(..., min_length=4, max_length=20, description="学号/工号")
    email: str = Field(..., max_length=100, description="校园邮箱")
    password: str = Field(..., min_length=6, max_length=64, description="密码")
    nickname: str = Field(..., min_length=1, max_length=50, description="昵称")
    department: Optional[str] = Field(None, max_length=100, description="院系")
    grade: Optional[str] = Field(None, max_length=20, description="年级")
    gender: Optional[Gender] = Field(None, description="性别")


class UserLoginRequest(BaseModel):
    """用户登录请求"""
    student_id: str = Field(..., description="学号/工号")
    password: str = Field(..., description="密码")


class UserDTO(BaseModel):
    """用户信息 DTO"""
    id: int
    student_id: str
    email: str
    nickname: str
    role: str
    department: Optional[str] = None
    grade: Optional[str] = None
    gender: Optional[Gender] = None
    avatar_url: Optional[str] = None
    is_online: bool = False
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class TokenDTO(BaseModel):
    """登录令牌 DTO"""
    access_token: str
    token_type: str = "bearer"
    user: UserDTO


class UserProfileUpdateRequest(BaseModel):
    """更新个人资料请求"""
    nickname: Optional[str] = Field(None, min_length=1, max_length=50, description="昵称")
    department: Optional[str] = Field(None, max_length=100, description="院系")
    grade: Optional[str] = Field(None, max_length=20, description="年级")
    gender: Optional[Gender] = Field(None, description="性别")
    avatar_url: Optional[str] = Field(None, max_length=256, description="头像 URL")


# ========== 帖子相关 ==========

class PostCreateRequest(BaseModel):
    """创建帖子请求"""
    title: str = Field(..., min_length=1, max_length=200, description="标题")
    content: str = Field(..., min_length=1, description="正文内容")
    tags: Optional[str] = Field(None, max_length=200, description="话题标签（逗号分隔）")
    club_id: Optional[int] = Field(None, description="所属社团 ID")


class PostUpdateRequest(BaseModel):
    """更新帖子请求"""
    title: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = None
    tags: Optional[str] = None


class PostDTO(BaseModel):
    """帖子信息 DTO"""
    id: int
    user_id: int
    title: str
    content: str
    tags: Optional[str] = None
    club_id: Optional[int] = None
    club_name: Optional[str] = None
    author_nickname: Optional[str] = None
    like_count: int = 0
    comment_count: int = 0
    view_count: int = 0
    is_liked: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class PostListResponse(BaseModel):
    """帖子列表响应"""
    items: List[PostDTO]
    total: int
    offset: int
    limit: int


# ========== 评论相关 ==========

class CommentCreateRequest(BaseModel):
    """创建评论请求"""
    content: str = Field(..., min_length=1, max_length=2000, description="评论内容")
    parent_id: Optional[int] = Field(None, description="父评论 ID（楼中楼）")


class CommentDTO(BaseModel):
    """评论信息 DTO"""
    id: int
    post_id: int
    user_id: int
    author_nickname: Optional[str] = None
    content: str
    parent_id: Optional[int] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class CommentListResponse(BaseModel):
    """评论列表响应"""
    items: List[CommentDTO]
    total: int


# ========== 点赞相关 ==========

class LikeResultDTO(BaseModel):
    """点赞结果 DTO"""
    is_liked: bool
    like_count: int


# ========== 社团相关 ==========

class ClubCreateRequest(BaseModel):
    """创建社团请求"""
    name: str = Field(..., min_length=1, max_length=100, description="社团名称")
    description: Optional[str] = Field(None, description="社团简介")


class ClubDTO(BaseModel):
    """社团信息 DTO"""
    id: int
    name: str
    description: Optional[str] = None
    logo_url: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ClubMemberDTO(BaseModel):
    """社团成员 DTO"""
    id: int
    user_id: int
    club_id: int
    role: str = "member"
    joined_at: Optional[datetime] = None
    user_nickname: Optional[str] = None

    model_config = {"from_attributes": True}


# ========== 活动相关 ==========

class EventCreateRequest(BaseModel):
    """创建活动请求"""
    title: str = Field(..., min_length=1, max_length=200, description="活动标题")
    description: str = Field(..., min_length=1, description="活动描述")
    location: Optional[str] = Field(None, max_length=200, description="活动地点")
    max_participants: Optional[int] = Field(None, ge=1, description="最大参与人数")
    club_id: Optional[int] = Field(None, description="所属社团 ID")
    start_time: datetime = Field(..., description="开始时间（ISO 格式）")
    end_time: datetime = Field(..., description="结束时间（ISO 格式）")


class EventUpdateRequest(BaseModel):
    """更新活动请求"""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="活动标题")
    description: Optional[str] = Field(None, min_length=1, description="活动描述")
    location: Optional[str] = Field(None, max_length=200, description="活动地点")
    max_participants: Optional[int] = Field(None, ge=1, description="最大参与人数")
    club_id: Optional[int] = Field(None, description="所属社团 ID")
    start_time: Optional[datetime] = Field(None, description="开始时间（ISO 格式）")
    end_time: Optional[datetime] = Field(None, description="结束时间（ISO 格式）")


class EventDTO(BaseModel):
    """活动信息 DTO"""
    id: int
    title: str
    description: str
    location: Optional[str] = None
    max_participants: Optional[int] = None
    club_id: Optional[int] = None
    participant_count: int = 0
    is_registered: bool = False
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class EventParticipantDTO(BaseModel):
    """活动报名信息 DTO"""
    id: int
    user_id: int
    event_id: int
    user_nickname: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ========== 排行榜相关 ==========

class ClubRankDTO(BaseModel):
    """社团排行榜 DTO"""
    club_id: int
    club_name: str
    post_count: int
    rank: int


# ========== 通知相关 ==========

class NotificationDTO(BaseModel):
    """通知 DTO"""
    id: str
    type: str
    content: str
    sender_id: Optional[int] = None
    post_id: Optional[int] = None
    is_read: bool = False
    created_at: Optional[datetime] = None


# ========== 失物招领相关 ==========

class LostItemCreateRequest(BaseModel):
    """发布失物/拾物请求"""
    title: str = Field(..., min_length=1, max_length=200, description="标题")
    description: str = Field(..., min_length=1, description="物品描述")
    location: Optional[str] = Field(None, max_length=200, description="丢失/拾到地点")
    contact: Optional[str] = Field(None, max_length=100, description="联系方式")
    is_lost: bool = Field(True, description="True=丢失, False=拾到")


class LostItemDTO(BaseModel):
    """失物招领 DTO"""
    id: int
    user_id: int
    title: str
    description: str
    location: Optional[str] = None
    contact: Optional[str] = None
    is_found: bool = False
    is_lost: bool = True
    expires_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    author_nickname: Optional[str] = None

    model_config = {"from_attributes": True}
