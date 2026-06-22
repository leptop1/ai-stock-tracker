import axios from 'axios'

const api = axios.create({ baseURL: '/api/viop' })

export const getViopWatchlist = () => api.get('/watchlist').then(r => r.data)
export const addToViopWatchlist = (symbol, name, category, currency) =>
  api.post('/watchlist', { symbol, name, category, currency }).then(r => r.data)
export const removeFromViopWatchlist = (symbol) =>
  api.delete(`/watchlist/${symbol}`).then(r => r.data)
export const resetViopWatchlist = () => api.put('/watchlist/reset').then(r => r.data)

export const getViopSummary = () => api.get('/summary').then(r => r.data)
export const getViopDetail = (symbol) => api.get(`/${symbol}`).then(r => r.data)
export const getViopHistory = (symbol) => api.get(`/${symbol}/history`).then(r => r.data)
export const getViopSignal = (symbol) => api.get(`/${symbol}/signal`).then(r => r.data)
export const getHedgeSignal = (symbol) => api.get(`/hedge-signal?symbol=${encodeURIComponent(symbol)}`).then(r => r.data)
