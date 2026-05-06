import { useEffect, useMemo, useRef, useState } from 'react'
import { Folder, Download, FolderPlus } from 'lucide-react'
import { useJobStore } from '../../stores/jobStore'
import { useAuthStore } from '../../stores/authStore'
import api from '../../lib/api'

function FileManager() {
  const { fetchJobs, getUserJobs, uploadJob, isLoading } = useJobStore()
  const { user } = useAuthStore()
  const fileInputRef = useRef(null)
  const [uploadMessage, setUploadMessage] = useState('')

  useEffect(() => {
    fetchJobs()
  }, [fetchJobs])

  const files = useMemo(() => {
    const jobs = getUserJobs()
    if (!jobs.length) return []
    return jobs.flatMap((job) => {
      return (job.outputs?.files || []).map((filename) => {
        const fileDetail = job.outputs?.file_details?.find((item) => item.name === filename)
        return {
          id: `${job.id}-${filename}`,
          jobId: job.id,
          jobName: job.name || job.fileName || `Job ${job.id}`,
          filename,
          type: filename.split('.').pop()?.toUpperCase() || 'FILE',
          updated: new Date(job.createdAt || job.created_at || Date.now()).toLocaleString(),
          status: job.status,
          size: fileDetail?.size || 0
        }
      })
    })
  }, [getUserJobs])

  const downloadFile = async (jobId, filename) => {
    try {
      const response = await api.get(`/download/${jobId}/${filename}`, { responseType: 'blob' })
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', filename)
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (error) {
      setUploadMessage(error?.message || 'Download failed. Please try again.')
    }
  }
  return (
    <div className="space-y-6">
      <div className="rounded-3xl border border-[rgba(0,212,255,0.15)] bg-[#0f1629] p-6">
        <p className="text-sm uppercase tracking-[0.24em] text-[#00d4ff]">Workspace</p>
        <h1 className="mt-3 text-3xl font-semibold text-[#e2e8f0]">File Manager</h1>
        <p className="mt-2 text-sm text-[#94a3b8]">Browse uploaded CAD assets and manage file versions.</p>
      </div>

      <div className="rounded-3xl border border-[#1f2a43] bg-[#09101d] p-6">
        <div className="flex items-center justify-between gap-4">
          <div>
            <h2 className="text-lg font-semibold text-[#e2e8f0]">Recent files</h2>
            <p className="text-sm text-[#94a3b8]">Search and export files from your workspace.</p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => fileInputRef.current?.click()}
              className="inline-flex items-center gap-2 rounded-2xl bg-[#00d4ff] px-5 py-3 text-sm font-semibold text-[#07101f] hover:bg-[#33e7ff] transition"
            >
              <FolderPlus className="w-4 h-4" /> Upload new file
            </button>
            {isLoading && <span className="text-sm text-secondary-400">Uploading...</span>}
          </div>
          <input
            ref={fileInputRef}
            type="file"
            accept=".dwg,.dxf,.json"
            className="hidden"
            onChange={async (e) => {
              const file = e.target.files?.[0]
              if (file) await handleUploadFile(file)
            }}
          />
          {uploadMessage && <p className="mt-3 text-sm text-secondary-400">{uploadMessage}</p>}
        </div>

        <div className="mt-6 overflow-hidden rounded-3xl border border-[#162039] bg-[#07101f]">
          <table className="w-full border-collapse text-left text-sm text-[#e2e8f0]">
            <thead className="bg-[#09101d] text-[#94a3b8]">
              <tr>
                <th className="px-4 py-4">Filename</th>
                <th className="px-4 py-4">Job</th>
                <th className="px-4 py-4">Status</th>
                <th className="px-4 py-4">Updated</th>
                <th className="px-4 py-4">Action</th>
              </tr>
            </thead>
            <tbody>
              {files.length > 0 ? files.map((file) => (
                <tr key={file.id} className="border-t border-[#162039] hover:bg-[#0f192f]">
                  <td className="px-4 py-4">
                    <div className="font-medium text-[#e2e8f0]">{file.filename}</div>
                    <div className="text-xs text-[#64748b]">{file.size ? `${(file.size / 1024).toFixed(1)} KB` : 'Unknown size'}</div>
                  </td>
                  <td className="px-4 py-4">{file.jobName}</td>
                  <td className="px-4 py-4 capitalize text-[#94a3b8]">{file.status}</td>
                  <td className="px-4 py-4">{file.updated}</td>
                  <td className="px-4 py-4">
                    <button
                      onClick={() => downloadFile(file.jobId, file.filename)}
                      className="inline-flex items-center gap-2 rounded-2xl bg-[#00d4ff] px-3 py-2 text-xs font-semibold text-[#07101f] hover:bg-[#33e7ff] transition"
                    >
                      <Download className="w-3 h-3" /> Download
                    </button>
                  </td>
                </tr>
              )) : (
                <tr>
                  <td colSpan={5} className="px-4 py-6 text-center text-sm text-[#64748b]">
                    No output files available yet. Upload a CAD file and wait for the pipeline to complete.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

export default FileManager
