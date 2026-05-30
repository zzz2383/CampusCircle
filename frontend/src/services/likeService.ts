import api from './api'
import type { LikeResultDTO } from '../types/api'

export const likeService = {
  async like(postId: number): Promise<LikeResultDTO> {
    const res = await api.post<LikeResultDTO>(`/posts/${postId}/like`)
    return res.data
  },

  async unlike(postId: number): Promise<LikeResultDTO> {
    const res = await api.delete<LikeResultDTO>(`/posts/${postId}/like`)
    return res.data
  },
}
