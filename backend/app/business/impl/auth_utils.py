"""
功能：认证工具函数（密码哈希 + JWT 令牌管理）

实现逻辑：
    1. 密码哈希：使用 bcrypt 直接进行哈希（不依赖 passlib）
    2. JWT 创建：使用 python-jose 的 jwt.encode，含过期时间
    3. JWT 解码：使用 jwt.decode，返回 payload 或 None

调用链路：
    - 被 UserServiceImpl 在注册/登录时调用
    - 被 presentation/dependencies.py 中的 get_current_user 调用

参数说明：
    settings.JWT_EXPIRATION_HOURS: Token 过期小时数（默认 24）
    settings.JWT_SECRET: 签名密钥
    settings.JWT_ALGORITHM: 签名算法（HS256）
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from jose import jwt, JWTError

from app.infrastructure.config import settings


def hash_password(password: str) -> str:
    """对密码进行 bcrypt 哈希

    参数：
        password: 明文密码

    返回值：
        bcrypt 哈希字符串（含 salt）
    """
    # bcrypt 只处理前 72 字节，但现代 bcrypt 需要手动截断
    pwd_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """校验密码是否匹配

    参数：
        plain_password: 明文密码
        hashed_password: bcrypt 哈希字符串

    返回值：
        True 如果匹配，False 否则
    """
    pwd_bytes = plain_password.encode("utf-8")[:72]
    hash_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(pwd_bytes, hash_bytes)


def create_access_token(data: dict) -> str:
    """创建 JWT 访问令牌

    实现逻辑：
        1. 复制 payload 数据
        2. 添加过期时间（exp）字段
        3. 使用 HS256 算法签名

    参数：
        data: JWT payload，通常包含 {"sub": user_id}

    返回值：
        编码后的 JWT 字符串
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    """解码 JWT 访问令牌

    实现逻辑：
        1. 使用相同的 secret 和 algorithm 解码
        2. 自动校验过期时间
        3. 解码失败返回 None（令牌无效或已过期）

    参数：
        token: JWT 字符串

    返回值：
        payload 字典，或 None（无效令牌）
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError:
        return None
