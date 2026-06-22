import axios from 'axios'

const api = axios.create({ baseURL: '/api/bist' })

export const getBistWatchlist = () => api.get('/watchlist').then(r => r.data)
export const addToBistWatchlist = (symbol, name, category) =>
  api.post('/watchlist', { symbol, name, category }).then(r => r.data)
export const removeFromBistWatchlist = (symbol) =>
  api.delete(`/watchlist/${symbol}`).then(r => r.data)
export const resetBistWatchlist = () => api.put('/watchlist/reset').then(r => r.data)

export const getBistSummary = () => api.get('/summary').then(r => r.data)
export const getBistDetail = (symbol) => api.get(`/${symbol}`).then(r => r.data)
export const getBistHistory = (symbol) => api.get(`/${symbol}/history`).then(r => r.data)
export const getBistSignal = (symbol) => api.get(`/${symbol}/signal`).then(r => r.data)
export const getAllBistStocks = (query) =>
  api.get('/all', { params: { q: query } }).then(r => r.data)
