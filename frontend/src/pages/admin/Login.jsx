import React, { useState } from 'react'
import axios from 'axios'
import { useNavigate, Link } from 'react-router-dom'
import { ShieldCheck, Lock, User } from 'lucide-react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8661'

function AdminLogin() {
  const [formData, setFormData] = useState({ username: '', password: '' })
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleLogin = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const { data } = await axios.post(`${API_URL}/api/auth/admin/login`, formData)
      localStorage.setItem('admin_token', data.access_token)
      localStorage.setItem('admin_user', JSON.stringify(data))
      navigate('/admin')
    } catch (err) {
      alert("Invalid username or password!")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center p-4">
      <div className="bg-slate-900 p-8 md:p-10 rounded-[2rem] shadow-2xl max-w-md w-full border border-slate-800">
        <div className="w-16 h-16 bg-indigo-600/10 rounded-2xl flex items-center justify-center mx-auto mb-6 border border-indigo-500/20">
          <ShieldCheck className="text-indigo-500" size={32} />
        </div>
        
        <h2 className="text-2xl font-black text-white mb-2 text-center">Admin Access</h2>
        <p className="text-slate-500 text-center text-sm mb-8">Manage SalaryPay licensing system</p>

        <form onSubmit={handleLogin} className="space-y-4">
          <div className="relative">
            <User className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
            <input 
              type="text" 
              required
              placeholder="Username" 
              className="w-full bg-slate-800 text-white p-4 pl-12 rounded-xl border border-slate-700 focus:outline-none focus:border-indigo-500 transition-all text-sm"
              value={formData.username}
              onChange={(e) => setFormData({...formData, username: e.target.value})}
            />
          </div>
          
          <div className="relative">
            <Lock className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
            <input 
              type="password" 
              required
              placeholder="Password" 
              className="w-full bg-slate-800 text-white p-4 pl-12 rounded-xl border border-slate-700 focus:outline-none focus:border-indigo-500 transition-all text-sm"
              value={formData.password}
              onChange={(e) => setFormData({...formData, password: e.target.value})}
            />
          </div>

          <button 
            type="submit"
            disabled={loading}
            className="w-full bg-indigo-600 text-white py-4 rounded-xl font-bold hover:bg-indigo-700 active:scale-95 transition-all shadow-lg shadow-indigo-500/20 text-sm uppercase tracking-widest"
          >
            {loading ? 'Authenticating...' : 'Sign In'}
          </button>
        </form>

        <p className="text-slate-600 text-center text-xs mt-8">
          Don't have an account? <Link to="/admin/register" className="text-indigo-400 font-bold hover:underline">Register here</Link>
        </p>
      </div>
    </div>
  )
}

export default AdminLogin
