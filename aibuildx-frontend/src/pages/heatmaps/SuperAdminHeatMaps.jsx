import { useMemo, useState } from 'react'
import { motion } from 'framer-motion'
import {
  ResponsiveContainer,
  Treemap,
  ScatterChart,
  Scatter,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  ReferenceLine,
  Cell
} from 'recharts'
import { Activity, ShieldCheck } from 'lucide-react'

const dayNames = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
const hours = Array.from({ length: 24 }, (_, index) => index)

const treemapData = [
  { name: 'Tower Design', size: 400, confidence: 0.89 },
  { name: 'Bridge Structure', size: 320, confidence: 0.76 },
  { name: 'Stadium Roof', size: 280, confidence: 0.68 },
  { name: 'Industrial Plant', size: 230, confidence: 0.82 },
  { name: 'Residential Cluster', size: 180, confidence: 0.92 },
  { name: 'Transit Hub', size: 150, confidence: 0.73 }
]

const scatterData = [
  { company: 'Apex', tokens: 12, revenue: 120, jobs: 42 },
  { company: 'BridgeCraft', tokens: 28, revenue: 240, jobs: 68 },
  { company: 'DesignWorks', tokens: 20, revenue: 180, jobs: 54 },
  { company: 'MetaStructures', tokens: 36, revenue: 305, jobs: 80 },
  { company: 'UrbanSpan', tokens: 18, revenue: 145, jobs: 38 },
  { company: 'Infra Solutions', tokens: 10, revenue: 95, jobs: 24 }
]

const getHeatColor = (value) => {
  if (value > 75) return '#22d3ee'
  if (value > 50) return '#38bdf8'
  if (value > 30) return '#60a5fa'
  return '#1e293b'
}

function CustomizedTreemapContent({ x, y, width, height, name, value }) {
  const color = getHeatColor(value * 100)
  return (
    <g>
      <rect x={x} y={y} width={width} height={height} fill={color} rx={14} ry={14} />
      {width > 90 && height > 60 && (
        <foreignObject x={x + 12} y={y + 12} width={width - 24} height={height - 24}>
          <div className="text-sm leading-tight" style={{ color: '#e2e8f0', fontWeight: 700 }}>
            <p>{name}</p>
            <p className="mt-1 text-xs">Confidence {Math.round(value * 100)}%</p>
          </div>
        </foreignObject>
      )}
    </g>
  )
}

