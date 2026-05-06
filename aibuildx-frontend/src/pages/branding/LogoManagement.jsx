import { useState, useCallback } from 'react'
import { ImagePlus, RefreshCcw } from 'lucide-react'
import { useBrandingStore } from '../../stores/brandingStore'

function LogoManagement() {
  const {
    logoText,
    logoPreview,
    logoFilename,
    setLogoText,
    setLogoPreview,
    resetLogo
  } = useBrandingStore()

  const [uploadedFileName, setUploadedFileName] = useState(logoFilename || '')

  const handleFileChange = useCallback((event) => {
    const file = event.target.files?.[0]
    if (!file) return

    const reader = new FileReader()
    reader.onload = () => {
      if (typeof reader.result === 'string') {
        setLogoPreview(reader.result, file.name)
        setUploadedFileName(file.name)
      }
    }
    reader.readAsDataURL(file)
  }, [setLogoPreview])

  return (
    <div className="space-y-6">
      <div className="rounded-3xl border border-[rgba(0,212,255,0.15)] bg-[#0f1629] p-6">
        <p className="text-sm uppercase tracking-[0.24em] text-[#00d4ff]">Branding</p>
        <h1 className="mt-3 text-3xl font-semibold text-[#e2e8f0]">Logo Management</h1>
        <p className="mt-2 text-sm text-[#94a3b8]">Upload brand marks and configure logo usage across the app.</p>
      </div>

      <div className="rounded-3xl border border-[#1f2a43] bg-[#09101d] p-6">
        <div className="flex items-center gap-3 mb-5">
          <ImagePlus className="h-6 w-6 text-[#00d4ff]" />
          <div>
            <h2 className="text-lg font-semibold text-[#e2e8f0]">Brand mark</h2>
            <p className="text-sm text-[#94a3b8]">Upload a logo file for the header and report exports.</p>
          </div>
        </div>
        <label className="flex min-h-[180px] flex-col items-center justify-center rounded-3xl border-2 border-dashed border-[#324255] bg-[#07101f] p-6 text-center text-sm text-[#94a3b8] cursor-pointer hover:border-[#00d4ff] hover:text-[#e2e8f0]">
          <span>Drag a PNG, SVG, or JPG file here</span>
          <input type="file" accept="image/png,image/svg+xml,image/jpeg" className="hidden" onChange={handleFileChange} />
        </label>
        {(uploadedFileName || logoFilename) && (
          <div className="mt-6 rounded-3xl border border-[#162039] bg-[#07101f] p-4 text-sm text-[#e2e8f0]">
            Uploaded: {uploadedFileName || logoFilename}
          </div>
        )}
      </div>

      <div className="rounded-3xl border border-[#1f2a43] bg-[#09101d] p-6">
        <div className="flex items-center justify-between gap-3">
          <div>
            <h2 className="text-lg font-semibold text-[#e2e8f0]">Logo tag</h2>
            <p className="text-sm text-[#94a3b8]">Override the default product mark text.</p>
          </div>
          <input value={logoText} onChange={(e) => setLogoText(e.target.value)} className="rounded-3xl border border-[#162039] bg-[#07101f] px-4 py-3 text-sm text-[#e2e8f0] outline-none" />
        </div>
        <div className="mt-8 flex flex-wrap items-center gap-4">
          <div className="rounded-3xl border border-[#162039] bg-[#07101f] p-4 text-center w-full sm:w-auto">
            <p className="text-sm text-[#94a3b8]">Current preview</p>
            {logoPreview ? (
              <img src={logoPreview} alt="Logo preview" className="mx-auto mt-3 h-16 w-16 rounded-lg object-contain" />
            ) : (
              <p className="mt-2 text-xl font-semibold text-[#e2e8f0]">{logoText}</p>
            )}
          </div>
          <button onClick={() => { resetLogo(); setUploadedFileName('') }} className="inline-flex items-center gap-2 rounded-2xl bg-[#00d4ff] px-5 py-3 text-sm font-semibold text-[#07101f] hover:bg-[#33e7ff] transition">
            <RefreshCcw className="w-4 h-4" /> Reset logo
          </button>
        </div>
      </div>
    </div>
  )
}

export default LogoManagement
