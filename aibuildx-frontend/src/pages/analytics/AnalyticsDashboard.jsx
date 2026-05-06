import { motion } from 'framer-motion'
import { BarChart3, TrendingUp, PieChart, LineChart } from 'lucide-react'

function AnalyticsDashboard() {
  const metrics = [
    { label: 'Conversion Rate', value: '86%', icon: TrendingUp, color: 'text-emerald-400' },
    { label: 'Average Throughput', value: '124 jobs', icon: BarChart3, color: 'text-cyan-400' },
    { label: 'Review Success', value: '91%', icon: PieChart, color: 'text-violet-400' },
    { label: 'Active Sessions', value: '42', icon: LineChart, color: 'text-yellow-400' }
  ]

  return (
    <div className="space-y-6">
      <div className="rounded-3xl border border-[rgba(0,212,255,0.15)] bg-[#0f1629] p-6">
        <p className="text-sm uppercase tracking-[0.24em] text-[#00d4ff]">Analytics</p>
        <h1 className="mt-3 text-3xl font-semibold text-[#e2e8f0]">Company Analytics</h1>
        <p className="mt-2 text-sm text-[#94a3b8]">Monitor resource usage, project health, and review metrics.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
        {metrics.map((item) => (
          <motion.div key={item.label} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="rounded-3xl border border-[#1f2a43] bg-[#09101d] p-6">
            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="text-sm text-[#94a3b8]">{item.label}</p>
                <p className="mt-3 text-3xl font-semibold text-[#e2e8f0]">{item.value}</p>
              </div>
              <item.icon className={`h-10 w-10 ${item.color}`} />
            </div>
          </motion.div>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-[1.4fr_0.8fr]">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="rounded-3xl border border-[#1f2a43] bg-[#09101d] p-6">
          <h2 className="text-lg font-semibold text-[#e2e8f0]">Project performance</h2>
          <p className="mt-3 text-sm text-[#94a3b8]">Analyze timeline efficiency and throughput across active conversions.</p>
          <div className="mt-6 space-y-4">
            <div className="rounded-3xl bg-[#07101f] p-4">
              <p className="text-sm text-[#94a3b8]">On-time delivery</p>
              <p className="mt-2 text-xl font-semibold text-[#e2e8f0]">92%</p>
            </div>
            <div className="rounded-3xl bg-[#07101f] p-4">
              <p className="text-sm text-[#94a3b8]">Average validation score</p>
              <p className="mt-2 text-xl font-semibold text-[#e2e8f0]">95.1%</p>
            </div>
          </div>
        </motion.div>
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="rounded-3xl border border-[#1f2a43] bg-[#09101d] p-6">
          <h2 className="text-lg font-semibold text-[#e2e8f0]">Insights</h2>
          <div className="mt-6 space-y-4 text-sm text-[#94a3b8]">
            <p>Supply chain latency improved by 8% after automating export packages.</p>
            <p>Top performing team is the structural detailing group.</p>
            <p>Highest-risk models appear in the western zone of the project.</p>
          </div>
        </motion.div>
      </div>
    </div>
  )
}

export default AnalyticsDashboard
