import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { PostDTO } from '@/types'
import { getPosts, createPost, likePost as likePostAPI, unlikePost as unlikePostAPI, updatePost, deletePost, getPostById } from '@/services/post'

export const usePostStore = defineStore('post', () => {
    const posts = ref<PostDTO[]>([])
    const total = ref(0)
    const loading = ref(false)
    const currentOffset = ref(0)
    const limit = 20
    const currentTag = ref('')
    const searchKeyword = ref('')

    const hasMore = computed(() => posts.value.length < total.value)

    const fetchPosts = async (reset = true) => {
        if (loading.value) return
        loading.value = true
        try {
            const offset = reset ? 0 : currentOffset.value
            const params: any = { offset, limit }

            // 搜索优先：keyword 非空时忽略 tag
            if (searchKeyword.value) {
                params.keyword = searchKeyword.value
            } else if (currentTag.value) {
                params.tag = currentTag.value
            }

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
        searchKeyword.value = '' // 切换标签时清空搜索词
        currentOffset.value = 0
        await fetchPosts(true)
    }

    const setSearch = async (keyword: string) => {
        searchKeyword.value = keyword
        currentTag.value = '' // 搜索时清空标签筛选
        currentOffset.value = 0
        await fetchPosts(true)
    }

    const createNewPost = async (data: { title: string; content: string; tags?: string; club_id?: number }) => {
        const newPost = await createPost(data)
        currentOffset.value = 0
        await fetchPosts(true)
        return newPost
    }

    const toggleLike = async (postId: number) => {
        const targetPost = posts.value.find(p => p.id === postId)
        if (!targetPost) return

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
            targetPost.is_liked = originalLiked
            targetPost.like_count = originalCount
            throw error
        }
    }

    // 更新列表中的帖子（用于编辑后同步）
    const updatePostInList = (updatedPost: PostDTO) => {
        const index = posts.value.findIndex(p => p.id === updatedPost.id)
        if (index !== -1) {
            posts.value[index] = updatedPost
        }
    }

    // 编辑帖子（调用后端接口，并同步列表和详情页状态）
    const editPost = async (postId: number, data: { title?: string; content?: string; tags?: string }) => {
        const updated = await updatePost(postId, data)
        // 更新列表中的对应帖子
        updatePostInList(updated)
        return updated
    }

    // 删除帖子
    const deletePostById = async (postId: number) => {
        await deletePost(postId)
        // 从列表中移除
        const index = posts.value.findIndex(p => p.id === postId)
        if (index !== -1) posts.value.splice(index, 1)
        total.value--
        // 如果当前详情页的帖子被删除，由组件处理路由跳转，这里不负责
    }

    const currentPost = ref<PostDTO | null>(null)
    const fetchPostDetail = async (postId: number) => {
        const data = await getPostById(postId)
        currentPost.value = data
        return data
    }

    const likePost = async (postId: number) => {
        const res = await likePostAPI(postId)
        return res
    }
    const unlikePost = async (postId: number) => {
        const res = await unlikePostAPI(postId)
        return res
    }


    return {
        posts,
        total,
        loading,
        hasMore,
        currentTag,
        searchKeyword,
        currentPost,
        fetchPosts,
        loadMore,
        setTag,
        setSearch,
        createNewPost,
        toggleLike,
        editPost,
        updatePostInList,
        deletePostById,
        fetchPostDetail,
        likePost,
        unlikePost,
    }
})