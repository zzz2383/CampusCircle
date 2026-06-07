FROM python:3.13-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制项目配置文件及源码（必须先有源码，才能安装项目本身）
COPY backend/pyproject.toml .
COPY backend/app ./app
COPY backend/.env ./.env

# 安装 Python 依赖（不使用 -e，直接安装项目及所有依赖）
RUN pip install --no-cache-dir ".[dev]"

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]