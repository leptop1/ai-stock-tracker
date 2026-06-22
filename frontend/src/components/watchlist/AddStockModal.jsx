import { useState, useEffect, useCallback } from 'react'
import { useStockStore } from '../../store/stockStore'
import { searchStocks } from '../../api/stockApi'
import { Search, X, Plus } from 'lucide-react'

export default function AddStockModal({ onClose }) {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [searching, setSearching] = useState(false)
  const { addStock } = useStockStore()

  const doSearch = useCallback(async (q) => {
    if (!q.trim()) { setResults([]); return }
    setSearching(true)
    try {
      const data = await searchStocks(q)
      setResults(data)
    } finally {
      setSearching(false)
    }
  }, [])

  useEffect(() => {
    const t = setTimeout(() => doSearch(query), 300)
    return () => clearTimeout(t)
  }, [query, doSearch])

  const handleAdd = async (stock) => {
    await addStock(stock.ticker, stock.name, stock.sector || '')
    onClose()
  }

  return (
    <div className="fixed inset-0 z-60 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/70" onClick={onClose} />
      <div className="relative bg-gray-800 rounded-xl border border-gray-600 w-full max-w-md mx-4 shadow-2xl">
        <div className="p-4 border-b border-gray-700 flex items-center gap-3">
          <Search size={16} className="text-gray-400" />
          <input
            autoFocus
            type="text"
            placeholder="Ticker veya şirket adı ara..."
            value={query}
            onChange={e => setQuery(e.target.value)}
            className="flex-1 bg-transparent text-white placeholder-gray-500 outline-none text-sm"
          />
          <button onClick={onClose} className="text-gray-400 hover:text-white">
            <X size={16} />
          </button>
        </div>
        <div className="max-h-80 overflow-y-auto">
          {searching && (
            <div className="p-4 text-center text-gray-500 text-sm">Aranıyor...</div>
          )}
          {!searching && results.length === 0 && query && (
            <div className="p-4 text-center text-gray-500 text-sm">Sonuç bulunamadı</div>
          )}
          {results.map((stock, i) => (
            <div key={i} className="flex items-center justify-between p-3 hover:bg-gray-700 transition-colors">
              <div>
                <div className="text-white font-semibold text-sm">{stock.ticker}</div>
                <div className="text-gray-400 text-xs">{stock.name}</div>
                {stock.exchange && <div className="text-gray-600 text-xs">{stock.exchange}</div>}
              </div>
              <button
                onClick={() => handleAdd(stock)}
                className="flex items-center gap-1 bg-blue-600 hover:bg-blue-500 text-white px-3 py-1 rounded-lg text-xs transition-colors"
              >
                <Plus size={12} />
                Ekle
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
