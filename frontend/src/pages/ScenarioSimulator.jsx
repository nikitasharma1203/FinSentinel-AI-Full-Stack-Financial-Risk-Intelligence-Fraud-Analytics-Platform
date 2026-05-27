import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, RadialBarChart, RadialBar, Legend,
} from 'recharts'
import { FlaskConical, AlertTriangle, TrendingUp, Zap, Play, RotateCcw } from 'lucide-react'
import { SectionHeader, LoadingSpinner } from '../components/dashboard/UIElements'

const DEFAULT_PARAMS = {
  scenario_name: 'Custom Scenario',
  inflation_spike_pct: 0,
  transaction_surge_pct: 0,
  fraud_spike_pct: 0,
  liquidity_stress_pct: 0,
  recession_severity: 0,
}

const PRESETS = [
  { name: '🛢️ Oil Shock', params: { inflation_spike_pct: 18, transaction_surge_pct: -15, fraud_spike_pct: 35, liquidity_stress_pct: 25, recession_severity: 0.3 } },
  { name: '📉 Recession',  params: { inflation_spike_pct: 8, transaction_surge_pct: -30, fraud_spike_pct: 80, liquidity_stress_pct: 45, recession_severity: 0.8 } },
  { name: '🚨 Fraud Storm', params: { inflation_spike_pct: 2, transaction_surge_pct: 40, fraud_spike_pct: 250, liquidity_stress_pct: 10, recession_severity: 0.1 } },
  { name: '💹 Boom',       params: { inflation_spike_pct: 5, transaction_surge_pct: 120, fraud_spike_pct: 20, liquidity_stress_pct: 0, recession_severity: 0 } },
]

function simulateLocally(params) {
  const baseTxn      = 284751
  const baseVolume   = 4_218_543_920
  const baseFraudRate = 0.0025
  const baseExposure  = baseVolume * baseFraudRate

  const inflation   = 1 + params.inflation_spike_pct / 100
  const surge       = 1 + params.transaction_surge_pct / 100
  const fraudBoost  = (1 + params.fraud_spike_pct / 100) * (1 + params.recession_severity * 0.35)
  const liq         = params.liquidity_stress_pct / 100

  const projTxn     = Math.round(baseTxn * surge)
  const projVol     = baseVolume * surge * (1 - params.inflation_spike_pct / 200)
  const projFraud   = Math.min(baseFraudRate * fraudBoost, 1)
  const projFraudCt = Math.round(projTxn * projFraud)
  const projFraudVol = projFraudCt * (baseVolume / baseTxn) * inflation
  const failureRate  = Math.min(0.02 + liq * 0.15, 0.5)
  const projExposure = projVol * projFraud
  const riskChange   = (projExposure - baseExposure) / baseExposure * 100

  const stressIndex = Math.min(100,
    params.fraud_spike_pct * 0.25
    + params.transaction_surge_pct * 0.15
    + params.liquidity_stress_pct * 0.3
    + params.inflation_spike_pct * 0.1
    + params.recession_severity * 20
  )

  const alerts = []
  if (stressIndex > 70) alerts.push({ severity: 'CRITICAL', message: 'Extreme operational stress. Activate incident response.' })
  if (riskChange > 100) alerts.push({ severity: 'HIGH',     message: `Risk exposure projected to increase by ${riskChange.toFixed(0)}%.` })
  if (projFraud > 0.1)  alerts.push({ severity: 'HIGH',     message: `Fraud rate exceeds 10% under this scenario.` })
  if (liq > 0.5)        alerts.push({ severity: 'MEDIUM',   message: 'High liquidity stress may trigger transaction failures.' })
  if (!alerts.length)   alerts.push({ severity: 'LOW',      message: 'Scenario within manageable risk parameters.' })

  return {
    baseline:  { transaction_count: baseTxn, total_volume: baseVolume, fraud_rate: baseFraudRate * 100, risk_exposure: baseExposure },
    projected: { transaction_count: projTxn, total_volume: projVol, fraud_count: projFraudCt, fraud_rate: projFraud * 100, fraud_volume: projFraudVol, risk_exposure: projExposure, risk_exposure_change_pct: riskChange, failed_transactions: Math.round(projTxn * failureRate) },
    stress_metrics: { operational_stress_index: stressIndex, model_accuracy_under_stress: Math.max(50, 94 - stressIndex * 0.4) },
    alerts,
  }
}

