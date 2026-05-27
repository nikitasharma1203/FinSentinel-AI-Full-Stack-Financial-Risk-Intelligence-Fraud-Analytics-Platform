import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, ZAxis, Cell, PieChart, Pie, Legend,
} from 'recharts'
import { Users, TrendingDown, AlertTriangle } from 'lucide-react'
import { SectionHeader, RiskBadge, LoadingSpinner, ProbabilityBar, StatRow } from '../components/dashboard/UIElements'
import KPICard from '../components/dashboard/KPICard'
import { mockCustomers, mockRiskDistribution } from '../services/mockData'

const TIER_COLORS = { LOW: '#00E5A0', MEDIUM: '#FFB020', HIGH: '#FF8C00', CRITICAL: '#FF3B5C' }

export default function CustomerRisk() {
  const [customers, setCustomers] = useState([])
  const [selected, setSelected]   = useState(null)
  const [loading, setLoading]     = useState(true)

  useEffect(() => {
    setTimeout(() => { setCustomers(mockCustomers); setLoading(false) }, 400)
  }, [])

  if (loading) return <LoadingSpinner size={32} />

  const scatterData = customers.map(c => ({
    x: +(c.total_volume / 1e5).toFixed(1),
    y: +(c.risk_score * 100).toFixed(1),
    z: c.total_transactions,
    tier: c.risk_tier,
    name: c.name,
    id: c.customer_id,
  }))

  const pieData = mockRiskDistribution.map(r => ({ name: r.tier, value: r.count, fill: TIER_COLORS[r.tier] }))

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <KPICard title="Total Customers"    value={mockRiskDistribution.reduce((a,b)=>a+b.count,0)} icon={Users}         color="cyan"   format="compact" delay={0} />
        <KPICard title="Critical Risk"      value={mockRiskDistribution.find(r=>r.tier==='CRITICAL')?.count || 0} icon={AlertTriangle} color="red"    format="number" delay={0.05} />
        <KPICard title="High Risk"          value={mockRiskDistribution.find(r=>r.tier==='HIGH')?.count || 0} icon={TrendingDown} color="orange" format="number" delay={0.1} />
        <KPICard title="Avg Risk Score"     value={+(customers.reduce((a,b)=>a+b.risk_score,0)/customers.length*100).toFixed(1)} icon={Users} color="yellow" format="percent" delay={0.15} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Scatter Plot */}
        <div className="lg:col-span-2 sentinel-card">
          <SectionHeader title="Customer Risk Map" subtitle="Volume vs Risk Score — bubble size = transaction count" />
          <ResponsiveContainer width="100%" height={280}>
            <ScatterChart margin={{ top: 10, right: 20, bottom: 10, left: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" />
              <XAxis type="number" dataKey="x" name="Volume (₹L)" tick={{ fill: '#6B7280', fontSize: 10 }} label={{ value: 'Volume (₹L)', fill: '#6B7280', fontSize: 10, position: 'insideBottom', offset: -5 }} />
              <YAxis type="number" dataKey="y" name="Risk Score" tick={{ fill: '#6B7280', fontSize: 10 }} label={{ value: 'Risk %', fill: '#6B7280', fontSize: 10, angle: -90, position: 'insideLeft' }} />
              <ZAxis type="number" dataKey="z" range={[20, 200]} />
              <Tooltip contentStyle={{ background: '#111827', border: '1px solid #1F2937', fontSize: 10 }} cursor={{ strokeDasharray: '3 3' }} />
              <Scatter data={scatterData} onClick={d => setSelected(customers.find(c=>c.customer_id===d.id))}>
                {scatterData.map((d, i) => <Cell key={i} fill={TIER_COLORS[d.tier]} fillOpacity={0.7} />)}
              </Scatter>
            </ScatterChart>
          </ResponsiveContainer>
        </div>

        {/* Pie */}
        <div className="sentinel-card">
          <SectionHeader title="Risk Distribution" />
          <ResponsiveContainer width="100%" height={180}>
            <PieChart>
              <Pie data={pieData} cx="50%" cy="50%" innerRadius={50} outerRadius={75} dataKey="value" paddingAngle={3}>
                {pieData.map((d, i) => <Cell key={i} fill={d.fill} />)}
              </Pie>
              <Tooltip contentStyle={{ background: '#111827', border: '1px solid #1F2937', fontSize: 10 }} />
              <Legend wrapperStyle={{ fontSize: 11 }} />
            </PieChart>
          </ResponsiveContainer>
          <div className="mt-3 space-y-1">
            {mockRiskDistribution.map(r => (
              <div key={r.tier} className="flex justify-between items-center">
                <span className="text-xs text-sentinel-muted">{r.tier}</span>
                <div className="flex items-center gap-2">
                  <div className="w-20 h-1 bg-sentinel-border rounded-full overflow-hidden">
                    <div className="h-full rounded-full" style={{ width: `${r.count/mockRiskDistribution.reduce((a,b)=>a+b.count,0)*100}%`, background: TIER_COLORS[r.tier] }} />
                  </div>
                  <span className="text-xs font-mono" style={{ color: TIER_COLORS[r.tier] }}>{r.count.toLocaleString()}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Customer Table & Detail */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 sentinel-card overflow-x-auto">
          <SectionHeader title="High-Risk Customers" subtitle="Ordered by risk score" />
          <table className="w-full text-xs">
            <thead><tr className="border-b border-sentinel-border">
              {['Name','Segment','Risk Score','Churn Prob.','Transactions','Tier'].map(h=>(
                <th key={h} className="text-left py-2 pr-3 text-sentinel-muted font-medium">{h}</th>
              ))}
            </tr></thead>
            <tbody>
              {customers.filter(c=>['HIGH','CRITICAL'].includes(c.risk_tier)).slice(0,15).map((c,i)=>(
                <motion.tr key={c.customer_id} initial={{opacity:0}} animate={{opacity:1}} transition={{delay:i*0.04}}
                  onClick={()=>setSelected(c)}
                  className="border-b border-sentinel-border/30 hover:bg-white/2 cursor-pointer transition-colors">
                  <td className="py-2.5 pr-3 text-white">{c.name}</td>
                  <td className="py-2.5 pr-3 text-sentinel-muted font-mono text-[10px]">{c.customer_segment}</td>
                  <td className="py-2.5 pr-3 w-28"><ProbabilityBar value={c.risk_score} /></td>
                  <td className="py-2.5 pr-3 w-28"><ProbabilityBar value={c.churn_probability} /></td>
                  <td className="py-2.5 pr-3 font-mono text-sentinel-muted">{c.total_transactions}</td>
                  <td className="py-2.5"><RiskBadge level={c.risk_tier} size="xs" /></td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>

        {selected ? (
          <div className="sentinel-card">
            <SectionHeader title="Customer Profile" />
            <div className="space-y-0.5">
              <StatRow label="Name"         value={selected.name} highlight />
              <StatRow label="Segment"      value={selected.customer_segment} />
              <StatRow label="Risk Score"   value={`${(selected.risk_score*100).toFixed(1)}%`} highlight />
              <StatRow label="Risk Tier"    value={selected.risk_tier} />
              <StatRow label="Churn Risk"   value={`${(selected.churn_probability*100).toFixed(1)}%`} />
              <StatRow label="Total Txns"   value={selected.total_transactions.toLocaleString()} />
              <StatRow label="Total Volume" value={`₹${(selected.total_volume/1e5).toFixed(1)}L`} highlight />
              <StatRow label="Avg Amount"   value={`₹${selected.avg_transaction_amount.toFixed(0)}`} />
            </div>
            <button onClick={()=>setSelected(null)} className="mt-4 w-full text-xs py-2 border border-sentinel-border rounded-lg text-sentinel-muted hover:text-white transition-colors">
              Clear
            </button>
          </div>
        ) : (
          <div className="sentinel-card flex items-center justify-center text-sentinel-muted">
            <p className="text-xs">Click a customer row to view profile</p>
          </div>
        )}
      </div>
    </div>
  )
}
