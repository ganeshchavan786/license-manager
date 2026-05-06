import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { useNavigate } from 'react-router-dom'
import { 
  Save, 
  TestTube, 
  Mail, 
  Server, 
  Lock,
  CheckCircle,
  XCircle,
  Loader,
  ArrowLeft,
  Building2,
  DollarSign,
  Settings as SettingsIcon,
  Clock,
  CreditCard,
  Layers,
  Globe,
  X
} from 'lucide-react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8661'

function Settings() {
  const [activeTab, setActiveTab] = useState('smtp')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [testing, setTesting] = useState(false)
  const [testResult, setTestResult] = useState(null)
  
  // SMTP Settings
  const [smtpSettings, setSmtpSettings] = useState({
    smtp_host: '',
    smtp_port: 587,
    smtp_username: '',
    smtp_password: '',
    smtp_from_email: '',
    smtp_use_tls: true
  })
  
  // Business Settings
  const [businessSettings, setBusinessSettings] = useState({
    app_name: '',
    support_email: '',
    frontend_url: '',
    company_address: '',
    company_gst: '',
    company_phone: '',
    invoice_footer: ''
  })
  
  // Plan Settings
  const [planSettings, setPlanSettings] = useState({
    trial_days: 7,
    free_offline_grace: 15,
    basic_offline_grace: 15,
    premium_offline_grace: 30,
    basic_price: 49900,
    premium_price: 99900
  })
  
  // System Settings
  const [systemSettings, setSystemSettings] = useState({
    access_token_expire_minutes: 60,
    maintenance_mode: false,
    max_login_attempts: 5,
    session_timeout_minutes: 30
  })
  
  // Payment Gateway Settings
  const [paymentSettings, setPaymentSettings] = useState({
    razorpay_key_id: '',
    razorpay_key_secret: '',
    payment_gateway_enabled: true,
    payment_gateway_mode: 'test'
  })
  
  // Plan Features Settings
  const [planFeatures, setPlanFeatures] = useState({
    trial: [],
    free: [],
    basic: [],
    premium: []
  })
  
  // CORS Origins Settings
  const [corsOrigins, setCorsOrigins] = useState({
    origins: []
  })
  
  const navigate = useNavigate()
  const token = localStorage.getItem('admin_token')
  const headers = { 'Authorization': `Bearer ${token}` }

  useEffect(() => {
    fetchSettings()
  }, [activeTab])

  const fetchSettings = async () => {
    if (!token) {
      navigate('/admin/login')
      return
    }

    setLoading(true)
    try {
      if (activeTab === 'smtp') {
        const response = await axios.get(`${API_URL}/api/admin/settings/smtp`, { headers })
        setSmtpSettings(response.data)
      } else if (activeTab === 'business') {
        const response = await axios.get(`${API_URL}/api/admin/settings/business`, { headers })
        setBusinessSettings(response.data)
      } else if (activeTab === 'plans') {
        const response = await axios.get(`${API_URL}/api/admin/settings/plans`, { headers })
        setPlanSettings(response.data)
      } else if (activeTab === 'system') {
        const response = await axios.get(`${API_URL}/api/admin/settings/system`, { headers })
        setSystemSettings(response.data)
      } else if (activeTab === 'payment') {
        const response = await axios.get(`${API_URL}/api/admin/settings/payment-gateway`, { headers })
        setPaymentSettings(response.data)
      } else if (activeTab === 'features') {
        const response = await axios.get(`${API_URL}/api/admin/settings/plans/features`, { headers })
        setPlanFeatures(response.data)
      } else if (activeTab === 'cors') {
        const response = await axios.get(`${API_URL}/api/admin/settings/cors/origins`, { headers })
        setCorsOrigins(response.data)
      }
    } catch (err) {
      if (err.response?.status === 401) {
        localStorage.removeItem('admin_token')
        navigate('/admin/login')
      } else {
        alert('Failed to load settings')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    setSaving(true)
    setTestResult(null)
    try {
      let endpoint = ''
      let data = {}
      
      if (activeTab === 'smtp') {
        endpoint = `${API_URL}/api/admin/settings/smtp`
        data = smtpSettings
      } else if (activeTab === 'business') {
        endpoint = `${API_URL}/api/admin/settings/business`
        data = businessSettings
      } else if (activeTab === 'plans') {
        endpoint = `${API_URL}/api/admin/settings/plans`
        data = planSettings
      } else if (activeTab === 'system') {
        endpoint = `${API_URL}/api/admin/settings/system`
        data = systemSettings
      } else if (activeTab === 'payment') {
        endpoint = `${API_URL}/api/admin/settings/payment-gateway`
        data = paymentSettings
      } else if (activeTab === 'features') {
        endpoint = `${API_URL}/api/admin/settings/plans/features`
        data = planFeatures
      } else if (activeTab === 'cors') {
        endpoint = `${API_URL}/api/admin/settings/cors/origins`
        data = corsOrigins
      }
      
      await axios.post(endpoint, data, { headers })
      alert('✅ Settings saved successfully!')
    } catch (err) {
      alert('❌ Failed to save settings: ' + (err.response?.data?.detail || err.message))
    } finally {
      setSaving(false)
    }
  }

  const handleTest = async () => {
    setTesting(true)
    setTestResult(null)
    try {
      const response = await axios.post(
        `${API_URL}/api/admin/settings/smtp/test`,
        {
          smtp_host: smtpSettings.smtp_host,
          smtp_port: smtpSettings.smtp_port,
          smtp_username: smtpSettings.smtp_username,
          smtp_password: smtpSettings.smtp_password,
          smtp_use_tls: smtpSettings.smtp_use_tls
        },
        { headers }
      )
      setTestResult({ success: true, message: response.data.message })
    } catch (err) {
      setTestResult({ 
        success: false, 
        message: err.response?.data?.detail || 'Connection failed' 
      })
    } finally {
      setTesting(false)
    }
  }

  return (
    <>
      <div className="max-w-4xl mx-auto">
        
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-lg font-black text-slate-900 uppercase tracking-widest">
            Admin Settings
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Configure system settings (all changes saved to database)
          </p>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-4 overflow-x-auto">
          <TabButton 
            active={activeTab === 'smtp'} 
            icon={<Mail size={14} />} 
            label="SMTP Email" 
            onClick={() => setActiveTab('smtp')} 
          />
          <TabButton 
            active={activeTab === 'business'} 
            icon={<Building2 size={14} />} 
            label="Business Info" 
            onClick={() => setActiveTab('business')} 
          />
          <TabButton 
            active={activeTab === 'plans'} 
            icon={<DollarSign size={14} />} 
            label="Plans & Pricing" 
            onClick={() => setActiveTab('plans')} 
          />
          <TabButton 
            active={activeTab === 'features'} 
            icon={<Layers size={14} />} 
            label="Plan Features" 
            onClick={() => setActiveTab('features')} 
          />
          <TabButton 
            active={activeTab === 'payment'} 
            icon={<CreditCard size={14} />} 
            label="Payment Gateway" 
            onClick={() => setActiveTab('payment')} 
          />
          <TabButton 
            active={activeTab === 'cors'} 
            icon={<Globe size={14} />} 
            label="CORS Origins" 
            onClick={() => setActiveTab('cors')} 
          />
          <TabButton 
            active={activeTab === 'system'} 
            icon={<SettingsIcon size={14} />} 
            label="System" 
            onClick={() => setActiveTab('system')} 
          />
        </div>

        {/* Settings Card */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200/50 p-5">
          
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader className="animate-spin text-indigo-600" size={32} />
            </div>
          ) : (
            <>
              {activeTab === 'smtp' && <SMTPSettings 
                settings={smtpSettings}
                onChange={setSmtpSettings}
                testResult={testResult}
                testing={testing}
                onTest={handleTest}
              />}
              
              {activeTab === 'business' && <BusinessSettings 
                settings={businessSettings}
                onChange={setBusinessSettings}
              />}
              
              {activeTab === 'plans' && <PlanSettings 
                settings={planSettings}
                onChange={setPlanSettings}
              />}
              
              {activeTab === 'payment' && <PaymentGatewaySettings 
                settings={paymentSettings}
                onChange={setPaymentSettings}
              />}
              
              {activeTab === 'features' && <PlanFeaturesSettings 
                settings={planFeatures}
                onChange={setPlanFeatures}
              />}
              
              {activeTab === 'cors' && <CorsOriginsSettings 
                settings={corsOrigins}
                onChange={setCorsOrigins}
              />}
              
              {activeTab === 'system' && <SystemSettings 
                settings={systemSettings}
                onChange={setSystemSettings}
              />}

              {/* Save Button */}
              <div className="flex gap-3 mt-6 pt-4 border-t border-slate-100">
                <button
                  onClick={handleSave}
                  disabled={saving}
                  className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-bold text-xs uppercase tracking-wide disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {saving ? (
                    <>
                      <Loader size={14} className="animate-spin" />
                      Saving...
                    </>
                  ) : (
                    <>
                      <Save size={14} />
                      Save Settings
                    </>
                  )}
                </button>
              </div>
            </>
          )}

        </div>

      </div>
    </>
  )
}

// Tab Button Component
function TabButton({ active, icon, label, onClick }) {
  return (
    <button
      onClick={onClick}
      className={`flex items-center gap-2 px-4 py-2 rounded-lg font-bold text-xs uppercase tracking-wide transition-all whitespace-nowrap ${
        active 
          ? 'bg-indigo-600 text-white shadow-md' 
          : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
      }`}
    >
      {icon}
      {label}
    </button>
  )
}

// SMTP Settings Component
function SMTPSettings({ settings, onChange, testResult, testing, onTest }) {
  const handleChange = (field, value) => {
    onChange(prev => ({ ...prev, [field]: value }))
  }

  return (
    <>
      <div className="flex items-center gap-2 mb-4 pb-3 border-b border-slate-100">
        <Mail className="text-indigo-600" size={18} />
        <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wide">
          SMTP Configuration
        </h2>
      </div>

      <div className="space-y-4">
        <div>
          <label className="block text-xs font-bold text-slate-700 mb-1.5 uppercase tracking-wide">
            <Server size={12} className="inline mr-1" />
            SMTP Host
          </label>
          <input
            type="text"
            value={settings.smtp_host}
            onChange={(e) => handleChange('smtp_host', e.target.value)}
            placeholder="smtp.gmail.com"
            className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:border-indigo-500 text-xs"
          />
        </div>

        <div>
          <label className="block text-xs font-bold text-slate-700 mb-1.5 uppercase tracking-wide">Port</label>
          <input
            type="number"
            value={settings.smtp_port}
            onChange={(e) => handleChange('smtp_port', parseInt(e.target.value))}
            className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:border-indigo-500 text-xs"
          />
        </div>

        <div>
          <label className="block text-xs font-bold text-slate-700 mb-1.5 uppercase tracking-wide">Username</label>
          <input
            type="text"
            value={settings.smtp_username}
            onChange={(e) => handleChange('smtp_username', e.target.value)}
            className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:border-indigo-500 text-xs"
          />
        </div>

        <div>
          <label className="block text-xs font-bold text-slate-700 mb-1.5 uppercase tracking-wide">
            <Lock size={12} className="inline mr-1" />
            Password (Encrypted)
          </label>
          <input
            type="password"
            value={settings.smtp_password}
            onChange={(e) => handleChange('smtp_password', e.target.value)}
            className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:border-indigo-500 text-xs"
          />
        </div>

        <div>
          <label className="block text-xs font-bold text-slate-700 mb-1.5 uppercase tracking-wide">From Email</label>
          <input
            type="email"
            value={settings.smtp_from_email}
            onChange={(e) => handleChange('smtp_from_email', e.target.value)}
            className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:border-indigo-500 text-xs"
          />
        </div>

        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            id="use_tls"
            checked={settings.smtp_use_tls}
            onChange={(e) => handleChange('smtp_use_tls', e.target.checked)}
            className="w-4 h-4 text-indigo-600 border-slate-300 rounded"
          />
          <label htmlFor="use_tls" className="text-xs font-bold text-slate-700 uppercase">Use TLS</label>
        </div>
      </div>

      {testResult && (
        <div className={`mt-4 p-3 rounded-lg flex items-center gap-2 text-xs ${
          testResult.success ? 'bg-emerald-50 text-emerald-700' : 'bg-red-50 text-red-700'
        }`}>
          {testResult.success ? <CheckCircle size={16} /> : <XCircle size={16} />}
          <span className="font-bold">{testResult.message}</span>
        </div>
      )}

      <button
        onClick={onTest}
        disabled={testing}
        className="mt-4 w-full flex items-center justify-center gap-2 px-4 py-2 bg-slate-100 text-slate-700 rounded-lg hover:bg-slate-200 font-bold text-xs uppercase disabled:opacity-50"
      >
        {testing ? <><Loader size={14} className="animate-spin" />Testing...</> : <><TestTube size={14} />Test Connection</>}
      </button>
    </>
  )
}

// Business Settings Component
function BusinessSettings({ settings, onChange }) {
  const handleChange = (field, value) => {
    onChange(prev => ({ ...prev, [field]: value }))
  }

  return (
    <>
      <div className="flex items-center gap-2 mb-4 pb-3 border-b border-slate-100">
        <Building2 className="text-indigo-600" size={18} />
        <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wide">
          Business Information
        </h2>
      </div>

      <div className="space-y-4">
        <div>
          <label className="block text-xs font-bold text-slate-700 mb-1.5 uppercase">Company Name</label>
          <input
            type="text"
            value={settings.app_name}
            onChange={(e) => handleChange('app_name', e.target.value)}
            className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:border-indigo-500 text-xs"
          />
        </div>

        <div>
          <label className="block text-xs font-bold text-slate-700 mb-1.5 uppercase">Support Email</label>
          <input
            type="email"
            value={settings.support_email}
            onChange={(e) => handleChange('support_email', e.target.value)}
            className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:border-indigo-500 text-xs"
          />
        </div>

        <div>
          <label className="block text-xs font-bold text-slate-700 mb-1.5 uppercase">Frontend URL</label>
          <input
            type="text"
            value={settings.frontend_url}
            onChange={(e) => handleChange('frontend_url', e.target.value)}
            className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:border-indigo-500 text-xs"
          />
        </div>

        <div>
          <label className="block text-xs font-bold text-slate-700 mb-1.5 uppercase">Company Address</label>
          <textarea
            value={settings.company_address}
            onChange={(e) => handleChange('company_address', e.target.value)}
            rows={3}
            className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:border-indigo-500 text-xs"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1.5 uppercase">GST Number</label>
            <input
              type="text"
              value={settings.company_gst}
              onChange={(e) => handleChange('company_gst', e.target.value)}
              className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:border-indigo-500 text-xs"
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1.5 uppercase">Phone</label>
            <input
              type="text"
              value={settings.company_phone}
              onChange={(e) => handleChange('company_phone', e.target.value)}
              className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:border-indigo-500 text-xs"
            />
          </div>
        </div>

        <div>
          <label className="block text-xs font-bold text-slate-700 mb-1.5 uppercase">Invoice Footer Text</label>
          <textarea
            value={settings.invoice_footer}
            onChange={(e) => handleChange('invoice_footer', e.target.value)}
            rows={2}
            className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:border-indigo-500 text-xs"
          />
        </div>
      </div>
    </>
  )
}

// Plan Settings Component
function PlanSettings({ settings, onChange }) {
  const handleChange = (field, value) => {
    onChange(prev => ({ ...prev, [field]: value }))
  }

  return (
    <>
      <div className="flex items-center gap-2 mb-4 pb-3 border-b border-slate-100">
        <DollarSign className="text-indigo-600" size={18} />
        <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wide">
          Plans & Pricing Configuration
        </h2>
      </div>

      <div className="space-y-4">
        <div>
          <label className="block text-xs font-bold text-slate-700 mb-1.5 uppercase">Trial Period (Days)</label>
          <input
            type="number"
            value={settings.trial_days}
            onChange={(e) => handleChange('trial_days', parseInt(e.target.value))}
            className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:border-indigo-500 text-xs"
          />
        </div>

        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1.5 uppercase">Free Grace Days</label>
            <input
              type="number"
              value={settings.free_offline_grace}
              onChange={(e) => handleChange('free_offline_grace', parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:border-indigo-500 text-xs"
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1.5 uppercase">Basic Grace Days</label>
            <input
              type="number"
              value={settings.basic_offline_grace}
              onChange={(e) => handleChange('basic_offline_grace', parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:border-indigo-500 text-xs"
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1.5 uppercase">Premium Grace Days</label>
            <input
              type="number"
              value={settings.premium_offline_grace}
              onChange={(e) => handleChange('premium_offline_grace', parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:border-indigo-500 text-xs"
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1.5 uppercase">Basic Plan Price (₹)</label>
            <input
              type="number"
              value={settings.basic_price / 100}
              onChange={(e) => handleChange('basic_price', parseInt(e.target.value) * 100)}
              className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:border-indigo-500 text-xs"
            />
            <p className="text-[10px] text-slate-500 mt-1">Currently: ₹{settings.basic_price / 100}</p>
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1.5 uppercase">Premium Plan Price (₹)</label>
            <input
              type="number"
              value={settings.premium_price / 100}
              onChange={(e) => handleChange('premium_price', parseInt(e.target.value) * 100)}
              className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:border-indigo-500 text-xs"
            />
            <p className="text-[10px] text-slate-500 mt-1">Currently: ₹{settings.premium_price / 100}</p>
          </div>
        </div>

        <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg">
          <p className="text-[10px] text-amber-800 font-bold">⚠️ Note: Price changes will apply to new subscriptions only.</p>
        </div>
      </div>
    </>
  )
}

// System Settings Component
function SystemSettings({ settings, onChange }) {
  const handleChange = (field, value) => {
    onChange(prev => ({ ...prev, [field]: value }))
  }

  return (
    <>
      <div className="flex items-center gap-2 mb-4 pb-3 border-b border-slate-100">
        <SettingsIcon className="text-indigo-600" size={18} />
        <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wide">
          System Configuration
        </h2>
      </div>

      <div className="space-y-4">
        <div>
          <label className="block text-xs font-bold text-slate-700 mb-1.5 uppercase">
            <Clock size={12} className="inline mr-1" />
            Access Token Expiry (Minutes)
          </label>
          <input
            type="number"
            value={settings.access_token_expire_minutes}
            onChange={(e) => handleChange('access_token_expire_minutes', parseInt(e.target.value))}
            className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:border-indigo-500 text-xs"
          />
        </div>

        <div>
          <label className="block text-xs font-bold text-slate-700 mb-1.5 uppercase">Max Login Attempts</label>
          <input
            type="number"
            value={settings.max_login_attempts}
            onChange={(e) => handleChange('max_login_attempts', parseInt(e.target.value))}
            className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:border-indigo-500 text-xs"
          />
        </div>

        <div>
          <label className="block text-xs font-bold text-slate-700 mb-1.5 uppercase">Session Timeout (Minutes)</label>
          <input
            type="number"
            value={settings.session_timeout_minutes}
            onChange={(e) => handleChange('session_timeout_minutes', parseInt(e.target.value))}
            className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:border-indigo-500 text-xs"
          />
        </div>

        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            id="maintenance_mode"
            checked={settings.maintenance_mode}
            onChange={(e) => handleChange('maintenance_mode', e.target.checked)}
            className="w-4 h-4 text-indigo-600 border-slate-300 rounded"
          />
          <label htmlFor="maintenance_mode" className="text-xs font-bold text-slate-700 uppercase">
            Maintenance Mode (Block all users)
          </label>
        </div>

        {settings.maintenance_mode && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-[10px] text-red-800 font-bold">⚠️ Warning: Maintenance mode is enabled. All users will be blocked!</p>
          </div>
        )}
      </div>
    </>
  )
}

// Payment Gateway Settings Component
function PaymentGatewaySettings({ settings, onChange }) {
  const handleChange = (field, value) => {
    onChange(prev => ({ ...prev, [field]: value }))
  }

  return (
    <>
      <div className="flex items-center gap-2 mb-4 pb-3 border-b border-slate-100">
        <CreditCard className="text-indigo-600" size={18} />
        <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wide">
          Payment Gateway Configuration
        </h2>
      </div>

      <div className="space-y-4">
        <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-[10px] text-blue-800 font-bold">
            💡 Tip: Credentials are encrypted and stored securely in database. You can easily switch to PhonePe, Stripe, or other gateways in future.
          </p>
        </div>

        <div>
          <label className="block text-xs font-bold text-slate-700 mb-1.5 uppercase">Payment Gateway Mode</label>
          <select
            value={settings.payment_gateway_mode}
            onChange={(e) => handleChange('payment_gateway_mode', e.target.value)}
            className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:border-indigo-500 text-xs"
          >
            <option value="test">Test Mode (Sandbox)</option>
            <option value="live">Live Mode (Production)</option>
          </select>
          <p className="text-[9px] text-slate-500 mt-1">
            {settings.payment_gateway_mode === 'test' ? '🧪 Test mode - use test credentials' : '🔴 Live mode - real transactions'}
          </p>
        </div>

        <div>
          <label className="block text-xs font-bold text-slate-700 mb-1.5 uppercase">Razorpay Key ID</label>
          <input
            type="text"
            value={settings.razorpay_key_id}
            onChange={(e) => handleChange('razorpay_key_id', e.target.value)}
            placeholder="rzp_test_xxxxxxxxxx or rzp_live_xxxxxxxxxx"
            className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:border-indigo-500 text-xs font-mono"
          />
        </div>

        <div>
          <label className="block text-xs font-bold text-slate-700 mb-1.5 uppercase">
            <Lock size={12} className="inline mr-1" />
            Razorpay Key Secret (Encrypted)
          </label>
          <input
            type="password"
            value={settings.razorpay_key_secret}
            onChange={(e) => handleChange('razorpay_key_secret', e.target.value)}
            placeholder="Enter secret key"
            className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:border-indigo-500 text-xs font-mono"
          />
          <p className="text-[9px] text-slate-500 mt-1">🔒 Stored encrypted with AES-128</p>
        </div>

        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            id="payment_gateway_enabled"
            checked={settings.payment_gateway_enabled}
            onChange={(e) => handleChange('payment_gateway_enabled', e.target.checked)}
            className="w-4 h-4 text-indigo-600 border-slate-300 rounded"
          />
          <label htmlFor="payment_gateway_enabled" className="text-xs font-bold text-slate-700 uppercase">
            Enable Payment Gateway
          </label>
        </div>

        {!settings.payment_gateway_enabled && (
          <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg">
            <p className="text-[10px] text-amber-800 font-bold">⚠️ Payment gateway is disabled. Users cannot make payments.</p>
          </div>
        )}

        <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg">
          <p className="text-[10px] text-slate-700 font-bold mb-2">📝 How to get Razorpay credentials:</p>
          <ol className="text-[9px] text-slate-600 space-y-1 ml-4 list-decimal">
            <li>Go to <a href="https://dashboard.razorpay.com/" target="_blank" rel="noopener noreferrer" className="text-indigo-600 underline">Razorpay Dashboard</a></li>
            <li>Navigate to Settings → API Keys</li>
            <li>Generate keys for Test or Live mode</li>
            <li>Copy Key ID and Key Secret</li>
            <li>Paste here and save</li>
          </ol>
        </div>
      </div>
    </>
  )
}

// Plan Features Settings Component
function PlanFeaturesSettings({ settings, onChange }) {
  const [newFeature, setNewFeature] = useState({ plan: 'trial', feature: '' })

  const addFeature = (plan) => {
    if (!newFeature.feature.trim()) return
    
    onChange(prev => ({
      ...prev,
      [plan]: [...prev[plan], newFeature.feature.trim()]
    }))
    setNewFeature({ plan, feature: '' })
  }

  const removeFeature = (plan, index) => {
    onChange(prev => ({
      ...prev,
      [plan]: prev[plan].filter((_, i) => i !== index)
    }))
  }

  const allFeatures = [
    'attendance_face', 'attendance_basic', 'employees_unlimited', 'employees_5', 
    'employees_25', 'salary_full', 'salary_basic', 'tax', 'loans', 
    'export_pdf', 'export_excel', 'leaves', 'reports_full', 'reports_basic', 
    'holidays', '*'
  ]

  return (
    <>
      <div className="flex items-center gap-2 mb-4 pb-3 border-b border-slate-100">
        <Layers className="text-indigo-600" size={18} />
        <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wide">
          Plan Features Configuration
        </h2>
      </div>

      <div className="space-y-6">
        <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-[10px] text-blue-800 font-bold">
            💡 Tip: Control which features are available for each plan. Use "*" for all features (Premium plan).
          </p>
        </div>

        {/* Trial Plan */}
        <div className="border border-slate-200 rounded-lg p-4">
          <h3 className="text-xs font-bold text-slate-900 uppercase mb-3">Trial Plan Features</h3>
          <div className="flex flex-wrap gap-2 mb-3">
            {settings.trial.map((feature, index) => (
              <span key={index} className="px-2 py-1 bg-amber-100 text-amber-700 rounded text-xs font-bold flex items-center gap-1">
                {feature}
                <button onClick={() => removeFeature('trial', index)} className="hover:text-amber-900">
                  <X size={12} />
                </button>
              </span>
            ))}
          </div>
          <div className="flex gap-2">
            <select
              value={newFeature.plan === 'trial' ? newFeature.feature : ''}
              onChange={(e) => setNewFeature({ plan: 'trial', feature: e.target.value })}
              className="flex-1 px-3 py-2 border border-slate-200 rounded-lg text-xs"
            >
              <option value="">Select feature to add...</option>
              {allFeatures.filter(f => !settings.trial.includes(f)).map(f => (
                <option key={f} value={f}>{f}</option>
              ))}
            </select>
            <button
              onClick={() => addFeature('trial')}
              className="px-4 py-2 bg-amber-600 text-white rounded-lg text-xs font-bold hover:bg-amber-700"
            >
              Add
            </button>
          </div>
        </div>

        {/* Free Plan */}
        <div className="border border-slate-200 rounded-lg p-4">
          <h3 className="text-xs font-bold text-slate-900 uppercase mb-3">Free Plan Features</h3>
          <div className="flex flex-wrap gap-2 mb-3">
            {settings.free.map((feature, index) => (
              <span key={index} className="px-2 py-1 bg-slate-100 text-slate-700 rounded text-xs font-bold flex items-center gap-1">
                {feature}
                <button onClick={() => removeFeature('free', index)} className="hover:text-slate-900">
                  <X size={12} />
                </button>
              </span>
            ))}
          </div>
          <div className="flex gap-2">
            <select
              value={newFeature.plan === 'free' ? newFeature.feature : ''}
              onChange={(e) => setNewFeature({ plan: 'free', feature: e.target.value })}
              className="flex-1 px-3 py-2 border border-slate-200 rounded-lg text-xs"
            >
              <option value="">Select feature to add...</option>
              {allFeatures.filter(f => !settings.free.includes(f)).map(f => (
                <option key={f} value={f}>{f}</option>
              ))}
            </select>
            <button
              onClick={() => addFeature('free')}
              className="px-4 py-2 bg-slate-600 text-white rounded-lg text-xs font-bold hover:bg-slate-700"
            >
              Add
            </button>
          </div>
        </div>

        {/* Basic Plan */}
        <div className="border border-slate-200 rounded-lg p-4">
          <h3 className="text-xs font-bold text-slate-900 uppercase mb-3">Basic Plan Features</h3>
          <div className="flex flex-wrap gap-2 mb-3">
            {settings.basic.map((feature, index) => (
              <span key={index} className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs font-bold flex items-center gap-1">
                {feature}
                <button onClick={() => removeFeature('basic', index)} className="hover:text-blue-900">
                  <X size={12} />
                </button>
              </span>
            ))}
          </div>
          <div className="flex gap-2">
            <select
              value={newFeature.plan === 'basic' ? newFeature.feature : ''}
              onChange={(e) => setNewFeature({ plan: 'basic', feature: e.target.value })}
              className="flex-1 px-3 py-2 border border-slate-200 rounded-lg text-xs"
            >
              <option value="">Select feature to add...</option>
              {allFeatures.filter(f => !settings.basic.includes(f)).map(f => (
                <option key={f} value={f}>{f}</option>
              ))}
            </select>
            <button
              onClick={() => addFeature('basic')}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg text-xs font-bold hover:bg-blue-700"
            >
              Add
            </button>
          </div>
        </div>

        {/* Premium Plan */}
        <div className="border border-slate-200 rounded-lg p-4">
          <h3 className="text-xs font-bold text-slate-900 uppercase mb-3">Premium Plan Features</h3>
          <div className="flex flex-wrap gap-2 mb-3">
            {settings.premium.map((feature, index) => (
              <span key={index} className="px-2 py-1 bg-purple-100 text-purple-700 rounded text-xs font-bold flex items-center gap-1">
                {feature}
                <button onClick={() => removeFeature('premium', index)} className="hover:text-purple-900">
                  <X size={12} />
                </button>
              </span>
            ))}
          </div>
          <div className="flex gap-2">
            <select
              value={newFeature.plan === 'premium' ? newFeature.feature : ''}
              onChange={(e) => setNewFeature({ plan: 'premium', feature: e.target.value })}
              className="flex-1 px-3 py-2 border border-slate-200 rounded-lg text-xs"
            >
              <option value="">Select feature to add...</option>
              {allFeatures.filter(f => !settings.premium.includes(f)).map(f => (
                <option key={f} value={f}>{f}</option>
              ))}
            </select>
            <button
              onClick={() => addFeature('premium')}
              className="px-4 py-2 bg-purple-600 text-white rounded-lg text-xs font-bold hover:bg-purple-700"
            >
              Add
            </button>
          </div>
          <p className="text-[9px] text-slate-500 mt-2">💡 Use "*" for all features</p>
        </div>
      </div>
    </>
  )
}

// CORS Origins Settings Component
function CorsOriginsSettings({ settings, onChange }) {
  const [newOrigin, setNewOrigin] = useState('')

  const addOrigin = () => {
    if (!newOrigin.trim()) return
    if (!newOrigin.startsWith('http://') && !newOrigin.startsWith('https://')) {
      alert('Origin must start with http:// or https://')
      return
    }
    
    onChange(prev => ({
      ...prev,
      origins: [...prev.origins, newOrigin.trim()]
    }))
    setNewOrigin('')
  }

  const removeOrigin = (index) => {
    onChange(prev => ({
      ...prev,
      origins: prev.origins.filter((_, i) => i !== index)
    }))
  }

  return (
    <>
      <div className="flex items-center gap-2 mb-4 pb-3 border-b border-slate-100">
        <Globe className="text-indigo-600" size={18} />
        <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wide">
          CORS Origins Configuration
        </h2>
      </div>

      <div className="space-y-4">
        <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg">
          <p className="text-[10px] text-amber-800 font-bold">
            ⚠️ Warning: Server restart required for CORS changes to take effect!
          </p>
        </div>

        <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-[10px] text-blue-800 font-bold mb-2">
            💡 What is CORS? Cross-Origin Resource Sharing allows your API to be accessed from different domains.
          </p>
          <p className="text-[9px] text-blue-700">
            Add domains that should be allowed to access your API. Example: https://app.example.com
          </p>
        </div>

        <div>
          <label className="block text-xs font-bold text-slate-700 mb-2 uppercase">Allowed Origins</label>
          <div className="space-y-2 mb-3">
            {settings.origins.length === 0 ? (
              <p className="text-xs text-slate-400 italic">No origins configured. Add one below.</p>
            ) : (
              settings.origins.map((origin, index) => (
                <div key={index} className="flex items-center gap-2 p-2 bg-slate-50 rounded-lg">
                  <Globe size={14} className="text-slate-400" />
                  <span className="flex-1 text-xs font-mono text-slate-700">{origin}</span>
                  <button
                    onClick={() => removeOrigin(index)}
                    className="p-1 text-red-600 hover:text-red-800 hover:bg-red-50 rounded"
                  >
                    <X size={14} />
                  </button>
                </div>
              ))
            )}
          </div>

          <div className="flex gap-2">
            <input
              type="text"
              value={newOrigin}
              onChange={(e) => setNewOrigin(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && addOrigin()}
              placeholder="https://app.example.com"
              className="flex-1 px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:border-indigo-500 text-xs font-mono"
            />
            <button
              onClick={addOrigin}
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg text-xs font-bold hover:bg-indigo-700"
            >
              Add Origin
            </button>
          </div>
        </div>

        <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg">
          <p className="text-[10px] text-slate-700 font-bold mb-2">📝 Common Use Cases:</p>
          <ul className="text-[9px] text-slate-600 space-y-1 ml-4 list-disc">
            <li>Development: http://localhost:3000, http://localhost:3441</li>
            <li>Production: https://app.yourdomain.com</li>
            <li>Multiple domains: Add each domain separately</li>
            <li>Subdomains: Add each subdomain (e.g., https://admin.example.com)</li>
          </ul>
        </div>
      </div>
    </>
  )
}

export default Settings
