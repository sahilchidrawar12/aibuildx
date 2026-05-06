import { useState, useEffect, useMemo } from 'react'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'
import StatusBadge from '../../components/StatusBadge'
import DataCounter from '../../components/DataCounter'
import { motion } from 'framer-motion'
import { useLLMStore } from '../../stores/llmStore'

const latencyData = []
const requestsData = []
const DEFAULT_LLM_ENDPOINT = import.meta.env.VITE_LLM_ENDPOINT || `${window.location.origin}/v1`
const DEFAULT_LLM_BACKEND = import.meta.env.VITE_LLM_BACKEND || 'ollama'
const DEFAULT_LLM_MODEL = import.meta.env.VITE_LLM_MODEL || 'meta-llama/Meta-Llama-3-70B-Instruct'

function LLMDashboard() {
  const { models, systemStats, fetchModels, fetchSystemStats } = useLLMStore()
  const [latency, setLatency] = useState(145)
  const [gpuUsage, setGpuUsage] = useState(68.2)
  const [requestsPerMin, setRequestsPerMin] = useState(23)
  const [backend, setBackend] = useState(DEFAULT_LLM_BACKEND)
  const [endpoint, setEndpoint] = useState(DEFAULT_LLM_ENDPOINT)
  const [selectedModel, setSelectedModel] = useState(DEFAULT_LLM_MODEL)

  useEffect(() => {
    fetchModels()
    fetchSystemStats()
  }, [fetchModels, fetchSystemStats])

  // Mock live data updates for smoother dashboard motion
  useEffect(() => {
    const latencyInterval = setInterval(() => {
      setLatency(prev => Math.max(120, Math.min(180, prev + (Math.random() - 0.5) * 60)))
    }, 3000)

    const gpuInterval = setInterval(() => {
      setGpuUsage(prev => Math.max(60, Math.min(85, prev + (Math.random() - 0.5) * 6)))
    }, 5000)

    const requestsInterval = setInterval(() => {
      setRequestsPerMin(prev => Math.max(15, Math.min(35, prev + (Math.random() - 0.5) * 10)))
    }, 4000)

    return () => {
      clearInterval(latencyInterval)
      clearInterval(gpuInterval)
      clearInterval(requestsInterval)
    }
  }, [])

  useEffect(() => {
    const now = new Date()
    const timeStr = now.toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit' })

    latencyData.push({ time: timeStr, latency })
    requestsData.push({ time: timeStr, requests: requestsPerMin })

    if (latencyData.length > 20) latencyData.shift()
    if (requestsData.length > 20) requestsData.shift()
  }, [latency, requestsPerMin])

  const backends = ['vllm', 'ollama', 'llama_cpp']
  const availableModels = useMemo(
    () => models.length ? models.map((model) => model.name) : [DEFAULT_LLM_MODEL, 'llama-3-70b', 'vicuna-13b'],
    [models]
  )

  const modelName = selectedModel || availableModels[0]
  const selectedModelDetails = models.find((model) => model.name === modelName) || {}
  const modelStatus = selectedModelDetails.status || 'online'
  const { cpuUtilization, memoryUsage, gpuUtilization, activeRequests } = systemStats

  useEffect(() => {
    if (!selectedModel && availableModels.length) {
      setSelectedModel(availableModels[0])
    }
  }, [availableModels, selectedModel])

  return (
    <div className="space-y-6">
      <div className="rounded-3xl border border-[rgba(0,212,255,0.15)] bg-[#0f1629] p-6">
        <p className="text-sm uppercase tracking-[0.24em] text-[#00d4ff]">Super Admin</p>
        <h1 className="mt-3 text-3xl font-semibold text-[#e2e8f0]">LLM Orchestration</h1>
        <p className="mt-2 text-sm text-[#94a3b8]">Monitor and manage AI model performance for structural analysis.</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Left Column */}
        <div className="space-y-6">
          <div className="rounded-3xl border border-[#1f2a43] bg-[#09101d] p-6">
            <div className="flex items-center gap-4 mb-6">
              <StatusBadge status={modelStatus} />
              <div>
                <p className="text-sm text-[#94a3b8]">Active Model</p>
                <p className="text-lg font-semibold text-[#e2e8f0] font-mono text-sm">{modelName}</p>
              </div>
            </div>

            <div className="grid gap-4">
              <div>
                <p className="text-sm text-[#94a3b8] mb-2">Select Model</p>
                <select
                  value={modelName}
                  onChange={(e) => setSelectedModel(e.target.value)}
                  className="w-full px-4 py-2 rounded-2xl bg-[#07101f] border border-[#1f2a43] text-[#e2e8f0] text-sm focus:border-[#00d4ff] focus:outline-none"
                >
                  {availableModels.map((model) => (
                    <option key={model} value={model}>{model}</option>
                  ))}
                </select>
              </div>

              <div>
                <p className="text-sm text-[#94a3b8] mb-2">Backend</p>
                <div className="flex flex-wrap gap-2">
                  {backends.map((b) => (
                    <button
                      key={b}
                      onClick={() => setBackend(b)}
                      className={`px-4 py-2 rounded-2xl text-sm font-semibold transition ${
                        backend === b
                          ? 'bg-[#00d4ff] text-[#07101f]'
                          : 'bg-[#07101f] text-[#94a3b8] border border-[#1f2a43] hover:border-[#00d4ff]/50'
                      }`}
                    >
                      {b}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <p className="text-sm text-[#94a3b8] mb-2">API Endpoint</p>
                <input
                  value={endpoint}
                  onChange={(e) => setEndpoint(e.target.value)}
                  className="w-full px-4 py-2 rounded-2xl bg-[#07101f] border border-[#1f2a43] text-[#e2e8f0] text-sm focus:border-[#00d4ff] focus:outline-none"
                />
              </div>
            </div>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <div className="rounded-3xl border border-[#1f2a43] bg-[#09101d] p-6">
              <p className="text-sm text-[#94a3b8] mb-2">Latency</p>
              <DataCounter value={latency} suffix="ms" />
            </div>
            <div className="rounded-3xl border border-[#1f2a43] bg-[#09101d] p-6">
              <p className="text-sm text-[#94a3b8] mb-2">Requests/min</p>
              <DataCounter value={requestsPerMin} />
            </div>
          </div>
        </div>

        {/* Right Column */}
        <div className="space-y-6">
          <div className="rounded-3xl border border-[#1f2a43] bg-[#09101d] p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <p className="text-sm text-[#94a3b8]">Inference Metrics</p>
                <p className="text-lg font-semibold text-[#e2e8f0]">Live system health</p>
              </div>
              <span className="text-sm text-[#e2e8f0]">Updated just now</span>
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="rounded-2xl bg-[#07101f] p-4 border border-[#1f2a43]">
                <p className="text-xs uppercase tracking-[0.24em] text-[#94a3b8]">CPU</p>
                <p className="mt-2 text-2xl font-semibold text-[#e2e8f0]">{cpuUtilization ?? 0}%</p>
              </div>
              <div className="rounded-2xl bg-[#07101f] p-4 border border-[#1f2a43]">
                <p className="text-xs uppercase tracking-[0.24em] text-[#94a3b8]">Memory</p>
                <p className="mt-2 text-2xl font-semibold text-[#e2e8f0]">{memoryUsage ?? 0}%</p>
              </div>
              <div className="rounded-2xl bg-[#07101f] p-4 border border-[#1f2a43]">
                <p className="text-xs uppercase tracking-[0.24em] text-[#94a3b8]">GPU</p>
                <p className="mt-2 text-2xl font-semibold text-[#e2e8f0]">{gpuUtilization ?? gpuUsage.toFixed(1)}%</p>
              </div>
              <div className="rounded-2xl bg-[#07101f] p-4 border border-[#1f2a43]">
                <p className="text-xs uppercase tracking-[0.24em] text-[#94a3b8]">In-flight Queries</p>
                <p className="mt-2 text-2xl font-semibold text-[#e2e8f0]">{activeRequests ?? 0}</p>
              </div>
            </div>
          </div>

          <div className="rounded-3xl border border-[#1f2a43] bg-[#09101d] p-6">
            <p className="text-sm text-[#94a3b8] mb-4">Latency History</p>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={latencyData}>
                  <CartesianGrid stroke="#172832" vertical={false} />
                  <XAxis dataKey="time" tick={{ fill: '#94a3b8', fontSize: 12 }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fill: '#94a3b8', fontSize: 12 }} axisLine={false} tickLine={false} />
                  <Tooltip
                    wrapperStyle={{ background: '#020617', borderRadius: 16, border: '1px solid #1e2f46' }}
                    contentStyle={{ color: '#e2e8f0', border: 'none', boxShadow: 'none' }}
                  />
                  <Line
                    type="monotone"
                    dataKey="latency"
                    stroke="#00d4ff"
                    strokeWidth={2}
                    dot={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom ChromaDB Panel */}
      <div className="rounded-3xl border border-[#1f2a43] bg-[#09101d] p-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-[#e2e8f0]">ChromaDB Vector Store</h3>
            <div className="flex items-center gap-4 mt-2">
              <span className="text-sm text-[#94a3b8]">Collection: structural_kb</span>
              <span className="text-sm text-[#94a3b8]">Documents: 1,247</span>
              <span className="text-sm text-[#94a3b8]">Embedding: all-MiniLM-L6-v2</span>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-[#94a3b8]">Last ingestion: 2 hours ago</span>
            <StatusBadge status="online" />
          </div>
        </div>
      </div>
    </div>
  )
}

export default LLMDashboard
