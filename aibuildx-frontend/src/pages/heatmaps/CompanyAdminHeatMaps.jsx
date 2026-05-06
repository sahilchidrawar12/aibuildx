import { useState } from 'react'
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Tooltip, ResponsiveContainer } from 'recharts'
import { Thermometer, Activity } from 'lucide-react'

const radarData = [
  { metric: 'Model Risk', value: 88 },
  { metric: 'Export Density', value: 74 },
  { metric: 'Review Lag', value: 61 },
  { metric: 'Delivery Speed', value: 83 },
  { metric: 'Quality', value: 92 }
]

function CompanyAdminHeatMaps() {
  const [activeMetric, setActiveMetric] = useState('quality')

  return (
    <div className="space-y-6">
      <div className="rounded-3xl border border-[rgba(0,212,255,0.15)] bg-[#0f1629] p-6">
        <p className="text-sm uppercase tracking-[0.24em] text-[#00d4ff]">Company Admin</p>
        <h1 className="mt-3 text-3xl font-semibold text-[#e2e8f0]">Project Heat Maps</h1>
        <p className="mt-2 text-sm text-[#94a3b8]">Review team performance and delivery hotspots for your company.</p>
      </div>

      <div className="rounded-3xl border border-[#1f2a43] bg-[#09101d] p-6">
        <div className="flex flex-wrap gap-3">
          {['quality', 'speed', 'risk'].map((item) => (
            <button key={item} onClick={() => setActiveMetric(item)} className={`rounded-2xl px-4 py-3 text-sm font-semibold ${activeMetric === item ? 'bg-[#00d4ff] text-[#07101f]' : 'bg-[#07101f] text-[#94a3b8] hover:bg-[#0f233f]'}`}>
              {item === 'quality' ? 'Quality' : item === 'speed' ? 'Speed' : 'Risk'}
            </button>
          ))}
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-[1.3fr_0.7fr]">
        <div className="rounded-3xl border border-[#1f2a43] bg-[#09101d] p-6">
          <h2 className="text-lg font-semibold text-[#e2e8f0]">Team radar</h2>
          <p className="mt-3 text-sm text-[#94a3b8]">Compare delivery metrics across key project areas.</p>
          <div className="mt-6 h-[360px]">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={radarData} outerRadius="80%">
                <PolarGrid stroke="#172832" />
                <PolarAngleAxis dataKey="metric" tick={{ fill: '#94a3b8', fontSize: 12 }} />
                <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fill: '#64748b', fontSize: 10 }} />
                <Radar name="Score" dataKey="value" stroke="#00d4ff" fill="#00d4ff" fillOpacity={0.3} />
                <Tooltip wrapperStyle={{ background: '#020617', borderRadius: '16px', border: '1px solid #1e2f46' }} contentStyle={{ color: '#e2e8f0', border: 'none', boxShadow: 'none' }} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="space-y-6">
          <div className="rounded-3xl border border-[#1f2a43] bg-[#09101d] p-6">
            <div className="flex items-center gap-3 mb-4">
              <Thermometer className="h-5 w-5 text-[#00d4ff]" />
              <h3 className="text-lg font-semibold text-[#e2e8f0]">Metric focus</h3>
            </div>
            <p className="text-sm text-[#94a3b8]">Active metric: {activeMetric === 'quality' ? 'Quality' : activeMetric === 'speed' ? 'Speed' : 'Risk'}</p>
          </div>
          <div className="rounded-3xl border border-[#1f2a43] bg-[#09101d] p-6">
            <div className="flex items-center gap-3 mb-4">
              <Activity className="h-5 w-5 text-[#00d4ff]" />
              <h3 className="text-lg font-semibold text-[#e2e8f0]">Status summary</h3>
            </div>
            <p className="text-sm text-[#94a3b8]">Your current release pipeline is tracking ahead of schedule with high quality scores. Continue to monitor risk areas in structural detailing.</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default CompanyAdminHeatMaps
