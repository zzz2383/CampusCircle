"""
功能：全局配置管理，基于 pydantic-settings 从 .env 文件加载配置

实现逻辑：
    1. 使用 pydantic-settings 的 BaseSettings 自动读取环境变量
    2. 优先从 .env 文件加载，其次从系统环境变量读取
    3. Redis 配置支持无密码场景
    4. 提供构建 Redis URL 的便捷属性

调用链路：
    - 被所有层引用获取配置项
    - 被 db.py 用于数据库连接字符串
    - 被 redis_client.py 用于 Redis 连接参数

参数说明：
    env_file: ".env" 指定开发环境配置文件
    extra: "ignore" 忽略未定义的环境变量

异常说明：
    无（启动时若缺失关键配置会直接报错）
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import json


class Settings(BaseSettings):
    """应用全局配置"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # 数据库配置
    DATABASE_URL: str = "sqlite+aiosqlite:///./app/infrastructure/data/campus_circle.db"

    # Redis 配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""

    # JWT 配置
    JWT_SECRET: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24

    # 应用配置
    APP_NAME: str = "CampusCircle"
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"

    # 上传配置
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 5 * 1024 * 1024
    ALLOWED_EXTENSIONS: str = "jpg,jpeg,png,gif,webp"

    # CORS
    CORS_ORIGINS: str = '["http://localhost:5173","http://localhost:3000"]'

    @property
    def cors_origins_list(self) -> List[str]:
        """将 JSON 字符串格式的 CORS_ORIGINS 解析为列表"""
        return json.loads(self.CORS_ORIGINS)

    @property
    def redis_url(self) -> str:
        """构建 Redis 连接 URL"""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


settings = Settings()
