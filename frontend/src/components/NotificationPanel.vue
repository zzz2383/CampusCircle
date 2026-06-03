<template>
    <div class="notification-panel" v-click-outside="closePanel">
        <div class="panel-header">
            <span>通知中心</span>
            <el-button v-if="notifications.length" link @click="handleClearAll">清空全部</el-button>
        </div>
        <div class="panel-list">
            <div v-if="loading" class="loading-state">
                <el-skeleton :rows="3" animated />
            </div>
            <div v-else-if="notifications.length === 0" class="empty-state">
                暂无通知
            </div>
            <div v-for="item in notifications" :key="item.id" class="notification-item" :class="{ unread: !item.read }"
                @click="handleItemClick(item)">
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
                    <div class="time">{{ formatTime(item.createdAt) }}</div>
                </div>
            </div>
            <div v-if="hasMore && !loading" class="load-more">
                <el-button link @click="loadMore">加载更多</el-button>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ChatDotRound, Star, User } from '@element-plus/icons-vue'
import { useNotificationStore } from '@/stores/notificationStore'

const router = useRouter()
const store = useNotificationStore()

const notifications = computed(() => store.notifications)
const loading = computed(() => store.loading)
const hasMore = computed(() => store.notifications.length < 50) // 简单判断

const formatTime = (iso: string) => {
    const date = new Date(iso)
    const diff = Date.now() - date.getTime()
    if (diff < 60000) return '刚刚'
    if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
    if (diff < 604800000) return `${Math.floor(diff / 86400000)}天前`
    return `${date.getMonth() + 1}/${date.getDate()}`
}

const handleItemClick = (item: any) => {
    if (!item.read) {
        store.markAsRead(item.id)
    }
    // 根据类型跳转
    if (item.type === 'comment' || item.type === 'like') {
        if (item.targetId) {
            router.push(`/posts/${item.targetId}`)
        } else {
            ElMessage.info('目标帖子不存在')
        }
    } else if (item.type === 'follow') {
        // 可跳转到关注者主页（后续实现）
        ElMessage.info('跳转到用户主页（演示）')
    }
    // 关闭面板（由父组件控制）
    emit('close')
}

const handleClearAll = () => {
    store.clearAll()
    ElMessage.success('已清空所有通知')
}

const loadMore = () => {
    // 分页加载（需后端支持）
    ElMessage.info('更多通知功能开发中')
}

const emit = defineEmits<{ (e: 'close'): void }>()
const closePanel = () => {
    emit('close')
}
</script>

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