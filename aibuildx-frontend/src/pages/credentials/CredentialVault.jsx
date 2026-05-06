import { useState } from 'react'
import { Key, Lock } from 'lucide-react'

const vaultItems = [
  { name: 'Tekla API Key', type: 'API Key', status: 'Valid' },
  { name: 'Flask Backend Token', type: 'Secret', status: 'Expiring' },
  { name: 'Cloud Storage Key', type: 'Secret', status: 'Valid' }
]

function CredentialVault() {
  const [revealed, setRevealed] = useState(false)

  return (
    <div className="space-y-6">
      <div className="rounded-3xl border border-[rgba(0,212,255,0.15)] bg-[#0f1629] p-6">
        <p className="text-sm uppercase tracking-[0.24em] text-[#00d4ff]">Company Admin</p>
        <h1 className="mt-3 text-3xl font-semibold text-[#e2e8f0]">Credential Vault</h1>
        <p className="mt-2 text-sm text-[#94a3b8]">Securely store integration secrets and service credentials for your team.</p>
      </div>

      <div className="rounded-3xl border border-[#1f2a43] bg-[#09101d] p-6">
        <div className="flex items-center justify-between gap-4 mb-6">
          <div>
            <h2 className="text-lg font-semibold text-[#e2e8f0]">Sensitive secrets</h2>
            <p className="text-sm text-[#94a3b8]">Mask credentials by default and reveal only when necessary.</p>
          </div>
          <button onClick={() => setRevealed(!revealed)} className="inline-flex items-center gap-2 rounded-2xl bg-[#00d4ff] px-5 py-3 text-sm font-semibold text-[#07101f] hover:bg-[#33e7ff] transition">
            <Lock className="w-4 h-4" /> {revealed ? 'Hide' : 'Reveal'} secrets
          </button>
        </div>
        <div className="space-y-3">
          {vaultItems.map((item) => (
            <div key={item.name} className="rounded-3xl border border-[#162039] bg-[#07101f] p-4 flex items-center justify-between gap-4">
              <div>
                <p className="text-white font-medium">{item.name}</p>
                <p className="text-secondary-400 text-sm">{item.type}</p>
              </div>
              <div className="text-sm text-[#94a3b8]">{item.status}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="rounded-3xl border border-[#1f2a43] bg-[#09101d] p-6">
        <div className="flex items-center gap-3 mb-4">
          <Key className="h-6 w-6 text-[#00d4ff]" />
          <h2 className="text-lg font-semibold text-[#e2e8f0]">Vault controls</h2>
        </div>
        <p className="text-sm text-[#94a3b8]">Rotate API keys regularly and limit access by role.</p>
      </div>
    </div>
  )
}

export default CredentialVault
