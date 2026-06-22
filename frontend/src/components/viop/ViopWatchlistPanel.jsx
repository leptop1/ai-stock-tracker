import { useState } from 'react'
import { useViopStore } from '../../store/viopStore'
import { Plus, RefreshCw } from 'lucide-react'
import { useChatStore } from '../../store/chatStore'
import BiscuitIcon from '../chat/BiscuitIcon'

function AddViopModal({ onClose }) {
  const [symbol, setSymbol] = useState('')
  const [name, setName] = useState('')
  const [category, setCategory] = useState('Hisse')
  const [currency, setCurrency] = useState('TRY')
  const { addInstrument } = useViopStore()

  const handleAdd = async () => {
    if (!symbol.trim()) return
    await addInstrument(symbol.trim().toUpperCase(), name || symbol, category, currency)
    onClose()
  }

  return (
    <div className="fixed inset-0 z-60 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/70" onClick={onClose} />
      <div className="relative bg-gray-800 rounded-xl border border-gray-600 w-full max-w-sm mx-4 p-5 shadow-2xl">
        <h3 className="text-white font-semibold mb-4">Enstrüman Ekle</h3>
        <div className="space-y-3">
          <input
            autoFocus
            placeholder="Sembol (örn: YKBNK.IS)"
            value={symbol}
            onChange={e => setSymbol(e.target.value)}
            className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm placeholder-gray-500 outline-none focus:border-blue-500"
          />
          <input
            placeholder="Ad (opsiyonel)"
            value={name}
            onChange={e => setName(e.target.value)}
            className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm placeholder-gray-500 outline-none focus:border-blue-500"
          />
          <div className="flex gap-2">
            <select value={category} onChange={e => setCategory(e.target.value)} className="flex-1 bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm outline-none">
              <option>Hisse</option>
              <option>Endeks</option>
              <option>Döviz</option>
              <option>Emtia</option>
            </select>
            <select value={currency} onChange={e => setCurrency(e.target.value)} className="flex-1 bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm outline-none">
              <option>TRY</option>
              <option>USD</option>
              <option>EUR</option>
            </select>
          </div>
          <div className="flex gap-2 pt-1">
            <button onClick={onClose} className="flex-1 bg-gray-700 hover:bg-gray-600 text-gray-300 py-2 rounded-lg text-sm transition-colors">İptal</button>
            <button onClick={handleAdd} className="flex-1 bg-blue-600 hover:bg-blue-500 text-white py-2 rounded-lg text-sm font-medium transition-colors">Ekle</button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default function ViopWatchlistPanel() {
  const { fetchSummaries } = useViopStore()
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
      {showAdd && <AddViopModal onClose={() => setShowAdd(false)} />}
    </div>
  )
}
