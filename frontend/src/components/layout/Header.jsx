import { TrendingUp, BarChart2, BarChart3, Globe } from 'lucide-react'

export default function Header({ activeTab, onTabChange }) {
  const subtitle = activeTab === 'stocks'
    ? 'ABD Borsası · AI Sektörü'
    : activeTab === 'viop'
    ? 'Borsa İstanbul · Türkiye Türev Araçları'
    : activeTab === 'indices'
    ? 'Küresel Endeksler & Piyasalar'
    : 'Borsa İstanbul · BIST30 + Seçili Hisseler'

  return (
    <header className="bg-gray-900 border-b border-gray-700 px-6 py-3 flex items-center gap-4 flex-shrink-0">
      <TrendingUp size={20} className="text-blue-400" />
      <span className="text-white font-bold text-lg">Market Tracker</span>

      <div className="flex items-center gap-1 ml-4 bg-gray-800 rounded-lg p-1">
        <button
          onClick={() => onTabChange('stocks')}
          className={`flex items-center gap-2 px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${activeTab === 'stocks' ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-gray-200'}`}
        >
          <TrendingUp size={14} />
          AI Stocks
        </button>
        <button
          onClick={() => onTabChange('viop')}
          className={`flex items-center gap-2 px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${activeTab === 'viop' ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-gray-200'}`}
        >
          <BarChart2 size={14} />
          VIOP
        </button>
        <button
          onClick={() => onTabChange('bist')}
          className={`flex items-center gap-2 px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${activeTab === 'bist' ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-gray-200'}`}
        >
          <BarChart3 size={14} />
          BIST
        </button>
        <button
          onClick={() => onTabChange('indices')}
          className={`flex items-center gap-2 px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${activeTab === 'indices' ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-gray-200'}`}
        >
          <Globe size={14} />
          Endeksler
        </button>
      </div>

      <span className="text-gray-600 text-xs ml-auto">{subtitle}</span>
    </header>
  )
}
