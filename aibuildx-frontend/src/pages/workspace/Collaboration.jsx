import { useMemo } from 'react'
import { motion } from 'framer-motion'
import { MessageCircle, Share2, Users } from 'lucide-react'
import { useAuthStore } from '../../stores/authStore'

function Collaboration() {
  const { user, getCompanyUsers } = useAuthStore()
  const collaborators = useMemo(() => {
    const team = getCompanyUsers(user?.companyId)
    return team.filter((member) => member.id !== user?.id)
  }, [getCompanyUsers, user?.companyId, user?.id])
  return (
    <div className="space-y-6">
      <div className="rounded-3xl border border-[rgba(0,212,255,0.15)] bg-[#0f1629] p-6">
        <p className="text-sm uppercase tracking-[0.24em] text-[#00d4ff]">Workspace</p>
        <h1 className="mt-3 text-3xl font-semibold text-[#e2e8f0]">Collaboration</h1>
        <p className="mt-2 text-sm text-[#94a3b8]">Keep your team aligned on model reviews, annotations, and export approvals.</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="rounded-3xl border border-[#1f2a43] bg-[#09101d] p-6">
          <div className="flex items-center gap-3 mb-4">
            <Users className="h-6 w-6 text-[#00d4ff]" />
            <h2 className="text-lg font-semibold text-[#e2e8f0]">Team updates</h2>
          </div>
          <div className="space-y-4">
            {collaborators.length > 0 ? collaborators.map((member) => (
              <div key={member.id} className="rounded-3xl border border-[#162039] bg-[#07101f] p-4 flex items-center justify-between">
                <div>
                  <p className="text-white font-medium">{member.name}</p>
                  <p className="text-secondary-400 text-sm">{member.role || member.permissions?.join(', ') || 'Team member'}</p>
                </div>
                <span className={`rounded-full px-3 py-1 text-xs ${member.lastLogin ? 'bg-green-500/20 text-green-300' : 'bg-secondary-700 text-secondary-300'}`}>{member.lastLogin ? 'Active' : 'Offline'}</span>
              </div>
            )) : (
              <div className="rounded-3xl border border-[#162039] bg-[#07101f] p-4 text-secondary-400">No collaborators found for your company yet.</div>
            )}
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="rounded-3xl border border-[#1f2a43] bg-[#09101d] p-6">
          <div className="flex items-center gap-3 mb-4">
            <MessageCircle className="h-6 w-6 text-[#00d4ff]" />
            <h2 className="text-lg font-semibold text-[#e2e8f0]">Quick actions</h2>
          </div>
          <div className="grid gap-3">
            <button className="rounded-3xl bg-[#0f192f] px-4 py-4 text-left text-sm text-[#e2e8f0] hover:bg-[#11223d] transition">Share model with a stakeholder</button>
            <button className="rounded-3xl bg-[#0f192f] px-4 py-4 text-left text-sm text-[#e2e8f0] hover:bg-[#11223d] transition">Create review request</button>
            <button className="rounded-3xl bg-[#0f192f] px-4 py-4 text-left text-sm text-[#e2e8f0] hover:bg-[#11223d] transition">Assign approval task</button>
          </div>
        </motion.div>
      </div>
    </div>
  )
}

export default Collaboration
