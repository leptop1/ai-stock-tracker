import { useEffect } from 'react'
import { useStockStore } from '../../store/stockStore'
import StockCard from './StockCard'
import { RefreshCw } from 'lucide-react'

export default function StockDashboard() {
  const { summaries, loading, lastRefresh, fetchSummaries, selectTicker, selectedTicker, removeStock } = useStockStore()

  useEffect(() => {
    fetchSummaries()
    const interval = setInterval(fetchSummaries, 60000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="flex-1 p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-white text-xl font-bold">AI Hisse Takip Paneli</h2>
          {lastRefresh && (
            <p className="text-gray-500 text-xs mt-1">
              Son güncelleme: {lastRefresh.toLocaleTimeString('tr-TR')}
            </p>
          )}
        </div>
        <button
          onClick={fetchSummaries}
          disabled={loading.summary}
          className="flex items-center gap-2 bg-gray-700 hover:bg-gray-600 text-gray-200 px-3 py-2 rounded-lg text-sm transition-colors disabled:opacity-50"
        >
          <RefreshCw size={14} className={loading.summary ? 'animate-spin' : ''} />
          Yenile
        </button>
      </div>

      {loading.summary && summaries.length === 0 ? (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
          {Array.from({ length: 10 }).map((_, i) => (
            <div key={i} className="bg-gray-800 rounded-xl border border-gray-700 p-4 animate-pulse h-40" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
          {summaries.map(stock => (
            <StockCard
              key={stock.ticker}
              stock={stock}
              selected={stock.ticker === selectedTicker}
              onClick={() => selectTicker(stock.ticker)}
              onRemove={removeStock}
            />
          ))}
        </div>
      )}
    </div>
  )
}
