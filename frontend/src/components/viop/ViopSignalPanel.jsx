import { TrendingUp, TrendingDown, Minus, ShieldAlert, ArrowUpDown } from 'lucide-react'

const VIOP_CONFIG = {
  LONG: {
    label: 'LONG',
    labelTR: 'Alış Pozisyonu',
    desc: 'İndikatörler yükseliş yönünde — vadeli alış pozisyonu açılabilir.',
    bg: 'bg-green-500/10 border-green-500/30',
    text: 'text-green-400',
    bar: 'bg-green-500',
    Icon: TrendingUp,
  },
  SHORT: {
    label: 'SHORT',
    labelTR: 'Satış Pozisyonu',
    desc: 'İndikatörler düşüş yönünde — vadeli satış pozisyonu açılabilir.',
    bg: 'bg-red-500/10 border-red-500/30',
    text: 'text-red-400',
    bar: 'bg-red-500',
    Icon: TrendingDown,
  },
  HEDGE: {
    label: 'HEDGE',
    labelTR: 'Riskten Korunma',
    desc: 'İndikatörler çelişkili sinyal veriyor — net bir yön yok. Mevcut pozisyonları hedge etmek veya beklemek önerilir.',
    bg: 'bg-purple-500/10 border-purple-500/30',
    text: 'text-purple-400',
    bar: 'bg-purple-500',
    Icon: ShieldAlert,
  },
  NEUTRAL: {
    label: 'NÖTR',
    labelTR: 'Bekle',
    desc: 'İndikatörler belirgin bir yön göstermiyor — pozisyon açmak için daha net sinyal beklenebilir.',
    bg: 'bg-gray-700/50 border-gray-600',
    text: 'text-gray-400',
    bar: 'bg-gray-500',
    Icon: ArrowUpDown,
  },
}

const DIRECTION_CONFIG = {
  LONG: { text: 'text-green-400', Icon: TrendingUp, label: 'LONG' },
  SHORT: { text: 'text-red-400', Icon: TrendingDown, label: 'SHORT' },
  NEUTRAL: { text: 'text-gray-500', Icon: Minus, label: 'NÖTR' },
}

export default function ViopSignalPanel({ signal }) {
  if (!signal?.viop_signal) return null

  const viop = signal.viop_signal
  const cfg = VIOP_CONFIG[viop] || VIOP_CONFIG.NEUTRAL
  const { Icon } = cfg
  const hedgeScore = signal.hedge_score ?? 0
  const reasoning = signal.viop_reasoning ?? []

  return (
    <div className={`rounded-xl border ${cfg.bg} p-4 space-y-4`}>
      {/* Başlık */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Icon size={22} className={cfg.text} />
          <div>
            <div className={`text-xl font-bold tracking-wide ${cfg.text}`}>{cfg.label}</div>
            <div className="text-gray-500 text-xs">{cfg.labelTR}</div>
          </div>
        </div>
        <div className="text-right">
          <div className="text-gray-500 text-xs">Bileşik Skor</div>
          <div className="font-mono text-sm text-gray-300">
            {signal.score >= 0 ? '+' : ''}{signal.score?.toFixed(3)}
          </div>
        </div>
      </div>

      {/* Açıklama */}
      <p className="text-gray-400 text-sm leading-relaxed">{cfg.desc}</p>

      {/* Hedge çelişki barı */}
      {viop === 'HEDGE' && (
        <div className="space-y-1">
          <div className="flex justify-between text-xs text-gray-500">
            <span>Çelişki Yoğunluğu</span>
            <span className="text-purple-400 font-semibold">{Math.round(hedgeScore * 100)}%</span>
          </div>
          <div className="h-1.5 bg-gray-700 rounded-full overflow-hidden">
            <div
              className="h-full bg-purple-500 rounded-full transition-all"
              style={{ width: `${hedgeScore * 100}%` }}
            />
          </div>
        </div>
      )}

      {/* İndikatör açıklamaları */}
      <div className="space-y-2 pt-1 border-t border-gray-700/50">
        <div className="text-gray-500 text-xs uppercase tracking-wider">İndikatör Gerekçeleri</div>
        {reasoning.map((r) => {
          const dirCfg = DIRECTION_CONFIG[r.direction] || DIRECTION_CONFIG.NEUTRAL
          const DirIcon = dirCfg.Icon
          return (
            <div key={r.indicator} className="flex gap-3 items-start">
              <div className={`mt-0.5 shrink-0 ${dirCfg.text}`}>
                <DirIcon size={14} />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="text-gray-300 text-sm font-medium">{r.indicator}</span>
                  <span className={`text-xs font-semibold ${dirCfg.text}`}>{dirCfg.label}</span>
                  <span className="text-gray-600 font-mono text-xs">
                    {r.weight * 100}% ağırlık · {r.weighted >= 0 ? '+' : ''}{r.weighted.toFixed(4)}
                  </span>
                </div>
                <p className="text-gray-500 text-xs mt-0.5 leading-relaxed">{r.reason}</p>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
