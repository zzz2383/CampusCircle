\# 「校园实时论坛系统」- 全局规范约束文档



> 版本：1.0  

> 适用项目：基于 FastAPI + Vue3 + TypeScript + SQLite + Redis 的校园实时论坛系统（面向高校师生）  

> 核心原则：分层解耦、单向依赖、接口契约、测试先行、注释即文档



\---



\## 1. 项目定位与功能清单



\*\*项目名称\*\*：\*\*校园圈（CampusCircle）\*\* —— 专为在校师生设计的实时交流与信息共享平台



\*\*核心功能模块\*\*（结合校园场景）：



| 模块 | 具体功能 |

|------|----------|

| 用户系统 | 学号/工号注册（需校园邮箱验证）、登录（JWT）、个人资料（昵称、头像、院系、年级）、关注/取关、在线状态 |

| 校园资讯 | 发布官方通知（教务处、学工部）、社团活动招募、讲座信息、失物招领 |

| 帖子系统 | 发布图文帖（支持话题标签 #课程# #社团# #求助#）、编辑、删除、分页列表、全文搜索 |

| 互动系统 | 点赞/取消点赞、收藏/取消收藏、评论（楼中楼）、@ 提及同学 |

| 实时通知 | 收到评论、被点赞、被关注、活动报名提醒时 WebSocket 推送 |

| 实时排行榜 | 今日热帖榜（按点赞+评论+浏览热度）、社团活跃榜（按发帖量）、学霸帮帮榜（按解答数） |

| 管理功能 | 管理员（辅导员或学生干部）删除违规帖子/评论、封禁用户（Redis 黑名单） |

| 统计看板 | 实时在线人数（区分学生/教师）、今日新增帖子数、本周活跃社团 |



\---



\## 2. 分层架构设计



系统自顶向下分为 \*\*4 个独立层次\*\*，每层仅允许调用其\*\*直接下层\*\*的接口，禁止跨层或反向调用。



```

┌─────────────────────────────────────────────┐

│              表现层 (Presentation)           │

│  - Vue3 前端页面 (浏览器)                    │

│  - FastAPI HTTP 路由 \& WebSocket 入口        │

│  调用: 业务层接口                            │

└─────────────────────────────────────────────┘

&#x20;                    ↓ (仅单向)

┌─────────────────────────────────────────────┐

│              业务层 (Business)               │

│  - 用户服务、帖子服务、互动服务、通知服务等   │

│  - 实现核心业务逻辑 \& 编排 Redis/SQLite 操作  │

│  调用: 数据访问层接口 + Redis 访问层接口       │

└─────────────────────────────────────────────┘

&#x20;                    ↓ (仅单向)

┌─────────────────────────────────────────────┐

│            数据访问层 (Data Access)           │

│  - SQLite DAO (UserDAO, PostDAO, ...)       │

│  - Redis Repository (LikeRepo, RankRepo, ..)│

│  调用: 基础设施层 (SQLite/Redis 客户端)       │

└─────────────────────────────────────────────┘

&#x20;                    ↓ (仅单向)

┌─────────────────────────────────────────────┐

│           基础设施层 (Infrastructure)         │

│  - SQLite 连接池                             │

│  - Redis 连接池 \& Pub/Sub 客户端             │

│  - 配置管理、日志、异常基类                   │

└─────────────────────────────────────────────┘

```



\*\*强制规则\*\*：

\- 业务层\*\*不能\*\*直接操作 SQLite 或 Redis 的原始连接，必须通过数据访问层的接口。

\- 表现层\*\*不能\*\*包含任何业务逻辑（如计算热度、判断权限），只能做参数校验、序列化、路由转发。

\- 每一层暴露的功能都必须通过\*\*接口（抽象类/协议）\*\*定义，实现类隐藏细节。



\---



\## 3. 各层职责与接口定义规范



\### 3.1 表现层 (Presentation)



| 组件类型 | 职责 | 接口定义方式 |

|---------|------|-------------|

