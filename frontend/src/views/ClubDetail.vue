<template>
    <div class="club-detail-container">
        <div class="header">
            <el-button link @click="router.back()">
                <el-icon>
                    <ArrowLeft />
                </el-icon> 返回
            </el-button>
            <div class="logo">社团详情</div>
        </div>

        <div v-if="store.loading" class="loading-state">
            <el-skeleton :rows="8" animated />
        </div>
        <div v-else-if="!store.currentClub" class="empty-state">
            <el-empty description="社团不存在" />
        </div>
        <div v-else>
            <!-- 社团基本信息 -->
            <div class="info-card">
                <div class="club-name">{{ store.currentClub.name }}</div>
                <div class="club-desc">{{ store.currentClub.description || '暂无简介' }}</div>
                <div class="club-meta">
                    <span><el-icon>
                            <User />
                        </el-icon> 成员 {{ store.members.length }}</span>
                    <span><el-icon>
                            <Calendar />
                        </el-icon> 创建于 {{ formatDate(store.currentClub.created_at) }}</span>
                </div>
                <div class="action-buttons">
                    <el-button v-if="!store.isMember" type="primary" @click="handleJoin">加入社团</el-button>
                    <el-button v-else type="danger" plain @click="handleLeave">退出社团</el-button>
                </div>
            </div>

            <!-- Tab 切换：成员、帖子、活动 -->
            <el-tabs v-model="activeTab" class="detail-tabs">
                <el-tab-pane label="成员列表" name="members">
                    <div v-if="store.members.length === 0" class="empty-tab">暂无成员</div>
                    <div v-else>
                        <div v-for="member in store.members" :key="member.id" class="member-item">
                            <el-avatar :size="32">{{ member.user_nickname.charAt(0) }}</el-avatar>
                            <span class="member-name">{{ member.user_nickname }}</span>
                            <span class="member-role">{{ member.role === 'founder' ? '创始人' : member.role === 'admin' ?
                                '管理员' : '成员' }}</span>
                            <span class="member-time">{{ formatDate(member.joined_at) }}</span>
                        </div>
                    </div>
                </el-tab-pane>

                <el-tab-pane label="社团帖子" name="posts">
                    <div v-if="store.posts.length === 0" class="empty-tab">暂无帖子</div>
                    <div v-else>
                        <div v-for="post in store.posts" :key="post.id" class="post-item" @click="goToPost(post.id)">
                            <div class="post-title">{{ post.title }}</div>
                            <div class="post-meta">
                                {{ post.author_nickname }} · {{ formatTime(post.created_at) }} · {{ post.like_count }}
                                点赞
                            </div>
                        </div>
                        <!-- 分页加载更多（暂简化） -->
                    </div>
                </el-tab-pane>

                <el-tab-pane label="社团活动" name="events">
                    <div v-if="store.events.length === 0" class="empty-tab">暂无活动</div>
                    <div v-else>
                        <div v-for="event in store.events" :key="event.id" class="event-item">
                            <div class="event-title">{{ event.title }}</div>
                            <div class="event-desc">{{ event.description }}</div>
                            <div class="event-meta">
                                <span><el-icon>
                                        <Location />
                                    </el-icon> {{ event.location || '待定' }}</span>
                                <span><el-icon>
                                        <Clock />
                                    </el-icon> {{ formatDate(event.start_time) }}</span>
                            </div>
                        </div>
                    </div>
                </el-tab-pane>
            </el-tabs>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, User, Calendar, Location, Clock } from '@element-plus/icons-vue'
import { useClubStore } from '@/stores/clubStore'
import { useUserStore } from '@/stores/userStore'

const route = useRoute()
const router = useRouter()
const store = useClubStore()
const userStore = useUserStore()

const clubId = Number(route.params.id)
const activeTab = ref('members')

const handleJoin = async () => {
    if (!userStore.isLoggedIn) {
        ElMessage.warning('请先登录')
        router.push('/auth')
        return
    }
    try {
        await store.joinClubAction(clubId)
        ElMessage.success('已加入社团')
    } catch {
        ElMessage.error('操作失败')
    }
}

const handleLeave = async () => {
    try {
        await ElMessageBox.confirm('确定要退出该社团吗？', '提示', { type: 'warning' })
        await store.leaveClubAction(clubId)
        ElMessage.success('已退出社团')
    } catch (error) {
        if (error !== 'cancel') ElMessage.error('操作失败')
    }
}

const goToPost = (postId: number) => {
    router.push(`/posts/${postId}`)
}

const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return `${date.getFullYear()}/${date.getMonth() + 1}/${date.getDate()}`
}

const formatTime = (iso: string) => {
    const date = new Date(iso)
    const diff = Date.now() - date.getTime()
    if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
    return `${date.getMonth() + 1}/${date.getDate()}`
}

onMounted(() => {
    store.fetchClubDetail(clubId)
})
</script>

<style scoped lang="scss">
.club-detail-container {
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

    .club-name {
        font-size: 1.6rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }

    .club-desc {
        color: #5b6e8c;
        margin-bottom: 1rem;
    }

    .club-meta {
        display: flex;
        gap: 1rem;
        font-size: 0.8rem;
        color: #8a9bb0;
        margin-bottom: 1.5rem;
    }

    .action-buttons {
        text-align: center;
    }
}

.detail-tabs {
    background: #fff;
    border-radius: 1.25rem;
    padding: 0 1rem;
}

.member-item {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 0.8rem 0;
    border-bottom: 1px solid #eef2f8;

    .member-name {
        flex: 1;
        font-weight: 500;
    }

    .member-role {
        font-size: 0.7rem;
        color: #2e5bff;
        background: #eef2fa;
        padding: 0.2rem 0.5rem;
        border-radius: 12px;
    }

    .member-time {
        font-size: 0.7rem;
        color: #8a9bb0;
    }
}

.post-item,
.event-item {
    padding: 1rem 0;
    border-bottom: 1px solid #eef2f8;
    cursor: pointer;

    .post-title,
    .event-title {
        font-weight: 600;
        margin-bottom: 0.25rem;
    }

    .post-meta,
    .event-meta {
        font-size: 0.75rem;
        color: #8a9bb0;
        display: flex;
        gap: 1rem;
    }
}

.empty-tab {
    text-align: center;
    padding: 2rem;
    color: #8a9bb0;
}
</style>