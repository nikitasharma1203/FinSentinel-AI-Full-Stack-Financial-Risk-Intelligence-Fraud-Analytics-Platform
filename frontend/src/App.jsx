import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import Sidebar from './components/dashboard/Sidebar'
import Header from './components/dashboard/Header'
import ExecutiveOverview from './pages/ExecutiveOverview'
import TransactionMonitor from './pages/TransactionMonitor'
import FraudAnalytics from './pages/FraudAnalytics'
import CustomerRisk from './pages/CustomerRisk'
import NetworkIntelligence from './pages/NetworkIntelligence'
import Explainability from './pages/Explainability'
import ScenarioSimulator from './pages/ScenarioSimulator'
import SentimentDashboard from './pages/SentimentDashboard'
import Reports from './pages/Reports'

export default function App() {
  return (
    <div className="flex h-screen bg-sentinel-bg overflow-hidden">
      <Sidebar />
      <div className="flex flex-col flex-1 overflow-hidden">
        <Header />
        <main className="flex-1 overflow-auto p-6">
          <Routes>
            <Route path="/" element={<Navigate to="/overview" replace />} />
            <Route path="/overview"      element={<ExecutiveOverview />} />
            <Route path="/transactions"  element={<TransactionMonitor />} />
            <Route path="/fraud"         element={<FraudAnalytics />} />
            <Route path="/customers"     element={<CustomerRisk />} />
            <Route path="/network"       element={<NetworkIntelligence />} />
            <Route path="/explainability"element={<Explainability />} />
            <Route path="/scenarios"     element={<ScenarioSimulator />} />
            <Route path="/sentiment"     element={<SentimentDashboard />} />
            <Route path="/reports"       element={<Reports />} />
          </Routes>
        </main>
      </div>
    </div>
  )
}
