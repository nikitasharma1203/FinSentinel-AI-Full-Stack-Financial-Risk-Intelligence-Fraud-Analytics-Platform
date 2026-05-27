import React, { useState, useEffect } from 'react'
import {
  Activity, Shield, Users, AlertTriangle,
  TrendingUp, DollarSign, BarChart2, Zap,
} from 'lucide-react'
import {
  AreaChart, Area, BarChart, Bar, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from 'recharts'
import { motion } from 'framer-motion'
import KPICard from '../components/dashboard/KPICard'
import { SectionHeader, LoadingSpinner, RiskBadge } from '../components/dashboard/UIElements'
import { mockKPIs, mockTrends, mockAlerts, mockCopilotInsights } from '../services/mockData'

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div className="chart-tooltip p-3 text-xs">
      <p className="font-mono text-sentinel-muted mb-1">{label}</p>
      {payload.map(p => (
        <p key={p.name} style={{ color: p.color }} className="font-medium">
          {p.name}: {p.value?.toLocaleString()}
        </p>
      ))}
    </div>
  )
}

const insightColors = { warning: 'border-yellow-500/30 bg-yellow-500/5', info: 'border-cyan-500/30 bg-cyan-500/5', positive: 'border-emerald-500/30 bg-emerald-500/5' }
const insightText   = { warning: 'text-yellow-400', info: 'text-cyan-400', positive: 'text-emerald-400' }

export default function ExecutiveOverview() {
  const [kpis, setKpis]       = useState(null)
  const [trends, setTrends]   = useState([])
  const [insights, setInsights] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setTimeout(() => {
      setKpis(mockKPIs)
      setTrends(mockTrends)
      setInsights(mockCopilotInsights.insights)
      setLoading(false)
    }, 600)
  }, [])

  if (loading) return <LoadingSpinner size={32} />

  const kpiCards = [
    { title: 'Total Transactions', value: kpis.total_transactions, icon: Activity, format: 'compact', color: 'cyan', trend: 8.2, delay: 0 },
    { title: 'Total Volume', value: kpis.total_volume, icon: DollarSign, format: 'currency', color: 'green', trend: 5.1, delay: 0.05 },
    { title: 'Fraud Detected', value: kpis.fraud_count, icon: Shield, format: 'number', color: 'red', trend: 14.2, delay: 0.1 },
    { title: 'Fraud Rate', value: kpis.fraud_rate, icon: AlertTriangle, format: 'percent', color: 'orange', trend: 12.7, delay: 0.15 },
    { title: 'Flagged Alerts', value: kpis.flagged_count, icon: Zap, format: 'number', color: 'yellow', trend: 6.3, delay: 0.2 },
    { title: 'High-Risk Customers', value: kpis.high_risk_customers, icon: Users, format: 'number', color: 'purple', trend: 3.8, delay: 0.25 },
    { title: 'Risk Exposure', value: kpis.risk_exposure, icon: TrendingUp, format: 'currency', color: 'red', trend: 18.4, delay: 0.3 },
    { title: 'Model Accuracy', value: 94.2, icon: BarChart2, format: 'percent', color: 'cyan', trend: -0.3, delay: 0.35 },
  ]

  return (
    <div className="space-y-6 animate-fade-in">
      {/* KPI Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {kpiCards.map((card, i) => (
          <KPICard key={i} {...card} />
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Trend Chart */}
        <div className="lg:col-span-2 sentinel-card">
          <SectionHeader title="Transaction & Fraud Trends" subtitle="Last 30 days — daily volume and fraud activity" />
          <ResponsiveContainer width="100%" height={240}>
            <AreaChart data={trends} margin={{ top: 5, right: 5, bottom: 5, left: 0 }}>
              <defs>
                <linearGradient id="volGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#00D4FF" stopOpacity={0.15} />
                  <stop offset="95%" stopColor="#00D4FF" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="fraudGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#FF3B5C" stopOpacity={0.2} />
                  <stop offset="95%" stopColor="#FF3B5C" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" />
              <XAxis dataKey="date" tick={{ fill: '#6B7280', fontSize: 10 }} tickFormatter={d => d.slice(5)} />
              <YAxis yAxisId="left"  tick={{ fill: '#6B7280', fontSize: 10 }} />
              <YAxis yAxisId="right" orientation="right" tick={{ fill: '#6B7280', fontSize: 10 }} />
              <Tooltip content={<CustomTooltip />} />
              <Legend wrapperStyle={{ fontSize: 11, color: '#6B7280' }} />
              <Area yAxisId="left"  type="monotone" dataKey="total" name="Transactions" stroke="#00D4FF" strokeWidth={1.5} fill="url(#volGrad)" dot={false} />
              <Area yAxisId="right" type="monotone" dataKey="fraud" name="Fraud" stroke="#FF3B5C" strokeWidth={1.5} fill="url(#fraudGrad)" dot={false} />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Copilot Insights */}
        <div className="sentinel-card">
          <SectionHeader title="AI Analyst Insights" subtitle="Auto-generated by Copilot" />
          <div className="space-y-3 overflow-y-auto max-h-64">
            {insights.map((ins, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: 10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.1 }}
                className={`p-3 rounded-lg border text-xs ${insightColors[ins.type] || insightColors.info}`}
              >
                <p className={`font-semibold mb-1 ${insightText[ins.type]}`}>{ins.title}</p>
                <p className="text-sentinel-muted leading-relaxed">{ins.message}</p>
                <p className="text-cyan-400/70 mt-1.5 italic">→ {ins.action}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Alerts */}
      <div className="sentinel-card">
        <SectionHeader title="Recent Fraud Alerts" subtitle="Latest high-probability detections" />
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b border-sentinel-border">
                {['Transaction ID', 'Amount', 'Category', 'Location', 'Fraud Prob.', 'Risk', 'Status'].map(h => (
                  <th key={h} className="text-left py-2 pr-4 text-sentinel-muted font-medium">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {mockAlerts.map((a, i) => (
                <motion.tr
                  key={a.prediction_id}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: i * 0.08 }}
                  className="border-b border-sentinel-border/40 hover:bg-white/2 transition-colors"
                >
                  <td className="py-2.5 pr-4 font-mono text-cyan-400">{a.transaction_id.slice(0,8)}…</td>
                  <td className="py-2.5 pr-4 font-mono text-white">₹{a.amount.toLocaleString('en-IN')}</td>
                  <td className="py-2.5 pr-4">
                    <span className="bg-sentinel-panel border border-sentinel-border rounded px-1.5 py-0.5 font-mono">
                      {a.merchant_category}
                    </span>
                  </td>
                  <td className="py-2.5 pr-4 text-sentinel-muted">{a.location_city}</td>
                  <td className="py-2.5 pr-4">
                    <div className="flex items-center gap-2">
                      <div className="w-16 h-1 bg-sentinel-border rounded-full overflow-hidden">
                        <div className="h-full bg-red-500 rounded-full" style={{ width: `${a.fraud_probability * 100}%` }} />
                      </div>
                      <span className="font-mono text-red-400">{(a.fraud_probability * 100).toFixed(1)}%</span>
                    </div>
                  </td>
                  <td className="py-2.5 pr-4"><RiskBadge level={a.risk_level} size="xs" /></td>
                  <td className="py-2.5">
                    <span className={`text-[9px] font-mono px-1.5 py-0.5 rounded border ${a.reviewed ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' : 'bg-yellow-500/10 text-yellow-400 border-yellow-500/30'}`}>
                      {a.reviewed ? 'REVIEWED' : 'PENDING'}
                    </span>
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
