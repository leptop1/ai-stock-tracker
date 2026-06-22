import { useState, useEffect, useMemo } from 'react'
import { useBistStore } from '../../store/bistStore'
import { Plus, RefreshCw, Search, X } from 'lucide-react'
import { useChatStore } from '../../store/chatStore'
import BiscuitIcon from '../chat/BiscuitIcon'

function BistStockBrowser({ onClose }) {
  const [query, setQuery] = useState('')
  const [stocks, setStocks] = useState([])
  const [loading, setLoading] = useState(false)
  const { watchlist, fetchAllStocks, addInstrument } = useBistStore()

  const watchlistSymbols = useMemo(() => new Set(watchlist.map(w => w.symbol)), [watchlist])

  useEffect(() => {
    setLoading(true)
    fetchAllStocks().then(data => {
      setStocks(data || [])
      setLoading(false)
    })
  }, [])

  const filtered = useMemo(() => {
    if (!query.trim()) return stocks
    const q = query.toLowerCase()
    return stocks.filter(s =>
      s.symbol.toLowerCase().includes(q) || s.name.toLowerCase().includes(q)
    )
  }, [query, stocks])

  const grouped = useMemo(() => {
    const g = {}
    for (const s of filtered) {
      const cat = s.category || 'Diğer'
      if (!g[cat]) g[cat] = []
      g[cat].push(s)
    }
    return g
  }, [filtered])

  const handleAdd = async (symbol, name, category) => {
    await addInstrument(symbol, name, category)
    onClose()
  }

  return (
    <div className="fixed inset-0 z-60 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/70" onClick={onClose} />
      <div className="relative bg-gray-800 rounded-xl border border-gray-600 w-full max-w-lg mx-4 shadow-2xl flex flex-col max-h-[80vh]">
        <div className="p-4 border-b border-gray-700 flex items-center gap-3 shrink-0">
          <Search size={16} className="text-gray-400" />
          <input
            autoFocus
            type="text"
            placeholder="Sembol veya şirket adı ile ara..."
            value={query}
            onChange={e => setQuery(e.target.value)}
            className="flex-1 bg-transparent text-white placeholder-gray-500 outline-none text-sm"
          />
          {query && (
            <button onClick={() => setQuery('')} className="text-gray-400 hover:text-white">
              <X size={14} />
            </button>
          )}
          <button onClick={onClose} className="text-gray-400 hover:text-white ml-1">
            <X size={16} />
          </button>
        </div>
        <div className="text-xs text-gray-500 px-4 py-1.5 shrink-0 border-b border-gray-700/50">
          {loading ? 'Yükleniyor...' : `${filtered.length} hisse bulundu`}
        </div>
        <div className="overflow-y-auto flex-1">
          {loading && stocks.length === 0 && (
            <div className="p-8 text-center text-gray-500 text-sm">Yükleniyor...</div>
          )}
          {!loading && filtered.length === 0 && (
            <div className="p-8 text-center text-gray-500 text-sm">Sonuç bulunamadı</div>
          )}
          {Object.entries(grouped).map(([cat, items]) => (
            <div key={cat}>
              <div className="px-4 py-2 bg-gray-800/50 text-xs font-semibold text-gray-400 uppercase tracking-wider sticky top-0">
                {cat} ({items.length})
              </div>
              {items.map(s => {
                const inWatchlist = watchlistSymbols.has(s.symbol)
                return (
                  <div key={s.symbol} className="flex items-center justify-between px-4 py-2 hover:bg-gray-700/50 transition-colors">
                    <div className="min-w-0">
                      <span className="text-white text-sm font-medium">{s.symbol.replace('.IS', '')}</span>
                      <span className="text-gray-400 text-xs ml-2 truncate">{s.name}</span>
                    </div>
                    {inWatchlist ? (
                      <span className="text-green-500 text-xs shrink-0">Eklendi</span>
                    ) : (
                      <button
                        onClick={() => handleAdd(s.symbol, s.name, s.category)}
                        className="flex items-center gap-1 bg-blue-600 hover:bg-blue-500 text-white px-2.5 py-1 rounded text-xs transition-colors shrink-0"
                      >
                        <Plus size={10} />Ekle
                      </button>
                    )}
                  </div>
                )
              })}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default function BistWatchlistPanel() {
  const { fetchSummaries } = useBistStore()
  const [showAdd, setShowAdd] = useState(false)
  const { toggle: toggleChat } = useChatStore()

  return (
    <div className="bg-gray-900 border-r border-gray-700 flex flex-col gap-1 p-2">
      <button
        onClick={() => setShowAdd(true)}
        className="flex items-center justify-center gap-1 bg-blue-600 hover:bg-blue-500 text-white px-3 py-1.5 rounded text-xs transition-colors"
      >
        <Plus size={12} />Ekle
      </button>
      <button
        onClick={fetchSummaries}
        className="flex items-center justify-center bg-gray-700 hover:bg-gray-600 text-gray-400 p-1.5 rounded transition-colors"
        title="Yenile"
      >
        <RefreshCw size={14} />
      </button>
      <div className="flex-1" />
      <button
        onClick={toggleChat}
        className="flex items-center justify-center bg-blue-600/20 hover:bg-blue-600/40 text-blue-400 p-1.5 rounded transition-colors"
        title="Biscuit — Yatırım Asistanı"
      >
        <BiscuitIcon size={16} />
      </button>
      {showAdd && <BistStockBrowser onClose={() => setShowAdd(false)} />}
    </div>
  )
}
