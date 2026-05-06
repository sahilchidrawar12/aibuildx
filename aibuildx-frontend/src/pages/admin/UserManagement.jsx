import { motion } from 'framer-motion'
import { Users, ShieldCheck, Plus } from 'lucide-react'

const users = [
  { name: 'Maya Patel', email: 'maya@aibuildx.com', role: 'Company Admin', status: 'Active' },
  { name: 'Jordan Kim', email: 'jordan@aibuildx.com', role: 'Employee', status: 'Pending' },
  { name: 'Aditi Shah', email: 'aditi@aibuildx.com', role: 'Employee', status: 'Active' }
]

function UserManagement() {
  return (
    <div className="space-y-6">
      <div className="rounded-3xl border border-[rgba(0,212,255,0.15)] bg-[#0f1629] p-6">
        <p className="text-sm uppercase tracking-[0.24em] text-[#00d4ff]">Admin</p>
        <h1 className="mt-3 text-3xl font-semibold text-[#e2e8f0]">User Management</h1>
        <p className="mt-2 text-sm text-[#94a3b8]">Manage access, roles, and onboarding for all platform users.</p>
      </div>

      <div className="rounded-3xl border border-[#1f2a43] bg-[#09101d] p-6">
        <div className="flex items-center justify-between gap-4 mb-6">
          <div>
            <h2 className="text-lg font-semibold text-[#e2e8f0]">Active user accounts</h2>
            <p className="text-sm text-[#94a3b8]">Assign roles and review account status.</p>
          </div>
          <button className="inline-flex items-center gap-2 rounded-2xl bg-[#00d4ff] px-5 py-3 text-sm font-semibold text-[#07101f] hover:bg-[#33e7ff] transition">
            <Plus className="w-4 h-4" /> Add user
          </button>
        </div>
        <div className="overflow-hidden rounded-3xl border border-[#162039] bg-[#07101f]">
          <table className="w-full border-collapse text-left text-sm text-[#e2e8f0]">
            <thead className="bg-[#09101d] text-[#94a3b8]">
              <tr>
                <th className="px-4 py-4">Name</th>
                <th className="px-4 py-4">Email</th>
                <th className="px-4 py-4">Role</th>
                <th className="px-4 py-4">Status</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user) => (
                <tr key={user.email} className="border-t border-[#162039] hover:bg-[#0f192f]">
                  <td className="px-4 py-4">{user.name}</td>
                  <td className="px-4 py-4">{user.email}</td>
                  <td className="px-4 py-4">{user.role}</td>
                  <td className="px-4 py-4">{user.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="rounded-3xl border border-[#1f2a43] bg-[#09101d] p-6">
        <div className="flex items-center gap-3 mb-3">
          <ShieldCheck className="h-5 w-5 text-[#00d4ff]" />
          <h2 className="text-lg font-semibold text-[#e2e8f0]">Role policies</h2>
        </div>
        <p className="text-sm text-[#94a3b8]">Review role settings for users and ensure permission segregation between super admin and company admin users.</p>
      </div>
    </div>
  )
}

export default UserManagement
