import GlowingPanel from '../../components/GlowingPanel'
import { useEffect } from 'react'
import { Server, Cpu, Database } from 'lucide-react'
import { useLLMStore } from '../../stores/llmStore'

function ModelManagement() {
  const { models, systemStats, fetchModels, fetchSystemStats } = useLLMStore()

  useEffect(() => {
    fetchModels()
    fetchSystemStats()
  }, [fetchModels, fetchSystemStats])
  return (
    <div className="space-y-6">
      <header className="rounded-3xl border border-[rgba(0,212,255,0.15)] bg-[#0f1629] p-6">
        <p className="text-sm uppercase tracking-[0.24em] text-[#00d4ff]">LLM Hub</p>
        <h1 className="mt-3 text-3xl font-semibold text-[#e2e8f0]">Model Management</h1>
        <p className="mt-2 text-sm text-[#94a3b8]">Control active inference engines and adjust available model settings.</p>
      </header>

      <div className="grid gap-6 lg:grid-cols-3">
        <GlowingPanel title="Model Fleet" icon={Server}>
          {models.map((model) => (
            <div key={model.id} className="rounded-3xl border border-[#1f2a43] bg-[#07101f] p-4">
              <div className="flex items-center justify-between gap-4">
                <div>
                  <p className="text-sm text-[#94a3b8]">{model.name}</p>
                  <p className="mt-2 text-lg font-semibold text-[#e2e8f0]">{model.status === 'online' ? 'Online' : 'Maintenance'}</p>
                  <p className="text-xs text-[#64748b]">{model.version}</p>
                </div>
                <span className="rounded-full bg-[#0f1928] px-3 py-1 text-xs text-[#94a3b8]">{model.latency ? `${model.latency} ms` : '—'}</span>
              </div>
            </div>
          ))}
        </GlowingPanel>

        <GlowingPanel title="Resource Usage" icon={Cpu}>
          <div className="space-y-4">
            <div className="rounded-3xl bg-[#07101f] p-4">
              <p className="text-sm text-[#94a3b8]">CPU utilization</p>
              <div className="mt-3 h-3 overflow-hidden rounded-full bg-[#12203a]">
                <div className="h-full rounded-full bg-[#00d4ff]" style={{ width: `${systemStats.cpuUtilization}%` }} />
              </div>
              <p className="mt-2 text-sm text-[#e2e8f0]">{systemStats.cpuUtilization}%</p>
            </div>
            <div className="rounded-3xl bg-[#07101f] p-4">
              <p className="text-sm text-[#94a3b8]">Memory usage</p>
              <div className="mt-3 h-3 overflow-hidden rounded-full bg-[#12203a]">
                <div className="h-full rounded-full bg-[#10b981]" style={{ width: `${systemStats.memoryUsage}%` }} />
              </div>
              <p className="mt-2 text-sm text-[#e2e8f0]">{systemStats.memoryUsage}%</p>
            </div>
            <div className="rounded-3xl bg-[#07101f] p-4">
              <p className="text-sm text-[#94a3b8]">GPU utilization</p>
              <div className="mt-3 h-3 overflow-hidden rounded-full bg-[#12203a]">
                <div className="h-full rounded-full bg-[#f59e0b]" style={{ width: `${systemStats.gpuUtilization}%` }} />
              </div>
              <p className="mt-2 text-sm text-[#e2e8f0]">{systemStats.gpuUtilization}%</p>
            </div>
            <div className="rounded-3xl bg-[#07101f] p-4">
              <p className="text-sm text-[#94a3b8]">Active requests</p>
              <p className="mt-2 text-lg font-semibold text-[#e2e8f0]">{systemStats.activeRequests}</p>
            </div>
          </div>
        </GlowingPanel>

        <GlowingPanel title="Database" icon={Database}>
          <div className="rounded-3xl bg-[#07101f] p-4">
            <p className="text-sm text-[#94a3b8]">Embedding store</p>
            <p className="mt-2 text-2xl font-semibold text-[#e2e8f0]">{Math.floor(Math.random() * 50 + 140)}K vectors</p>
            <p className="mt-2 text-sm text-[#94a3b8]">Updated {Math.floor(Math.random() * 30 + 1)} minutes ago</p>
          </div>
        </GlowingPanel>
      </div>
    </div>
  )
}

export default ModelManagement
