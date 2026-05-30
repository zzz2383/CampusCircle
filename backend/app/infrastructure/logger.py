"""
功能：全局日志配置

实现逻辑：
    1. 使用 Python 标准 logging 模块
    2. 根据 settings.DEBUG 设置日志级别
    3. 统一的日志格式：时间 - 日志级别 - 模块名 - 消息

调用链路：
    - 被所有模块通过 get_logger(__name__) 调用
"""

import logging
import sys

from app.infrastructure.config import settings


def get_logger(name: str) -> logging.Logger:
    """获取配置好的日志记录器

    参数：
        name: 模块名，通常传入 __name__

    返回值：
        配置完成的 Logger 实例
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s - %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        level = logging.DEBUG if settings.DEBUG else logging.INFO
        logger.setLevel(level)

    return logger
