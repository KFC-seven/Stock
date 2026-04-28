import api from './index'

export interface LoginData {
  username: string
  password: string
}

export interface RegisterData {
  username: string
  password: string
  display_name: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
  user_id: number
  username: string
  display_name: string
}

export const authApi = {
  login: (data: LoginData) => api.post<TokenResponse>('/auth/login', data),
  register: (data: RegisterData) => api.post<TokenResponse>('/auth/register', data),
  me: () => api.get('/auth/me'),
}
