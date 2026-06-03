"""
功能：SQLAlchemy ORM 数据库模型定义

实现逻辑：
    1. 所有模型继承自 declarative_base()
    2. 使用 SQLAlchemy 2.0 Mapped 类型注解风格
    3. 定义 User、Post、Comment、Club、Event、LostItem 六个模型

调用链路：
    - 被 db.py 中的 init_db() 用于自动建表
    - 被 data_access/sqlite_dao 层用于 ORM 操作
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Text, Boolean, DateTime, Integer, ForeignKey, UniqueConstraint, Enum as SAEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.enums import UserRole, Gender, TagType


class Base(DeclarativeBase):
    """ORM 基类"""
    pass


class User(Base):
    """用户模型"""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_id: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, comment="学号/工号")
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, comment="校园邮箱")
    nickname: Mapped[str] = mapped_column(String(50), nullable=False, comment="昵称")
    password_hash: Mapped[str] = mapped_column(String(128), nullable=False, comment="密码哈希")
    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole, name="user_role"), default=UserRole.STUDENT, nullable=False
    )
    gender: Mapped[Optional[Gender]] = mapped_column(
        SAEnum(Gender, name="gender"), nullable=True
    )
    department: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment="院系")
    grade: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, comment="年级")
    avatar_url: Mapped[Optional[str]] = mapped_column(String(256), nullable=True, comment="头像 URL")
    is_online: Mapped[bool] = mapped_column(Boolean, default=False, comment="在线状态")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否激活")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), comment="创建时间"
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间"
    )

    # 关系
    posts = relationship("Post", back_populates="author", lazy="selectin")


class Post(Base):
    """帖子模型"""
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False, comment="作者 ID"
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False, comment="标题")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="正文内容")
    tags: Mapped[Optional[str]] = mapped_column(
        String(200), nullable=True, comment="话题标签（逗号分隔）"
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否可见（软删除）")
    view_count: Mapped[int] = mapped_column(Integer, default=0, comment="浏览数")
    club_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("clubs.id"), nullable=True, comment="所属社团 ID"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), comment="创建时间"
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间"
    )

    # 关系
    author = relationship("User", back_populates="posts", lazy="selectin")


class Comment(Base):
    """评论模型（支持楼中楼）"""
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    post_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("posts.id"), nullable=False, comment="所属帖子 ID"
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False, comment="评论者 ID"
    )
    parent_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("comments.id"), nullable=True, comment="父评论 ID（楼中楼）"
    )
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="评论内容")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否可见")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), comment="创建时间"
    )

    # 关系
    author = relationship("User", lazy="selectin")


class Club(Base):
    """社团模型"""
    __tablename__ = "clubs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, comment="社团名称")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="社团简介")
    logo_url: Mapped[Optional[str]] = mapped_column(String(256), nullable=True, comment="社团 Logo")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), comment="创建时间"
    )


class ClubMember(Base):
    """社团成员模型"""
    __tablename__ = "club_members"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False, comment="用户 ID"
    )
    club_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("clubs.id"), nullable=False, comment="社团 ID"
    )
    role: Mapped[str] = mapped_column(String(20), default="member", comment="角色: member/admin")
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), comment="加入时间"
    )

    __table_args__ = (
        UniqueConstraint("user_id", "club_id", name="uq_user_club"),
    )


class Event(Base):
    """活动模型（社团活动、讲座等）"""
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    club_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("clubs.id"), nullable=True, comment="所属社团 ID"
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False, comment="活动标题")
    description: Mapped[str] = mapped_column(Text, nullable=False, comment="活动描述")
    location: Mapped[Optional[str]] = mapped_column(String(200), nullable=True, comment="活动地点")
    max_participants: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="最大参与人数")
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, comment="开始时间")
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, comment="结束时间")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), comment="创建时间"
    )



class EventParticipant(Base):
    """活动报名模型"""
    __tablename__ = "event_participants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False, comment="用户 ID"
    )
    event_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("events.id"), nullable=False, comment="活动 ID"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), comment="报名时间"
    )

    __table_args__ = (
        UniqueConstraint("user_id", "event_id", name="uq_user_event"),
    )


class LostItem(Base):
    """失物招领模型"""
    __tablename__ = "lost_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False, comment="发布者 ID"
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False, comment="标题")
    description: Mapped[str] = mapped_column(Text, nullable=False, comment="物品描述")
    image_url: Mapped[Optional[str]] = mapped_column(String(256), nullable=True, comment="物品图片 URL")
    location: Mapped[Optional[str]] = mapped_column(String(200), nullable=True, comment="丢失/拾到地点")
    contact: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment="联系方式")
    is_found: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, comment="是否已找回")
    is_lost: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, comment="True=丢失, False=拾到")
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="自动过期时间（7天后）"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), comment="创建时间"
    )
