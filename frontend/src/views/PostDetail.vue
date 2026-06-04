<template>
    <div class="post-detail-container">
        <div class="detail-header">
            <el-button link @click="goBack">
                <el-icon>
                    <ArrowLeft />
                </el-icon> 返回
            </el-button>
            <div class="logo">校园圈</div>
        </div>

        <!-- 骨架屏 / 错误状态 -->
        <div v-if="loading && !post" class="loading-wrapper">
            <el-skeleton :rows="8" animated />
        </div>
        <div v-else-if="error" class="error-state">
            <el-empty description="帖子不存在或已删除" />
            <el-button type="primary" @click="router.push('/')">返回首页</el-button>
        </div>

        <template v-else-if="post">
            <!-- 帖子卡片 -->
            <div class="post-card">
                <div class="author-area">
                    <el-avatar :size="36" :src="post.author_avatar || undefined">
                        {{ post.author_nickname?.charAt(0) || '?' }}
                    </el-avatar>
                    <div class="author-info">
                        <div class="author-name">{{ post.author_nickname }}</div>
                        <div class="post-time">{{ formatTime(post.created_at) }}</div>
                    </div>
                    <!-- 操作菜单（仅作者或管理员可见） -->
                    <el-dropdown v-if="canManagePost" trigger="click" @command="handlePostAction">
                        <el-icon class="more-icon">
                            <MoreFilled />
                        </el-icon>
                        <template #dropdown>
                            <el-dropdown-menu>
                                <el-dropdown-item command="edit">编辑</el-dropdown-item>
                                <el-dropdown-item command="delete">删除</el-dropdown-item>
                            </el-dropdown-menu>
                        </template>
                    </el-dropdown>
                </div>
                <h1 class="post-title">{{ post.title }}</h1>
                <div class="post-content" v-html="renderMarkdown(post.content)"></div>
                <div class="tags" v-if="post.tags">
                    <el-tag v-for="t in post.tags.split(',')" :key="t" size="small" effect="plain">
                        {{ t.trim() }}
                    </el-tag>
                </div>
                <div class="post-stats">
                    <div class="stat-item" :class="{ liked: post.is_liked }" @click="handleLike">
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

            <!-- 评论区 -->
            <div class="comments-section">
                <div class="comments-header">
                    <el-icon>
                        <ChatLineSquare />
                    </el-icon>
                    <span>评论 · {{ totalComments }}</span>
                </div>

                <!-- 评论列表 -->
                <div v-if="commentsLoading" class="comment-skeleton">
                    <el-skeleton :rows="3" animated />
                </div>
                <div v-else-if="comments.length === 0" class="empty-comments">
                    暂无评论，快来抢沙发～
                </div>
                <div v-else>
                    <div v-for="comment in comments" :key="comment.id" class="comment-item">
                        <div class="comment-header">
                            <el-avatar :size="28" :src="comment.author_avatar || undefined">
                                {{ comment.author_nickname.charAt(0) }}
                            </el-avatar>
                            <span class="comment-author">{{ comment.author_nickname }}</span>
                            <span class="comment-time">{{ formatTime(comment.created_at) }}</span>
                        </div>
                        <div class="comment-content">{{ comment.content }}</div>
                        <div class="reply-btn" @click="startReply(comment)">
                            <el-icon>
                                <ChatLineRound />
                            </el-icon> 回复
                        </div>
                        <!-- 回复列表 -->
                        <div class="replies" v-if="getReplies(comment.id).length">
                            <div v-for="reply in getReplies(comment.id)" :key="reply.id" class="reply-item">
                                <span class="reply-author">{{ reply.author_nickname }}</span>
                                <span>{{ reply.content }}</span>
                                <span class="reply-time">{{ formatTime(reply.created_at) }}</span>
                            </div>
                        </div>
                        <!-- 回复输入框 -->
                        <div v-if="replyTarget && replyTarget.id === comment.id" class="reply-form">
                            <el-input v-model="replyContent" placeholder="写下你的回复..." size="small" clearable
                                @keyup.enter="submitReply(comment.id)" />
                            <el-button type="primary" size="small" @click="submitReply(comment.id)"
                                :loading="replyLoading">
                                发送
                            </el-button>
                            <el-button size="small" @click="cancelReply">取消</el-button>
                        </div>
                    </div>
                    <!-- 加载更多评论 -->
                    <div v-if="hasMoreComments" class="load-more-comments">
                        <el-button type="primary" plain @click="loadMoreComments" :loading="commentsLoadingMore">
                            加载更多评论
                        </el-button>
                    </div>
                </div>

                <!-- 发表评论表单 -->
                <div class="comment-form">
                    <el-avatar :size="36" :src="post.author_avatar || undefined">
                        {{ post.author_nickname?.charAt(0) || '?' }}
                    </el-avatar>
                    <div class="comment-input-wrapper">
                        <el-input v-model="newCommentContent" type="textarea" :rows="2" placeholder="写下你的评论..."
                            resize="none" />
                        <div class="comment-actions">
                            <el-button type="primary" @click="submitComment" :loading="commentSubmitting">
                                发表评论
                            </el-button>
                        </div>
                    </div>
                </div>
                <!-- 编辑帖子对话框 -->
                <el-dialog v-model="editDialogVisible" title="编辑帖子" width="550px" destroy-on-close>
                    <el-form :model="editForm" label-position="top">
                        <el-form-item label="标题">
                            <el-input v-model="editForm.title" placeholder="标题" maxlength="100" show-word-limit />
                        </el-form-item>
                        <el-form-item label="内容">
                            <el-input type="textarea" v-model="editForm.content" rows="6" placeholder="正文"
                                maxlength="2000" show-word-limit />
                        </el-form-item>
                        <el-form-item label="标签（多个用逗号分隔）">
                            <el-input v-model="editForm.tags" placeholder="例如：课程,求助" />
                        </el-form-item>
                    </el-form>
                    <template #footer>
                        <el-button @click="editDialogVisible = false">取消</el-button>
                        <el-button type="primary" @click="submitEdit" :loading="editSubmitting">保存</el-button>
                    </template>
                </el-dialog>
            </div>
        </template>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Star, ChatDotRound, View, ChatLineSquare } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/userStore'
