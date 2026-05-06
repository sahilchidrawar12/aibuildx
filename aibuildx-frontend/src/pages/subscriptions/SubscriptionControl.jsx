import { useMemo, useState } from 'react'
import { motion } from 'framer-motion'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'
import { ToggleRight, Eye, EyeOff, Pencil, Mail, Check, Sparkles } from 'lucide-react'
import toast from 'react-hot-toast'

const initialPlans = [
  {
    id: 'trial',
    label: 'Trial',
    price: '0',
    jobs: '10/month',
    members: '1',
    support: 'Community',
    badge: 'FREE',
    badgeClass: 'bg-slate-500 text-white'
  },
  {
    id: 'pro',
    label: 'Pro',
    price: '4999',
    jobs: '500/month',
    members: '10',
    support: 'Priority',
    badge: 'POPULAR',
    badgeClass: 'bg-cyan-500 text-slate-900 ring-1 ring-cyan-400'
  },
  {
    id: 'enterprise',
    label: 'Enterprise',
    price: 'Custom',
    jobs: 'Unlimited',
    members: 'Unlimited',
    support: 'Dedicated',
    badge: 'ENTERPRISE',
    badgeClass: 'bg-slate-700 text-slate-100'
  }
]

const planMetrics = [
  { month: 'Jan', revenue: 42 },
  { month: 'Feb', revenue: 57 },
  { month: 'Mar', revenue: 65 },
  { month: 'Apr', revenue: 74 },
  { month: 'May', revenue: 84 },
  { month: 'Jun', revenue: 97 }
]

const initialCredentials = [
  { label: 'Billing Admin', value: 'billing-admin@aibuildx.com', active: true },
  { label: 'Workspace Owner', value: 'ops@aibuildx.com', active: true },
  { label: 'Support Contact', value: 'support@aibuildx.com', active: false }
]

function formatCurrency(value) {
  return `₹${Number(value).toLocaleString('en-IN')}`
}

