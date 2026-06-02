import request from './request'
import type { LoginPayload, RegisterPayload, User } from '@/types'

// 假设后端登录返回结构包含 refresh_token
export interface LoginResponse {
    access_token: string
    refresh_token: string
    token_type: string
    user: User
}

export const login = async (payload: LoginPayload): Promise<LoginResponse> => {
    const data = await request.post<never, LoginResponse>('/auth/login', payload)
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('refresh_token', data.refresh_token)
    return data
}

export const register = async (payload: RegisterPayload): Promise<User> => {
    return await request.post<never, User>('/auth/register', payload)
}

export const getUserInfo = async (): Promise<User> => {
    return await request.get('/auth/me')
}

export const logout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
}