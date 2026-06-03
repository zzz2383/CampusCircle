<template>
    <div class="lost-container">
        <div class="header">
            <el-button link @click="router.back()">
                <el-icon>
                    <ArrowLeft />
                </el-icon> 返回
            </el-button>
            <div class="logo">校园圈 · 失物招领</div>
        </div>

        <!-- 筛选栏 -->
        <div class="filter-bar">
            <el-radio-group v-model="currentFilter" @change="handleFilterChange">
                <el-radio-button value="all">全部</el-radio-button>
                <el-radio-button value="lost">丢失</el-radio-button>
                <el-radio-button value="found">拾到</el-radio-button>
            </el-radio-group>
        </div>

        <!-- 列表 -->
        <div v-if="store.loading && store.items.length === 0" class="loading-state">
            <el-skeleton :rows="5" animated />
        </div>
        <div v-else-if="store.items.length === 0" class="empty-state">
            <el-empty description="暂无相关物品" />
        </div>
        <div v-else>
            <div v-for="item in store.items" :key="item.id" class="item-card" @click="viewDetail(item)">
                <div class="card-header">
                    <span :class="['type-badge', item.is_lost ? 'lost' : 'found']">
                        {{ item.is_lost ? '丢失' : '拾到' }}
                    </span>
                    <span v-if="item.is_expired" class="status-badge expired">已过期</span>
                    <span v-else-if="item.is_found" class="status-badge found">已找回</span>
                </div>
                <img v-if="item.image_url" :src="item.image_url" style="width:100%;max-height:180px;object-fit:cover;border-radius:8px;margin-bottom:8px" />
                <div class="item-title">{{ item.title }}</div>
                <div class="item-meta">
                    <span><el-icon>
                            <Location />
                        </el-icon> {{ item.location || '未填地点' }}</span>
                    <span><el-icon>
                            <Clock />
                        </el-icon> {{ formatTime(item.created_at) }}</span>
                </div>
            </div>
            <div v-if="store.hasMore" class="load-more">
                <el-button @click="store.loadMore" :loading="store.loading" type="primary" plain>加载更多</el-button>
            </div>
        </div>

        <!-- 发布按钮 -->
        <el-button class="float-btn" type="primary" circle @click="openPublishDialog">
            <el-icon>
                <Plus />
            </el-icon>
        </el-button>

        <!-- 发布对话框 -->
        <el-dialog v-model="publishVisible" title="发布失物/拾物" width="500px" destroy-on-close>
            <el-form :model="publishForm" label-position="top">
                <el-form-item label="类型" required>
                    <el-radio-group v-model="publishForm.is_lost">
                        <el-radio :label="true">丢失</el-radio>
                        <el-radio :label="false">拾到</el-radio>
                    </el-radio-group>
                </el-form-item>
                <el-form-item label="标题" required>
                    <el-input v-model="publishForm.title" placeholder="例：丢失蓝色校园卡" maxlength="50" show-word-limit />
                </el-form-item>
                <el-form-item label="描述" required>
                    <el-input type="textarea" v-model="publishForm.description" rows="4" placeholder="详细描述物品特征、时间地点等"
                        maxlength="500" show-word-limit />
                </el-form-item>
                <el-form-item label="物品图片（可选）">
                    <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap">
                        <input type="file" accept="image/png,image/jpeg,image/gif,image/webp"
                            ref="lostItemImageInput" style="display:none" @change="handleLostItemImage" />
                        <el-button size="small" @click="lostItemImageInput?.click()" :loading="publishForm.imageUploading">
                            上传图片
                        </el-button>
                        <span v-if="publishForm.image_url" style="font-size:0.8rem;color:#67c23a">已上传</span>
                    </div>
                    <img v-if="publishForm.image_url" :src="publishForm.image_url" style="max-width:200px;max-height:150px;border-radius:8px;margin-top:4px" />
                </el-form-item>
                <el-form-item label="地点（可选）">
                    <el-input v-model="publishForm.location" placeholder="例：二食堂三楼" />
                </el-form-item>
                <el-form-item label="联系方式（可选）">
                    <el-input v-model="publishForm.contact" placeholder="手机号/微信号" />
                </el-form-item>
            </el-form>
            <template #footer>
                <el-button @click="publishVisible = false">取消</el-button>
                <el-button type="primary" @click="submitPublish" :loading="publishing">发布</el-button>
            </template>
        </el-dialog>

        <!-- 详情对话框 -->
        <el-dialog v-model="detailVisible" title="物品详情" width="500px">
            <div v-if="currentItem">
                <el-descriptions :column="1" border>
                    <el-descriptions-item label="类型">
                        <span :style="{ color: currentItem.is_lost ? '#d9534f' : '#2c7cb0' }">
                            {{ currentItem.is_lost ? '丢失' : '拾到' }}
                        </span>
                    </el-descriptions-item>
                    <el-descriptions-item label="标题">{{ currentItem.title }}</el-descriptions-item>
                    <el-descriptions-item v-if="currentItem.image_url" label="物品图片">
                        <img :src="currentItem.image_url" style="max-width:100%;max-height:200px;border-radius:8px" />
                    </el-descriptions-item>
                    <el-descriptions-item label="描述">{{ currentItem.description }}</el-descriptions-item>
                    <el-descriptions-item label="地点">{{ currentItem.location || '未填' }}</el-descriptions-item>
                    <el-descriptions-item label="联系方式">{{ currentItem.contact || '未填' }}</el-descriptions-item>
                    <el-descriptions-item label="发布时间">{{ formatTime(currentItem.created_at) }}</el-descriptions-item>
                    <el-descriptions-item label="状态">
                        <span v-if="currentItem.is_expired" style="color:#999;">已过期（超过7天）</span>
                        <span v-else-if="currentItem.is_found" style="color:#2c7cb0;">已找回</span>
                        <span v-else style="color:#52c41a;">进行中</span>
                    </el-descriptions-item>
                </el-descriptions>
                <div v-if="!currentItem.is_expired && !currentItem.is_found && canMarkFound(currentItem)"
                    class="found-action">
                    <el-button type="primary" plain @click="handleMarkFound(currentItem.id)">标记为已找回</el-button>
                </div>
            </div>
        </el-dialog>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Location, Clock, Plus } from '@element-plus/icons-vue'
