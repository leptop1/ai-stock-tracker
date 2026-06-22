import { useState } from 'react'
import { useViopStore } from '../../store/viopStore'
import { X } from 'lucide-react'
import SignalBadge from '../signals/SignalBadge'
import SignalSummary from '../signals/SignalSummary'
import IndicatorCard from '../signals/IndicatorCard'
import BollingerSqueezeAlert from '../signals/BollingerSqueezeAlert'
import ViopSignalPanel from './ViopSignalPanel'
import PriceChart from '../charts/PriceChart'
import RSIChart from '../charts/RSIChart'
import MACDChart from '../charts/MACDChart'
import VolumeChart from '../charts/VolumeChart'
import { formatChange, formatVolume } from '../../utils/formatters'

const TABS = ['Grafikler', 'İndikatörler']

function formatPrice(price, currency) {
  if (price == null) return 'N/A'
  const opts = { minimumFractionDigits: 2, maximumFractionDigits: currency === 'TRY' ? 2 : 4 }
  const val = new Intl.NumberFormat('tr-TR', opts).format(price)
  return currency === 'TRY' ? `₺${val}` : `$${val}`
}

export default function ViopDetail() {
  const { selectedSymbol, detail, loading, clearSelected } = useViopStore()
  const [tab, setTab] = useState('Grafikler')

  if (!selectedSymbol) return null

  const ind = detail?.indicators
  const signal = detail?.signal
  const latest = ind?.latest
  const currency = detail?.currency || 'TRY'

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-end">
      <div className="absolute inset-0 bg-black/60" onClick={clearSelected} />
      <div className="relative w-full max-w-2xl h-full bg-gray-900 border-l border-gray-700 overflow-y-auto shadow-2xl">
        <div className="p-5 border-b border-gray-700 flex items-start justify-between">
          <div>
            <div className="flex items-center gap-3">
              <h2 className="text-white text-xl font-bold">{detail?.name || selectedSymbol}</h2>
              {signal && <SignalBadge signal={signal.signal} confidence={signal.confidence} size="lg" />}
            </div>
            <p className="text-gray-500 text-xs mt-0.5 font-mono">{selectedSymbol}</p>
            {detail && (
              <div className="flex gap-4 mt-2">
                <span className="text-white font-semibold text-lg">{formatPrice(detail.price, currency)}</span>
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
          {loading.detail && !detail && (
            <div className="space-y-4">
              {Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="bg-gray-800 rounded-lg h-40 animate-pulse" />
              ))}
            </div>
          )}

          {detail && tab === 'Grafikler' && (
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

          {detail && tab === 'İndikatörler' && (
            <div className="space-y-4">
              <ViopSignalPanel signal={signal} />
              <SignalSummary signal={signal} />
              <div className="grid grid-cols-2 gap-3">
                {[
                  ['RSI', latest?.rsi?.toFixed(1)],
                  ['MACD', latest?.macd_line?.toFixed(4)],
                  ['Sinyal Çizgisi', latest?.signal_line?.toFixed(4)],
                  ['Histogram', latest?.histogram?.toFixed(4)],
                  ['BB Üst', formatPrice(latest?.bb_upper, currency)],
                  ['BB Alt', formatPrice(latest?.bb_lower, currency)],
                  ['BB %B', latest?.bb_percent_b?.toFixed(2)],
                  ['Hacim Oranı', latest?.volume_ratio != null ? latest.volume_ratio.toFixed(2) + 'x' : 'N/A'],
                  ['Hacim', formatVolume(latest?.volume)],
                  ['52H Yüksek', formatPrice(detail?.['52w_high'], currency)],
                  ['52H Düşük', formatPrice(detail?.['52w_low'], currency)],
                  ['Para Birimi', currency],
                ].map(([label, val]) => (
                  <IndicatorCard key={label} label={label} value={val} />
                ))}
              </div>
              {latest?.bb_squeeze && (
                <BollingerSqueezeAlert bandwidth={latest?.bb_bandwidth} />
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