| FastAPI 路由 | 解析 HTTP 请求，调用一个\*\*业务层方法\*\*，返回标准 JSON | Pydantic 模型 + `APIRouter` |

| WebSocket 处理器 | 管理连接，转发 Redis Pub/Sub 消息 | 异步函数 + `@app.websocket` |

| 前端 Vue 组件 | 渲染 UI，调用后端 API，管理局部状态 | TypeScript interface + Pinia store |



\*\*接口示例（后端）\*\*：

```python

\# 业务层接口必须通过依赖注入

@router.post("/campus/posts/{id}/like")

async def like\_post(

&#x20;   id: int,

&#x20;   current\_user: User = Depends(get\_current\_user),

&#x20;   like\_service: LikeService = Depends(get\_like\_service)

) -> JSONResponse:

&#x20;   """表现层仅做参数提取和响应封装"""

&#x20;   result = await like\_service.like\_post(current\_user.id, id)

&#x20;   return success\_response(result)

```



\### 3.2 业务层 (Business)



每个业务模块对应一个 \*\*Service 类\*\*，类中的每个公共方法代表一个\*\*独立功能\*\*。



| 业务模块 | 核心功能 | 接口方法示例 |

|---------|---------|-------------|

| `UserService` | 校园邮箱注册、登录、获取在线状态、关注/取关、认证学生/教师身份 | `register(student\_id, email, password)` → `UserDTO` |

| `PostService` | 发布校园帖（带话题标签）、删帖、查询最新列表、查询热榜、按标签筛选 | `create\_post(user\_id, title, content, tags)` → `PostDTO` |

| `LikeService` | 点赞、取消点赞、查询点赞状态 | `like\_post(user\_id, post\_id)` → `bool` |

| `RankService` | 获取热帖排行榜、获取社团活跃榜、更新热度分 | `get\_hot\_posts(limit, tag)` → `List\[PostDTO]` |

| `NotificationService` | 发送实时通知（评论、点赞、活动提醒）、获取未读通知 | `send\_notification(user\_id, data)` → `void` |



\*\*约束\*\*：

\- 每个 Service 方法必须定义\*\*输入和输出的 Pydantic 模型\*\*（DTO）。

\- Service 内部\*\*不允许\*\*出现 SQL 语句或 Redis 命令字符串，只能调用 DAO / Repository 接口。

\- 事务边界由业务层控制（如需跨表操作，使用 SQLite 事务）。



\### 3.3 数据访问层 (Data Access)



分为 \*\*SQLite DAO\*\* 和 \*\*Redis Repository\*\*，每个实体对应一个 DAO/Repository。



\*\*SQLite DAO 示例\*\*：

```python

class PostDAO(ABC):

&#x20;   @abstractmethod

&#x20;   async def insert(self, post: PostCreate) -> int: ...

&#x20;   @abstractmethod

&#x20;   async def get\_by\_id(self, post\_id: int) -> Optional\[PostModel]: ...

&#x20;   @abstractmethod

&#x20;   async def list\_latest\_by\_tag(self, tag: str, offset: int, limit: int) -> List\[PostModel]: ...

```



\*\*Redis Repository 示例\*\*：

```python

class LikeRepository(ABC):

&#x20;   @abstractmethod

&#x20;   async def add\_like(self, post\_id: int, user\_id: int) -> int: ...  # 返回新点赞数

&#x20;   @abstractmethod

&#x20;   async def remove\_like(self, post\_id: int, user\_id: int) -> int: ...

&#x20;   @abstractmethod

&#x20;   async def is\_liked(self, post\_id: int, user\_id: int) -> bool: ...

```



\*\*强制规则\*\*：

\- DAO/Repository 只做\*\*单一数据源\*\*的增删改查，不包含业务逻辑。

\- 每个方法必须有明确的\*\*单元测试\*\*（使用内存 SQLite 和 fakeredis）。



\### 3.4 基础设施层



提供可复用的底层组件，不暴露给表现层直接调用（仅数据访问层使用）。



