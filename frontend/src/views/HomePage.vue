<template>
    <div class="home-container">
        <!-- 顶部导航复用已有布局，可抽取为公共组件 -->
        <div class="navbar">
            <div class="logo">CampusCircle</div>
            <div class="user-info">
                <el-avatar :size="40" :src="userStore.user?.avatar_url || undefined">
                    {{ userStore.user?.nickname?.charAt(0) }}
                </el-avatar>
                <span class="nickname">{{ userStore.user?.nickname || '游客' }}</span>
                <el-button v-if="!userStore.isLoggedIn" @click="router.push('/auth')" text>登录</el-button>
                <el-button v-else @click="handleLogout" text>退出</el-button>
            </div>
        </div>

        <!-- 筛选栏 -->
        <div class="filter-bar">
            <div class="tag-group">
                <el-button v-for="tag in tagOptions" :key="tag.value"
                    :type="postStore.currentTag === tag.value ? 'primary' : 'default'"
                    :plain="postStore.currentTag !== tag.value" size="small" round
                    @click="() => postStore.setTag(tag.value)">
                    {{ tag.label }}
                </el-button>
            </div>
            <el-input v-model="searchKeyword" placeholder="搜索帖子..." clearable class="search-input" @clear="handleSearch"
                @keyup.enter="handleSearch">
                <template #prefix>
                    <el-icon>
                        <Search />
                    </el-icon>
                </template>
            </el-input>
        </div>

        <!-- 帖子列表 -->
        <el-skeleton :loading="postStore.loading && postStore.posts.length === 0" animated :row="3" />
        <div v-if="!postStore.loading && postStore.posts.length === 0" class="empty-state">
            <el-empty description="暂无帖子，发布第一条吧～" />
        </div>
        <div v-else>
            <div v-for="post in postStore.posts" :key="post.id" class="post-card">
                <div class="card-header">
                    <div class="author">
                        <el-avatar :size="36">{{ post.author_nickname.charAt(0) }}</el-avatar>
                        <div>
                            <div class="author-name">{{ post.author_nickname }}</div>
                            <div class="post-time">{{ formatTime(post.created_at) }}</div>
                        </div>
                    </div>
                </div>
                <div class="post-title">{{ post.title }}</div>
                <div class="post-content">{{ post.content }}</div>
                <div class="tags" v-if="post.tags">
                    <el-tag v-for="t in post.tags.split(',')" :key="t" size="small" effect="plain">
                        {{ t.trim() }}
                    </el-tag>
                </div>
                <div class="post-stats">
                    <div class="stat-item" :class="{ liked: post.is_liked }" @click="() => handleLike(post.id)">
                        <el-icon>
                            <Star />
                        </el-icon>
                        <span>{{ post.like_count }}</span>
                    </div>
                    <div class="stat-item">
                        <el-icon>
                            <ChatDotRound />
                        </el-icon>
                        <span>{{ post.comment_count }}</span>
                    </div>
                    <div class="stat-item">
                        <el-icon>
                            <View />
                        </el-icon>
                        <span>{{ post.view_count }}</span>
                    </div>
                </div>
            </div>
            <div class="load-more" v-if="postStore.hasMore">
                <el-button @click="postStore.loadMore" :loading="postStore.loading" type="primary" plain>
                    加载更多
                </el-button>
            </div>
        </div>

        <!-- 发帖浮动按钮 -->
        <el-button class="float-btn" type="primary" circle @click="openPostDialog">
            <el-icon>
                <Plus />
            </el-icon>
        </el-button>

        <!-- 发帖对话框 -->
        <el-dialog v-model="dialogVisible" title="发布新帖" width="550px" destroy-on-close>
            <el-form :model="postForm" label-position="top">
                <el-form-item label="标题" required>
                    <el-input v-model="postForm.title" placeholder="给帖子一个醒目的标题" maxlength="100" show-word-limit />
                </el-form-item>
                <el-form-item label="内容" required>
                    <el-input type="textarea" v-model="postForm.content" rows="6" placeholder="分享你的校园生活..."
                        maxlength="2000" show-word-limit />
                </el-form-item>
                <el-form-item label="话题标签（可选，多个用逗号分隔）">
                    <el-select v-model="postForm.tagsArray" multiple filterable allow-create default-first-option
                        placeholder="选择或创建标签" style="width: 100%">
                        <el-option v-for="item in commonTags" :key="item" :label="item" :value="item" />
                    </el-select>
                    <div class="form-hint">例如: 课程,社团,求助,失物招领</div>
                </el-form-item>
            </el-form>
            <template #footer>
                <el-button @click="dialogVisible = false">取消</el-button>
                <el-button type="primary" @click="submitPost" :loading="submitting">发布</el-button>
            </template>
        </el-dialog>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Star, ChatDotRound, View, Plus } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/userStore'
import { usePostStore } from '@/stores/postStore'

const router = useRouter()
const userStore = useUserStore()
const postStore = usePostStore()

// 本地搜索关键词
const searchKeyword = ref('')
const handleSearch = () => {
    postStore.setSearch(searchKeyword.value)
}

