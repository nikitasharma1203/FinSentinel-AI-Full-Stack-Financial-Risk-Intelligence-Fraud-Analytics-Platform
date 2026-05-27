// FinSentinel AI — Mock data for frontend development
// Used when backend is unavailable (VITE_USE_MOCK=true)

export const mockKPIs = {
  total_transactions: 284751,
  total_volume: 4_218_543_920,
  fraud_count: 712,
  fraud_rate: 0.25,
  flagged_count: 1843,
  high_risk_customers: 342,
  risk_exposure: 38_420_000,
  period_days: 30,
}

export const mockTrends = Array.from({ length: 30 }, (_, i) => {
  const date = new Date(); date.setDate(date.getDate() - (29 - i))
  const total = 8000 + Math.random() * 4000
  const fraud  = Math.floor(total * (0.002 + Math.random() * 0.003))
  return {
    date: date.toISOString().split('T')[0],
    total: Math.round(total),
    volume: +(total * (2500 + Math.random() * 2000)).toFixed(2),
    fraud,
    fraud_rate: +(fraud / total * 100).toFixed(3),
  }
})

export const mockAlerts = [
  { prediction_id: 'p1', transaction_id: 't1', customer_id: 'c1', amount: 285000, currency: 'INR',
    timestamp: new Date().toISOString(), location_city: 'Mumbai', merchant_category: 'CRYPTO',
    fraud_probability: 0.94, risk_level: 'CRITICAL', flagged: true, reviewed: false,
    explanation: 'Transaction flagged due to: unusually high amount, high-risk merchant category: CRYPTO, international transaction.' },
  { prediction_id: 'p2', transaction_id: 't2', customer_id: 'c2', amount: 145000, currency: 'INR',
    timestamp: new Date(Date.now()-3600000).toISOString(), location_city: 'Delhi', merchant_category: 'WIRE_TRANSFER',
    fraud_probability: 0.81, risk_level: 'HIGH', flagged: true, reviewed: false,
    explanation: 'Transaction flagged due to: abnormal velocity, unseen merchant category, amount deviation +340%.' },
  { prediction_id: 'p3', transaction_id: 't3', customer_id: 'c3', amount: 67500, currency: 'USD',
    timestamp: new Date(Date.now()-7200000).toISOString(), location_city: 'Bangalore', merchant_category: 'GAMBLING',
    fraud_probability: 0.76, risk_level: 'HIGH', flagged: true, reviewed: true,
    explanation: 'Transaction flagged due to: international transaction, high-risk merchant, late night (02:34).' },
]

export const mockHeatmap = [
  { category: 'CRYPTO',          total: 1842, fraud_count: 312, fraud_rate: 16.9, avg_fraud_probability: 0.72 },
  { category: 'WIRE_TRANSFER',   total: 2341, fraud_count: 284, fraud_rate: 12.1, avg_fraud_probability: 0.64 },
  { category: 'GAMBLING',        total: 987,  fraud_count: 198, fraud_rate: 20.1, avg_fraud_probability: 0.81 },
  { category: 'FOREIGN_EXCHANGE',total: 1543, fraud_count: 167, fraud_rate: 10.8, avg_fraud_probability: 0.59 },
  { category: 'ELECTRONICS',     total: 8234, fraud_count: 124, fraud_rate: 1.5,  avg_fraud_probability: 0.22 },
  { category: 'TRAVEL',          total: 12543,fraud_count: 89,  fraud_rate: 0.7,  avg_fraud_probability: 0.18 },
  { category: 'FOOD_DINING',     total: 45231,fraud_count: 67,  fraud_rate: 0.15, avg_fraud_probability: 0.08 },
  { category: 'RETAIL',          total: 67821,fraud_count: 52,  fraud_rate: 0.08, avg_fraud_probability: 0.06 },
]

export const mockRiskDistribution = [
  { tier: 'LOW',      count: 18432 },
  { tier: 'MEDIUM',   count: 6821 },
  { tier: 'HIGH',     count: 1284 },
  { tier: 'CRITICAL', count: 342 },
]