| 组件 | 接口 |

|------|------|

| 数据库连接池 | `get\_sqlite\_connection()` -> `async with conn:` |

| Redis 客户端 | `get\_redis() -> Redis` (单例) |

| 日志记录器 | `logger = get\_logger(\_\_name\_\_)` |

| 配置管理 | `settings = Settings()` (pydantic-settings) |



\---



\## 4. 接口契约与功能映射（校园版）



每个功能在系统中由 \*\*唯一的接口路径\*\* 标识，且满足：一个接口只做一件事，命名遵循 `动词+名词`，输入输出用 Pydantic 模型定义。



\*\*功能清单\*\*（重点标注 Redis 使用场景）：



| 功能编号 | 功能名称 | 所属层 | 接口签名 | Redis 使用点 |

|---------|---------|--------|----------|--------------|

| F01 | 学生注册 | 业务层 | `register(student\_id, email, pwd) -> UserDTO` | 无（仅写 SQLite） |

| F02 | 用户登录 | 业务层 | `login(student\_id, pwd) -> TokenDTO` | 设置在线状态 String |

| F03 | 发布校园帖 | 业务层 | `create\_post(user\_id, title, content, tags) -> PostDTO` | 限流检查 + LPUSH 时间线 |

| F04 | 点赞帖子 | 业务层 | `like\_post(user\_id, post\_id) -> LikeResultDTO` | SADD + INCR + ZINCRBY |

| F05 | 获取热帖榜（按标签） | 业务层 | `get\_hot\_posts(tag, limit) -> List\[PostDTO]` | ZREVRANGE（不同标签不同 Sorted Set） |

| F06 | 获取社团活跃榜 | 业务层 | `get\_club\_rank(limit) -> List\[ClubDTO]` | ZREVRANGE 社团发帖数 |

| F07 | 发送实时通知 | 业务层 | `send\_notification(user\_id, data)` | Pub/Sub |

| F08 | 失物招领自动过期 | 业务层 | `create\_lost\_item(...)` | 设置过期时间（EXPIRE） |

| F09 | 接口限流（防刷） | 业务层（中间件） | `rate\_limit(ip, action)` | String + EXPIRE |

| F10 | 黑名单封禁 | 业务层 | `ban\_user(admin\_id, user\_id, duration)` | SETEX 黑名单 |



\---



\## 5. 测试规范（TDD 先行）



\### 5.1 核心原则

\*\*每个功能实现前，必须先编写其测试用例\*\*（红灯 → 绿灯 → 重构）。



\### 5.2 测试分层与工具



| 测试层级 | 测试对象 | 工具 | 独立运行要求 |

|---------|---------|------|-------------|

| \*\*单元测试\*\* | 单个 Service 方法 / DAO 方法 / Repository 方法 | `pytest` + `pytest-asyncio` | Mock 掉所有外部依赖（数据库、Redis 用 fakeredis / 内存 SQLite） |

| \*\*集成测试\*\* | 数据访问层 + 真实 SQLite/Redis（测试专用实例） | `pytest` + `tempfile`（SQLite） + `testcontainers`（Redis） | 使用独立数据库，每次测试后清空 |

| \*\*端到端测试\*\* | 完整 HTTP API（FastAPI TestClient） | `httpx.AsyncClient` | 启动完整应用，但使用测试数据库和 Redis |



\### 5.3 测试覆盖率要求

\- 核心业务模块（点赞、排行榜、限流、通知）的行覆盖率 ≥ 90%

\- 所有 DAO/Repository 方法的行覆盖率 = 100%



\### 5.4 测试文件组织

```

tests/

├── unit/

│   ├── business/

│   │   ├── test\_like\_service.py

│   │   ├── test\_rank\_service.py

│   │   └── test\_notification\_service.py

│   └── data\_access/

│       ├── test\_post\_dao.py

│       └── test\_like\_repo.py

├── integration/

│   ├── test\_post\_crud\_with\_real\_sqlite.py

│   └── test\_redis\_operations.py

└── e2e/

&#x20;   └── test\_api\_endpoints.py

```



