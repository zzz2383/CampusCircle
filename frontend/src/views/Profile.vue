<template>
    <div class="profile-container">
        <div class="profile-header">
            <el-button link @click="router.back()">
                <el-icon>
                    <ArrowLeft />
                </el-icon> 返回
            </el-button>
            <div class="logo">校园圈</div>
        </div>

        <div v-if="loading" class="skeleton-wrapper">
            <el-skeleton :rows="6" animated />
        </div>

        <div v-else-if="user" class="profile-content">
            <!-- 个人信息卡片 -->
            <div class="info-card">
                <div class="avatar-section">
                    <el-avatar :size="80" class="avatar">
                        {{ user.nickname.charAt(0) }}
                    </el-avatar>
                    <h2 class="nickname">{{ user.nickname }}</h2>
                    <div class="meta">
                        <span>{{ user.student_id }}</span>
                        <span v-if="user.department">{{ user.department }}</span>
                        <span v-if="user.grade">{{ user.grade }}</span>
                        <span v-if="user.gender">{{ genderText(user.gender) }}</span>
                    </div>
                    <el-button type="primary" plain @click="openEditDialog">编辑资料</el-button>
                </div>

                <!-- 仅保留帖子数统计 -->
                <div class="stats-row">
                    <div class="stat-item">
                        <div class="stat-number">{{ postsCount }}</div>
                        <div class="stat-label">帖子</div>
                    </div>
                </div>
            </div>

            <!-- 我的帖子列表 -->
            <div class="posts-card">
                <div class="posts-header">
                    <el-icon>
                        <Document />
                    </el-icon>
                    <span>我的帖子</span>
                </div>
                <div v-if="postsLoading" class="loading-placeholder">加载中...</div>
                <div v-else-if="myPosts.length === 0" class="empty-placeholder">暂无帖子，去发布一条吧～</div>
                <div v-else>
                    <div v-for="post in myPosts" :key="post.id" class="post-item" @click="goToPost(post.id)">
                        <div class="post-title">{{ post.title }}</div>
                        <div class="post-meta">{{ formatTime(post.created_at) }} · {{ post.like_count }} 点赞 · {{
                            post.comment_count }} 评论</div>
                    </div>
                    <!-- 分页加载更多 -->
                    <div v-if="hasMorePosts" class="load-more">
                        <el-button type="primary" plain @click="loadMorePosts"
                            :loading="postsLoadingMore">加载更多</el-button>
                    </div>
                </div>
            </div>
        </div>

        <!-- 编辑资料对话框 -->
        <el-dialog v-model="editDialogVisible" title="编辑资料" width="480px" destroy-on-close>
            <el-form :model="editForm" label-position="top">
                <el-form-item label="昵称">
                    <el-input v-model="editForm.nickname" placeholder="昵称" maxlength="20" show-word-limit />
                </el-form-item>
                <el-form-item label="院系">
                    <el-select v-model="editForm.department" placeholder="选择院系" clearable style="width: 100%">
                        <el-option label="计算机学院" value="计算机学院" />
                        <el-option label="软件学院" value="软件学院" />
                        <el-option label="经济管理学院" value="经济管理学院" />
                        <el-option label="人文学院" value="人文学院" />
                        <el-option label="其他" value="其他" />
                    </el-select>
                </el-form-item>
                <el-form-item label="年级">
                    <el-select v-model="editForm.grade" placeholder="年级" clearable style="width: 100%">
                        <el-option label="2026级" value="2026级" />
                        <el-option label="2025级" value="2025级" />
                        <el-option label="2024级" value="2024级" />
                        <el-option label="2023级" value="2023级" />
                        <el-option label="研究生/教师" value="研究生/教师" />
                    </el-select>
                </el-form-item>
                <el-form-item label="性别">
                    <el-radio-group v-model="editForm.gender">
                        <el-radio value="male">男</el-radio>
                        <el-radio value="female">女</el-radio>
                        <el-radio value="other">其他</el-radio>
                    </el-radio-group>
                </el-form-item>
                <!-- 头像上传占位 -->
                <el-form-item label="头像">
                    <el-upload action="#" :auto-upload="false" :show-file-list="false" @change="handleAvatarChange">
                        <el-button size="small">上传头像（演示）</el-button>
                    </el-upload>
                    <div class="form-hint">建议上传 200x200 图片</div>
                </el-form-item>
            </el-form>
            <template #footer>
                <el-button @click="editDialogVisible = false">取消</el-button>
                <el-button type="primary" @click="saveProfile" :loading="saving">保存</el-button>
            </template>
        </el-dialog>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Document } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/userStore'
import { updateProfile } from '@/services/auth'
import { getMyPosts } from '@/services/post'
import type { PostDTO, Gender } from '@/types'

const router = useRouter()
const userStore = useUserStore()

const user = userStore.user
const loading = ref(false)

// 帖子相关
const myPosts = ref<PostDTO[]>([])
const postsLoading = ref(false)
const postsLoadingMore = ref(false)
const postsCount = ref(0)
const postsOffset = ref(0)
const postsLimit = 20
const hasMorePosts = ref(false)

