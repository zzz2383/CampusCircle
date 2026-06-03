<template>
    <div class="notification-panel">
        <div class="panel-header">
            <span>通知中心</span>
            <el-button v-if="notifications.length" link @click="handleMarkAllRead">全部已读</el-button>
        </div>
        <div class="panel-list">
            <div v-if="loading" class="loading-state">
                <el-skeleton :rows="3" animated />
            </div>
            <div v-else-if="notifications.length === 0" class="empty-state">
                暂无通知
            </div>
            <div v-for="item in notifications" :key="item.id" class="notification-item"
                @click="handleNotificationClick(item)">
                <div class="icon">
                    <el-icon v-if="item.type === 'comment'">
                        <ChatDotRound />
                    </el-icon>
                    <el-icon v-else-if="item.type === 'like'">
                        <Star />
                    </el-icon>
                    <el-icon v-else>
                        <User />
                    </el-icon>
                </div>
                <div class="content">
                    <div class="text">{{ item.content }}</div>
                    <div class="time">{{ formatTime(item.timestamp) }}</div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ChatDotRound, Star, User } from '@element-plus/icons-vue'
import { useNotificationStore } from '@/stores/notificationStore'

const router = useRouter()
const store = useNotificationStore()

const notifications = computed(() => store.notifications)
const loading = computed(() => store.loading)

const formatTime = (iso: string) => {
    const date = new Date(iso)
    const diff = Date.now() - date.getTime()
    if (diff < 60000) return '刚刚'
    if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
    if (diff < 604800000) return `${Math.floor(diff / 86400000)}天前`
    return `${date.getMonth() + 1}/${date.getDate()}`
}

const handleNotificationClick = (item: any) => {
    // 跳转到对应资源（帖子详情页）
    if (item.post_id) {
        router.push(`/posts/${item.post_id}`)
    } else {
        // 关注类型可能没有 post_id，跳转到用户主页（后续实现）
        ElMessage.info('跳转用户主页（开发中）')
    }
    // 通知被点击后，可考虑本地标记为已读（但后端无单条标记接口，先不做）
}

const handleMarkAllRead = async () => {
    await store.markAllAsRead()
    ElMessage.success('已全部标记为已读')
    // 重新拉取列表（可选）
    await store.fetchNotifications()
}

// 组件挂载时拉取通知列表
onMounted(() => {
    store.fetchNotifications()
})

// 由于组件可能在面板打开时才挂载，但为了确保数据最新，每次打开时调用父组件传递的刷新？目前直接在 onMounted 中拉取一次。
// 如果有实时推送，push 时会自动更新，不需要额外操作。
</script>

<style scoped lang="scss">
/* 样式与之前相同，略 */
</style>
<style scoped lang="scss">
.notification-panel {
    position: absolute;
    top: 50px;
    right: 0;
    width: 360px;
    background: #fff;
    border-radius: 16px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
    border: 1px solid #eef2f8;
    z-index: 1000;
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

.panel-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 16px;
    border-bottom: 1px solid #eef2f8;
    font-weight: 600;
}

.panel-list {
    max-height: 400px;
    overflow-y: auto;
}

.notification-item {
    display: flex;
    gap: 12px;
    padding: 12px 16px;
    border-bottom: 1px solid #f0f2f6;
    cursor: pointer;
    transition: background 0.2s;

    &:hover {
        background: #f8fafc;
    }

    &.unread {
        background: #f0f7ff;
    }

    .icon {
        width: 36px;
        height: 36px;
        background: #eef2fa;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #2e5bff;
    }

    .content {
        flex: 1;

        .text {
            font-size: 0.85rem;
            margin-bottom: 4px;
        }

        .time {
            font-size: 0.7rem;
            color: #8a9bb0;
        }
    }
}

.empty-state,
.loading-state {
    text-align: center;
    padding: 2rem;
    color: #8a9bb0;
}

.load-more {
    text-align: center;
    padding: 10px;
}
</style>