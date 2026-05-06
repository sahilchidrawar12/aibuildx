import { motion } from 'framer-motion'
import { Upload, FileText, Activity, Layers } from 'lucide-react'

function WorkspaceDashboard() {
  return (
    <div className="space-y-6">
      <div className="rounded-3xl border border-[rgba(0,212,255,0.15)] bg-[#0f1629] p-6">
        <p className="text-sm uppercase tracking-[0.24em] text-[#00d4ff]">Workspace</p>
        <h1 className="mt-3 text-3xl font-semibold text-[#e2e8f0]">Workspace Overview</h1>
        <p className="mt-2 text-sm text-[#94a3b8]">Track file uploads, collaboration, and project handoffs.</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {[
          { label: 'Active Jobs', value: '14', icon: Upload },
          { label: 'Files', value: '112', icon: FileText },
          { label: 'Collaboration', value: '8 active', icon: Activity }
        ].map((item) => (
          <motion.div key={item.label} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="rounded-3xl border border-[#1f2a43] bg-[#09101d] p-6">
            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="text-sm text-[#94a3b8]">{item.label}</p>
                <p className="mt-3 text-3xl font-semibold text-[#e2e8f0]">{item.value}</p>
              </div>
              <item.icon className="h-10 w-10 text-[#00d4ff]" />
            </div>
          </motion.div>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="rounded-3xl border border-[#1f2a43] bg-[#09101d] p-6">
          <div className="flex items-center gap-3 mb-4">
            <Layers className="h-6 w-6 text-[#00d4ff]" />
            <h2 className="text-lg font-semibold text-[#e2e8f0]">Recent Activity</h2>
          </div>
          <div className="space-y-3 text-sm text-[#94a3b8]">
            <p>01/03: Imported section dataset</p>
            <p>01/03: Validated model for IFC export</p>
            <p>12/02: Shared review notes with team</p>
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="rounded-3xl border border-[#1f2a43] bg-[#09101d] p-6">
          <div className="flex items-center gap-3 mb-4">
            <Activity className="h-6 w-6 text-[#00d4ff]" />
            <h2 className="text-lg font-semibold text-[#e2e8f0]">Quick Access</h2>
          </div>
          <div className="grid gap-3">
            <button className="rounded-3xl bg-[#0f192f] px-4 py-4 text-left text-sm text-[#e2e8f0] hover:bg-[#11223d] transition">Upload CAD file</button>
            <button className="rounded-3xl bg-[#0f192f] px-4 py-4 text-left text-sm text-[#e2e8f0] hover:bg-[#11223d] transition">Open latest viewer</button>
            <button className="rounded-3xl bg-[#0f192f] px-4 py-4 text-left text-sm text-[#e2e8f0] hover:bg-[#11223d] transition">Review AI recommendations</button>
          </div>
        </motion.div>
      </div>
    </div>
  )
}

export default WorkspaceDashboard
