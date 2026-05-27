import React, { useEffect, useState } from 'react'
import {
  AreaChart, Area, LineChart, Line, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, Legend,
} from 'recharts'
import { Globe, Zap, TrendingDown } from 'lucide-react'
import { SectionHeader, LoadingSpinner } from '../components/dashboard/UIElements'
import { mockSentimentSeries } from '../services/mockData'

export default function SentimentDashboard() {
  const [series, setSeries] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => { setTimeout(() => { setSeries(mockSentimentSeries); setLoading(false) }, 400) }, [])
  if (loading) return <LoadingSpinner size={32} />

  const topics = [
    { topic: 'RBI Monetary Policy',    sentiment: 0.12,  volume: 847,  impact: 'MEDIUM' },
    { topic: 'India Inflation CPI',    sentiment: -0.31, volume: 1203, impact: 'HIGH' },
    { topic: 'Rupee Depreciation',     sentiment: -0.54, volume: 962,  impact: 'HIGH' },
    { topic: 'Middle East Oil Prices', sentiment: -0.41, volume: 1548, impact: 'CRITICAL' },
    { topic: 'FII Outflows',           sentiment: -0.28, volume: 634,  impact: 'MEDIUM' },
    { topic: 'India GDP Growth',       sentiment: 0.38,  volume: 712,  impact: 'MEDIUM' },
    { topic: 'US Fed Rate Decision',   sentiment: -0.19, volume: 1891, impact: 'HIGH' },
    { topic: 'India Digital Payments', sentiment: 0.61,  volume: 423,  impact: 'LOW' },
  ]

  const shocks = [
    { date:'2024-04-15', event:'Iran-Israel Tensions',       shock_score:0.82, impact_on_inr:-1.2 },
    { date:'2023-10-07', event:'Israel-Gaza War Outbreak',   shock_score:0.91, impact_on_inr:-1.8 },
    { date:'2023-08-23', event:'Brent Crude 9-Month High',   shock_score:0.67, impact_on_inr:-0.9 },
    { date:'2022-02-24', event:'Russia-Ukraine War',          shock_score:0.95, impact_on_inr:-2.3 },
    { date:'2020-03-23', event:'COVID-19 Market Crash',       shock_score:0.99, impact_on_inr:-4.1 },
  ]

  const impactColors = { CRITICAL:'text-red-400 border-red-500/30 bg-red-500/5', HIGH:'text-orange-400 border-orange-500/30 bg-orange-500/5', MEDIUM:'text-yellow-400 border-yellow-500/30 bg-yellow-500/5', LOW:'text-emerald-400 border-emerald-500/30 bg-emerald-500/5' }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Sentiment time series */}
      <div className="sentinel-card">
        <SectionHeader title="News Sentiment & Geopolitical Risk" subtitle="NLP-scored daily sentiment from financial news (last 90 days)" />
        <ResponsiveContainer width="100%" height={220}>
          <AreaChart data={series} margin={{ top: 5, right: 5, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="sentPos" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%"  stopColor="#00E5A0" stopOpacity={0.2} />
                <stop offset="95%" stopColor="#00E5A0" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="riskGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%"  stopColor="#FF3B5C" stopOpacity={0.15} />
                <stop offset="95%" stopColor="#FF3B5C" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" />
            <XAxis dataKey="date" tick={{ fill: '#6B7280', fontSize: 9 }} tickFormatter={d => d.slice(5)} />
            <YAxis tick={{ fill: '#6B7280', fontSize: 10 }} />
            <Tooltip contentStyle={{ background: '#111827', border: '1px solid #1F2937', fontSize: 10 }} />
            <Legend wrapperStyle={{ fontSize: 11 }} />
            <Area type="monotone" dataKey="sentiment_score" name="Sentiment" stroke="#00E5A0" strokeWidth={1.5} fill="url(#sentPos)" dot={false} />
            <Area type="monotone" dataKey="geopolitical_risk" name="Geo Risk" stroke="#FF3B5C" strokeWidth={1.5} fill="url(#riskGrad)" dot={false} />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Topics */}
        <div className="sentinel-card">
          <SectionHeader title="News Topic Sentiment" subtitle="Aggregated NLP scores by topic" />
          <div className="space-y-2.5">
            {topics.map((t, i) => (
              <div key={i} className="flex items-center gap-3">
                <span className="text-xs text-sentinel-muted w-40 shrink-0 truncate">{t.topic}</span>
                <div className="flex-1 h-1.5 bg-sentinel-border rounded-full overflow-hidden">
                  <div className={`h-full rounded-full ${t.sentiment > 0 ? 'bg-emerald-500' : 'bg-red-500'}`}
                    style={{ width: `${Math.abs(t.sentiment)*100}%` }} />
                </div>
                <span className={`text-xs font-mono w-10 text-right ${t.sentiment > 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                  {t.sentiment > 0 ? '+' : ''}{t.sentiment.toFixed(2)}
                </span>
                <span className={`text-[9px] font-mono px-1.5 py-0.5 rounded border shrink-0 ${impactColors[t.impact]}`}>{t.impact}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Shock Events */}
        <div className="sentinel-card">
          <SectionHeader title="Geopolitical Shock Events" subtitle="High-severity events and INR impact" />
          <div className="space-y-2">
            {shocks.map((s, i) => (
              <div key={i} className="p-3 bg-sentinel-panel rounded-lg border border-sentinel-border">
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <p className="text-xs text-white font-medium">{s.event}</p>
                    <p className="text-xs text-sentinel-muted font-mono mt-0.5">{s.date}</p>
                  </div>
                  <div className="text-right shrink-0">
                    <p className="text-xs font-mono text-red-400">Score: {s.shock_score.toFixed(2)}</p>
                    <p className="text-xs font-mono text-orange-400 mt-0.5">INR: {s.impact_on_inr > 0 ? '+' : ''}{s.impact_on_inr}%</p>
                  </div>
                </div>
                <div className="mt-2 h-1 bg-sentinel-border rounded-full overflow-hidden">
                  <div className="h-full bg-red-500 rounded-full" style={{ width: `${s.shock_score * 100}%` }} />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
