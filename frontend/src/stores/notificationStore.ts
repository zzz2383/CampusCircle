import { defineStore } from 'pinia'
import { ref } from 'vue'
import request from '@/services/request'

export interface Notification {
    id: string
    type: 'comment' | 'like' | 'follow'
    content: string
    sender_id: number
    post_id?: number | null
    timestamp: string
    read?: boolean   // 后端返回时可能没有，本地维护
}

export const useNotificationStore = defineStore('notification', () => {
    const notifications = ref<Notification[]>([])
    const unreadCount = ref(0)
    const loading = ref(false)

    /**
     * 从后端获取通知列表（最新优先）
     * @param limit 获取条数，默认20
     */
    const fetchNotifications = async (limit = 20) => {
        loading.value = true
        try {
            const res = await request.get<never, { notifications: Notification[]; count: number }>('/notifications', { params: { limit } })
            notifications.value = res.notifications
            // 后端返回的 count 是所有未读数量（假设），直接使用
            unreadCount.value = res.count
        } catch (error) {
            console.error('fetchNotifications failed', error)
        } finally {
            loading.value = false
        }
    }

    /**
     * 标记所有通知为已读（调用后端接口）
     */
    const markAllAsRead = async () => {
        try {
            await request.post('/notifications/read')
            unreadCount.value = 0
            // 可选：将本地列表中的 read 标记为 true
            notifications.value.forEach(n => { n.read = true })
        } catch (error) {
            console.error('markAllAsRead failed', error)
        }
    }

    /**
     * 添加一条新通知（由 WebSocket 推送时调用）
     * 同时推送到本地列表顶部，并增加未读数
     */
    const addNotification = (notif: Notification) => {
        // 防止重复（根据 id）
        const exists = notifications.value.some(n => n.id === notif.id)
        if (exists) return
        notifications.value.unshift(notif)
        unreadCount.value++
    }

    /**
     * 清空本地通知（不常用，可选）
     */
    const clearAll = () => {
        notifications.value = []
        unreadCount.value = 0
    }

    return {
        notifications,
        unreadCount,
        loading,
        fetchNotifications,
        markAllAsRead,
        addNotification,
        clearAll,
    }
})