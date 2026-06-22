import { create } from 'zustand'
import * as api from '../api/stockApi'

export const useStockStore = create((set, get) => ({
  watchlist: [],
  summaries: [],
  selectedTicker: null,
  stockDetail: null,
  news: [],
  newsSummary: null,
  loading: { summary: false, detail: false, news: false },
  error: null,
  lastRefresh: null,

  fetchWatchlist: async () => {
    const watchlist = await api.getWatchlist()
    set({ watchlist })
  },

  addStock: async (ticker, name, category) => {
    await api.addToWatchlist(ticker, name, category)
    await get().fetchWatchlist()
    await get().fetchSummaries()
  },

  removeStock: async (ticker) => {
    await api.removeFromWatchlist(ticker)
    set(state => ({
      watchlist: state.watchlist.filter(w => w.ticker !== ticker),
      summaries: state.summaries.filter(s => s.ticker !== ticker),
    }))
  },

  resetWatchlist: async () => {
    await api.resetWatchlist()
    await get().fetchWatchlist()
    await get().fetchSummaries()
  },

  fetchSummaries: async () => {
    set(state => ({ loading: { ...state.loading, summary: true }, error: null }))
    try {
      const summaries = await api.getStocksSummary()
      set({ summaries, lastRefresh: new Date() })
    } catch (e) {
      set({ error: e.message })
    } finally {
      set(state => ({ loading: { ...state.loading, summary: false } }))
    }
  },

  selectTicker: async (ticker) => {
    set({ selectedTicker: ticker, stockDetail: null })
    set(state => ({ loading: { ...state.loading, detail: true } }))
    try {
      const detail = await api.getStockDetail(ticker)
      set({ stockDetail: detail })
    } catch (e) {
      set({ error: e.message })
    } finally {
      set(state => ({ loading: { ...state.loading, detail: false } }))
    }
    get().fetchTickerNews(ticker)
  },

  clearSelected: () => set({ selectedTicker: null, stockDetail: null }),

  fetchTickerNews: async (ticker) => {
    set(state => ({ loading: { ...state.loading, news: true }, newsSummary: null }))
    try {
      const data = await api.getTickerNewsSummary(ticker)
      set({ news: data.articles || [], newsSummary: data.summary || null })
    } finally {
      set(state => ({ loading: { ...state.loading, news: false } }))
    }
  },

  fetchAllNews: async () => {
    set(state => ({ loading: { ...state.loading, news: true } }))
    try {
      const news = await api.getNews()
      set({ news })
    } finally {
      set(state => ({ loading: { ...state.loading, news: false } }))
    }
  },
}))
