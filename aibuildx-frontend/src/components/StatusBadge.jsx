function StatusBadge({ status }) {
  const config = {
    online: { label: 'ONLINE', color: '#10b981', dotClass: 'animate-pulse bg-[#10b981]' },
    processing: { label: 'PROCESSING', color: '#f59e0b', dotClass: 'animate-spin border border-[#f59e0b] bg-transparent' },
    error: { label: 'ERROR', color: '#ef4444', dotClass: 'bg-[#ef4444]' },
    pending: { label: 'PENDING', color: '#64748b', dotClass: 'bg-[#64748b]' }
  }[status] || { label: 'UNKNOWN', color: '#64748b', dotClass: 'bg-[#64748b]' }

  return (
    <div className="inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-semibold uppercase" style={{ backgroundColor: `${config.color}15`, color: config.color }}>
      <span className={`h-2.5 w-2.5 rounded-full ${config.dotClass}`} />
      <span>{config.label}</span>
    </div>
  )
}

export default StatusBadge
