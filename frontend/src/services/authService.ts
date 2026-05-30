import api from './api'
import type { UserRegisterRequest, UserLoginRequest, UserDTO, TokenDTO } from '../types/api'

export const authService = {
  async register(data: UserRegisterRequest): Promise<UserDTO> {
    const res = await api.post<UserDTO>('/auth/register', data)
    return res.data
  },

  async login(data: UserLoginRequest): Promise<TokenDTO> {
    const res = await api.post<TokenDTO>('/auth/login', data)
    return res.data
  },

  async getMe(): Promise<UserDTO> {
    const res = await api.get<UserDTO>('/auth/me')
    return res.data
  },
}
