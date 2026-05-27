import React from 'react'
import { clsx } from 'clsx'

export function RiskBadge({ level, size = 'sm' }) {
  const classes = {
    LOW:      'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
    MEDIUM:   'bg-yellow-500/10  text-yellow-400  border-yellow-500/30',
    HIGH:     'bg-orange-500/10  text-orange-400  border-orange-500/30',
    CRITICAL: 'bg-red-500/10     text-red-400     border-red-500/30',
  }
  const sz = size === 'xs' ? 'text-[9px] px-1.5 py-0.5' : 'text-xs px-2 py-0.5'
  return (
    <span className={clsx('rounded border font-mono font-bold tracking-wider', sz, classes[level] || classes.LOW)}>
      {level}
    </span>
  )
}

export function SectionHeader({ title, subtitle, action }) {
  return (
    <div className="flex items-center justify-between mb-4">
      <div>
        <h2 className="font-display font-bold text-white text-base">{title}</h2>
        {subtitle && <p className="text-xs text-sentinel-muted mt-0.5">{subtitle}</p>}
      </div>
      {action}
    </div>
  )
}

export function LoadingSpinner({ size = 20 }) {
  return (
    <div className="flex items-center justify-center p-8">
      <div
        className="border-2 border-sentinel-border border-t-cyan-500 rounded-full animate-spin"
        style={{ width: size, height: size }}
      />
    </div>
  )
}

export function EmptyState({ message = 'No data available' }) {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-sentinel-muted">
      <div className="w-12 h-12 rounded-full bg-sentinel-panel border border-sentinel-border flex items-center justify-center mb-3">
        <span className="text-xl">📭</span>
      </div>
      <p className="text-sm">{message}</p>
    </div>
  )
}

export function StatRow({ label, value, highlight }) {
  return (
    <div className="flex items-center justify-between py-2 border-b border-sentinel-border/50 last:border-0">
      <span className="text-xs text-sentinel-muted">{label}</span>
      <span className={clsx('text-xs font-mono font-medium', highlight ? 'text-cyan-400' : 'text-sentinel-text')}>
        {value}
      </span>
    </div>
  )
}

export function ProbabilityBar({ value, max = 1 }) {
  const pct = Math.min((value / max) * 100, 100)
  const color = pct > 85 ? 'bg-red-500' : pct > 60 ? 'bg-orange-500' : pct > 30 ? 'bg-yellow-500' : 'bg-emerald-500'
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-1.5 bg-sentinel-border rounded-full overflow-hidden">
        <div className={clsx('h-full rounded-full transition-all duration-500', color)} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-xs font-mono text-sentinel-muted w-10 text-right">{(value * 100).toFixed(1)}%</span>
    </div>
  )
}

export function TabGroup({ tabs, active, onChange }) {
  return (
    <div className="flex gap-1 p-1 bg-sentinel-panel rounded-lg border border-sentinel-border">
      {tabs.map(tab => (
        <button
          key={tab.value}
          onClick={() => onChange(tab.value)}
          className={clsx(
            'px-3 py-1.5 rounded text-xs font-medium transition-all',
            active === tab.value
              ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20'
              : 'text-sentinel-muted hover:text-white'
          )}
        >
          {tab.label}
        </button>
      ))}
    </div>
  )
}
