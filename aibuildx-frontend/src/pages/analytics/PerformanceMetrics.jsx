import { motion } from 'framer-motion'
import { Activity, Gauge, Cpu } from 'lucide-react'

const metrics = [
  { name: 'CPU Load', value: '43%', color: 'bg-cyan-600' },
  { name: 'Memory', value: '71%', color: 'bg-violet-600' },
  { name: 'Inference Success', value: '97.2%', color: 'bg-emerald-600' }
]

function PerformanceMetrics() {
  return (
    <div className="space-y-6">
      <div className="rounded-3xl border border-[rgba(0,212,255,0.15)] bg-[#0f1629] p-6">
        <p className="text-sm uppercase tracking-[0.24em] text-[#00d4ff]">Analytics</p>
        <h1 className="mt-3 text-3xl font-semibold text-[#e2e8f0]">Performance Metrics</h1>
        <p className="mt-2 text-sm text-[#94a3b8]">Review system and model performance for your company.</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {metrics.map((metric) => (
          <motion.div key={metric.name} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="rounded-3xl border border-[#1f2a43] bg-[#09101d] p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-[#94a3b8]">{metric.name}</p>
                <p className="mt-3 text-3xl font-semibold text-[#e2e8f0]">{metric.value}</p>
              </div>
              <Cpu className="h-10 w-10 text-[#00d4ff]" />
            </div>
            <div className="mt-6 h-3 rounded-full bg-[#07101f] overflow-hidden">
              <div className={`${metric.color} h-full w-[70%]`} />
            </div>
          </motion.div>
        ))}
      </div>

      <div className="rounded-3xl border border-[#1f2a43] bg-[#09101d] p-6">
        <div className="flex items-center gap-3 mb-4">
          <Activity className="h-6 w-6 text-[#00d4ff]" />
          <h2 className="text-lg font-semibold text-[#e2e8f0]">Resource timeline</h2>
        </div>
        <div className="space-y-4 text-sm text-[#94a3b8]">
          <p>CPU peak is expected during heavy export jobs at 12:00 PM.</p>
          <p>Model inference latency averages 210 ms across all jobs.</p>
          <p>Memory pressure remains stable at 71% during batch conversion.</p>
        </div>
      </div>
    </div>
  )
}

export default PerformanceMetrics
