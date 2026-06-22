import { useEffect } from 'react'
import { useViopStore } from '../../store/viopStore'
import ViopCard from './ViopCard'
import { RefreshCw } from 'lucide-react'

const CATEGORIES = ['Endeks', 'Döviz', 'Emtia', 'Hisse']

export default function ViopDashboard() {
  const { summaries, loading, lastRefresh, fetchSummaries, selectSymbol, selectedSymbol, removeInstrument } = useViopStore()

  useEffect(() => {
    fetchSummaries()
    const interval = setInterval(fetchSummaries, 60000)
    return () => clearInterval(interval)
  }, [])

  const grouped = CATEGORIES.reduce((acc, cat) => {
    acc[cat] = summaries.filter(s => s.category === cat)
    return acc
  }, {})

  return (
    <div className="flex-1 p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-white text-xl font-bold">VIOP — Vadeli İşlem ve Opsiyon Piyasası</h2>
          <p className="text-gray-500 text-xs mt-1">Borsa İstanbul · Türkiye Türev Araçları</p>
          {lastRefresh && (
            <p className="text-gray-600 text-xs">Son güncelleme: {lastRefresh.toLocaleTimeString('tr-TR')}</p>
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
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="bg-gray-800 rounded-xl border border-gray-700 p-4 animate-pulse h-40" />
          ))}
        </div>
      ) : (
        <div className="space-y-8">
          {CATEGORIES.map(cat => {
            const items = grouped[cat] || []
            if (items.length === 0) return null
            const catColor = { Endeks: 'text-blue-400', Döviz: 'text-yellow-400', Emtia: 'text-orange-400', Hisse: 'text-purple-400' }
            return (
              <div key={cat}>
                <h3 className={`text-sm font-semibold uppercase tracking-wider mb-3 ${catColor[cat] || 'text-gray-400'}`}>
                  {cat}
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
                  {items.map(instrument => (
                    <ViopCard
                      key={instrument.symbol}
                      instrument={instrument}
                      selected={instrument.symbol === selectedSymbol}
                      onClick={() => selectSymbol(instrument.symbol)}
                      onRemove={removeInstrument}
                    />
                  ))}
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
