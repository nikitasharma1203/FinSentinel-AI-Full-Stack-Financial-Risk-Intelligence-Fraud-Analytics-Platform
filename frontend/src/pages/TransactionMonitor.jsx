import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, AreaChart, Area,
} from 'recharts'
import { Activity, Search, Filter, Download } from 'lucide-react'
import { RiskBadge, SectionHeader, LoadingSpinner, ProbabilityBar } from '../components/dashboard/UIElements'
import { mockAlerts, mockTrends } from '../services/mockData'

function generateTransactions(n = 40) {
  const cats = ['RETAIL','FOOD_DINING','TRAVEL','ELECTRONICS','CRYPTO','WIRE_TRANSFER','GAMBLING','HEALTHCARE','FUEL','GROCERY']
  const cities = ['Mumbai','Delhi','Bangalore','Hyderabad','Chennai','Pune','Rajkot','Jaipur']
  const methods = ['UPI','CREDIT_CARD','DEBIT_CARD','NETBANKING','WALLET']
  const statuses = ['COMPLETED','COMPLETED','COMPLETED','COMPLETED','FAILED']
  return Array.from({ length: n }, (_, i) => {
    const prob = Math.random()
    const isHighRisk = Math.random() < 0.08
    return {
      transaction_id: `TXN${(Math.random()*1e9|0).toString(16).toUpperCase()}`,
      amount: Math.round(Math.random() * (isHighRisk ? 200000 : 25000) + 200),
      currency: 'INR',
      timestamp: new Date(Date.now() - Math.random() * 86400000 * 7).toISOString(),
      location_city: cities[Math.floor(Math.random() * cities.length)],
      merchant_category: cats[Math.floor(Math.random() * cats.length)],
      payment_method: methods[Math.floor(Math.random() * methods.length)],
      fraud_probability: isHighRisk ? 0.65 + Math.random() * 0.35 : prob * 0.4,
      risk_level: isHighRisk ? (prob > 0.5 ? 'CRITICAL' : 'HIGH') : (prob > 0.7 ? 'MEDIUM' : 'LOW'),
      flagged: isHighRisk,
      status: statuses[Math.floor(Math.random() * statuses.length)],
    }
  }).sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
}

export default function TransactionMonitor() {
  const [txns, setTxns]           = useState([])
  const [filter, setFilter]       = useState('')
  const [flaggedOnly, setFlagged] = useState(false)
  const [loading, setLoading]     = useState(true)

  useEffect(() => {
    setTimeout(() => { setTxns(generateTransactions(50)); setLoading(false) }, 400)
    const interval = setInterval(() => {
      setTxns(prev => [generateTransactions(1)[0], ...prev].slice(0, 100))
    }, 5000)
    return () => clearInterval(interval)
  }, [])

  const filtered = txns.filter(t => {
    const matchText = !filter || t.transaction_id.includes(filter.toUpperCase()) || t.merchant_category.includes(filter.toUpperCase()) || t.location_city.toLowerCase().includes(filter.toLowerCase())
    const matchFlag = !flaggedOnly || t.flagged
    return matchText && matchFlag
  })

  if (loading) return <LoadingSpinner size={32} />

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Live Trend */}
      <div className="sentinel-card">
        <SectionHeader title="Live Transaction Volume" subtitle="Real-time monitoring — updates every 5s" />
        <ResponsiveContainer width="100%" height={140}>
          <AreaChart data={mockTrends.slice(-14)} margin={{ top: 5, right: 5, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="liveGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%"  stopColor="#00D4FF" stopOpacity={0.2} />
                <stop offset="95%" stopColor="#00D4FF" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" />
            <XAxis dataKey="date" tick={{ fill: '#6B7280', fontSize: 9 }} tickFormatter={d => d.slice(5)} />
            <YAxis tick={{ fill: '#6B7280', fontSize: 9 }} />
            <Tooltip contentStyle={{ background: '#111827', border: '1px solid #1F2937', fontSize: 10 }} />
            <Area type="monotone" dataKey="total" stroke="#00D4FF" strokeWidth={1.5} fill="url(#liveGrad)" dot={false} />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-3 flex-wrap">
        <div className="relative flex-1 min-w-48">
          <Search size={13} className="absolute left-3 top-1/2 -translate-y-1/2 text-sentinel-muted" />
          <input
            value={filter} onChange={e => setFilter(e.target.value)}
            placeholder="Filter by ID, category, city…"
            className="w-full pl-8 pr-4 py-2 text-xs bg-sentinel-panel border border-sentinel-border rounded-lg text-sentinel-text placeholder-sentinel-muted focus:outline-none focus:border-cyan-500/50"
          />
        </div>
        <button
          onClick={() => setFlagged(!flaggedOnly)}
          className={`flex items-center gap-2 px-3 py-2 text-xs rounded-lg border transition-all ${flaggedOnly ? 'bg-red-500/10 border-red-500/30 text-red-400' : 'border-sentinel-border text-sentinel-muted hover:text-white'}`}
        >
          <Filter size={12} /> Flagged Only
        </button>
        <span className="text-xs text-sentinel-muted font-mono">{filtered.length} transactions</span>
      </div>

      {/* Table */}
      <div className="sentinel-card overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b border-sentinel-border">
              {['ID','Amount','Category','City','Method','Fraud Prob.','Risk','Status'].map(h => (
                <th key={h} className="text-left py-2.5 pr-3 text-sentinel-muted font-medium whitespace-nowrap">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filtered.slice(0, 30).map((t, i) => (
              <motion.tr
                key={t.transaction_id}
                initial={{ opacity: 0, x: -6 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: Math.min(i * 0.03, 0.5) }}
                className="border-b border-sentinel-border/30 hover:bg-white/2 transition-colors"
              >
                <td className="py-2.5 pr-3 font-mono text-cyan-400 whitespace-nowrap">{t.transaction_id.slice(0,10)}</td>
                <td className="py-2.5 pr-3 font-mono text-white whitespace-nowrap">₹{t.amount.toLocaleString('en-IN')}</td>
                <td className="py-2.5 pr-3">
                  <span className="bg-sentinel-panel border border-sentinel-border rounded px-1.5 py-0.5 font-mono text-[10px]">{t.merchant_category}</span>
                </td>
                <td className="py-2.5 pr-3 text-sentinel-muted">{t.location_city}</td>
                <td className="py-2.5 pr-3 text-sentinel-muted font-mono text-[10px]">{t.payment_method}</td>
                <td className="py-2.5 pr-3 w-40"><ProbabilityBar value={t.fraud_probability} /></td>
                <td className="py-2.5 pr-3"><RiskBadge level={t.risk_level} size="xs" /></td>
                <td className="py-2.5">
                  <span className={`text-[9px] font-mono px-1.5 py-0.5 rounded border ${t.status === 'COMPLETED' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' : 'bg-red-500/10 text-red-400 border-red-500/30'}`}>
                    {t.status}
                  </span>
                </td>
              </motion.tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
