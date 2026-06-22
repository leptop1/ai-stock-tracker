import { timeAgo } from '../../utils/formatters'
import { ExternalLink, Sparkles } from 'lucide-react'

export default function NewsFeed({ news, newsSummary, loading }) {
  if (loading) {
    return (
      <div className="space-y-3">
        <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg h-24 animate-pulse" />
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="bg-gray-800 rounded-lg h-12 animate-pulse" />
        ))}
      </div>
    )
  }

  if (!news || news.length === 0) {
    return <div className="text-gray-500 text-sm text-center py-8">Haber bulunamadı</div>
  }

  return (
    <div className="space-y-4">
      {newsSummary && (
        <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <Sparkles size={14} className="text-blue-400" />
            <span className="text-blue-400 text-xs font-semibold uppercase tracking-wide">AI Özeti</span>
          </div>
          <p className="text-gray-200 text-sm leading-relaxed">{newsSummary}</p>
        </div>
      )}

      <div className="space-y-1">
        <div className="text-gray-500 text-xs uppercase mb-2">Son Haberler</div>
        {news.map((item, i) => (
          <a
            key={i}
            href={item.link}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-3 p-2.5 rounded-lg hover:bg-gray-800 transition-colors group"
          >
            <div className="flex-1 min-w-0">
              <div className="text-gray-300 text-sm line-clamp-1 group-hover:text-white">
                {item.title}
              </div>
              <div className="flex items-center gap-2 mt-0.5">
                {item.publisher && <span className="text-gray-500 text-xs">{item.publisher}</span>}
                {item.published_at && (
                  <>
                    <span className="text-gray-600 text-xs">·</span>
                    <span className="text-gray-500 text-xs">{timeAgo(item.published_at)}</span>
                  </>
                )}
              </div>
            </div>
            <ExternalLink size={12} className="text-gray-600 flex-shrink-0 group-hover:text-gray-400" />
          </a>
        ))}
      </div>
    </div>
  )
}
