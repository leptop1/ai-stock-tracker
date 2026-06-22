import SignalBadge from '../signals/SignalBadge'
import { formatChange, formatVolume } from '../../utils/formatters'
import { Trash2 } from 'lucide-react'

const categoryColors = {
  'Bankacılık': 'border-blue-500/40',
  'Holding': 'border-gray-500/40',
  'Savunma': 'border-red-500/40',
  'Telekomünikasyon': 'border-purple-500/40',
  'Ulaşım': 'border-cyan-500/40',
  'Perakende': 'border-yellow-500/40',
  'Enerji': 'border-orange-500/40',
  'Metal': 'border-zinc-500/40',
  'İnşaat': 'border-amber-500/40',
  'Cam': 'border-teal-500/40',
  'Dayanıklı Tüketim': 'border-pink-500/40',
  'Tekstil': 'border-violet-500/40',
  'Teknoloji': 'border-green-500/40',
  'Otomotiv': 'border-red-400/40',
  'Kimya': 'border-lime-500/40',
}

const categoryTextColors = {
  'Bankacılık': 'text-blue-400',
  'Holding': 'text-gray-400',
  'Savunma': 'text-red-400',
  'Telekomünikasyon': 'text-purple-400',
  'Ulaşım': 'text-cyan-400',
  'Perakende': 'text-yellow-400',
  'Enerji': 'text-orange-400',
  'Metal': 'text-zinc-400',
  'İnşaat': 'text-amber-400',
  'Cam': 'text-teal-400',
  'Dayanıklı Tüketim': 'text-pink-400',
  'Tekstil': 'text-violet-400',
  'Teknoloji': 'text-green-400',
  'Otomotiv': 'text-red-400',
  'Kimya': 'text-lime-400',
}

export default function BistCard({ instrument, onClick, onRemove, selected }) {
  const aboveSma20 = instrument.price != null && instrument.sma_20 != null && instrument.price > instrument.sma_20
  const aboveAvgVol10 = instrument.volume != null && instrument.avg_volume_10 != null && instrument.volume > instrument.avg_volume_10
  const rsiOk = instrument.rsi != null && instrument.rsi <= 50
  const allConditionsMet = aboveSma20 && aboveAvgVol10 && rsiOk
  const borderColor = allConditionsMet ? 'border-green-500' : 'border-red-500'
  const textColor = categoryTextColors[instrument.category] || 'text-gray-400'
  const changeColor = (instrument.change_pct ?? 0) >= 0 ? 'text-green-400' : 'text-red-400'
  const price = instrument.price != null
    ? `₺${new Intl.NumberFormat('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(instrument.price)}`
    : 'N/A'

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
          <div className={`text-xs mt-0.5 font-medium ${textColor}`}>{instrument.category}</div>
        </div>
        <SignalBadge signal={instrument.signal} confidence={instrument.confidence} />
      </div>
      <div className="flex items-end justify-between">
        <div>
          <div className="text-white font-semibold text-xl">{price}</div>
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