import { getComments, createComment } from '@/services/comment'
import type { PostDTO, CommentDTO } from '@/types'
import { usePostStore } from '@/stores/postStore'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const postStore = usePostStore()

const postId = computed(() => Number(route.params.id))
const post = ref<PostDTO | null>(null)
const loading = ref(true)
const error = ref(false)

// 评论相关
const comments = ref<CommentDTO[]>([])
const totalComments = ref(0)
const commentsOffset = ref(0)
const commentsLimit = 20
const commentsLoading = ref(true)
const commentsLoadingMore = ref(false)
const hasMoreComments = computed(() => comments.value.length < totalComments.value)

const newCommentContent = ref('')
const commentSubmitting = ref(false)

// 回复相关
const replyTarget = ref<CommentDTO | null>(null)
const replyContent = ref('')
const replyLoading = ref(false)

// 编辑相关
const editDialogVisible = ref(false)
const editSubmitting = ref(false)
const editForm = ref({
    title: '',
    content: '',
    tags: ''
})

// 删除帖子（通过 store）
const deleteCurrentPost = async () => {
    await ElMessageBox.confirm('确定删除该帖子吗？删除后不可恢复。', '提示', { type: 'warning' })
    await postStore.deletePostById(postId.value)
    ElMessage.success('删除成功')
    router.push('/')
}

// 编辑帖子（通过 store）
const openEditDialog = () => {
    if (!post.value) return
    editForm.value = {
        title: post.value.title,
        content: post.value.content,
        tags: post.value.tags || ''
    }
    editDialogVisible.value = true
}

const submitEdit = async () => {
    editSubmitting.value = true
    try {
        const payload: any = {}
        if (editForm.value.title !== post.value?.title) payload.title = editForm.value.title
        if (editForm.value.content !== post.value?.content) payload.content = editForm.value.content
        if (editForm.value.tags !== (post.value?.tags || '')) payload.tags = editForm.value.tags || null

        if (Object.keys(payload).length === 0) {
            ElMessage.warning('未作任何修改')
            return
        }

        const updated = await postStore.editPost(postId.value, payload)
        // 由于 store 已更新列表中的帖子，且 currentPost 也需手动更新
        postStore.currentPost = updated
        ElMessage.success('编辑成功')
        editDialogVisible.value = false
    } catch (error) {
        ElMessage.error('编辑失败')
    } finally {
        editSubmitting.value = false
    }
}

const fetchPost = async () => {
    try {
        loading.value = true
        await postStore.fetchPostDetail(postId.value)
        // ✅ 关键：将 store 中的帖子数据同步到本地 ref
        post.value = postStore.currentPost
        error.value = false
    } catch (err) {
        error.value = true
    } finally {
        loading.value = false
    }
}

