import { ResponsiveContainer, Treemap, Tooltip } from 'recharts'

function HeatMapChart({ data, title, colorFrom = '#ef4444', colorTo = '#00d4ff' }) {
  const lerp = (a, b, t) => a + (b - a) * t

  const getColor = (value, min, max) => {
    const ratio = max === min ? 0.5 : (value - min) / (max - min)
    const r1 = parseInt(colorFrom.slice(1, 3), 16)
    const g1 = parseInt(colorFrom.slice(3, 5), 16)
    const b1 = parseInt(colorFrom.slice(5, 7), 16)
    const r2 = parseInt(colorTo.slice(1, 3), 16)
    const g2 = parseInt(colorTo.slice(3, 5), 16)
    const b2 = parseInt(colorTo.slice(5, 7), 16)
    const r = Math.round(lerp(r1, r2, ratio))
    const g = Math.round(lerp(g1, g2, ratio))
    const b = Math.round(lerp(b1, b2, ratio))
    return `rgb(${r}, ${g}, ${b})`
  }

  const values = data.map(item => item.value || item.size || 1)
  const min = Math.min(...values)
  const max = Math.max(...values)

  const CustomizedContent = ({ x, y, width, height, index, name, value }) => (
    <g>
      <rect x={x} y={y} width={width} height={height} fill={getColor(value, min, max)} rx={12} ry={12} />
      {width > 70 && height > 30 && (
        <>
          <text x={x + 12} y={y + 20} fill="#e2e8f0" fontSize={12} fontWeight="600">
            {name}
          </text>
          <text x={x + 12} y={y + 35} fill="#94a3b8" fontSize={10}>
            {value}
          </text>
        </>
      )}
    </g>
  )

  return (
    <div className="rounded-3xl border border-[rgba(0,212,255,0.15)] bg-[#0f1629] p-5">
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-lg font-semibold text-[#e2e8f0]" style={{ fontFamily: 'Syne' }}>{title}</h3>
      </div>
      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <Treemap
            data={data}
            dataKey="value"
            ratio="4/3"
            stroke="#0f1629"
            content={<CustomizedContent />}
          >
            <Tooltip cursor={{ fill: 'rgba(0,0,0,0.2)' }} formatter={(value) => [value, 'Value']} />
          </Treemap>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

export default HeatMapChart
