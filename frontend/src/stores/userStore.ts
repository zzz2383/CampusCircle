// src/stores/userStore.ts
import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { User } from '@/types'
import { login as apiLogin, logout as apiLogout, getUserInfo } from '@/services/auth'

export const useUserStore = defineStore('user', () => {
    const user = ref<User | null>(null)
    const isLoggedIn = ref(false)

    /**
     * 登录 — 调用真实后端
     * 成功后自动设置 user 和 isLoggedIn 状态
     */
    const login = async (student_id: string, password: string) => {
        const tokenDTO = await apiLogin({ student_id, password })
        user.value = tokenDTO.user
        isLoggedIn.value = true
        return tokenDTO
    }

    /**
     * 初始化：尝试从 token 恢复用户信息（用于页面刷新）
     */
    const initAuth = async () => {
        const token = localStorage.getItem('access_token')
        if (token && !user.value) {
            try {
                const userInfo = await getUserInfo()
                user.value = userInfo
                isLoggedIn.value = true
            } catch {
                logout()
            }
        }
    }

    const logout = () => {
        apiLogout()
        user.value = null
        isLoggedIn.value = false
    }

    return { user, isLoggedIn, login, initAuth, logout }
})