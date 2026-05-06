import { create } from 'zustand'
import { persist } from 'zustand/middleware'

const DEFAULT_SETTINGS = {
  security: {
    require2FA: true,
    passwordPolicy: 'Strong',
    auditLogging: true
  },
  integrations: {
    allowExternalApi: true,
    enableMonitoring: true,
    webhookUrl: ''
  },
  localization: {
    timezone: 'UTC',
    currency: 'INR',
    dateFormat: 'DD/MM/YYYY'
  }
}

export const useSystemStore = create(
  persist(
    (set) => ({
      settings: DEFAULT_SETTINGS,
      updateSetting: (section, key, value) =>
        set((state) => ({
          settings: {
            ...state.settings,
            [section]: {
              ...state.settings[section],
              [key]: value
            }
          }
        })),
      resetSettings: () => set({ settings: DEFAULT_SETTINGS })
    }),
    {
      name: 'aibuildx-system-settings'
    }
  )
)
