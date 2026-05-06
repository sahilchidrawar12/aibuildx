import { motion } from 'framer-motion'
import { Settings, ShieldCheck, Globe } from 'lucide-react'

function SystemSettings() {
  return (
    <div className="space-y-6">
      <div className="rounded-3xl border border-[rgba(0,212,255,0.15)] bg-[#0f1629] p-6">
        <p className="text-sm uppercase tracking-[0.24em] text-[#00d4ff]">Admin</p>
        <h1 className="mt-3 text-3xl font-semibold text-[#e2e8f0]">System Settings</h1>
        <p className="mt-2 text-sm text-[#94a3b8]">Adjust platform defaults for security, localization, and integrations.</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {[
          { label: 'Security', description: 'Access policies and audit settings.', icon: ShieldCheck },
          { label: 'Integrations', description: 'API keys and external connectors.', icon: Settings },
          { label: 'Localization', description: 'Timezone and regional formatting.', icon: Globe }
        ].map((item) => (
          <motion.div key={item.label} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="rounded-3xl border border-[#1f2a43] bg-[#09101d] p-6">
            <div className="flex items-center gap-3 mb-4">
              <item.icon className="h-6 w-6 text-[#00d4ff]" />
              <div>
                <h2 className="text-lg font-semibold text-[#e2e8f0]">{item.label}</h2>
                <p className="text-sm text-[#94a3b8]">{item.description}</p>
              </div>
            </div>
            <button className="rounded-2xl bg-[#0f192f] px-4 py-3 text-sm text-[#e2e8f0] hover:bg-[#11223d] transition">Manage {item.label}</button>
          </motion.div>
        ))}
      </div>
    </div>
  )
}

export default SystemSettings
