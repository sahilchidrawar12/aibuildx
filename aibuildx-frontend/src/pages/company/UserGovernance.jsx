import { useMemo, useState } from 'react'
import { motion } from 'framer-motion'
import { Eye, Pause, Trash2, Plus } from 'lucide-react'
import toast from 'react-hot-toast'

const initialCompanies = [
  { name: 'SteelCorp India', email: 'admin@steelcorp.com', plan: 'Pro', users: 28, jobs: 140, storage: '42GB', status: 'Active' },
  { name: 'BuildTech Ltd', email: 'admin@buildtech.com', plan: 'Enterprise', users: 112, jobs: 540, storage: '186GB', status: 'Active' },
  { name: 'Infra Solutions', email: 'admin@infrasol.com', plan: 'Trial', users: 2, jobs: 4, storage: '1.8GB', status: 'Trial' },
  { name: 'MetaStructures', email: 'admin@metastruct.com', plan: 'Pro', users: 19, jobs: 112, storage: '58GB', status: 'Active' },
  { name: 'DesignWorks', email: 'admin@designworks.com', plan: 'Pro', users: 13, jobs: 84, storage: '32GB', status: 'Suspended' },
  { name: 'Apex Engineering', email: 'admin@apexeng.com', plan: 'Enterprise', users: 67, jobs: 324, storage: '112GB', status: 'Active' },
  { name: 'UrbanSpan', email: 'admin@urbanspan.com', plan: 'Trial', users: 4, jobs: 9, storage: '6GB', status: 'Trial' },
  { name: 'BridgeCraft', email: 'admin@bridgecraft.com', plan: 'Enterprise', users: 34, jobs: 212, storage: '78GB', status: 'Active' }
]

const archivedCompanies = [
  { name: 'Skyline Fabricators', email: 'admin@skyline.com', plan: 'Pro', users: 5, jobs: 22, storage: '9GB', status: 'Archived' },
  { name: 'Quantum Structures', email: 'admin@quantum.com', plan: 'Trial', users: 1, jobs: 2, storage: '1GB', status: 'Archived' }
]

const filterOptions = ['All', 'Active', 'Suspended', 'Trial', 'Enterprise']

