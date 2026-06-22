import {
  ComposedChart, Line, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend
} from 'recharts'

export default function PriceChart({ indicators }) {
  if (!indicators?.dates) return null
  const { dates, close, bb_upper, bb_middle, bb_lower } = indicators
  const data = dates.map((d, i) => ({
    date: d,
    price: close[i],
    upper: bb_upper[i],
    middle: bb_middle[i],
    lower: bb_lower[i],
  })).filter(d => d.price != null)

  return (
    <ResponsiveContainer width="100%" height={280}>
      <ComposedChart data={data} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
        <XAxis dataKey="date" tick={{ fill: '#6b7280', fontSize: 10 }} tickLine={false} interval="preserveStartEnd" />
        <YAxis domain={['auto', 'auto']} tick={{ fill: '#6b7280', fontSize: 10 }} tickLine={false} width={60}
          tickFormatter={v => `$${v.toFixed(0)}`} />
        <Tooltip
          contentStyle={{ background: '#1f2937', border: '1px solid #374151', borderRadius: 8, fontSize: 12 }}
          labelStyle={{ color: '#9ca3af' }}
          formatter={(v, name) => [`$${v?.toFixed(2)}`, name]}
        />
        <Area type="monotone" dataKey="upper" fill="#3b82f620" stroke="none" />
        <Area type="monotone" dataKey="lower" fill="#0f1117" stroke="none" />
        <Line type="monotone" dataKey="upper" stroke="#3b82f650" dot={false} strokeWidth={1} name="BB Üst" />
        <Line type="monotone" dataKey="middle" stroke="#6b7280" dot={false} strokeWidth={1} strokeDasharray="4 2" name="BB Orta" />
        <Line type="monotone" dataKey="lower" stroke="#3b82f650" dot={false} strokeWidth={1} name="BB Alt" />
        <Line type="monotone" dataKey="price" stroke="#60a5fa" dot={false} strokeWidth={2} name="Fiyat" />
      </ComposedChart>
    </ResponsiveContainer>
  )
}
