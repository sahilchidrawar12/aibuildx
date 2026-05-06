import { motion } from 'framer-motion'

const colorMap = {
  cyan: '#00d4ff',
  amber: '#f59e0b',
  green: '#10b981',
  red: '#ef4444'
}

function GlowingPanel({ title, icon: Icon, children, glowColor = 'cyan', className = '' }) {
  const color = colorMap[glowColor] || colorMap.cyan

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`rounded-3xl border border-[${color}]/20 bg-[#0f1629] p-6 transition-all duration-300 hover:shadow-[0_0_20px_${color}/30] ${className}`}
    >
      {(title || Icon) && (
        <div className="mb-4 flex items-center gap-3">
          {Icon && <Icon className="h-5 w-5 text-[#00d4ff]" />}
          {title && <h3 className="font-semibold text-[#e2e8f0]" style={{ fontFamily: 'Space Mono' }}>{title}</h3>}
        </div>
      )}
      {children}
    </motion.div>
  )
}

export default GlowingPanel
