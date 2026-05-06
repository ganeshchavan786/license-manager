import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { useNavigate } from 'react-router-dom'
import { 
  Users, 
  CreditCard, 
  LayoutDashboard, 
  Search, 
  ShieldAlert, 
  ShieldCheck, 
  Zap, 
  Clock, 
  Banknote,
  ArrowUpRight,
  LogOut,
  RefreshCw,
  Menu,
  X,
  Tag,
  FileText,
  Download,
  Mail,
  Settings as SettingsIcon,
  BarChart3
} from 'lucide-react'
import AnalyticsDashboard from '../analytics/Dashboard'
import Settings from './Settings'
import PromoCodeManagement from './PromoCodeManagement'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8661'

function Dashboard() {
  const [activeTab, setActiveTab] = useState('overview')
  const [stats, setStats] = useState(null)
  const [customers, setCustomers] = useState([])
  const [payments, setPayments] = useState([])
  const [invoices, setInvoices] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [isAuthorized, setIsAuthorized] = useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const navigate = useNavigate()

  // JWT Token Fetch करा
  const token = localStorage.getItem('admin_token')
  const headers = { 'Authorization': `Bearer ${token}` }

  const fetchData = async () => {
    if (!token) { navigate('/admin/login'); return; }
    setLoading(true)
    try {
      const config = { headers }
      const [statsRes, custRes, payRes, invRes] = await Promise.all([
        axios.get(`${API_URL}/api/admin/stats`, config),
        axios.get(`${API_URL}/api/admin/customers`, config),
        axios.get(`${API_URL}/api/admin/payments?range=all`, config),
        axios.get(`${API_URL}/api/invoices/admin/list?limit=100`, config)
      ])
      setStats(statsRes.data)
      setCustomers(custRes.data.customers)
      setPayments(payRes.data.payments)
      setInvoices(invRes.data.invoices)
      setIsAuthorized(true)
    } catch (err) {
      if (err.response?.status === 401) {
        localStorage.removeItem('admin_token')
        navigate('/admin/login')
      } else {
        alert("Server error!")
      }
    } finally {
      setLoading(false)
    }
  }

  const toggleStatus = async (id) => {
    if (!window.confirm("Change status?")) return
    try {
      await axios.post(`${API_URL}/api/admin/customers/${id}/toggle-status`, {}, { headers })
      fetchData()
    } catch (err) { alert("Failed") }
  }

  const manualUpgrade = async (id) => {
    const months = window.prompt("Months?", "12")
    if (!months) return
    try {
      await axios.post(`${API_URL}/api/admin/customers/${id}/upgrade?plan=premium&months=${months}`, {}, { headers })
      fetchData()
    } catch (err) { alert("Failed") }
  }

  useEffect(() => {
    fetchData()
  }, [])

  if (loading && !isAuthorized) {
    return <div className="min-h-screen bg-slate-50 flex items-center justify-center font-bold text-slate-400 uppercase tracking-widest text-xs">Loading Dashboard...</div>
  }

  const filteredCustomers = customers.filter(c => 
    c.business_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    c.email.toLowerCase().includes(searchTerm.toLowerCase())
  )

  return (
    <div className="min-h-screen bg-[#F8FAFC] flex flex-col lg:flex-row text-[11px]">
      {/* Mobile Header */}
      <div className="lg:hidden bg-white border-b border-slate-200 p-2 flex justify-between items-center sticky top-0 z-50">
        <div className="flex items-center gap-1.5">
          <Zap className="text-indigo-600" size={14} fill="currentColor" />
          <span className="font-black text-slate-900">SalaryPay</span>
        </div>
        <button onClick={() => setMobileMenuOpen(!mobileMenuOpen)} className="p-1 text-slate-600">
          {mobileMenuOpen ? <X size={16} /> : <Menu size={16} />}
        </button>
      </div>

      {/* Sidebar Overlay */}
      <div className={`fixed inset-0 bg-slate-900/30 z-40 lg:hidden transition-opacity ${mobileMenuOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'}`} onClick={() => setMobileMenuOpen(false)} />

      {/* Sidebar */}
      <div className={`fixed inset-y-0 left-0 w-44 bg-white border-r border-slate-200 p-4 flex flex-col z-50 transition-transform lg:static lg:translate-x-0 ${mobileMenuOpen ? 'translate-x-0' : '-translate-x-full'}`}>
        <div className="hidden lg:flex items-center gap-2 mb-6">
          <Zap className="text-indigo-600" size={14} fill="currentColor" />
          <span className="text-sm font-black text-slate-900 tracking-tighter uppercase">SALARYPAY</span>
        </div>

        <nav className="space-y-0.5 flex-1">
          <NavItem active={activeTab === 'overview'} icon={<LayoutDashboard size={14}/>} label="Dashboard" onClick={()=>{setActiveTab('overview'); setMobileMenuOpen(false)}} />
          <NavItem active={activeTab === 'customers'} icon={<Users size={14}/>} label="Customers" onClick={()=>{setActiveTab('customers'); setMobileMenuOpen(false)}} />
          <NavItem active={activeTab === 'payments'} icon={<CreditCard size={14}/>} label="Payments" onClick={()=>{setActiveTab('payments'); setMobileMenuOpen(false)}} />
          <NavItem active={activeTab === 'invoices'} icon={<FileText size={14}/>} label="Invoices" onClick={()=>{setActiveTab('invoices'); setMobileMenuOpen(false)}} />
          <NavItem active={activeTab === 'analytics'} icon={<BarChart3 size={14}/>} label="Analytics" onClick={()=>{setActiveTab('analytics'); setMobileMenuOpen(false)}} />
          <NavItem active={activeTab === 'promos'} icon={<Tag size={14}/>} label="Promo Codes" onClick={()=>{setActiveTab('promos'); setMobileMenuOpen(false)}} />
          <NavItem active={activeTab === 'settings'} icon={<SettingsIcon size={14}/>} label="Settings" onClick={()=>{setActiveTab('settings'); setMobileMenuOpen(false)}} />
        </nav>

        <button onClick={() => { localStorage.removeItem('admin_token'); navigate('/'); }} className="mt-auto flex items-center gap-1.5 text-slate-400 hover:text-red-500 font-bold text-[10px] uppercase">
          <LogOut size={14} /> Logout
        </button>
      </div>

      {/* Main Content */}
      <div className="flex-1 p-3 md:p-5 overflow-y-auto">
        <div className="max-w-4xl mx-auto">
          
          <header className="flex justify-between items-center mb-4">
            <h1 className="text-sm font-black text-slate-900 uppercase tracking-widest">
              {activeTab === 'overview' ? 'Dashboard' : 
               activeTab === 'customers' ? 'Customers' : 
               activeTab === 'invoices' ? 'Invoices' : 
               activeTab === 'analytics' ? 'Analytics' :
               activeTab === 'promos' ? 'Promo Codes' :
               activeTab === 'settings' ? 'Settings' :
               'Payments'}
            </h1>
            {activeTab !== 'analytics' && activeTab !== 'settings' && activeTab !== 'promos' && (
              <button onClick={() => fetchData()} className="p-1.5 bg-white border border-slate-200 rounded-md hover:bg-slate-50 shadow-sm">
                <RefreshCw size={12} className={`text-slate-600 ${loading ? 'animate-spin' : ''}`} />
              </button>
            )}
          </header>

          {activeTab === 'overview' && (
            <>
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-4">
                <StatCard title="Total" value={stats?.total_customers} icon={<Users/>} color="blue" />
                <StatCard title="Trials" value={stats?.active_trials} icon={<Clock/>} color="amber" />
                <StatCard title="Premium" value={stats?.premium_plan} icon={<Zap/>} color="emerald" />
                <StatCard title="Revenue" value={`₹${(stats?.revenue_total / 100).toLocaleString()}`} icon={<Banknote/>} color="indigo" />
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                <div className="lg:col-span-2 bg-white rounded-xl shadow-sm border border-slate-200/50 p-4">
                  <h3 className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-3">Recent activity</h3>
                  <div className="space-y-1">
                    {stats?.recent_registrations.map((reg, i) => (
                      <div key={i} className="flex justify-between items-center p-2 hover:bg-slate-50 rounded-lg">
                        <div className="flex gap-2 items-center">
                          <div className="w-6 h-6 bg-slate-100 rounded flex items-center justify-center text-slate-400 font-bold text-[9px]">
                            {reg.business_name[0]}
                          </div>
                          <div>
                            <p className="font-bold text-slate-700 text-[10px] leading-tight">{reg.business_name}</p>
                            <p className="text-[9px] text-slate-400 leading-tight">{reg.email}</p>
                          </div>
                        </div>
                        <p className="text-[9px] font-bold text-slate-300">{new Date(reg.created_at).toLocaleDateString()}</p>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="bg-indigo-600 rounded-xl p-5 text-white flex flex-col justify-between shadow-lg shadow-indigo-100">
                  <div className="mb-4 text-center">
                    <p className="text-indigo-200 text-[9px] uppercase tracking-widest font-bold mb-0.5">Conversion</p>
                    <p className="text-3xl font-black">{stats?.conversion_rate}%</p>
                  </div>
                  <div className="text-center">
                    <p className="text-indigo-200 text-[9px] uppercase tracking-widest font-bold mb-0.5">ARPU</p>
                    <p className="text-xl font-black">₹{stats?.arpu / 100}</p>
                  </div>
                </div>
              </div>
            </>
          )}

          {activeTab === 'customers' && (
            <div className="bg-white rounded-xl shadow-sm border border-slate-200/50 p-4">
              <div className="mb-4 relative">
                <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-400" size={12} />
                <input 
                  type="text" 
                  placeholder="Search..." 
                  className="w-full bg-slate-50 border border-slate-200 p-1.5 pl-8 rounded-lg focus:outline-none focus:border-indigo-500 text-[10px]"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>

              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="text-left text-slate-400 text-[9px] uppercase tracking-wider border-b border-slate-50">
                    <tr>
                      <th className="pb-2">Business</th>
                      <th className="pb-2">Joined</th>
                      <th className="pb-2">Plan</th>
                      <th className="pb-2">Status</th>
                      <th className="pb-2 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-50">
                    {filteredCustomers.map((c) => (
                      <tr key={c.id} className="text-[10px] hover:bg-slate-50/50">
                        <td className="py-2 font-bold text-slate-700">{c.business_name} <br/><span className="font-normal text-[9px] text-slate-400">{c.email}</span></td>
                        <td className="py-2 text-slate-500">{new Date(c.created_at).toLocaleDateString()}</td>
                        <td className="py-2">
                          <span className={`px-1.5 py-0.5 rounded text-[8px] font-bold uppercase ${c.plan === 'premium' ? 'bg-emerald-100 text-emerald-700' : 'bg-blue-100 text-blue-700'}`}>{c.plan}</span>
                        </td>
                        <td className="py-2">
                          <button onClick={() => toggleStatus(c.id)} className={`font-bold ${c.is_active ? 'text-emerald-500' : 'text-red-500'}`}>
                            {c.is_active ? 'Active' : 'Blocked'}
                          </button>
                        </td>
                        <td className="py-2 text-right">
                          <button onClick={() => manualUpgrade(c.id)} className="bg-indigo-50 text-indigo-600 px-2 py-0.5 rounded font-bold hover:bg-indigo-600 hover:text-white uppercase">Upgrade</button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {activeTab === 'payments' && (
            <div className="bg-white rounded-xl shadow-sm border border-slate-200/50 p-4">
               <div className="overflow-x-auto text-[10px]">
                <table className="w-full">
                  <thead className="text-left text-slate-400 text-[9px] uppercase tracking-wider border-b border-slate-50">
                    <tr>
                      <th className="pb-2">Business</th>
                      <th className="pb-2">Amount</th>
                      <th className="pb-2">Status</th>
                      <th className="pb-2 text-right">Date</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-50">
                    {payments.map((p) => (
                      <tr key={p.id} className="hover:bg-slate-50/50">
                        <td className="py-2 font-bold text-slate-700">{p.business_name}</td>
                        <td className="py-2 font-black">₹{p.amount / 100}</td>
                        <td className="py-2"><span className={`px-1 py-0.5 rounded text-[8px] font-bold uppercase ${p.status === 'captured' ? 'bg-emerald-100 text-emerald-700' : 'bg-red-100 text-red-700'}`}>{p.status}</span></td>
                        <td className="py-2 text-slate-400 text-right">{new Date(p.created_at).toLocaleDateString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {activeTab === 'invoices' && (
            <div className="bg-white rounded-xl shadow-sm border border-slate-200/50 p-4">
              <div className="overflow-x-auto text-[10px]">
                <table className="w-full">
                  <thead className="text-left text-slate-400 text-[9px] uppercase tracking-wider border-b border-slate-50">
                    <tr>
                      <th className="pb-2">Invoice #</th>
                      <th className="pb-2">Customer</th>
                      <th className="pb-2">Plan</th>
                      <th className="pb-2">Amount</th>
                      <th className="pb-2">Date</th>
                      <th className="pb-2 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-50">
                    {invoices.map((inv) => (
                      <tr key={inv.id} className="hover:bg-slate-50/50">
                        <td className="py-2">
                          <div className="flex items-center gap-2">
                            <FileText size={14} className="text-indigo-600" />
                            <span className="font-bold text-slate-700">{inv.invoice_number}</span>
                          </div>
                        </td>
                        <td className="py-2 text-slate-600 text-[9px]">{inv.id.slice(0, 8)}...</td>
                        <td className="py-2">
                          <span className={`px-1.5 py-0.5 rounded text-[8px] font-bold uppercase ${inv.plan === 'premium' ? 'bg-purple-100 text-purple-700' : 'bg-blue-100 text-blue-700'}`}>
                            {inv.plan}
                          </span>
                        </td>
                        <td className="py-2">
                          <div>
                            <p className="font-black text-slate-900">₹{inv.total_amount / 100}</p>
                            {inv.discount_amount > 0 && (
                              <p className="text-[8px] text-emerald-600">-₹{inv.discount_amount / 100} off</p>
                            )}
                          </div>
                        </td>
                        <td className="py-2 text-slate-500">{new Date(inv.invoice_date).toLocaleDateString()}</td>
                        <td className="py-2 text-right">
                          <div className="flex items-center justify-end gap-1">
                            {inv.pdf_available && (
                              <button 
                                onClick={async () => {
                                  try {
                                    const response = await axios.get(
                                      `${API_URL}/api/invoices/admin/${inv.id}/download`,
                                      { headers, responseType: 'blob' }
                                    )
                                    const url = window.URL.createObjectURL(new Blob([response.data]))
                                    const link = document.createElement('a')
                                    link.href = url
                                    link.setAttribute('download', `${inv.invoice_number}.pdf`)
                                    document.body.appendChild(link)
                                    link.click()
                                    link.remove()
                                    window.URL.revokeObjectURL(url)
                                  } catch (err) {
                                    alert('Failed to download invoice')
                                  }
                                }}
                                className="p-1 bg-indigo-50 text-indigo-600 rounded hover:bg-indigo-100"
                                title="Download PDF"
                              >
                                <Download size={12} />
                              </button>
                            )}
                            <button 
                              className={`p-1 rounded ${inv.is_emailed ? 'bg-emerald-50 text-emerald-600' : 'bg-slate-50 text-slate-400'}`}
                              title={inv.is_emailed ? 'Emailed' : 'Not Emailed'}
                            >
                              <Mail size={12} />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              
              {invoices.length === 0 && (
                <div className="text-center py-12">
                  <FileText className="mx-auto text-slate-300 mb-3" size={48} />
                  <p className="text-slate-500 font-bold text-sm">No invoices yet</p>
                  <p className="text-slate-400 text-xs mt-1">Invoices will appear here after payments</p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'analytics' && (
            <div className="bg-white rounded-xl shadow-sm border border-slate-200/50 p-4">
              <AnalyticsDashboard />
            </div>
          )}

          {activeTab === 'promos' && (
            <PromoCodeManagement />
          )}

          {activeTab === 'settings' && (
            <Settings />
          )}

        </div>
      </div>
    </div>
  )
}

function NavItem({ active, icon, label, onClick }) {
  return (
    <button onClick={onClick} className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg font-bold text-[10px] uppercase tracking-tight transition-all ${active ? 'bg-indigo-50 text-indigo-600' : 'text-slate-400 hover:bg-slate-50 hover:text-slate-900'}`}>
      {icon} <span>{label}</span>
    </button>
  )
}

function StatCard({ title, value, icon, color }) {
  const colors = {
    blue: 'bg-blue-500/10 text-blue-600',
    amber: 'bg-amber-500/10 text-amber-600',
    emerald: 'bg-emerald-500/10 text-emerald-600',
    indigo: 'bg-indigo-500/10 text-indigo-600'
  }
  return (
    <div className="bg-white p-3 rounded-xl shadow-sm border border-slate-200/50">
      <div className={`w-7 h-7 ${colors[color]} rounded-lg flex items-center justify-center mb-2`}>
        {React.cloneElement(icon, { size: 14 })}
      </div>
      <p className="text-slate-400 text-[8px] font-bold uppercase tracking-widest">{title}</p>
      <p className="text-sm font-black text-slate-900 mt-0">{value}</p>
    </div>
  )
}

export default Dashboard
