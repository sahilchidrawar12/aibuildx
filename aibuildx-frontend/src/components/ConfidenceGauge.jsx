import { useEffect, useRef } from 'react'

function getGaugeColor(value) {
  if (value < 0.5) return '#ef4444'
  if (value < 0.75) return '#f59e0b'
  return '#00d4ff'
}

function ConfidenceGauge({ value = 0, size = 120, animate = true }) {
  const circleRef = useRef(null)
  const normalized = Math.min(1, Math.max(0, value))
  const radius = (size - 24) / 2
  const circumference = 2 * Math.PI * radius

  useEffect(() => {
    if (circleRef.current && animate) {
      circleRef.current.style.strokeDashoffset = `${circumference * (1 - normalized)}`
    }
  }, [normalized, circumference, animate])

  return (
    <div className="relative inline-flex flex-col items-center justify-center">
      <svg width={size} height={size} className="rotate-[-90deg]">
        {/* Outer track */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="#102135"
          strokeWidth="12"
        />
        {/* Fill arc */}
        <circle
          ref={circleRef}
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={getGaugeColor(normalized)}
          strokeWidth="12"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={animate ? circumference : circumference * (1 - normalized)}
          style={{ transition: animate ? 'stroke-dashoffset 0.8s ease, stroke 0.4s ease' : 'none' }}
        />
      </svg>
      {/* Center content */}
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-3xl font-semibold text-[#e2e8f0]">{Math.round(normalized * 100)}%</span>
        <span className="text-sm uppercase tracking-[0.24em] text-[#64748b]">CONFIDENCE</span>
      </div>
    </div>
  )
}

export default ConfidenceGauge