\### 5.5 单元测试示例（先写测试，后写实现）



```python

\# tests/unit/business/test\_like\_service.py

import pytest

from unittest.mock import AsyncMock

from app.business.like\_service import LikeService

from app.data\_access.like\_repository import LikeRepository



@pytest.mark.asyncio

async def test\_like\_post\_success():

&#x20;   # Arrange

&#x20;   like\_repo\_mock = AsyncMock(spec=LikeRepository)

&#x20;   like\_repo\_mock.add\_like.return\_value = 42

&#x20;   service = LikeService(like\_repo=like\_repo\_mock)

&#x20;   

&#x20;   # Act

&#x20;   result = await service.like\_post(user\_id=1, post\_id=100)

&#x20;   

&#x20;   # Assert

&#x20;   assert result.like\_count == 42

&#x20;   assert result.is\_liked is True

&#x20;   like\_repo\_mock.add\_like.assert\_called\_once\_with(100, 1)

```



\---



\## 6. 注释规范（详细说明逻辑与过程）



每个\*\*公共接口\*\*必须包含以下内容的文档字符串：



1\. \*\*功能描述\*\*：一句话说明该功能做什么。

2\. \*\*实现逻辑\*\*：分步骤描述关键流程（尤其是 Redis 数据结构的选择和操作）。

3\. \*\*调用链路\*\*：标注会调用的下层接口。

4\. \*\*参数说明\*\*：类型、范围、是否可选。

5\. \*\*返回值说明\*\*：成功/失败时的返回结构。

6\. \*\*异常说明\*\*：可能抛出的异常类型及触发条件。

7\. \*\*测试用例关联\*\*：对应的测试函数名称。



\*\*代码示例\*\*（校园论坛点赞功能）：



```python

async def like\_post(self, user\_id: int, post\_id: int) -> LikeResultDTO:

&#x20;   """

&#x20;   功能：点赞一篇校园帖子（如果未点赞则点赞，已点赞则幂等返回当前状态）



&#x20;   实现逻辑：

&#x20;       1. 调用 LikeRepository.add\_like()，该方法内部使用 Redis SADD 将 user\_id 加入集合

&#x20;       2. 若 SADD 返回 1（新增成功），则通过 INCR 增加点赞计数，并通过 ZINCRBY 给热帖榜（对应话题标签）加 2 分

&#x20;       3. 若 SADD 返回 0（已点赞），则直接返回当前点赞数而不重复计数

&#x20;       4. 异步调用 NotificationService 发送 Redis Pub/Sub 消息通知帖子作者



&#x20;   调用链路：

&#x20;       - LikeRepository.add\_like(post\_id, user\_id)

&#x20;       - RankService.increment\_hot\_score(post\_id, tag, increment=2)  (仅首次)

&#x20;       - NotificationService.notify\_author(post\_id, "like")



&#x20;   参数：

&#x20;       user\_id: 点赞者 ID (int, 必须存在于 users 表)

&#x20;       post\_id: 帖子 ID (int, 必须存在于 posts 表)



&#x20;   返回值：

&#x20;       LikeResultDTO: 包含 is\_liked (True), like\_count (当前总点赞数)



&#x20;   异常：

&#x20;       - PostNotFoundError: 帖子不存在

&#x20;       - UserNotFoundError: 用户不存在



&#x20;   测试用例：

&#x20;       - test\_like\_post\_success

&#x20;       - test\_like\_post\_twice\_idempotent

&#x20;       - test\_like\_post\_not\_exist\_post

&#x20;   """

&#x20;   # 实现代码...

```



\---



\## 7. 开发流程规范（TDD 驱动）



每个功能（接口）的开发必须遵循以下 5 个步骤：



| 步骤 | 动作 | 输出产物 |

|------|------|----------|

| 1 | 定义接口（抽象类 + DTO 模型） | `interfaces.py` 中的抽象方法定义 |