// 获取评论（顶层评论）
const fetchComments = async (reset = true) => {
    try {
        if (reset) {
            commentsLoading.value = true
            commentsOffset.value = 0
        } else {
            commentsLoadingMore.value = true
        }
        const res = await getComments(postId.value, {
            offset: commentsOffset.value,
            limit: commentsLimit,
        })
        if (reset) {
            comments.value = res.items
        } else {
            comments.value.push(...res.items)
        }
        totalComments.value = res.total
        commentsOffset.value += res.items.length
    } catch (err) {
        ElMessage.error('加载评论失败')
    } finally {
        commentsLoading.value = false
        commentsLoadingMore.value = false
    }
}

// 是否可管理（作者或管理员）
const canManagePost = computed(() => {
    if (!userStore.isLoggedIn) return false
    return userStore.user?.id === post.value?.user_id || userStore.user?.role === 'admin'
})

// 操作菜单命令处理
const handlePostAction = (command: string) => {
    if (command === 'edit') openEditDialog()
    else if (command === 'delete') deleteCurrentPost()
}

const loadMoreComments = () => {
    if (!hasMoreComments.value || commentsLoadingMore.value) return
    fetchComments(false)
}

// 获取楼中楼回复（内存筛选）
const getReplies = (commentId: number) => {
    return comments.value.filter(c => c.parent_id === commentId)
}

// 点赞（通过 store 的 updatePostLike，但需要先调用接口）
const handleLike = async () => {
    if (!userStore.isLoggedIn) {
        ElMessage.warning('请先登录')
        router.push('/auth')
        return
    }
    if (!post.value) return
    const wasLiked = post.value.is_liked
    const originalCount = post.value.like_count
    // 乐观更新本地显示
    post.value.is_liked = !wasLiked
    post.value.like_count = wasLiked ? originalCount - 1 : originalCount + 1
    try {
        if (wasLiked) {
            await postStore.unlikePost(post.value.id)
        } else {
            await postStore.likePost(post.value.id)
        }
    } catch {
        // 回滚
        post.value.is_liked = wasLiked
        post.value.like_count = originalCount
        ElMessage.error('操作失败，请重试')
    }
}

// 发表评论
const submitComment = async () => {
    if (!userStore.isLoggedIn) {
        ElMessage.warning('请先登录')
        router.push('/auth')
        return
    }
    if (!newCommentContent.value.trim()) {
        ElMessage.warning('评论内容不能为空')
        return
    }
    commentSubmitting.value = true
    try {
        const newComment = await createComment(postId.value, { content: newCommentContent.value.trim() })
        // 将新评论添加到列表顶部（模拟父评论）
        comments.value.unshift(newComment)
        totalComments.value++
        if (post.value) post.value.comment_count++
        newCommentContent.value = ''
        ElMessage.success('评论成功')
    } catch (err) {
        ElMessage.error('评论失败')
    } finally {
        commentSubmitting.value = false
    }
}

// 回复评论
const startReply = (comment: CommentDTO) => {
    if (!userStore.isLoggedIn) {
        ElMessage.warning('请先登录')
        router.push('/auth')
        return
    }
    replyTarget.value = comment
    replyContent.value = ''
}
const cancelReply = () => {
    replyTarget.value = null
    replyContent.value = ''
}
const submitReply = async (parentId: number) => {
    if (!replyContent.value.trim()) {
        ElMessage.warning('回复内容不能为空')
        return
    }
    replyLoading.value = true
    try {
        const newReply = await createComment(postId.value, {
            content: replyContent.value.trim(),
            parent_id: parentId,
        })
        // 将回复添加到对应父评论的旁边（这里直接插入到 comments 数组中，渲染时根据 parent_id 分组）
        comments.value.push(newReply)
        totalComments.value++
        if (post.value) post.value.comment_count++
        replyContent.value = ''
        replyTarget.value = null
        ElMessage.success('回复成功')
    } catch (err) {
        ElMessage.error('回复失败')
    } finally {
        replyLoading.value = false
    }
}


const renderMarkdown = (text: string): string => {
    if (!text) return ''
    let html = text
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/!\[([^\]]*)\]\(([^)]+)\)/g, '<img src="$2" alt="$1" style="max-width:100%;border-radius:8px;margin:8px 0" />')
        .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>')
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.+?)\*/g, '<em>$1</em>')
        .replace(/\n/g, '<br>')   // 确保这一行没有换行
    return html
}

