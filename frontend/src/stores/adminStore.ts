import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getAdminStats, getAdminUsers, getAdminComments, deletePostByAdmin, deleteCommentByAdmin, deleteEventByAdmin, deleteLostItemByAdmin, deleteClubByAdmin, updateUserRole, banUser, unbanUser } from '@/services/admin'
import type { AdminStats, User, AdminComment } from '@/types'

export const useAdminStore = defineStore('admin', () => {
    // 统计
    const stats = ref<AdminStats>({
        total_users: 0,
        total_posts: 0,
        total_clubs: 0,
        total_events: 0,
        total_lost_items: 0
    })

    // 用户列表
    const users = ref<User[]>([])
    const usersTotal = ref(0)
    const usersLoading = ref(false)

    // 评论列表
    const comments = ref<AdminComment[]>([])
    const commentsTotal = ref(0)
    const commentsLoading = ref(false)

    // 获取统计
    const fetchStats = async () => {
        try {
            const data = await getAdminStats()
            stats.value = data
        } catch (error) {
            console.error('fetchStats failed', error)
        }
    }

    // 获取用户列表（分页+搜索）
    const fetchUsers = async (offset = 0, limit = 20, keyword = '') => {
        usersLoading.value = true
        try {
            const res = await getAdminUsers({ offset, limit, keyword: keyword || undefined })
            users.value = res.items
            usersTotal.value = res.total
        } finally {
            usersLoading.value = false
        }
    }

    // 获取评论列表
    const fetchComments = async (offset = 0, limit = 20) => {
        commentsLoading.value = true
        try {
            const res = await getAdminComments({ offset, limit })
            comments.value = res.items
            commentsTotal.value = res.total
        } finally {
            commentsLoading.value = false
        }
    }

    // 删除操作
    const deletePost = async (postId: number) => {
        await deletePostByAdmin(postId)
    }
    const deleteComment = async (commentId: number) => {
        await deleteCommentByAdmin(commentId)
    }
    const deleteEvent = async (eventId: number) => {
        await deleteEventByAdmin(eventId)
    }
    const deleteLostItem = async (itemId: number) => {
        await deleteLostItemByAdmin(itemId)
    }
    const deleteClub = async (clubId: number) => {
        await deleteClubByAdmin(clubId)
    }

    // 用户角色修改
    const changeUserRole = async (userId: number, role: 'student' | 'teacher' | 'admin') => {
        await updateUserRole(userId, role)
        // 刷新用户列表
        await fetchUsers(0, 20, '')
    }

    // 封禁/解封
    const banUserById = async (userId: number, durationHours = 24) => {
        await banUser(userId, durationHours)
        await fetchUsers(0, 20, '')
    }
    const unbanUserById = async (userId: number) => {
        await unbanUser(userId)
        await fetchUsers(0, 20, '')
    }

    return {
        stats,
        users,
        usersTotal,
        usersLoading,
        comments,
        commentsTotal,
        commentsLoading,
        fetchStats,
        fetchUsers,
        fetchComments,
        deletePost,
        deleteComment,
        deleteEvent,
        deleteLostItem,
        deleteClub,
        changeUserRole,
        banUserById,
        unbanUserById,
    }
})