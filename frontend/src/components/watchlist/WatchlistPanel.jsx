import { useState } from 'react'
import { useStockStore } from '../../store/stockStore'
import AddStockModal from './AddStockModal'
import { Plus, RefreshCw } from 'lucide-react'
import { useChatStore } from '../../store/chatStore'
import BiscuitIcon from '../chat/BiscuitIcon'

export default function WatchlistPanel() {
  const { fetchSummaries } = useStockStore()
  const [showAdd, setShowAdd] = useState(false)
  const { toggle: toggleChat } = useChatStore()

  return (
    <div className="bg-gray-900 border-r border-gray-700 flex flex-col gap-1 p-2">
      <button
        onClick={() => setShowAdd(true)}
        className="flex items-center justify-center gap-1 bg-blue-600 hover:bg-blue-500 text-white px-3 py-1.5 rounded text-xs transition-colors"
      >
        <Plus size={12} />Ekle
      </button>
      <button
        onClick={fetchSummaries}
        className="flex items-center justify-center bg-gray-700 hover:bg-gray-600 text-gray-400 p-1.5 rounded transition-colors"
        title="Yenile"
      >
        <RefreshCw size={14} />
      </button>
      <div className="flex-1" />
      <button
        onClick={toggleChat}
        className="flex items-center justify-center bg-blue-600/20 hover:bg-blue-600/40 text-blue-400 p-1.5 rounded transition-colors"
        title="Biscuit — Yatırım Asistanı"
      >
        <BiscuitIcon size={16} />
      </button>
      {showAdd && <AddStockModal onClose={() => setShowAdd(false)} />}
    </div>
  )
}