const formatTime = (iso: string) => {
    if (!iso) return '未知时间'
    // 后端存储的是 UTC 时间，加 Z 后缀让浏览器正确转换为本地时区
    const date = new Date(iso.endsWith('Z') ? iso : iso + 'Z')
    if (isNaN(date.getTime())) return '无效时间'
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    // 处理未来时间（时钟不同步或数据异常）
    if (diff < 0) return '刚刚'
    if (diff < 60000) return '刚刚'
    if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
    if (diff < 604800000) return `${Math.floor(diff / 86400000)}天前`
    return `${date.getMonth() + 1}/${date.getDate()}`
}

const goBack = () => {
    router.back()
}

onMounted(async () => {
    await fetchPost()
    if (post.value) {
        // 增加浏览量（不阻塞页面渲染）
        fetch(`/api/posts/${post.value.id}/view`, { method: 'POST' }).catch(() => { })
        await fetchComments()
    }
})
</script>

<style scoped lang="scss">
.post-detail-container {
    max-width: 900px;
    margin: 0 auto;
    padding: 1.5rem;
}

.detail-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1.5rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid var(--el-border-color-light);

    .logo {
        font-size: 1.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        background-clip: text;
        -webkit-background-clip: text;
        color: transparent;
    }
}

.post-card {
    background: #fff;
    border-radius: 1.25rem;
    padding: 1.8rem;
    margin-bottom: 2rem;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
    border: 1px solid var(--el-border-color-lighter);
}

.author-area {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1.2rem;
}

.author-info {
    .author-name {
        font-weight: 700;
        font-size: 1.1rem;
    }

    .post-time {
        font-size: 0.75rem;
        color: var(--el-text-color-secondary);
    }
}

.post-title {
    font-size: 1.8rem;
    font-weight: 700;
    margin: 1rem 0;
    line-height: 1.3;
}

.post-content {
    font-size: 1rem;
    line-height: 1.6;
    color: #334155;
    margin: 1rem 0;
    white-space: pre-wrap;
}

.tags {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
    margin: 1rem 0;
}

.post-stats {
    display: flex;
    gap: 2rem;
    margin-top: 1.5rem;
    padding-top: 1rem;
    border-top: 1px solid var(--el-border-color-lighter);
}

.stat-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: var(--el-text-color-secondary);
    cursor: pointer;
    transition: color 0.2s;

    &.liked {
        color: var(--el-color-primary);
    }

    &:hover {
        color: var(--el-color-primary);
    }
}

.comments-section {
    background: #fff;
    border-radius: 1.25rem;
    padding: 1.8rem;
    border: 1px solid var(--el-border-color-lighter);
}

.comments-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 1.2rem;
    font-weight: 600;
    margin-bottom: 1.5rem;
}

.comment-item {
    padding: 1rem 0;
    border-bottom: 1px solid var(--el-border-color-lighter);
}

.comment-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 0.5rem;
}

.comment-author {
    font-weight: 600;
    font-size: 0.9rem;
}

.comment-time {
    font-size: 0.7rem;
    color: var(--el-text-color-secondary);
    margin-left: auto;
}

.comment-content {
    margin-left: 2.5rem;
    margin-bottom: 0.5rem;
}

.reply-btn {
    margin-left: 2.5rem;
    font-size: 0.75rem;
    color: var(--el-text-color-secondary);
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;

    &:hover {
        color: var(--el-color-primary);
    }
}

.replies {
    margin-left: 2.5rem;
    margin-top: 0.75rem;
    padding-left: 1rem;
    border-left: 2px solid var(--el-border-color-lighter);
}

.reply-item {
    margin-bottom: 0.5rem;
    font-size: 0.85rem;

    .reply-author {
        font-weight: 600;
        margin-right: 0.5rem;
    }

    .reply-time {
        font-size: 0.7rem;
        color: var(--el-text-color-secondary);
        margin-left: 0.5rem;
    }
}

.reply-form {
    margin-top: 0.75rem;
    margin-left: 2.5rem;
    display: flex;
    gap: 0.5rem;
    align-items: center;
}

.comment-form {
    margin-top: 1.5rem;
    display: flex;
    gap: 0.75rem;
    align-items: flex-start;
}

.comment-input-wrapper {
    flex: 1;

    .comment-actions {
        display: flex;
        justify-content: flex-end;
        margin-top: 0.5rem;
    }
}

.load-more-comments {
    text-align: center;
    margin-top: 1rem;
}

.empty-comments {
    text-align: center;
    padding: 2rem;
    color: var(--el-text-color-secondary);
}

.error-state,
.loading-wrapper {
    text-align: center;
    padding: 3rem;
}

@media (max-width: 680px) {
    .post-detail-container {
        padding: 1rem;
    }

    .post-title {
        font-size: 1.4rem;
    }
}
</style>