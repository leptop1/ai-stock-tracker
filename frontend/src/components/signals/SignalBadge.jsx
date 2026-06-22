export default function SignalBadge({ signal, confidence, size = 'sm' }) {
  const colors = {
    BUY: 'bg-green-500/20 text-green-400 border-green-500/40',
    SELL: 'bg-red-500/20 text-red-400 border-red-500/40',
    HOLD: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/40',
    'N/A': 'bg-gray-500/20 text-gray-400 border-gray-500/40',
  }
  const confidenceDot = {
    HIGH: 'bg-white',
    MEDIUM: 'bg-gray-300',
    LOW: 'bg-gray-500',
  }
  const cls = colors[signal] || colors['N/A']
  const px = size === 'lg' ? 'px-3 py-1 text-sm' : 'px-2 py-0.5 text-xs'

  return (
    <span className={`inline-flex items-center gap-1.5 rounded border font-semibold ${cls} ${px}`}>
      {confidence && (
        <span className={`inline-block w-1.5 h-1.5 rounded-full ${confidenceDot[confidence] || 'bg-gray-500'}`} />
      )}
      {signal}
    </span>
  )
}
