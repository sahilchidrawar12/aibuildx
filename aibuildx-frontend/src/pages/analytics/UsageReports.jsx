import { motion } from 'framer-motion'
import { FileText, CalendarDays, DollarSign } from 'lucide-react'

const reportItems = [
  { title: 'Monthly Export Volume', value: '412', icon: FileText },
  { title: 'Revision Requests', value: '67', icon: CalendarDays },
  { title: 'License Utilization', value: '82%', icon: DollarSign }
]

function UsageReports() {
  return (
    <div className="space-y-6">
      <div className="rounded-3xl border border-[rgba(0,212,255,0.15)] bg-[#0f1629] p-6">
        <p className="text-sm uppercase tracking-[0.24em] text-[#00d4ff]">Analytics</p>
        <h1 className="mt-3 text-3xl font-semibold text-[#e2e8f0]">Usage Reports</h1>
        <p className="mt-2 text-sm text-[#94a3b8]">Review platform usage, export volume and business metrics.</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {reportItems.map((item) => (
          <motion.div key={item.title} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="rounded-3xl border border-[#1f2a43] bg-[#09101d] p-6">
            <div className="flex items-center gap-3">
              <item.icon className="h-6 w-6 text-[#00d4ff]" />
              <div>
                <p className="text-sm text-[#94a3b8]">{item.title}</p>
                <p className="mt-2 text-2xl font-semibold text-[#e2e8f0]">{item.value}</p>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      <div className="rounded-3xl border border-[#1f2a43] bg-[#09101d] p-6">
        <h2 className="text-lg font-semibold text-[#e2e8f0]">Summary</h2>
        <p className="mt-4 text-sm text-[#94a3b8]">This quarter, conversion demand increased across all active companies while average time-to-delivery improved by 11%.</p>
      </div>
    </div>
  )
}

export default UsageReports
