import { useState } from 'react'
import { UploadCloud, Database, Sparkles } from 'lucide-react'

function TrainingData() {
  const [files, setFiles] = useState([])
  const [status, setStatus] = useState('Idle')

  const handleUpload = (filesList) => {
    setFiles(Array.from(filesList))
    setStatus('Ready')
  }

  return (
    <div className="space-y-6">
      <header className="rounded-3xl border border-[rgba(0,212,255,0.15)] bg-[#0f1629] p-6">
        <p className="text-sm uppercase tracking-[0.24em] text-[#00d4ff]">LLM Hub</p>
        <h1 className="mt-3 text-3xl font-semibold text-[#e2e8f0]">Training Data</h1>
        <p className="mt-2 text-sm text-[#94a3b8]">Manage knowledge ingestion sources and training corpus for AI models.</p>
      </header>

      <div className="grid gap-6 lg:grid-cols-[1.5fr_0.8fr]">
        <div className="rounded-3xl border border-[#1f2a43] bg-[#09101d] p-6">
          <div className="flex items-center gap-3">
            <UploadCloud className="h-6 w-6 text-[#00d4ff]" />
            <h2 className="text-lg font-semibold text-[#e2e8f0]">Upload training assets</h2>
          </div>
          <label className="mt-6 flex min-h-[220px] flex-col items-center justify-center rounded-3xl border-2 border-dashed border-[#324255] bg-[#07101f] p-6 text-center text-sm text-[#94a3b8] transition hover:border-[#00d4ff] hover:text-[#e2e8f0] cursor-pointer">
            <span className="text-[#00d4ff]">Select files to ingest</span>
            <input type="file" multiple className="hidden" onChange={(e) => e.target.files && handleUpload(e.target.files)} accept=".pdf,.txt,.docx" />
          </label>
          <div className="mt-6 space-y-3">
            {files.map((file) => (
              <div key={file.name} className="rounded-3xl border border-[#162039] bg-[#07101f] p-4">
                <p className="text-sm text-[#e2e8f0]">{file.name}</p>
                <p className="mt-1 text-xs text-[#64748b]">{Math.round(file.size / 1024)} KB</p>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-3xl border border-[#1f2a43] bg-[#09101d] p-6">
          <div className="flex items-center gap-3">
            <Database className="h-6 w-6 text-[#00d4ff]" />
            <h2 className="text-lg font-semibold text-[#e2e8f0]">Ingestion status</h2>
          </div>
          <div className="mt-6 space-y-4">
            <div className="rounded-3xl bg-[#07101f] p-4">
              <p className="text-sm text-[#94a3b8]">Current workflow</p>
              <p className="mt-2 text-lg font-semibold text-[#e2e8f0]">File → Chunker → Embedder → ChromaDB</p>
            </div>
            <div className="rounded-3xl bg-[#07101f] p-4">
              <p className="text-sm text-[#94a3b8]">Pipeline status</p>
              <p className="mt-2 text-2xl font-semibold text-[#10b981]">{status}</p>
            </div>
            <button className="inline-flex items-center gap-2 rounded-2xl bg-[#00d4ff] px-5 py-3 text-sm font-semibold text-[#07101f] transition hover:bg-[#33e7ff]"><Sparkles className="h-4 w-4" /> Start ingestion</button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default TrainingData
