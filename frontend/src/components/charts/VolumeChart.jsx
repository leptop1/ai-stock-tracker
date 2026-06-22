import { BarChart, Bar, XAxis, YAxis, Tooltip, ReferenceLine, ResponsiveContainer, Cell } from 'recharts'
import { formatVolume } from '../../utils/formatters'

export default function VolumeChart({ indicators }) {
  if (!indicators?.dates) return null
  const closes = indicators.close
  const data = indicators.dates.map((d, i) => ({
    date: d,
    volume: indicators.volume[i],
    up: closes[i] >= (closes[i - 1] || closes[i]),
  })).filter(d => d.volume != null)

  const avgVol = indicators.avg_volume_20

  return (
    <ResponsiveContainer width="100%" height={140}>
      <BarChart data={data} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
        <XAxis dataKey="date" tick={{ fill: '#6b7280', fontSize: 10 }} tickLine={false} interval="preserveStartEnd" />
        <YAxis tick={{ fill: '#6b7280', fontSize: 10 }} tickLine={false} width={40}
          tickFormatter={v => formatVolume(v)} />
        <Tooltip
          contentStyle={{ background: '#1f2937', border: '1px solid #374151', borderRadius: 8, fontSize: 12 }}
          formatter={(v) => [formatVolume(v), 'Hacim']}
        />
        {avgVol && <ReferenceLine y={avgVol} stroke="#f59e0b80" strokeDasharray="4 2" label={{ value: 'Ort', fill: '#f59e0b', fontSize: 10 }} />}
        <Bar dataKey="volume">
          {data.map((d, i) => <Cell key={i} fill={d.up ? '#22c55e80' : '#ef444480'} />)}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
