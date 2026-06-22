import { LineChart, Line, XAxis, YAxis, Tooltip, ReferenceLine, ResponsiveContainer } from 'recharts'

export default function RSIChart({ indicators }) {
  if (!indicators?.dates) return null
  const data = indicators.dates.map((d, i) => ({
    date: d, rsi: indicators.rsi[i]
  })).filter(d => d.rsi != null)

  const getColor = (rsi) => rsi < 30 ? '#22c55e' : rsi > 70 ? '#ef4444' : '#a78bfa'

  return (
    <ResponsiveContainer width="100%" height={160}>
      <LineChart data={data} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
        <XAxis dataKey="date" tick={{ fill: '#6b7280', fontSize: 10 }} tickLine={false} interval="preserveStartEnd" />
        <YAxis domain={[0, 100]} tick={{ fill: '#6b7280', fontSize: 10 }} tickLine={false} width={30} />
        <Tooltip
          contentStyle={{ background: '#1f2937', border: '1px solid #374151', borderRadius: 8, fontSize: 12 }}
          formatter={(v) => [v?.toFixed(1), 'RSI']}
        />
        <ReferenceLine y={70} stroke="#ef444460" strokeDasharray="4 2" label={{ value: '70', fill: '#ef4444', fontSize: 10 }} />
        <ReferenceLine y={30} stroke="#22c55e60" strokeDasharray="4 2" label={{ value: '30', fill: '#22c55e', fontSize: 10 }} />
        <Line type="monotone" dataKey="rsi" stroke="#a78bfa" dot={false} strokeWidth={2} />
      </LineChart>
    </ResponsiveContainer>
  )
}
