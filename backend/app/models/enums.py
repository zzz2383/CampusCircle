"""
功能：项目枚举类型定义

实现逻辑：
    使用 Python 标准库 enum 定义系统中所有枚举常量
"""

from enum import IntEnum, StrEnum


class UserRole(StrEnum):
    """用户角色"""
    STUDENT = "student"       # 学生
    TEACHER = "teacher"       # 教师
    ADMIN = "admin"           # 管理员（辅导员/学生干部）


class Gender(StrEnum):
    """性别"""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class TagType(StrEnum):
    """帖子话题标签"""
    COURSE = "课程"
    CLUB = "社团"
    HELP = "求助"
    LOST = "失物招领"
    NOTICE = "通知"
    ACTIVITY = "活动"
    LECTURE = "讲座"
    GENERAL = "综合"


class NotificationType(StrEnum):
    """通知类型"""
    LIKE = "like"               # 被点赞
    COMMENT = "comment"         # 被评论
    FOLLOW = "follow"           # 被关注
    EVENT_SIGNUP = "event_signup"  # 活动报名提醒
    SYSTEM = "system"           # 系统通知
