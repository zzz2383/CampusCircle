import { defineStore } from 'pinia'
import { ref } from 'vue'
import request from '@/services/request'

export interface Notification {
    id: number
    type: 'comment' | 'like' | 'follow'
    content: string
    targetId: number | null   // 帖子ID或其他资源ID
    createdAt: string
    read: boolean
}

export const useNotificationStore = defineStore('notification', () => {
    const notifications = ref<Notification[]>([])
    const unreadCount = ref(0)
    const loading = ref(false)

    /**
     * 从后端获取未读数量（初次加载或定时刷新）
     */
    const fetchUnreadCount = async () => {
        try {
            const res = await request.get<never, { unread_count: number }>('/notifications/unread-count')
            unreadCount.value = res.unread_count
        } catch (error) {
            console.error('fetch unread count failed', error)
        }
    }

    /**
     * 添加一条新通知（由 WebSocket 消息触发）
     */
    const addNotification = (notif: Notification) => {
        // 避免重复（可选，根据 id 去重）
        const exists = notifications.value.some(n => n.id === notif.id)
        if (exists) return
        notifications.value.unshift(notif)
        if (!notif.read) {
            unreadCount.value++
        }
    }

    /**
     * 将某条通知标记为已读（客户端标记，后端未提供接口则仅本地）
     */
    const markAsRead = (notifId: number) => {
        const notif = notifications.value.find(n => n.id === notifId)
        if (notif && !notif.read) {
            notif.read = true
            unreadCount.value = Math.max(0, unreadCount.value - 1)
            // TODO: 调用后端标记已读接口（如果有）
        }
    }

    /**
     * 将所有通知标记为已读
     */
    const markAllAsRead = () => {
        notifications.value.forEach(n => { if (!n.read) n.read = true })
        unreadCount.value = 0
        // TODO: 调用后端全部已读接口
    }

    /**
     * 清空所有通知（仅本地，可选）
     */
    const clearAll = () => {
        notifications.value = []
        unreadCount.value = 0
    }

    /**
     * 加载历史通知列表（后端如有接口）
     */
    const fetchNotifications = async (offset = 0, limit = 20) => {
        loading.value = true
        try {
            // 假设后端有 GET /api/notifications?offset=&limit=
            const res = await request.get<never, { items: Notification[]; total: number }>('/notifications', { params: { offset, limit } })
            notifications.value = res.items
            // 重新计算未读数（因为可能标记已读）
            unreadCount.value = res.items.filter(n => !n.read).length
        } catch (error) {
            console.error('fetch notifications failed', error)
        } finally {
            loading.value = false
        }
    }

    return {
        notifications,
        unreadCount,
        loading,
        fetchUnreadCount,
        addNotification,
        markAsRead,
        markAllAsRead,
        clearAll,
        fetchNotifications,
    }
})