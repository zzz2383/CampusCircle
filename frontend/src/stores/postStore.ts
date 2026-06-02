import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { PostDTO } from '@/types'
import { getPosts, createPost, likePost, unlikePost } from '@/services/post'

export const usePostStore = defineStore('post', () => {
    const posts = ref<PostDTO[]>([])
    const total = ref(0)
    const loading = ref(false)
    const currentOffset = ref(0)
    const limit = 20
    const currentTag = ref('')
    const searchKeyword = ref('')

    const hasMore = computed(() => posts.value.length < total.value)

    /**
     * 获取帖子列表 (支持重置或追加)
     * Given: 用户进入首页或切换筛选条件
     * When: 调用 fetchPosts(reset=true) 或 loadMore()
     * Then: 更新 posts 列表，保持分页状态
     */
    const fetchPosts = async (reset = true) => {
        if (loading.value) return
        loading.value = true
        try {
            const offset = reset ? 0 : currentOffset.value
            const params: any = {
                offset,
                limit,
                tag: currentTag.value || undefined,
            }
            // 注意：后端搜索可能需要单独接口，这里假设 tag 参数可传 search
            // 若后端无搜索，可扩展，目前暂不实现搜索
            const res = await getPosts(params)
            if (reset) {
                posts.value = res.items
                currentOffset.value = res.items.length
            } else {
                posts.value.push(...res.items)
                currentOffset.value += res.items.length
            }
            total.value = res.total
        } catch (error) {
            console.error('Fetch posts failed', error)
        } finally {
            loading.value = false
        }
    }

    const loadMore = async () => {
        if (loading.value || !hasMore.value) return
        await fetchPosts(false)
    }

    const setTag = async (tag: string) => {
        currentTag.value = tag
        currentOffset.value = 0
        await fetchPosts(true)
    }

    const setSearch = async (keyword: string) => {
        searchKeyword.value = keyword
        // 搜索实现需后端支持，暂时仅做本地过滤或后续扩展
        currentOffset.value = 0
        await fetchPosts(true)
    }

    /**
     * 创建新帖子
     * Given: 用户已登录，填写标题、内容、标签
     * When: 调用 createNewPost(data)
     * Then: 帖子创建成功，刷新列表顶部
     */
    const createNewPost = async (data: { title: string; content: string; tags?: string }) => {
        const newPost = await createPost(data)
        // 刷新列表到顶部
        currentOffset.value = 0
        await fetchPosts(true)
        return newPost
    }

    /**
     * 切换点赞状态 (乐观更新)
     */
    const toggleLike = async (postId: number) => {
        const targetPost = posts.value.find(p => p.id === postId)
        if (!targetPost) return

        // 乐观更新
        const originalLiked = targetPost.is_liked
        const originalCount = targetPost.like_count
        targetPost.is_liked = !originalLiked
        targetPost.like_count = originalLiked ? originalCount - 1 : originalCount + 1

        try {
            if (targetPost.is_liked) {
                await likePost(postId)
            } else {
                await unlikePost(postId)
            }
        } catch (error) {
            // 回滚
            targetPost.is_liked = originalLiked
            targetPost.like_count = originalCount
            throw error
        }
    }

    return {
        posts,
        total,
        loading,
        hasMore,
        currentTag,
        searchKeyword,
        fetchPosts,
        loadMore,
        setTag,
        setSearch,
        createNewPost,
        toggleLike,
    }
})