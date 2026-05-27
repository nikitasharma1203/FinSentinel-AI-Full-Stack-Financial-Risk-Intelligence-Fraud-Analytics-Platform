import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: `${BASE_URL}/api/v1`,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

// ── Transactions ──────────────────────────────────────────────────────────────
export const transactionApi = {
  getAll:   (params) => api.get('/transactions/', { params }),
  getKPIs:  (days = 30) => api.get('/transactions/kpis', { params: { days } }),
  getTrends:(days = 30) => api.get('/transactions/trends', { params: { days } }),
  getOne:   (id) => api.get(`/transactions/${id}`),
}

// ── Fraud ─────────────────────────────────────────────────────────────────────
export const fraudApi = {
  score:          (transaction_id) => api.post('/fraud/score', { transaction_id }),
  getAlerts:      (params) => api.get('/fraud/alerts', { params }),
  getHeatmap:     (days = 30) => api.get('/fraud/heatmap', { params: { days } }),
  getByPayment:   (days = 30) => api.get('/fraud/by-payment-method', { params: { days } }),
  review:         (id, outcome, reviewer_id) =>
    api.post(`/fraud/review/${id}`, null, { params: { outcome, reviewer_id } }),
}

// ── Customers ─────────────────────────────────────────────────────────────────
export const customerApi = {
  getAll:             (params) => api.get('/customers/', { params }),
  getRiskDistribution:() => api.get('/customers/risk-distribution'),
  getOne:             (id) => api.get(`/customers/${id}`),
}

// ── Network ───────────────────────────────────────────────────────────────────
export const networkApi = {
  getGraph:       (params) => api.get('/network/graph', { params }),
  getCentrality:  (limit = 20) => api.get('/network/centrality', { params: { limit } }),
  getClusters:    () => api.get('/network/clusters'),
  getPropagation: (node_id, depth = 2) =>
    api.get(`/network/propagation/${node_id}`, { params: { depth } }),
}

// ── Scenarios ─────────────────────────────────────────────────────────────────
export const scenarioApi = {
  run:        (params) => api.post('/scenarios/run', params),
  getHistory: (user_id) => api.get('/scenarios/history', { params: { user_id } }),
}

// ── Explainability ────────────────────────────────────────────────────────────
export const explainabilityApi = {
  getExplanation:      (prediction_id) => api.get(`/explainability/${prediction_id}`),
  getGlobalImportance: () => api.get('/explainability/feature-importance/global'),
}

// ── Analytics ─────────────────────────────────────────────────────────────────
export const analyticsApi = {
  getMacro:       (days = 90) => api.get('/analytics/macro', { params: { days } }),
  getCorrelations:() => api.get('/analytics/correlations'),
  getCopilot:     () => api.get('/analytics/copilot-insights'),
}

// ── Sentiment ─────────────────────────────────────────────────────────────────
export const sentimentApi = {
  getLatest:     (days = 30) => api.get('/sentiment/latest', { params: { days } }),
  getTopics:     () => api.get('/sentiment/topics'),
  getEventShocks:() => api.get('/sentiment/event-shocks'),
}

// ── Reports ───────────────────────────────────────────────────────────────────
export const reportApi = {
  generate: (body) => api.post('/reports/generate', body),
  list:     (user_id) => api.get('/reports/', { params: { user_id } }),
  download: (id) => `${BASE_URL}/api/v1/reports/${id}/download`,
}

export default api
