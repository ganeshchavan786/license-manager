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

function App() {
  return (
    <LicenseProvider>
      <Router>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/register" element={<Register />} />
          <Route path="/plans" element={<Plans />} />
          <Route path="/checkout" element={<Checkout />} />
          
          {/* Admin Routes */}
          <Route path="/admin" element={<Dashboard />} />
          <Route path="/admin/login" element={<AdminLogin />} />
          <Route path="/admin/register" element={<AdminRegister />} />
        </Routes>
      </Router>
    </LicenseProvider>
  )
}

export default App
