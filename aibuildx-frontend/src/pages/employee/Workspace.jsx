import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { UploadCloud, X, CheckCircle, Loader2, AlertCircle, Download, ArrowRight, ShieldCheck, Sparkles, Eye } from 'lucide-react'
import api from '../../lib/api'
import { useJobStore } from '../../stores/jobStore'
import { useAuthStore } from '../../stores/authStore'
import SelfHealingModal from '../../components/SelfHealingModal'
import ConfidenceGauge from '../../components/ConfidenceGauge'

const stepDefinitions = [
  { label: 'Upload', icon: CheckCircle },
  { label: 'Convert', icon: Loader2 },
  { label: 'Analyze', icon: Loader2 },
  { label: 'Export', icon: Loader2 }
]

function formatBytes(bytes) {
  if (!bytes) return '0 B'
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`
}

function StatusBubble({ status }) {
  const map = {
    idle: { label: 'Idle', color: '#64748b' },
    uploading: { label: 'Uploading', color: '#00d4ff' },
    processing: { label: 'Processing', color: '#f59e0b' },
    results: { label: 'Analyzing', color: '#10b981' },
    'ready-to-export': { label: 'Ready to Export', color: '#10b981' }
  }
  const config = map[status] || map.idle
  return <span className="rounded-full px-3 py-2 text-sm font-semibold" style={{ background: '#07101f', color: config.color, border: '1px solid rgba(0,212,255,0.15)' }}>{config.label}</span>
}

function StatChip({ label, value }) {
  return (
    <div className="rounded-3xl border border-[#1f2a43] bg-[#0b1524] p-4">
      <p className="text-sm text-[#94a3b8]">{label}</p>
      <p className="mt-2 text-xl font-semibold text-[#e2e8f0]">{value}</p>
    </div>
  )
}

function MetricBar({ label, value, color }) {
  return (
    <div>
      <div className="flex items-center justify-between text-sm text-[#94a3b8]">
        <span>{label}</span>
        <span>{Math.round(value * 100)}%</span>
      </div>
      <div className="mt-2 h-3 overflow-hidden rounded-full bg-[#12203a]">
        <div className="h-full rounded-full" style={{ width: `${value * 100}%`, background: color }} />
      </div>
    </div>
  )
}

function SummaryTile({ label, value }) {
  return (
    <div className="rounded-3xl border border-[#1f2a43] bg-[#07101f] p-4">
      <p className="text-sm text-[#94a3b8]">{label}</p>
      <p className="mt-2 text-lg font-semibold text-[#e2e8f0]">{value}</p>
    </div>
  )
}

function Workspace() {
  const navigate = useNavigate()
  const { uploadJob, fetchJobs, updateJobStatus, getJobById, getUserJobs } = useJobStore()
  const { user } = useAuthStore()
  const [selectedFile, setSelectedFile] = useState(null)
  const [dragging, setDragging] = useState(false)
  const [status, setStatus] = useState('idle')
  const [progress, setProgress] = useState(0)
  const [jobId, setJobId] = useState(null)
  const [jobResult, setJobResult] = useState(null)
  const [aiAudit, setAiAudit] = useState(null)
  const [needsConfirmation, setNeedsConfirmation] = useState(false)
  const [modalOpen, setModalOpen] = useState(false)
  const [error, setError] = useState('')
  const [exportEnabled, setExportEnabled] = useState(false)
  const [qualityValues, setQualityValues] = useState({ accuracy: 0.82, completeness: 0.76, quality: 0.69 })
  const [activeSection, setActiveSection] = useState('overview')

  const userJobs = useMemo(() => getUserJobs(), [getUserJobs])
  const selectedJob = useMemo(() => (jobId ? getJobById(jobId) : null), [jobId, getJobById])
  const jobOutput = jobResult?.outputs || {}
  const jobSummary = jobOutput.summary || {}
  const files = jobOutput.files || []
  const fileDetails = jobOutput.file_details || []

  useEffect(() => {
    fetchJobs()
  }, [fetchJobs])

  useEffect(() => {
    if (status === 'uploading') {
      setProgress(10)
      const interval = setInterval(() => {
        setProgress(prev => Math.min(85, prev + Math.random() * 5))
      }, 1000)
      return () => clearInterval(interval)
    }
  }, [status])

  useEffect(() => {
    if (status === 'processing') {
      setProgress(85)
      const interval = setInterval(() => {
        setProgress(prev => Math.min(95, prev + Math.random() * 2))
      }, 800)
      return () => clearInterval(interval)
    }
  }, [status])

  useEffect(() => {
    if (status === 'results') {
      setProgress(100)
      setError('')
    }
  }, [status])

  const handleRemoveFile = () => {
    setSelectedFile(null)
    setStatus('idle')
    setProgress(0)
    setJobId(null)
    setJobResult(null)
    setAiAudit(null)
    setExportEnabled(false)
    setError('')
  }

  const handleFileSelect = (file) => {
    setSelectedFile(file)
    setStatus('idle')
    setProgress(0)
    setJobId(null)
    setJobResult(null)
    setExportEnabled(false)
    setError('')
  }

  const handleUpload = async () => {
    if (!selectedFile) return
    setError('')
    setStatus('uploading')
    setProgress(10)

    try {
      const response = await uploadJob(selectedFile, {
        userId: user?.id,
        companyId: user?.companyId
      })

      const createdJobId = response?.job_id || response?.job?.id || response?.id
      if (!createdJobId) {
        throw new Error(response?.message || 'Upload failed')
      }

      setJobId(createdJobId)
      updateJobStatus(createdJobId, 'processing', 20)
      setStatus('processing')

      await fetchJobs()

      const validateRes = await api.get(`/ai-validate/${createdJobId}`)
      if (validateRes.data.needs_user_confirmation) {
        setAiAudit(validateRes.data.audit)
        setNeedsConfirmation(true)
        setModalOpen(true)
        setStatus('ai-validating')
      } else {
        setAiAudit(validateRes.data.audit)
        setExportEnabled(true)
        setStatus('ready-to-export')
      }

      const mock = {
        outputs: {
          files: validateRes.data.outputs?.files || ['model.ifc', 'report.json'],
          file_details: validateRes.data.outputs?.file_details || [],
          summary: {
            members: validateRes.data.outputs?.summary?.members ?? '—',
            format: validateRes.data.outputs?.summary?.format ?? 'DWG',
            time: validateRes.data.outputs?.summary?.time ?? '—',
            entities: validateRes.data.outputs?.summary?.entities ?? '—'
          }
        }
      }
      setJobResult({ job_id: createdJobId, ...mock })
    } catch (err) {
      setStatus('idle')
      setProgress(0)
      setError(err.message || 'Upload failed')
    }
  }



  const handleResolve = async (decision) => {
    try {
      setError('')
      // YES button:
      // await axios.post(`/api/ai-act/${jobId}`, { action: 'apply_all', decision: 'yes' });
      // NO button:
      // await axios.post(`/api/ai-act/${jobId}`, { action: 'accept_as_is', decision: 'no' });
      // After either: close modal, enable export buttons, update AI summary card
      const action = decision === 'yes' ? 'apply_all' : 'accept_as_is'
      const decisionValue = decision === 'yes' ? 'yes' : 'no'
      const res = await api.post(`/ai-act/${jobId}`, { action, decision: decisionValue })
      setAiAudit(res.data.audit)
      setModalOpen(false)
      setExportEnabled(true)
      setStatus('ready-to-export')
    } catch (err) {
      setError(err.message || 'AI action failed')
    }
  }

  const handleDownload = async (filename) => {
    try {
      // Each file from outputs.files gets a link:
      // href={`/api/download/${jobId}/${filename}`}
      const res = await api.get(`/download/${jobId}/${filename}`, { responseType: 'blob' })
      const url = window.URL.createObjectURL(new Blob([res.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', filename)
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (err) {
      setError(err.message || 'Download failed')
    }
  }

  const handleExportTekla = async (direct = false) => {
    try {
      // Tekla IFC:
      // const res = await axios.get(`/api/export-tekla/${jobId}`);
      // Direct:
      // const res = await axios.get(`/api/export-tekla-direct/${jobId}`);
      const endpoint = direct ? `/export-tekla-direct/${jobId}` : `/export-tekla/${jobId}`
      const res = await api.get(endpoint)
      if (res.data.ifc_available) {
        window.open(res.data.ifc_path, '_blank')
      }
    } catch (err) {
      setError(err.message || 'Export action failed')
    }
  }

  const handleViewerNavigate = () => {
    navigate(`/employee/viewer/${jobId}`)
  }

  const progressStages = [
    { label: 'Upload', status: status === 'uploading' || status === 'processing' || status === 'results' || status === 'ready-to-export' ? 'done' : 'pending', icon: CheckCircle },
    { label: 'Convert', status: status === 'processing' || status === 'results' || status === 'ready-to-export' ? 'active' : 'pending', icon: Loader2 },
    { label: 'Analyze', status: status === 'results' || status === 'ready-to-export' ? 'active' : 'pending', icon: Loader2 },
    { label: 'Export', status: status === 'ready-to-export' ? 'active' : 'pending', icon: Loader2 }
  ]

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 rounded-3xl border border-[rgba(0,212,255,0.15)] bg-[#0f1629] p-6 shadow-[0_0_40px_rgba(0,212,255,0.1)]">
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-sm uppercase tracking-[0.3em] text-[#00d4ff]">Employee Workspace</p>
            <h1 className="text-3xl font-semibold text-[#e2e8f0]">DWG → BIM Conversion</h1>
            <p className="max-w-2xl text-sm text-[#94a3b8]">Load your CAD package, track conversion status, review AI validation, and export straight to Tekla.</p>
          </div>
          <div className="flex items-center gap-3">
            <StatusBubble status={status} />
            <button onClick={() => handleRemoveFile()} className="rounded-2xl border border-[#2c3345] bg-[#09101d] px-4 py-2 text-sm text-[#e2e8f0] transition hover:border-[#00d4ff]/70">Reset</button>
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-[1.6fr_1fr]">
          <div className="rounded-3xl border border-[rgba(0,212,255,0.12)] bg-[#09101d] p-6">
            <div className={`group relative rounded-3xl border-2 border-dashed ${dragging ? 'border-[#00d4ff] bg-[#07101f]' : 'border-[#324255] bg-[#09101d]'} px-5 py-12 text-center transition-all duration-200`} onDragEnter={() => setDragging(true)} onDragLeave={() => setDragging(false)} onDragOver={(e) => { e.preventDefault(); setDragging(true) }} onDrop={(e) => { e.preventDefault(); setDragging(false); if (e.dataTransfer.files.length) handleFileSelect(e.dataTransfer.files[0]) }}>
              <UploadCloud className="mx-auto mb-4 h-12 w-12 text-[#00d4ff]" />
              <p className="text-lg font-semibold text-[#e2e8f0]">Drag & drop your DWG/DXF file</p>
              <p className="mt-2 text-sm text-[#94a3b8]">or click to choose from your device</p>
              <input type="file" accept=".dwg,.dxf,.json" className="absolute inset-0 opacity-0 cursor-pointer" onChange={(e) => e.target.files?.[0] && handleFileSelect(e.target.files[0])} />
            </div>

            {selectedFile && (
              <div className="mt-6 rounded-3xl border border-[#1f2a43] bg-[#0a1220] p-4">
                <div className="flex items-center justify-between gap-4">
                  <div>
                    <p className="text-sm uppercase tracking-[0.24em] text-[#94a3b8]">Selected File</p>
                    <p className="mt-2 text-lg font-medium text-[#e2e8f0]">{selectedFile.name}</p>
                    <p className="text-sm text-[#64748b]">{formatBytes(selectedFile.size)}</p>
                  </div>
                  <button onClick={handleRemoveFile} className="inline-flex h-10 w-10 items-center justify-center rounded-full border border-[#2c3345] bg-[#09101d] text-[#94a3b8] transition hover:border-[#00d4ff] hover:text-[#e2e8f0]">
                    <X className="h-4 w-4" />
                  </button>
                </div>
              </div>
            )}

            <div className="mt-6 flex flex-col gap-3 sm:flex-row">
              <button
                disabled={!selectedFile || status === 'uploading' || status === 'processing'}
                onClick={handleUpload}
                className="inline-flex min-w-[180px] items-center justify-center gap-2 rounded-2xl bg-[#00d4ff] px-5 py-3 text-sm font-semibold text-[#07101f] transition hover:bg-[#33e7ff] disabled:cursor-not-allowed disabled:opacity-50"
              >
                <span>Start Conversion</span>
                <ArrowRight className="h-4 w-4" />
              </button>
              <button onClick={handleRemoveFile} className="inline-flex min-w-[180px] items-center justify-center gap-2 rounded-2xl border border-[#2c3345] bg-[#09101d] px-5 py-3 text-sm font-semibold text-[#e2e8f0] transition hover:border-[#00d4ff]">
                Remove File
              </button>
            </div>

            {error && (
              <div className="mt-4 rounded-2xl bg-[#2b1221] p-4 text-sm text-[#ef4444]">
                <div className="flex items-center gap-2"><AlertCircle className="h-4 w-4" />{error}</div>
              </div>
            )}
          </div>

          <div className="rounded-3xl border border-[rgba(0,212,255,0.12)] bg-[#09101d] p-6">
            <p className="text-sm uppercase tracking-[0.24em] text-[#94a3b8]">Conversion status</p>
            <div className="mt-4 rounded-3xl bg-[#07101f] p-4">
              <div className="h-3 overflow-hidden rounded-full bg-[#12203a]">
                <div className="h-full rounded-full bg-gradient-to-r from-[#00d4ff] to-[#1ce0ff] transition-all" style={{ width: `${progress}%` }} />
              </div>
              <p className="mt-3 text-sm text-[#94a3b8]">{status === 'idle' ? 'Waiting for upload' : status === 'uploading' ? 'Uploading file…' : status === 'processing' ? 'Converting and analyzing model…' : status === 'results' ? 'Validation in progress…' : 'Ready to export'}</p>
            </div>

            <div className="mt-6 space-y-3">
              {progressStages.map((item, index) => (
                <div key={item.label} className="flex items-center gap-3 rounded-3xl border border-[#1f2a43] bg-[#0b1524] px-4 py-3">
                  <div className={`flex h-10 w-10 items-center justify-center rounded-2xl ${item.status === 'done' ? 'bg-[#0f442e]' : item.status === 'active' ? 'bg-[#02425d]' : 'bg-[#1f2a43]'}`}>
                    <item.icon className={`h-5 w-5 ${item.status === 'done' ? 'text-[#10b981]' : item.status === 'active' ? 'text-[#00d4ff] animate-spin-slow' : 'text-[#64748b]'}`} />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-[#e2e8f0]">{item.label}</p>
                    <p className="text-xs text-[#64748b]">{item.status === 'done' ? 'Completed' : item.status === 'active' ? 'In progress' : 'Pending'}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {jobResult && (
        <div className="space-y-6 rounded-3xl border border-[rgba(0,212,255,0.15)] bg-[#0f1629] p-6 shadow-[0_0_40px_rgba(0,212,255,0.1)]">
          <div className="flex flex-wrap gap-3">
            {['overview', 'files', 'ai'].map((section) => (
              <button
                key={section}
                onClick={() => setActiveSection(section)}
                className={`rounded-full border px-4 py-2 text-sm font-semibold transition ${activeSection === section ? 'border-[#00d4ff] bg-[#07101f] text-[#e2e8f0]' : 'border-[#1f2a43] bg-[#09101d] text-[#94a3b8]'}`}
              >
                {section === 'overview' ? 'Overview' : section === 'files' ? 'Files & Jobs' : 'AI Insights'}
              </button>
            ))}
          </div>

          {activeSection === 'overview' && (
            <>
              <div className="grid gap-6 sm:grid-cols-2 xl:grid-cols-4">
              <div className="rounded-3xl border border-[#1e2a44] bg-[#07101f] p-5">
                <p className="text-sm text-[#94a3b8]">Total Members</p>
                <p className="mt-3 text-3xl font-semibold text-[#e2e8f0]">{jobSummary.members}</p>
              </div>
              <div className="rounded-3xl border border-[#1e2a44] bg-[#07101f] p-5">
                <p className="text-sm text-[#94a3b8]">Conversion Time</p>
                <p className="mt-3 text-3xl font-semibold text-[#e2e8f0]">{jobSummary.time}</p>
              </div>
              <div className="rounded-3xl border border-[#1e2a44] bg-[#07101f] p-5">
                <p className="text-sm text-[#94a3b8]">Format</p>
                <p className="mt-3 text-3xl font-semibold text-[#e2e8f0]">{jobSummary.format}</p>
              </div>
              <div className="rounded-3xl border border-[#1e2a44] bg-[#07101f] p-5">
                <p className="text-sm text-[#94a3b8]">Entities</p>
                <p className="mt-3 text-3xl font-semibold text-[#e2e8f0]">{jobSummary.entities}</p>
              </div>
            </div>

            <div className="mt-6 flex flex-col gap-3 sm:flex-row">
              <button
                onClick={handleViewerNavigate}
                disabled={!jobId}
                className="inline-flex min-w-[180px] items-center justify-center gap-2 rounded-2xl border border-[#2c3345] bg-[#07101f] px-5 py-3 text-sm font-semibold text-[#e2e8f0] transition hover:border-[#00d4ff] disabled:cursor-not-allowed disabled:opacity-50"
              >
                <Eye className="h-4 w-4" /> Preview in Viewer
              </button>
            </div>

            <div className="grid gap-6 lg:grid-cols-2">
              <div className="rounded-3xl border border-[rgba(0,212,255,0.12)] bg-[#09101d] p-5">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-[#e2e8f0]">Downloads</h3>
                  <span className="text-sm text-[#94a3b8]">{files.length} files</span>
                </div>
                <div className="mt-4 space-y-3">
                  {files.map((file) => (
                    <div key={file} className="flex items-center justify-between gap-3 rounded-3xl border border-[#1f2a43] bg-[#07101f] px-4 py-3">
                      <div>
                        <p className="text-sm font-medium text-[#e2e8f0]">{file}</p>
                        <p className="text-xs text-[#64748b]">{fileDetails.find((item) => item.name === file)?.size ? formatBytes(fileDetails.find((item) => item.name === file)?.size) : '—'}</p>
                      </div>
                      <button onClick={() => handleDownload(file)} className="inline-flex items-center gap-2 rounded-2xl bg-[#00d4ff] px-4 py-2 text-xs font-semibold text-[#07101f] transition hover:bg-[#33e7ff]">
                        <Download className="h-4 w-4" /> Download
                      </button>
                    </div>
                  ))}
                </div>
              </div>

              <div className="rounded-3xl border border-[rgba(0,212,255,0.12)] bg-[#09101d] p-5">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-[#e2e8f0]">Recent Jobs</h3>
                  <span className="text-sm text-[#94a3b8]">{userJobs.length} jobs</span>
                </div>
                <div className="mt-4 space-y-3">
                  {userJobs.slice(0, 5).map((job) => (
                    <div key={job.id} className="flex items-center justify-between gap-3 rounded-3xl border border-[#1f2a43] bg-[#07101f] px-4 py-3">
                      <div>
                        <p className="text-sm font-medium text-[#e2e8f0]">Job {job.id}</p>
                        <p className="text-xs text-[#64748b]">{job.status} • {job.created_at ? new Date(job.created_at).toLocaleDateString() : '—'}</p>
                      </div>
                      <button onClick={() => navigate(`/employee/viewer/${job.id}`)} className="inline-flex items-center gap-2 rounded-2xl bg-[#00d4ff] px-4 py-2 text-xs font-semibold text-[#07101f] transition hover:bg-[#33e7ff]">
                        <Eye className="h-4 w-4" /> View
                      </button>
                    </div>
                  ))}
                  {userJobs.length === 0 && (
                    <p className="text-sm text-[#64748b] text-center py-4">No jobs found. Upload a file to get started.</p>
                  )}
                </div>
              </div>
            </div>
          </>
          )}

          {activeSection === 'files' && (
            <div className="space-y-6">
              <div className="grid gap-6 lg:grid-cols-2">
                <div className="rounded-3xl border border-[rgba(0,212,255,0.12)] bg-[#09101d] p-5">
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-semibold text-[#e2e8f0]">Downloads</h3>
                    <span className="text-sm text-[#94a3b8]">{files.length} files</span>
                  </div>
                  <div className="mt-4 space-y-3">
                    {files.map((file) => (
                      <div key={file} className="flex items-center justify-between gap-3 rounded-3xl border border-[#1f2a43] bg-[#07101f] px-4 py-3">
                        <div>
                          <p className="text-sm font-medium text-[#e2e8f0]">{file}</p>
                          <p className="text-xs text-[#64748b]">{fileDetails.find((item) => item.name === file)?.size ? formatBytes(fileDetails.find((item) => item.name === file)?.size) : '—'}</p>
                        </div>
                        <button onClick={() => handleDownload(file)} className="inline-flex items-center gap-2 rounded-2xl bg-[#00d4ff] px-4 py-2 text-xs font-semibold text-[#07101f] transition hover:bg-[#33e7ff]">
                          <Download className="h-4 w-4" /> Download
                        </button>
                      </div>
                    ))}
                    {files.length === 0 && <p className="text-sm text-[#64748b]">No downloadable files are available yet.</p>}
                  </div>
                </div>

                <div className="rounded-3xl border border-[rgba(0,212,255,0.12)] bg-[#09101d] p-5">
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-semibold text-[#e2e8f0]">Recent Jobs</h3>
                    <span className="text-sm text-[#94a3b8]">{userJobs.length} jobs</span>
                  </div>
                  <div className="mt-4 space-y-3">
                    {userJobs.slice(0, 5).map((job) => (
                      <div key={job.id} className="flex items-center justify-between gap-3 rounded-3xl border border-[#1f2a43] bg-[#07101f] px-4 py-3">
                        <div>
                          <p className="text-sm font-medium text-[#e2e8f0]">Job {job.id}</p>
                          <p className="text-xs text-[#64748b]">{job.status} • {job.created_at ? new Date(job.created_at).toLocaleDateString() : '—'}</p>
                        </div>
                        <button onClick={() => navigate(`/employee/viewer/${job.id}`)} className="inline-flex items-center gap-2 rounded-2xl bg-[#00d4ff] px-4 py-2 text-xs font-semibold text-[#07101f] transition hover:bg-[#33e7ff]">
                          <Eye className="h-4 w-4" /> View
                        </button>
                      </div>
                    ))}
                    {userJobs.length === 0 && (
                      <p className="text-sm text-[#64748b] text-center py-4">No jobs found. Upload a file to get started.</p>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeSection === 'ai' && (
            <div className="grid gap-6 lg:grid-cols-2">
              <div className="rounded-3xl border border-[rgba(0,212,255,0.15)] bg-[#0f1629] p-6 shadow-[0_0_40px_rgba(0,212,255,0.1)]">
                <h3 className="text-lg font-semibold text-[#e2e8f0]">AI Summary</h3>
                <p className="mt-3 text-sm leading-6 text-[#94a3b8]">{aiAudit?.summary || 'AI validation is pending. Once complete, export options will become available.'}</p>
                <div className="mt-5 grid gap-3">
                  <SummaryTile label="Recommendation" value={aiAudit?.recommendation || 'Pending review'} />
                  <SummaryTile label="Scale correction" value={aiAudit?.scale_correction_needed ? 'Required' : 'No'} />
                  <SummaryTile label="Disconnected nodes" value={aiAudit?.disconnected_node_count ?? 0} />
                </div>
              </div>

              <div className="space-y-6">
                <div className="rounded-3xl border border-[rgba(0,212,255,0.12)] bg-[#09101d] p-5">
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-semibold text-[#e2e8f0]">AI Self-Healing</h3>
                    <span className="text-xs text-[#94a3b8]">Confidence: {Math.round((aiAudit?.confidence_score ?? 0) * 100)}%</span>
                  </div>
                  <div className="mt-4 space-y-4">
                    <div className="rounded-3xl bg-[#07111f] p-4">
                      <p className="text-sm text-[#64748b]">Advisory</p>
                      <p className="mt-2 text-sm text-[#e2e8f0]">{aiAudit?.advisory_text || 'Awaiting AI validation results before export.'}</p>
                    </div>
                    <div className="grid gap-3">
                      <StatChip label="Gap Count" value={aiAudit?.gap_count ?? 0} />
                      <StatChip label="Issue Count" value={aiAudit?.issue_count ?? 0} />
                      <StatChip label="Confidence" value={`${Math.round((aiAudit?.confidence_score ?? 0) * 100)}%`} />
                    </div>
                  </div>
                </div>

                <div className="rounded-3xl border border-[rgba(0,212,255,0.12)] bg-[#09101d] p-5">
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-semibold text-[#e2e8f0]">Quality Report</h3>
                    <span className="text-xs text-[#94a3b8]">KPI snapshot</span>
                  </div>
                  <div className="mt-6 space-y-4">
                    <MetricBar label="Accuracy" value={aiAudit?.accuracy_score ?? qualityValues.accuracy} color="#00d4ff" />
                    <MetricBar label="Completeness" value={aiAudit?.completeness_score ?? qualityValues.completeness} color="#f59e0b" />
                    <MetricBar label="Quality" value={aiAudit?.quality_score ?? qualityValues.quality} color="#10b981" />
                  </div>
                </div>

                <div className="rounded-3xl border border-[rgba(0,212,255,0.15)] bg-[#0f1629] p-6 shadow-[0_0_40px_rgba(0,212,255,0.1)]">
                  <h3 className="text-lg font-semibold text-[#e2e8f0]">Action Log</h3>
                  <div className="mt-4 space-y-3 text-sm text-[#94a3b8]">
                    <p>Job ID: <span className="text-[#e2e8f0]">{jobId}</span></p>
                    <p>Status: <span className="text-[#00d4ff]">{status}</span></p>
                    <p>AI validation: <span className="text-[#10b981]">{aiAudit ? 'Completed' : 'Pending'}</span></p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      <SelfHealingModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        audit={aiAudit || { suggestions: [] }}
        jobId={jobId}
        onResolved={(decision) => handleResolve(decision)}
      />
    </div>
  )
}

export default Workspace
