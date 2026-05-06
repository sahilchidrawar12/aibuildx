import { useRef, useState } from 'react'
import { UploadCloud, FilePlus, CheckCircle, ArrowUpCircle } from 'lucide-react'
import api from '../../lib/api'

function DocumentUpload() {
  const [files, setFiles] = useState([])
  const [uploadMessage, setUploadMessage] = useState('')
  const [isUploading, setIsUploading] = useState(false)
  const fileInputRef = useRef(null)

  const handleFiles = (selectedFiles) => {
    const fileArray = Array.from(selectedFiles || [])
    setFiles(fileArray)
    setUploadMessage('')
  }

  const handleUpload = async () => {
    if (!files.length) {
      setUploadMessage('Select one or more files before uploading.')
      return
    }

    setIsUploading(true)
    setUploadMessage('')

    const formData = new FormData()
    files.forEach((file) => formData.append('documents', file))

    try {
      await api.post('/knowledge/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      setUploadMessage('Files uploaded successfully and queued for ingestion.')
      setFiles([])
      if (fileInputRef.current) fileInputRef.current.value = ''
    } catch (err) {
      setUploadMessage('Files are ready locally; upload endpoint may not be available.')
    } finally {
      setIsUploading(false)
    }
  }

  const handleClear = () => {
    setFiles([])
    setUploadMessage('Selection cleared.')
    if (fileInputRef.current) fileInputRef.current.value = ''
  }

  return (
    <div className="space-y-6">
      <div className="rounded-3xl border border-[rgba(0,212,255,0.15)] bg-[#0f1629] p-6">
        <p className="text-sm uppercase tracking-[0.24em] text-[#00d4ff]">Knowledge Base</p>
        <h1 className="mt-3 text-3xl font-semibold text-[#e2e8f0]">Upload Documents</h1>
        <p className="mt-2 text-sm text-[#94a3b8]">Add PDF and text assets for semantic search and model ingestion.</p>
      </div>

      <div className="rounded-3xl border border-[#1f2a43] bg-[#09101d] p-6">
        <div className="flex items-center gap-3">
          <UploadCloud className="h-6 w-6 text-[#00d4ff]" />
          <h2 className="text-lg font-semibold text-[#e2e8f0]">Drop assets here</h2>
        </div>

        <label className="mt-6 flex min-h-[180px] flex-col items-center justify-center rounded-3xl border-2 border-dashed border-[#324255] bg-[#07101f] p-6 text-center text-sm text-[#94a3b8] transition hover:border-[#00d4ff] hover:text-[#e2e8f0] cursor-pointer">
          <span className="text-[#00d4ff]">Select PDF or TXT files</span>
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.txt"
            multiple
            className="hidden"
            onChange={(e) => handleFiles(e.target.files)}
          />
        </label>

        <div className="mt-6 space-y-3">
          {files.length === 0 ? (
            <div className="rounded-3xl border border-[#162039] bg-[#07101f] p-6 text-center text-sm text-[#94a3b8]">
              <p>Select documents to prepare them for ingestion.</p>
            </div>
          ) : (
            files.map((file) => (
              <div key={file.name} className="flex items-center justify-between rounded-3xl border border-[#162039] bg-[#07101f] p-4">
                <div>
                  <p className="text-sm text-[#e2e8f0]">{file.name}</p>
                  <p className="text-xs text-[#64748b]">{Math.round(file.size / 1024)} KB</p>
                </div>
                <CheckCircle className="h-5 w-5 text-[#10b981]" />
              </div>
            ))
          )}
        </div>

        <div className="mt-6 flex flex-col gap-3 sm:flex-row">
          <button
            type="button"
            disabled={isUploading}
            onClick={handleUpload}
            className="inline-flex items-center justify-center gap-2 rounded-2xl bg-[#00d4ff] px-5 py-3 text-sm font-semibold text-[#07101f] transition hover:bg-[#33e7ff] disabled:opacity-50"
          >
            <ArrowUpCircle className="h-5 w-5" />
            {isUploading ? 'Uploading...' : 'Upload Documents'}
          </button>
          <button
            type="button"
            onClick={handleClear}
            className="inline-flex items-center justify-center gap-2 rounded-2xl border border-[#324255] bg-[#0f172a] px-5 py-3 text-sm font-semibold text-[#94a3b8] transition hover:border-[#00d4ff] hover:text-[#e2e8f0]"
          >
            <FilePlus className="h-5 w-5" />
            Clear Selection
          </button>
        </div>

        {uploadMessage && (
          <div className="mt-4 rounded-2xl border border-secondary-700 bg-secondary-800 p-4 text-sm text-secondary-200">
            {uploadMessage}
          </div>
        )}
      </div>
    </div>
  )
}

export default DocumentUpload