function SuperAdminHeatMaps() {
  const [activeTab, setActiveTab] = useState('confidence')

  const heatmapData = useMemo(() => {
    return dayNames.flatMap((day) => hours.map((hour) => {
      const isWeekday = day !== 'Sat' && day !== 'Sun'
      const highTraffic = isWeekday && hour >= 9 && hour <= 18
      const base = highTraffic ? 70 : hour >= 0 && hour <= 5 ? 10 : 35
      const variance = Math.round(base + (Math.sin((hour / 24) * Math.PI * 2) * 20) + Math.random() * 12)
      return { day, hour, volume: Math.max(4, Math.min(100, variance)) }
    }))
  }, [])

  const averageCost = useMemo(() => scatterData.reduce((sum, item) => sum + item.revenue, 0) / scatterData.length, [])

  return (
    <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }} className="space-y-6">
      <div className="rounded-3xl border border-secondary-700 bg-secondary-800 p-6 shadow-lg">
        <span className="inline-flex rounded-full bg-cyan-500/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.24em] text-cyan-300">Super Admin</span>
        <h1 className="mt-3 text-3xl font-semibold text-white">Platform Intelligence</h1>
        <p className="mt-2 text-sm text-slate-400">Monitor confidence, load patterns, and ROI across the platform.</p>
      </div>

      <div className="rounded-3xl border border-secondary-700 bg-secondary-900 p-5 shadow-lg">
        <div className="flex flex-wrap gap-2">
          <button onClick={() => setActiveTab('confidence')} className={`rounded-2xl px-4 py-2 text-sm font-semibold transition ${activeTab === 'confidence' ? 'bg-cyan-500 text-slate-950' : 'bg-slate-950/60 text-slate-300 hover:bg-slate-900'}`}>AI Confidence</button>
          <button onClick={() => setActiveTab('load')} className={`rounded-2xl px-4 py-2 text-sm font-semibold transition ${activeTab === 'load' ? 'bg-cyan-500 text-slate-950' : 'bg-slate-950/60 text-slate-300 hover:bg-slate-900'}`}>System Load</button>
          <button onClick={() => setActiveTab('roi')} className={`rounded-2xl px-4 py-2 text-sm font-semibold transition ${activeTab === 'roi' ? 'bg-cyan-500 text-slate-950' : 'bg-slate-950/60 text-slate-300 hover:bg-slate-900'}`}>Revenue vs Compute</button>
        </div>
      </div>

      {activeTab === 'confidence' && (
        <div className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
          <div className="rounded-3xl border border-secondary-700 bg-secondary-900 p-5 shadow-lg">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-semibold text-white">Model Confidence by Project Type</h2>
                <p className="mt-2 text-sm text-slate-400">Color indicates how confidently the model predicted project structure.</p>
              </div>
            </div>
            <div className="mt-6 h-[420px]">
              <ResponsiveContainer width="100%" height="100%">
                <Treemap
                  data={treemapData}
                  dataKey="size"
                  ratio={4 / 3}
                  stroke="#0f172a"
                  content={<CustomizedTreemapContent />}
                />
              </ResponsiveContainer>
            </div>
          </div>

          <div className="space-y-4">
            <div className="rounded-3xl border border-secondary-700 bg-secondary-900 p-5 shadow-lg">
              <h3 className="text-lg font-semibold text-white">Legend</h3>
              <div className="mt-4 space-y-3 text-sm text-slate-300">
                <div className="flex items-center gap-3"><span className="h-3 w-3 rounded-full bg-orange-500" /> Low confidence (&lt;60%)</div>
                <div className="flex items-center gap-3"><span className="h-3 w-3 rounded-full bg-amber-500" /> Medium confidence (60–75%)</div>
                <div className="flex items-center gap-3"><span className="h-3 w-3 rounded-full bg-cyan-500" /> High confidence (&gt;75%)</div>
              </div>
            </div>
            <div className="rounded-3xl border border-secondary-700 bg-secondary-900 p-5 shadow-lg">
              <h3 className="text-lg font-semibold text-white">Takeaway</h3>
              <p className="mt-3 text-sm text-slate-400">Residential Tower and Office Building show the strongest confidence, while Stadium Structure and Bridge Truss require further model tuning.</p>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'load' && (
        <div className="grid gap-6">
          <div className="rounded-3xl border border-secondary-700 bg-secondary-900 p-5 shadow-lg">
            <h2 className="text-xl font-semibold text-white">Request Volume — Last 7 Days × 24 Hours</h2>
            <p className="mt-2 text-sm text-slate-400">Hover each cell to reveal hourly traffic spikes.</p>
            <div className="mt-6 overflow-hidden rounded-3xl border border-slate-800 bg-slate-950/80 p-4">
              <div className="grid grid-cols-[auto_1fr] gap-4">
                <div className="space-y-4">
                  {hours.filter((hour) => [0, 4, 8, 12, 16, 20].includes(hour)).map((hour) => (
                    <div key={hour} className="text-right text-xs text-slate-400">{`${hour.toString().padStart(2, '0')}:00`}</div>
                  ))}
                </div>
                <div className="overflow-x-auto">
                  <div className="grid grid-cols-7 gap-1">
                    {dayNames.map((day) => (
                      <div key={day} className="text-center text-xs font-semibold text-slate-400">{day}</div>
                    ))}
                    {heatmapData.map((cell) => (
                      <div
                        key={`${cell.day}-${cell.hour}`}
                        title={`${cell.day} ${cell.hour.toString().padStart(2, '0')}:00 — ${cell.volume} requests`}
                        className="h-10 w-full rounded-lg"
                        style={{ backgroundColor: getHeatColor(cell.volume) }}
                      />
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'roi' && (
        <div className="grid gap-6 xl:grid-cols-[1.4fr_0.6fr]">
          <div className="rounded-3xl border border-secondary-700 bg-secondary-900 p-5 shadow-lg">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-semibold text-white">Company ROI Analysis</h2>
                <p className="mt-2 text-sm text-slate-400">Compute spend versus monthly revenue for strategic planning.</p>
              </div>
              <div className="rounded-3xl bg-slate-950/80 px-4 py-2 text-sm text-slate-300">Break-even ratio: 20</div>
            </div>
            <div className="mt-6 h-[420px]">
              <ResponsiveContainer width="100%" height="100%">
                <ScatterChart margin={{ top: 20, right: 20, left: 0, bottom: 20 }}>
                  <CartesianGrid stroke="#15202f" />
                  <XAxis type="number" dataKey="tokens" name="GPU Tokens Used" tick={{ fill: '#94a3b8' }} axisLine={false} tickLine={false} />
                  <YAxis type="number" dataKey="revenue" name="Monthly Revenue" tickFormatter={(value) => `₹${value}`} tick={{ fill: '#94a3b8' }} axisLine={false} tickLine={false} />
                  <Tooltip cursor={{ stroke: '#0f172a' }} contentStyle={{ background: '#020617', borderRadius: 16, border: '1px solid #1e2f46' }} formatter={(value, name) => [name === 'revenue' ? `₹${value}` : value, name]} labelFormatter={() => ''} />
                  <ReferenceLine x={0} stroke="#64748b" />
                  <Scatter data={scatterData} fill="#22d3ee" shape={(props) => {
                    const color = props.payload.revenue / Math.max(1, props.payload.tokens) < 20 ? '#f59e0b' : '#22d3ee'
                    return (
                      <circle cx={props.cx} cy={props.cy} r={Math.max(8, Math.min(18, props.payload.jobs / 40))} fill={color} opacity={0.9} />
                    )
                  }}>
                    {scatterData.map((entry) => (
                      <Cell key={entry.company} fill={entry.revenue / Math.max(1, entry.tokens) < 20 ? '#f59e0b' : '#22d3ee'} />
                    ))}
                  </Scatter>
                </ScatterChart>
              </ResponsiveContainer>
            </div>
          </div>
          <div className="rounded-3xl border border-secondary-700 bg-secondary-900 p-5 shadow-lg">
            <h3 className="text-lg font-semibold text-white">Key metrics</h3>
            <div className="mt-4 space-y-4 text-sm text-slate-400">
              <div className="rounded-3xl bg-slate-950/80 p-4">
                <p>Total companies analyzed</p>
                <p className="mt-2 text-2xl font-semibold text-white">6</p>
              </div>
              <div className="rounded-3xl bg-slate-950/80 p-4">
                <p>Average revenue</p>
                <p className="mt-2 text-2xl font-semibold text-white">{`₹${Math.round(averageCost)}`}</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </motion.div>
  )
}

export default SuperAdminHeatMaps
