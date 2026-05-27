import React, { useState, useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import { Bell, Search, RefreshCw, Wifi } from 'lucide-react'

const PAGE_TITLES = {
  '/overview':       'Executive Overview',
  '/transactions':   'Transaction Monitor',
  '/fraud':          'Fraud Analytics',
  '/customers':      'Customer Risk Intelligence',
  '/network':        'Network Intelligence',
  '/explainability': 'AI Explainability',
  '/scenarios':      'Scenario Simulator',
  '/sentiment':      'Sentiment & Macro',
  '/reports':        'Reports',
}

export default function Header() {
  const location = useLocation()
  const [time, setTime] = useState(new Date())
  const [alerts] = useState(3)

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000)
    return () => clearInterval(timer)
  }, [])

  return (
    <header className="h-16 flex items-center justify-between px-6 border-b border-sentinel-border bg-sentinel-surface/50 backdrop-blur-sm flex-shrink-0">
      {/* Title */}
      <div>
        <h1 className="font-display font-bold text-lg text-white">
          {PAGE_TITLES[location.pathname] || 'Dashboard'}
        </h1>
        <div className="flex items-center gap-2 mt-0.5">
          <div className="flex items-center gap-1.5">
            <div className="relative">
              <div className="w-1.5 h-1.5 bg-green-400 rounded-full" />
              <div className="absolute inset-0 w-1.5 h-1.5 bg-green-400 rounded-full animate-ping opacity-75" />
            </div>
            <span className="text-xs text-green-400 font-mono">LIVE</span>
          </div>
          <span className="text-sentinel-muted text-xs font-mono">
            {time.toLocaleTimeString('en-IN', { hour12: false })} IST
          </span>
          <Wifi size={10} className="text-sentinel-muted" />
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-3">
        {/* Search */}
        <div className="relative hidden md:flex items-center">
          <Search size={14} className="absolute left-3 text-sentinel-muted" />
          <input
            type="text"
            placeholder="Search transactions..."
            className="pl-8 pr-4 py-1.5 text-sm bg-sentinel-panel border border-sentinel-border rounded-lg text-sentinel-text placeholder-sentinel-muted focus:outline-none focus:border-cyan-500/50 w-48 transition-all focus:w-64"
          />
        </div>

        {/* Refresh */}
        <button className="p-2 rounded-lg border border-sentinel-border bg-sentinel-panel text-sentinel-muted hover:text-white hover:border-cyan-500/30 transition-all">
          <RefreshCw size={14} />
        </button>

        {/* Notifications */}
        <button className="relative p-2 rounded-lg border border-sentinel-border bg-sentinel-panel text-sentinel-muted hover:text-white hover:border-cyan-500/30 transition-all">
          <Bell size={14} />
          {alerts > 0 && (
            <span className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 rounded-full text-[9px] font-bold text-white flex items-center justify-center">
              {alerts}
            </span>
          )}
        </button>

        {/* User Avatar */}
        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center text-white text-xs font-bold cursor-pointer border border-cyan-500/30">
          FS
        </div>
      </div>
    </header>
  )
}