function UserGovernance() {
  const [companies, setCompanies] = useState(initialCompanies)
  const [archived, setArchived] = useState(archivedCompanies)
  const [search, setSearch] = useState('')
  const [activeFilter, setActiveFilter] = useState('All')
  const [showArchived, setShowArchived] = useState(false)
  const [modal, setModal] = useState({ type: '', company: null })
  const [deleteConfirm, setDeleteConfirm] = useState('')
  const [createOpen, setCreateOpen] = useState(false)
  const [newCompany, setNewCompany] = useState({ name: '', email: '', plan: 'Trial', users: 1 })

  const filteredCompanies = useMemo(() => companies.filter((company) => {
    const text = `${company.name} ${company.email}`.toLowerCase()
    const matchesSearch = text.includes(search.toLowerCase())
    const matchesFilter = activeFilter === 'All' || company.status === activeFilter || company.plan === activeFilter
    return matchesSearch && matchesFilter
  }), [companies, search, activeFilter])

  const handleCreate = () => {
    if (!newCompany.name || !newCompany.email) {
      toast.error('Please enter a company name and admin email.')
      return
    }
    setCompanies((prev) => [
      {
        name: newCompany.name,
        email: newCompany.email,
        plan: newCompany.plan,
        users: Number(newCompany.users),
        jobs: 0,
        storage: '0GB',
        status: 'Active'
      },
      ...prev
    ])
    setCreateOpen(false)
    setNewCompany({ name: '', email: '', plan: 'Trial', users: 1 })
    toast.success(`Company ${newCompany.name} added successfully.`)
  }

  const handleSuspend = () => {
    if (!modal.company) return
    setCompanies((prev) => prev.map((row) => (row.name === modal.company.name ? { ...row, status: 'Suspended' } : row)))
    toast.success(`${modal.company.name} suspended.`)
    setModal({ type: '', company: null })
  }

  const handleDelete = () => {
    if (!modal.company) return
    setCompanies((prev) => prev.filter((row) => row.name !== modal.company.name))
    toast.success(`${modal.company.name} deleted permanently.`)
    setModal({ type: '', company: null })
    setDeleteConfirm('')
  }

  const handleRestore = (company) => {
    setArchived((prev) => prev.filter((item) => item.name !== company.name))
    setCompanies((prev) => [{ ...company, status: 'Active' }, ...prev])
    toast.success(`${company.name} restored from archive.`)
  }

  return (
    <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }} className="space-y-6">
      <div className="rounded-3xl border border-secondary-700 bg-secondary-800 p-6 shadow-lg">
        <div className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <span className="inline-flex rounded-full bg-cyan-500/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.24em] text-cyan-300">Company Admin</span>
            <h1 className="mt-3 text-3xl font-semibold text-white">User Governance</h1>
            <p className="mt-2 text-sm text-slate-400">Manage company accounts, archive flow, and employee onboarding controls.</p>
          </div>
          <button onClick={() => setCreateOpen(true)} className="inline-flex items-center gap-2 rounded-2xl bg-cyan-500 px-5 py-3 text-sm font-semibold text-slate-950 hover:bg-cyan-400 transition">
            <Plus className="h-4 w-4" /> Create Company
          </button>
        </div>
      </div>

      <div className="rounded-3xl border border-secondary-700 bg-secondary-900 p-6 shadow-lg">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div className="relative max-w-md">
            <input
              type="search"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search companies..."
              className="input w-full pl-10"
            />
            <span className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-500">🔍</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {filterOptions.map((option) => (
              <button
                key={option}
                onClick={() => setActiveFilter(option)}
                className={`rounded-full px-4 py-2 text-sm font-semibold transition ${activeFilter === option ? 'bg-cyan-500 text-slate-950' : 'bg-slate-950/70 text-slate-300 hover:bg-slate-900'}`}
              >
                {option}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="rounded-3xl border border-secondary-700 bg-secondary-800 p-6 shadow-lg">
        <div className="flex items-center justify-between gap-3">
          <h2 className="text-xl font-semibold text-white">Companies</h2>
          <button
            onClick={() => setShowArchived((prev) => !prev)}
            className={`rounded-2xl px-4 py-2 text-sm font-semibold transition ${showArchived ? 'bg-cyan-500 text-slate-950' : 'bg-slate-950/70 text-slate-300 hover:bg-slate-900'}`}
          >
            {showArchived ? 'Hide Archived' : 'Show Archived'}
          </button>
        </div>

        <div className="mt-6 overflow-hidden rounded-3xl border border-slate-700 bg-slate-950/80">
          <table className="min-w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-950/90 text-slate-400">
              <tr>
                <th className="px-5 py-4">Company</th>
                <th className="px-5 py-4">Admin Email</th>
                <th className="px-5 py-4">Plan</th>
                <th className="px-5 py-4">Users</th>
                <th className="px-5 py-4">Jobs Run</th>
                <th className="px-5 py-4">Storage</th>
                <th className="px-5 py-4">Status</th>
                <th className="px-5 py-4">Actions</th>
              </tr>
            </thead>
            <tbody>
              {(showArchived ? archived : filteredCompanies).map((company) => (
                <tr key={company.name} className="border-t border-slate-900 hover:bg-slate-900/40 transition-colors">
                  <td className="px-5 py-4 font-medium text-white">{company.name}</td>
                  <td className="px-5 py-4 text-slate-300">{company.email}</td>
                  <td className="px-5 py-4 text-slate-300">{company.plan}</td>
                  <td className="px-5 py-4 text-slate-300">{company.users}</td>
                  <td className="px-5 py-4 text-slate-300">{company.jobs}</td>
                  <td className="px-5 py-4 text-slate-300">{company.storage}</td>
                  <td className="px-5 py-4">
                    <span className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${company.status === 'Active' ? 'bg-emerald-500/15 text-emerald-300' : company.status === 'Suspended' ? 'bg-amber-500/15 text-amber-300' : 'bg-slate-700/15 text-slate-300'}`}>
                      {company.status}
                    </span>
                  </td>
                  <td className="px-5 py-4">
                    {showArchived ? (
                      <button onClick={() => handleRestore(company)} className="rounded-2xl border border-cyan-500/20 bg-cyan-500/10 px-3 py-2 text-xs font-semibold text-cyan-300 hover:bg-cyan-500/20 transition">Restore</button>
                    ) : (
                      <div className="flex flex-wrap gap-2">
                        <button onClick={() => toast('Opening company view')} className="rounded-2xl border border-slate-700 bg-slate-950/80 px-3 py-2 text-xs font-semibold text-slate-200 hover:bg-slate-900 transition">
                          <Eye className="inline-block h-4 w-4" />
                        </button>
                        <button onClick={() => setModal({ type: 'suspend', company })} className="rounded-2xl border border-amber-500/20 bg-amber-500/10 px-3 py-2 text-xs font-semibold text-amber-300 hover:bg-amber-500/20 transition">
                          <Pause className="inline-block h-4 w-4" />
                        </button>
                        <button onClick={() => setModal({ type: 'delete', company })} className="rounded-2xl border border-red-500/20 bg-red-500/10 px-3 py-2 text-xs font-semibold text-red-300 hover:bg-red-500/20 transition">
                          <Trash2 className="inline-block h-4 w-4" />
                        </button>
                      </div>
                    )}
                  </td>
                </tr>
              ))}
              {!showArchived && filteredCompanies.length === 0 && (
                <tr>
                  <td colSpan="8" className="px-5 py-10 text-center text-slate-500">No companies found.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {createOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
          <div className="w-full max-w-2xl rounded-3xl border border-cyan-500/20 bg-secondary-900 p-8 shadow-2xl">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h2 className="text-2xl font-semibold text-white">Create Company Account</h2>
                <p className="mt-2 text-sm text-slate-400">Add a new company with an admin account and selected plan.</p>
              </div>
              <button onClick={() => setCreateOpen(false)} className="text-slate-400 hover:text-white">Close</button>
            </div>
            <div className="mt-6 grid gap-4 md:grid-cols-2">
              <label className="block text-sm text-slate-300">
                <span className="mb-2 block">Company Name</span>
                <input value={newCompany.name} onChange={(e) => setNewCompany((prev) => ({ ...prev, name: e.target.value }))} className="input w-full" placeholder="New Company Ltd" />
              </label>
              <label className="block text-sm text-slate-300">
                <span className="mb-2 block">Admin Email</span>
                <input value={newCompany.email} onChange={(e) => setNewCompany((prev) => ({ ...prev, email: e.target.value }))} className="input w-full" placeholder="admin@newco.com" />
              </label>
              <label className="block text-sm text-slate-300">
                <span className="mb-2 block">Plan</span>
                <select value={newCompany.plan} onChange={(e) => setNewCompany((prev) => ({ ...prev, plan: e.target.value }))} className="input w-full">
                  <option>Trial</option>
                  <option>Pro</option>
                  <option>Enterprise</option>
                </select>
              </label>
              <label className="block text-sm text-slate-300">
                <span className="mb-2 block">Max Users</span>
                <input type="number" min="1" value={newCompany.users} onChange={(e) => setNewCompany((prev) => ({ ...prev, users: Number(e.target.value) }))} className="input w-full" />
              </label>
            </div>
            <div className="mt-6 flex justify-end gap-3">
              <button onClick={() => setCreateOpen(false)} className="rounded-2xl border border-slate-700 bg-secondary-800 px-5 py-3 text-sm font-semibold text-slate-300 hover:bg-secondary-700 transition">Cancel</button>
              <button onClick={handleCreate} className="rounded-2xl bg-cyan-500 px-5 py-3 text-sm font-semibold text-slate-950 hover:bg-cyan-400 transition">Create Company Account</button>
            </div>
          </div>
        </div>
      )}

      {modal.type === 'suspend' && modal.company && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
          <div className="w-full max-w-lg rounded-3xl border border-amber-500/20 bg-secondary-900 p-8 shadow-2xl">
            <h2 className="text-2xl font-semibold text-white">Suspend {modal.company.name}?</h2>
            <p className="mt-3 text-sm text-slate-400">This will immediately revoke access for all employees at this company.</p>
            <div className="mt-6 flex justify-end gap-3">
              <button onClick={() => setModal({ type: '', company: null })} className="rounded-2xl border border-slate-700 bg-secondary-800 px-5 py-3 text-sm font-semibold text-slate-300 hover:bg-secondary-700 transition">Cancel</button>
              <button onClick={handleSuspend} className="rounded-2xl bg-amber-500 px-5 py-3 text-sm font-semibold text-slate-950 hover:bg-amber-400 transition">Suspend Company</button>
            </div>
          </div>
        </div>
      )}

      {modal.type === 'delete' && modal.company && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
          <div className="w-full max-w-lg rounded-3xl border border-red-500/20 bg-secondary-900 p-8 shadow-2xl">
            <h2 className="text-2xl font-semibold text-white">Delete {modal.company.name}?</h2>
            <p className="mt-3 text-sm text-slate-400">This action cannot be undone.</p>
            <label className="mt-6 block text-sm text-slate-300">
              <span className="mb-2 block">Type company name to confirm</span>
              <input value={deleteConfirm} onChange={(e) => setDeleteConfirm(e.target.value)} className="input w-full" placeholder={modal.company.name} />
            </label>
            <div className="mt-6 flex justify-end gap-3">
              <button onClick={() => setModal({ type: '', company: null })} className="rounded-2xl border border-slate-700 bg-secondary-800 px-5 py-3 text-sm font-semibold text-slate-300 hover:bg-secondary-700 transition">Cancel</button>
              <button onClick={handleDelete} disabled={deleteConfirm !== modal.company.name} className="rounded-2xl bg-red-500 px-5 py-3 text-sm font-semibold text-slate-950 hover:bg-red-400 transition disabled:opacity-50 disabled:cursor-not-allowed">Delete</button>
            </div>
          </div>
        </div>
      )}
    </motion.div>
  )
}

export default UserGovernance
