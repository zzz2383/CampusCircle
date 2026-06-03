import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getLostItems, createLostItem, markAsFound } from '@/services/lostItem'
import type { LostItem, CreateLostItemPayload } from '@/types'

// 辅助函数：计算是否过期
const computeExpired = (expiresAt: string): boolean => {
    return new Date(expiresAt) < new Date()
}

export const useLostItemStore = defineStore('lostItem', () => {
    const items = ref<LostItem[]>([])
    const total = ref(0)
    const loading = ref(false)
    const currentFilter = ref<'all' | 'lost' | 'found'>('all')
    const offset = ref(0)
    const limit = 20
    const hasMore = ref(false)

    const fetchItems = async (reset = true) => {
        if (loading.value) return
        loading.value = true
        try {
            const params: any = {
                offset: reset ? 0 : offset.value,
                limit,
            }
            if (currentFilter.value === 'lost') params.is_lost = true
            else if (currentFilter.value === 'found') params.is_lost = false

            const res = await getLostItems(params)
            const itemsWithExpired = res.items.map(item => ({
                ...item,
                is_expired: computeExpired(item.expires_at)
            }))

            if (reset) {
                items.value = itemsWithExpired
                offset.value = itemsWithExpired.length
            } else {
                items.value.push(...itemsWithExpired)
                offset.value += itemsWithExpired.length
            }
            total.value = res.total
            hasMore.value = items.value.length < res.total
        } catch (error) {
            console.error('fetchLostItems failed', error)
        } finally {
            loading.value = false
        }
    }

    const loadMore = () => {
        if (!hasMore.value || loading.value) return
        fetchItems(false)
    }

    const setFilter = async (filter: 'all' | 'lost' | 'found') => {
        currentFilter.value = filter
        offset.value = 0
        await fetchItems(true)
    }

    const publishItem = async (data: CreateLostItemPayload) => {
        const newItem = await createLostItem(data)
        const newItemWithExpired = {
            ...newItem,
            is_expired: computeExpired(newItem.expires_at)
        }
        items.value.unshift(newItemWithExpired)
        total.value++
        return newItemWithExpired
    }

    const setFound = async (id: number) => {
        await markAsFound(id)
        const item = items.value.find(i => i.id === id)
        if (item) {
            item.is_found = true
        }
    }

    return {
        items,
        total,
        loading,
        hasMore,
        currentFilter,
        fetchItems,
        loadMore,
        setFilter,
        publishItem,
        setFound,
    }
})