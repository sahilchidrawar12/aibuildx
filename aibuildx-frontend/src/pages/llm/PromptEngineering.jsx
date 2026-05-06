import { useState } from 'react'
import { Edit3, Sparkles, Layers } from 'lucide-react'

function PromptEngineering() {
  const [prompt, setPrompt] = useState('Convert the selected DWG model to IFC, preserving beams and columns.')
  const [history, setHistory] = useState([
    { label: 'Default conversion prompt', date: 'Today', status: 'Saved' },
    { label: 'High precision detail mode', date: 'Yesterday', status: 'Saved' }
  ])

  return (
    <div className="space-y-6">
      <header className="rounded-3xl border border-[rgba(0,212,255,0.15)] bg-[#0f1629] p-6">
        <p className="text-sm uppercase tracking-[0.24em] text-[#00d4ff]">LLM Hub</p>
        <h1 className="mt-3 text-3xl font-semibold text-[#e2e8f0]">Prompt Engineering</h1>
        <p className="mt-2 text-sm text-[#94a3b8]">Refine the AI instruction set used during CAD-to-BIM conversion.</p>
      </header>

      <div className="grid gap-6 lg:grid-cols-[1.4fr_0.8fr]">
        <div className="rounded-3xl border border-[#1f2a43] bg-[#09101d] p-6">
          <div className="flex items-center gap-3">
            <Edit3 className="h-6 w-6 text-[#00d4ff]" />
            <div>
              <p className="text-sm text-[#94a3b8]">Active prompt</p>
              <p className="text-lg font-semibold text-[#e2e8f0]">Conversion behavior</p>
            </div>
          </div>
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            className="mt-6 min-h-[220px] w-full rounded-3xl border border-[#1f2a43] bg-[#07101f] p-4 text-sm text-[#e2e8f0] outline-none transition focus:border-[#00d4ff]"
          />
          <button className="mt-4 inline-flex items-center gap-2 rounded-2xl bg-[#00d4ff] px-5 py-3 text-sm font-semibold text-[#07101f] transition hover:bg-[#33e7ff]">
            <Sparkles className="h-4 w-4" /> Save prompt
          </button>
        </div>

        <div className="space-y-4 rounded-3xl border border-[#1f2a43] bg-[#09101d] p-6">
          <div className="flex items-center gap-3">
            <Layers className="h-6 w-6 text-[#00d4ff]" />
            <h2 className="text-lg font-semibold text-[#e2e8f0]">Prompt history</h2>
          </div>
          <div className="space-y-3">
            {history.map((item) => (
              <div key={item.label} className="rounded-3xl border border-[#162039] bg-[#07101f] p-4">
                <p className="text-sm font-medium text-[#e2e8f0]">{item.label}</p>
                <div className="mt-2 flex items-center justify-between text-xs text-[#64748b]">
                  <span>{item.date}</span>
                  <span>{item.status}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default PromptEngineering
