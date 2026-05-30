import { ref } from 'vue'
import { defineStore } from 'pinia'
import type { UserDTO, TokenDTO } from '../types/api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('token'))
  const currentUser = ref<UserDTO | null>(null)

  const isLoggedIn = () => !!token.value

  function setAuth(authData: TokenDTO) {
    token.value = authData.access_token
    currentUser.value = authData.user
    localStorage.setItem('token', authData.access_token)
  }

  function logout() {
    token.value = null
    currentUser.value = null
    localStorage.removeItem('token')
  }

  return { token, currentUser, isLoggedIn, setAuth, logout }
})
