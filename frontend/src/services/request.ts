import axios from 'axios'
import type { AxiosInstance, AxiosResponse, InternalAxiosRequestConfig } from 'axios'
import { ElMessage } from 'element-plus'

// 是否正在刷新 token
let isRefreshing = false
// 等待队列：存储需要重试的请求
let failedQueue: Array<{
    resolve: (value: unknown) => void
    reject: (reason?: any) => void
    config: InternalAxiosRequestConfig
}> = []

const processQueue = (error: Error | null, token: string | null = null) => {
    failedQueue.forEach(prom => {
        if (error) {
            prom.reject(error)
        } else {
            // 重新设置请求头的 Authorization
            if (token && prom.config.headers) {
                prom.config.headers.Authorization = `Bearer ${token}`
            }
            prom.resolve(axios(prom.config))
        }
    })
    failedQueue = []
}

const request: AxiosInstance = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
    timeout: 15000,
})

// 请求拦截器：添加 token
request.interceptors.request.use((config) => {
    const token = localStorage.getItem('access_token')
    if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`
    }
    return config
})

// 响应拦截器：处理 401 自动刷新
request.interceptors.response.use(
    (response: AxiosResponse) => response.data,
    async (error) => {
        const originalRequest = error.config
        // 如果是登录接口的 401，直接显示错误，不尝试刷新 token
        if (error.response?.status === 401 && originalRequest.url === '/auth/login') {
            const message = error.response?.data?.message || error.response?.data?.detail || '账号或密码错误'
            ElMessage.error(message)
            return Promise.reject(error)
        }
        // 防止无限循环
        if (error.response?.status === 401 && !originalRequest._retry) {
            if (isRefreshing) {
                // 正在刷新中，将请求加入队列
                return new Promise((resolve, reject) => {
                    failedQueue.push({ resolve, reject, config: originalRequest })
                })
            }

            originalRequest._retry = true
            isRefreshing = true

            const refreshToken = localStorage.getItem('refresh_token')
            if (!refreshToken) {
                // 没有 refresh token，直接跳转登录
                isRefreshing = false
                ElMessage.error('请重新登录')
                localStorage.removeItem('access_token')
                localStorage.removeItem('refresh_token')
                window.location.href = '/auth'
                return Promise.reject(error)
            }

            try {
                // 调用刷新接口
                const { data } = await axios.post(
                    `${import.meta.env.VITE_API_BASE_URL || '/api'}/auth/refresh`,
                    { refresh_token: refreshToken }
                )
                const newAccessToken = data.access_token
                localStorage.setItem('access_token', newAccessToken)
                // 更新原请求的 Authorization
                if (originalRequest.headers) {
                    originalRequest.headers.Authorization = `Bearer ${newAccessToken}`
                }
                // 处理队列中的请求
                processQueue(null, newAccessToken)
                // 重试原请求
                return axios(originalRequest)
            } catch (refreshError) {
                // 刷新失败，清除本地 token，跳转登录
                processQueue(refreshError as Error, null)
                localStorage.removeItem('access_token')
                localStorage.removeItem('refresh_token')
                ElMessage.error('登录已过期，请重新登录')
                window.location.href = '/auth'
                return Promise.reject(refreshError)
            } finally {
                isRefreshing = false
            }
        }

        // 其他错误正常抛出
        const backendMsg = error.response?.data?.message || error.response?.data?.detail
        const message = backendMsg || error.message || '网络错误'
        ElMessage.error(message)
        return Promise.reject(error)
    }
)

export default request