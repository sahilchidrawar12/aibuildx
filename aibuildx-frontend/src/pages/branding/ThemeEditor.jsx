import { useMemo } from 'react'
import { Palette, Brush, LayoutGrid } from 'lucide-react'
import { useBrandingStore } from '../../stores/brandingStore'

function ThemeEditor() {
  const {
    themeMode,
    accentColor,
    layoutDensity,
    setThemeMode,
    setAccentColor,
    setLayoutDensity,
    resetTheme
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

  return (
    <div className="space-y-6">
      <div className="rounded-3xl border border-[rgba(0,212,255,0.15)] bg-[#0f1629] p-6">
        <p className="text-sm uppercase tracking-[0.24em] text-[#00d4ff]">Branding</p>
        <h1 className="mt-3 text-3xl font-semibold text-[#e2e8f0]">Theme Editor</h1>
        <p className="mt-2 text-sm text-[#94a3b8]">Control colors, typography, and interface tone for your company experience.</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="rounded-3xl border border-[#1f2a43] bg-[#09101d] p-6">
          <div className="flex items-center gap-3 mb-4">
            <Palette className="h-6 w-6 text-[#00d4ff]" />
            <div>
              <h2 className="text-lg font-semibold text-[#e2e8f0]">Theme</h2>
              <p className="text-sm text-[#94a3b8]">Switch between brand palettes.</p>
            </div>
          </div>
          <select value={themeMode} onChange={(e) => setThemeMode(e.target.value)} className="w-full rounded-3xl border border-[#162039] bg-[#07101f] px-4 py-3 text-sm text-[#e2e8f0] outline-none">
            <option>Dark</option>
            <option>Deep Ocean</option>
            <option>Slate</option>
            <option>Corporate</option>
          </select>
        </div>

        <div className="rounded-3xl border border-[#1f2a43] bg-[#09101d] p-6">
          <div className="flex items-center gap-3 mb-4">
            <Brush className="h-6 w-6 text-[#00d4ff]" />
            <div>
              <h2 className="text-lg font-semibold text-[#e2e8f0]">Accent Color</h2>
              <p className="text-sm text-[#94a3b8]">Choose a primary highlight color.</p>
            </div>
          </div>
          <input type="color" value={accentColor} onChange={(e) => setAccentColor(e.target.value)} className="h-16 w-full rounded-3xl border border-[#162039] bg-[#07101f] p-2" />
          <div className="mt-4 rounded-3xl bg-[#07101f] p-4 text-sm text-[#e2e8f0]">
            Current accent:
            <span className="ml-2 font-semibold" style={{ color: accentColor }}>{accentColor}</span>
          </div>
        </div>

        <div className="rounded-3xl border border-[#1f2a43] bg-[#09101d] p-6">
          <div className="flex items-center gap-3 mb-4">
            <LayoutGrid className="h-6 w-6 text-[#00d4ff]" />
            <div>
              <h2 className="text-lg font-semibold text-[#e2e8f0]">Layout</h2>
              <p className="text-sm text-[#94a3b8]">Configure panel density and spacing.</p>
            </div>
          </div>
          <div className="space-y-3">
            {['Compact', 'Balanced', 'Spacious'].map((option) => (
              <label key={option} className={`flex items-center gap-3 rounded-3xl border p-4 cursor-pointer transition ${layoutDensity === option ? 'border-[#00d4ff] bg-[#0b1c2d]' : 'border-[#162039] bg-[#07101f]'}`}>
                <input type="radio" name="layout" checked={layoutDensity === option} className="h-4 w-4 accent-[#00d4ff]" onChange={() => setLayoutDensity(option)} />
                <span className="text-sm text-[#e2e8f0]">{option}</span>
              </label>
            ))}
          </div>
        </div>
      </div>

      <div className="rounded-3xl border border-[#1f2a43] bg-[#09101d] p-6">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <h2 className="text-lg font-semibold text-[#e2e8f0]">Preview</h2>
            <p className="text-sm text-[#94a3b8]">A quick preview of your current theme settings.</p>
          </div>
          <div className="inline-flex items-center gap-3 rounded-3xl border border-[#162039] bg-[#07101f] px-4 py-3 text-sm text-[#94a3b8]">
            <span className="h-4 w-4 rounded-full" style={{ backgroundColor: accentColor }} /> Accent active
          </div>
        </div>
        <div className="mt-6 grid gap-4 md:grid-cols-2">
          <div className="rounded-3xl border border-[#162039] bg-[#07101f] p-4">
            <p className="text-sm text-[#94a3b8]">Top navigation</p>
            <div className="mt-4 h-20 rounded-3xl" style={{ background: `linear-gradient(90deg, ${accentColor}, ${primaryColor})` }} />
          </div>
          <div className="rounded-3xl border border-[#162039] bg-[#07101f] p-4">
            <p className="text-sm text-[#94a3b8]">Sidebar</p>
            <div className="mt-4 h-20 rounded-3xl" style={{ backgroundColor: '#0b1220' }}>
              <div className="h-full rounded-3xl" style={{ background: `linear-gradient(180deg, rgba(255,255,255,0.04), transparent)` }} />
            </div>
          </div>
        </div>
      </div>

      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div className="rounded-3xl border border-[#162039] bg-[#07101f] p-4 text-sm text-[#94a3b8]">
          <p className="font-semibold text-[#e2e8f0]">Current theme</p>
          <p className="mt-2">{themeMode} • {layoutDensity} density</p>
        </div>
        <button onClick={resetTheme} className="inline-flex items-center justify-center rounded-3xl bg-[#0f172a] px-6 py-3 text-sm font-semibold text-[#00d4ff] hover:bg-[#112138] transition">
          Reset to default
        </button>
      </div>
    </div>
  )
}

export default ThemeEditor
