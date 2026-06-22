import { useState } from 'react'
import { Info } from 'lucide-react'

const signalColor = { BUY: 'text-green-400', SELL: 'text-red-400', HOLD: 'text-yellow-400', 'N/A': 'text-gray-500' }
const signalBg = { BUY: 'bg-green-500/10 border-green-500/20', SELL: 'bg-red-500/10 border-red-500/20', HOLD: 'bg-yellow-500/10 border-yellow-500/20', 'N/A': 'bg-gray-700/50 border-gray-600' }

function fmt(v, digits = 4) {
  if (v == null) return 'N/A'
  return typeof v === 'number' ? v.toFixed(digits) : String(v)
}

function RsiTooltip({ item }) {
  const rsi = item.values?.rsi
  const rules = [
    { cond: rsi < 30,  score: '+1.00', label: 'RSI < 30 → Aşırı satım → BUY' },
    { cond: rsi < 40,  score: '+0.60', label: 'RSI < 40 → Oversold yakın → BUY' },
    { cond: rsi <= 60, score: '0.00',  label: '30 ≤ RSI ≤ 60 → Nötr → HOLD' },
    { cond: rsi <= 70, score: '−0.60', label: '60 < RSI ≤ 70 → Overbought yakın → SELL' },
    { cond: true,      score: '−1.00', label: 'RSI > 70 → Aşırı alım → SELL' },
  ]
  const active = rules.find(r => r.cond)
  return (
    <div className="space-y-2">
      <div className="text-gray-300 font-semibold">RSI (Ağırlık: %30)</div>
      <div className="bg-gray-900 rounded p-2 font-mono text-xs space-y-0.5">
        <div>RSI değeri: <span className="text-yellow-300">{fmt(rsi, 2)}</span></div>
        <div>Ham skor: <span className="text-yellow-300">{fmt(item.score, 2)}</span></div>
        <div>Ağırlıklı: <span className="text-blue-300">{item.weight} × {fmt(item.score, 2)} = <b>{fmt(item.weighted, 4)}</b></span></div>
      </div>
      <div className="text-gray-400 text-xs space-y-0.5">
        {rules.map((r, i) => (
          <div key={i} className={`flex gap-2 ${r === active ? 'text-yellow-300' : ''}`}>
            <span className="w-16 shrink-0 font-mono">{r.score}</span>
            <span>{r.label} {r === active ? '← aktif kural' : ''}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

function MacdTooltip({ item }) {
  const { macd_line, signal_line, histogram, histogram_prev } = item.values || {}
  const crossover = histogram_prev != null && histogram_prev * histogram < 0
  let activeRule = ''
  if (crossover) {
    activeRule = histogram > 0 ? 'Crossover yukarı (hist işaret değişti → +) → BUY +0.90' : 'Crossover aşağı (hist işaret değişti → −) → SELL −0.90'
  } else if (histogram > 0 && (histogram_prev == null || histogram > histogram_prev)) {
    activeRule = 'Hist > 0 ve artıyor → BUY +0.50'
  } else if (histogram < 0 && (histogram_prev == null || histogram < histogram_prev)) {
    activeRule = 'Hist < 0 ve azalıyor → SELL −0.50'
  } else {
    activeRule = 'Diğer → HOLD 0.00'
  }
  return (
    <div className="space-y-2">
      <div className="text-gray-300 font-semibold">MACD (Ağırlık: %30)</div>
      <div className="bg-gray-900 rounded p-2 font-mono text-xs space-y-0.5">
        <div>MACD çizgisi: <span className="text-yellow-300">{fmt(macd_line)}</span></div>
        <div>Sinyal çizgisi: <span className="text-yellow-300">{fmt(signal_line)}</span></div>
        <div>Histogram: <span className="text-yellow-300">{fmt(histogram)}</span></div>
        <div>Önceki histogram: <span className="text-yellow-300">{fmt(histogram_prev)}</span></div>
        <div>Ham skor: <span className="text-yellow-300">{fmt(item.score, 2)}</span></div>
        <div>Ağırlıklı: <span className="text-blue-300">{item.weight} × {fmt(item.score, 2)} = <b>{fmt(item.weighted, 4)}</b></span></div>
      </div>
      <div className="text-gray-400 text-xs space-y-0.5">
        <div className="text-gray-500 mb-1">Kural öncelik sırası:</div>
        <div className={crossover ? 'text-yellow-300' : ''}>±0.90 — Crossover: hist işaret değiştiyse {crossover ? '← aktif' : ''}</div>
        <div className={!crossover && Math.abs(item.score) === 0.5 ? 'text-yellow-300' : ''}>±0.50 — Hist yönü devam ediyorsa</div>
        <div className={item.score === 0 ? 'text-yellow-300' : ''}>0.00 — Diğer (HOLD)</div>
        <div className="mt-1 border-t border-gray-700 pt-1 text-yellow-300">← {activeRule}</div>
      </div>
    </div>
  )
}

function BollingerTooltip({ item }) {
  const { percent_b, bb_upper, bb_lower, price } = item.values || {}
  const rules = [
    { cond: percent_b < 0,    score: '+1.00', label: '%B < 0 → Alt bandın altında → BUY' },
    { cond: percent_b < 0.2,  score: '+0.50', label: '%B < 0.2 → Alt banda yakın → BUY' },
    { cond: percent_b <= 0.8, score: '0.00',  label: '0.2 ≤ %B ≤ 0.8 → Nötr → HOLD' },
    { cond: percent_b <= 1.0, score: '−0.50', label: '%B > 0.8 → Üst banda yakın → SELL' },
    { cond: true,             score: '−1.00', label: '%B > 1.0 → Üst bandın üzerinde → SELL' },
  ]
  const active = rules.find(r => r.cond)
  return (
    <div className="space-y-2">
      <div className="text-gray-300 font-semibold">Bollinger Bands (Ağırlık: %25)</div>
      <div className="bg-gray-900 rounded p-2 font-mono text-xs space-y-0.5">
        <div>%B değeri: <span className="text-yellow-300">{fmt(percent_b, 4)}</span></div>
        <div>Fiyat: <span className="text-yellow-300">{fmt(price, 2)}</span></div>
        <div>BB Üst: <span className="text-yellow-300">{fmt(bb_upper, 2)}</span></div>
        <div>BB Alt: <span className="text-yellow-300">{fmt(bb_lower, 2)}</span></div>
        <div>Ham skor: <span className="text-yellow-300">{fmt(item.score, 2)}</span></div>
        <div>Ağırlıklı: <span className="text-blue-300">{item.weight} × {fmt(item.score, 2)} = <b>{fmt(item.weighted, 4)}</b></span></div>
      </div>
      <div className="text-gray-400 text-xs space-y-0.5">
        {rules.map((r, i) => (
          <div key={i} className={`flex gap-2 ${r === active ? 'text-yellow-300' : ''}`}>
            <span className="w-16 shrink-0 font-mono">{r.score}</span>
            <span>{r.label} {r === active ? '← aktif kural' : ''}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

function VolumeTooltip({ item }) {
  const { volume_ratio, price_change_pct } = item.values || {}
  let activeRule = ''
  if (volume_ratio > 1.5 && price_change_pct > 0) activeRule = 'vol>1.5 & fiyat↑ → BUY +0.80'
  else if (volume_ratio > 1.5 && price_change_pct < 0) activeRule = 'vol>1.5 & fiyat↓ → SELL −0.80'
  else if (volume_ratio > 1.2 && price_change_pct > 0) activeRule = 'vol>1.2 & fiyat↑ → BUY +0.40'
  else if (volume_ratio > 1.2 && price_change_pct < 0) activeRule = 'vol>1.2 & fiyat↓ → SELL −0.40'
  else activeRule = 'Normal hacim → HOLD 0.00'
  return (
    <div className="space-y-2">
      <div className="text-gray-300 font-semibold">Hacim (Ağırlık: %15)</div>
      <div className="bg-gray-900 rounded p-2 font-mono text-xs space-y-0.5">
        <div>Hacim oranı: <span className="text-yellow-300">{fmt(volume_ratio, 2)}x</span> <span className="text-gray-500">(anlık / 20g ort.)</span></div>
        <div>Fiyat değişimi: <span className="text-yellow-300">{fmt(price_change_pct, 2)}%</span></div>
        <div>Ham skor: <span className="text-yellow-300">{fmt(item.score, 2)}</span></div>
        <div>Ağırlıklı: <span className="text-blue-300">{item.weight} × {fmt(item.score, 2)} = <b>{fmt(item.weighted, 4)}</b></span></div>
      </div>
      <div className="text-gray-400 text-xs space-y-0.5">
        <div className={volume_ratio > 1.5 && price_change_pct > 0 ? 'text-yellow-300' : ''}>+0.80 — vol &gt; 1.5x & fiyat↑ → BUY</div>
        <div className={volume_ratio > 1.5 && price_change_pct < 0 ? 'text-yellow-300' : ''}>−0.80 — vol &gt; 1.5x & fiyat↓ → SELL</div>
        <div className={volume_ratio > 1.2 && price_change_pct > 0 ? 'text-yellow-300' : ''}>+0.40 — vol &gt; 1.2x & fiyat↑ → BUY</div>
        <div className={volume_ratio > 1.2 && price_change_pct < 0 ? 'text-yellow-300' : ''}>−0.40 — vol &gt; 1.2x & fiyat↓ → SELL</div>
        <div className={item.score === 0 ? 'text-yellow-300' : ''}>0.00 — Diğer → HOLD</div>
        <div className="mt-1 border-t border-gray-700 pt-1 text-yellow-300">← {activeRule}</div>
      </div>
    </div>
  )
}

const TOOLTIPS = { rsi: RsiTooltip, macd: MacdTooltip, bollinger: BollingerTooltip, volume: VolumeTooltip }

function BreakdownRow({ label, itemKey, item }) {
  const [show, setShow] = useState(false)
  const TooltipContent = TOOLTIPS[itemKey]
  const sig = item?.signal || 'N/A'
  const color = signalColor[sig] || 'text-gray-400'
  const bg = signalBg[sig] || signalBg['N/A']

  return (
    <div
      className={`relative flex items-center justify-between rounded px-2 py-1.5 border ${bg} cursor-default`}
      onMouseEnter={() => setShow(true)}
      onMouseLeave={() => setShow(false)}
    >
      <div className="flex items-center gap-1">
        <span className="text-gray-400 text-xs">{label}</span>
        <Info size={9} className="text-gray-600" />
      </div>
      <div className="flex items-center gap-2">
        {item?.weighted != null && (
          <span className="text-gray-600 font-mono text-xs">{item.weighted >= 0 ? '+' : ''}{item.weighted.toFixed(4)}</span>
        )}
        <span className={`text-xs font-semibold ${color}`}>{sig}</span>
      </div>

      {show && TooltipContent && (
        <div className="absolute z-50 bottom-full left-0 mb-2 w-80 bg-gray-800 border border-gray-600 rounded-lg p-3 shadow-xl text-xs text-gray-200 leading-relaxed pointer-events-none">
          <TooltipContent item={item} />
          <div className="absolute bottom-[-6px] left-4 w-3 h-3 bg-gray-800 border-r border-b border-gray-600 rotate-45" />
        </div>
      )}
    </div>
  )
}

export default function SignalSummary({ signal }) {
  if (!signal) return null
  const { score, confidence, breakdown } = signal

  const rows = [
    { key: 'rsi',       label: 'RSI' },
    { key: 'macd',      label: 'MACD' },
    { key: 'bollinger', label: 'Bollinger' },
    { key: 'volume',    label: 'Hacim' },
  ]

  const formula = rows
    .filter(r => breakdown?.[r.key])
    .map(r => {
      const it = breakdown[r.key]
      return `${it.weight}×${it.score >= 0 ? '+' : ''}${it.score}`
    })
    .join(' + ')

  return (
    <div className="bg-gray-800 rounded-lg p-4 space-y-3">
      <div className="flex items-center justify-between">
        <span className="text-gray-400 text-sm">Bileşik Skor</span>
        <span className="text-sm font-mono">{score > 0 ? '+' : ''}{score?.toFixed(3)}</span>
      </div>
      <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all ${score > 0 ? 'bg-green-500' : 'bg-red-500'}`}
          style={{ width: `${Math.min(Math.abs(score) * 100, 100)}%`, marginLeft: score < 0 ? 'auto' : 0 }}
        />
      </div>
      <div className="font-mono text-xs text-gray-600 bg-gray-900/60 rounded px-2 py-1 text-center">
        {formula} = {score >= 0 ? '+' : ''}{score?.toFixed(3)}
        <span className="ml-2 text-gray-700">(±0.3 eşiği: AL/SAT, arada: TUT)</span>
      </div>
      <div className="grid grid-cols-2 gap-2 pt-1">
        {rows.map(({ key, label }) => (
          <BreakdownRow key={key} label={label} itemKey={key} item={breakdown?.[key]} />
        ))}
      </div>
      <div className="text-xs text-gray-500 text-center">Güven: {confidence}</div>
    </div>
  )
}
