import { useEffect, useState } from 'react'
import Header from './components/layout/Header'
import WatchlistPanel from './components/watchlist/WatchlistPanel'
import StockDashboard from './components/stocks/StockDashboard'
import StockDetail from './components/stocks/StockDetail'
import ViopWatchlistPanel from './components/viop/ViopWatchlistPanel'
import ViopDashboard from './components/viop/ViopDashboard'
import ViopDetail from './components/viop/ViopDetail'
import BistWatchlistPanel from './components/bist/BistWatchlistPanel'
import BistDashboard from './components/bist/BistDashboard'
import BistDetail from './components/bist/BistDetail'
import IndicesDashboard from './components/indices/IndicesDashboard'
import { useStockStore } from './store/stockStore'
import { useViopStore } from './store/viopStore'
import { useBistStore } from './store/bistStore'
import BiscuitChat from './components/chat/BiscuitChat'

export default function App() {
  const [activeTab, setActiveTab] = useState('stocks')
  const { fetchWatchlist: fetchStocks } = useStockStore()
  const { fetchWatchlist: fetchViop } = useViopStore()
  const { fetchWatchlist: fetchBist } = useBistStore()

  useEffect(() => { fetchStocks() }, [])
  useEffect(() => { if (activeTab === 'viop') fetchViop() }, [activeTab])
  useEffect(() => { if (activeTab === 'bist') fetchBist() }, [activeTab])

  return (
    <div className="flex flex-col h-screen bg-gray-950 text-gray-200">
      <Header activeTab={activeTab} onTabChange={setActiveTab} />
      <div className="flex flex-1 overflow-hidden">
        {activeTab === 'stocks' ? (
          <>
            <WatchlistPanel />
            <main className="flex-1 overflow-y-auto">
              <StockDashboard />
            </main>
            <StockDetail />
          </>
        ) : activeTab === 'viop' ? (
          <>
            <ViopWatchlistPanel />
            <main className="flex-1 overflow-y-auto">
              <ViopDashboard />
            </main>
            <ViopDetail />
          </>
        ) : activeTab === 'indices' ? (
          <main className="flex-1 overflow-y-auto">
            <IndicesDashboard />
          </main>
        ) : (
          <>
            <BistWatchlistPanel />
            <main className="flex-1 overflow-y-auto">
              <BistDashboard />
            </main>
            <BistDetail />
          </>
        )}
      </div>
      <BiscuitChat />
    </div>
  )
}
