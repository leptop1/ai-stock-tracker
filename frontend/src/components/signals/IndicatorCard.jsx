import { useState } from 'react'
import { Info } from 'lucide-react'

const INDICATOR_META = {
  RSI: {
    desc: 'Relative Strength Index (14 periyot) — Fiyatın aşırı alım/satım bölgesinde olup olmadığını gösterir.',
    signal: (v) => {
      const n = parseFloat(v)
      if (isNaN(n)) return 'neutral'
      if (n < 30) return 'buy'
      if (n < 40) return 'weak-buy'
      if (n > 70) return 'sell'
      if (n > 60) return 'weak-sell'
      return 'neutral'
    },
    hint: (v) => {
      const n = parseFloat(v)
      if (isNaN(n)) return null
      if (n < 30) return 'Aşırı satım — güçlü alım sinyali'
      if (n < 40) return 'Oversold bölgesine yakın — zayıf alım'
      if (n > 70) return 'Aşırı alım — güçlü satım sinyali'
      if (n > 60) return 'Overbought bölgesine yakın — zayıf satım'
      return 'Nötr bölge (30–70)'
    },
  },
  MACD: {
    desc: 'Moving Average Convergence Divergence — 12 ve 26 günlük EMA farkı. Trend yönünü ve momentumu gösterir.',
    signal: (v) => {
      const n = parseFloat(v)
      if (isNaN(n)) return 'neutral'
      return n > 0 ? 'buy' : n < 0 ? 'sell' : 'neutral'
    },
    hint: (v) => {
      const n = parseFloat(v)
      if (isNaN(n)) return null
      return n > 0 ? 'Pozitif MACD — yükseliş momentumu' : n < 0 ? 'Negatif MACD — düşüş momentumu' : 'Sıfır çizgisinde'
    },
  },
  Sinyal: {
    desc: 'MACD Sinyal Çizgisi (9 günlük EMA) — MACD bu çizgiyi yukarı keser ise alım, aşağı keser ise satım sinyali.',
    signal: () => 'neutral',
    hint: () => 'MACD çizgisi ile karşılaştırın: MACD > Sinyal → yükseliş',
  },
  'Sinyal Çizgisi': {
    desc: 'MACD Sinyal Çizgisi (9 günlük EMA) — MACD bu çizgiyi yukarı keser ise alım, aşağı keser ise satım sinyali.',
    signal: () => 'neutral',
    hint: () => 'MACD çizgisi ile karşılaştırın: MACD > Sinyal → yükseliş',
  },
  Histogram: {
    desc: 'MACD Histogram — MACD ile sinyal çizgisi arasındaki fark. Pozitif ve artan ise güçlü yükseliş.',
    signal: (v) => {
      const n = parseFloat(v)
      if (isNaN(n)) return 'neutral'
      return n > 0 ? 'buy' : n < 0 ? 'sell' : 'neutral'
    },
    hint: (v) => {
      const n = parseFloat(v)
      if (isNaN(n)) return null
      return n > 0 ? 'Pozitif histogram — yükseliş baskısı' : 'Negatif histogram — düşüş baskısı'
    },
  },
  'BB Üst': {
    desc: 'Bollinger Band Üst Sınır — 20 günlük SMA + 2 standart sapma. Fiyat bu seviyeye ulaşırsa aşırı alım.',
    signal: () => 'neutral',
    hint: () => 'Fiyat bu seviyeye yaklaşırsa satış baskısı artar',
  },
  'BB Alt': {
    desc: 'Bollinger Band Alt Sınır — 20 günlük SMA - 2 standart sapma. Fiyat bu seviyeye ulaşırsa aşırı satım.',
    signal: () => 'neutral',
    hint: () => 'Fiyat bu seviyeye yaklaşırsa alım fırsatı doğabilir',
  },
  'BB %B': {
    desc: 'Bollinger %B — Fiyatın bantlar içindeki konumu. 0 = alt bant, 1 = üst bant, 0.5 = orta.',
    signal: (v) => {
      const n = parseFloat(v)
      if (isNaN(n)) return 'neutral'
      if (n < 0) return 'buy'
      if (n < 0.2) return 'weak-buy'
      if (n > 1) return 'sell'
      if (n > 0.8) return 'weak-sell'
      return 'neutral'
    },
    hint: (v) => {
      const n = parseFloat(v)
      if (isNaN(n)) return null
      if (n < 0) return 'Alt bandın altında — güçlü alım sinyali'
      if (n < 0.2) return 'Alt banda yakın — zayıf alım'
      if (n > 1) return 'Üst bandın üzerinde — güçlü satım sinyali'
      if (n > 0.8) return 'Üst banda yakın — zayıf satım'
      return 'Bantlar içinde nötr bölge'
    },
  },
  'BB Bant': {
    desc: 'Bollinger Band Genişliği — Düşük değer sıkışma (squeeze), yüksek değer yüksek volatilite anlamına gelir.',
    signal: (v) => {
      const n = parseFloat(v)
      if (isNaN(n)) return 'neutral'
      return n < 10 ? 'warning' : 'neutral'
    },
    hint: (v) => {
      const n = parseFloat(v)
      if (isNaN(n)) return null
      return n < 10 ? 'Düşük genişlik — Bollinger Squeeze! Güçlü hareket yakın olabilir' : 'Normal volatilite seviyesi'
    },
  },
  'Hacim Oranı': {
    desc: 'Anlık hacmin 20 günlük ortalama hacme oranı. 1.5x üzeri anlamlı hacim artışı sayılır.',
    signal: (v) => {
      const n = parseFloat(v)
      if (isNaN(n)) return 'neutral'
      return n > 1.5 ? 'warning' : 'neutral'
    },
    hint: (v) => {
      const n = parseFloat(v)
      if (isNaN(n)) return null
      if (n > 2) return 'Çok yüksek hacim — güçlü hareket onayı'
      if (n > 1.5) return 'Yüksek hacim — hareket güvenilir'
      if (n < 0.5) return 'Çok düşük hacim — hareket güvenilmez olabilir'
      return 'Normal hacim seviyesi'
    },
  },
  Hacim: {
    desc: 'Günlük işlem hacmi (kaç adet hisse el değiştirdi).',
    signal: () => 'neutral',
    hint: () => 'Hacim Oranı ile birlikte değerlendirin',
  },
  '52H Yüksek': {
    desc: 'Son 52 haftanın en yüksek kapanış fiyatı.',
    signal: () => 'neutral',
    hint: () => 'Fiyat bu seviyeye yaklaşırsa güçlü direnç bölgesi',
  },
  '52H Düşük': {
    desc: 'Son 52 haftanın en düşük kapanış fiyatı.',
    signal: () => 'neutral',
    hint: () => 'Fiyat bu seviyeye yaklaşırsa güçlü destek bölgesi',
  },
  'Para Birimi': {
    desc: 'Fiyatların gösterildiği para birimi.',
    signal: () => 'neutral',
    hint: () => null,
  },
}

