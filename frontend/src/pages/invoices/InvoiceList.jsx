import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { useNavigate } from 'react-router-dom'
import { 
  FileText, 
  Download, 
  Mail, 
  Calendar, 
  CreditCard,
  ArrowLeft,
  RefreshCw,
  CheckCircle,
  XCircle,
  Tag
} from 'lucide-react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8661'

function InvoiceList() {
  const [invoices, setInvoices] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [emailingId, setEmailingId] = useState(null)
  const [downloadingId, setDownloadingId] = useState(null)
  const navigate = useNavigate()

  // JWT Token Fetch करा
  const token = localStorage.getItem('sp_token')
  const headers = { 'Authorization': `Bearer ${token}` }

  const fetchInvoices = async () => {
    if (!token) {
      navigate('/register')
      return
    }

    setLoading(true)
    setError('')

    try {
      const response = await axios.get(`${API_URL}/api/invoices/list`, { headers })
      setInvoices(response.data.invoices)
    } catch (err) {
      if (err.response?.status === 401) {
        localStorage.removeItem('sp_token')
        navigate('/register')
      } else {
        setError('Failed to load invoices. Please try again.')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleDownload = async (invoiceId, invoiceNumber) => {
    setDownloadingId(invoiceId)
    try {
      const response = await axios.get(
        `${API_URL}/api/invoices/${invoiceId}/download`,
        { 
          headers,
          responseType: 'blob'
        }
      )

      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `${invoiceNumber}.pdf`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
    } catch (err) {
      alert('Failed to download invoice. Please try again.')
    } finally {
      setDownloadingId(null)
    }
  }

  const handleEmail = async (invoiceId, invoiceNumber) => {
    if (!window.confirm(`Send invoice ${invoiceNumber} to your email?`)) return

    setEmailingId(invoiceId)
    try {
      await axios.post(
        `${API_URL}/api/invoices/${invoiceId}/email`,
        {},
        { headers }
      )
      alert(`✅ Invoice ${invoiceNumber} has been sent to your email!`)
    } catch (err) {
      alert('Failed to send email. Please try again.')
    } finally {
      setEmailingId(null)
    }
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-IN', { 
      day: '2-digit', 
      month: 'short', 
      year: 'numeric' 
    })
  }

  const formatAmount = (amount) => {
    return `₹${(amount / 100).toLocaleString('en-IN')}`
  }

  const getPlanColor = (plan) => {
    const colors = {
      basic: 'bg-blue-100 text-blue-700',
      premium: 'bg-purple-100 text-purple-700',
      trial: 'bg-amber-100 text-amber-700'
    }
    return colors[plan] || 'bg-slate-100 text-slate-700'
  }

  useEffect(() => {
    fetchInvoices()
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="animate-spin text-indigo-600 mx-auto mb-2" size={32} />
          <p className="text-slate-600 font-bold text-sm">Loading invoices...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-50 p-4 md:p-8">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <button 
            onClick={() => navigate('/')} 
            className="flex items-center gap-2 text-slate-600 hover:text-slate-900 mb-4 text-sm font-medium"
          >
            <ArrowLeft size={16} />
            Back to Home
          </button>

          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-black text-slate-900 uppercase tracking-tight">
                My Invoices
              </h1>
              <p className="text-slate-500 text-sm mt-1">
                View and download your payment invoices
              </p>
            </div>
            <button 
              onClick={fetchInvoices}
              disabled={loading}
              className="p-2 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 shadow-sm"
            >
              <RefreshCw size={16} className={`text-slate-600 ${loading ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6 flex items-center gap-3">
            <XCircle className="text-red-500" size={20} />
            <p className="text-red-700 text-sm font-medium">{error}</p>
          </div>
        )}

        {/* Empty State */}
        {!loading && invoices.length === 0 && (
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-12 text-center">
            <FileText className="text-slate-300 mx-auto mb-4" size={48} />
            <h3 className="text-lg font-bold text-slate-900 mb-2">No Invoices Yet</h3>
            <p className="text-slate-500 text-sm mb-6">
              Your invoices will appear here after you make a payment
            </p>
            <button 
              onClick={() => navigate('/plans')}
              className="bg-indigo-600 text-white px-6 py-2 rounded-lg font-bold text-sm hover:bg-indigo-700"
            >
              View Plans
            </button>
          </div>
        )}

        {/* Invoice List */}
        {invoices.length > 0 && (
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
            {/* Desktop Table */}
            <div className="hidden md:block overflow-x-auto">
              <table className="w-full">
                <thead className="bg-slate-50 border-b border-slate-200">
                  <tr className="text-left text-slate-600 text-xs font-bold uppercase tracking-wider">
                    <th className="px-6 py-4">Invoice</th>
                    <th className="px-6 py-4">Date</th>
                    <th className="px-6 py-4">Plan</th>
                    <th className="px-6 py-4">Amount</th>
                    <th className="px-6 py-4">Status</th>
                    <th className="px-6 py-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {invoices.map((invoice) => (
                    <tr key={invoice.id} className="hover:bg-slate-50/50 transition-colors">
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 bg-indigo-100 rounded-lg flex items-center justify-center">
                            <FileText className="text-indigo-600" size={20} />
                          </div>
                          <div>
                            <p className="font-bold text-slate-900 text-sm">{invoice.invoice_number}</p>
                            <p className="text-slate-500 text-xs">ID: {invoice.id.slice(0, 8)}...</p>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2 text-slate-600 text-sm">
                          <Calendar size={14} />
                          {formatDate(invoice.invoice_date)}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase ${getPlanColor(invoice.plan)}`}>
                          {invoice.plan}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <div>
                          <p className="font-black text-slate-900 text-sm">{formatAmount(invoice.total_amount)}</p>
                          {invoice.discount_amount > 0 && (
                            <p className="text-xs text-emerald-600 flex items-center gap-1">
                              <Tag size={12} />
                              -{formatAmount(invoice.discount_amount)} discount
                            </p>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          {invoice.is_emailed ? (
                            <>
                              <CheckCircle className="text-emerald-500" size={16} />
                              <span className="text-emerald-600 text-xs font-bold">Emailed</span>
                            </>
                          ) : (
                            <>
                              <XCircle className="text-slate-400" size={16} />
                              <span className="text-slate-500 text-xs font-bold">Not Sent</span>
                            </>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center justify-end gap-2">
                          <button
                            onClick={() => handleDownload(invoice.id, invoice.invoice_number)}
                            disabled={!invoice.pdf_available || downloadingId === invoice.id}
                            className="p-2 bg-indigo-50 text-indigo-600 rounded-lg hover:bg-indigo-100 disabled:opacity-50 disabled:cursor-not-allowed"
                            title="Download PDF"
                          >
                            {downloadingId === invoice.id ? (
                              <RefreshCw size={16} className="animate-spin" />
                            ) : (
                              <Download size={16} />
                            )}
                          </button>
                          <button
                            onClick={() => handleEmail(invoice.id, invoice.invoice_number)}
                            disabled={emailingId === invoice.id}
                            className="p-2 bg-emerald-50 text-emerald-600 rounded-lg hover:bg-emerald-100 disabled:opacity-50 disabled:cursor-not-allowed"
                            title="Email Invoice"
                          >
                            {emailingId === invoice.id ? (
                              <RefreshCw size={16} className="animate-spin" />
                            ) : (
                              <Mail size={16} />
                            )}
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Mobile Cards */}
            <div className="md:hidden divide-y divide-slate-100">
              {invoices.map((invoice) => (
                <div key={invoice.id} className="p-4">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-indigo-100 rounded-lg flex items-center justify-center flex-shrink-0">
                        <FileText className="text-indigo-600" size={20} />
                      </div>
                      <div>
                        <p className="font-bold text-slate-900 text-sm">{invoice.invoice_number}</p>
                        <p className="text-slate-500 text-xs">{formatDate(invoice.invoice_date)}</p>
                      </div>
                    </div>
                    <span className={`px-2 py-1 rounded-full text-xs font-bold uppercase ${getPlanColor(invoice.plan)}`}>
                      {invoice.plan}
                    </span>
                  </div>

                  <div className="flex items-center justify-between mb-3">
                    <div>
                      <p className="text-slate-500 text-xs mb-1">Total Amount</p>
                      <p className="font-black text-slate-900">{formatAmount(invoice.total_amount)}</p>
                      {invoice.discount_amount > 0 && (
                        <p className="text-xs text-emerald-600 flex items-center gap-1 mt-1">
                          <Tag size={12} />
                          -{formatAmount(invoice.discount_amount)} discount
                        </p>
                      )}
                    </div>
                    <div className="text-right">
                      <p className="text-slate-500 text-xs mb-1">Status</p>
                      <div className="flex items-center gap-1 justify-end">
                        {invoice.is_emailed ? (
                          <>
                            <CheckCircle className="text-emerald-500" size={14} />
                            <span className="text-emerald-600 text-xs font-bold">Emailed</span>
                          </>
                        ) : (
                          <>
                            <XCircle className="text-slate-400" size={14} />
                            <span className="text-slate-500 text-xs font-bold">Not Sent</span>
                          </>
                        )}
                      </div>
                    </div>
                  </div>

                  <div className="flex gap-2">
                    <button
                      onClick={() => handleDownload(invoice.id, invoice.invoice_number)}
                      disabled={!invoice.pdf_available || downloadingId === invoice.id}
                      className="flex-1 flex items-center justify-center gap-2 p-2 bg-indigo-50 text-indigo-600 rounded-lg hover:bg-indigo-100 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-bold"
                    >
                      {downloadingId === invoice.id ? (
                        <RefreshCw size={16} className="animate-spin" />
                      ) : (
                        <Download size={16} />
                      )}
                      Download
                    </button>
                    <button
                      onClick={() => handleEmail(invoice.id, invoice.invoice_number)}
                      disabled={emailingId === invoice.id}
                      className="flex-1 flex items-center justify-center gap-2 p-2 bg-emerald-50 text-emerald-600 rounded-lg hover:bg-emerald-100 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-bold"
                    >
                      {emailingId === invoice.id ? (
                        <RefreshCw size={16} className="animate-spin" />
                      ) : (
                        <Mail size={16} />
                      )}
                      Email
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Summary Card */}
        {invoices.length > 0 && (
          <div className="mt-6 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-xl shadow-lg p-6 text-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-indigo-200 text-xs font-bold uppercase tracking-wider mb-1">Total Invoices</p>
                <p className="text-3xl font-black">{invoices.length}</p>
              </div>
              <div className="text-right">
                <p className="text-indigo-200 text-xs font-bold uppercase tracking-wider mb-1">Total Paid</p>
                <p className="text-3xl font-black">
                  {formatAmount(invoices.reduce((sum, inv) => sum + inv.total_amount, 0))}
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default InvoiceList
