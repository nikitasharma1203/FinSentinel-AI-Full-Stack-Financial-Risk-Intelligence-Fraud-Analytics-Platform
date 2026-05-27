import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { FileText, Download, Plus, CheckCircle } from 'lucide-react'
import { SectionHeader } from '../components/dashboard/UIElements'

const REPORT_TYPES = [
  { type: 'EXECUTIVE',  label: 'Executive Summary',      desc: 'High-level KPIs, fraud trends, top alerts' },
  { type: 'FRAUD',      label: 'Fraud Analytics Report', desc: 'Full fraud detection breakdown with SHAP' },
  { type: 'CUSTOMER',   label: 'Customer Risk Report',   desc: 'Risk scores, segments, churn analysis' },
  { type: 'NETWORK',    label: 'Network Intelligence',   desc: 'Graph clusters, propagation paths' },
  { type: 'SCENARIO',   label: 'Scenario Simulation',    desc: 'Stress test results and projections' },
]

const SAMPLE_REPORTS = [
  { id: 'r1', title: 'Executive Summary — May 2025',     type: 'EXECUTIVE', generated_at: '2025-05-01T09:00:00Z', available: true },
  { id: 'r2', title: 'Fraud Analytics — April 2025',     type: 'FRAUD',     generated_at: '2025-04-30T17:22:00Z', available: true },
  { id: 'r3', title: 'Customer Risk Report — Q1 2025',   type: 'CUSTOMER',  generated_at: '2025-04-01T11:00:00Z', available: true },
  { id: 'r4', title: 'Scenario: Oil Shock Analysis',     type: 'SCENARIO',  generated_at: '2025-03-15T14:45:00Z', available: true },
  { id: 'r5', title: 'Network Intelligence — March 2025',type: 'NETWORK',   generated_at: '2025-03-05T08:30:00Z', available: true },
]

const typeColors = {
  EXECUTIVE: 'bg-cyan-500/10   text-cyan-400   border-cyan-500/20',
  FRAUD:     'bg-red-500/10    text-red-400    border-red-500/20',
  CUSTOMER:  'bg-purple-500/10 text-purple-400 border-purple-500/20',
  NETWORK:   'bg-orange-500/10 text-orange-400 border-orange-500/20',
  SCENARIO:  'bg-yellow-500/10 text-yellow-400 border-yellow-500/20',
}

export default function Reports() {
  const [generating, setGenerating]   = useState(false)
  const [generated, setGenerated]     = useState(null)
  const [selectedType, setSelectedType] = useState(null)
  const [reports] = useState(SAMPLE_REPORTS)

  const handleGenerate = () => {
    if (!selectedType) return
    setGenerating(true)
    setTimeout(() => {
      setGenerated(selectedType)
      setGenerating(false)
    }, 2000)
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Generate */}
      <div className="sentinel-card">
        <SectionHeader title="Generate New Report" subtitle="Select report type and export as PDF" />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 mb-5">
          {REPORT_TYPES.map(rt => (
            <button
              key={rt.type}
              onClick={() => setSelectedType(rt.type)}
              className={`p-3 text-left rounded-lg border transition-all ${selectedType === rt.type ? 'border-cyan-500/40 bg-cyan-500/5' : 'border-sentinel-border bg-sentinel-panel hover:border-sentinel-muted/30'}`}
            >
              <p className="text-xs font-semibold text-white">{rt.label}</p>
              <p className="text-xs text-sentinel-muted mt-0.5">{rt.desc}</p>
            </button>
          ))}
        </div>
        <button
          onClick={handleGenerate}
          disabled={!selectedType || generating}
          className="flex items-center gap-2 px-4 py-2 bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 rounded-lg text-sm font-medium hover:bg-cyan-500/20 transition-all disabled:opacity-40"
        >
          {generating ? (
            <><div className="w-4 h-4 border-2 border-cyan-500/30 border-t-cyan-400 rounded-full animate-spin" /> Generating…</>
          ) : generated ? (
            <><CheckCircle size={14} className="text-emerald-400" /> Report Ready — Download</>
          ) : (
            <><Plus size={14} /> Generate Report</>
          )}
        </button>
        {generated && !generating && (
          <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-xs text-emerald-400 mt-2">
            ✓ {REPORT_TYPES.find(r=>r.type===generated)?.label} generated successfully.
          </motion.p>
        )}
      </div>

      {/* Saved Reports */}
      <div className="sentinel-card">
        <SectionHeader title="Saved Reports" subtitle="Previously generated analyses" />
        <div className="space-y-2">
          {reports.map((r, i) => (
            <motion.div
              key={r.id}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.07 }}
              className="flex items-center justify-between p-3 bg-sentinel-panel rounded-lg border border-sentinel-border hover:border-sentinel-muted/30 transition-all"
            >
              <div className="flex items-center gap-3">
                <div className="p-2 bg-sentinel-border rounded-lg">
                  <FileText size={14} className="text-sentinel-muted" />
                </div>
                <div>
                  <p className="text-xs font-medium text-white">{r.title}</p>
                  <p className="text-xs text-sentinel-muted font-mono mt-0.5">
                    {new Date(r.generated_at).toLocaleDateString('en-IN', { day:'2-digit', month:'short', year:'numeric' })}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <span className={`text-[9px] font-mono px-1.5 py-0.5 rounded border ${typeColors[r.type]}`}>{r.type}</span>
                <button className="flex items-center gap-1.5 text-xs text-cyan-400 hover:text-cyan-300 transition-colors">
                  <Download size={12} /> PDF
                </button>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  )
}
