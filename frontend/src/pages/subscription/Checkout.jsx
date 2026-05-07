import React, { useEffect, useState } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8661'

// Plan prices in paise
const PLAN_PRICES = {
  basic: 49900,   // ₹499
  premium: 99900  // ₹999
}

function Checkout() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const licenseKey = searchParams.get('key')
  const plan = searchParams.get('plan') || 'basic'
  const [loading, setLoading] = useState(false)
  const [status, setStatus] = useState('')
  
  // Promo code state
  const [promoCode, setPromoCode] = useState('')
  const [promoApplied, setPromoApplied] = useState(false)
  const [promoValidating, setPromoValidating] = useState(false)
  const [promoError, setPromoError] = useState('')
  const [discountInfo, setDiscountInfo] = useState(null)
  const [finalAmount, setFinalAmount] = useState(PLAN_PRICES[plan] || 50000)

  // Razorpay Script लोड करा
  useEffect(() => {
    const script = document.createElement('script')
    script.src = 'https://checkout.razorpay.com/v1/checkout.js'
    script.async = true
    document.body.appendChild(script)
  }, [])

  // Apply promo code
  const handleApplyPromo = async () => {
    if (!promoCode.trim()) {
      setPromoError('Please enter a promo code')
      return
    }

    setPromoValidating(true)
    setPromoError('')
    
    try {
      const { data } = await axios.post(`${API_URL}/api/promo/validate`, {
        code: promoCode,
        plan: plan,
        customer_id: null // Optional for public validation
      })

      if (data.valid) {
        setPromoApplied(true)
        setDiscountInfo(data)
        setFinalAmount(data.final_amount)
        setPromoError('')
      } else {
        setPromoError(data.reason || 'Invalid promo code')
        setPromoApplied(false)
        setDiscountInfo(null)
      }
    } catch (err) {
      console.error('Promo validation error:', err)
      setPromoError('Failed to validate promo code')
      setPromoApplied(false)
      setDiscountInfo(null)
    } finally {
      setPromoValidating(false)
    }
  }

  // Remove promo code
  const handleRemovePromo = () => {
    setPromoCode('')
    setPromoApplied(false)
    setDiscountInfo(null)
    setPromoError('')
    setFinalAmount(PLAN_PRICES[plan] || 50000)
  }

  const handlePayment = async () => {
    if (!licenseKey) return alert("License key missing!")
    
    setLoading(true)
    try {
      // license_key वापरून order create करा — customer_id लागत नाही
      const { data: order } = await axios.post(`${API_URL}/api/license/create-order`, {
        license_key: licenseKey,
        amount: finalAmount,
        plan: plan
      })

      const options = {
        key: import.meta.env.VITE_RAZORPAY_KEY_ID || 'rzp_test_xxxxxxxxxx',
        amount: order.amount,
        currency: order.currency,
        name: "SalaryPay",
        description: `${plan.charAt(0).toUpperCase() + plan.slice(1)} Plan`,
        order_id: order.id,
        handler: async (response) => {
          try {
            // verify-payment ला license_key पाठवा
            const verifyRes = await axios.post(`${API_URL}/api/license/verify-payment`, {
              razorpay_order_id: response.razorpay_order_id,
              razorpay_payment_id: response.razorpay_payment_id,
              razorpay_signature: response.razorpay_signature,
              license_key: licenseKey
            })
            if (verifyRes.data.status === 'success') {
              alert(`✅ Payment Successful! License extended till ${new Date(verifyRes.data.new_expiry).toLocaleDateString()}`)
              navigate('/')
            }
          } catch (err) {
            alert("Payment verification failed!")
          }
        },
        prefill: { name: "Customer" },
        theme: { color: "#4f46e5" },
      }

      const rzp = new window.Razorpay(options)
      rzp.open()
    } catch (err) {
      console.error(err)
      alert("Error creating order")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
      <div className="bg-white max-w-md w-full rounded-3xl shadow-xl p-8 border border-slate-100">
        <div className="text-center mb-8">
          <div className="w-20 h-20 bg-indigo-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-10 h-10 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
            </svg>
          </div>
          <h2 className="text-3xl font-extrabold text-slate-900">Upgrade to {plan.charAt(0).toUpperCase() + plan.slice(1)}</h2>
          <p className="text-slate-500 mt-2">Get 1 year of full access to SalaryPay HRMS</p>
        </div>

        <div className="bg-slate-50 rounded-2xl p-6 mb-6 border border-slate-100">
          <div className="flex justify-between mb-4">
            <span className="text-slate-500 font-medium">License Key</span>
            <span className="text-slate-900 font-bold font-mono text-sm">{licenseKey?.substring(0, 10)}...</span>
          </div>
          <div className="flex justify-between mb-4">
            <span className="text-slate-500 font-medium">Plan</span>
            <span className="text-slate-900 font-bold">{plan.charAt(0).toUpperCase() + plan.slice(1)}</span>
          </div>
          <div className="flex justify-between mb-4">
            <span className="text-slate-500 font-medium">Base Amount</span>
            <span className="text-slate-900 font-bold">₹{(PLAN_PRICES[plan] / 100).toFixed(2)}</span>
          </div>
          
          {/* Discount Display */}
          {promoApplied && discountInfo && (
            <div className="flex justify-between mb-4 text-green-600">
              <span className="font-medium">Discount ({promoCode})</span>
              <span className="font-bold">-₹{(discountInfo.discount_amount / 100).toFixed(2)}</span>
            </div>
          )}
          
          <div className="flex justify-between border-t border-slate-200 pt-4">
            <span className="text-slate-900 font-bold">Total Amount</span>
            <span className="text-indigo-600 font-extrabold text-xl">₹{(finalAmount / 100).toFixed(2)}</span>
          </div>
        </div>

        {/* Promo Code Section */}
        <div className="mb-6">
          <label className="block text-slate-700 font-medium mb-2 text-sm">Have a promo code?</label>
          {!promoApplied ? (
            <div className="flex gap-2">
              <input
                type="text"
                value={promoCode}
                onChange={(e) => setPromoCode(e.target.value.toUpperCase())}
                placeholder="Enter promo code"
                className="flex-1 px-4 py-2 border border-slate-300 rounded-xl focus:outline-none focus:border-indigo-500 text-sm uppercase"
                disabled={promoValidating}
              />
              <button
                onClick={handleApplyPromo}
                disabled={promoValidating || !promoCode.trim()}
                className="px-6 py-2 bg-slate-600 text-white rounded-xl font-bold hover:bg-slate-700 active:scale-95 transition-all disabled:opacity-50 disabled:cursor-not-allowed text-sm"
              >
                {promoValidating ? "Checking..." : "Apply"}
              </button>
            </div>
          ) : (
            <div className="flex items-center justify-between bg-green-50 border border-green-200 rounded-xl px-4 py-3">
              <div className="flex items-center gap-2">
                <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                </svg>
                <span className="text-green-700 font-bold text-sm">{promoCode} applied!</span>
              </div>
              <button
                onClick={handleRemovePromo}
                className="text-green-600 hover:text-green-800 font-bold text-sm"
              >
                Remove
              </button>
            </div>
          )}
          
          {/* Error Message */}
          {promoError && (
            <div className="mt-2 flex items-center gap-2 text-red-600 text-sm">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
              <span>{promoError}</span>
            </div>
          )}
        </div>

        <button
          onClick={handlePayment}
          disabled={loading}
          className="w-full bg-indigo-600 text-white py-4 rounded-2xl font-bold shadow-lg shadow-indigo-100 hover:bg-indigo-700 active:scale-95 transition-all disabled:opacity-50"
        >
          {loading ? "Processing..." : "Pay with Razorpay"}
        </button>
        
        <p className="text-center text-[11px] text-slate-400 mt-6">
          Secure payment processed by Razorpay. 
          By paying, you agree to our terms of service.
        </p>
      </div>
    </div>
  )
}

export default Checkout