export const mockCustomers = Array.from({ length: 50 }, (_, i) => ({
  customer_id: `c${i+1}`,
  name: `Customer ${i+1}`,
  email: `user${i+1}@example.com`,
  risk_score: Math.random(),
  risk_tier: ['LOW','MEDIUM','HIGH','CRITICAL'][Math.floor(Math.random()*4)],
  customer_segment: ['RETAIL','SME','HNI','STUDENT'][Math.floor(Math.random()*4)],
  churn_probability: Math.random(),
  total_transactions: Math.floor(Math.random() * 500) + 10,
  total_volume: Math.random() * 5000000,
  avg_transaction_amount: Math.random() * 25000 + 500,
}))

export const mockGlobalFeatureImportance = {
  model: 'XGBoost Fraud Classifier v1.0',
  feature_importance: [
    { feature: 'transaction_velocity_1h',   importance: 0.187, description: 'Transactions in last 1 hour' },
    { feature: 'amount_deviation_from_avg', importance: 0.164, description: 'Amount vs customer average' },
    { feature: 'merchant_risk_score',       importance: 0.141, description: 'Merchant historical fraud rate' },
    { feature: 'geographic_distance_km',    importance: 0.118, description: 'Distance from usual location' },
    { feature: 'hour_of_day',              importance: 0.096, description: 'Transaction hour (night=risk)' },
    { feature: 'device_switch_frequency',   importance: 0.083, description: 'Device switching rate' },
    { feature: 'failed_txn_last_24h',       importance: 0.071, description: 'Failed transactions (24h)' },
    { feature: 'is_international',          importance: 0.058, description: 'International flag' },
    { feature: 'merchant_category_rarity',  importance: 0.047, description: 'Category rarity for customer' },
    { feature: 'time_since_last_transaction',importance: 0.035, description: 'Minutes since last txn' },
  ]
}

export const mockCorrelations = {
  correlations: [
    { feature: 'India VIX',               correlation: 0.61,  direction: 'positive' },
    { feature: 'USD/INR Rate',            correlation: 0.54,  direction: 'positive' },
    { feature: 'Crude Oil Price',         correlation: 0.48,  direction: 'positive' },
    { feature: 'Geopolitical Risk Score', correlation: 0.43,  direction: 'positive' },
    { feature: 'Repo Rate',               correlation: -0.38, direction: 'negative' },
    { feature: 'NIFTY 50',               correlation: -0.31, direction: 'negative' },
    { feature: 'Forex Reserves',          correlation: -0.27, direction: 'negative' },
    { feature: 'FII Flow',               correlation: -0.22, direction: 'negative' },
  ]
}

export const mockSentimentSeries = Array.from({ length: 90 }, (_, i) => {
  const date = new Date(); date.setDate(date.getDate() - (89 - i))
  return {
    date: date.toISOString().split('T')[0],
    sentiment_score: +(Math.sin(i / 10) * 0.4 + Math.random() * 0.3 - 0.15).toFixed(4),
    geopolitical_risk: +(0.3 + Math.random() * 0.4).toFixed(4),
    volatility_score: +(0.1 + Math.random() * 0.5).toFixed(4),
  }
})

export const mockCopilotInsights = {
  insights: [
    { type: 'warning', title: 'Fraud Activity Increased 14%',
      message: 'Fraud activity has increased by 14.2% compared to the previous week, concentrated in CRYPTO and WIRE_TRANSFER categories.',
      action: 'Review flagged transactions in the Transaction Monitor.' },
    { type: 'info', title: 'Merchant Cluster Anomaly Detected',
      message: 'Electronics and Crypto merchant categories show coordinated anomaly patterns across 3 customer clusters.',
      action: 'Investigate network cluster #2 in the Network Intelligence module.' },
    { type: 'warning', title: 'Rising Churn Risk in HNI Segment',
      message: 'High Net Worth Individual customers show 18% elevated churn probability this month.',
      action: 'Engage retention team for top 50 at-risk customers.' },
    { type: 'positive', title: 'Model Accuracy Holding at 94.2%',
      message: 'XGBoost fraud classifier maintaining strong performance. AUC-ROC stable at 0.97 over last 30 days.',
      action: 'No action required. Next retrain scheduled in 14 days.' },
  ]
}
