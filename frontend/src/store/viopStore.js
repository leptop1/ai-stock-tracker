import { create } from 'zustand'
import * as api from '../api/viopApi'

export const useViopStore = create((set, get) => ({
  watchlist: [],
  summaries: [],
  selectedSymbol: null,
  detail: null,
  hedgeSignals: {},   // { [symbol]: { hedge_signal, confidence, score, reasoning, key_factors } }
  loading: { summary: false, detail: false, hedge: {} },
  error: null,
  lastRefresh: null,

  fetchWatchlist: async () => {
    const watchlist = await api.getViopWatchlist()
    set({ watchlist })
  },

  addInstrument: async (symbol, name, category, currency) => {
    await api.addToViopWatchlist(symbol, name, category, currency)
    await get().fetchWatchlist()
    await get().fetchSummaries()
  },

  removeInstrument: async (symbol) => {
    await api.removeFromViopWatchlist(symbol)
    set(state => ({
      watchlist: state.watchlist.filter(w => w.symbol !== symbol),
      summaries: state.summaries.filter(s => s.symbol !== symbol),
    }))
  },

  resetWatchlist: async () => {
    await api.resetViopWatchlist()
    await get().fetchWatchlist()
    await get().fetchSummaries()
  },

  fetchSummaries: async () => {
    set(state => ({ loading: { ...state.loading, summary: true }, error: null }))
    try {
      const summaries = await api.getViopSummary()
      set({ summaries, lastRefresh: new Date() })
      // Hedge sinyallerini arka planda yükle
      summaries.forEach(s => get().fetchHedgeSignal(s.symbol))
    } catch (e) {
      set({ error: e.message })
    } finally {
      set(state => ({ loading: { ...state.loading, summary: false } }))
    }
  },

  fetchHedgeSignal: async (symbol) => {
    set(state => ({ loading: { ...state.loading, hedge: { ...state.loading.hedge, [symbol]: true } } }))
    try {
      const data = await api.getHedgeSignal(symbol)
      set(state => ({ hedgeSignals: { ...state.hedgeSignals, [symbol]: data } }))
    } catch {
      set(state => ({
        hedgeSignals: {
          ...state.hedgeSignals,
          [symbol]: { hedge_signal: 'NÖTR', confidence: 'DÜŞÜK', score: 0, reasoning: '', key_factors: [] },
        },
      }))
    } finally {
      set(state => ({ loading: { ...state.loading, hedge: { ...state.loading.hedge, [symbol]: false } } }))
    }
  },

  selectSymbol: async (symbol) => {
    set({ selectedSymbol: symbol, detail: null })
    set(state => ({ loading: { ...state.loading, detail: true } }))
    try {
      const detail = await api.getViopDetail(symbol)
      set({ detail })
    } catch (e) {
      set({ error: e.message })
    } finally {
      set(state => ({ loading: { ...state.loading, detail: false } }))
    }
  },

  clearSelected: () => set({ selectedSymbol: null, detail: null }),
}))
