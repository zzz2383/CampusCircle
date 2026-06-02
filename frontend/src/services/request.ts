// src/services/request.ts
import axios from 'axios'
import type { AxiosInstance, AxiosResponse } from 'axios'
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
    (response: AxiosResponse) => response.data,  // 直接返回 data
    (error) => {
        const message = error.response?.data?.detail || error.message || '网络错误'
        ElMessage.error(message)
        // 如果是 401 未认证，清除本地 token 并跳转登录
        if (error.response?.status === 401) {
            localStorage.removeItem('access_token')
            window.location.href = '/auth'
        }
        return Promise.reject(error)
    }
)

export default request