import { useState } from 'react'
import { useStockStore } from '../../store/stockStore'
import { X } from 'lucide-react'
import SignalBadge from '../signals/SignalBadge'
import SignalSummary from '../signals/SignalSummary'
import IndicatorCard from '../signals/IndicatorCard'
import BollingerSqueezeAlert from '../signals/BollingerSqueezeAlert'
import PriceChart from '../charts/PriceChart'
import RSIChart from '../charts/RSIChart'
import MACDChart from '../charts/MACDChart'
import VolumeChart from '../charts/VolumeChart'
import NewsFeed from '../news/NewsFeed'
import { formatPrice, formatChange, formatVolume } from '../../utils/formatters'

const TABS = ['Grafikler', 'İndikatörler', 'Haberler']

export default function StockDetail() {
  const { selectedTicker, stockDetail, loading, clearSelected, news, newsSummary } = useStockStore()
  const [tab, setTab] = useState('Grafikler')

  if (!selectedTicker) return null

  const ind = stockDetail?.indicators
  const signal = stockDetail?.signal
  const latest = ind?.latest

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-end">
      <div className="absolute inset-0 bg-black/60" onClick={clearSelected} />
      <div className="relative w-full max-w-2xl h-full bg-gray-900 border-l border-gray-700 overflow-y-auto shadow-2xl">
        <div className="p-5 border-b border-gray-700 flex items-start justify-between">
          <div>
            <div className="flex items-center gap-3">
              <h2 className="text-white text-2xl font-bold">{selectedTicker}</h2>
              {signal && <SignalBadge signal={signal.signal} confidence={signal.confidence} size="lg" />}
            </div>
            <p className="text-gray-400 text-sm mt-0.5">{stockDetail?.name}</p>
            {stockDetail && (
              <div className="flex gap-4 mt-2">
                <span className="text-white font-semibold text-lg">{formatPrice(stockDetail.price)}</span>
                <span className={`font-medium ${(latest?.price_change_pct ?? 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {formatChange(latest?.price_change_pct)}
                </span>
              </div>
            )}
          </div>
          <button onClick={clearSelected} className="text-gray-400 hover:text-white p-1">
            <X size={20} />
          </button>
        </div>

        <div className="flex border-b border-gray-700">
          {TABS.map(t => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={`px-5 py-3 text-sm font-medium transition-colors ${tab === t ? 'text-blue-400 border-b-2 border-blue-400' : 'text-gray-400 hover:text-gray-200'}`}
            >
              {t}
            </button>
          ))}
        </div>

        <div className="p-5">
          {loading.detail && !stockDetail && (
            <div className="space-y-4">
              {Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="bg-gray-800 rounded-lg h-40 animate-pulse" />
              ))}
            </div>
          )}

          {!loading.detail && !stockDetail && (
            <div className="text-center py-12 text-gray-500">
              <p className="text-lg">Veri yüklenemedi</p>
              <p className="text-sm mt-1">API sağlayıcı şu anda kullanılamıyor (rate limit)</p>
            </div>
          )}

          {stockDetail && tab === 'Grafikler' && (
            <div className="space-y-6">
              <div>
                <h3 className="text-gray-400 text-xs uppercase mb-2">Fiyat + Bollinger Bands</h3>
                <PriceChart indicators={ind} />
              </div>
              <div>
                <h3 className="text-gray-400 text-xs uppercase mb-2">RSI (14)</h3>
                <RSIChart indicators={ind} />
              </div>
              <div>
                <h3 className="text-gray-400 text-xs uppercase mb-2">MACD</h3>
                <MACDChart indicators={ind} />
              </div>
              <div>
                <h3 className="text-gray-400 text-xs uppercase mb-2">Hacim</h3>
                <VolumeChart indicators={ind} />
              </div>
            </div>
          )}

          {stockDetail && tab === 'İndikatörler' && (
            <div className="space-y-4">
              <SignalSummary signal={signal} />
              <div className="grid grid-cols-2 gap-3">
                {[
                  ['RSI', latest?.rsi?.toFixed(1)],
                  ['MACD', latest?.macd_line?.toFixed(4)],
                  ['Sinyal', latest?.signal_line?.toFixed(4)],
                  ['Histogram', latest?.histogram?.toFixed(4)],
                  ['BB Üst', formatPrice(latest?.bb_upper)],
                  ['BB Alt', formatPrice(latest?.bb_lower)],
                  ['BB %B', latest?.bb_percent_b?.toFixed(2)],
                  ['BB Bant', latest?.bb_bandwidth?.toFixed(2)],
                  ['Hacim Oranı', latest?.volume_ratio?.toFixed(2) + 'x'],
                  ['Hacim', formatVolume(latest?.volume)],
                  ['52H Yüksek', formatPrice(stockDetail?.['52w_high'])],
                  ['52H Düşük', formatPrice(stockDetail?.['52w_low'])],
                ].map(([label, val]) => (
                  <IndicatorCard key={label} label={label} value={val} />
                ))}
              </div>
              {latest?.bb_squeeze && (
                <BollingerSqueezeAlert bandwidth={latest?.bb_bandwidth} />
              )}
            </div>
          )}

          {tab === 'Haberler' && <NewsFeed news={news} newsSummary={newsSummary} loading={loading.news} />}
        </div>
      </div>
    </div>
  )
}
