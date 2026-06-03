<template>
    <div class="admin-container">
        <div class="admin-header">
            <div class="logo">校园圈 · 管理后台</div>
            <el-menu mode="horizontal" :default-active="activeMenu" @select="handleMenuSelect" class="nav-menu">
                <el-menu-item index="stats">数据概览</el-menu-item>
                <el-menu-item index="users">用户管理</el-menu-item>
                <el-menu-item index="posts">帖子管理</el-menu-item>
                <el-menu-item index="comments">评论管理</el-menu-item>
                <el-menu-item index="events">活动管理</el-menu-item>
                <el-menu-item index="lost">失物招领</el-menu-item>
                <el-menu-item index="clubs">社团管理</el-menu-item>
            </el-menu>
            <div class="user-info">
                <el-avatar :size="32">{{ adminName?.charAt(0) }}</el-avatar>
                <span>{{ adminName }}</span>
                <el-button link @click="logout">退出</el-button>
            </div>
        </div>

        <div class="admin-content">
            <!-- 数据概览 -->
            <div v-if="activeMenu === 'stats'">
                <div class="stats-cards">
                    <div class="stat-card">
                        <div>
                            <h3>总用户数</h3>
                            <div class="number">{{ adminStore.stats.total_users }}</div>
                        </div>
                        <el-icon :size="32">
                            <User />
                        </el-icon>
                    </div>
                    <div class="stat-card">
                        <div>
                            <h3>帖子总数</h3>
                            <div class="number">{{ adminStore.stats.total_posts }}</div>
                        </div>
                        <el-icon :size="32">
                            <Document />
                        </el-icon>
                    </div>
                    <div class="stat-card">
                        <div>
                            <h3>社团数量</h3>
                            <div class="number">{{ adminStore.stats.total_clubs }}</div>
                        </div>
                        <el-icon :size="32">
                            <Flag />
                        </el-icon>
                    </div>
                    <div class="stat-card">
                        <div>
                            <h3>活动数量</h3>
                            <div class="number">{{ adminStore.stats.total_events }}</div>
                        </div>
                        <el-icon :size="32">
                            <Calendar />
                        </el-icon>
                    </div>
                    <div class="stat-card">
                        <div>
                            <h3>失物招领</h3>
                            <div class="number">{{ adminStore.stats.total_lost_items }}</div>
                        </div>
                        <el-icon :size="32">
                            <Search />
                        </el-icon>
                    </div>
                </div>
                <!-- 图表区域 -->
                <div class="chart-container">
                    <h3>近7天帖子发布趋势</h3>
                    <canvas id="trendChart" style="width:100%; height:300px;"></canvas>
                </div>
                <div class="chart-container">
                    <h3>社团活跃度（帖子数）</h3>
                    <canvas id="clubChart" style="width:100%; height:300px;"></canvas>
                </div>
            </div>

            <!-- 用户管理 -->
            <div v-if="activeMenu === 'users'">
                <div class="section-title">用户管理</div>
                <div class="search-bar">
                    <el-input v-model="userKeyword" placeholder="搜索昵称/学号" clearable style="width: 260px"
                        @clear="searchUsers" @keyup.enter="searchUsers" />
                    <el-button type="primary" @click="searchUsers">搜索</el-button>
                </div>
                <el-table :data="adminStore.users" v-loading="adminStore.usersLoading" stripe>
                    <el-table-column prop="id" label="ID" width="60" />
                    <el-table-column prop="nickname" label="昵称" />
                    <el-table-column prop="student_id" label="学号" />
                    <el-table-column label="角色" width="100">
                        <template #default="{ row }">
                            <span :class="['role-badge', row.role]">{{ row.role === 'admin' ? '管理员' : row.role ===
                                'teacher' ? '教师' : '学生' }}</span>
                        </template>
                    </el-table-column>
                    <el-table-column label="状态" width="100">
                        <template #default="{ row }">
                            <span v-if="row.is_banned" class="status-banned">已封禁</span>
                            <span v-else class="status-normal">正常</span>
                        </template>
                    </el-table-column>
                    <el-table-column label="操作" width="220">
                        <template #default="{ row }">
                            <el-dropdown @command="(cmd: string) => handleUserCommand(cmd, row)">
                                <el-button size="small">管理</el-button>
                                <template #dropdown>
                                    <!-- 在用户管理表格的操作列中 -->
                                    <el-dropdown-menu>
                                        <el-dropdown-item command="role_student">设为学生</el-dropdown-item>
                                        <el-dropdown-item command="role_teacher">设为教师</el-dropdown-item>
                                        <!-- 仅超级管理员可见 -->
                                        <el-dropdown-item v-if="isSuperAdmin"
                                            command="role_admin">设为管理员</el-dropdown-item>
                                        <el-dropdown-item v-if="!row.is_banned" command="ban"
                                            divided>封禁24小时</el-dropdown-item>
                                        <el-dropdown-item v-else command="unban">解封</el-dropdown-item>
                                    </el-dropdown-menu>
                                </template>
                            </el-dropdown>
                        </template>
                    </el-table-column>
                </el-table>
                <div class="pagination" v-if="adminStore.usersTotal > 20">
                    <el-pagination layout="prev, pager, next" :total="adminStore.usersTotal" :page-size="20"
                        @current-change="handleUserPageChange" />
                </div>
            </div>

            <!-- 帖子管理 -->
            <div v-if="activeMenu === 'posts'">
                <div class="section-title">帖子管理</div>
                <el-table :data="postList" stripe>
                    <el-table-column prop="id" label="ID" width="60" />
                    <el-table-column prop="title" label="标题" />
                    <el-table-column prop="author_nickname" label="作者" />
                    <el-table-column label="操作" width="100">
                        <template #default="{ row }">
                            <el-button type="danger" size="small" @click="handleDeletePost(row.id)">删除</el-button>
                        </template>
                    </el-table-column>
                </el-table>
            </div>

            <!-- 评论管理 -->
            <div v-if="activeMenu === 'comments'">
                <div class="section-title">评论管理</div>
                <el-table :data="adminStore.comments" v-loading="adminStore.commentsLoading" stripe>
                    <el-table-column prop="id" label="ID" width="60" />
                    <el-table-column prop="content" label="评论内容" />
                    <el-table-column prop="author_nickname" label="作者" />
                    <el-table-column label="操作" width="100">
                        <template #default="{ row }">
                            <el-button type="danger" size="small" @click="handleDeleteComment(row.id)">删除</el-button>
                        </template>
                    </el-table-column>
                </el-table>
            </div>

            <!-- 活动管理 -->
            <div v-if="activeMenu === 'events'">
                <div class="section-title">活动管理</div>
                <el-table :data="eventList" stripe>
                    <el-table-column prop="id" label="ID" width="60" />
                    <el-table-column prop="title" label="标题" />
                    <el-table-column prop="location" label="地点" />
                    <el-table-column label="操作" width="100">
                        <template #default="{ row }">
                            <el-button type="danger" size="small" @click="handleDeleteEvent(row.id)">删除</el-button>
                        </template>
                    </el-table-column>
                </el-table>
            </div>

            <!-- 失物招领管理 -->
            <div v-if="activeMenu === 'lost'">
                <div class="section-title">失物招领管理</div>
                <el-table :data="lostItemList" stripe>
                    <el-table-column prop="id" label="ID" width="60" />
                    <el-table-column prop="title" label="标题" />
                    <el-table-column label="类型" width="80"><template #default="{ row }">{{ row.is_lost ? '丢失' : '拾到'
                    }}</template></el-table-column>
                    <el-table-column label="操作" width="100">
                        <template #default="{ row }">
                            <el-button type="danger" size="small" @click="handleDeleteLostItem(row.id)">删除</el-button>
                        </template>
                    </el-table-column>
                </el-table>
            </div>

            <!-- 社团管理 -->
            <div v-if="activeMenu === 'clubs'">
                <div class="section-title">社团管理</div>
                <el-table :data="clubList" stripe>
                    <el-table-column prop="id" label="ID" width="60" />
                    <el-table-column prop="name" label="社团名称" />
                    <el-table-column prop="description" label="简介" />
                    <el-table-column label="操作" width="100">
                        <template #default="{ row }">
                            <el-button type="danger" size="small" @click="handleDeleteClub(row.id)">删除</el-button>
                        </template>
                    </el-table-column>
                </el-table>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { User, Document, Flag, Calendar, Search } from '@element-plus/icons-vue'
