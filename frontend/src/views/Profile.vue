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
            <el-skeleton :rows="8" animated />
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

                <div class="stats-row">
                    <div class="stat-item" @click="activeTab = 'followers'">
                        <div class="stat-number">{{ followersCount }}</div>
                        <div class="stat-label">粉丝</div>
                    </div>
                    <div class="stat-item" @click="activeTab = 'following'">
                        <div class="stat-number">{{ followingCount }}</div>
                        <div class="stat-label">关注</div>
                    </div>
                    <div class="stat-item" @click="activeTab = 'posts'">
                        <div class="stat-number">{{ postsCount }}</div>
                        <div class="stat-label">帖子</div>
                    </div>
                </div>
            </div>

            <!-- Tab 内容：我的帖子 / 关注 / 粉丝 -->
            <div class="tabs-card">
                <el-tabs v-model="activeTab">
                    <el-tab-pane label="我的帖子" name="posts">
                        <div v-if="postsLoading" class="loading-placeholder">加载中...</div>
                        <div v-else-if="myPosts.length === 0" class="empty-placeholder">暂无帖子</div>
                        <div v-else>
                            <div v-for="post in myPosts" :key="post.id" class="post-item" @click="goToPost(post.id)">
                                <div class="post-title">{{ post.title }}</div>
                                <div class="post-meta">{{ formatTime(post.created_at) }} · {{ post.like_count }} 点赞
                                </div>
                            </div>
                        </div>
                    </el-tab-pane>

                    <el-tab-pane label="关注" name="following">
                        <div v-if="followingLoading" class="loading-placeholder">加载中...</div>
                        <div v-else-if="followingList.length === 0" class="empty-placeholder">还没有关注任何人</div>
                        <div v-else>
                            <div v-for="item in followingList" :key="item.id" class="user-item">
                                <div class="user-avatar">{{ item.nickname.charAt(0) }}</div>
                                <div class="user-info">
                                    <div class="user-nickname">{{ item.nickname }}</div>
                                    <div class="user-meta">{{ item.student_id }}</div>
                                </div>
                                <el-button size="small" type="danger" plain
                                    @click.stop="unfollowUser(item.id)">取消关注</el-button>
                            </div>
                        </div>
                    </el-tab-pane>

                    <el-tab-pane label="粉丝" name="followers">
                        <div v-if="followersLoading" class="loading-placeholder">加载中...</div>
                        <div v-else-if="followersList.length === 0" class="empty-placeholder">暂无粉丝</div>
                        <div v-else>
                            <div v-for="item in followersList" :key="item.id" class="user-item">
                                <div class="user-avatar">{{ item.nickname.charAt(0) }}</div>
                                <div class="user-info">
                                    <div class="user-nickname">{{ item.nickname }}</div>
                                    <div class="user-meta">{{ item.student_id }}</div>
                                </div>
                                <el-button size="small" type="primary" plain
                                    @click.stop="followUser(item.id)">关注</el-button>
                            </div>
                        </div>
                    </el-tab-pane>
                </el-tabs>
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
                <!-- 头像上传（可选，先留占位） -->
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
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/userStore'
import { updateProfile } from '@/services/auth'
import type { User, Gender } from '@/types'

const router = useRouter()
const userStore = useUserStore()

const user = computed(() => userStore.user)
const loading = ref(false)

// 统计数据（模拟，后续需对接真实接口）
const followersCount = ref(0)
const followingCount = ref(0)
const postsCount = ref(0)

// 帖子相关
const activeTab = ref<'posts' | 'following' | 'followers'>('posts')
const myPosts = ref<any[]>([])
const postsLoading = ref(false)
const followingList = ref<any[]>([])
const followingLoading = ref(false)
const followersList = ref<any[]>([])
const followersLoading = ref(false)

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

// 获取用户统计数据（关注数、粉丝数、帖子数）- 需要后端接口，暂时模拟
const fetchStats = async () => {
    // TODO: 对接 GET /api/users/{id}/stats 或类似接口
    followersCount.value = 128
    followingCount.value = 86
    postsCount.value = 12
}

// 获取我的帖子
const fetchMyPosts = async () => {
    postsLoading.value = true
    try {
        // TODO: 对接 GET /api/users/me/posts
        // 模拟数据
        myPosts.value = [
            { id: 101, title: '计算机学院讲座: AI 前沿与应用', like_count: 24, created_at: new Date(Date.now() - 86400000).toISOString() },
            { id: 102, title: '食堂麻辣香锅推荐', like_count: 32, created_at: new Date(Date.now() - 172800000).toISOString() }
        ]
    } finally {
        postsLoading.value = false
    }
}

