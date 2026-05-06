import { create } from 'zustand'
import { useAuthStore } from './authStore'
import api from '../lib/api'

export const JOB_STATUS = {
  PENDING: 'pending',
  PROCESSING: 'processing',
  COMPLETED: 'completed',
  FAILED: 'failed',
  CANCELLED: 'cancelled'
}

export const JOB_TYPES = {
  CAD_TO_BIM: 'cad_to_bim',
  STRUCTURAL_ANALYSIS: 'structural_analysis',
  DETAILING_CORRECTION: 'detailing_correction'
}

export const useJobStore = create((set, get) => ({
  jobs: [],
  currentJob: null,
  isLoading: false,
  error: null,

  fetchJobs: async () => {
    set({ isLoading: true, error: null })
    try {
      const response = await api.get('/jobs')
      set({ jobs: response.data.jobs || [], isLoading: false })
    } catch (error) {
      set({ error: error.message || error, isLoading: false })
    }
  },

  fetchJobById: async (jobId) => {
    set({ isLoading: true, error: null })
    try {
      const response = await api.get(`/jobs/${jobId}`)
      set({ currentJob: response.data.job || null, isLoading: false })
      return response.data.job
    } catch (error) {
      set({ error: error.message || error, isLoading: false })
      return null
    }
  },

  uploadJob: async (file, metadata = {}) => {
    set({ isLoading: true, error: null })
    try {
      const formData = new FormData()
      formData.append('file', file)
      if (metadata.companyId) formData.append('company_id', metadata.companyId)
      if (metadata.userId) formData.append('user_id', metadata.userId)

      const response = await api.post('/upload', formData)

      await get().fetchJobs()
      set({ isLoading: false })
      return response.data
    } catch (error) {
      set({ error: error.message || error, isLoading: false })
      return { status: 'error', message: error.message || error }
    }
  },

  updateJobStatus: (jobId, status, progress = null) => {
    set(state => ({
      jobs: state.jobs.map(job =>
        job.id === jobId
          ? {
              ...job,
              status,
              progress: progress !== null ? progress : job.progress,
              ...(status === JOB_STATUS.COMPLETED && { completedAt: new Date().toISOString() })
            }
          : job
      ),
      currentJob: state.currentJob?.id === jobId
        ? { ...state.currentJob, status, progress: progress !== null ? progress : state.currentJob.progress }
        : state.currentJob
    }))
  },

  getJobById: (jobId) => {
    return get().jobs.find(job => job.id === jobId)
  },

  cancelJob: async (jobId) => {
    try {
      get().updateJobStatus(jobId, JOB_STATUS.CANCELLED)
      return { success: true }
    } catch (error) {
      return { success: false, error: error.message }
    }
  },

  clearError: () => set({ error: null }),

  getJobsByStatus: (status) => {
    return get().jobs.filter(job => job.status === status)
  },

  getUserJobs: () => {
    const { user } = useAuthStore.getState()
    if (!user?.id) return []
    return get().jobs.filter(job => job.user_id === user.id)
  },

  getCompanyJobs: () => {
    const { user } = useAuthStore.getState()
    if (!user?.companyId) return []
    return get().jobs.filter(job => job.company_id === user.companyId)
  }
}))