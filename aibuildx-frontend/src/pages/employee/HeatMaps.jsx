import { useEffect, useMemo, useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LineChart, Line, CartesianGrid } from 'recharts'
import HeatMapChart from '../../components/HeatMapChart'
import { useJobStore } from '../../stores/jobStore'

const structuralData = [
  { name: 'Column Grid', value: 847, errors: 23 },
  { name: 'Beam Connections', value: 623, errors: 45 },
  { name: 'Foundation', value: 412, errors: 8 },
  { name: 'Roof Structure', value: 534, errors: 31 },
  { name: 'Lateral Bracing', value: 289, errors: 12 },
  { name: 'Floor Plates', value: 756, errors: 67 },
]

const fixData = [
  { fix: 'Scale Correction', before: 89, after: 4 },
  { fix: 'Node Snap', before: 67, after: 3 },
  { fix: 'Semantic Fix', before: 34, after: 1 },
  { fix: 'Connection Repair', before: 78, after: 5 },
]

const historyData = [
  { name: 'Week 1', score: 62 },
  { name: 'Week 2', score: 68 },
  { name: 'Week 3', score: 71 },
  { name: 'Week 4', score: 75 },
  { name: 'Week 5', score: 79 },
  { name: 'Week 6', score: 81 },
  { name: 'Week 7', score: 85 },
  { name: 'Week 8', score: 87 },
]

function HeatMaps() {
  const [activeTab, setActiveTab] = useState('structural')
  const { fetchJobs, jobs, getUserJobs } = useJobStore()

  useEffect(() => {
    fetchJobs()
  }, [fetchJobs])

  const userJobs = useMemo(() => getUserJobs(), [getUserJobs, jobs])

  const completedJobs = userJobs.filter((job) => job.status === 'completed')
  const avgAccuracy = completedJobs.length > 0
    ? completedJobs.reduce((sum, job) => sum + (job.results?.accuracy || 0), 0) / completedJobs.length
    : 0

  const tabs = [
    { id: 'structural', label: 'Structural Errors' },
    { id: 'verification', label: 'Fix Verification' },
    { id: 'optimization', label: 'Optimization Score' }
  ]

  const computedHistoryData = useMemo(() => {
    if (!userJobs.length) return historyData
    return userJobs.slice(-8).map((job, index) => ({
      name: `Job ${index + 1}`,
      score: job.results?.accuracy ? Math.round(job.results.accuracy) : 50
    }))
  }, [userJobs])

  const computedStructuralData = useMemo(() => {
    const count = userJobs.length || 1
    return structuralData.map((item, idx) => ({
      ...item,
      errors: Math.max(0, Math.round((item.value * (1 - avgAccuracy / 100)) / 2))
    }))
  }, [avgAccuracy, userJobs.length])

  const qualityScore = Math.round(avgAccuracy || 72)

  return (
    <div className="space-y-6">
      <div className="rounded-3xl border border-[rgba(0,212,255,0.15)] bg-[#0f1629] p-6">
        <p className="text-sm uppercase tracking-[0.24em] text-[#00d4ff]">Employee</p>
        <h1 className="mt-3 text-3xl font-semibold text-[#e2e8f0]">My Performance</h1>
        <p className="mt-2 text-sm text-[#94a3b8]">Track your conversion accuracy and job completion metrics.</p>
      </div>

      <div className="rounded-3xl border border-[#1f2a43] bg-[#09101d] p-6">
        <div className="flex flex-wrap gap-3">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`rounded-2xl px-4 py-3 text-sm font-semibold transition ${
                activeTab === tab.id ? 'bg-[#00d4ff] text-[#07101f]' : 'bg-[#07101f] text-[#94a3b8] hover:bg-[#0f233f]'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
        <p className="mt-4 text-sm text-[#94a3b8]">
          {activeTab === 'structural' && 'Structural integrity analysis across building components.'}
          {activeTab === 'verification' && 'Before and after comparison of AI-applied fixes.'}
          {activeTab === 'optimization' && 'Model optimization score progression over time.'}
        </p>
      </div>

      {activeTab === 'structural' && (
        <HeatMapChart
          data={computedStructuralData.map(item => ({ name: item.name, value: item.errors }))}
          title="Structural Errors Heat Map"
          colorFrom="#ef4444"
          colorTo="#00d4ff"
        />
      )}

      {activeTab === 'verification' && (
        <div className="rounded-3xl border border-[rgba(0,212,255,0.15)] bg-[#0f1629] p-6">
          <h3 className="mb-6 text-lg font-semibold text-[#e2e8f0]" style={{ fontFamily: 'Syne' }}>Fix Verification Results</h3>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={fixData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid stroke="#172832" vertical={false} />
                <XAxis dataKey="fix" tick={{ fill: '#94a3b8', fontSize: 12 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: '#94a3b8', fontSize: 12 }} axisLine={false} tickLine={false} />
                <Tooltip
                  wrapperStyle={{ background: '#020617', borderRadius: 16, border: '1px solid #1e2f46' }}
                  contentStyle={{ color: '#e2e8f0', border: 'none', boxShadow: 'none' }}
                />
                <Bar dataKey="before" fill="#ef4444" radius={[4, 4, 0, 0]} animationBegin={0} animationDuration={1000} />
                <Bar dataKey="after" fill="#00d4ff" radius={[4, 4, 0, 0]} animationBegin={500} animationDuration={1000} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {activeTab === 'optimization' && (
        <div className="space-y-6">
          <div className="rounded-3xl border border-[rgba(0,212,255,0.15)] bg-[#0f1629] p-6">
            <h3 className="mb-6 text-lg font-semibold text-[#e2e8f0]" style={{ fontFamily: 'Syne' }}>Optimization Score History</h3>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={computedHistoryData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                  <CartesianGrid stroke="#172832" vertical={false} />
                  <XAxis dataKey="name" tick={{ fill: '#94a3b8', fontSize: 12 }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fill: '#94a3b8', fontSize: 12 }} axisLine={false} tickLine={false} />
                  <Tooltip
                    wrapperStyle={{ background: '#020617', borderRadius: 16, border: '1px solid #1e2f46' }}
                    contentStyle={{ color: '#e2e8f0', border: 'none', boxShadow: 'none' }}
                  />
                  <Line
                    type="monotone"
                    dataKey="score"
                    stroke="#00d4ff"
                    strokeWidth={3}
                    dot={false}
                    animationDuration={2000}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="flex justify-center">
            <div className="rounded-3xl border border-[rgba(0,212,255,0.15)] bg-[#0f1629] p-8">
              <div className="text-center">
                <div className="text-6xl font-bold text-[#00d4ff] mb-2">{qualityScore}%</div>
                <div className="text-sm uppercase tracking-[0.24em] text-[#64748b]">Current Optimization Score</div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default HeatMaps