const alertColors = { CRITICAL: 'border-red-500/40 bg-red-500/5 text-red-400', HIGH: 'border-orange-500/40 bg-orange-500/5 text-orange-400', MEDIUM: 'border-yellow-500/40 bg-yellow-500/5 text-yellow-400', LOW: 'border-emerald-500/40 bg-emerald-500/5 text-emerald-400' }

function Slider({ label, value, onChange, min = 0, max = 100, step = 1, unit = '%', color = 'cyan' }) {
  const pct = ((value - min) / (max - min)) * 100
  const colors = { cyan: '#00D4FF', red: '#FF3B5C', yellow: '#FFB020', orange: '#FF8C00', green: '#00E5A0' }
  return (
    <div className="space-y-1.5">
      <div className="flex justify-between items-center">
        <label className="text-xs text-sentinel-muted">{label}</label>
        <span className="text-xs font-mono font-bold" style={{ color: colors[color] }}>
          {value}{unit}
        </span>
      </div>
      <div className="relative">
        <input
          type="range" min={min} max={max} step={step} value={value}
          onChange={e => onChange(Number(e.target.value))}
          className="w-full h-1.5 rounded-full appearance-none cursor-pointer"
          style={{
            background: `linear-gradient(to right, ${colors[color]} ${pct}%, #1F2937 ${pct}%)`,
          }}
        />
      </div>
    </div>
  )
}