| 2 | \*\*编写单元测试\*\*（先红灯） | `tests/unit/.../test\_xxx.py` |

| 3 | 实现接口（填充逻辑） | 具体类文件（如 `like\_service\_impl.py`） |

| 4 | 运行测试，直到绿灯 | 测试报告 |

| 5 | 重构并保证测试依然通过 | 优化后的代码 |



\*\*代码审查重点\*\*：

\- 是否每个公共方法都有文档字符串？

\- 是否每个方法只做一层抽象？

\- 是否存在跨层调用（如 Service 中直接调用 Redis 命令）？

\- 单元测试是否覆盖了正常路径和至少 2 种异常路径？



\---



\## 8. 项目目录结构（强制）



```

campus\_circle/

├── backend/

│   ├── app/

│   │   ├── presentation/

│   │   │   ├── api/           (FastAPI 路由：auth, posts, likes, rank, notifications)

│   │   │   └── websocket/     (WebSocket 处理器)

│   │   ├── business/

│   │   │   ├── interfaces/    (抽象 Service 接口)

│   │   │   └── impl/          (Service 实现)

│   │   ├── data\_access/

│   │   │   ├── sqlite\_dao/    (DAO 接口 + 实现)

│   │   │   └── redis\_repo/    (Repository 接口 + 实现)

│   │   ├── infrastructure/

│   │   │   ├── db.py          (SQLite 连接池)

│   │   │   ├── redis\_client.py

│   │   │   └── config.py

│   │   ├── models/            (Pydantic DTO + SQLAlchemy 模型)

│   │   └── main.py

│   └── tests/                 (如上测试结构)

├── frontend/

│   ├── src/

│   │   ├── components/        (Vue 组件：帖子列表、排行榜、通知面板)

│   │   ├── stores/            (Pinia 状态管理)

│   │   ├── services/          (API 调用，每个 service 对应一个后端模块)

│   │   └── types/             (自动生成的 TypeScript 接口)

│   └── tests/                 (Vitest 单元测试)

├── docker-compose.yml         (包含 FastAPI, Redis, SQLite 服务)

└── README.md

```



\---



\## 9. 版本管理与文档同步



\- 每次提交前必须运行全部测试并通过。

\- 所有 API 变更必须同步更新 `docs/api/openapi.json`（由 FastAPI 自动生成，提交时需确认）。

\- 新增 Redis 数据结构使用场景时，需在 `docs/redis\_design.md` 中记录 key 命名规范、过期策略、数据类型。



\*\*Key 命名规范（校园版）\*\*：

```

{业务域}:{实体}:{操作}:{标识}

示例：

\- post:like:set:123            # 帖子123的点赞用户集合

\- hot\_posts:day:tag:课程        # 课程标签下的日榜

\- club:post:count:计算机协会     # 社团发帖数

\- online:user:456              # 用户456在线状态

\- lost:item:789                # 失物招领条目（带过期时间）

```



\---



\## 10. 校园特色功能补充说明（Redis 练习强化）



| 校园场景 | Redis 使用方式 | 练习目的 |

|---------|----------------|----------|

| 失物招领自动下架 | 发布时 `SETEX lost:item:{id} 604800 data`，7天自动过期 | String + EXPIRE |

| 课程话题热度榜 | 每个课程标签一个 Sorted Set，按点赞+评论数排序 | Sorted Set 分片 |

| 社团活跃度排名 | 社团每发一帖，`ZINCRBY club:active 1 {club\_id}` | Sorted Set 实时更新 |

| 活动报名人数实时统计 | `INCR event:signup:{event\_id}`，前端轮询或 WebSocket 推送 | String 计数器 |

| 防止同一学生重复报名 | `SADD event:participants:{event\_id} {user\_id}` | Set 去重 |

| 教师认证状态缓存 | `SETEX teacher:verify:{user\_id} 3600 "pending"` | 临时状态缓存 |



\---

每次对话后都必须追加，happy coding