function SubscriptionControl() {
  const [selectedPlan, setSelectedPlan] = useState('pro')
  const [billingEnabled, setBillingEnabled] = useState(true)
  const [credentials, setCredentials] = useState(initialCredentials)
  const activePlan = useMemo(() => initialPlans.find((plan) => plan.id === selectedPlan), [selectedPlan])

  const toggleBilling = () => {
    setBillingEnabled((current) => !current)
    toast.success(`Billing ${billingEnabled ? 'disabled' : 'enabled'} successfully.`)
  }

  const toggleCredential = (label) => {
    setCredentials((current) => current.map((item) => (item.label === label ? { ...item, active: !item.active } : item)))
    toast.success('Credential status updated.')
  }

  return (
    <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }} className="space-y-6">
      <div className="rounded-3xl border border-secondary-700 bg-secondary-800 p-6 shadow-lg">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <span className="inline-flex rounded-full bg-cyan-500/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.24em] text-cyan-300">Super Admin</span>
            <h1 className="mt-3 text-3xl font-semibold text-white">Subscription Control</h1>
            <p className="mt-2 text-sm text-slate-400">Manage billing settings, active plans, and enterprise access in one place.</p>
          </div>
          <button onClick={toggleBilling} className="inline-flex items-center gap-2 rounded-2xl bg-cyan-500 px-5 py-3 text-sm font-semibold text-slate-950 hover:bg-cyan-400 transition">
            <ToggleRight className={`h-5 w-5 ${billingEnabled ? 'text-slate-950' : 'text-slate-700'}`} />
            {billingEnabled ? 'Billing Enabled' : 'Billing Disabled'}
          </button>
        </div>
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.4fr_0.8fr]">
        <section className="rounded-3xl border border-secondary-700 bg-secondary-900 p-6 shadow-lg">
          <div className="flex items-center justify-between gap-4">
            <div>
              <h2 className="text-xl font-semibold text-white">Plan management</h2>
              <p className="mt-2 text-sm text-slate-400">Review active subscription tiers, adjust plans, and monitor usage growth.</p>
            </div>
            <div className="rounded-2xl bg-slate-950/80 px-4 py-2 text-sm font-semibold text-slate-200">Active: {activePlan.label}</div>
          </div>

          <div className="mt-6 grid gap-4 md:grid-cols-3">
            {initialPlans.map((plan) => (
              <button
                key={plan.id}
                onClick={() => setSelectedPlan(plan.id)}
                className={`rounded-[2rem] border px-5 py-6 text-left transition ${selectedPlan === plan.id ? 'border-cyan-500 bg-slate-950/90 shadow-xl shadow-cyan-500/10' : 'border-slate-700 bg-slate-950/80 hover:border-slate-500'}`}
              >
                <div className="flex items-center justify-between gap-3">
                  <span className="text-sm font-semibold uppercase tracking-[0.22em] text-slate-400">{plan.label}</span>
                  <span className={`rounded-full px-2 py-1 text-[10px] font-semibold uppercase tracking-[0.2em] ${plan.badgeClass}`}>{plan.badge}</span>
                </div>
                <div className="mt-4 flex items-end gap-2">
                  <span className="text-3xl font-semibold text-white">{plan.price === 'Custom' ? plan.price : `₹${plan.price}`}</span>
                  <span className="text-sm text-slate-400">{plan.price === 'Custom' ? '' : '/month'}</span>
                </div>
                <div className="mt-4 space-y-2 text-sm text-slate-300">
                  <div>{plan.jobs}</div>
                  <div>{plan.members} members</div>
                  <div>{plan.support} support</div>
                </div>
              </button>
            ))}
          </div>

          <div className="mt-6 rounded-[2rem] border border-slate-700 bg-slate-950/80 p-5">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <p className="text-sm text-slate-400">Active plan revenue forecast</p>
                <p className="text-2xl font-semibold text-white">{formatCurrency(activePlan.price === 'Custom' ? '120000' : activePlan.price)}</p>
              </div>
              <div className="rounded-2xl bg-slate-900 px-4 py-2 text-sm text-slate-300">Next invoice in 12 days</div>
            </div>
            <div className="mt-6 h-72">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={planMetrics} margin={{ top: 10, right: 0, left: -10, bottom: 0 }}>
                  <CartesianGrid stroke="#172337" vertical={false} />
                  <XAxis dataKey="month" axisLine={false} tickLine={false} tick={{ fill: '#94a3b8', fontSize: 12 }} />
                  <YAxis axisLine={false} tickLine={false} tick={{ fill: '#94a3b8', fontSize: 12 }} />
                  <Tooltip formatter={(value) => [formatCurrency(value), 'Revenue']} contentStyle={{ background: '#020617', border: '1px solid rgba(148,163,184,0.12)' }} />
                  <Bar dataKey="revenue" fill="#22d3ee" radius={[12, 12, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </section>

        <section className="rounded-3xl border border-secondary-700 bg-secondary-900 p-6 shadow-lg">
          <div className="flex items-center justify-between gap-4">
            <div>
              <h2 className="text-xl font-semibold text-white">Payment & credentials</h2>
              <p className="mt-2 text-sm text-slate-400">Keep secure billing contacts and monitor active payment channels.</p>
            </div>
            <button onClick={() => toast.success('Opening billing settings')} className="rounded-2xl border border-cyan-500/20 bg-cyan-500/10 px-4 py-2 text-sm font-semibold text-cyan-300 hover:bg-cyan-500/20 transition">Open billing</button>
          </div>

          <div className="mt-6 space-y-4">
            {credentials.map((credential) => (
              <div key={credential.label} className="rounded-3xl border border-slate-700 bg-slate-950/80 p-4 flex items-center justify-between gap-4">
                <div>
                  <p className="text-sm text-slate-400">{credential.label}</p>
                  <p className="mt-1 text-sm font-semibold text-white">{credential.value}</p>
                </div>
                <button
                  onClick={() => toggleCredential(credential.label)}
                  className={`inline-flex items-center gap-2 rounded-2xl px-4 py-2 text-sm font-semibold transition ${credential.active ? 'bg-emerald-500 text-slate-950' : 'bg-slate-950/80 text-slate-300 hover:bg-slate-900'}`}
                >
                  {credential.active ? <Check className="h-4 w-4" /> : <EyeOff className="h-4 w-4" />}
                  {credential.active ? 'Active' : 'Inactive'}
                </button>
              </div>
            ))}
          </div>

          <div className="mt-8 rounded-[2rem] border border-slate-700 bg-slate-950/80 p-5">
            <p className="text-sm text-slate-400">Billing contacts</p>
            <div className="mt-4 space-y-3">
              <div className="rounded-3xl border border-slate-700 bg-slate-900/90 p-4">
                <p className="text-sm font-medium text-white">Finance Team</p>
                <p className="text-sm text-slate-400">billing@aibuildx.com</p>
              </div>
              <div className="rounded-3xl border border-slate-700 bg-slate-900/90 p-4">
                <p className="text-sm font-medium text-white">Platform Operations</p>
                <p className="text-sm text-slate-400">ops@aibuildx.com</p>
              </div>
            </div>
          </div>

          <div className="mt-6 rounded-3xl border border-slate-700 bg-slate-950/80 p-5">
            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="text-sm text-slate-400">Payment status</p>
                <p className="text-lg font-semibold text-white">On schedule</p>
              </div>
              <span className="inline-flex rounded-full bg-emerald-500/10 px-3 py-1 text-sm font-semibold text-emerald-300">No overdue invoices</span>
            </div>
            <div className="mt-4 flex items-center gap-3 text-sm text-slate-400">
              <Sparkles className="h-4 w-4 text-cyan-300" />
              <span>Subscription renewal is set for the 20th of next month.</span>
            </div>
          </div>
        </section>
      </div>
    </motion.div>
  )
}

export default SubscriptionControl
