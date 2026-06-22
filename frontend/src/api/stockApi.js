import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

export const getWatchlist = () => api.get('/watchlist/').then(r => r.data)
export const addToWatchlist = (ticker, name, category) =>
  api.post('/watchlist/', { ticker, name, category }).then(r => r.data)
export const removeFromWatchlist = (ticker) =>
  api.delete(`/watchlist/${ticker}`).then(r => r.data)
export const resetWatchlist = () => api.put('/watchlist/reset').then(r => r.data)

export const getStocksSummary = () => api.get('/stocks/summary').then(r => r.data)
export const getStockDetail = (ticker) => api.get(`/stocks/${ticker}`).then(r => r.data)
export const getStockHistory = (ticker) => api.get(`/stocks/${ticker}/history`).then(r => r.data)
export const getStockSignal = (ticker) => api.get(`/stocks/${ticker}/signal`).then(r => r.data)

export const getNews = () => api.get('/news/').then(r => r.data)
export const getTickerNews = (ticker) => api.get(`/news/${ticker}`).then(r => r.data)
export const getTickerNewsSummary = (ticker) => api.get(`/news/${ticker}/summary`).then(r => r.data)

export const discoverStocks = () => api.get('/discover/').then(r => r.data)
export const searchStocks = (q) => api.get(`/discover/search?q=${encodeURIComponent(q)}`).then(r => r.data)
