<template>
    <div class="rank-container">
        <div class="rank-header">
            <div class="logo">校园圈</div>
            <el-button link @click="router.push('/')" class="back-home">
                <el-icon>
                    <ArrowLeft />
                </el-icon> 返回首页
            </el-button>
        </div>

        <el-tabs v-model="activeTab" class="rank-tabs" @tab-click="handleTabClick">
            <el-tab-pane label="热帖榜" name="hot">
                <div class="rank-card">
                    <div class="tag-filter" v-if="activeTab === 'hot'">
                        <el-button v-for="tag in tagOptions" :key="tag.value"
                            :type="currentTag === tag.value ? 'primary' : 'default'" :plain="currentTag !== tag.value"
                            size="small" round @click="setTagFilter(tag.value)">
                            {{ tag.label }}
                        </el-button>
                    </div>

                    <div v-if="hotLoading" class="state-placeholder">
                        <el-skeleton :rows="5" animated />
                    </div>
                    <div v-else-if="hotPosts.length === 0" class="state-placeholder">
                        <el-empty description="暂无热帖数据" />
                    </div>
                    <ul class="rank-list" v-else>
                        <li v-for="(post, idx) in hotPosts" :key="post.id" class="rank-item">
                            <div class="rank-number" :class="getRankClass(idx)">
                                {{ idx + 1 }}
                            </div>
                            <div class="rank-info" @click="goToPost(post.id)">
                                <div class="rank-title">{{ post.title }}</div>
                                <div class="rank-meta">
                                    {{ post.author_nickname }} ·
                                    <span v-if="post.tags">{{ post.tags.split(',').slice(0, 2).join(', ') }}</span>
                                    <span v-else>无标签</span>
                                </div>
                            </div>
                            <div class="rank-value">
                                <el-icon>
                                    <Star />
                                </el-icon>
                                {{ post.like_count + post.comment_count * 2 }} 热度
                            </div>
                        </li>
                    </ul>
                </div>
            </el-tab-pane>

            <el-tab-pane label="社团活跃榜" name="club">
                <div class="rank-card">
                    <div v-if="clubLoading" class="state-placeholder">
                        <el-skeleton :rows="5" animated />
                    </div>
                    <div v-else-if="clubs.length === 0" class="state-placeholder">
                        <el-empty description="暂无社团数据" />
                    </div>
                    <ul class="rank-list" v-else>
                        <li v-for="(club, idx) in clubs" :key="club.club_id" class="rank-item">
                            <div class="rank-number" :class="getRankClass(idx)">
                                {{ idx + 1 }}
                            </div>
                            <div class="rank-info">
                                <div class="rank-title">{{ club.club_name }}</div>
                            </div>
                            <div class="rank-value club-post-count">
                                {{ club.post_count }} 篇帖子
                            </div>
                        </li>
                    </ul>
                </div>
            </el-tab-pane>
        </el-tabs>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Star } from '@element-plus/icons-vue'
import { getHotRank, getClubRank } from '@/services/rank'
import type { PostDTO, ClubRank } from '@/types'

const router = useRouter()

// Tab 状态
const activeTab = ref<'hot' | 'club'>('hot')

// 热帖榜
const hotPosts = ref<PostDTO[]>([])
const hotLoading = ref(false)
const currentTag = ref('')
const tagOptions = [
    { label: '全部', value: '' },
    { label: '课程', value: '课程' },
    { label: '社团', value: '社团' },
    { label: '求助', value: '求助' },
    { label: '失物招领', value: '失物招领' },
]

// 社团榜
const clubs = ref<ClubRank[]>([])
const clubLoading = ref(false)

// 获取热帖榜
const fetchHotRank = async () => {
    hotLoading.value = true
    try {
        const params: { limit?: number; tag?: string } = { limit: 20 }
        if (currentTag.value) params.tag = currentTag.value
        const data = await getHotRank(params)
        hotPosts.value = data
    } catch (error) {
        ElMessage.error('加载热帖榜失败')
    } finally {
        hotLoading.value = false
    }
}

// 获取社团榜
const fetchClubRank = async () => {
    clubLoading.value = true
    try {
        const data = await getClubRank({ limit: 20 })
        clubs.value = data
    } catch (error) {
        ElMessage.error('加载社团榜失败')
    } finally {
        clubLoading.value = false
    }
}

// 切换标签筛选
const setTagFilter = (tag: string) => {
    currentTag.value = tag
    fetchHotRank()
}

// 处理 Tab 切换
const handleTabClick = (tab: { paneName: string }) => {
    if (tab.paneName === 'hot' && hotPosts.value.length === 0) {
        fetchHotRank()
    } else if (tab.paneName === 'club' && clubs.value.length === 0) {
        fetchClubRank()
    }
}

// 跳转到帖子详情
const goToPost = (postId: number) => {
    router.push(`/posts/${postId}`)
}

// 排名样式
const getRankClass = (idx: number) => {
    if (idx === 0) return 'top-1'
    if (idx === 1) return 'top-2'
    if (idx === 2) return 'top-3'
    return ''
}

onMounted(() => {
    // 默认加载热帖榜
    fetchHotRank()
    // 社团榜懒加载，等用户点击 Tab 时再加载
})
</script>

<style scoped lang="scss">
.rank-container {
    max-width: 1000px;
    margin: 0 auto;
    padding: 1.5rem;
}

.rank-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-bottom: 1.5rem;
    margin-bottom: 2rem;
    border-bottom: 1px solid var(--el-border-color-light);

    .logo {
        font-size: 1.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        background-clip: text;
        -webkit-background-clip: text;
        color: transparent;
    }

    .back-home {
        font-size: 0.9rem;
    }
}

.rank-tabs {
    margin-bottom: 1.5rem;
}

.rank-card {
    background: #fff;
    border-radius: 1.25rem;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
    padding: 1.5rem;
    border: 1px solid var(--el-border-color-lighter);
}

.tag-filter {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
    margin-bottom: 1.5rem;
}

.rank-list {
    list-style: none;
    margin: 0;
    padding: 0;
}

.rank-item {
    display: flex;
    align-items: center;
    padding: 1rem 0;
    border-bottom: 1px solid var(--el-border-color-lighter);
    transition: background 0.2s;

    &:last-child {
        border-bottom: none;
    }

    &:hover {
        background: #f8fafc;
    }
}

.rank-number {
    width: 48px;
    font-size: 1.2rem;
    font-weight: 700;
    text-align: center;

    &.top-1 {
        color: #ffb800;
    }

    &.top-2 {
        color: #b0b0b0;
    }

    &.top-3 {
        color: #cd7f32;
    }
}

.rank-info {
    flex: 1;
    padding: 0 1rem;
    cursor: pointer;
}

.rank-title {
    font-weight: 600;
    font-size: 1rem;
    margin-bottom: 0.25rem;
    color: var(--el-text-color-primary);
}

.rank-meta {
    font-size: 0.75rem;
    color: var(--el-text-color-secondary);
}

.rank-value {
    font-weight: 600;
    color: var(--el-color-primary);
    min-width: 80px;
    text-align: right;
    display: flex;
    align-items: center;
    gap: 0.25rem;
    justify-content: flex-end;

    &.club-post-count {
        color: #2e5bff;
    }
}

.state-placeholder {
    text-align: center;
    padding: 2rem;
}

@media (max-width: 680px) {
    .rank-container {
        padding: 1rem;
    }

    .rank-number {
        width: 36px;
        font-size: 1rem;
    }

    .rank-title {
        font-size: 0.9rem;
    }

    .rank-value {
        min-width: 70px;
        font-size: 0.85rem;
    }
}
</style>