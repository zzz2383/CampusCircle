"""
功能：帖子业务逻辑接口

实现逻辑：
    定义校园帖子的发布、查询、删除等业务操作抽象接口

调用链路：
    - 被表现层的 posts 路由调用
    - 调用数据访问层的 PostDAO + 部分 Redis Repository
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from app.models.dto import (
    PostCreateRequest,
    PostUpdateRequest,
    PostDTO,
    PostListResponse,
)


class IPostService(ABC):
    """帖子服务接口"""

    @abstractmethod
    async def create_post(self, user_id: int, request: PostCreateRequest) -> PostDTO:
        """发布校园帖

        实现逻辑：
            1. 校验用户是否存在
            2. 写入 SQLite posts 表
            3. 写入话题标签关联
            4. 写入 Redis 时间线（LPUSH）

        参数：
            user_id: 作者 ID
            request: 帖子创建请求（title, content, tags）

        返回值：
            PostDTO: 帖子信息

        测试用例：
            - test_create_post_success
            - test_create_post_user_not_found
        """
        ...

    @abstractmethod
    async def get_post_by_id(self, post_id: int) -> Optional[PostDTO]:
        """根据 ID 获取帖子"""
        ...

    @abstractmethod
    async def delete_post(self, post_id: int, user_id: int) -> bool:
        """删除帖子（仅作者可删）"""
        ...

    @abstractmethod
    async def list_posts(
        self, offset: int = 0, limit: int = 20, tag: Optional[str] = None
    ) -> PostListResponse:
        """获取帖子列表（支持分页和标签筛选）"""
        ...

    @abstractmethod
    async def increment_view_count(self, post_id: int) -> int:
        """增加帖子浏览量

        参数：
            post_id: 帖子 ID

        返回值：
            更新后的浏览量
        """
        ...

    @abstractmethod
    async def get_user_posts(
        self, user_id: int, offset: int = 0, limit: int = 20
    ) -> PostListResponse:
        """获取用户的帖子列表

        实现逻辑：
            1. 调用 PostDAO.list_by_user 按用户 ID 分页查询
            2. 转换为 PostDTO 列表（含真实评论/点赞数据）

        参数：
            user_id: 用户 ID
            offset: 分页偏移量
            limit: 每页数量

        返回值：
            PostListResponse: 帖子列表响应
        """
        ...
