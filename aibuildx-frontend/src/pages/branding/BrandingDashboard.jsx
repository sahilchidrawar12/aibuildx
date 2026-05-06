import { useMemo } from 'react'
import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { Palette, Image, Type, Settings, Eye, Download } from 'lucide-react'
import { useBrandingStore } from '../../stores/brandingStore'

function BrandingDashboard() {
  const navigate = useNavigate()
  const {
    brandName,
    themeMode,
    accentColor,
    layoutDensity,
    logoText,
    logoPreview,
    logoFilename,
    brandingUpdatedAt,
    exportBranding
  } = useBrandingStore()

  const primaryColor = useMemo(() => {
    switch (themeMode) {
      case 'Deep Ocean':
        return '#0b3d91'
      case 'Slate':
        return '#64748b'
      case 'Corporate':
        return '#0f4c81'
      default:
        return '#0284c7'
    }
  }, [themeMode])

  const logoInitials = useMemo(() => {
    return logoText
      .split(' ')
      .map((word) => word[0])
      .slice(0, 2)
      .join('')
      .toUpperCase()
  }, [logoText])

  const handleExport = () => {
    const payload = exportBranding()
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const anchor = document.createElement('a')
    anchor.href = url
    anchor.download = `${brandName.toLowerCase().replace(/\s+/g, '_')}_branding.json`
    document.body.appendChild(anchor)
    anchor.click()
    anchor.remove()
    URL.revokeObjectURL(url)
  }

  const currentBranding = [
    {
      name: 'Primary Logo',
      type: 'Logo',
      status: logoText || logoPreview ? 'Active' : 'Draft',
      lastModified: logoFilename ? `Updated ${new Date(brandingUpdatedAt).toLocaleDateString()}` : 'Not uploaded'
    },
    {
      name: 'Color Palette',
      type: 'Theme',
      status: accentColor ? 'Active' : 'Draft',
      lastModified: accentColor ? `Updated ${new Date(brandingUpdatedAt).toLocaleDateString()}` : 'Not configured'
    },
    {
      name: 'Typography',
      type: 'Fonts',
      status: 'Active',
      lastModified: 'Stable'
    },
    {
      name: 'Layout Density',
      type: 'Design',
      status: layoutDensity ? 'Active' : 'Draft',
      lastModified: layoutDensity ? `Updated ${new Date(brandingUpdatedAt).toLocaleDateString()}` : 'Not configured'
    }
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Branding & Customization</h1>
          <p className="text-secondary-400 mt-1">Manage AIBuildX branding elements and visual identity.</p>
        </div>
        <div className="flex flex-wrap gap-3">
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="btn-secondary"
            onClick={() => navigate('/company-admin/branding/theme')}
          >
            <Eye className="w-5 h-5 mr-2" />
            Theme Editor
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="btn-secondary"
            onClick={() => navigate('/company-admin/branding/logo')}
          >
            <Image className="w-5 h-5 mr-2" />
            Logo Manager
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="btn-primary"
            onClick={handleExport}
          >
            <Download className="w-5 h-5 mr-2" />
            Export Settings
          </motion.button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="lg:col-span-2 bg-secondary-800 border border-secondary-700 rounded-lg p-6"
        >
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div>
              <h2 className="text-xl font-bold text-white mb-2">Current Brand Identity</h2>
              <p className="text-secondary-400 text-sm">A quick overview of the active visual identity and settings.</p>
            </div>
            <div className="flex items-center gap-3 text-sm text-secondary-300">
              <span>{brandName || 'AIBuildX'}</span>
              <span className="h-2 w-2 rounded-full bg-green-400" aria-hidden="true" />
              <span>{themeMode || 'Light'} mode</span>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
            <div className="bg-secondary-900 rounded-lg p-6 text-center">
              <div className="mx-auto mb-4 flex h-24 w-24 items-center justify-center rounded-lg" style={{ backgroundColor: accentColor || '#1f2937' }}>
                {logoPreview ? (
                  <img src={logoPreview} alt="Brand Logo" className="max-h-full max-w-full object-contain" />
                ) : (
                  <span className="text-white font-bold text-2xl">{logoInitials || 'AX'}</span>
                )}
              </div>
              <h3 className="text-white font-medium mb-2">{logoText || 'AIBuildX'}</h3>
              <p className="text-secondary-400 text-sm">Primary brand mark</p>
            </div>

            <div className="space-y-4">
              <div className="rounded-lg border border-secondary-700 bg-secondary-900 p-4">
                <p className="text-secondary-400 text-sm">Theme mode</p>
                <p className="text-white font-medium">{themeMode || 'Light'}</p>
              </div>
              <div className="rounded-lg border border-secondary-700 bg-secondary-900 p-4">
                <p className="text-secondary-400 text-sm">Accent color</p>
                <div className="mt-3 flex items-center gap-3">
                  <div className="h-10 w-10 rounded-full border border-secondary-600" style={{ backgroundColor: accentColor || '#0284c7' }} />
                  <p className="text-white font-medium">{accentColor || '#0284c7'}</p>
                </div>
              </div>
              <div className="rounded-lg border border-secondary-700 bg-secondary-900 p-4">
                <p className="text-secondary-400 text-sm">Density</p>
                <p className="text-white font-medium">{layoutDensity || 'Comfortable'}</p>
              </div>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-secondary-800 border border-secondary-700 rounded-lg p-6"
        >
          <h2 className="text-xl font-bold text-white mb-4">Quick Actions</h2>
          <div className="space-y-3">
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="w-full flex items-center space-x-3 p-4 bg-primary-600/20 border border-primary-500/30 rounded-lg hover:bg-primary-600/30 transition-colors text-left"
              onClick={() => navigate('/company-admin/branding/theme')}
            >
              <Palette className="w-5 h-5 text-primary-400" />
              <div>
                <p className="text-white font-medium">Edit Theme</p>
                <p className="text-secondary-400 text-sm">Customize colors & styles</p>
              </div>
            </motion.button>

            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="w-full flex items-center space-x-3 p-4 bg-secondary-700/50 border border-secondary-600 rounded-lg hover:bg-secondary-700 transition-colors text-left"
              onClick={() => navigate('/company-admin/branding/logo')}
            >
              <Image className="w-5 h-5 text-secondary-400" />
              <div>
                <p className="text-white font-medium">Update Logo</p>
                <p className="text-secondary-400 text-sm">Change brand assets</p>
              </div>
            </motion.button>

            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="w-full flex items-center space-x-3 p-4 bg-secondary-700/50 border border-secondary-600 rounded-lg hover:bg-secondary-700 transition-colors text-left"
              onClick={handleExport}
            >
              <Download className="w-5 h-5 text-secondary-400" />
              <div>
                <p className="text-white font-medium">Export Settings</p>
                <p className="text-secondary-400 text-sm">Save a local branding package</p>
              </div>
            </motion.button>
          </div>
        </motion.div>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="bg-secondary-800 border border-secondary-700 rounded-lg p-6"
      >
        <h2 className="text-xl font-bold text-white mb-4">Branding Assets</h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {currentBranding.map((element, index) => (
            <div key={index} className="bg-secondary-700/50 border border-secondary-600 rounded-lg p-4">
              <div className="flex items-center justify-between mb-3">
                <div className={`p-2 rounded ${
                  element.type === 'Logo' ? 'bg-blue-600/20' :
                  element.type === 'Theme' ? 'bg-purple-600/20' :
                  element.type === 'Fonts' ? 'bg-green-600/20' :
                  'bg-yellow-600/20'
                }`}>
                  {element.type === 'Logo' && <Image className="w-4 h-4 text-blue-400" />}
                  {element.type === 'Theme' && <Palette className="w-4 h-4 text-purple-400" />}
                  {element.type === 'Fonts' && <Type className="w-4 h-4 text-green-400" />}
                  {element.type === 'Design' && <Settings className="w-4 h-4 text-yellow-400" />}
                </div>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  element.status === 'Active' ? 'bg-green-500/20 text-green-400' : 'bg-yellow-500/20 text-yellow-400'
                }`}>
                  {element.status}
                </span>
              </div>

              <h3 className="text-white font-medium mb-1">{element.name}</h3>
              <p className="text-secondary-400 text-sm mb-2">{element.type}</p>
              <p className="text-secondary-500 text-xs">{element.lastModified}</p>
            </div>
          ))}
        </div>
      </motion.div>
    </div>
  )
}

export default BrandingDashboard