import { useAdminStore } from '@/stores/adminStore'
import { useUserStore } from '@/stores/userStore'
import { getPosts } from '@/services/post'
import { getEvents } from '@/services/event'
import { getLostItems } from '@/services/lostItem'
import { getClubs } from '@/services/club'
import Chart from 'chart.js/auto'

const router = useRouter()
const adminStore = useAdminStore()
const userStore = useUserStore()

const activeMenu = ref('stats')
const adminName = userStore.user?.nickname

// 图表实例
let trendChart: InstanceType<typeof Chart> | null = null
let clubChart: InstanceType<typeof Chart> | null = null

const isSuperAdmin = computed(() => userStore.user?.id === 1)

// 初始化图表（模拟数据）
const initCharts = () => {
    const trendCtx = document.getElementById('trendChart') as HTMLCanvasElement
    const clubCtx = document.getElementById('clubChart') as HTMLCanvasElement
    if (!trendCtx || !clubCtx) return

    // 销毁旧实例
    if (trendChart) trendChart.destroy()
    if (clubChart) clubChart.destroy()

    // 趋势图（近7天帖子发布量）
    trendChart = new Chart(trendCtx, {
        type: 'line',
        data: {
            labels: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
            datasets: [{
                label: '帖子发布量',
                data: [45, 52, 38, 47, 69, 88, 73],
                borderColor: '#2e5bff',
                backgroundColor: 'rgba(46,91,255,0.1)',
                tension: 0.3,
                fill: true
            }]
        },
        options: { responsive: true, maintainAspectRatio: true }
    })

    // 社团活跃度条形图
    clubChart = new Chart(clubCtx, {
        type: 'bar',
        data: {
            labels: ['计算机协会', '音乐社', '羽毛球社', '英语角', '志愿者协会'],
            datasets: [{
                label: '社团帖子数',
                data: [47, 35, 28, 22, 19],
                backgroundColor: '#2e5bff',
                borderRadius: 8
            }]
        },
        options: { responsive: true, maintainAspectRatio: true }
    })
}

