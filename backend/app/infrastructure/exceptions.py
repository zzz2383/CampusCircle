"""
功能：项目全局异常基类体系

实现逻辑：
    1. AppException 是所有业务异常的基类，携带 code、message、status_code
    2. NotFoundError -> PostNotFoundError / UserNotFoundError：资源不存在
    3. DuplicateError：资源重复（如重复注册、重复点赞）
    4. AuthError：认证/授权失败
    5. BusinessError：通用业务逻辑异常

调用链路：
    - 被业务层 Service 抛出
    - 被表现层全局异常处理器捕获并返回标准化错误响应
"""


class AppException(Exception):
    """应用基础异常"""

    def __init__(self, code: str, message: str, status_code: int = 400):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundError(AppException):
    """资源不存在"""

    def __init__(self, code: str = "NOT_FOUND", message: str = "资源不存在", status_code: int = 404):
        super().__init__(code, message, status_code)


class PostNotFoundError(NotFoundError):
    """帖子不存在"""

    def __init__(self, post_id: int):
        super().__init__(
            code="POST_NOT_FOUND",
            message=f"帖子 #{post_id} 不存在",
            status_code=404,
        )


class UserNotFoundError(NotFoundError):
    """用户不存在"""

    def __init__(self, user_id: int):
        super().__init__(
            code="USER_NOT_FOUND",
            message=f"用户 #{user_id} 不存在",
            status_code=404,
        )


class DuplicateError(AppException):
    """资源重复"""

    def __init__(self, code: str = "DUPLICATE", message: str = "资源已存在", status_code: int = 409):
        super().__init__(code, message, status_code)


class AuthError(AppException):
    """认证/授权失败"""

    def __init__(self, code: str = "AUTH_ERROR", message: str = "认证失败", status_code: int = 401):
        super().__init__(code, message, status_code)


class ForbiddenError(AppException):
    """权限不足"""

    def __init__(self, code: str = "FORBIDDEN", message: str = "权限不足", status_code: int = 403):
        super().__init__(code, message, status_code)


class BusinessError(AppException):
    """通用业务逻辑异常"""

    def __init__(self, code: str = "BUSINESS_ERROR", message: str = "业务逻辑错误", status_code: int = 400):
        super().__init__(code, message, status_code)
