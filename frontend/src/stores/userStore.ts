import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { User } from '@/types'
import { login as apiLogin, logout as apiLogout, getUserInfo } from '@/services/auth'

export const useUserStore = defineStore('user', () => {
    const user = ref<User | null>(null)
    const isLoggedIn = ref(false)

    const login = async (student_id: string, password: string) => {
        const loginRes = await apiLogin({ student_id, password })
        user.value = loginRes.user
        isLoggedIn.value = true
        return loginRes
    }

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