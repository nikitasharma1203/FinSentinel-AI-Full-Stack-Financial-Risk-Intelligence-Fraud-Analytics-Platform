import React, { useState, useEffect } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, Radar,
  ScatterChart, Scatter, ZAxis, Cell, PieChart, Pie, Legend,
} from 'recharts'
import { motion } from 'framer-motion'
import { Shield, AlertTriangle, TrendingUp, Filter } from 'lucide-react'
import { SectionHeader, RiskBadge, TabGroup, LoadingSpinner } from '../components/dashboard/UIElements'
import KPICard from '../components/dashboard/KPICard'
import { mockHeatmap, mockTrends, mockAlerts } from '../services/mockData'

const COLORS = ['#FF3B5C','#FF8C00','#FFB020','#00D4FF','#00E5A0','#8B5CF6','#EC4899','#64748B']

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null
  const d = payload[0]?.payload
  return (
    <div className="chart-tooltip p-3 text-xs space-y-1">
      <p className="font-semibold text-white">{d?.category || d?.name}</p>
      {payload.map(p => (
        <p key={p.name} style={{ color: p.color }}>
          {p.name}: {typeof p.value === 'number' ? p.value.toLocaleString() : p.value}
        </p>
      ))}
    </div>
  )
}

export default function FraudAnalytics() {
  const [tab, setTab]     = useState('heatmap')
  const [loading, setLoading] = useState(true)
  const [heatmap, setHeatmap] = useState([])
  const [byPayment, setByPayment] = useState([])

  useEffect(() => {
    setTimeout(() => {
      setHeatmap(mockHeatmap)
      setByPayment([
        { payment_method: 'CRYPTO_WALLET', total: 421,   fraud_count: 78,  fraud_rate: 18.5 },
        { payment_method: 'WIRE',          total: 1243,  fraud_count: 134, fraud_rate: 10.8 },
        { payment_method: 'CREDIT_CARD',   total: 45231, fraud_count: 312, fraud_rate: 0.69 },
        { payment_method: 'UPI',           total: 98432, fraud_count: 142, fraud_rate: 0.14 },
        { payment_method: 'DEBIT_CARD',    total: 34211, fraud_count: 89,  fraud_rate: 0.26 },
        { payment_method: 'NETBANKING',    total: 12841, fraud_count: 54,  fraud_rate: 0.42 },
        { payment_method: 'WALLET',        total: 23142, fraud_count: 67,  fraud_rate: 0.29 },
      ])
      setLoading(false)
    }, 500)
  }, [])

  if (loading) return <LoadingSpinner size={32} />

  const kpis = [
    { title: 'Total Fraud Cases',   value: 712,    icon: Shield,       color: 'red',    format: 'number'  },
    { title: 'Avg Fraud Prob.',     value: 0.67,   icon: AlertTriangle,color: 'orange', format: 'percent' },
    { title: 'Highest Risk Cat.',   value: 'GAMBLING', icon: TrendingUp, color: 'yellow', format: 'text' },
    { title: 'Pending Reviews',     value: 843,    icon: Filter,       color: 'cyan',   format: 'number'  },
  ]

  const radarData = heatmap.slice(0, 6).map(h => ({
    category: h.category.replace('_', ' '),
    fraud_rate: h.fraud_rate,
    avg_prob: h.avg_fraud_probability * 100,
  }))

  return (
    <div className="space-y-6 animate-fade-in">
      {/* KPIs */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {kpis.map((k, i) => (
          <KPICard key={i} {...k} delay={i * 0.05} />
        ))}
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-4">
        <TabGroup
          tabs={[
            { label: 'By Category',       value: 'heatmap' },
            { label: 'By Payment Method', value: 'payment' },
            { label: 'Radar Analysis',    value: 'radar'   },
          ]}
          active={tab}
          onChange={setTab}
        />
      </div>

      {/* Charts */}
      {tab === 'heatmap' && (
        <div className="sentinel-card">
          <SectionHeader title="Fraud by Merchant Category" subtitle="Transaction count vs fraud count — last 30 days" />
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={heatmap} layout="vertical" margin={{ left: 80, right: 30 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" horizontal={false} />
              <XAxis type="number" tick={{ fill: '#6B7280', fontSize: 10 }} />
              <YAxis type="category" dataKey="category" tick={{ fill: '#9CA3AF', fontSize: 10 }} width={80} />
              <Tooltip content={<CustomTooltip />} />
              <Legend wrapperStyle={{ fontSize: 11 }} />
              <Bar dataKey="total"       name="Total Txns"  fill="#1F2937"  radius={[0,4,4,0]} />
              <Bar dataKey="fraud_count" name="Fraud Count" fill="#FF3B5C"  radius={[0,4,4,0]}>
                {heatmap.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {tab === 'payment' && (
        <div className="sentinel-card">
          <SectionHeader title="Fraud by Payment Method" subtitle="Fraud rate per payment channel" />
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={byPayment} margin={{ top: 5, right: 20, bottom: 20, left: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" />
              <XAxis dataKey="payment_method" tick={{ fill: '#6B7280', fontSize: 10 }} angle={-20} textAnchor="end" />
              <YAxis tick={{ fill: '#6B7280', fontSize: 10 }} />
              <Tooltip content={<CustomTooltip />} />
              <Legend wrapperStyle={{ fontSize: 11 }} />
              <Bar dataKey="fraud_count" name="Fraud Count" fill="#FF3B5C" radius={[4,4,0,0]}>
                {byPayment.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>

          {/* Table below */}
          <div className="mt-4 overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-sentinel-border">
                  {['Method','Total','Fraud','Fraud Rate'].map(h => (
                    <th key={h} className="text-left py-2 pr-4 text-sentinel-muted font-medium">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {byPayment.map((row, i) => (
                  <tr key={i} className="border-b border-sentinel-border/40">
                    <td className="py-2 pr-4 font-mono text-cyan-400">{row.payment_method}</td>
                    <td className="py-2 pr-4 text-sentinel-text">{row.total.toLocaleString()}</td>
                    <td className="py-2 pr-4 text-red-400">{row.fraud_count}</td>
                    <td className="py-2">
                      <span className={`font-mono ${row.fraud_rate > 5 ? 'text-red-400' : row.fraud_rate > 1 ? 'text-yellow-400' : 'text-emerald-400'}`}>
                        {row.fraud_rate.toFixed(2)}%
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {tab === 'radar' && (
        <div className="sentinel-card">
          <SectionHeader title="Risk Radar — Top 6 Categories" subtitle="Fraud rate vs avg probability by merchant category" />
          <ResponsiveContainer width="100%" height={340}>
            <RadarChart data={radarData}>
              <PolarGrid stroke="#1F2937" />
              <PolarAngleAxis dataKey="category" tick={{ fill: '#9CA3AF', fontSize: 10 }} />
              <Radar name="Fraud Rate %" dataKey="fraud_rate" stroke="#FF3B5C" fill="#FF3B5C" fillOpacity={0.15} strokeWidth={2} />
              <Radar name="Avg Prob %" dataKey="avg_prob" stroke="#00D4FF" fill="#00D4FF" fillOpacity={0.1} strokeWidth={2} />
              <Legend wrapperStyle={{ fontSize: 11 }} />
              <Tooltip content={<CustomTooltip />} />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Alert Table */}
      <div className="sentinel-card">
        <SectionHeader title="Recent High-Risk Alerts" subtitle="Fraud probability ≥ 75% — awaiting review" />
        <div className="space-y-2">
          {mockAlerts.map((a, i) => (
            <motion.div
              key={a.prediction_id}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              className="flex items-center justify-between p-3 bg-sentinel-panel rounded-lg border border-sentinel-border hover:border-red-500/20 transition-all"
            >
              <div className="flex items-center gap-3">
                <div className={`w-2 h-2 rounded-full ${a.risk_level === 'CRITICAL' ? 'bg-red-500 animate-pulse' : 'bg-orange-500'}`} />
                <div>
                  <p className="text-xs font-mono text-cyan-400">{a.transaction_id.slice(0,12)}…</p>
                  <p className="text-xs text-sentinel-muted mt-0.5">{a.location_city} · {a.merchant_category}</p>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <div className="text-right">
                  <p className="text-xs font-mono text-white">₹{a.amount.toLocaleString('en-IN')}</p>
                  <p className="text-xs text-red-400 font-mono">{(a.fraud_probability * 100).toFixed(1)}% fraud</p>
                </div>
                <RiskBadge level={a.risk_level} size="xs" />
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  )
}
