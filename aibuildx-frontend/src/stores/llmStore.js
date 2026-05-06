import { create } from 'zustand'
import api from '../lib/api'

export const useLLMStore = create((set, get) => ({
  models: [],
  systemStats: {
    cpuUtilization: 0,
    memoryUsage: 0,
    gpuUtilization: 0,
    activeRequests: 0
  },
  isLoading: false,
  error: null,

  fetchModels: async () => {
    set({ isLoading: true, error: null })
    try {
      const response = await api.get('/llm/models')
      set({ models: response.data.models || [], isLoading: false })
    } catch (error) {
      set({ error: error.message || error, isLoading: false })
    }
  },

  fetchSystemStats: async () => {
    set({ isLoading: true, error: null })
    try {
      const response = await api.get('/llm/stats')
      set({ systemStats: response.data.stats || {}, isLoading: false })
    } catch (error) {
      set({ error: error.message || error, isLoading: false })
    }
  }
}))