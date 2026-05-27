import React, { useState } from 'react'
import { NavLink, useLocation } from 'react-router-dom'
import {
  LayoutDashboard, Activity, Shield, Users, Network,
  BrainCircuit, FlaskConical, Globe, FileText, ChevronLeft,
} from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

const NAV_ITEMS = [
  { to: '/overview',       icon: LayoutDashboard, label: 'Executive Overview',    badge: null },
  { to: '/transactions',   icon: Activity,        label: 'Transaction Monitor',   badge: 'LIVE' },
  { to: '/fraud',          icon: Shield,          label: 'Fraud Analytics',       badge: null },
  { to: '/customers',      icon: Users,           label: 'Customer Risk',         badge: null },
  { to: '/network',        icon: Network,         label: 'Network Intelligence',  badge: null },
  { to: '/explainability', icon: BrainCircuit,    label: 'AI Explainability',     badge: null },
  { to: '/scenarios',      icon: FlaskConical,    label: 'Scenario Simulator',    badge: null },
  { to: '/sentiment',      icon: Globe,           label: 'Sentiment & Macro',     badge: null },
  { to: '/reports',        icon: FileText,        label: 'Reports',               badge: null },
]

export default function Sidebar() {
  const [collapsed, setCollapsed] = useState(false)

  return (
    <motion.aside
      animate={{ width: collapsed ? 64 : 220 }}
      transition={{ duration: 0.25, ease: 'easeInOut' }}
      className="relative flex flex-col h-full border-r border-sentinel-border bg-sentinel-surface z-20 overflow-hidden"
    >
      {/* Logo */}
      <div className="flex items-center gap-3 px-4 h-16 border-b border-sentinel-border flex-shrink-0">
        <div className="relative flex-shrink-0">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center">
            <Shield size={16} className="text-white" />
          </div>
          <span className="absolute -top-1 -right-1 w-2.5 h-2.5 bg-green-400 rounded-full border-2 border-sentinel-surface" />
        </div>
        <AnimatePresence>
          {!collapsed && (
            <motion.div
              initial={{ opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -8 }}
              transition={{ duration: 0.15 }}
              className="overflow-hidden"
            >
              <p className="font-display font-bold text-sm text-white leading-tight">FinSentinel</p>
              <p className="text-xs text-sentinel-muted font-mono">AI v1.0</p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Nav */}
      <nav className="flex-1 py-4 overflow-y-auto overflow-x-hidden">
        {NAV_ITEMS.map(({ to, icon: Icon, label, badge }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `group flex items-center gap-3 px-4 py-2.5 mx-2 mb-0.5 rounded-lg transition-all duration-150 relative
               ${isActive
                 ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20'
                 : 'text-sentinel-muted hover:text-white hover:bg-white/5'
               }`
            }
          >
            {({ isActive }) => (
              <>
                <Icon size={16} className="flex-shrink-0" />
                <AnimatePresence>
                  {!collapsed && (
                    <motion.span
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      className="text-sm font-medium whitespace-nowrap"
                    >
                      {label}
                    </motion.span>
                  )}
                </AnimatePresence>
                {badge && !collapsed && (
                  <span className="ml-auto text-[9px] font-mono font-bold bg-green-500/20 text-green-400 px-1.5 py-0.5 rounded border border-green-500/30">
                    {badge}
                  </span>
                )}
                {isActive && (
                  <motion.div
                    layoutId="active-indicator"
                    className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-4 bg-cyan-400 rounded-r"
                  />
                )}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Collapse toggle */}
      <button
        onClick={() => setCollapsed(!collapsed)}
        className="flex items-center justify-center h-10 border-t border-sentinel-border text-sentinel-muted hover:text-white transition-colors"
      >
        <motion.div animate={{ rotate: collapsed ? 180 : 0 }} transition={{ duration: 0.25 }}>
          <ChevronLeft size={16} />
        </motion.div>
      </button>
    </motion.aside>
  )
}