// 用户管理搜索
const userKeyword = ref('')
const searchUsers = () => {
    adminStore.fetchUsers(0, 20, userKeyword.value)
}
const handleUserPageChange = (page: number) => {
    adminStore.fetchUsers((page - 1) * 20, 20, userKeyword.value)
}

// 帖子列表
const postList = ref<any[]>([])
const fetchPosts = async () => {
    const res = await getPosts({ offset: 0, limit: 100 })
    postList.value = res.items
}
const handleDeletePost = async (id: number) => {
    await ElMessageBox.confirm('确定删除该帖子？', '提示', { type: 'warning' })
    await adminStore.deletePost(id)
    await fetchPosts()
    ElMessage.success('删除成功')
}

// 活动列表
const eventList = ref<any[]>([])
const fetchEvents = async () => {
    const res = await getEvents({ offset: 0, limit: 100 })
    eventList.value = res.items
}
const handleDeleteEvent = async (id: number) => {
    await ElMessageBox.confirm('确定删除该活动？', '提示', { type: 'warning' })
    await adminStore.deleteEvent(id)
    await fetchEvents()
    ElMessage.success('删除成功')
}

// 失物招领列表
const lostItemList = ref<any[]>([])
const fetchLostItems = async () => {
    const res = await getLostItems({ offset: 0, limit: 100 })
    lostItemList.value = res.items
}
const handleDeleteLostItem = async (id: number) => {
    await ElMessageBox.confirm('确定删除该失物招领？', '提示', { type: 'warning' })
    await adminStore.deleteLostItem(id)
    await fetchLostItems()
    ElMessage.success('删除成功')
}

// 社团列表
const clubList = ref<any[]>([])
const fetchClubs = async () => {
    const res = await getClubs()
    clubList.value = res
}
const handleDeleteClub = async (id: number) => {
    await ElMessageBox.confirm('确定删除该社团？', '提示', { type: 'warning' })
    await adminStore.deleteClub(id)
    await fetchClubs()
    ElMessage.success('删除成功')
}

