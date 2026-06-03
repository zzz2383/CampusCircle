<template>
    <div class="event-list-container">
        <div class="header">
            <el-button link @click="router.back()">
                <el-icon>
                    <ArrowLeft />
                </el-icon> 返回
            </el-button>
            <div class="logo">校园圈 · 活动中心</div>
        </div>

        <div class="filter-bar">
            <el-input v-model="searchKeyword" placeholder="搜索活动标题" clearable style="width: 240px" @clear="handleSearch"
                @keyup.enter="handleSearch">
                <template #prefix><el-icon>
                        <Search />
                    </el-icon></template>
            </el-input>
        </div>

        <div v-if="store.loading && store.events.length === 0" class="loading-state">
            <el-skeleton :rows="5" animated />
        </div>
        <div v-else-if="filteredEvents.length === 0" class="empty-state">
            <el-empty description="暂无活动" />
        </div>
        <div v-else>
            <div v-for="event in filteredEvents" :key="event.id" class="event-card" @click="goToDetail(event.id)">
                <div class="event-title">{{ event.title }}</div>
                <div class="event-desc">{{ event.description }}</div>
                <div class="event-meta">
                    <span><el-icon>
                            <Location />
                        </el-icon> {{ event.location || '待定' }}</span>
                    <span><el-icon>
                            <Calendar />
                        </el-icon> {{ formatDate(event.start_time) }}</span>
                    <span><el-icon>
                            <User />
                        </el-icon> {{ event.participant_count || 0 }} / {{ event.max_participants || '不限' }}</span>
                </div>
                <div class="event-stats">
                    <span v-if="event.is_registered" class="status-badge registered">已报名</span>
                    <span v-else-if="event.max_participants && event.participant_count >= event.max_participants"
                        class="status-badge full">已满员</span>
                    <span v-else class="status-badge available">可报名</span>
                </div>
            </div>
            <div v-if="store.hasMore" class="load-more">
                <el-button @click="store.loadMore" :loading="store.loading" type="primary" plain>加载更多</el-button>
            </div>
        </div>

        <el-button class="float-btn" type="primary" circle @click="openCreateDialog">
            <el-icon>
                <Plus />
            </el-icon>
        </el-button>

        <!-- 创建活动对话框 -->
        <el-dialog v-model="createDialogVisible" title="创建活动" width="550px" destroy-on-close>
            <el-form :model="eventForm" label-position="top">
                <el-form-item label="活动标题" required>
                    <el-input v-model="eventForm.title" placeholder="例：AI 技术沙龙" maxlength="200" show-word-limit />
                </el-form-item>
                <el-form-item label="活动描述" required>
                    <el-input type="textarea" v-model="eventForm.description" rows="3" placeholder="详细介绍活动内容、流程等"
                        maxlength="1000" show-word-limit />
                </el-form-item>
                <el-form-item label="地点">
                    <el-input v-model="eventForm.location" placeholder="教学楼A101" />
                </el-form-item>
                <el-form-item label="人数上限">
                    <el-input-number v-model="eventForm.max_participants" :min="1" :max="999" placeholder="不限"
                        style="width:100%" />
                </el-form-item>
                <el-form-item label="开始时间" required>
                    <el-date-picker v-model="eventForm.start_time" type="datetime" placeholder="选择开始时间"
                        style="width:100%" value-format="YYYY-MM-DDTHH:mm:ssZ" />
                </el-form-item>
                <el-form-item label="结束时间" required>
                    <el-date-picker v-model="eventForm.end_time" type="datetime" placeholder="选择结束时间" style="width:100%"
                        value-format="YYYY-MM-DDTHH:mm:ssZ" />
                </el-form-item>
                <el-form-item label="关联社团（可选）">
                    <el-select v-model="eventForm.club_id" placeholder="选择社团" clearable style="width:100%">
                        <el-option v-for="club in clubs" :key="club.id" :label="club.name" :value="club.id" />
                    </el-select>
                </el-form-item>
            </el-form>
            <template #footer>
                <el-button @click="createDialogVisible = false">取消</el-button>
                <el-button type="primary" @click="submitCreate" :loading="submitting">创建</el-button>
            </template>
        </el-dialog>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Search, Location, Calendar, User, Plus } from '@element-plus/icons-vue'
import { useEventStore } from '@/stores/eventStore'
import { getClubs } from '@/services/club'
import type { Club } from '@/types'

const router = useRouter()
const store = useEventStore()
const searchKeyword = ref('')

const filteredEvents = computed(() => {
    if (!searchKeyword.value) return store.events
    return store.events.filter(e => e.title.toLowerCase().includes(searchKeyword.value.toLowerCase()))
})

const clubs = ref<Club[]>([])

const createDialogVisible = ref(false)
const submitting = ref(false)
const eventForm = ref({
    title: '',
    description: '',
    location: '',
    max_participants: null as number | null,
    club_id: null as number | null,
    start_time: '',
    end_time: '',
})

const handleSearch = () => {
    // 搜索已在 computed 中实现，无需额外请求
}

const goToDetail = (eventId: number) => {
    router.push(`/events/${eventId}`)
}

const openCreateDialog = () => {
    eventForm.value = {
        title: '',
        description: '',
        location: '',
        max_participants: null,
        club_id: null,
        start_time: '',
        end_time: '',
    }
    createDialogVisible.value = true
}

const submitCreate = async () => {
    if (!eventForm.value.title.trim() || !eventForm.value.description.trim()) {
        ElMessage.warning('请填写标题和描述')
        return
    }
    if (!eventForm.value.start_time || !eventForm.value.end_time) {
        ElMessage.warning('请选择起止时间')
        return
    }
    submitting.value = true
    try {
        await store.createNewEvent(eventForm.value)
        ElMessage.success('创建成功')
        createDialogVisible.value = false
    } catch (error) {
        ElMessage.error('创建失败')
    } finally {
        submitting.value = false
    }
}

const formatDate = (iso: string) => {
    const date = new Date(iso)
    return `${date.getFullYear()}/${date.getMonth() + 1}/${date.getDate()}`
}

onMounted(async () => {
    await store.fetchEvents()
    // 加载社团列表用于关联
    clubs.value = await getClubs()
})
</script>

<style scoped lang="scss">
.event-list-container {
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

.filter-bar {
    margin-bottom: 1.5rem;
}

.event-card {
    background: #fff;
    border-radius: 1rem;
    padding: 1.2rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    border: 1px solid #eef2f8;
    cursor: pointer;
    transition: all 0.2s;

    &:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
    }
}

.event-title {
    font-size: 1.2rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
}

.event-desc {
    color: #5b6e8c;
    font-size: 0.85rem;
    margin-bottom: 0.75rem;
}

.event-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
    font-size: 0.75rem;
    color: #8a9bb0;
    margin-bottom: 0.5rem;
}

.event-stats {
    margin-top: 0.5rem;
}

.status-badge {
    font-size: 0.7rem;
    padding: 0.2rem 0.6rem;
    border-radius: 20px;

    &.registered {
        background: #e0f2fe;
        color: #2c7cb0;
    }

    &.full {
        background: #fee2e2;
        color: #d9534f;
    }

    &.available {
        background: #eef2fa;
        color: #2e5bff;
    }
}

.float-btn {
    position: fixed;
    bottom: 2rem;
    right: 2rem;
    width: 56px;
    height: 56px;
    border-radius: 28px;
    box-shadow: 0 8px 20px rgba(46, 91, 255, 0.3);
}

.load-more {
    text-align: center;
    margin-top: 1rem;
}

.loading-state,
.empty-state {
    text-align: center;
    padding: 3rem;
}
</style>