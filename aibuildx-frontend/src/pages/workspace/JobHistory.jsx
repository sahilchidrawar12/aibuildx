import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Clock, ListChecks, CheckCircle, XCircle } from 'lucide-react'
import { useJobStore } from '../../stores/jobStore'

function JobHistory() {
  const { jobs: _jobs, fetchJobs, getUserJobs, isLoading, error } = useJobStore()
  const navigate = useNavigate()
  const userJobs = getUserJobs()

  useEffect(() => {
    fetchJobs()
  }, [fetchJobs])

  return (
    <div className="space-y-6">
      <div className="rounded-3xl border border-[rgba(0,212,255,0.15)] bg-[#0f1629] p-6">
        <p className="text-sm uppercase tracking-[0.24em] text-[#00d4ff]">Workspace</p>
        <h1 className="mt-3 text-3xl font-semibold text-[#e2e8f0]">Job History</h1>
        <p className="mt-2 text-sm text-[#94a3b8]">Review past conversion jobs and export the latest delivery packages.</p>
      </div>

      <div className="rounded-3xl border border-[#1f2a43] bg-[#09101d] p-6">
        <div className="flex items-center justify-between gap-4">
          <div>
            <h2 className="text-lg font-semibold text-[#e2e8f0]">Conversion history</h2>
            <p className="text-sm text-[#94a3b8]">Track job status, runtime, and result quality.</p>
          </div>
          <button
            onClick={fetchJobs}
            className="inline-flex items-center gap-2 rounded-2xl bg-[#00d4ff] px-5 py-3 text-sm font-semibold text-[#07101f] hover:bg-[#33e7ff] transition"
          >
            <ListChecks className="w-4 h-4" /> Refresh
          </button>
        </div>

        <div className="mt-6 divide-y divide-[#162039] rounded-3xl border border-[#162039] bg-[#07101f] overflow-hidden">
          {userJobs.length > 0 ? userJobs.map((job) => (
            <div key={job.id} className="flex flex-col gap-4 p-5 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="text-white font-semibold">{job.name || job.fileName || `Job ${job.id}`}</p>
                <p className="text-secondary-400 text-sm">Created {new Date(job.createdAt || job.created_at || Date.now()).toLocaleString()}</p>
                <p className="text-secondary-500 text-xs mt-1">{job.outputs?.files?.length ? `${job.outputs.files.length} output file(s)` : 'Output files unavailable'}</p>
              </div>
              <div className="flex flex-col gap-3 sm:items-end">
                <div className="flex items-center gap-3 text-sm text-secondary-300">
                  <span className={`rounded-full px-3 py-1 ${job.status === 'completed' ? 'bg-green-500/10 text-green-300' : job.status === 'processing' ? 'bg-yellow-500/10 text-yellow-300' : job.status === 'failed' ? 'bg-red-500/10 text-red-300' : 'bg-gray-500/10 text-gray-300'}`}>{job.status}</span>
                  {job.results?.accuracy != null ? <span>{job.results.accuracy}% accuracy</span> : <span className="italic">Pending</span>}
                  <div className="text-secondary-400">
                    {job.status === 'completed' ? <CheckCircle className="inline-block w-4 h-4" /> : job.status === 'failed' ? <XCircle className="inline-block w-4 h-4" /> : <Clock className="inline-block w-4 h-4" />}
                  </div>
                </div>
                <button
                  onClick={() => navigate(`/viewer/${job.id}`)}
                  className="inline-flex items-center justify-center rounded-2xl bg-[#00d4ff] px-4 py-2 text-xs font-semibold text-[#07101f] transition hover:bg-[#33e7ff]"
                >
                  View IFC
                </button>
              </div>
            </div>
          )) : (
            <div className="p-8 text-center text-secondary-400">
              {isLoading ? 'Loading job history…' : error ? `Unable to load jobs: ${error}` : 'No job history available yet. Upload a DWG/DXF file to start a conversion.'}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default JobHistory
