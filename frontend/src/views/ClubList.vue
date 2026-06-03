<template>
    <div class="club-list-container">
        <div class="header">
            <el-button link @click="router.back()">
                <el-icon>
                    <ArrowLeft />
                </el-icon> 返回
            </el-button>
            <div class="logo">校园圈 · 社团中心</div>
        </div>

        <div v-if="store.loading" class="loading-state">
            <el-skeleton :rows="5" animated />
        </div>
        <div v-else-if="store.clubs.length === 0" class="empty-state">
            <el-empty description="暂无社团，快来创建第一个吧～" />
        </div>
        <div v-else>
            <div v-for="club in store.clubs" :key="club.id" class="club-card" @click="goToDetail(club.id)">
                <div class="club-name">{{ club.name }}</div>
                <div class="club-desc">{{ club.description || '暂无简介' }}</div>
                <div class="club-meta">
                    <span><el-icon>
                            <User />
                        </el-icon> 成员 {{ club.member_count ?? '--' }}</span>
                    <span><el-icon>
                            <Calendar />
                        </el-icon> {{ formatDate(club.created_at) }}</span>
                </div>
            </div>
        </div>

        <el-button class="float-btn" type="primary" circle @click="openCreateDialog">
            <el-icon>
                <Plus />
            </el-icon>
        </el-button>

        <el-dialog v-model="createDialogVisible" title="创建社团" width="450px" destroy-on-close>
            <el-form :model="createForm" label-position="top">
                <el-form-item label="社团名称" required>
                    <el-input v-model="createForm.name" placeholder="例：计算机协会" maxlength="30" show-word-limit />
                </el-form-item>
                <el-form-item label="社团简介">
                    <el-input type="textarea" v-model="createForm.description" rows="3" placeholder="介绍社团宗旨、活动内容等"
                        maxlength="200" show-word-limit />
                </el-form-item>
            </el-form>
            <template #footer>
                <el-button @click="createDialogVisible = false">取消</el-button>
                <el-button type="primary" @click="submitCreate" :loading="creating">创建</el-button>
            </template>
        </el-dialog>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, User, Calendar, Plus } from '@element-plus/icons-vue'
import { useClubStore } from '@/stores/clubStore'
import { useUserStore } from '@/stores/userStore'

const router = useRouter()
const store = useClubStore()
const userStore = useUserStore()

const createDialogVisible = ref(false)
const creating = ref(false)
const createForm = ref({ name: '', description: '' })

const openCreateDialog = () => {
    if (!userStore.isLoggedIn) {
        ElMessage.warning('请先登录')
        router.push('/auth')
        return
    }
    createForm.value = { name: '', description: '' }
    createDialogVisible.value = true
}

const submitCreate = async () => {
    if (!createForm.value.name.trim()) {
        ElMessage.warning('请填写社团名称')
        return
    }
    creating.value = true
    try {
        await store.createNewClub({
            name: createForm.value.name.trim(),
            description: createForm.value.description.trim() || undefined,
        })
        ElMessage.success('创建成功')
        createDialogVisible.value = false
    } catch (error) {
        ElMessage.error('创建失败')
    } finally {
        creating.value = false
    }
}

const goToDetail = (clubId: number) => {
    router.push(`/clubs/${clubId}`)
}

const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return `${date.getFullYear()}/${date.getMonth() + 1}/${date.getDate()}`
}

onMounted(() => {
    store.fetchClubs()
})
</script>

<style scoped lang="scss">
.club-list-container {
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

.club-card {
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

.club-name {
    font-size: 1.2rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
}

.club-desc {
    color: #5b6e8c;
    font-size: 0.85rem;
    margin-bottom: 0.75rem;
}

.club-meta {
    display: flex;
    gap: 1rem;
    font-size: 0.75rem;
    color: #8a9bb0;
    align-items: center;
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

.loading-state,
.empty-state {
    text-align: center;
    padding: 3rem;
}
</style>