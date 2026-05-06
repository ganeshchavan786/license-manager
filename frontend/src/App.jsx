import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { LicenseProvider } from './context/LicenseContext'
import Register from './pages/subscription/Register'
import Plans from './pages/subscription/Plans'
import Checkout from './pages/subscription/Checkout'
import Dashboard from './pages/admin/Dashboard'
import Home from './pages/Home'
import AdminLogin from './pages/admin/Login'
import AdminRegister from './pages/admin/Register'
import PromoCodeManagement from './pages/admin/PromoCodeManagement'
import InvoiceList from './pages/invoices/InvoiceList'
import Settings from './pages/admin/Settings'
import AnalyticsDashboard from './pages/analytics/Dashboard'

function App() {
  return (
    <LicenseProvider>
      <Router>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/register" element={<Register />} />
          <Route path="/plans" element={<Plans />} />
          <Route path="/checkout" element={<Checkout />} />
          <Route path="/invoices" element={<InvoiceList />} />
          <Route path="/analytics" element={<AnalyticsDashboard />} />
          
          {/* Admin Routes */}
          <Route path="/admin" element={<Dashboard />} />
          <Route path="/admin/login" element={<AdminLogin />} />
          <Route path="/admin/register" element={<AdminRegister />} />
          <Route path="/admin/promo-codes" element={<PromoCodeManagement />} />
          <Route path="/admin/settings" element={<Settings />} />
          <Route path="/admin/analytics" element={<AnalyticsDashboard />} />
        </Routes>
      </Router>
    </LicenseProvider>
  )
}

export default App
