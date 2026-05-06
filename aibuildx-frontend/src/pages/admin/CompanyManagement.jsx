import { motion } from 'framer-motion'
import { Building, Globe, Layers } from 'lucide-react'

const companies = [
  { name: 'Apex Structures', status: 'Active', projects: 12 },
  { name: 'Skyline Engineering', status: 'Active', projects: 8 },
  { name: 'Vector Design', status: 'Review', projects: 5 }
]

function CompanyManagement() {
  return (
    <div className="space-y-6">
      <div className="rounded-3xl border border-[rgba(0,212,255,0.15)] bg-[#0f1629] p-6">
        <p className="text-sm uppercase tracking-[0.24em] text-[#00d4ff]">Admin</p>
        <h1 className="mt-3 text-3xl font-semibold text-[#e2e8f0]">Company Management</h1>
        <p className="mt-2 text-sm text-[#94a3b8]">Manage company accounts, subscriptions, and enterprise settings.</p>
      </div>

      <div className="rounded-3xl border border-[#1f2a43] bg-[#09101d] p-6">
        <div className="flex items-center justify-between gap-4 mb-6">
          <div>
            <h2 className="text-lg font-semibold text-[#e2e8f0]">Companies</h2>
            <p className="text-sm text-[#94a3b8]">Review active enterprise users and account health.</p>
          </div>
        </div>
        <div className="space-y-4">
          {companies.map((company) => (
            <motion.div key={company.name} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="rounded-3xl border border-[#162039] bg-[#07101f] p-5 flex items-center justify-between gap-4">
              <div>
                <p className="text-white font-semibold">{company.name}</p>
                <p className="text-secondary-400 text-sm">{company.projects} active projects</p>
              </div>
              <div className="text-sm text-[#94a3b8]">{company.status}</div>
            </motion.div>
          ))}
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="rounded-3xl border border-[#1f2a43] bg-[#09101d] p-6">
          <div className="flex items-center gap-3 mb-3">
            <Building className="h-5 w-5 text-[#00d4ff]" />
            <h2 className="text-lg font-semibold text-[#e2e8f0]">Account health</h2>
          </div>
          <p className="text-sm text-[#94a3b8]">Enterprise accounts with high usage are optimized for priority support and export bandwidth.</p>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="rounded-3xl border border-[#1f2a43] bg-[#09101d] p-6">
          <div className="flex items-center gap-3 mb-3">
            <Globe className="h-5 w-5 text-[#00d4ff]" />
            <h2 className="text-lg font-semibold text-[#e2e8f0]">Global policies</h2>
          </div>
          <p className="text-sm text-[#94a3b8]">Set region, security, and data retention defaults for all managed companies.</p>
        </motion.div>
      </div>
    </div>
  )
}

export default CompanyManagement
