import { create } from 'zustand'
import { persist } from 'zustand/middleware'

const defaultBranding = {
  brandName: 'AIBuildX',
  themeMode: 'Dark',
  accentColor: '#00d4ff',
  layoutDensity: 'Balanced',
  logoText: 'AIBuildX',
  logoFilename: '',
  logoPreview: '',
  brandingUpdatedAt: new Date().toISOString()
}

export const useBrandingStore = create(
  persist(
    (set, get) => ({
      ...defaultBranding,
      setBrandName: (brandName) => set({ brandName, brandingUpdatedAt: new Date().toISOString() }),
      setThemeMode: (themeMode) => set({ themeMode, brandingUpdatedAt: new Date().toISOString() }),
      setAccentColor: (accentColor) => set({ accentColor, brandingUpdatedAt: new Date().toISOString() }),
      setLayoutDensity: (layoutDensity) => set({ layoutDensity, brandingUpdatedAt: new Date().toISOString() }),
      setLogoText: (logoText) => set({ logoText, brandingUpdatedAt: new Date().toISOString() }),
      setLogoPreview: (logoPreview, logoFilename = '') => set({ logoPreview, logoFilename, brandingUpdatedAt: new Date().toISOString() }),
      resetLogo: () => set({ logoText: defaultBranding.logoText, logoFilename: '', logoPreview: '', brandingUpdatedAt: new Date().toISOString() }),
      resetTheme: () => set({ themeMode: defaultBranding.themeMode, accentColor: defaultBranding.accentColor, layoutDensity: defaultBranding.layoutDensity, brandingUpdatedAt: new Date().toISOString() }),
      exportBranding: () => {
        const { brandName, themeMode, accentColor, layoutDensity, logoText, logoFilename, logoPreview } = get()
        return {
          brandName,
          themeMode,
          accentColor,
          layoutDensity,
          logoText,
          logoFilename,
          logoPreview
        }
      }
    }),
    {
      name: 'branding-storage',
      partialize: (state) => ({
        brandName: state.brandName,
        themeMode: state.themeMode,
        accentColor: state.accentColor,
        layoutDensity: state.layoutDensity,
        logoText: state.logoText,
        logoFilename: state.logoFilename,
        logoPreview: state.logoPreview,
        brandingUpdatedAt: state.brandingUpdatedAt
      })
    }
  )
)