// 评论管理操作
const handleDeleteComment = async (id: number) => {
    await ElMessageBox.confirm('确定删除该评论？', '提示', { type: 'warning' })
    await adminStore.deleteComment(id)
    await adminStore.fetchComments(0, 20)
    ElMessage.success('删除成功')
}

// 用户操作
const handleUserCommand = async (cmd: string, user: any) => {
    if (cmd === 'role_student') await adminStore.changeUserRole(user.id, 'student')
    else if (cmd === 'role_teacher') await adminStore.changeUserRole(user.id, 'teacher')
    else if (cmd === 'role_admin') await adminStore.changeUserRole(user.id, 'admin')
    else if (cmd === 'ban') await adminStore.banUserById(user.id, 24)
    else if (cmd === 'unban') await adminStore.unbanUserById(user.id)
    ElMessage.success('操作成功')
}

const handleMenuSelect = (index: string) => {
    activeMenu.value = index
    if (index === 'stats') {
        adminStore.fetchStats()
        // 等待 DOM 渲染完成后初始化图表
        nextTick(() => initCharts())
    }
    if (index === 'users') adminStore.fetchUsers(0, 20, '')
    if (index === 'comments') adminStore.fetchComments(0, 20)
    if (index === 'posts') fetchPosts()
    if (index === 'events') fetchEvents()
    if (index === 'lost') fetchLostItems()
    if (index === 'clubs') fetchClubs()
}

const logout = () => {
    userStore.logout()
    router.push('/auth')
}

onMounted(async () => {
    if (userStore.user?.role !== 'admin') {
        ElMessage.error('无权限访问管理后台')
        router.push('/')
        return
    }
    await adminStore.fetchStats()
    // 初始加载 stats 页面时，需要初始化图表
    if (activeMenu.value === 'stats') {
        nextTick(() => initCharts())
    }
})

// 监听 stats 的显示（如果重新切换到 stats 重新初始化）
watch(activeMenu, (newVal) => {
    if (newVal === 'stats') {
        nextTick(() => initCharts())
    }
})

// 组件卸载时销毁图表
onUnmounted(() => {
    if (trendChart) trendChart.destroy()
    if (clubChart) clubChart.destroy()
})
</script>

<style scoped lang="scss">
.admin-container {
    min-height: 100vh;
    background: #f5f7fb;
}

.admin-header {
    background: white;
    border-bottom: 1px solid #eef2f8;
    padding: 0 24px;
    display: flex;
    align-items: center;
    height: 64px;
    position: sticky;
    top: 0;
    z-index: 100;

    .logo {
        font-size: 1.25rem;
        font-weight: 700;
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        background-clip: text;
        -webkit-background-clip: text;
        color: transparent;
    }

    .nav-menu {
        flex: 1;
        margin-left: 32px;
        border-bottom: none;
    }

    .user-info {
        display: flex;
        align-items: center;
        gap: 12px;
    }
}

.admin-content {
    padding: 24px;
    max-width: 1400px;
    margin: 0 auto;
}

.stats-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    margin-bottom: 24px;
}

.stat-card {
    background: white;
    border-radius: 1rem;
    padding: 1.2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);

    h3 {
        font-size: 0.85rem;
        color: #5b6e8c;
        margin-bottom: 4px;
    }

    .number {
        font-size: 1.8rem;
        font-weight: 700;
    }
}

.section-title {
    font-size: 1.2rem;
    font-weight: 600;
    margin: 20px 0 16px;
}

.search-bar {
    display: flex;
    gap: 12px;
    margin-bottom: 20px;
}

.role-badge {
    font-size: 0.7rem;
    padding: 2px 8px;
    border-radius: 20px;

    &.student {
        background: #eef2fa;
        color: #2e5bff;
    }

    &.teacher {
        background: #e0f2fe;
        color: #2c7cb0;
    }

    &.admin {
        background: #fee2e2;
        color: #d9534f;
    }
}

.status-banned {
    color: #d9534f;
    font-size: 0.75rem;
}

.status-normal {
    color: #52c41a;
    font-size: 0.75rem;
}

.pagination {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
}

.chart-container {
    background: white;
    border-radius: 1rem;
    padding: 1rem;
    margin-bottom: 24px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);

    h3 {
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 12px;
        color: #1e2a3e;
    }
}
</style>