export default function ScenarioSimulator() {
  const [params, setParams]     = useState(DEFAULT_PARAMS)
  const [results, setResults]   = useState(null)
  const [running, setRunning]   = useState(false)

  const set = (key) => (val) => setParams(p => ({ ...p, [key]: val }))

  const runScenario = () => {
    setRunning(true)
    setTimeout(() => {
      setResults(simulateLocally(params))
      setRunning(false)
    }, 800)
  }

  const reset = () => { setParams(DEFAULT_PARAMS); setResults(null) }

  const stressColor = results
    ? results.stress_metrics.operational_stress_index > 70 ? 'text-red-400'
    : results.stress_metrics.operational_stress_index > 40 ? 'text-yellow-400'
    : 'text-emerald-400'
    : 'text-sentinel-muted'

  const comparisonData = results ? [
    { name: 'Transactions', baseline: results.baseline.transaction_count, projected: results.projected.transaction_count },
    { name: 'Fraud Count',  baseline: Math.round(results.baseline.transaction_count * results.baseline.fraud_rate / 100), projected: results.projected.fraud_count },
  ] : []

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        {/* Controls Panel */}
        <div className="lg:col-span-2 space-y-4">
          <div className="sentinel-card">
            <SectionHeader title="Scenario Parameters" subtitle="Adjust stress conditions" />

            {/* Presets */}
            <div className="grid grid-cols-2 gap-2 mb-5">
              {PRESETS.map(p => (
                <button
                  key={p.name}
                  onClick={() => setParams({ ...DEFAULT_PARAMS, scenario_name: p.name, ...p.params })}
                  className="text-xs py-1.5 px-2 rounded border border-sentinel-border bg-sentinel-panel text-sentinel-muted hover:text-white hover:border-cyan-500/30 transition-all text-left"
                >
                  {p.name}
                </button>
              ))}
            </div>

            <div className="space-y-5">
              <Slider label="Inflation Spike"        value={params.inflation_spike_pct}    onChange={set('inflation_spike_pct')}    max={100} color="yellow" />
              <Slider label="Transaction Surge"      value={params.transaction_surge_pct}  onChange={set('transaction_surge_pct')}  max={500} color="cyan" />
              <Slider label="Fraud Attack Surge"     value={params.fraud_spike_pct}        onChange={set('fraud_spike_pct')}        max={500} color="red" />
              <Slider label="Liquidity Stress"       value={params.liquidity_stress_pct}   onChange={set('liquidity_stress_pct')}   max={100} color="orange" />
              <Slider label="Recession Severity"     value={params.recession_severity}     onChange={set('recession_severity')}     max={1} step={0.01} unit="" color="orange" />
            </div>

            <div className="flex gap-3 mt-6">
              <button
                onClick={runScenario}
                disabled={running}
                className="flex-1 flex items-center justify-center gap-2 py-2.5 bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 rounded-lg text-sm font-medium hover:bg-cyan-500/20 transition-all disabled:opacity-50"
              >
                {running ? <LoadingSpinner size={14} /> : <Play size={14} />}
                {running ? 'Simulating…' : 'Run Scenario'}
              </button>
              <button onClick={reset} className="p-2.5 border border-sentinel-border rounded-lg text-sentinel-muted hover:text-white hover:border-sentinel-muted/50 transition-all">
                <RotateCcw size={14} />
              </button>
            </div>
          </div>
        </div>

        {/* Results */}
        <div className="lg:col-span-3 space-y-4">
          <AnimatePresence mode="wait">
            {!results && !running ? (
              <motion.div
                key="empty"
                initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                className="sentinel-card flex flex-col items-center justify-center h-64 text-sentinel-muted"
              >
                <FlaskConical size={32} className="mb-3 opacity-30" />
                <p className="text-sm">Adjust parameters and run a scenario</p>
              </motion.div>
            ) : results ? (
              <motion.div key="results" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
                {/* Stress Index */}
                <div className="sentinel-card">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-xs text-sentinel-muted">Operational Stress Index</p>
                      <p className={`text-5xl font-display font-bold mt-1 ${stressColor}`}>
                        {results.stress_metrics.operational_stress_index.toFixed(0)}
                        <span className="text-lg ml-1 opacity-60">/100</span>
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-xs text-sentinel-muted">Model Accuracy</p>
                      <p className="text-2xl font-display font-bold text-white mt-1">
                        {results.stress_metrics.model_accuracy_under_stress.toFixed(1)}%
                      </p>
                    </div>
                  </div>
                </div>

                {/* Key Metrics Comparison */}
                <div className="grid grid-cols-2 gap-3">
                  {[
                    { label: 'Projected Fraud Rate', value: results.projected.fraud_rate.toFixed(3) + '%', change: ((results.projected.fraud_rate - results.baseline.fraud_rate) / results.baseline.fraud_rate * 100).toFixed(0) },
                    { label: 'Risk Exposure Δ', value: `₹${(results.projected.risk_exposure/1e7).toFixed(1)}Cr`, change: results.projected.risk_exposure_change_pct.toFixed(0) },
                    { label: 'Failed Txns', value: results.projected.failed_transactions.toLocaleString(), change: null },
                    { label: 'Fraud Volume', value: `₹${(results.projected.fraud_volume/1e7).toFixed(1)}Cr`, change: null },
                  ].map((m, i) => (
                    <div key={i} className="sentinel-card py-3">
                      <p className="text-xs text-sentinel-muted">{m.label}</p>
                      <p className="text-lg font-display font-bold text-white mt-0.5">{m.value}</p>
                      {m.change && <p className={`text-xs font-mono mt-0.5 ${+m.change > 0 ? 'text-red-400' : 'text-emerald-400'}`}>{+m.change > 0 ? '↑' : '↓'} {Math.abs(+m.change)}%</p>}
                    </div>
                  ))}
                </div>

                {/* Comparison Chart */}
                <div className="sentinel-card">
                  <SectionHeader title="Baseline vs Projected" />
                  <ResponsiveContainer width="100%" height={180}>
                    <BarChart data={comparisonData} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" />
                      <XAxis dataKey="name" tick={{ fill: '#6B7280', fontSize: 10 }} />
                      <YAxis tick={{ fill: '#6B7280', fontSize: 10 }} />
                      <Tooltip contentStyle={{ background: '#111827', border: '1px solid #1F2937', fontSize: 11 }} />
                      <Legend wrapperStyle={{ fontSize: 11 }} />
                      <Bar dataKey="baseline"  name="Baseline"  fill="#1F4F6B" radius={[4,4,0,0]} />
                      <Bar dataKey="projected" name="Projected" fill="#FF3B5C" radius={[4,4,0,0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>

                {/* Alerts */}
                <div className="space-y-2">
                  {results.alerts.map((a, i) => (
                    <div key={i} className={`p-3 rounded-lg border text-xs ${alertColors[a.severity]}`}>
                      <span className="font-bold mr-2">[{a.severity}]</span>{a.message}
                    </div>
                  ))}
                </div>
              </motion.div>
            ) : null}
          </AnimatePresence>
        </div>
      </div>
    </div>
  )
}
