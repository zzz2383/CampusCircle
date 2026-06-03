"""图片上传路由"""
import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.infrastructure.config import settings
from app.infrastructure.logger import get_logger
from app.models.dto import UserDTO
from app.presentation.dependencies import get_current_user

logger = get_logger(__name__)

router = APIRouter(prefix="/api/upload", tags=["上传"])

ALLOWED_EXTENSIONS = set(settings.ALLOWED_EXTENSIONS.split(","))
UPLOAD_DIR = Path(settings.UPLOAD_DIR) / "images"


@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    current_user: UserDTO = Depends(get_current_user),
):
    """上传图片（需要登录）

    限制：
        - 仅允许 jpg/png/gif/webp 格式
        - 最大 5MB
        - 自动 UUID 重命名防冲突

    返回：
        url: 图片访问路径
        filename: 文件名
    """
    # 校验文件类型
    ext = os.path.splitext(file.filename or "")[1].lower().replace(".", "")
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件格式: .{ext}，仅支持 {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # 创建上传目录
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    # UUID 命名，保留扩展名
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = UPLOAD_DIR / filename

    # 写入文件
    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文件过大（{len(content)} bytes），最大允许 {settings.MAX_UPLOAD_SIZE} bytes",
        )

    with open(filepath, "wb") as f:
        f.write(content)

    url = f"/uploads/images/{filename}"
    logger.info(f"Image uploaded: {filename} by user #{current_user.id}")

    return {"url": url, "filename": filename}
