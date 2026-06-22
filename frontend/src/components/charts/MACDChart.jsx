import { ComposedChart, Bar, Line, XAxis, YAxis, Tooltip, ReferenceLine, ResponsiveContainer } from 'recharts'

export default function MACDChart({ indicators }) {
  if (!indicators?.dates) return null
  const data = indicators.dates.map((d, i) => ({
    date: d,
    macd: indicators.macd_line[i],
    signal: indicators.signal_line[i],
    histogram: indicators.histogram[i],
  })).filter(d => d.macd != null)

  return (
    <ResponsiveContainer width="100%" height={160}>
      <ComposedChart data={data} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
        <XAxis dataKey="date" tick={{ fill: '#6b7280', fontSize: 10 }} tickLine={false} interval="preserveStartEnd" />
        <YAxis tick={{ fill: '#6b7280', fontSize: 10 }} tickLine={false} width={40} />
        <Tooltip
          contentStyle={{ background: '#1f2937', border: '1px solid #374151', borderRadius: 8, fontSize: 12 }}
          formatter={(v, name) => [v?.toFixed(4), name]}
        />
        <ReferenceLine y={0} stroke="#4b5563" />
        <Bar dataKey="histogram" fill="#3b82f6"
          cells={data.map((d, i) => <cell key={i} fill={d.histogram >= 0 ? '#22c55e' : '#ef4444'} />)}
          name="Histogram" opacity={0.7}
        />
        <Line type="monotone" dataKey="macd" stroke="#60a5fa" dot={false} strokeWidth={2} name="MACD" />
        <Line type="monotone" dataKey="signal" stroke="#f59e0b" dot={false} strokeWidth={1.5} name="Sinyal" />
      </ComposedChart>
    </ResponsiveContainer>
  )
}