// 编辑对话框
const editDialogVisible = ref(false)
const editForm = ref({
    nickname: '',
    department: '',
    grade: '',
    gender: '' as Gender | '',
    avatar_url: ''
})
const saving = ref(false)

// 获取我的帖子
const fetchMyPosts = async (reset = true) => {
    if (reset) {
        postsLoading.value = true
        postsOffset.value = 0
    } else {
        postsLoadingMore.value = true
    }
    try {
        const res = await getMyPosts({ offset: postsOffset.value, limit: postsLimit })
        if (reset) {
            myPosts.value = res.items
        } else {
            myPosts.value.push(...res.items)
        }
        postsCount.value = res.total
        postsOffset.value += res.items.length
        hasMorePosts.value = myPosts.value.length < res.total
    } catch (error) {
        ElMessage.error('加载帖子失败')
    } finally {
        postsLoading.value = false
        postsLoadingMore.value = false
    }
}

const loadMorePosts = () => {
    if (!hasMorePosts.value || postsLoadingMore.value) return
    fetchMyPosts(false)
}

// 编辑资料
const openEditDialog = () => {
    if (!user) return
    editForm.value = {
        nickname: user.nickname,
        department: user.department || '',
        grade: user.grade || '',
        gender: user.gender || '',
        avatar_url: user.avatar_url || ''
    }
    editDialogVisible.value = true
}

const handleAvatarChange = () => {
    ElMessage.info('头像上传功能即将开放')
}

const saveProfile = async () => {
    saving.value = true
    try {
        const payload: any = {}
        if (editForm.value.nickname !== user?.nickname) payload.nickname = editForm.value.nickname
        if (editForm.value.department !== user?.department) payload.department = editForm.value.department || null
        if (editForm.value.grade !== user?.grade) payload.grade = editForm.value.grade || null
        if (editForm.value.gender !== (user?.gender || '')) payload.gender = editForm.value.gender || null
        if (editForm.value.avatar_url !== user?.avatar_url) payload.avatar_url = editForm.value.avatar_url || null

        if (Object.keys(payload).length === 0) {
            ElMessage.warning('未作任何修改')
            return
        }

        const updatedUser = await updateProfile(payload)
        userStore.user = updatedUser
        ElMessage.success('资料更新成功')
        editDialogVisible.value = false
        // 刷新页面显示新昵称
        window.location.reload()
    } catch (error) {
        ElMessage.error('更新失败')
    } finally {
        saving.value = false
    }
}

// 性别文本
const genderText = (gender: Gender) => {
    const map = { male: '男', female: '女', other: '其他' }
    return map[gender] || ''
}

// 时间格式化
const formatTime = (iso: string) => {
    const date = new Date(iso)
    const diff = Date.now() - date.getTime()
    if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
    if (diff < 604800000) return `${Math.floor(diff / 86400000)}天前`
    return `${date.getMonth() + 1}/${date.getDate()}`
}

const goToPost = (postId: number) => {
    router.push(`/posts/${postId}`)
}

onMounted(async () => {
    if (!userStore.user) {
        await userStore.initAuth()
    }
    if (userStore.user) {
        await fetchMyPosts()
    }
})
</script>

<style scoped lang="scss">
.profile-container {
    max-width: 900px;
    margin: 0 auto;
    padding: 1.5rem;
}

.profile-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;

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
    padding: 2rem;
    text-align: center;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
    margin-bottom: 1.5rem;

    .avatar {
        width: 80px;
        height: 80px;
        line-height: 80px;
        font-size: 2rem;
        background: #eef2fa;
    }

    .nickname {
        margin-top: 1rem;
        font-size: 1.4rem;
    }

    .meta {
        color: var(--el-text-color-secondary);
        font-size: 0.85rem;
        margin: 0.5rem 0 1rem;
        display: flex;
        gap: 0.75rem;
        justify-content: center;
        flex-wrap: wrap;
    }
}

.stats-row {
    display: flex;
    justify-content: center;
    margin-top: 1.5rem;

    .stat-item {
        text-align: center;

        .stat-number {
            font-size: 1.5rem;
            font-weight: 700;
        }

        .stat-label {
            font-size: 0.8rem;
            color: var(--el-text-color-secondary);
        }
    }
}

.posts-card {
    background: #fff;
    border-radius: 1.25rem;
    padding: 1.5rem;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);

    .posts-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 1.1rem;
        font-weight: 600;
        padding-bottom: 1rem;
        border-bottom: 1px solid var(--el-border-color-lighter);
        margin-bottom: 1rem;
    }
}

.post-item {
    padding: 1rem 0;
    border-bottom: 1px solid var(--el-border-color-lighter);
    cursor: pointer;
    transition: background 0.2s;

    &:hover {
        background: #f8fafc;
    }

    .post-title {
        font-weight: 600;
        margin-bottom: 0.25rem;
    }

    .post-meta {
        font-size: 0.75rem;
        color: var(--el-text-color-secondary);
    }
}

.load-more {
    text-align: center;
    margin-top: 1rem;
}

.loading-placeholder,
.empty-placeholder {
    text-align: center;
    padding: 2rem;
    color: var(--el-text-color-secondary);
}

.form-hint {
    font-size: 0.7rem;
    color: var(--el-text-color-secondary);
    margin-top: 0.25rem;
}
</style>