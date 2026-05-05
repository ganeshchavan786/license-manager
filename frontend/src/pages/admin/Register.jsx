import React, { useState } from 'react'
import axios from 'axios'
import { useNavigate, Link } from 'react-router-dom'
import { UserPlus, User, Lock, ShieldAlert, Key } from 'lucide-react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8661'

function AdminRegister() {
  const [formData, setFormData] = useState({ 
    full_name: '', 
    username: '', 
    password: '',
    admin_key: '' // X-Admin-Key requirement
  })
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleRegister = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      await axios.post(`${API_URL}/api/auth/admin/register`, {
        full_name: formData.full_name,
        username: formData.username,
        password: formData.password
      }, {
        headers: { 'X-Admin-Key': formData.admin_key }
      })
      alert("Admin registered successfully! Please login.")
      navigate('/admin/login')
    } catch (err) {
      alert(err.response?.data?.detail || "Registration failed. Check your admin key.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center p-4">
      <div className="bg-slate-900 p-8 md:p-10 rounded-[2rem] shadow-2xl max-w-md w-full border border-slate-800">
        <div className="w-16 h-16 bg-emerald-600/10 rounded-2xl flex items-center justify-center mx-auto mb-6 border border-emerald-500/20">
          <UserPlus className="text-emerald-500" size={32} />
        </div>
        
        <h2 className="text-2xl font-black text-white mb-2 text-center">New Admin Account</h2>
        <p className="text-slate-500 text-center text-sm mb-8">Create a secure administrative user</p>

        <form onSubmit={handleRegister} className="space-y-4">
          <div className="relative">
            <User className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
            <input 
              type="text" 
              required
              placeholder="Full Name" 
              className="w-full bg-slate-800 text-white p-4 pl-12 rounded-xl border border-slate-700 focus:outline-none focus:border-indigo-500 transition-all text-sm"
              value={formData.full_name}
              onChange={(e) => setFormData({...formData, full_name: e.target.value})}
            />
          </div>

          <div className="relative">
            <User className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
            <input 
              type="text" 
              required
              placeholder="Desired Username" 
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

          <div className="relative">
            <Key className="absolute left-4 top-1/2 -translate-y-1/2 text-amber-500/50" size={18} />
            <input 
              type="password" 
              required
              placeholder="Admin Secret Key" 
              className="w-full bg-slate-800 text-white p-4 pl-12 rounded-xl border border-amber-500/20 focus:outline-none focus:border-amber-500 transition-all text-sm"
              value={formData.admin_key}
              onChange={(e) => setFormData({...formData, admin_key: e.target.value})}
            />
          </div>

          <div className="bg-amber-500/5 p-4 rounded-xl border border-amber-500/10 flex gap-3 items-start mb-6">
            <ShieldAlert className="text-amber-500 shrink-0" size={18} />
            <p className="text-[10px] text-amber-200/60 leading-relaxed uppercase tracking-wider font-bold">
              Only authorized staff can register. You need the master admin secret key to proceed.
            </p>
          </div>

          <button 
            type="submit"
            disabled={loading}
            className="w-full bg-emerald-600 text-white py-4 rounded-xl font-bold hover:bg-emerald-700 active:scale-95 transition-all shadow-lg shadow-emerald-500/20 text-sm uppercase tracking-widest"
          >
            {loading ? 'Creating Account...' : 'Register Admin'}
          </button>
        </form>

        <p className="text-slate-600 text-center text-xs mt-8">
          Already have an account? <Link to="/admin/login" className="text-indigo-400 font-bold hover:underline">Sign In</Link>
        </p>
      </div>
    </div>
  )
}

export default AdminRegister
