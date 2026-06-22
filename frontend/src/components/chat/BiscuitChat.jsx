import { useState, useRef, useEffect, useCallback } from 'react'
import { X, Send, Maximize2, Minimize2 } from 'lucide-react'
import { sendChatMessage } from '../../api/chatApi'
import { useStockStore } from '../../store/stockStore'
import { useViopStore } from '../../store/viopStore'
import { useBistStore } from '../../store/bistStore'
import { useChatStore } from '../../store/chatStore'
import BiscuitIcon from './BiscuitIcon'

function buildContext(stocks, viop, bist) {
  const lines = []
  if (stocks.length) {
    lines.push('=== AI Stocks ===')
    stocks.forEach(s => lines.push(`${s.ticker} (${s.name}): $${s.price ?? 'N/A'} | ${s.signal} ${s.confidence ? Math.round(s.confidence * 100) + '%' : ''} | RSI ${s.rsi?.toFixed(1) ?? 'N/A'}`))
  }
  if (viop.length) {
    lines.push('=== VIOP ===')
    viop.forEach(s => lines.push(`${s.symbol} (${s.category}): ${s.price ?? 'N/A'} | ${s.signal ?? '-'} | RSI ${s.rsi?.toFixed(1) ?? 'N/A'}`))
  }
  if (bist.length) {
    lines.push('=== BIST ===')
    bist.forEach(s => lines.push(`${s.symbol} (${s.category}): ₺${s.price ?? 'N/A'} | ${s.signal ?? '-'} | RSI ${s.rsi?.toFixed(1) ?? 'N/A'}`))
  }
  return lines.join('\n')
}

