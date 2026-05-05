import React, { useEffect, useState } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8661'

function Checkout() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const licenseKey = searchParams.get('key')
  const [loading, setLoading] = useState(false)
  const [status, setStatus] = useState('')

  // Razorpay Script लोड करा
  useEffect(() => {
    const script = document.createElement('script')
    script.src = 'https://checkout.razorpay.com/v1/checkout.js'
    script.async = true
    document.body.appendChild(script)
  }, [])

  const handlePayment = async () => {
    if (!licenseKey) return alert("License key missing!")
    
    setLoading(true)
    try {
      // १. सर्व्हरवर ऑर्डर तयार करा (Amount Rs. 500 = 50000 paise)
      const { data: order } = await axios.post(`${API_URL}/api/license/create-order`, {
        license_key: licenseKey,
        amount: 50000 
      })

      const options = {
        key: import.meta.env.VITE_RAZORPAY_KEY_ID || 'rzp_test_xxxxxxxxxx',
        amount: order.amount,
        currency: order.currency,
        name: "SalaryPay Premium",
        description: "1 Year License Extension",
        order_id: order.id,
        handler: async (response) => {
          // २. पेमेंट झाल्यावर व्हेरिफाय करा
          try {
            const verifyRes = await axios.post(`${API_URL}/api/license/verify-payment`, {
              ...response,
              license_key: licenseKey
            })
            if (verifyRes.data.status === 'success') {
              alert("✅ Payment Successful! License extended.")
              window.close() // पेमेंट झाल्यावर विंडो बंद करा
            }
          } catch (err) {
            alert("Payment verification failed!")
          }
        },
        prefill: {
          name: "Customer",
          email: "customer@example.com",
        },
        theme: { color: "#4f46e5" }
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
          <h2 className="text-3xl font-extrabold text-slate-900">Upgrade to Premium</h2>
          <p className="text-slate-500 mt-2">Get 1 year of full access to SalaryPay HRMS</p>
        </div>

        <div className="bg-slate-50 rounded-2xl p-6 mb-8 border border-slate-100">
          <div className="flex justify-between mb-4">
            <span className="text-slate-500 font-medium">License Key</span>
            <span className="text-slate-900 font-bold font-mono text-sm">{licenseKey?.substring(0, 10)}...</span>
          </div>
          <div className="flex justify-between border-t border-slate-200 pt-4">
            <span className="text-slate-900 font-bold">Total Amount</span>
            <span className="text-indigo-600 font-extrabold text-xl">₹500.00</span>
          </div>
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