// 获取关注列表
const fetchFollowing = async () => {
    followingLoading.value = true
    try {
        // TODO: 对接 GET /api/users/me/following
        followingList.value = [
            { id: 2, nickname: '李华', student_id: '20240002' },
            { id: 3, nickname: '王老师', student_id: '20230001' }
        ]
    } finally {
        followingLoading.value = false
    }
}

// 获取粉丝列表
const fetchFollowers = async () => {
    followersLoading.value = true
    try {
        // TODO: 对接 GET /api/users/me/followers
        followersList.value = [
            { id: 4, nickname: '张小花', student_id: '20240005' },
            { id: 5, nickname: '赵学长', student_id: '20230010' }
        ]
    } finally {
        followersLoading.value = false
    }
}

// 监听 Tab 切换，懒加载数据
const onTabChange = (tabName: string) => {
    if (tabName === 'posts' && myPosts.value.length === 0) fetchMyPosts()
    if (tabName === 'following' && followingList.value.length === 0) fetchFollowing()
    if (tabName === 'followers' && followersList.value.length === 0) fetchFollowers()
}

// 关注/取消关注（模拟）
const followUser = async (userId: number) => {
    // TODO: 对接 POST /api/users/{id}/follow
    ElMessage.success('已关注')
    await fetchFollowing()
}
const unfollowUser = async (userId: number) => {
    // TODO: 对接 DELETE /api/users/{id}/follow
    followingList.value = followingList.value.filter(u => u.id !== userId)
    followingCount.value--
    ElMessage.success('已取消关注')
}

// 编辑资料
const openEditDialog = () => {
    if (!user.value) return
    editForm.value = {
        nickname: user.value.nickname,
        department: user.value.department || '',
        grade: user.value.grade || '',
        gender: user.value.gender || '',
        avatar_url: user.value.avatar_url || ''
    }
    editDialogVisible.value = true
}

const handleAvatarChange = (file: any) => {
    // 演示：仅占位，实际上传需调用上传接口获取 url
    ElMessage.info('头像上传功能演示，实际需对接文件上传接口')
}

const saveProfile = async () => {
    saving.value = true
    try {
        const payload: any = {}
        if (editForm.value.nickname !== user.value?.nickname) payload.nickname = editForm.value.nickname
        if (editForm.value.department !== user.value?.department) payload.department = editForm.value.department || null
        if (editForm.value.grade !== user.value?.grade) payload.grade = editForm.value.grade || null
        if (editForm.value.gender !== (user.value?.gender || '')) payload.gender = editForm.value.gender || null
        if (editForm.value.avatar_url !== user.value?.avatar_url) payload.avatar_url = editForm.value.avatar_url || null

        if (Object.keys(payload).length === 0) {
            ElMessage.warning('未作任何修改')
            return
        }

        const updatedUser = await updateProfile(payload)
        userStore.user = updatedUser
        ElMessage.success('资料更新成功')
        editDialogVisible.value = false
    } catch (error) {
        ElMessage.error('更新失败')
    } finally {
        saving.value = false
    }
}

// 跳转帖子详情
const goToPost = (postId: number) => {
    router.push(`/posts/${postId}`)
}

// 性别文本转换
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

onMounted(async () => {
    if (!userStore.user) {
        await userStore.initAuth()
    }
    if (userStore.user) {
        await fetchStats()
        // 默认加载我的帖子
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
    gap: 3rem;
    margin-top: 1.5rem;

    .stat-item {
        text-align: center;
        cursor: pointer;

        .stat-number {
            font-size: 1.5rem;
            font-weight: 700;
        }

        .stat-label {
            font-size: 0.8rem;
            color: var(--el-text-color-secondary);
        }

        &:hover .stat-number {
            color: var(--el-color-primary);
        }
    }
}

.tabs-card {
    background: #fff;
    border-radius: 1.25rem;
    padding: 0 1.5rem;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
}

.post-item {
    padding: 1rem 0;
    border-bottom: 1px solid var(--el-border-color-lighter);
    cursor: pointer;

    .post-title {
        font-weight: 600;
        margin-bottom: 0.25rem;
    }

    .post-meta {
        font-size: 0.75rem;
        color: var(--el-text-color-secondary);
    }
}

.user-item {
    display: flex;
    align-items: center;
    padding: 1rem 0;
    border-bottom: 1px solid var(--el-border-color-lighter);

    .user-avatar {
        width: 44px;
        height: 44px;
        background: #eef2fa;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        margin-right: 1rem;
    }

    .user-info {
        flex: 1;

        .user-nickname {
            font-weight: 600;
        }

        .user-meta {
            font-size: 0.7rem;
            color: var(--el-text-color-secondary);
        }
    }
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