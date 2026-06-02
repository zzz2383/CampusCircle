// src/services/auth.ts
import request from './request'
import type { LoginPayload, RegisterPayload, TokenDTO, User } from '@/types'

/**
 * 用户登录 — 对接真实后端
 *
 * Given: 用户输入正确的学号 (student_id) 和密码
 * When:  调用 login(loginPayload)
 * Then:  返回 TokenDTO，存储 access_token 和 user 信息
 */
export const login = async (payload: LoginPayload): Promise<TokenDTO> => {
    // 后端路径: POST /api/auth/login
    const data = await request.post<never, TokenDTO>('/auth/login', payload)
    // 存储 token
    localStorage.setItem('access_token', data.access_token)
    return data
}

/**
 * 用户注册 — 对接真实后端
 *
 * Given: 用户填写注册信息（student_id, email, password, nickname 可选）
 * When:  调用 register(registerPayload)
 * Then:  返回 UserDTO（注册成功后的用户信息，但不会自动登录）
 */
export const register = async (payload: RegisterPayload): Promise<User> => {
    // 后端路径: POST /api/auth/register
    return await request.post<never, User>('/auth/register', payload)
}

/**
 * 获取当前用户信息
 * GET /api/auth/me
 */
export const getUserInfo = async (): Promise<User> => {
    return await request.get('/auth/me')
}

/**
 * 登出
 */
export const logout = () => {
    localStorage.removeItem('access_token')
}