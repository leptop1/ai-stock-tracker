import { useEffect, useState, useMemo } from 'react'
import { useBistStore } from '../../store/bistStore'
import BistCard from './BistCard'
import { RefreshCw, Filter, ChevronDown, ChevronUp } from 'lucide-react'

const PAGE_SIZE = 30

const CAT_COLORS = {
  'Bankacılık': 'text-blue-400',      'Holding': 'text-gray-400',
  'Savunma': 'text-red-400',           'Telekomünikasyon': 'text-purple-400',
  'Ulaşım': 'text-cyan-400',          'Perakende': 'text-yellow-400',
  'Enerji': 'text-orange-400',        'Metal': 'text-zinc-400',
  'İnşaat': 'text-amber-400',         'Cam': 'text-teal-400',
  'Dayanıklı Tüketim': 'text-pink-400','Tekstil': 'text-violet-400',
  'Teknoloji': 'text-green-400',      'Otomotiv': 'text-red-400',
  'Kimya': 'text-lime-400',           'GYO': 'text-emerald-400',
  'Gıda': 'text-rose-400',            'Finans': 'text-sky-400',
  'Sigorta': 'text-fuchsia-400',      'Sağlık': 'text-indigo-400',
  'Turizm': 'text-yellow-400',        'Madencilik': 'text-stone-400',
  'Medya': 'text-neutral-400',        'Otomotiv Yan': 'text-orange-400',
  'Ambalaj': 'text-emerald-400',      'Girişim': 'text-cyan-400',
  'Spor': 'text-yellow-400',          'Kağıt': 'text-stone-400',
  'Emtia': 'text-amber-400',          'Kiralama': 'text-slate-400',
  'Kırtasiye': 'text-gray-400',       'Diğer': 'text-gray-500',
}

const CAT_ORDER = [
  'Bankacılık', 'Holding', 'Enerji', 'Perakende', 'Ulaşım',
  'Telekomünikasyon', 'Teknoloji', 'Otomotiv', 'Metal', 'İnşaat',
  'Savunma', 'Cam', 'Dayanıklı Tüketim', 'Tekstil', 'Kimya',
  'GYO', 'Gıda', 'Finans', 'Sigorta', 'Sağlık', 'Turizm',
  'Madencilik', 'Medya', 'Otomotiv Yan', 'Ambalaj', 'Girişim',
  'Spor', 'Kağıt', 'Emtia', 'Kiralama', 'Kırtasiye', 'Diğer',
]

function isGreen(instrument) {
  return instrument.price != null && instrument.sma_20 != null && instrument.price > instrument.sma_20
    && instrument.volume != null && instrument.avg_volume_10 != null && instrument.volume > instrument.avg_volume_10
    && instrument.rsi != null && instrument.rsi <= 50
}

const FILTERS = [
  { key: 'all', label: 'Tümü', color: '' },
  { key: 'green', label: 'Yeşil', color: 'border-green-600 bg-green-900/30' },
  { key: 'red', label: 'Kırmızı', color: 'border-red-600 bg-red-900/30' },
]

