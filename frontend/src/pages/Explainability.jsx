import React from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { BrainCircuit } from 'lucide-react'
import { SectionHeader } from '../components/dashboard/UIElements'
import { mockGlobalFeatureImportance, mockCorrelations } from '../services/mockData'

export default function Explainability() {
  const features = mockGlobalFeatureImportance.feature_importance
  const maxImp = Math.max(...features.map(f => f.importance))
  const correlations = mockCorrelations.correlations

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Global Feature Importance */}
        <div className="sentinel-card">
          <SectionHeader title="Global Feature Importance" subtitle="Mean |SHAP| across all predictions" />
          <ResponsiveContainer width="100%" height={320}>
            <BarChart data={features} layout="vertical" margin={{ left: 140, right: 30 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" horizontal={false} />
              <XAxis type="number" tick={{ fill: '#6B7280', fontSize: 10 }} />
              <YAxis type="category" dataKey="feature" tick={{ fill: '#9CA3AF', fontSize: 9 }} width={140} />
              <Tooltip contentStyle={{ background: '#111827', border: '1px solid #1F2937', fontSize: 10 }} />
              <Bar dataKey="importance" name="Importance" radius={[0,4,4,0]}>
                {features.map((f, i) => (
                  <Cell key={i} fill={`rgba(0,212,255,${0.3 + (f.importance/maxImp)*0.7})`} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Macro Correlations */}
        <div className="sentinel-card">
          <SectionHeader title="Macro Correlations with Fraud" subtitle="Pearson correlation between macro variables and fraud rate" />
          <div className="space-y-3 mt-2">
            {correlations.map((c, i) => (
              <div key={i} className="flex items-center gap-3">
                <span className="text-xs text-sentinel-muted w-40 shrink-0">{c.feature}</span>
                <div className="flex-1 h-2 bg-sentinel-border rounded-full overflow-hidden relative">
                  <div
                    className={`h-full rounded-full transition-all duration-500 ${c.direction === 'positive' ? 'bg-red-500' : 'bg-emerald-500'}`}
                    style={{
                      width: `${Math.abs(c.correlation) * 100}%`,
                      marginLeft: c.direction === 'negative' ? `${(1 - Math.abs(c.correlation)) * 100}%` : 0
                    }}
                  />
                </div>
                <span className={`text-xs font-mono w-12 text-right ${c.direction === 'positive' ? 'text-red-400' : 'text-emerald-400'}`}>
                  {c.correlation > 0 ? '+' : ''}{c.correlation.toFixed(2)}
                </span>
              </div>
            ))}
          </div>

          <div className="mt-4 p-3 bg-sentinel-panel rounded-lg border border-sentinel-border text-xs text-sentinel-muted">
            <p className="font-semibold text-white mb-1">Interpretation</p>
            <p><span className="text-red-400">Positive correlation</span>: As variable increases, fraud risk increases.</p>
            <p className="mt-1"><span className="text-emerald-400">Negative correlation</span>: As variable increases, fraud risk decreases.</p>
          </div>
        </div>
      </div>

      {/* Example Explanation Panel */}
      <div className="sentinel-card">
        <SectionHeader title="Sample Prediction Explanation" subtitle="Why was TXN-A1B2C3 flagged as CRITICAL?" />
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div>
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 bg-red-500/10 rounded-lg border border-red-500/20">
                <BrainCircuit size={16} className="text-red-400" />
              </div>
              <div>
                <p className="text-sm font-semibold text-white">Fraud Probability: <span className="text-red-400">94.2%</span></p>
                <p className="text-xs text-sentinel-muted">XGBoost + Isolation Forest v1.0 — CRITICAL</p>
              </div>
            </div>
            <div className="p-3 bg-red-500/5 border border-red-500/20 rounded-lg text-xs text-sentinel-muted">
              <p className="text-red-300 font-medium mb-1">Explanation</p>
              Transaction flagged due to: <span className="text-white">abnormal spending velocity</span> (+480% above average),
              <span className="text-white"> unseen merchant category</span> (CRYPTO — first occurrence for this customer),
              <span className="text-white"> location mismatch</span> (usual: Mumbai, current: Dubai),
              and <span className="text-white"> unusually high amount</span> (₹2,85,000 vs ₹12,400 avg).
            </div>
          </div>
          <div>
            <p className="text-xs text-sentinel-muted mb-3">Feature Contributions (SHAP)</p>
            {[
              { feature: 'transaction_velocity_1h',  value: 0.38, positive: true },
              { feature: 'amount_deviation_from_avg',value: 0.27, positive: true },
              { feature: 'merchant_category_rarity', value: 0.19, positive: true },
              { feature: 'geographic_distance_km',   value: 0.14, positive: true },
              { feature: 'hour_of_day',              value: 0.08, positive: true },
              { feature: 'is_regular_merchant',      value: -0.06, positive: false },
            ].map((f, i) => (
              <div key={i} className="flex items-center gap-2 mb-1.5">
                <span className="text-[10px] font-mono text-sentinel-muted w-44 shrink-0">{f.feature}</span>
                <div className="flex-1 h-1.5 bg-sentinel-border rounded-full overflow-hidden">
                  <div className={`h-full rounded-full ${f.positive ? 'bg-red-500' : 'bg-emerald-500'}`}
                    style={{ width: `${Math.abs(f.value) / 0.38 * 100}%` }} />
                </div>
                <span className={`text-[10px] font-mono w-10 text-right ${f.positive ? 'text-red-400' : 'text-emerald-400'}`}>
                  {f.value > 0 ? '+' : ''}{f.value.toFixed(2)}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
