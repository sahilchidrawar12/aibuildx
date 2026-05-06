import { motion, AnimatePresence } from 'framer-motion'
import { X } from 'lucide-react'
import ConfidenceGauge from './ConfidenceGauge'
import { useState } from 'react'

function SelfHealingModal({ isOpen, audit, jobId, onResolved, onClose }) {
  const [loading, setLoading] = useState(false)
  const [selected, setSelected] = useState(() => new Set(audit.suggestions || []))

  const toggleSuggestion = (label) => {
    setSelected(prev => {
      const next = new Set(prev)
      if (next.has(label)) next.delete(label)
      else next.add(label)
      return next
    })
  }

  const handleAction = async (decision) => {
    if (!onResolved) return
    setLoading(true)
    await onResolved(decision)
    setLoading(false)
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm"
          />
          
          {/* Modal */}
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="w-full max-w-lg rounded-2xl border border-cyan-500/30 bg-[#0f1629] p-8"
            >
              {/* Header */}
              <div className="flex items-start justify-between mb-6">
                <div>
                  <h2 className="text-xl font-semibold text-[#e2e8f0]">🤖 AI Validation Consultant</h2>
                </div>
                <button onClick={onClose} className="text-[#94a3b8] hover:text-[#e2e8f0] transition">
                  <X className="h-5 w-5" />
                </button>
              </div>

              {/* Advisory text */}
              <p className="text-sm text-[#94a3b8] mb-6">{audit.advisory_text || 'AI has detected potential issues that may affect model quality.'}</p>

              {/* Suggestions section */}
              <div className="mb-6">
                <h3 className="text-sm font-medium text-[#e2e8f0] mb-3">Suggested Repairs</h3>
                <div className="space-y-2">
                  {(audit.suggestions || []).map((suggestion) => (
                    <label key={suggestion} className="flex items-center gap-3 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={selected.has(suggestion)}
                        onChange={() => toggleSuggestion(suggestion)}
                        className="h-4 w-4 rounded border-[#64748b] bg-[#0f1629] text-[#00d4ff] accent-cyan-400"
                      />
                      <span className="text-sm text-[#e2e8f0]">{suggestion}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Metrics row */}
              <div className="flex justify-center gap-4 mb-6">
                <div className="text-center">
                  <div className="text-2xl font-bold text-[#e2e8f0]">{audit.confidence_score ? Math.round(audit.confidence_score * 100) : 0}</div>
                  <div className="text-xs text-[#94a3b8]">Confidence</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-[#e2e8f0]">{audit.gap_count || 0}</div>
                  <div className="text-xs text-[#94a3b8]">Gaps</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-[#e2e8f0]">{audit.mismatch_count || 0}</div>
                  <div className="text-xs text-[#94a3b8]">Mismatches</div>
                </div>
              </div>

              {/* Confidence Gauge */}
              <div className="flex justify-center mb-6">
                <ConfidenceGauge value={audit.confidence_score || 0} animate={true} />
              </div>

              {/* Action buttons */}
              <div className="flex gap-3">
                <button
                  onClick={() => handleAction('yes')}
                  disabled={loading}
                  className="flex-1 rounded-2xl bg-emerald-600 px-4 py-3 text-sm font-semibold text-white hover:bg-emerald-500 transition disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? 'Applying...' : '✅ Yes, repair now'}
                </button>
                <button
                  onClick={() => handleAction('no')}
                  disabled={loading}
                  className="flex-1 rounded-2xl bg-slate-700 px-4 py-3 text-sm font-semibold text-white hover:bg-slate-600 transition disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? 'Saving...' : '❌ No, export as-is'}
                </button>
              </div>
            </motion.div>
          </div>
        </>
      )}
    </AnimatePresence>
  )
}

export default SelfHealingModal
