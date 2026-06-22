import { useState } from 'react'
import { useStockStore } from '../../store/stockStore'
import { discoverStocks } from '../../api/stockApi'
import { X, Zap, Plus } from 'lucide-react'

export default function DiscoveryPanel({ onClose }) {
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [selected, setSelected] = useState(new Set())
  const { addStock, watchlist } = useStockStore()
  const watchlistTickers = new Set(watchlist.map(w => w.ticker))

  const handleDiscover = async () => {
    setLoading(true)
    try {
      const data = await discoverStocks()
      setResults(data.filter(d => !watchlistTickers.has(d.ticker)))
    } finally {
      setLoading(false)
    }
  }

  const toggle = (ticker) => {
    setSelected(prev => {
      const next = new Set(prev)
      next.has(ticker) ? next.delete(ticker) : next.add(ticker)
      return next
    })
  }

  const addSelected = async () => {
    for (const stock of results.filter(r => selected.has(r.ticker))) {
      await addStock(stock.ticker, stock.name, stock.sector || '')
    }
    onClose()
  }

  return (
    <div className="fixed inset-0 z-60 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/70" onClick={onClose} />
      <div className="relative bg-gray-800 rounded-xl border border-gray-600 w-full max-w-lg mx-4 shadow-2xl max-h-[80vh] flex flex-col">
        <div className="p-4 border-b border-gray-700 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Zap size={16} className="text-yellow-400" />
            <span className="text-white font-semibold text-sm">AI Hisse Keşfi</span>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-white"><X size={16} /></button>
        </div>

        <div className="p-4">
          {results.length === 0 && (
            <button
              onClick={handleDiscover}
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white py-2 rounded-lg text-sm font-medium transition-colors"
            >
              {loading ? 'AI hisseleri taranıyor...' : 'Otomatik Keşfet'}
            </button>
          )}
        </div>

        {results.length > 0 && (
          <>
            <div className="flex-1 overflow-y-auto px-4">
              <div className="text-gray-400 text-xs mb-2">{results.length} hisse bulundu — eklemek istediklerini seç</div>
              {results.map((stock, i) => (
                <div
                  key={i}
                  onClick={() => toggle(stock.ticker)}
                  className={`flex items-center gap-3 p-2 rounded-lg cursor-pointer transition-colors mb-1 ${selected.has(stock.ticker) ? 'bg-blue-600/20 border border-blue-500/40' : 'hover:bg-gray-700'}`}
                >
                  <div className={`w-4 h-4 rounded border flex-shrink-0 flex items-center justify-center ${selected.has(stock.ticker) ? 'bg-blue-500 border-blue-500' : 'border-gray-500'}`}>
                    {selected.has(stock.ticker) && <span className="text-white text-xs">✓</span>}
                  </div>
                  <div>
                    <div className="text-white text-sm font-semibold">{stock.ticker}</div>
                    <div className="text-gray-400 text-xs">{stock.name}</div>
                  </div>
                </div>
              ))}
            </div>
            <div className="p-4 border-t border-gray-700">
              <button
                onClick={addSelected}
                disabled={selected.size === 0}
                className="w-full bg-green-600 hover:bg-green-500 disabled:opacity-40 text-white py-2 rounded-lg text-sm font-medium transition-colors flex items-center justify-center gap-2"
              >
                <Plus size={14} />
                {selected.size} hisse ekle
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