import { useLostItemStore } from '@/stores/lostItemStore'
import { useUserStore } from '@/stores/userStore'

const router = useRouter()
const store = useLostItemStore()
const userStore = useUserStore()

// 筛选联动
const currentFilter = computed({
    get: () => store.currentFilter,
    set: (val) => store.setFilter(val),
})
const handleFilterChange = (val: 'all' | 'lost' | 'found') => {
    store.setFilter(val)
}

// 发布
const publishVisible = ref(false)
const publishing = ref(false)
const publishForm = ref({
    is_lost: true,
    title: '',
    description: '',
    location: '',
    contact: '',
})

const lostItemImageInput = ref<HTMLInputElement>()
const handleLostItemImage = async (e: Event) => {
    const input = e.target as HTMLInputElement
    const file = input.files?.[0]
    if (!file) return
    if (file.size > 5 * 1024 * 1024) {
        ElMessage.error('图片超过 5MB 限制')
        return
    }
    publishForm.value.imageUploading = true
    try {
        const { uploadImage } = await import('@/services/upload')
        const result = await uploadImage(file)
        publishForm.value.image_url = result.url
        ElMessage.success('图片已上传')
    } catch {
        ElMessage.error('图片上传失败')
    }
    publishForm.value.imageUploading = false
    input.value = ''
}

const openPublishDialog = () => {
    if (!userStore.isLoggedIn) {
        ElMessage.warning('请先登录')
        router.push('/auth')
        return
    }
    publishForm.value = { is_lost: true, title: '', description: '', location: '', contact: '' }
    publishVisible.value = true
}

const submitPublish = async () => {
    if (!publishForm.value.title.trim() || !publishForm.value.description.trim()) {
        ElMessage.warning('请填写标题和描述')
        return
    }
    publishing.value = true
    try {
        await store.publishItem({
            is_lost: publishForm.value.is_lost,
            title: publishForm.value.title.trim(),
            description: publishForm.value.description.trim(),
            location: publishForm.value.location.trim() || undefined,
            contact: publishForm.value.contact.trim() || undefined,
        })
        ElMessage.success('发布成功')
        publishVisible.value = false
    } catch (error) {
        ElMessage.error('发布失败')
    } finally {
        publishing.value = false
    }
}

// 详情
const detailVisible = ref(false)
const currentItem = ref<any>(null)
const viewDetail = (item: any) => {
    currentItem.value = item
    detailVisible.value = true
}

const canMarkFound = (item: any) => {
    // 只有发布者本人或管理员可以标记找回，这里简化：仅验证登录用户是否匹配
    return userStore.isLoggedIn && userStore.user?.id === item.user_id
}

const handleMarkFound = async (id: number) => {
    try {
        await store.setFound(id)
        ElMessage.success('已标记为已找回')
        detailVisible.value = false
        // 刷新列表以更新状态
        await store.fetchItems(true)
    } catch (error) {
        ElMessage.error('操作失败')
    }
}

// 时间格式化
const formatTime = (iso: string) => {
    const date = new Date(iso)
    const diff = Date.now() - date.getTime()
    if (diff < 60000) return '刚刚'
    if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
    if (diff < 604800000) return `${Math.floor(diff / 86400000)}天前`
    return `${date.getMonth() + 1}/${date.getDate()}`
}

onMounted(async () => {
    await store.fetchItems()
})
</script>

<style scoped lang="scss">
.lost-container {
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

.item-card {
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

.card-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 0.5rem;
}

.type-badge {
    font-size: 0.7rem;
    padding: 0.2rem 0.6rem;
    border-radius: 20px;

    &.lost {
        background: #fee2e2;
        color: #d9534f;
    }

    &.found {
        background: #e0f2fe;
        color: #2c7cb0;
    }
}

.status-badge {
    font-size: 0.7rem;
    padding: 0.2rem 0.6rem;
    border-radius: 20px;
    background: #f0f0f0;
    color: #999;

    &.found {
        background: #e0f2fe;
        color: #2c7cb0;
    }
}

.item-title {
    font-weight: 700;
    font-size: 1.1rem;
    margin: 0.5rem 0;
}

.item-meta {
    display: flex;
    gap: 1rem;
    font-size: 0.75rem;
    color: #8a9bb0;
    align-items: center;
}

.load-more {
    text-align: center;
    margin: 1.5rem 0;
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

.found-action {
    margin-top: 1rem;
    text-align: center;
}
</style>