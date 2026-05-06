import { useEffect, useState } from 'react'

function DataCounter({ value, prefix = '', suffix = '', duration = 2000, className = '' }) {
  const [displayValue, setDisplayValue] = useState(0)

  useEffect(() => {
    let start = null
    const startValue = 0
    const diff = value - startValue

    function step(timestamp) {
      if (!start) start = timestamp
      const elapsed = timestamp - start
      const progress = Math.min(elapsed / duration, 1)
      // Easing: ease-out (progress = 1 - Math.pow(1-t, 3))
      const easedProgress = 1 - Math.pow(1 - progress, 3)
      setDisplayValue(Math.floor(startValue + diff * easedProgress))
      if (progress < 1) {
        requestAnimationFrame(step)
      }
    }

    requestAnimationFrame(step)
    return () => {}
  }, [value, duration])

  return (
    <div className={className}>
      <span className="text-3xl font-semibold text-[#e2e8f0]">{prefix}{displayValue.toLocaleString()}{suffix}</span>
    </div>
  )
}

export default DataCounter
