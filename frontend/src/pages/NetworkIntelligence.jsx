import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { Network, AlertTriangle, GitBranch } from 'lucide-react'
import { SectionHeader, StatRow } from '../components/dashboard/UIElements'
import KPICard from '../components/dashboard/KPICard'

// Synthetic network data
const NODES = Array.from({ length: 30 }, (_, i) => ({
  id: `N${i}`,
  type: i < 20 ? 'CUSTOMER' : 'MERCHANT',
  risk: Math.random(),
  x: 50 + Math.random() * 400,
  y: 50 + Math.random() * 250,
}))

const EDGES = Array.from({ length: 40 }, (_, i) => ({
  source: `N${Math.floor(Math.random() * 20)}`,
  target: `N${20 + Math.floor(Math.random() * 10)}`,
  risk: Math.random(),
  suspicious: Math.random() > 0.75,
}))

const CLUSTERS = [
  { cluster_id: 0, size: 12, risk_level: 'CRITICAL', nodes: NODES.slice(0, 12).map(n => n.id) },
  { cluster_id: 1, size: 7,  risk_level: 'HIGH',     nodes: NODES.slice(5, 12).map(n => n.id) },
  { cluster_id: 2, size: 4,  risk_level: 'MEDIUM',   nodes: NODES.slice(15, 19).map(n => n.id) },
]

const riskColor = (r) => r > 0.75 ? '#FF3B5C' : r > 0.5 ? '#FF8C00' : r > 0.25 ? '#FFB020' : '#00E5A0'
const tierBg = { CRITICAL: 'bg-red-500/10 border-red-500/30 text-red-400', HIGH: 'bg-orange-500/10 border-orange-500/30 text-orange-400', MEDIUM: 'bg-yellow-500/10 border-yellow-500/30 text-yellow-400' }

export default function NetworkIntelligence() {
  const [selectedNode, setSelectedNode] = useState(null)

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <KPICard title="Total Nodes"       value={NODES.length}  icon={Network}       color="cyan"   format="number" delay={0} />
        <KPICard title="Suspicious Edges"  value={EDGES.filter(e=>e.suspicious).length} icon={AlertTriangle} color="red" format="number" delay={0.05} />
        <KPICard title="Fraud Clusters"    value={CLUSTERS.length} icon={GitBranch}    color="orange" format="number" delay={0.1} />
        <KPICard title="Critical Cluster"  value={CLUSTERS[0].size} icon={Network}     color="red"    format="number" delay={0.15} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* SVG Graph */}
        <div className="lg:col-span-2 sentinel-card">
          <SectionHeader title="Transaction Network Graph" subtitle="Customer → Merchant edges — red = suspicious" />
          <div className="relative bg-sentinel-panel rounded-lg border border-sentinel-border overflow-hidden" style={{ height: 340 }}>
            <svg width="100%" height="100%" viewBox="0 0 500 320" className="w-full h-full">
              {/* Edges */}
              {EDGES.map((e, i) => {
                const src = NODES.find(n => n.id === e.source)
                const tgt = NODES.find(n => n.id === e.target)
                if (!src || !tgt) return null
                return (
                  <line key={i}
                    x1={src.x} y1={src.y} x2={tgt.x} y2={tgt.y}
                    stroke={e.suspicious ? '#FF3B5C' : '#1F2937'}
                    strokeWidth={e.suspicious ? 1.5 : 0.8}
                    strokeOpacity={e.suspicious ? 0.6 : 0.4}
                    strokeDasharray={e.suspicious ? '4 2' : undefined}
                  />
                )
              })}
              {/* Nodes */}
              {NODES.map(n => (
                <g key={n.id} onClick={() => setSelectedNode(n)} style={{ cursor: 'pointer' }}>
                  <circle
                    cx={n.x} cy={n.y}
                    r={n.type === 'MERCHANT' ? 10 : 7}
                    fill={riskColor(n.risk)}
                    fillOpacity={0.8}
                    stroke={selectedNode?.id === n.id ? '#00D4FF' : 'transparent'}
                    strokeWidth={2}
                  />
                  {n.risk > 0.75 && (
                    <circle cx={n.x} cy={n.y} r={14} fill="none" stroke="#FF3B5C" strokeWidth={1} opacity={0.4}>
                      <animate attributeName="r" values="10;16;10" dur="2s" repeatCount="indefinite" />
                      <animate attributeName="opacity" values="0.4;0;0.4" dur="2s" repeatCount="indefinite" />
                    </circle>
                  )}
                  <text x={n.x + 9} y={n.y + 3} fontSize={7} fill="#6B7280">{n.id}</text>
                </g>
              ))}
            </svg>
            {/* Legend */}
            <div className="absolute bottom-3 left-3 flex items-center gap-4 text-[10px] text-sentinel-muted">
              <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-emerald-400 inline-block" /> Low Risk</span>
              <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-yellow-400 inline-block" /> Medium</span>
              <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-red-400 inline-block" /> High/Critical</span>
              <span className="flex items-center gap-1"><span className="w-4 border-t border-dashed border-red-400 inline-block" /> Suspicious</span>
            </div>
          </div>
        </div>

        {/* Clusters + Node Detail */}
        <div className="space-y-4">
          <div className="sentinel-card">
            <SectionHeader title="Fraud Clusters" subtitle="Detected suspicious groups" />
            <div className="space-y-2">
              {CLUSTERS.map(c => (
                <div key={c.cluster_id} className={`p-3 rounded-lg border text-xs ${tierBg[c.risk_level]}`}>
                  <div className="flex justify-between">
                    <span className="font-semibold">Cluster #{c.cluster_id}</span>
                    <span>{c.size} nodes</span>
                  </div>
                  <p className="text-sentinel-muted mt-1 font-mono text-[10px]">{c.nodes.slice(0,6).join(', ')}…</p>
                </div>
              ))}
            </div>
          </div>

          {selectedNode && (
            <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="sentinel-card">
              <SectionHeader title="Node Details" />
              <StatRow label="Node ID"    value={selectedNode.id} highlight />
              <StatRow label="Type"       value={selectedNode.type} />
              <StatRow label="Risk Score" value={`${(selectedNode.risk * 100).toFixed(1)}%`} highlight />
              <div className="mt-3 h-1.5 bg-sentinel-border rounded-full overflow-hidden">
                <div className="h-full rounded-full transition-all" style={{ width: `${selectedNode.risk*100}%`, background: riskColor(selectedNode.risk) }} />
              </div>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  )
}
