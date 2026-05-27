import React from 'react'
import { motion } from 'framer-motion'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { clsx } from 'clsx'

export default function KPICard({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,        // number: positive=up, negative=down
  trendLabel,
  color = 'cyan',
  format = 'number',
  delay = 0,
}) {
  const colorMap = {
    cyan:   { bg: 'bg-cyan-500/10',   text: 'text-cyan-400',   border: 'border-cyan-500/20',   glow: 'shadow-cyan-500/10' },
    red:    { bg: 'bg-red-500/10',    text: 'text-red-400',    border: 'border-red-500/20',    glow: 'shadow-red-500/10' },
    green:  { bg: 'bg-emerald-500/10',text: 'text-emerald-400',border: 'border-emerald-500/20',glow: 'shadow-emerald-500/10' },
    yellow: { bg: 'bg-yellow-500/10', text: 'text-yellow-400', border: 'border-yellow-500/20', glow: 'shadow-yellow-500/10' },
    purple: { bg: 'bg-purple-500/10', text: 'text-purple-400', border: 'border-purple-500/20', glow: 'shadow-purple-500/10' },
    orange: { bg: 'bg-orange-500/10', text: 'text-orange-400', border: 'border-orange-500/20', glow: 'shadow-orange-500/10' },
  }
  const c = colorMap[color] || colorMap.cyan

  const formatValue = (v) => {
    if (v === undefined || v === null) return '—'
    switch (format) {
      case 'currency': return `₹${v >= 1e7 ? (v/1e7).toFixed(1)+'Cr' : v >= 1e5 ? (v/1e5).toFixed(1)+'L' : v.toLocaleString('en-IN')}`
      case 'percent':  return `${typeof v === 'number' ? v.toFixed(2) : v}%`
      case 'compact':  return v >= 1e6 ? (v/1e6).toFixed(1)+'M' : v >= 1e3 ? (v/1e3).toFixed(1)+'K' : v.toLocaleString()
      default:         return typeof v === 'number' ? v.toLocaleString('en-IN') : v
    }
  }

  const TrendIcon = trend > 0 ? TrendingUp : trend < 0 ? TrendingDown : Minus
  const trendColor = trend > 0 ? 'text-red-400' : trend < 0 ? 'text-emerald-400' : 'text-sentinel-muted'

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay }}
      className={clsx(
        'sentinel-card border shadow-lg',
        c.border,
        c.glow
      )}
    >
      <div className="flex items-start justify-between mb-3">
        <div className={clsx('p-2 rounded-lg', c.bg)}>
          {Icon && <Icon size={16} className={c.text} />}
        </div>
        {trend !== undefined && (
          <div className={clsx('flex items-center gap-1 text-xs', trendColor)}>
            <TrendIcon size={12} />
            <span className="font-mono">{Math.abs(trend).toFixed(1)}%</span>
          </div>
        )}
      </div>

      <div className="mt-1">
        <p className="text-2xl font-display font-bold text-white count-up">
          {formatValue(value)}
        </p>
        <p className="text-xs text-sentinel-muted mt-1">{title}</p>
        {subtitle && (
          <p className="text-xs text-sentinel-muted/60 mt-0.5">{subtitle}</p>
        )}
        {trendLabel && (
          <p className={clsx('text-xs mt-1', trendColor)}>{trendLabel}</p>
        )}
      </div>
    </motion.div>
  )
}
