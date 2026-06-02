// src/services/request.ts
import axios from 'axios'
import type { AxiosInstance } from 'axios'
import { ElMessage } from 'element-plus'

const request: AxiosInstance = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || '/api',  // 与后端 /api 前缀匹配
    timeout: 15000,
})

// 请求拦截器：自动附加 token
request.interceptors.request.use((config) => {
    const token = localStorage.getItem('access_token')
    if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`
    }
    return config
})

// 响应拦截器：统一错误处理
request.interceptors.response.use(
    (response) => response.data,
    async (error) => {
        const originalRequest = error.config
        // 401 未认证：清除本地 token 并提示跳转
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true
            ElMessage.error('登录已过期，请重新登录')
            localStorage.removeItem('access_token')
            // 延迟跳转，让用户看到提示
            setTimeout(() => {
                window.location.href = '/auth'
            }, 1500)
            return Promise.reject(error)
        }
        const message = error.response?.data?.detail || error.message || '网络错误'
        ElMessage.error(message)
        return Promise.reject(error)
    }
)
export default request