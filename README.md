
```markdown
# 校园圈 (CampusCircle)

> 专为在校师生设计的实时交流与信息共享平台

## 技术栈

### 后端
- 框架: FastAPI (Python 3.13+)
- ORM: SQLAlchemy 2.0 (异步)
- 数据库: SQLite (开发) / aiosqlite
- 缓存: Redis (异步)
- 认证: JWT (python-jose)

### 前端
- 框架: Vue 3 + TypeScript
- UI 库: Element Plus
- 构建工具: Vite
- 状态管理: Pinia
- 路由: Vue Router 4
- HTTP 客户端: Axios

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

- 用户系统：注册、登录、个人资料（含头像上传）、关注/取关
- 帖子系统：发布（支持 Markdown 图片）、编辑、删除、分页列表、标签筛选、全文搜索
- 互动系统：点赞、收藏、评论（楼中楼）、实时通知推送
- 排行榜：热帖榜（按标签筛选）、社团活跃榜
- 社团中心：创建社团、加入/退出、社团成员列表、社团专属帖子/活动
- 活动模块：发布活动、报名/取消报名、查看参与者列表、按社团筛选
- 失物招领：发布丢失/拾到物品、标记已找回、自动过期（7天）
- 实时通知：WebSocket 连接，新评论/点赞/关注即时推送，未读计数
- 管理后台（管理员/超级管理员）：
  - 数据概览：总用户数/帖子数/社团数/活动数/失物招领数，近7天发帖趋势图表，社团活跃度图表
  - 用户管理：搜索、修改角色、封禁/解封（超级管理员可设置管理员）
  - 内容管理：删除任意帖子、评论、活动、失物招领、社团

## Docker 部署

```bash
# 构建并启动前后端容器
进入到有docker-compose.yml的目录下  

docker compose up -d

# 访问前端页面（默认端口 3000）
http://localhost:3000
# 访问 API 文档 http://localhost:8000/docs
```

![登录页面](/docs/images/1.png)
![帖子列表](/docs/images/2.png)
![帖子详情](/docs/images/3.png)
![社团中心](/docs/images/4.png)
![活动列表](/docs/images/5.png)
![失物招领](/docs/images/6.png)
![排行榜](/docs/images/7.png)
![管理后台](/docs/images/8.png)
