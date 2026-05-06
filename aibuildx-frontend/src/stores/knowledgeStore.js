import { create } from 'zustand'
import api from '../lib/api'

export const useKnowledgeStore = create((set, get) => ({
  documents: [],
  stats: {
    totalDocuments: 0,
    vectorEmbeddings: 0,
    searchQueries: 0,
    avgRelevance: 0
  },
  isLoading: false,
  error: null,

  fetchStats: async () => {
    set({ isLoading: true, error: null })
    try {
      const response = await api.get('/knowledge/stats')
      set({ stats: response.data.stats || {}, isLoading: false })
    } catch (error) {
      set({ error: error.message || error, isLoading: false })
    }
  },

  fetchDocuments: async () => {
    set({ isLoading: true, error: null })
    try {
      const response = await api.get('/knowledge/documents')
      set({ documents: response.data.documents || [], isLoading: false })
    } catch (error) {
      set({ error: error.message || error, isLoading: false })
    }
  },

  uploadDocument: async (file) => {
    set({ isLoading: true, error: null })
    try {
      const formData = new FormData()
      formData.append('document', file)
      await api.post('/knowledge/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      await get().fetchDocuments()
      set({ isLoading: false })
    } catch (error) {
      set({ error: error.message || error, isLoading: false })
    }
  },

  searchDocuments: async (query) => {
    set({ isLoading: true, error: null })
    try {
      const response = await api.get('/knowledge/search', { params: { q: query } })
      set({ isLoading: false })
      return response.data.documents || []
    } catch (error) {
      set({ error: error.message || error, isLoading: false })
      return []
    }
  }
}))