import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { useNavigate } from 'react-router-dom'
import { Tag, Plus, X, Calendar, Users, TrendingDown, AlertCircle } from 'lucide-react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8661'

function PromoCodeManagement() {
  const [promoCodes, setPromoCodes] = useState([])
  const [loading, setLoading] = useState(true)
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [formData, setFormData] = useState({
    code: '',
    discount_type: 'percentage',
    discount_value: '',
    applicable_plans: ['basic', 'premium'],
    expiry_date: '',
    usage_limit: '',
    is_multi_use: false
  })
  const [formError, setFormError] = useState('')
  const [formSuccess, setFormSuccess] = useState('')
  const navigate = useNavigate()

  const token = localStorage.getItem('admin_token')
  const headers = { 'Authorization': `Bearer ${token}` }

  const fetchPromoCodes = async () => {
    if (!token) {
      navigate('/admin/login')
      return
    }

    setLoading(true)
    try {
      const { data } = await axios.get(`${API_URL}/api/promo/admin/list`, { headers })
      setPromoCodes(data.promo_codes)
    } catch (err) {
      if (err.response?.status === 401) {
        localStorage.removeItem('admin_token')
        navigate('/admin/login')
      } else {
        console.error('Failed to fetch promo codes:', err)
      }
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchPromoCodes()
  }, [])

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
  }

  const handlePlanToggle = (plan) => {
    setFormData(prev => ({
      ...prev,
      applicable_plans: prev.applicable_plans.includes(plan)
        ? prev.applicable_plans.filter(p => p !== plan)
        : [...prev.applicable_plans, plan]
    }))
  }

  const handleCreatePromo = async (e) => {
    e.preventDefault()
    setFormError('')
    setFormSuccess('')

    // Validation
    if (!formData.code.trim()) {
      setFormError('Promo code is required')
      return
    }
    if (!formData.discount_value || formData.discount_value <= 0) {
      setFormError('Discount value must be greater than 0')
      return
    }
    if (formData.discount_type === 'percentage' && formData.discount_value > 100) {
      setFormError('Percentage discount cannot exceed 100%')
      return
    }
    if (formData.applicable_plans.length === 0) {
      setFormError('Select at least one applicable plan')
      return
    }

    try {
      const payload = {
        code: formData.code.toUpperCase(),
        discount_type: formData.discount_type,
        discount_value: formData.discount_type === 'percentage' 
          ? parseInt(formData.discount_value)
          : parseInt(formData.discount_value) * 100, // Convert to paise for fixed
        applicable_plans: formData.applicable_plans,
        expiry_date: formData.expiry_date || null,
        usage_limit: formData.usage_limit ? parseInt(formData.usage_limit) : null,
        is_multi_use: formData.is_multi_use
      }

      await axios.post(`${API_URL}/api/promo/admin/create`, payload, { headers })
      
      setFormSuccess('Promo code created successfully!')
      setShowCreateForm(false)
      setFormData({
        code: '',
        discount_type: 'percentage',
        discount_value: '',
        applicable_plans: ['basic', 'premium'],
        expiry_date: '',
        usage_limit: '',
        is_multi_use: false
      })
      fetchPromoCodes()
    } catch (err) {
      setFormError(err.response?.data?.detail || 'Failed to create promo code')
    }
  }

  const handleDeactivate = async (promoId, code) => {
    if (!window.confirm(`Deactivate promo code "${code}"?`)) return

    try {
      await axios.put(`${API_URL}/api/promo/admin/${promoId}/deactivate`, {}, { headers })
      fetchPromoCodes()
    } catch (err) {
      alert('Failed to deactivate promo code')
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-slate-400 font-bold uppercase tracking-widest text-xs">Loading...</div>
      </div>
    )
  }

  return (
    <>
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <div>
            <p className="text-slate-500 text-sm">Manage discount codes for marketing campaigns</p>
          </div>
          <button
            onClick={() => setShowCreateForm(!showCreateForm)}
            className="flex items-center gap-2 bg-indigo-600 text-white px-4 py-2 rounded-lg font-bold hover:bg-indigo-700 transition-all text-sm"
          >
            {showCreateForm ? <X size={16} /> : <Plus size={16} />}
            {showCreateForm ? 'Cancel' : 'Create Promo Code'}
          </button>
        </div>

        {/* Success Message */}
        {formSuccess && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6 flex items-center gap-2 text-green-700">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
            </svg>
            <span className="font-medium">{formSuccess}</span>
          </div>
        )}

        {/* Create Form */}
        {showCreateForm && (
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 mb-6">
            <h2 className="text-lg font-bold text-slate-900 mb-4">Create New Promo Code</h2>
            
            {formError && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-4 flex items-center gap-2 text-red-700 text-sm">
                <AlertCircle size={16} />
                <span>{formError}</span>
              </div>
            )}

            <form onSubmit={handleCreatePromo} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Promo Code */}
                <div>
                  <label className="block text-slate-700 font-medium mb-2 text-sm">Promo Code *</label>
                  <input
                    type="text"
                    name="code"
                    value={formData.code}
                    onChange={handleInputChange}
                    placeholder="e.g., LAUNCH50"
                    className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:border-indigo-500 text-sm uppercase"
                    required
                  />
                </div>

                {/* Discount Type */}
                <div>
                  <label className="block text-slate-700 font-medium mb-2 text-sm">Discount Type *</label>
                  <select
                    name="discount_type"
                    value={formData.discount_type}
                    onChange={handleInputChange}
                    className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:border-indigo-500 text-sm"
                  >
                    <option value="percentage">Percentage (%)</option>
                    <option value="fixed">Fixed Amount (₹)</option>
                  </select>
                </div>

                {/* Discount Value */}
                <div>
                  <label className="block text-slate-700 font-medium mb-2 text-sm">
                    Discount Value * {formData.discount_type === 'percentage' ? '(%)' : '(₹)'}
                  </label>
                  <input
                    type="number"
                    name="discount_value"
                    value={formData.discount_value}
                    onChange={handleInputChange}
                    placeholder={formData.discount_type === 'percentage' ? '50' : '100'}
                    min="1"
                    max={formData.discount_type === 'percentage' ? '100' : undefined}
                    className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:border-indigo-500 text-sm"
                    required
                  />
                </div>

                {/* Usage Limit */}
                <div>
                  <label className="block text-slate-700 font-medium mb-2 text-sm">Usage Limit (Optional)</label>
                  <input
                    type="number"
                    name="usage_limit"
                    value={formData.usage_limit}
                    onChange={handleInputChange}
                    placeholder="Leave empty for unlimited"
                    min="1"
                    className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:border-indigo-500 text-sm"
                  />
                </div>

                {/* Expiry Date */}
                <div>
                  <label className="block text-slate-700 font-medium mb-2 text-sm">Expiry Date (Optional)</label>
                  <input
                    type="datetime-local"
                    name="expiry_date"
                    value={formData.expiry_date}
                    onChange={handleInputChange}
                    className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:border-indigo-500 text-sm"
                  />
                </div>
              </div>

              {/* Applicable Plans */}
              <div>
                <label className="block text-slate-700 font-medium mb-2 text-sm">Applicable Plans *</label>
                <div className="flex gap-4">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={formData.applicable_plans.includes('basic')}
                      onChange={() => handlePlanToggle('basic')}
                      className="w-4 h-4 text-indigo-600 rounded focus:ring-indigo-500"
                    />
                    <span className="text-sm text-slate-700">Basic (₹499)</span>
                  </label>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={formData.applicable_plans.includes('premium')}
                      onChange={() => handlePlanToggle('premium')}
                      className="w-4 h-4 text-indigo-600 rounded focus:ring-indigo-500"
                    />
                    <span className="text-sm text-slate-700">Premium (₹999)</span>
                  </label>
                </div>
              </div>

              {/* Multi-use */}
              <div>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    name="is_multi_use"
                    checked={formData.is_multi_use}
                    onChange={handleInputChange}
                    className="w-4 h-4 text-indigo-600 rounded focus:ring-indigo-500"
                  />
                  <span className="text-sm text-slate-700">Allow customers to use this code multiple times</span>
                </label>
              </div>

              {/* Submit Button */}
              <div className="flex justify-end gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowCreateForm(false)}
                  className="px-6 py-2 border border-slate-300 text-slate-700 rounded-lg font-bold hover:bg-slate-50 transition-all text-sm"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-6 py-2 bg-indigo-600 text-white rounded-lg font-bold hover:bg-indigo-700 transition-all text-sm"
                >
                  Create Promo Code
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Promo Codes List */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-slate-50 border-b border-slate-200">
                <tr className="text-left text-slate-600 text-xs uppercase tracking-wider">
                  <th className="px-6 py-4 font-bold">Code</th>
                  <th className="px-6 py-4 font-bold">Discount</th>
                  <th className="px-6 py-4 font-bold">Plans</th>
                  <th className="px-6 py-4 font-bold">Usage</th>
                  <th className="px-6 py-4 font-bold">Expiry</th>
                  <th className="px-6 py-4 font-bold">Status</th>
                  <th className="px-6 py-4 font-bold text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {promoCodes.length === 0 ? (
                  <tr>
                    <td colSpan="7" className="px-6 py-12 text-center text-slate-400 text-sm">
                      No promo codes created yet. Click "Create Promo Code" to get started.
                    </td>
                  </tr>
                ) : (
                  promoCodes.map((promo) => (
                    <tr key={promo.id} className="hover:bg-slate-50 transition-colors">
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          <Tag size={16} className="text-indigo-600" />
                          <span className="font-bold text-slate-900 text-sm">{promo.code}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className="text-slate-700 text-sm font-medium">
                          {promo.discount_type === 'percentage' 
                            ? `${promo.discount_value}%` 
                            : `₹${promo.discount_value / 100}`}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex gap-1">
                          {promo.applicable_plans.map(plan => (
                            <span key={plan} className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs font-bold uppercase">
                              {plan}
                            </span>
                          ))}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-1 text-sm">
                          <Users size={14} className="text-slate-400" />
                          <span className="text-slate-700 font-medium">
                            {promo.usage_count}{promo.usage_limit ? `/${promo.usage_limit}` : ''}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        {promo.expiry_date ? (
                          <div className="flex items-center gap-1 text-sm text-slate-600">
                            <Calendar size={14} className="text-slate-400" />
                            <span>{new Date(promo.expiry_date).toLocaleDateString()}</span>
                          </div>
                        ) : (
                          <span className="text-slate-400 text-sm">No expiry</span>
                        )}
                      </td>
                      <td className="px-6 py-4">
                        <span className={`px-2 py-1 rounded text-xs font-bold uppercase ${
                          promo.is_active 
                            ? 'bg-green-100 text-green-700' 
                            : 'bg-red-100 text-red-700'
                        }`}>
                          {promo.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-right">
                        {promo.is_active && (
                          <button
                            onClick={() => handleDeactivate(promo.id, promo.code)}
                            className="text-red-600 hover:text-red-800 font-bold text-sm"
                          >
                            Deactivate
                          </button>
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </>
  )
}

export default PromoCodeManagement
