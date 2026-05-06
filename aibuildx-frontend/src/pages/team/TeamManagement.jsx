import { motion } from 'framer-motion'
import { Users, Layers, Sparkles } from 'lucide-react'

const teamMembers = [
  { name: 'Isla Romero', title: 'Detailing Engineer', status: 'Online' },
  { name: 'Noah Blake', title: 'BIM Coordinator', status: 'Offline' },
  { name: 'Amina Hassan', title: 'QA Specialist', status: 'Reviewing' }
]

function TeamManagement() {
  return (
    <div className="space-y-6">
      <div className="rounded-3xl border border-[rgba(0,212,255,0.15)] bg-[#0f1629] p-6">
        <p className="text-sm uppercase tracking-[0.24em] text-[#00d4ff]">Company Admin</p>
        <h1 className="mt-3 text-3xl font-semibold text-[#e2e8f0]">Team Management</h1>
        <p className="mt-2 text-sm text-[#94a3b8]">Organize teams, assign roles, and view collaboration status.</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="rounded-3xl border border-[#1f2a43] bg-[#09101d] p-6">
          <div className="flex items-center gap-3 mb-4">
            <Users className="h-6 w-6 text-[#00d4ff]" />
            <div>
              <h2 className="text-lg font-semibold text-[#e2e8f0]">Current Team</h2>
              <p className="text-sm text-[#94a3b8]">Active roles and open assignments.</p>
            </div>
          </div>
          <p className="text-3xl font-semibold text-[#e2e8f0]">{teamMembers.length}</p>
        </motion.div>
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="rounded-3xl border border-[#1f2a43] bg-[#09101d] p-6">
          <div className="flex items-center gap-3 mb-4">
            <Layers className="h-6 w-6 text-[#00d4ff]" />
            <div>
              <h2 className="text-lg font-semibold text-[#e2e8f0]">Roles</h2>
              <p className="text-sm text-[#94a3b8]">Admin, review, and execution.</p>
            </div>
          </div>
          <p className="text-3xl font-semibold text-[#e2e8f0]">5 roles</p>
        </motion.div>
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="rounded-3xl border border-[#1f2a43] bg-[#09101d] p-6">
          <div className="flex items-center gap-3 mb-4">
            <Sparkles className="h-6 w-6 text-[#00d4ff]" />
            <div>
              <h2 className="text-lg font-semibold text-[#e2e8f0]">Activity</h2>
              <p className="text-sm text-[#94a3b8]">Recent collaboration checks.</p>
            </div>
          </div>
          <p className="text-3xl font-semibold text-[#e2e8f0]">8 updates</p>
        </motion.div>
      </div>

      <div className="rounded-3xl border border-[#1f2a43] bg-[#09101d] p-6">
        <h2 className="text-lg font-semibold text-[#e2e8f0] mb-4">Team members</h2>
        <div className="space-y-3">
          {teamMembers.map((member) => (
            <div key={member.name} className="rounded-3xl border border-[#162039] bg-[#07101f] p-4 flex items-center justify-between">
              <div>
                <p className="text-white font-medium">{member.name}</p>
                <p className="text-secondary-400 text-sm">{member.title}</p>
              </div>
              <span className={`rounded-full px-3 py-1 text-xs ${member.status === 'Online' ? 'bg-green-500/20 text-green-300' : member.status === 'Reviewing' ? 'bg-yellow-500/20 text-yellow-300' : 'bg-secondary-700 text-secondary-300'}`}>{member.status}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default TeamManagement
