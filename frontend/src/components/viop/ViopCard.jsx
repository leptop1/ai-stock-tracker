import SignalBadge from '../signals/SignalBadge'
import { formatChange, formatVolume } from '../../utils/formatters'
import { useViopStore } from '../../store/viopStore'
import { Trash2 } from 'lucide-react'

const categoryColors = {
  'Endeks': 'border-blue-500/40',
  'Döviz': 'border-yellow-500/40',
  'Emtia': 'border-orange-500/40',
  'Hisse': 'border-purple-500/40',
}

const categoryBg = {
  'Endeks': 'text-blue-400',
  'Döviz': 'text-yellow-400',
  'Emtia': 'text-orange-400',
  'Hisse': 'text-purple-400',
}

function formatPrice(price, currency) {
  if (price == null) return 'N/A'
  const opts = { minimumFractionDigits: 2, maximumFractionDigits: currency === 'TRY' ? 2 : 4 }
  const val = new Intl.NumberFormat('tr-TR', opts).format(price)
  return currency === 'TRY' ? `₺${val}` : `$${val}`
}

const HEDGE_COLORS = {
  'HEDGE_AL':   'bg-purple-500/20 text-purple-300 border-purple-500/40',
  'HEDGE_ALMA': 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40',
  'NÖTR':       'bg-gray-500/20 text-gray-400 border-gray-500/40',
}

const HEDGE_LABELS = {
  'HEDGE_AL':   'HEDGE AL',
  'HEDGE_ALMA': 'HEDGE ALMA',
  'NÖTR':       'NÖTR',
}

const CONFIDENCE_DOT = {
  'YÜKSEK': 'bg-white',
  'ORTA':   'bg-gray-300',
  'DÜŞÜK':  'bg-gray-500',
}

function HedgeBadge({ hedgeData, loading }) {
  if (loading) {
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded border text-xs font-semibold bg-gray-700/50 text-gray-500 border-gray-600/40 animate-pulse">
        ...
      </span>
    )
  }
  if (!hedgeData) return null

  const signal = hedgeData.hedge_signal || 'NÖTR'
  const cls = HEDGE_COLORS[signal] || HEDGE_COLORS['NÖTR']
  const label = HEDGE_LABELS[signal] || signal
  const dot = CONFIDENCE_DOT[hedgeData.confidence] || 'bg-gray-500'

  return (
    <span
      title={hedgeData.reasoning || ''}
      className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded border text-xs font-semibold ${cls}`}
    >
      <span className={`inline-block w-1.5 h-1.5 rounded-full ${dot}`} />
      {label}
    </span>
  )
}

export default function ViopCard({ instrument, onClick, onRemove, selected }) {
  const { hedgeSignals, loading } = useViopStore()
  const hedgeData = hedgeSignals?.[instrument.symbol]
  const hedgeLoading = loading.hedge?.[instrument.symbol] ?? false

  const borderColor = categoryColors[instrument.category] || 'border-gray-700'
  const changeColor = (instrument.change_pct ?? 0) >= 0 ? 'text-green-400' : 'text-red-400'

  return (
    <div
      onClick={onClick}
      className={`relative bg-gray-800 rounded-xl border ${borderColor} p-4 cursor-pointer hover:bg-gray-750 transition-all hover:border-gray-500 group ${selected ? 'ring-2 ring-blue-500' : ''}`}
    >
      {onRemove && (
        <button
          onClick={e => { e.stopPropagation(); onRemove(instrument.symbol) }}
          className="absolute top-2 left-2 text-gray-600 hover:text-red-400 opacity-0 group-hover:opacity-100 transition-all p-1 rounded"
          title="Sil"
        >
          <Trash2 size={13} />
        </button>
      )}
      <div className="flex items-start justify-between mb-3">
        <div>
          <div className="font-bold text-white text-base leading-tight">{instrument.name}</div>
          <div className={`text-xs mt-0.5 font-medium ${categoryBg[instrument.category] || 'text-gray-400'}`}>
            {instrument.category}
          </div>
        </div>
        <div className="flex flex-col items-end gap-1">
          <SignalBadge signal={instrument.signal} confidence={instrument.confidence} />
          <HedgeBadge hedgeData={hedgeData} loading={hedgeLoading && !hedgeData} />
        </div>
      </div>
      <div className="flex items-end justify-between">
        <div>
          <div className="text-white font-semibold text-xl">
            {formatPrice(instrument.price, instrument.currency)}
          </div>
          <div className={`text-sm font-medium ${changeColor}`}>{formatChange(instrument.change_pct)}</div>
        </div>
        <div className="text-right">
          <div className="text-gray-400 text-xs">RSI</div>
          <div className="text-gray-200 text-sm font-mono">
            {instrument.rsi != null ? instrument.rsi.toFixed(1) : 'N/A'}
          </div>
        </div>
      </div>
      <div className="mt-3 pt-3 border-t border-gray-700 flex justify-between text-xs text-gray-500">
        <span className="font-mono">{instrument.symbol}</span>
        <span>Vol {formatVolume(instrument.volume)}</span>
      </div>
    </div>
  )
}
