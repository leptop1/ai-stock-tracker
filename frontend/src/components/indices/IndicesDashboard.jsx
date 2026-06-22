import { useEffect, useState } from 'react'
import { RefreshCw, Filter, TrendingUp, TrendingDown } from 'lucide-react'
import { formatVolume } from '../../utils/formatters'
import axios from 'axios'

const EXCHANGE_ORDER = ['Türkiye', 'ABD', 'Almanya', 'İngiltere', 'Japonya', 'Hong Kong', 'Emtia', 'Kripto', 'Döviz']

const EXCHANGE_LABELS = {
  'Türkiye': '🇹🇷 Türkiye', 'ABD': '🇺🇸 ABD', 'Almanya': '🇩🇪 Almanya',
  'İngiltere': '🇬🇧 İngiltere', 'Japonya': '🇯🇵 Japonya', 'Hong Kong': '🇭🇰 Hong Kong',
  'Emtia': '🥇 Emtia', 'Kripto': '₿ Kripto', 'Döviz': '💱 Döviz',
}

function isGreen(idx) {
  const priceOk = idx.price != null && idx.sma_20 != null && idx.price > idx.sma_20
  const volOk = !idx.volume || !idx.avg_volume_10 || idx.volume > idx.avg_volume_10
  const rsiOk = idx.rsi != null && idx.rsi <= 50
  return priceOk && volOk && rsiOk
}

const FILTERS = [
  { key: 'all', label: 'Tümü' },
  { key: 'green', label: 'Yeşil' },
  { key: 'red', label: 'Kırmızı' },
]

function Sparkline({ data, color }) {
  if (!data || data.length < 2) return null
  const min = Math.min(...data)
  const max = Math.max(...data)
  const range = max - min || 1
  const w = 80
  const h = 24
  const points = data.map((v, i) => `${(i / (data.length - 1)) * w},${h - ((v - min) / range) * h}`).join(' ')
  return (
    <svg width={w} height={h} className="ml-auto shrink-0">
      <polyline points={points} fill="none" stroke={color} strokeWidth="1.5" />
    </svg>
  )
}

export default function IndicesDashboard() {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [lastRefresh, setLastRefresh] = useState(null)
  const [filter, setFilter] = useState('all')

  const fetchData = async () => {
    setLoading(true)
    try {
      const res = await axios.get('/api/indices')
      setData(res.data)
      setLastRefresh(new Date())
    } catch (e) {
      console.error('Indices fetch error:', e)
    }
    setLoading(false)
  }

  useEffect(() => {
    fetchData()
    const interval = setInterval(fetchData, 3600000)
    return () => clearInterval(interval)
  }, [])

  const filtered = filter === 'all' ? data
    : filter === 'green' ? data.filter(isGreen)
    : data.filter(idx => !isGreen(idx))

  const grouped = {}
  for (const idx of filtered) {
    const ex = idx.exchange || 'Diğer'
    if (!grouped[ex]) grouped[ex] = []
    grouped[ex].push(idx)
  }

  const greenCount = data.filter(isGreen).length
  const redCount = data.length - greenCount

  return (
    <div className="flex-1 p-6 overflow-y-auto">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-white text-xl font-bold">Endeksler & Piyasalar</h2>
          {lastRefresh && (
            <p className="text-gray-600 text-xs mt-1">Son güncelleme: {lastRefresh.toLocaleTimeString('tr-TR')}</p>
          )}
        </div>
        <button
          onClick={fetchData}
          disabled={loading}
          className="flex items-center gap-2 bg-gray-700 hover:bg-gray-600 text-gray-200 px-3 py-2 rounded-lg text-sm transition-colors disabled:opacity-50"
        >
          <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
          Yenile
        </button>
      </div>

      <div className="flex items-center gap-2 mb-6">
        <Filter size={14} className="text-gray-500" />
        {FILTERS.map(f => (
          <button
            key={f.key}
            onClick={() => setFilter(f.key)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors ${
              filter === f.key
                ? 'bg-gray-700 border-gray-500 text-white'
                : 'border-gray-700 text-gray-400 hover:border-gray-500'
            }`}
          >
            {f.label}
            {f.key === 'all' && <span className="ml-1.5 text-gray-400">({data.length})</span>}
            {f.key === 'green' && <span className="ml-1.5 text-green-400">({greenCount})</span>}
            {f.key === 'red' && <span className="ml-1.5 text-red-400">({redCount})</span>}
          </button>
        ))}
      </div>

      {loading && data.length === 0 ? (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="bg-gray-800 rounded-xl border border-gray-700 p-4 animate-pulse h-28" />
          ))}
        </div>
      ) : (
        <div className="space-y-8">
          {EXCHANGE_ORDER.map(ex => {
            const items = grouped[ex] || []
            if (items.length === 0) return null
            return (
              <div key={ex}>
                <h3 className="text-sm font-semibold uppercase tracking-wider mb-3 text-gray-400">
                  {EXCHANGE_LABELS[ex] || ex}
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
                  {items.map(idx => {
                    const allMet = isGreen(idx)
                    const borderColor = allMet ? 'border-green-500' : 'border-red-500'
                    const isUp = (idx.change_pct ?? 0) >= 0
                    return (
                      <div
                        key={idx.symbol}
                        className={`bg-gray-800 rounded-xl border ${borderColor} p-4 hover:border-gray-500 transition-colors`}
                      >
                        <div className="flex items-start justify-between mb-2">
                          <div className="text-white font-semibold text-sm truncate">{idx.name}</div>
                          {isUp ? (
                            <TrendingUp size={16} className="text-green-400 shrink-0" />
                          ) : (
                            <TrendingDown size={16} className="text-red-400 shrink-0" />
                          )}
                        </div>
                        <div className="flex items-end justify-between">
                          <div>
                            <div className="text-white font-bold text-lg">
                              {idx.price?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })}
                            </div>
                            <div className={`text-sm font-medium ${isUp ? 'text-green-400' : 'text-red-400'}`}>
                              {isUp ? '+' : ''}{idx.change_pct}%
                            </div>
                          </div>
                          <Sparkline data={idx.sparkline} color={isUp ? '#4ade80' : '#f87171'} />
                        </div>
                        <div className="mt-2 pt-2 border-t border-gray-700 flex justify-between text-xs text-gray-500">
                          <span>RSI {idx.rsi != null ? idx.rsi.toFixed(1) : 'N/A'}</span>
                          <span>{idx.volume != null ? `Vol ${formatVolume(idx.volume)}` : `SMA20 ${idx.sma_20 != null ? idx.sma_20.toFixed(0) : 'N/A'}`}</span>
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
