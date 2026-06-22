import SignalBadge from '../signals/SignalBadge'
import { formatPrice, formatChange, formatVolume } from '../../utils/formatters'
import { Trash2 } from 'lucide-react'

export default function StockCard({ stock, onClick, onRemove, selected }) {
  const changeColor = stock.change_pct >= 0 ? 'text-green-400' : 'text-red-400'
  const borderColor = stock.signal === 'BUY' ? 'border-green-500/30' : stock.signal === 'SELL' ? 'border-red-500/30' : 'border-gray-700'

  return (
    <div
      onClick={onClick}
      className={`relative bg-gray-800 rounded-xl border ${borderColor} p-4 cursor-pointer hover:bg-gray-750 transition-all hover:border-gray-500 group ${selected ? 'ring-2 ring-blue-500' : ''}`}
    >
      {onRemove && (
        <button
          onClick={e => { e.stopPropagation(); onRemove(stock.ticker) }}
          className="absolute top-2 left-2 text-gray-600 hover:text-red-400 opacity-0 group-hover:opacity-100 transition-all p-1 rounded"
          title="Sil"
        >
          <Trash2 size={13} />
        </button>
      )}
      <div className="flex items-start justify-between mb-3">
        <div>
          <div className="font-bold text-white text-lg">{stock.ticker}</div>
          <div className="text-gray-400 text-xs truncate max-w-[120px]">{stock.name}</div>
        </div>
        <SignalBadge signal={stock.signal} confidence={stock.confidence} />
      </div>
      <div className="flex items-end justify-between">
        <div>
          <div className="text-white font-semibold text-xl">{formatPrice(stock.price)}</div>
          <div className={`text-sm font-medium ${changeColor}`}>{formatChange(stock.change_pct)}</div>
        </div>
        <div className="text-right">
          <div className="text-gray-400 text-xs">RSI</div>
          <div className="text-gray-200 text-sm font-mono">{stock.rsi != null ? stock.rsi.toFixed(1) : 'N/A'}</div>
        </div>
      </div>
      <div className="mt-3 pt-3 border-t border-gray-700 flex justify-between text-xs text-gray-500">
        <span>{stock.category}</span>
        <span>Vol {formatVolume(stock.volume)}</span>
      </div>
    </div>
  )
}
