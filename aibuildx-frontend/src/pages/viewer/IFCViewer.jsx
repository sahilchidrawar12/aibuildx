import { useEffect, useMemo, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useAuthStore } from '../../stores/authStore'
import { useJobStore } from '../../stores/jobStore'

const COMPLETED_STATUS = ['completed', 'validated', 'ready-to-export']

function IFCViewer() {
  const { jobId } = useParams()
  const navigate = useNavigate()
  const user = useAuthStore(state => state.user)
  const jobs = useJobStore(state => state.jobs)
  const { fetchJobs, getUserJobs, isLoading } = useJobStore()
  const completedJobs = useMemo(() => {
    const finished = jobs.filter(job => COMPLETED_STATUS.includes(job.status))
    const userJobs = finished.filter(job => job.user_id === user?.id)
    return userJobs.length > 0 ? userJobs : finished
  }, [jobs, user?.id])

  useEffect(() => {
    fetchJobs()
  }, [fetchJobs])

  const [showRawUrl, setShowRawUrl] = useState(false)

  useEffect(() => {
    if (!jobId && !isLoading && completedJobs.length === 1) {
      navigate(`/viewer/${completedJobs[0].id}`)
    }
  }, [jobId, isLoading, completedJobs, navigate])

  const API_BASE_URL = import.meta.env.VITE_API_URL || window.location.origin
  const viewerUrl = jobId ? `${API_BASE_URL}/viewer/${jobId}` : ''

  if (!jobId) {
    return (
      <div className="min-h-screen bg-slate-950 p-8">
        <div className="max-w-3xl mx-auto rounded-3xl border border-slate-700 bg-slate-900/95 p-10 text-center shadow-xl shadow-slate-950/20">
          <h1 className="text-3xl font-semibold text-white">No completed job selected</h1>
          <p className="mt-4 text-slate-400">
            Select a completed job from Job History or the pipeline dashboard to view its IFC model.
          </p>
          <p className="mt-4 text-sm text-slate-500">
            If you opened this page directly, choose a completed job below or return to Workspace to run a conversion.
          </p>

          {isLoading ? (
            <p className="mt-6 text-sm text-slate-400">Loading your recent jobs…</p>
          ) : completedJobs.length > 0 ? (
            <>
              {getUserJobs().filter(job => COMPLETED_STATUS.includes(job.status)).length === 0 && (
                <p className="mt-4 text-sm text-yellow-300">No completed jobs were found for your account. Showing all completed jobs available in the system.</p>
              )}
              <div className="mt-6 grid gap-3">
                {completedJobs.map((job) => (
                  <button
                    key={job.id}
                    onClick={() => navigate(`/viewer/${job.id}`)}
                    className="w-full rounded-3xl border border-slate-700 bg-slate-950/80 px-5 py-4 text-left text-white transition hover:border-cyan-400 hover:bg-slate-900"
                  >
                    <div className="flex items-center justify-between gap-4">
                      <div>
                        <p className="font-semibold">{job.name || job.fileName || `Job ${job.id}`}</p>
                        <p className="text-sm text-slate-400">Completed {new Date(job.createdAt || job.created_at || Date.now()).toLocaleString()}</p>
                      </div>
                      <span className="rounded-full bg-cyan-500/10 px-3 py-1 text-xs text-cyan-200">View</span>
                    </div>
                  </button>
                ))}
              </div>
            </>
          ) : (
            <p className="mt-6 text-sm text-slate-500">No completed jobs available yet. Upload a DWG/DXF file and wait for conversion to finish before opening a viewer.</p>
          )}
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="border-b border-slate-800 bg-slate-900/95 px-6 py-4 lg:px-10">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.32em] text-cyan-300/80">IFC Viewer</p>
            <h1 className="mt-2 text-2xl font-semibold text-white">Job Viewer</h1>
            <p className="mt-1 text-sm text-slate-400">Rendering model for job <span className="font-medium text-cyan-300">{jobId}</span>.</p>
          </div>
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={() => setShowRawUrl(!showRawUrl)}
              className="rounded-2xl border border-slate-700 bg-slate-900 px-4 py-2 text-sm text-slate-100 transition hover:border-cyan-400"
            >
              {showRawUrl ? 'Hide raw URL' : 'Show raw URL'}
            </button>
          </div>
        </div>
        {showRawUrl && (
          <div className="mt-4 rounded-2xl bg-slate-950/95 p-4 text-sm text-slate-300 ring-1 ring-slate-800">
            <div className="break-all">
              Viewer URL: <a href={viewerUrl} className="text-cyan-300 underline">{viewerUrl}</a>
            </div>
          </div>
        )}
      </div>

      <div className="relative h-[calc(100vh-96px)] bg-slate-950">
        <iframe
          title={`IFC Viewer ${jobId}`}
          src={viewerUrl}
          className="absolute inset-0 h-full w-full border-0"
        />
      </div>
    </div>
  )
}

export default IFCViewer