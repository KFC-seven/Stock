import { defineStore } from 'pinia'
import { ref } from 'vue'
import { authApi, type TokenResponse } from '../api/auth'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const username = ref('')
  const displayName = ref('')
  const userId = ref(0)
  const loggedIn = ref(!!token.value)

  function setUser(data: TokenResponse) {
    token.value = data.access_token
    username.value = data.username
    displayName.value = data.display_name
    userId.value = data.user_id
    loggedIn.value = true
    localStorage.setItem('token', data.access_token)
    localStorage.setItem('user', JSON.stringify({ username: data.username, display_name: data.display_name, user_id: data.user_id }))
  }

  function restoreUser() {
    const saved = localStorage.getItem('user')
    if (saved) {
      try {
        const u = JSON.parse(saved)
        username.value = u.username
        displayName.value = u.display_name
        userId.value = u.user_id
        loggedIn.value = true
      } catch { /* ignore */ }
    }
  }

  async function login(loginData: { username: string; password: string }) {
    const res = await authApi.login(loginData)
    setUser(res.data)
  }

  async function register(registerData: { username: string; password: string; display_name: string }) {
    const res = await authApi.register(registerData)
    setUser(res.data)
  }

  function logout() {
    token.value = ''
    username.value = ''
    displayName.value = ''
    userId.value = 0
    loggedIn.value = false
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  restoreUser()

  return { token, username, displayName, userId, loggedIn, login, register, logout }
})
