import { useState } from 'react'
import { Info } from 'lucide-react'

const TOOLTIP_TEXT =
  'Bollinger Squeeze, bant genişliği (Bandwidth) son 20 günlük ortalama fiyatın %10\'unun altına düştüğünde tetiklenir. ' +
  'Bollinger Bands bantları bu kadar daralınca volatilite çok düşük demektir — ' +
  'piyasada enerji birikmektedir. Tarihsel olarak bu sıkışmanın ardından güçlü bir fiyat hareketi gelir; ' +
  'ancak hareketin yönü (yukarı mı aşağı mı) bu sinyal tarafından söylenmez. ' +
  'Diğer indikatörlerle (RSI, MACD, hacim) birlikte değerlendirin.'

export default function BollingerSqueezeAlert({ bandwidth }) {
  const [visible, setVisible] = useState(false)

  return (
    <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-3 text-yellow-400 text-sm flex items-start justify-between gap-3">
      <span>
        Bollinger Squeeze tespit edildi — yakında güçlü bir fiyat hareketi bekleniyor
        {bandwidth != null && (
          <span className="text-yellow-500/70 text-xs ml-2">(Bandwidth: {bandwidth.toFixed(2)}%)</span>
        )}
      </span>
      <div className="relative flex-shrink-0">
        <button
          onMouseEnter={() => setVisible(true)}
          onMouseLeave={() => setVisible(false)}
          onFocus={() => setVisible(true)}
          onBlur={() => setVisible(false)}
          className="text-yellow-400/70 hover:text-yellow-300 transition-colors"
          aria-label="Bollinger Squeeze hakkında bilgi"
        >
          <Info size={16} />
        </button>
        {visible && (
          <div className="absolute right-0 bottom-6 w-72 bg-gray-800 border border-gray-600 rounded-lg p-3 text-gray-200 text-xs leading-relaxed shadow-xl z-10">
            <div className="font-semibold text-yellow-400 mb-1">Bollinger Squeeze Nedir?</div>
            {TOOLTIP_TEXT}
            <div className="mt-2 text-gray-500 text-xs">Eşik: Bandwidth &lt; 10%</div>
          </div>
        )}
      </div>
    </div>
  )
}
