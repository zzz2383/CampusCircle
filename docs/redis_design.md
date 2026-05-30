# Redis 数据结构设计方案

## Key 命名规范

```
{业务域}:{实体}:{操作}:{标识}
```

### 命名示例

| Key | 用途 | 数据类型 | 过期策略 |
|-----|------|---------|---------|
| `post:like:set:123` | 帖子 123 的点赞用户集合 | Set | 无（持久） |
| `post:like:count:123` | 帖子 123 的点赞计数 | String | 无 |
| `hot:posts:day:课程` | 课程标签下的日榜 | Sorted Set | 每天 00:00 过期 |
| `hot:posts:day:社团` | 社团标签下的日榜 | Sorted Set | 每天 00:00 过期 |
| `club:active` | 社团活跃度排名 | Sorted Set | 每周重置 |
| `online:user:456` | 用户 456 在线状态 | String | 5 分钟过期 |
| `lost:item:789` | 失物招领条目 | String | 7 天过期 |
| `notification:user:456` | 用户 456 的通知列表 | List | 保留最近 100 条 |
| `blacklist:user:456` | 封禁用户 | String | 按封禁时长设置过期 |
| `rate:limit:ip:192.168.x.x` | 接口限流 | String | 按窗口时间过期 |
| `event:signup:1` | 活动 1 报名人数 | String | 活动结束后过期 |
| `event:participants:1` | 活动 1 的参与者集合 | Set | 活动结束后过期 |
| `teacher:verify:456` | 教师认证状态 | String | 1 小时过期 |

## 数据结构选择说明

### Set（集合）
- **适用场景**：点赞用户集合、活动参与者去重
- **原因**：利用 SADD 做去重，SISMEMBER 做快速判断

### Sorted Set（有序集合）
- **适用场景**：排行榜（热帖、社团活跃度）
- **原因**：ZINCRBY 支持实时更新分数，ZREVRANGE 支持按分取 top N

### String（字符串）
- **适用场景**：计数器、状态标记、缓存
- **原因**：INCR/DECR 原子操作，SETEX 支持过期时间

### List（列表）
- **适用场景**：时间线、通知列表
- **原因**：LPUSH 添加新通知，LRANGE 分页读取

### Pub/Sub（发布订阅）
- **适用场景**：实时通知推送
- **原因**：解耦通知发送方和接收方，WebSocket 订阅频道

## 排行榜更新策略

1. 点赞时：通过 `ZINCRBY hot:posts:day:{tag} 2 {post_id}` 增加热度分
2. 评论时：通过 `ZINCRBY hot:posts:day:{tag} 3 {post_id}` 增加热度分
3. 浏览时：通过 `ZINCRBY hot:posts:day:{tag} 1 {post_id}` 增加热度分
4. 每日 00:00 自动重置日榜（Redis EXPIRE）
