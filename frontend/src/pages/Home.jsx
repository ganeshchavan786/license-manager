import React from 'react'
import { Link } from 'react-router-dom'
import { 
  ShieldCheck, 
  Zap, 
  BarChart3, 
  Globe, 
  CheckCircle2, 
  ArrowRight,
  ChevronRight,
  Server,
  Lock,
  Smartphone
} from 'lucide-react'

const PLANS = [
  {
    id: "free",
    name: "Free",
    price: "0",
    description: "Ideal for small teams and startups starting their journey.",
    color: "slate",
    features: ["5 Employees", "Basic Attendance", "Leave Management", "Community Support"]
  },
  {
    id: "basic",
    name: "Basic",
    price: "499",
    description: "Full-featured HRMS for growing businesses.",
    color: "indigo",
    popular: false,
    features: ["25 Employees", "Face Recognition", "Salary System", "Tax & TDS", "Export Reports"]
  },
  {
    id: "premium",
    name: "Premium",
    price: "999",
    description: "Unlimited power for large enterprises and corporations.",
    color: "purple",
    popular: true,
    features: ["Unlimited Employees", "Face Recognition", "Priority Support", "Loans & TDS", "Audit Logs"]
  }
]

function Home() {
  return (
    <div className="min-h-screen bg-white font-sans selection:bg-indigo-100 selection:text-indigo-900">
      {/* Navbar */}
      <nav className="fixed top-0 w-full bg-white/80 backdrop-blur-md z-50 border-b border-slate-100">
        <div className="max-w-7xl mx-auto px-6 h-16 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center shadow-lg shadow-indigo-200">
              <Zap className="text-white" size={18} fill="white" />
            </div>
            <span className="text-lg font-black text-slate-900 tracking-tight">SalaryPay</span>
          </div>
          <div className="hidden md:flex gap-8 text-sm font-bold text-slate-500">
            <a href="#features" className="hover:text-indigo-600 transition-colors">Features</a>
            <a href="#pricing" className="hover:text-indigo-600 transition-colors">Pricing</a>
            <a href="#about" className="hover:text-indigo-600 transition-colors">Why Us</a>
          </div>
          <div className="flex items-center gap-4">
            <Link to="/invoices" className="text-sm font-bold text-slate-600 hover:text-indigo-600 transition-colors">My Invoices</Link>
            <Link to="/admin/login" className="text-sm font-bold text-slate-600 hover:text-indigo-600 transition-colors">Admin Login</Link>
            <a href="#pricing" className="bg-slate-900 text-white px-5 py-2.5 rounded-xl text-sm font-bold hover:bg-indigo-600 transition-all shadow-xl shadow-slate-200">View Plans</a>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-6">
        <div className="max-w-7xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 bg-indigo-50 border border-indigo-100 px-4 py-1.5 rounded-full text-indigo-600 text-xs font-bold mb-8 animate-bounce">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-indigo-500"></span>
            </span>
            New: Face Recognition Attendance v2.0
          </div>
          <h1 className="text-5xl md:text-7xl font-black text-slate-900 mb-6 leading-tight tracking-tight">
            Manage your Software <br />
            <span className="text-indigo-600">Licenses</span> with ease.
          </h1>
          <p className="text-slate-500 text-lg md:text-xl max-w-2xl mx-auto mb-10 font-medium">
            The world's most powerful license management system for SalaryPay HRMS. 
            Zero-touch activation, offline support, and real-time analytics.
          </p>
          <div className="flex flex-col md:flex-row gap-4 justify-center items-center">
            <a href="https://your-download-link.com" target="_blank" className="w-full md:w-auto bg-indigo-600 text-white px-8 py-4 rounded-2xl text-lg font-bold hover:bg-indigo-700 transition-all shadow-2xl shadow-indigo-200 flex items-center justify-center gap-2">
              Download SalaryPay <ArrowRight size={20} />
            </a>
            <a href="#pricing" className="w-full md:w-auto px-8 py-4 rounded-2xl text-lg font-bold text-slate-600 hover:bg-slate-50 transition-all flex items-center justify-center gap-2">
              View Pricing <ChevronRight size={20} />
            </a>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section id="features" className="py-20 bg-slate-50 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-black text-slate-900 mb-4 uppercase tracking-tight">Powering Modern HRMS</h2>
            <p className="text-slate-500 font-medium">Designed for performance, security, and scalability.</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <FeatureCard 
              icon={<Zap className="text-amber-500" />}
              title="Zero-Touch Activation"
              desc="Automatic machine ID detection means your customers never have to type a license key."
            />
            <FeatureCard 
              icon={<ShieldCheck className="text-emerald-500" />}
              title="Offline Resilience"
              desc="Built-in 5-day grace period keeps the software running even when the internet goes out."
            />
            <FeatureCard 
              icon={<BarChart3 className="text-indigo-500" />}
              title="Real-time Analytics"
              desc="Monitor your business growth, revenue, and active trials from a single unified dashboard."
            />
            <FeatureCard 
              icon={<Globe className="text-blue-500" />}
              title="Scalable Infrastructure"
              desc="Host your own license server on any VPS and manage thousands of instances effortlessly."
            />
            <FeatureCard 
              icon={<Lock className="text-purple-500" />}
              title="Enterprise Security"
              desc="PBKDF2 hashing and JWT tokens ensure that your customer data is always protected."
            />
            <FeatureCard 
              icon={<Smartphone className="text-rose-500" />}
              title="Mobile Ready"
              desc="Manage your entire licensing business from your phone with our fully responsive dashboard."
            />
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-20 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-black text-slate-900 mb-4 uppercase tracking-tight">Simple, Transparent Pricing</h2>
            <p className="text-slate-500 font-medium">Choose the plan that fits your business needs.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {PLANS.map((plan) => (
              <div key={plan.id} className={`relative bg-white p-8 rounded-[2.5rem] border ${plan.popular ? 'border-indigo-600 shadow-2xl shadow-indigo-100 ring-4 ring-indigo-50' : 'border-slate-200'}`}>
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-indigo-600 text-white px-4 py-1 rounded-full text-xs font-black uppercase tracking-widest shadow-lg">
                    Most Popular
                  </div>
                )}
                <h3 className={`text-xl font-black mb-2 text-${plan.color}-600`}>{plan.name}</h3>
                <p className="text-slate-400 text-sm mb-6 font-medium">{plan.description}</p>
                <div className="flex items-baseline gap-1 mb-8">
                  <span className="text-4xl font-black text-slate-900">₹{plan.price}</span>
                  <span className="text-slate-400 font-bold">/month</span>
                </div>
                
                <ul className="space-y-4 mb-8">
                  {plan.features.map((f, i) => (
                    <li key={i} className="flex items-center gap-3 text-sm text-slate-600 font-medium">
                      <CheckCircle2 size={18} className="text-indigo-500 shrink-0" />
                      {f}
                    </li>
                  ))}
                </ul>

                <a href="https://your-download-link.com" className={`block text-center py-4 rounded-2xl font-black uppercase tracking-widest text-xs transition-all ${
                  plan.popular ? 'bg-indigo-600 text-white hover:bg-indigo-700 shadow-xl shadow-indigo-100' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}>
                  Download App
                </a>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-slate-950 py-20 px-6 text-white overflow-hidden relative">
        <div className="absolute top-0 left-0 w-full h-full opacity-5 pointer-events-none">
          <div className="absolute top-10 left-10 w-96 h-96 bg-indigo-500 rounded-full blur-[100px]" />
          <div className="absolute bottom-10 right-10 w-96 h-96 bg-purple-500 rounded-full blur-[100px]" />
        </div>
        <div className="max-w-7xl mx-auto relative">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-12">
            <div className="md:col-span-2">
              <div className="flex items-center gap-2 mb-6">
                <Zap className="text-indigo-500" size={24} fill="currentColor" />
                <span className="text-2xl font-black tracking-tight">SalaryPay</span>
              </div>
              <p className="text-slate-400 max-w-sm mb-8 font-medium">
                The leading license management platform for SalaryPay HRMS. 
                Securing software worldwide since 2026.
              </p>
            </div>
            <div>
              <h4 className="font-black mb-6 uppercase tracking-widest text-xs text-indigo-400">Product</h4>
              <ul className="space-y-4 text-sm font-bold text-slate-400">
                <li><a href="#" className="hover:text-white transition-colors">Features</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Pricing</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Documentation</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-black mb-6 uppercase tracking-widest text-xs text-indigo-400">Company</h4>
              <ul className="space-y-4 text-sm font-bold text-slate-400">
                <li><a href="#" className="hover:text-white transition-colors">About Us</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Contact</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Privacy Policy</a></li>
              </ul>
            </div>
          </div>
          <div className="mt-20 pt-8 border-t border-slate-900 flex justify-between items-center text-[10px] uppercase font-black tracking-widest text-slate-600">
            <p>© 2026 SalaryPay Infotech. All rights reserved.</p>
            <p>Made with ❤️ for HRs worldwide</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

function FeatureCard({ icon, title, desc }) {
  return (
    <div className="bg-white p-8 rounded-[2.5rem] border border-slate-100 hover:border-indigo-100 transition-all hover:shadow-xl hover:shadow-indigo-50 group">
      <div className="w-14 h-14 bg-slate-50 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
        {React.cloneElement(icon, { size: 28 })}
      </div>
      <h3 className="text-xl font-black text-slate-900 mb-3 tracking-tight">{title}</h3>
      <p className="text-slate-500 text-sm font-medium leading-relaxed">{desc}</p>
    </div>
  )
}

export default Home