// 标签选项
const tagOptions = [
    { label: '全部', value: '' },
    { label: '课程', value: '课程' },
    { label: '社团', value: '社团' },
    { label: '求助', value: '求助' },
    { label: '失物招领', value: '失物招领' },
]

// 点赞处理
const handleLike = async (postId: number) => {
    if (!userStore.isLoggedIn) {
        ElMessage.warning('请先登录')
        router.push('/auth')
        return
    }
    try {
        await postStore.toggleLike(postId)
    } catch {
        ElMessage.error('操作失败，请重试')
    }
}

// 发帖对话框
const dialogVisible = ref(false)
const submitting = ref(false)
const postForm = ref({
    title: '',
    content: '',
    tagsArray: [] as string[],
})
const commonTags = ['课程', '社团', '求助', '失物招领', '生活', '吐槽']

const openPostDialog = () => {
    if (!userStore.isLoggedIn) {
        ElMessage.warning('请先登录')
        router.push('/auth')
        return
    }
    dialogVisible.value = true
    postForm.value = { title: '', content: '', tagsArray: [] }
}

const submitPost = async () => {
    if (!postForm.value.title.trim() || !postForm.value.content.trim()) {
        ElMessage.warning('请填写标题和内容')
        return
    }
    submitting.value = true
    try {
        await postStore.createNewPost({
            title: postForm.value.title.trim(),
            content: postForm.value.content.trim(),
            tags: postForm.value.tagsArray.join(','),
        })
        ElMessage.success('发布成功')
        dialogVisible.value = false
    } catch (error) {
        ElMessage.error('发布失败')
    } finally {
        submitting.value = false
    }
}

// 退出登录
const handleLogout = async () => {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', { type: 'warning' })
    userStore.logout()
    router.push('/auth')
}

// 时间格式化
const formatTime = (iso: string) => {
    const date = new Date(iso)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    if (diff < 60 * 60 * 1000) return `${Math.floor(diff / 60000)}分钟前`
    if (diff < 24 * 60 * 60 * 1000) return `${Math.floor(diff / (60 * 60 * 1000))}小时前`
    if (diff < 7 * 24 * 60 * 60 * 1000) return `${Math.floor(diff / (24 * 60 * 60 * 1000))}天前`
    return `${date.getMonth() + 1}/${date.getDate()}`
}

onMounted(async () => {
    if (userStore.isLoggedIn) {
        await postStore.fetchPosts()
    } else {
        // 未登录也可查看列表
        await postStore.fetchPosts()
    }
})
</script>

<style scoped lang="scss">
.home-container {
    max-width: 1000px;
    margin: 0 auto;
    padding: 1.5rem;
}

.navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-bottom: 1.5rem;
    margin-bottom: 2rem;
    border-bottom: 1px solid var(--el-border-color-light);
}

.logo {
    font-size: 1.8rem;
    font-weight: 700;
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
    background-clip: text;
    -webkit-background-clip: text;
    color: transparent;
}

.user-info {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.nickname {
    font-weight: 600;
}

.filter-bar {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
    margin-bottom: 2rem;
    align-items: center;
    justify-content: space-between;
}

.tag-group {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
}

.search-input {
    width: 240px;
}

.post-card {
    background: #ffffff;
    border-radius: 1.25rem;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
    padding: 1.5rem;
    margin-bottom: 1.25rem;
    transition: all 0.2s;
    border: 1px solid var(--el-border-color-lighter);

    &:hover {
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
        transform: translateY(-2px);
    }
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
}

.author {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.author-name {
    font-weight: 600;
}

.post-time {
    font-size: 0.75rem;
    color: var(--el-text-color-secondary);
}

.post-title {
    font-size: 1.35rem;
    font-weight: 700;
    margin: 0.5rem 0;
}

.post-content {
    color: #334155;
    line-height: 1.5;
    margin: 0.75rem 0;
    display: -webkit-box;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

.tags {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
    margin: 0.75rem 0;
}

.post-stats {
    display: flex;
    gap: 1.5rem;
    margin-top: 1rem;
    padding-top: 0.75rem;
    border-top: 1px solid var(--el-border-color-lighter);
}

.stat-item {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    color: var(--el-text-color-secondary);
    font-size: 0.85rem;
    cursor: pointer;
    transition: color 0.2s;

    &.liked {
        color: var(--el-color-primary);
    }

    &:hover {
        color: var(--el-color-primary);
    }
}

.load-more {
    text-align: center;
    margin: 2rem 0;
}

.float-btn {
    position: fixed;
    bottom: 2rem;
    right: 2rem;
    width: 56px;
    height: 56px;
    border-radius: 28px;
    box-shadow: 0 8px 20px rgba(46, 91, 255, 0.3);
    transition: transform 0.2s;

    &:hover {
        transform: scale(1.05);
    }
}

.form-hint {
    font-size: 0.75rem;
    color: var(--el-text-color-secondary);
    margin-top: 0.25rem;
}

.empty-state {
    text-align: center;
    padding: 3rem;
}

@media (max-width: 680px) {
    .home-container {
        padding: 1rem;
    }

    .search-input {
        width: 100%;
    }
}
</style>