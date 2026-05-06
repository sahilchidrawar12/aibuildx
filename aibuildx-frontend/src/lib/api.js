import axios from 'axios'
import { useAuthStore } from '../stores/authStore'

const API_BASE_URL = import.meta.env.VITE_API_URL || window.location.origin

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: {
    'Accept': 'application/json'
  }
})

api.interceptors.request.use((config) => {
  const user = useAuthStore.getState().user
  if (user) {
    config.headers = config.headers || {}
    config.headers['X-User-Id'] = user.id
    config.headers['X-Company-Id'] = user.companyId
    config.headers['X-User-Role'] = user.role
  }
  return config
})

api.interceptors.response.use(
  response => response,
  error => {
    if (error.response) {
      return Promise.reject(error.response.data || error.response)
    }
    return Promise.reject(error)
  }
)

export default api
