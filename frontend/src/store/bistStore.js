import { create } from 'zustand'
import * as api from '../api/bistApi'

export const useBistStore = create((set, get) => ({
  watchlist: [],
  summaries: [],
  allStocks: [],
  selectedSymbol: null,
  detail: null,
  loading: { summary: false, detail: false, browser: false },
  error: null,
  lastRefresh: null,

  fetchWatchlist: async () => {
    const watchlist = await api.getBistWatchlist()
    set({ watchlist })
  },

  fetchAllStocks: async (query = '') => {
    const { allStocks } = get()
    if (allStocks.length > 0 && !query) return allStocks
    set(state => ({ loading: { ...state.loading, browser: true } }))
    try {
      const data = await api.getAllBistStocks(query)
      set({ allStocks: data })
      return data
    } finally {
      set(state => ({ loading: { ...state.loading, browser: false } }))
    }
  },

  addInstrument: async (symbol, name, category) => {
    await api.addToBistWatchlist(symbol, name, category)
    await get().fetchWatchlist()
    set(state => ({
      summaries: [
        ...state.summaries,
        {
          symbol,
          name,
          category: category || 'Diğer',
          price: null, change_pct: null,
          signal: 'N/A', score: 0, confidence: 'LOW',
          rsi: null, volume: null,
        }
      ]
    }))
  },

  removeInstrument: async (symbol) => {
    await api.removeFromBistWatchlist(symbol)
    set(state => ({
      watchlist: state.watchlist.filter(w => w.symbol !== symbol),
      summaries: state.summaries.filter(s => s.symbol !== symbol),
    }))
  },

  resetWatchlist: async () => {
    await api.resetBistWatchlist()
    await get().fetchWatchlist()
    await get().fetchSummaries()
  },

  fetchSummaries: async () => {
    set(state => ({ loading: { ...state.loading, summary: true }, error: null }))
    try {
      const summaries = await api.getBistSummary()
      set({ summaries, lastRefresh: new Date() })
    } catch (e) {
      set({ error: e.message })
    } finally {
      set(state => ({ loading: { ...state.loading, summary: false } }))
    }
  },

  selectSymbol: async (symbol) => {
    set({ selectedSymbol: symbol, detail: null })
    set(state => ({ loading: { ...state.loading, detail: true } }))
    try {
      const detail = await api.getBistDetail(symbol)
      set({ detail })
    } catch (e) {
      set({ error: e.message })
    } finally {
      set(state => ({ loading: { ...state.loading, detail: false } }))
    }
  },

  clearSelected: () => set({ selectedSymbol: null, detail: null }),
}))
