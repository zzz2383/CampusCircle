# 🏫 校园圈 (CampusCircle)

> 专为在校师生设计的实时交流与信息共享平台

## 技术栈

### 后端
- **框架**: FastAPI (Python 3.13+)
- **ORM**: SQLAlchemy 2.0 (异步)
- **数据库**: SQLite (开发) / aiosqlite
- **缓存**: Redis (异步)
- **认证**: JWT (python-jose)

### 前端
- **框架**: Vue 3 + TypeScript
- **构建工具**: Vite
- **状态管理**: Pinia
- **路由**: Vue Router 4
- **HTTP 客户端**: Axios

## 快速开始

### 前置要求

- Python 3.11+
- Node.js 18+
- Redis 7+（可选，开发模式下不用 Redis 也能启动）

### 后端启动

```bash
cd backend

# 初始化虚拟环境（已存在则跳过）
python -m venv .venv

# 安装依赖（Windows 使用 .venv\Scripts\pip）
.venv/Scripts/pip install -e ".[dev]"

# 启动开发服务器
.venv/Scripts/uvicorn app.main:app --reload

# 访问 API 文档
# http://localhost:8000/docs
```

### 前端启动

```bash
cd frontend
npm install
npm run dev
```

### 测试

```bash
cd backend
.venv/Scripts/pytest -v
```

## 项目结构

```
campus_circle/
├── backend/
│   ├── app/
│   │   ├── presentation/     # 表现层（API 路由 + WebSocket）
│   │   ├── business/         # 业务层（Service 接口 + 实现）
│   │   ├── data_access/      # 数据访问层（DAO + Repository）
│   │   ├── infrastructure/   # 基础设施层（DB、Redis、配置）
│   │   ├── models/           # 数据模型（ORM + DTO）
│   │   └── main.py           # 应用入口
│   └── tests/                # 测试（单元/集成/端到端）
├── frontend/
│   └── src/
│       ├── components/       # Vue 组件
│       ├── views/            # 页面视图
│       ├── stores/           # Pinia 状态
│       ├── services/         # API 调用
│       └── types/            # TypeScript 类型
├── docs/                     # 项目文档
├── docker-compose.yml        # Docker 编排
└── README.md
```

## 功能模块

- 👤 用户系统：注册、登录、个人资料、关注
- 📝 帖子系统：发布、编辑、删除、分页搜索
- ❤️ 互动系统：点赞、收藏、评论（楼中楼）
- 🏆 排行榜：热帖榜、社团活跃榜
- 🔔 实时通知：WebSocket 推送
- 🛠️ 管理功能：删除违规内容、封禁用户
- 📊 统计看板：在线人数、活跃数据

## Docker 部署

```bash
docker compose up -d
```

访问 http://localhost:8000/docs 查看 API 文档。
