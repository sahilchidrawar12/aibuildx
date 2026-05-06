import { motion } from 'framer-motion'
import { SlidersHorizontal, BarChart3 } from 'lucide-react'

function ModelComparison() {
  const comparisons = [
    { label: 'Accuracy', baseline: '91%', current: '96%' },
    { label: 'Export Speed', baseline: '38m', current: '27m' },
    { label: 'Geometry fidelity', baseline: '88%', current: '94%' }
  ]

  return (
    <div className="space-y-6">
      <div className="rounded-3xl border border-[rgba(0,212,255,0.15)] bg-[#0f1629] p-6">
        <p className="text-sm uppercase tracking-[0.24em] text-[#00d4ff]">Viewer</p>
        <h1 className="mt-3 text-3xl font-semibold text-[#e2e8f0]">Model Comparison</h1>
        <p className="mt-2 text-sm text-[#94a3b8]">Compare conversion results across model versions and export settings.</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {comparisons.map((item) => (
          <motion.div key={item.label} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="rounded-3xl border border-[#1f2a43] bg-[#09101d] p-6">
            <div className="flex items-center gap-3 mb-4">
              <SlidersHorizontal className="h-5 w-5 text-[#00d4ff]" />
              <h2 className="text-lg font-semibold text-[#e2e8f0]">{item.label}</h2>
            </div>
            <div className="space-y-3 text-sm text-[#94a3b8]">
              <div className="flex justify-between rounded-3xl bg-[#07101f] p-4">
                <span>Baseline</span>
                <strong className="text-white">{item.baseline}</strong>
              </div>
              <div className="flex justify-between rounded-3xl bg-[#07101f] p-4">
                <span>Current</span>
                <strong className="text-white">{item.current}</strong>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="rounded-3xl border border-[#1f2a43] bg-[#09101d] p-6">
        <div className="flex items-center gap-3 mb-4">
          <BarChart3 className="h-5 w-5 text-[#00d4ff]" />
          <h2 className="text-lg font-semibold text-[#e2e8f0]">Comparison summary</h2>
        </div>
        <p className="text-sm text-[#94a3b8]">Current model version demonstrates stronger export fidelity and shorter runtime, making it the recommended production candidate.</p>
      </motion.div>
    </div>
  )
}

export default ModelComparison
