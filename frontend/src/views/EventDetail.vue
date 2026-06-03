<template>
    <div class="event-detail-container">
        <div class="header">
            <el-button link @click="router.back()">
                <el-icon>
                    <ArrowLeft />
                </el-icon> 返回
            </el-button>
            <div class="logo">活动详情</div>
        </div>

        <div v-if="store.loading" class="loading-state">
            <el-skeleton :rows="8" animated />
        </div>
        <div v-else-if="!store.currentEvent" class="empty-state">
            <el-empty description="活动不存在" />
        </div>
        <div v-else>
            <div class="info-card">
                <div class="event-title">{{ store.currentEvent.title }}</div>
                <div class="event-desc">{{ store.currentEvent.description }}</div>
                <div class="event-meta">
                    <span><el-icon>
                            <Location />
                        </el-icon> {{ store.currentEvent.location || '待定' }}</span>
                    <span><el-icon>
                            <Calendar />
                        </el-icon> 开始：{{ formatDateTime(store.currentEvent.start_time) }}</span>
                    <span><el-icon>
                            <Calendar />
                        </el-icon> 结束：{{ formatDateTime(store.currentEvent.end_time) }}</span>
                    <span><el-icon>
                            <User />
                        </el-icon> 报名 {{ store.currentEvent.participant_count || 0 }} / {{
                            store.currentEvent.max_participants || '不限' }}</span>
                    <span v-if="store.currentEvent.club_name"><el-icon>
                            <Flag />
                        </el-icon> {{ store.currentEvent.club_name }}</span>
                </div>
                <div class="action-buttons">
                    <el-button
                        v-if="!store.currentEvent.is_registered && (!store.currentEvent.max_participants || store.currentEvent.participant_count < store.currentEvent.max_participants)"
                        type="primary" @click="handleRegister">报名活动</el-button>
                    <el-button v-else-if="store.currentEvent.is_registered" type="danger" plain
                        @click="handleCancel">取消报名</el-button>
                    <el-button v-else disabled type="info">已满员</el-button>
                </div>
            </div>

            <div class="participants-section">
                <h4>参与成员 ({{ store.participants.length }})</h4>
                <div v-if="store.participantsLoading" class="loading-small">加载中...</div>
                <div v-else-if="store.participants.length === 0" class="empty-small">暂无成员报名</div>
                <div v-else>
                    <div v-for="p in store.participants" :key="p.id" class="participant-item">
                        <el-avatar :size="28">{{ p.user_nickname.charAt(0) }}</el-avatar>
                        <span>{{ p.user_nickname }}</span>
                        <span class="participant-time">{{ formatDate(p.created_at) }}</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Location, Calendar, User, Flag } from '@element-plus/icons-vue'
import { useEventStore } from '@/stores/eventStore'
import { useUserStore } from '@/stores/userStore'

const route = useRoute()
const router = useRouter()
const store = useEventStore()
const userStore = useUserStore()

const eventId = Number(route.params.id)

const handleRegister = async () => {
    if (!userStore.isLoggedIn) {
        ElMessage.warning('请先登录')
        router.push('/auth')
        return
    }
    try {
        await store.registerForEvent(eventId)
        ElMessage.success('报名成功')
    } catch (error: any) {
        if (error.response?.data?.code === 'EVENT_FULL') {
            ElMessage.error('活动已满员')
        } else {
            ElMessage.error('报名失败')
        }
    }
}

const handleCancel = async () => {
    try {
        await ElMessageBox.confirm('确定取消报名吗？', '提示', { type: 'warning' })
        await store.cancelRegistration(eventId)
        ElMessage.success('已取消报名')
    } catch (error) {
        if (error !== 'cancel') ElMessage.error('操作失败')
    }
}

const formatDate = (iso: string) => {
    const date = new Date(iso)
    return `${date.getFullYear()}/${date.getMonth() + 1}/${date.getDate()}`
}
const formatDateTime = (iso: string) => {
    const date = new Date(iso)
    return `${date.getFullYear()}/${date.getMonth() + 1}/${date.getDate()} ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
}

onMounted(() => {
    store.fetchEventDetail(eventId)
})
</script>

<style scoped lang="scss">
.event-detail-container {
    max-width: 900px;
    margin: 0 auto;
    padding: 1.5rem;
}

.header {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1.5rem;

    .logo {
        font-size: 1.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        background-clip: text;
        -webkit-background-clip: text;
        color: transparent;
    }
}

.info-card {
    background: #fff;
    border-radius: 1.25rem;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);

    .event-title {
        font-size: 1.6rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }

    .event-desc {
        color: #5b6e8c;
        margin-bottom: 1rem;
        line-height: 1.5;
    }

    .event-meta {
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
        font-size: 0.8rem;
        color: #8a9bb0;
        margin-bottom: 1.5rem;
    }

    .action-buttons {
        text-align: center;
    }
}

.participants-section {
    background: #fff;
    border-radius: 1.25rem;
    padding: 1.5rem;

    h4 {
        margin-bottom: 1rem;
    }
}

.participant-item {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    padding: 0.6rem 0;
    border-bottom: 1px solid #eef2f8;

    .participant-time {
        margin-left: auto;
        font-size: 0.7rem;
        color: #8a9bb0;
    }
}

.loading-state,
.empty-state {
    text-align: center;
    padding: 3rem;
}

.loading-small,
.empty-small {
    text-align: center;
    padding: 1rem;
    color: #8a9bb0;
}
</style>