export default function BistDashboard() {
  const { summaries, loading, lastRefresh, error, fetchSummaries, selectSymbol, selectedSymbol, removeInstrument } = useBistStore()
  const [filter, setFilter] = useState('all')
  const [visible, setVisible] = useState(PAGE_SIZE)

  useEffect(() => {
    fetchSummaries()
    const interval = setInterval(fetchSummaries, 14400000)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    if (!Array.isArray(summaries) || summaries.length === 0) return
    if (!("Notification" in window)) return
    try {
      if (Notification.permission === "default") Notification.requestPermission()
      if (Notification.permission !== "granted") return
      const prev = JSON.parse(sessionStorage.getItem("bist_snap") || "[]")
      const prevGreen = new Set(prev.filter(isGreen).map(s => s.symbol))
      for (const s of summaries) {
        if (s && isGreen(s) && !prevGreen.has(s.symbol)) {
          new Notification("🟢 Yeni Yeşil Sinyal", {
            body: `${s.name} (${s.symbol}) — 🟢 kriterleri karşılıyor!`,
            silent: true,
          })
        }
      }
      sessionStorage.setItem("bist_snap", JSON.stringify(summaries))
    } catch {}
  }, [summaries])

  const grouped = useMemo(() => {
    if (!Array.isArray(summaries)) return {}
    const g = {}
    for (const s of summaries) {
      if (!s) continue
      if (filter === 'green' && !isGreen(s)) continue
      if (filter === 'red' && isGreen(s)) continue
      const cat = s.category || 'Diğer'
      if (!g[cat]) g[cat] = []
      g[cat].push(s)
    }
    return g
  }, [summaries, filter])

  const greenCount = Array.isArray(summaries) ? summaries.filter(isGreen).length : 0
  const redCount = Array.isArray(summaries) ? summaries.length - greenCount : 0

  return (
    <div className="flex-1 p-6">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-white text-xl font-bold">BIST — Borsa İstanbul</h2>
          <p className="text-gray-500 text-xs mt-1">Türkiye · BIST100 + Seçili Hisseler</p>
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

      <div className="flex items-center gap-2 mb-6">
        <Filter size={14} className="text-gray-500" />
        {FILTERS.map(f => (
          <button
            key={f.key}
            onClick={() => setFilter(f.key)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors ${
              filter === f.key
                ? f.color || 'bg-gray-700 border-gray-500 text-white'
                : 'border-gray-700 text-gray-400 hover:border-gray-500'
            }`}
          >
            {f.label}
            {f.key === 'green' && <span className="ml-1.5 text-green-400">({greenCount})</span>}
            {f.key === 'red' && <span className="ml-1.5 text-red-400">({redCount})</span>}
            {f.key === 'all' && <span className="ml-1.5 text-gray-400">({summaries.length})</span>}
          </button>
        ))}
      </div>

      {loading.summary && summaries.length === 0 ? (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {Array.from({ length: 12 }).map((_, i) => (
            <div key={i} className="bg-gray-800 rounded-xl border border-gray-700 p-4 animate-pulse h-40" />
          ))}
        </div>
      ) : !loading.summary && summaries.length === 0 && lastRefresh ? (
        <div className="text-center py-12">
          <p className="text-gray-400 text-lg">Veri yüklenemedi</p>
          {error && <p className="text-gray-600 text-sm mt-1">{error}</p>}
          <button onClick={fetchSummaries} className="mt-4 bg-gray-700 hover:bg-gray-600 text-gray-200 px-4 py-2 rounded-lg text-sm transition-colors">
            Tekrar Dene
          </button>
        </div>
      ) : (
        <div className="space-y-8">
          {CAT_ORDER.map(cat => {
            const items = grouped[cat] || []
            if (items.length === 0) return null
            return (
              <div key={cat}>
                <h3 className={`text-sm font-semibold uppercase tracking-wider mb-3 ${CAT_COLORS[cat] || 'text-gray-400'}`}>
                  {cat}
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
                  {items.slice(0, visible).map(instrument => (
                    <BistCard
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
          {summaries.length > visible && (
            <div className="flex justify-center pb-8">
              <button
                onClick={() => setVisible(v => v + PAGE_SIZE)}
                className="flex items-center gap-2 bg-gray-700 hover:bg-gray-600 text-gray-200 px-6 py-2 rounded-lg text-sm transition-colors"
              >
                <ChevronDown size={16} />
                Daha Fazla Göster ({summaries.length - visible} kalan)
              </button>
            </div>
          )}
          {visible >= summaries.length && summaries.length > PAGE_SIZE && (
            <div className="flex justify-center pb-4">
              <button
                onClick={() => setVisible(PAGE_SIZE)}
                className="flex items-center gap-2 bg-gray-700 hover:bg-gray-600 text-gray-200 px-4 py-1.5 rounded-lg text-xs transition-colors"
              >
                <ChevronUp size={14} />
                Daralt
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
