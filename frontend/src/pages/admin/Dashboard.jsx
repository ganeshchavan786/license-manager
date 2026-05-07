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
  BarChart3,
  Calendar,
  AlertTriangle,
  CheckCircle,
  ChevronRight,
  Phone,
  MapPin,
  User,
  Receipt
} from 'lucide-react'
import AnalyticsDashboard from '../analytics/Dashboard'
import Settings from './Settings'
import PromoCodeManagement from './PromoCodeManagement'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8661'

const PLAN_PRICES = { basic: 499, premium: 999 }
const GRACE_PERIOD_DAYS = { basic: 15, premium: 30, trial: 15, free: 15 }

// ─── Upgrade Modal ────────────────────────────────────────────────────────────
function UpgradeModal({ upgradeModal, setUpgradeModal, headers, fetchData }) {
  const { open, customer, plan, months } = upgradeModal
  const [loading, setLoading] = useState(false)
  const [successMsg, setSuccessMsg] = useState('')

  if (!open || !customer) return null

  const price = PLAN_PRICES[plan] || 0
  const total = price * months

  const currentExpiry = customer.valid_till ? new Date(customer.valid_till) : null
  const now = new Date()
  const base = currentExpiry && currentExpiry > now ? currentExpiry : now
  const newExpiry = new Date(base)
  newExpiry.setDate(newExpiry.getDate() + months * 30)

  const fmtDate = (d) => d ? d.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' }) : '—'

  const handleConfirm = async () => {
    setLoading(true)
    try {
      await axios.post(
        `${API_URL}/api/admin/customers/${customer.id}/upgrade?plan=${plan}&months=${months}`,
        {},
        { headers }
      )
      setSuccessMsg('Upgraded successfully!')
      setTimeout(() => {
        setSuccessMsg('')
        setUpgradeModal({ open: false, customer: null, plan: 'basic', months: 1 })
        fetchData()
      }, 1500)
    } catch (err) {
      alert('Upgrade failed: ' + (err.response?.data?.detail || err.message))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-slate-900/40 z-[60] flex items-center justify-center p-4"
      onClick={() => setUpgradeModal({ open: false, customer: null, plan: 'basic', months: 1 })}>
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-sm" onClick={e => e.stopPropagation()}>
        <div className="p-5 border-b border-slate-100 flex justify-between items-center">
          <div>
            <h2 className="font-black text-slate-900 text-sm">Upgrade / Extend Plan</h2>
            <p className="text-[10px] text-slate-400 mt-0.5">{customer.business_name}</p>
          </div>
          <button onClick={() => setUpgradeModal({ open: false, customer: null, plan: 'basic', months: 1 })}
            className="p-1 text-slate-400 hover:text-slate-700"><X size={16} /></button>
        </div>

        <div className="p-5 space-y-4">
          {successMsg && (
            <div className="bg-emerald-50 border border-emerald-200 text-emerald-700 rounded-lg p-3 text-[10px] font-bold text-center">
              {successMsg}
            </div>
          )}

          {/* Plan selector */}
          <div>
            <p className="text-[9px] font-bold text-slate-400 uppercase tracking-widest mb-2">Plan</p>
            <div className="flex gap-2">
              {['basic', 'premium'].map(p => (
                <button key={p}
                  onClick={() => setUpgradeModal(prev => ({ ...prev, plan: p }))}
                  className={`flex-1 py-2 rounded-lg text-[10px] font-bold uppercase border-2 transition-all ${
                    plan === p
                      ? p === 'premium' ? 'border-emerald-500 bg-emerald-50 text-emerald-700' : 'border-blue-500 bg-blue-50 text-blue-700'
                      : 'border-slate-200 text-slate-400 hover:border-slate-300'
                  }`}>
                  {p}<br/>
                  <span className="text-[9px] font-normal">₹{PLAN_PRICES[p]}/mo</span>
                </button>
              ))}
            </div>
          </div>

          {/* Months selector */}
          <div>
            <p className="text-[9px] font-bold text-slate-400 uppercase tracking-widest mb-2">Duration</p>
            <div className="flex gap-1.5">
              {[1, 3, 6, 12].map(m => (
                <button key={m}
                  onClick={() => setUpgradeModal(prev => ({ ...prev, months: m }))}
                  className={`flex-1 py-1.5 rounded-lg text-[10px] font-bold border-2 transition-all ${
                    months === m
                      ? 'border-indigo-500 bg-indigo-50 text-indigo-700'
                      : 'border-slate-200 text-slate-400 hover:border-slate-300'
                  }`}>
                  {m}mo
                </button>
              ))}
            </div>
          </div>

          {/* Price preview */}
          <div className="bg-slate-50 rounded-xl p-3">
            <div className="flex justify-between items-center">
              <span className="text-[10px] text-slate-500">Total</span>
              <span className="text-sm font-black text-indigo-600">₹{total.toLocaleString()}</span>
            </div>
            <div className="mt-2 pt-2 border-t border-slate-200 text-[9px] text-slate-400">
              <div className="flex justify-between">
                <span>Current expiry:</span>
                <span className="font-bold text-slate-600">{fmtDate(currentExpiry)}</span>
              </div>
              <div className="flex justify-between mt-0.5">
                <span>New expiry:</span>
                <span className="font-bold text-emerald-600">{fmtDate(newExpiry)}</span>
              </div>
            </div>
          </div>
        </div>

        <div className="p-4 border-t border-slate-100 flex gap-2">
          <button
            onClick={() => setUpgradeModal({ open: false, customer: null, plan: 'basic', months: 1 })}
            className="flex-1 py-2 rounded-lg text-[10px] font-bold uppercase border border-slate-200 text-slate-500 hover:bg-slate-50">
            Cancel
          </button>
          <button
            onClick={handleConfirm}
            disabled={loading}
            className="flex-1 py-2 bg-indigo-600 text-white rounded-lg text-[10px] font-bold uppercase hover:bg-indigo-700 disabled:opacity-50 transition-all">
            {loading ? 'Processing...' : 'Confirm'}
          </button>
        </div>
      </div>
    </div>
  )
}

// ─── Customer Detail Modal ────────────────────────────────────────────────────
function CustomerDetailModal({ customer, onClose, onUpgrade, onToggleStatus, headers, openUpgradeModal, onTrialExtended }) {
  const [activeTab, setActiveTab] = useState('details')
  const [payments, setPayments] = useState([])
  const [paymentsLoading, setPaymentsLoading] = useState(false)
  const [paymentsFetched, setPaymentsFetched] = useState(false)
  const [extendTrialDays, setExtendTrialDays] = useState(null) // null = not showing, 7/14/30 = selected
  const [extendLoading, setExtendLoading] = useState(false)
  const [extendSuccess, setExtendSuccess] = useState('')

  if (!customer) return null

  const now = new Date()
  const validTill = customer.valid_till ? new Date(customer.valid_till) : null
  const trialStart = customer.trial_start ? new Date(customer.trial_start) : null
  const trialEnd = customer.trial_end ? new Date(customer.trial_end) : null
  const licenseStart = customer.license_start ? new Date(customer.license_start) : null

  const planColors = {
    premium: 'bg-emerald-100 text-emerald-700',
    basic: 'bg-blue-100 text-blue-700',
    trial: 'bg-amber-100 text-amber-700',
    free: 'bg-slate-100 text-slate-600',
    none: 'bg-red-100 text-red-600',
  }

  // Feature 4: Grace period calculation
  const graceTotalDays = GRACE_PERIOD_DAYS[customer.plan] || 15
  let graceRemaining = null
  if (customer.is_expired && validTill) {
    const daysSinceExpiry = Math.floor((now - validTill) / (1000 * 60 * 60 * 24))
    graceRemaining = graceTotalDays - daysSinceExpiry
  }

  const getDaysLabel = () => {
    if (customer.is_expired) {
      if (graceRemaining !== null && graceRemaining > 0) {
        return { text: `Grace: ${graceRemaining}d`, color: 'text-orange-500' }
      }
      return { text: 'Grace Expired', color: 'text-red-500' }
    }
    if (customer.days_remaining === 0) return { text: 'Expires today', color: 'text-orange-500' }
    if (customer.days_remaining <= 3) return { text: `${customer.days_remaining}d left`, color: 'text-orange-500' }
    if (customer.days_remaining <= 7) return { text: `${customer.days_remaining}d left`, color: 'text-amber-500' }
    return { text: `${customer.days_remaining}d left`, color: 'text-emerald-600' }
  }

  const daysLabel = customer.days_remaining !== null ? getDaysLabel() : null

  const fetchPayments = async () => {
    if (paymentsFetched) return
    setPaymentsLoading(true)
    try {
      const res = await axios.get(`${API_URL}/api/admin/customers/${customer.id}/payments`, { headers })
      setPayments(res.data.payments || [])
      setPaymentsFetched(true)
    } catch (err) {
      console.error('Failed to fetch payments', err)
    } finally {
      setPaymentsLoading(false)
    }
  }

  const handleTabClick = (tab) => {
    setActiveTab(tab)
    if (tab === 'payments') fetchPayments()
  }

  const downloadInvoice = async (invoiceId, invoiceNumber) => {
    try {
      const response = await axios.get(
        `${API_URL}/api/invoices/admin/${invoiceId}/download`,
        { headers, responseType: 'blob' }
      )
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `${invoiceNumber || invoiceId}.pdf`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
    } catch (err) {
      alert('Failed to download invoice')
    }
  }

  const statusBadge = (status) => {
    const map = {
      captured: 'bg-emerald-100 text-emerald-700',
      failed: 'bg-red-100 text-red-700',
      pending: 'bg-amber-100 text-amber-700',
    }
    return map[status] || 'bg-slate-100 text-slate-600'
  }

  return (
    <div className="fixed inset-0 bg-slate-900/40 z-50 flex items-center justify-center p-4" onClick={onClose}>
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md" onClick={e => e.stopPropagation()}>
        {/* Header */}
        <div className="p-5 border-b border-slate-100 flex justify-between items-start">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-indigo-100 rounded-xl flex items-center justify-center text-indigo-600 font-black text-sm">
              {customer.business_name[0]}
            </div>
            <div>
              <h2 className="font-black text-slate-900 text-sm">{customer.business_name}</h2>
              <p className="text-[10px] text-slate-400">{customer.email}</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1 text-slate-400 hover:text-slate-700">
            <X size={16} />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-slate-100">
          <button
            onClick={() => handleTabClick('details')}
            className={`flex-1 py-2.5 text-[10px] font-bold uppercase tracking-wide transition-all ${
              activeTab === 'details'
                ? 'text-indigo-600 border-b-2 border-indigo-600'
                : 'text-slate-400 hover:text-slate-600'
            }`}>
            Details
          </button>
          <button
            onClick={() => handleTabClick('payments')}
            className={`flex-1 py-2.5 text-[10px] font-bold uppercase tracking-wide flex items-center justify-center gap-1 transition-all ${
              activeTab === 'payments'
                ? 'text-indigo-600 border-b-2 border-indigo-600'
                : 'text-slate-400 hover:text-slate-600'
            }`}>
            <Receipt size={11} /> Payments
          </button>
        </div>

        {/* Details Tab */}
        {activeTab === 'details' && (
          <div className="p-5 space-y-4">
            {/* Plan + Status */}
            <div className="flex items-center gap-2 flex-wrap">
              <span className={`px-2 py-1 rounded-lg text-[10px] font-bold uppercase ${planColors[customer.plan] || planColors.none}`}>
                {customer.plan}
              </span>
              <span className={`px-2 py-1 rounded-lg text-[10px] font-bold uppercase ${customer.is_active ? 'bg-emerald-50 text-emerald-600' : 'bg-red-50 text-red-600'}`}>
                {customer.is_active ? 'Active' : 'Blocked'}
              </span>
              {daysLabel && (
                <span className={`text-[10px] font-bold ${daysLabel.color}`}>
                  • {daysLabel.text}
                </span>
              )}
            </div>

            {/* Feature 4: Grace Period Banner */}
            {customer.is_expired && graceRemaining !== null && (
              <div>
                {graceRemaining > 0 ? (
                  <div className="bg-orange-50 border border-orange-200 rounded-xl p-3">
                    <p className="text-[10px] font-bold text-orange-700 mb-1.5">
                      ⚠️ Grace Period: {graceRemaining} days remaining — customer still has access
                    </p>
                    <div className="w-full bg-orange-100 rounded-full h-1.5">
                      <div
                        className="h-1.5 rounded-full bg-orange-400 transition-all"
                        style={{ width: `${Math.max(0, Math.min(100, (graceRemaining / graceTotalDays) * 100))}%` }}
                      />
                    </div>
                    <div className="flex justify-between mt-1">
                      <span className="text-[8px] text-orange-400">0d</span>
                      <span className="text-[8px] text-orange-400">{graceTotalDays}d total</span>
                    </div>
                  </div>
                ) : (
                  <div className="bg-red-50 border border-red-200 rounded-xl p-3">
                    <p className="text-[10px] font-bold text-red-700">
                      🚫 Grace Period Expired — access blocked
                    </p>
                    <div className="w-full bg-red-100 rounded-full h-1.5 mt-1.5">
                      <div className="h-1.5 rounded-full bg-red-400 w-full" />
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Subscription Dates */}
            <div className="bg-slate-50 rounded-xl p-4 space-y-2.5">
              <p className="text-[9px] font-bold text-slate-400 uppercase tracking-widest mb-2">Subscription Dates</p>

              <DateRow
                icon={<Calendar size={12} />}
                label="Registered"
                value={new Date(customer.created_at).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })}
              />

              {(trialStart || licenseStart) && (
                <DateRow
                  icon={<CheckCircle size={12} className="text-blue-500" />}
                  label="Plan Start"
                  value={(trialStart || licenseStart).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })}
                />
              )}

              {trialEnd && customer.plan === 'trial' && (
                <DateRow
                  icon={<Clock size={12} className="text-amber-500" />}
                  label="Trial Ends"
                  value={trialEnd.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })}
                  highlight={customer.days_remaining <= 3}
                />
              )}

              {validTill && customer.plan !== 'trial' && customer.plan !== 'free' && (
                <DateRow
                  icon={customer.is_expired
                    ? <AlertTriangle size={12} className="text-red-500" />
                    : <CheckCircle size={12} className="text-emerald-500" />
                  }
                  label="Expires On"
                  value={validTill.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })}
                  highlight={customer.is_expired || customer.days_remaining <= 7}
                  expired={customer.is_expired}
                />
              )}

              {customer.days_remaining !== null && !customer.is_expired && customer.plan !== 'free' && (
                <div className="mt-2 pt-2 border-t border-slate-200">
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-[9px] text-slate-400 font-bold uppercase">Days Remaining</span>
                    <span className={`text-[10px] font-black ${daysLabel.color}`}>{customer.days_remaining} days</span>
                  </div>
                  <div className="w-full bg-slate-200 rounded-full h-1.5">
                    <div
                      className={`h-1.5 rounded-full transition-all ${
                        customer.days_remaining <= 3 ? 'bg-red-500' :
                        customer.days_remaining <= 7 ? 'bg-orange-500' :
                        customer.days_remaining <= 15 ? 'bg-amber-500' : 'bg-emerald-500'
                      }`}
                      style={{ width: `${Math.min(100, (customer.days_remaining / 30) * 100)}%` }}
                    />
                  </div>
                </div>
              )}
            </div>

            {/* Contact Info */}
            <div className="space-y-1.5">
              <p className="text-[9px] font-bold text-slate-400 uppercase tracking-widest">Contact</p>
              <div className="flex items-center gap-2 text-[10px] text-slate-600">
                <User size={11} className="text-slate-400" /> {customer.owner_name}
              </div>
              <div className="flex items-center gap-2 text-[10px] text-slate-600">
                <Phone size={11} className="text-slate-400" /> {customer.phone}
              </div>
              {customer.city && (
                <div className="flex items-center gap-2 text-[10px] text-slate-600">
                  <MapPin size={11} className="text-slate-400" /> {customer.city}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Payments Tab */}
        {activeTab === 'payments' && (
          <div className="p-5">
            {paymentsLoading ? (
              <div className="flex items-center justify-center py-10">
                <RefreshCw size={20} className="animate-spin text-indigo-400" />
              </div>
            ) : payments.length === 0 ? (
              <div className="text-center py-10">
                <Receipt className="mx-auto text-slate-300 mb-2" size={32} />
                <p className="text-slate-400 text-[10px] font-bold">No payments yet</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="text-left text-slate-400 text-[9px] uppercase tracking-wider border-b border-slate-100">
                    <tr>
                      <th className="pb-2">Date</th>
                      <th className="pb-2">Plan</th>
                      <th className="pb-2">Amount</th>
                      <th className="pb-2">Status</th>
                      <th className="pb-2 text-right">Invoice</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-50">
                    {payments.map((p) => (
                      <tr key={p.id} className="text-[10px] hover:bg-slate-50/80">
                        <td className="py-2 text-slate-500">
                          {new Date(p.created_at).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: '2-digit' })}
                        </td>
                        <td className="py-2">
                          <span className={`px-1.5 py-0.5 rounded text-[8px] font-bold uppercase ${
                            p.plan === 'premium' ? 'bg-emerald-100 text-emerald-700' :
                            p.plan === 'basic' ? 'bg-blue-100 text-blue-700' :
                            'bg-slate-100 text-slate-500'
                          }`}>{p.plan}</span>
                        </td>
                        <td className="py-2 font-black text-slate-800">₹{p.amount / 100}</td>
                        <td className="py-2">
                          <span className={`px-1.5 py-0.5 rounded text-[8px] font-bold uppercase ${statusBadge(p.status)}`}>
                            {p.status}
                          </span>
                        </td>
                        <td className="py-2 text-right">
                          {p.pdf_available && p.invoice_id ? (
                            <button
                              onClick={() => downloadInvoice(p.invoice_id, p.invoice_number)}
                              className="p-1 bg-indigo-50 text-indigo-600 rounded hover:bg-indigo-100"
                              title="Download PDF">
                              <Download size={12} />
                            </button>
                          ) : (
                            <span className="text-slate-300 text-[9px]">—</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* Actions */}
        <div className="p-4 border-t border-slate-100 space-y-2">
          {/* Extend Trial — फक्त trial plan साठी दाखवा */}
          {customer.plan === 'trial' && (
            <div>
              {extendSuccess ? (
                <div className="bg-emerald-50 border border-emerald-200 text-emerald-700 rounded-lg p-2.5 text-[10px] font-bold text-center">
                  {extendSuccess}
                </div>
              ) : extendTrialDays === null ? (
                <button
                  onClick={() => setExtendTrialDays(7)}
                  className="w-full py-2 rounded-lg text-[10px] font-bold uppercase border-2 border-amber-300 text-amber-600 hover:bg-amber-50 transition-all flex items-center justify-center gap-1.5"
                >
                  <Clock size={12} /> Extend Trial
                </button>
              ) : (
                <div className="bg-amber-50 border border-amber-200 rounded-xl p-3 space-y-2">
                  <p className="text-[9px] font-bold text-amber-700 uppercase tracking-widest">Extend trial by:</p>
                  <div className="flex gap-1.5">
                    {[7, 14, 30].map(d => (
                      <button
                        key={d}
                        onClick={() => setExtendTrialDays(d)}
                        className={`flex-1 py-1.5 rounded-lg text-[10px] font-bold border-2 transition-all ${
                          extendTrialDays === d
                            ? 'border-amber-500 bg-amber-100 text-amber-700'
                            : 'border-amber-200 text-amber-500 hover:border-amber-400'
                        }`}
                      >
                        {d}d
                      </button>
                    ))}
                  </div>
                  <div className="flex gap-1.5">
                    <button
                      onClick={() => setExtendTrialDays(null)}
                      className="flex-1 py-1.5 rounded-lg text-[10px] font-bold border border-slate-200 text-slate-400 hover:bg-slate-50"
                    >
                      Cancel
                    </button>
                    <button
                      disabled={extendLoading}
                      onClick={async () => {
                        setExtendLoading(true)
                        try {
                          await axios.post(
                            `${API_URL}/api/admin/customers/${customer.id}/extend-trial?days=${extendTrialDays}`,
                            {},
                            { headers }
                          )
                          setExtendSuccess(`Trial extended by ${extendTrialDays} days! ✓`)
                          setExtendTrialDays(null)
                          setTimeout(() => {
                            setExtendSuccess('')
                            onClose()
                            onTrialExtended && onTrialExtended()
                          }, 1800)
                        } catch (err) {
                          alert('Failed: ' + (err.response?.data?.detail || err.message))
                        } finally {
                          setExtendLoading(false)
                        }
                      }}
                      className="flex-1 py-1.5 bg-amber-500 text-white rounded-lg text-[10px] font-bold uppercase hover:bg-amber-600 disabled:opacity-50 transition-all"
                    >
                      {extendLoading ? '...' : 'Confirm'}
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}

          <div className="flex gap-2">
            <button
              onClick={() => { onToggleStatus(customer.id); onClose(); }}
              className={`flex-1 py-2 rounded-lg text-[10px] font-bold uppercase border transition-all ${
                customer.is_active
                  ? 'border-red-200 text-red-500 hover:bg-red-50'
                  : 'border-emerald-200 text-emerald-600 hover:bg-emerald-50'
              }`}>
              {customer.is_active ? 'Block' : 'Unblock'}
            </button>
            <button
              onClick={() => { onClose(); openUpgradeModal(customer); }}
              className="flex-1 py-2 bg-indigo-600 text-white rounded-lg text-[10px] font-bold uppercase hover:bg-indigo-700 transition-all">
              Upgrade / Extend
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

function DateRow({ icon, label, value, highlight, expired }) {
  return (
    <div className="flex justify-between items-center">
      <div className="flex items-center gap-1.5 text-slate-500">
        {icon}
        <span className="text-[10px]">{label}</span>
      </div>
      <span className={`text-[10px] font-bold ${expired ? 'text-red-500' : highlight ? 'text-orange-500' : 'text-slate-700'}`}>
        {value}
      </span>
    </div>
  )
}

// ─── Expiry Warning Section ───────────────────────────────────────────────────
function ExpiryWarningSection({ headers, openUpgradeModal }) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchExpiring = async () => {
      try {
        const res = await axios.get(`${API_URL}/api/admin/expiring-soon?days=7`, { headers })
        setData(res.data)
      } catch (err) {
        console.error('Failed to fetch expiring soon', err)
      } finally {
        setLoading(false)
      }
    }
    fetchExpiring()
  }, [])

  if (loading) {
    return (
      <div className="mt-4 flex items-center gap-2 text-slate-400 text-[10px]">
        <RefreshCw size={12} className="animate-spin" /> Loading expiry data...
      </div>
    )
  }

  if (!data) return null

  const expiringSoon = data.expiring_soon || []
  const expiredGrace = data.expired_in_grace || []

  const planBadge = (plan) => {
    const map = {
      premium: 'bg-emerald-100 text-emerald-700',
      basic: 'bg-blue-100 text-blue-700',
      trial: 'bg-amber-100 text-amber-700',
    }
    return map[plan] || 'bg-slate-100 text-slate-500'
  }

  return (
    <div className="mt-4 space-y-3">
      {/* Expiring Soon */}
      <div className="bg-white rounded-xl shadow-sm border border-amber-200/60 p-4">
        <div className="flex items-center gap-2 mb-3">
          <AlertTriangle size={14} className="text-amber-500" />
          <h3 className="text-[10px] font-bold text-amber-700 uppercase tracking-widest">Expiring Soon (7 days)</h3>
          {expiringSoon.length > 0 && (
            <span className="ml-auto bg-amber-100 text-amber-700 text-[9px] font-bold px-2 py-0.5 rounded-full">
              {expiringSoon.length}
            </span>
          )}
        </div>

        {expiringSoon.length === 0 ? (
          <p className="text-emerald-600 text-[10px] font-bold">✓ No expiring subscriptions</p>
        ) : (
          <div className="space-y-1.5">
            {expiringSoon.map((c) => (
              <div key={c.customer_id} className="flex items-center justify-between p-2 bg-amber-50/50 rounded-lg">
                <div className="flex-1 min-w-0">
                  <p className="font-bold text-slate-700 text-[10px] truncate">{c.business_name}</p>
                  <p className="text-[9px] text-slate-400 truncate">{c.email}</p>
                </div>
                <div className="flex items-center gap-2 ml-2 shrink-0">
                  <span className={`px-1.5 py-0.5 rounded text-[8px] font-bold uppercase ${planBadge(c.plan)}`}>
                    {c.plan}
                  </span>
                  <span className="text-[9px] font-bold text-amber-600">
                    {c.days_remaining !== null ? `${c.days_remaining}d left` : '—'}
                  </span>
                  <button
                    onClick={() => openUpgradeModal({
                      id: c.customer_id,
                      business_name: c.business_name,
                      plan: c.plan,
                      valid_till: c.valid_till,
                    })}
                    className="bg-amber-500 text-white px-2 py-0.5 rounded text-[9px] font-bold hover:bg-amber-600 transition-all">
                    Extend
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Expired in Grace Period */}
      {expiredGrace.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-red-200/60 p-4">
          <div className="flex items-center gap-2 mb-3">
            <ShieldAlert size={14} className="text-red-500" />
            <h3 className="text-[10px] font-bold text-red-700 uppercase tracking-widest">Expired — Grace Period</h3>
            <span className="ml-auto bg-red-100 text-red-700 text-[9px] font-bold px-2 py-0.5 rounded-full">
              {expiredGrace.length}
            </span>
          </div>
          <div className="space-y-1.5">
            {expiredGrace.map((c) => (
              <div key={c.customer_id} className="flex items-center justify-between p-2 bg-red-50/50 rounded-lg">
                <div className="flex-1 min-w-0">
                  <p className="font-bold text-slate-700 text-[10px] truncate">{c.business_name}</p>
                  <span className={`px-1.5 py-0.5 rounded text-[8px] font-bold uppercase ${planBadge(c.plan)}`}>
                    {c.plan}
                  </span>
                </div>
                <div className="flex items-center gap-2 ml-2 shrink-0">
                  <span className={`text-[9px] font-bold ${c.grace_remaining > 0 ? 'text-orange-600' : 'text-red-600'}`}>
                    {c.grace_remaining > 0 ? `Grace: ${c.grace_remaining}d left` : 'Grace Expired'}
                  </span>
                  <button
                    onClick={() => openUpgradeModal({
                      id: c.customer_id,
                      business_name: c.business_name,
                      plan: c.plan,
                      valid_till: c.valid_till,
                    })}
                    className="bg-red-500 text-white px-2 py-0.5 rounded text-[9px] font-bold hover:bg-red-600 transition-all">
                    Renew
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

// ─── Dashboard Main Component ─────────────────────────────────────────────────
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
  const [selectedCustomer, setSelectedCustomer] = useState(null)
  const [upgradeModal, setUpgradeModal] = useState({ open: false, customer: null, plan: 'basic', months: 1 })
  const navigate = useNavigate()

  const token = localStorage.getItem('admin_token')
  const headers = { 'Authorization': `Bearer ${token}` }

  const openUpgradeModal = (customer) => {
    setUpgradeModal({
      open: true,
      customer,
      plan: customer.plan === 'premium' ? 'premium' : 'basic',
      months: 1,
    })
  }

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
      {/* Upgrade Modal */}
      <UpgradeModal
        upgradeModal={upgradeModal}
        setUpgradeModal={setUpgradeModal}
        headers={headers}
        fetchData={fetchData}
      />

      {/* Customer Detail Modal */}
      {selectedCustomer && (
        <CustomerDetailModal
          customer={selectedCustomer}
          onClose={() => setSelectedCustomer(null)}
          onUpgrade={(id) => openUpgradeModal(customers.find(c => c.id === id) || selectedCustomer)}
          onToggleStatus={(id) => toggleStatus(id)}
          headers={headers}
          openUpgradeModal={(c) => { setSelectedCustomer(null); openUpgradeModal(c); }}
          onTrialExtended={() => fetchData()}
        />
      )}

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
                <StatCard title="Revenue" value={`₹${((stats?.revenue_total || 0) / 100).toLocaleString()}`} icon={<Banknote/>} color="indigo" />
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
                    <p className="text-xl font-black">₹{(stats?.arpu || 0) / 100}</p>
                  </div>
                </div>
              </div>

              {/* Feature 3: Expiry Warning Section */}
              <ExpiryWarningSection headers={headers} openUpgradeModal={openUpgradeModal} />
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
                      <th className="pb-2">Expiry</th>
                      <th className="pb-2">Status</th>
                      <th className="pb-2 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-50">
                    {filteredCustomers.map((c) => {
                      const daysRemaining = c.days_remaining
                      const isExpired = c.is_expired
                      const validTill = c.valid_till ? new Date(c.valid_till) : null
                      const trialEnd = c.trial_end ? new Date(c.trial_end) : null
                      const expiryDate = c.plan === 'trial' ? trialEnd : validTill

                      const daysColor = isExpired ? 'text-red-500' :
                        daysRemaining <= 3 ? 'text-red-500' :
                        daysRemaining <= 7 ? 'text-orange-500' :
                        daysRemaining <= 15 ? 'text-amber-500' : 'text-emerald-600'

                      return (
                        <tr
                          key={c.id}
                          className="text-[10px] hover:bg-slate-50/80 cursor-pointer transition-colors"
                          onClick={() => setSelectedCustomer(c)}
                        >
                          <td className="py-2.5 font-bold text-slate-700">
                            {c.business_name}
                            <br/>
                            <span className="font-normal text-[9px] text-slate-400">{c.email}</span>
                          </td>
                          <td className="py-2.5 text-slate-500">
                            {new Date(c.created_at).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: '2-digit' })}
                          </td>
                          <td className="py-2.5">
                            <span className={`px-1.5 py-0.5 rounded text-[8px] font-bold uppercase ${
                              c.plan === 'premium' ? 'bg-emerald-100 text-emerald-700' :
                              c.plan === 'basic' ? 'bg-blue-100 text-blue-700' :
                              c.plan === 'trial' ? 'bg-amber-100 text-amber-700' :
                              'bg-slate-100 text-slate-500'
                            }`}>{c.plan}</span>
                          </td>
                          <td className="py-2.5">
                            {expiryDate && c.plan !== 'free' ? (
                              <div>
                                <p className="text-slate-600">
                                  {expiryDate.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: '2-digit' })}
                                </p>
                                {daysRemaining !== null && (
                                  <p className={`text-[9px] font-bold ${daysColor}`}>
                                    {isExpired ? 'Expired' : `${daysRemaining}d left`}
                                  </p>
                                )}
                              </div>
                            ) : (
                              <span className="text-slate-300">—</span>
                            )}
                          </td>
                          <td className="py-2.5">
                            <button
                              onClick={(e) => { e.stopPropagation(); toggleStatus(c.id); }}
                              className={`font-bold ${c.is_active ? 'text-emerald-500' : 'text-red-500'}`}
                            >
                              {c.is_active ? 'Active' : 'Blocked'}
                            </button>
                          </td>
                          <td className="py-2.5 text-right">
                            <div className="flex items-center justify-end gap-1">
                              <button
                                onClick={(e) => { e.stopPropagation(); openUpgradeModal(c); }}
                                className="bg-indigo-50 text-indigo-600 px-2 py-0.5 rounded font-bold hover:bg-indigo-600 hover:text-white uppercase text-[9px]"
                              >
                                Upgrade
                              </button>
                              <button
                                onClick={(e) => { e.stopPropagation(); setSelectedCustomer(c); }}
                                className="p-1 text-slate-400 hover:text-slate-700"
                              >
                                <ChevronRight size={12} />
                              </button>
                            </div>
                          </td>
                        </tr>
                      )
                    })}
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
