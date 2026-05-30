import api from './api'
import type { PostCreateRequest, PostDTO, PostListResponse } from '../types/api'

export const postService = {
  async create(data: PostCreateRequest): Promise<PostDTO> {
    const res = await api.post<PostDTO>('/posts', data)
    return res.data
  },

  async list(offset = 0, limit = 20, tag?: string): Promise<PostListResponse> {
    const params: Record<string, string | number> = { offset, limit }
    if (tag) params.tag = tag
    const res = await api.get<PostListResponse>('/posts', { params })
    return res.data
  },

  async getById(id: number): Promise<PostDTO> {
    const res = await api.get<PostDTO>(`/posts/${id}`)
    return res.data
  },

  async delete(id: number): Promise<void> {
    await api.delete(`/posts/${id}`)
  },
}