function Message({ msg }) {
  const isUser = msg.role === 'user'
  return (
    <div className={`flex gap-2 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
      {!isUser && (
        <div className="w-7 h-7 rounded-full bg-blue-600 flex items-center justify-center flex-shrink-0 mt-0.5">
          <BiscuitIcon size={14} className="text-white" />
        </div>
      )}
      <div
        className={`max-w-[80%] rounded-2xl px-3 py-2 text-sm leading-relaxed whitespace-pre-wrap ${
          isUser
            ? 'bg-blue-600 text-white rounded-tr-sm'
            : 'bg-gray-700 text-gray-100 rounded-tl-sm'
        }`}
      >
        {msg.content}
      </div>
    </div>
  )
}

const MIN_W = 320
const MIN_H = 360

export default function BiscuitChat() {
  const { open, setOpen } = useChatStore()
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Merhaba! Ben Biscuit 🐇 Market Tracker\'ın yatırım asistanıyım. Hangi hisse hakkında konuşalım?' }
  ])
  const [loading, setLoading] = useState(false)
  const [fullscreen, setFullscreen] = useState(false)
  const [size, setSize] = useState({ w: 360, h: 520 })
  const bottomRef = useRef(null)
  const inputRef = useRef(null)
  const resizeRef = useRef(null) // tracks active resize state

  const { summaries: stocks } = useStockStore()
  const { summaries: viop } = useViopStore()
  const { summaries: bist } = useBistStore()

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  useEffect(() => {
    if (open) setTimeout(() => inputRef.current?.focus(), 100)
  }, [open])

  // --- Resize logic ---
  const onResizeMouseDown = useCallback((e) => {
    e.preventDefault()
    const startX = e.clientX
    const startY = e.clientY
    const startW = size.w
    const startH = size.h

    const onMove = (ev) => {
      const newW = Math.max(MIN_W, startW + (startX - ev.clientX))
      const newH = Math.max(MIN_H, startH + (startY - ev.clientY))
      setSize({ w: newW, h: newH })
    }
    const onUp = () => {
      window.removeEventListener('mousemove', onMove)
      window.removeEventListener('mouseup', onUp)
    }
    window.addEventListener('mousemove', onMove)
    window.addEventListener('mouseup', onUp)
  }, [size])

  const send = async () => {
    const text = input.trim()
    if (!text || loading) return

    const userMsg = { role: 'user', content: text }
    const newMessages = [...messages, userMsg]
    setMessages(newMessages)
    setInput('')
    setLoading(true)

    try {
      const context = buildContext(stocks, viop, bist)
      const apiMessages = newMessages
        .slice(1)
        .map(m => ({ role: m.role, content: m.content }))

      const { reply } = await sendChatMessage(apiMessages, context)
      setMessages(prev => [...prev, { role: 'assistant', content: reply }])
    } catch {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Bir hata oluştu, tekrar dener misin?' }])
    } finally {
      setLoading(false)
    }
  }

  const handleKey = e => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send() }
  }

  if (!open) return null

  const panelStyle = fullscreen
    ? { inset: 0, borderRadius: 0 }
    : { bottom: 16, right: 16, width: size.w, height: size.h, borderRadius: 16 }

  return (
    <div
      className="fixed z-50 bg-gray-900 border border-gray-700 shadow-2xl flex flex-col overflow-hidden"
      style={panelStyle}
    >
      {/* Resize handle — top-left corner, only when not fullscreen */}
      {!fullscreen && (
        <div
          onMouseDown={onResizeMouseDown}
          className="absolute top-0 left-0 w-5 h-5 cursor-nw-resize z-10"
          style={{ background: 'transparent' }}
        >
          {/* visual grip dots */}
          <svg width="14" height="14" viewBox="0 0 14 14" className="absolute top-1 left-1 text-gray-600">
            <circle cx="2" cy="2" r="1.2" fill="currentColor" />
            <circle cx="6" cy="2" r="1.2" fill="currentColor" />
            <circle cx="2" cy="6" r="1.2" fill="currentColor" />
          </svg>
        </div>
      )}

      {/* Header */}
      <div className="bg-gray-800 border-b border-gray-700 px-4 py-3 flex items-center gap-3 flex-shrink-0">
        <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center">
          <BiscuitIcon size={16} className="text-white" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="text-white text-sm font-semibold">Biscuit</div>
          <div className="text-gray-500 text-xs">Yatırım Asistanı</div>
        </div>
        <button
          onClick={() => setFullscreen(f => !f)}
          className="text-gray-400 hover:text-white p-1 rounded transition-colors"
          title={fullscreen ? 'Küçült' : 'Tam Ekran'}
        >
          {fullscreen ? <Minimize2 size={15} /> : <Maximize2 size={15} />}
        </button>
        <button
          onClick={() => setOpen(false)}
          className="text-gray-400 hover:text-white p-1 rounded transition-colors"
          title="Kapat"
        >
          <X size={16} />
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.map((msg, i) => <Message key={i} msg={msg} />)}
        {loading && (
          <div className="flex gap-2">
            <div className="w-7 h-7 rounded-full bg-blue-600 flex items-center justify-center flex-shrink-0">
              <BiscuitIcon size={14} className="text-white" />
            </div>
            <div className="bg-gray-700 rounded-2xl rounded-tl-sm px-3 py-2">
              <div className="flex gap-1 items-center h-5">
                <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="border-t border-gray-700 p-2 flex gap-2 flex-shrink-0">
        <textarea
          ref={inputRef}
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKey}
          placeholder="Bir hisse sor..."
          rows={1}
          className="flex-1 bg-gray-800 border border-gray-600 rounded-xl px-3 py-2 text-sm text-white placeholder-gray-500 outline-none focus:border-blue-500 resize-none"
          style={{ maxHeight: 80 }}
        />
        <button
          onClick={send}
          disabled={!input.trim() || loading}
          className="w-9 h-9 bg-blue-600 hover:bg-blue-500 disabled:bg-gray-700 disabled:text-gray-600 text-white rounded-xl flex items-center justify-center transition-colors flex-shrink-0 self-end"
        >
          <Send size={14} />
        </button>
      </div>
    </div>
  )
}