const signalColors = {
  buy: {
    bg: 'bg-green-500/10 border-green-500/30',
    text: 'text-green-400',
    label: 'text-green-500/80',
  },
  'weak-buy': {
    bg: 'bg-green-500/5 border-green-500/20',
    text: 'text-green-300',
    label: 'text-green-600/80',
  },
  sell: {
    bg: 'bg-red-500/10 border-red-500/30',
    text: 'text-red-400',
    label: 'text-red-500/80',
  },
  'weak-sell': {
    bg: 'bg-red-500/5 border-red-500/20',
    text: 'text-red-300',
    label: 'text-red-600/80',
  },
  warning: {
    bg: 'bg-yellow-500/10 border-yellow-500/30',
    text: 'text-yellow-400',
    label: 'text-yellow-500/80',
  },
  neutral: {
    bg: 'bg-gray-800 border-gray-700/50',
    text: 'text-gray-200',
    label: 'text-gray-500',
  },
}

export default function IndicatorCard({ label, value }) {
  const [showTooltip, setShowTooltip] = useState(false)
  const meta = INDICATOR_META[label] || { desc: label, signal: () => 'neutral', hint: () => null }

  const val = value ?? 'N/A'
  const sigKey = val !== 'N/A' ? meta.signal(val) : 'neutral'
  const colors = signalColors[sigKey] || signalColors.neutral
  const hint = val !== 'N/A' ? meta.hint(val) : null

  return (
    <div
      className={`relative rounded-lg p-3 border ${colors.bg} cursor-default`}
      onMouseEnter={() => setShowTooltip(true)}
      onMouseLeave={() => setShowTooltip(false)}
    >
      <div className={`flex items-center gap-1 text-xs mb-1 ${colors.label}`}>
        <span>{label}</span>
        <Info size={10} className="opacity-60" />
      </div>
      <div className={`font-mono text-sm font-semibold ${colors.text}`}>{val}</div>
      {hint && (
        <div className={`text-xs mt-1 ${colors.text} opacity-70`}>{hint}</div>
      )}

      {showTooltip && (
        <div className="absolute z-50 bottom-full left-0 mb-2 w-64 bg-gray-700 border border-gray-600 rounded-lg p-3 shadow-xl text-xs text-gray-200 leading-relaxed pointer-events-none">
          <div className="font-semibold text-white mb-1">{label}</div>
          <div>{meta.desc}</div>
          <div className="absolute bottom-[-6px] left-4 w-3 h-3 bg-gray-700 border-r border-b border-gray-600 rotate-45" />
        </div>
      )}
    </div>
  )
}
