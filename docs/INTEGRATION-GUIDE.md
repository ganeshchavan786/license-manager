# 🔗 Integration Guide - Main Application Madhye

**Step-by-Step Integration** | **Tumchya Existing App Madhye**

---

## 📋 Overview

Tumchya **existing SalaryPay HRMS application** madhye license system integrate kasa karayche:

```
your-salarypay-app/
├── src/
│   ├── components/
│   │   ├── Sidebar.jsx          ← Update (add menu item)
│   │   ├── Navbar.jsx           ← Update (add admin dropdown)
│   │   └── ...
│   ├── pages/
│   │   ├── Dashboard.jsx        ← Your existing dashboard
│   │   ├── Employees.jsx
│   │   ├── Attendance.jsx
│   │   ├── Salary.jsx
│   │   └── admin/
│   │       └── LicenseDashboard.jsx  ← New (copy from our files)
│   ├── services/
│   │   ├── licenseService.js    ← New (copy from our files)
│   │   └── ...
│   ├── context/
│   │   ├── LicenseContext.jsx   ← New (copy from our files)
│   │   └── ...
│   └── App.jsx                  ← Update (add routes)
```

---

## 🚀 Step-by-Step Integration

### **Step 1: Copy Required Files**

```bash
# License service
cp frontend/src/services/licenseService.js your-app/src/services/

# License context
cp frontend/src/context/LicenseContext.jsx your-app/src/context/

# Feature gate component
cp frontend/src/components/common/FeatureGate.jsx your-app/src/components/common/

# Trial banner
cp frontend/src/components/common/TrialBanner.jsx your-app/src/components/common/

# Admin dashboard
cp frontend/src/pages/admin/Dashboard.jsx your-app/src/pages/admin/LicenseDashboard.jsx
cp frontend/src/pages/admin/Dashboard.css your-app/src/pages/admin/LicenseDashboard.css
```

---

### **Step 2: Update App.jsx (Add LicenseProvider)**

```javascript
// your-app/src/App.jsx

import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { LicenseProvider } from './context/LicenseContext';  // ← Add

// Your existing imports
import MainLayout from './layouts/MainLayout';
import Dashboard from './pages/Dashboard';
import Employees from './pages/Employees';
import Attendance from './pages/Attendance';
import Salary from './pages/Salary';

// New imports
import LicenseDashboard from './pages/admin/LicenseDashboard';  // ← Add

function App() {
  return (
    <LicenseProvider>  {/* ← Wrap everything */}
      <Router>
        <Routes>
          {/* Your existing routes */}
          <Route path="/" element={<MainLayout />}>
            <Route index element={<Dashboard />} />
            <Route path="employees" element={<Employees />} />
            <Route path="attendance" element={<Attendance />} />
            <Route path="salary" element={<Salary />} />
            
            {/* New admin route */}
            <Route path="admin/license-dashboard" element={<LicenseDashboard />} />
          </Route>
        </Routes>
      </Router>
    </LicenseProvider>
  );
}

export default App;
```

---

### **Step 3: Update Sidebar (Add Menu Item)**

```javascript
// your-app/src/components/Sidebar.jsx

import { Link, useLocation } from 'react-router-dom';
import { useLicense } from '../context/LicenseContext';  // ← Add

function Sidebar() {
  const location = useLocation();
  const { license } = useLicense();  // ← Add
  
  // Check if user is admin (you can use your own logic)
  const isAdmin = true; // Replace with your admin check
  
  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <h2>SalaryPay HRMS</h2>
        {/* Show current plan */}
        <span className="plan-badge">{license?.plan || 'Free'}</span>
      </div>
      
      <nav className="sidebar-nav">
        {/* Your existing menu items */}
        <Link 
          to="/" 
          className={location.pathname === '/' ? 'active' : ''}
        >
          📊 Dashboard
        </Link>
        
        <Link 
          to="/employees" 
          className={location.pathname === '/employees' ? 'active' : ''}
        >
          👥 Employees
        </Link>
        
        <Link 
          to="/attendance" 
          className={location.pathname === '/attendance' ? 'active' : ''}
        >
          📅 Attendance
        </Link>
        
        <Link 
          to="/salary" 
          className={location.pathname === '/salary' ? 'active' : ''}
        >
          💰 Salary
        </Link>
        
        {/* Admin section */}
        {isAdmin && (
          <>
            <div className="sidebar-divider"></div>
            <div className="sidebar-section-title">Admin</div>
            
            <Link 
              to="/admin/license-dashboard" 
              className={location.pathname === '/admin/license-dashboard' ? 'active' : ''}
            >
              📊 License Dashboard
            </Link>
          </>
        )}
      </nav>
    </div>
  );
}

export default Sidebar;
```

---

### **Step 4: Update MainLayout (Add Trial Banner)**

```javascript
// your-app/src/layouts/MainLayout.jsx

import { Outlet } from 'react-router-dom';
import Sidebar from '../components/Sidebar';
import Navbar from '../components/Navbar';
import TrialBanner from '../components/common/TrialBanner';  // ← Add

function MainLayout() {
  return (
    <div className="main-layout">
      <Sidebar />
      
      <div className="main-content">
        <Navbar />
        
        {/* Trial banner - shows countdown */}
        <TrialBanner />  {/* ← Add */}
        
        <div className="page-content">
          <Outlet />
        </div>
      </div>
    </div>
  );
}

export default MainLayout;
```

---

### **Step 5: Lock Features (Example - Attendance Page)**

```javascript
// your-app/src/pages/Attendance.jsx

import { useState } from 'react';
import FeatureGate from '../components/common/FeatureGate';  // ← Add

function AttendancePage() {
  const [attendanceData, setAttendanceData] = useState([]);
  
  return (
    <div className="attendance-page">
      <h1>Attendance Management</h1>
      
      {/* Manual attendance - available for all */}
      <div className="manual-attendance">
        <h2>Manual Attendance</h2>
        <button onClick={handleManualPunchIn}>Punch In</button>
        <button onClick={handleManualPunchOut}>Punch Out</button>
      </div>
      
      {/* Face recognition - locked for free plan */}
      <FeatureGate feature="attendance_face">
        <div className="face-attendance">
          <h2>Face Recognition Attendance</h2>
          <button onClick={handleFaceRecognition}>
            📸 Start Face Recognition
          </button>
        </div>
      </FeatureGate>
      
      {/* Attendance table */}
      <div className="attendance-table">
        <table>
          {/* Your table code */}
        </table>
      </div>
    </div>
  );
}

export default AttendancePage;
```

---

### **Step 6: Lock Features (Example - Salary Page)**

```javascript
// your-app/src/pages/Salary.jsx

import { useLicense } from '../context/LicenseContext';  // ← Add
import FeatureGate from '../components/common/FeatureGate';  // ← Add

function SalaryPage() {
  const { license } = useLicense();
  const features = license?.features || [];
  
  // Check if tax feature available
  const hasTaxFeature = features.includes('tax');
  
  return (
    <div className="salary-page">
      <h1>Salary Processing</h1>
      
      {/* Basic salary - available for all */}
      <div className="basic-salary">
        <h2>Basic Salary</h2>
        <input type="number" placeholder="Enter basic salary" />
      </div>
      
      {/* Tax calculations - locked for free plan */}
      <FeatureGate feature="tax">
        <div className="tax-section">
          <h2>Tax Calculations</h2>
          <div className="tax-fields">
            <label>Income Tax</label>
            <input type="number" />
            
            <label>Professional Tax</label>
            <input type="number" />
            
            <label>PF Deduction</label>
            <input type="number" />
          </div>
        </div>
      </FeatureGate>
      
      {/* Show message if tax not available */}
      {!hasTaxFeature && (
        <div className="upgrade-message">
          <p>💡 Upgrade to Basic or Premium plan to enable tax calculations</p>
          <button onClick={() => navigate('/plans')}>View Plans</button>
        </div>
      )}
      
      {/* Export buttons - locked for free plan */}
      <div className="export-section">
        <FeatureGate feature="export_pdf">
          <button onClick={handleExportPDF}>📄 Export PDF</button>
        </FeatureGate>
        
        <FeatureGate feature="export_excel">
          <button onClick={handleExportExcel}>📊 Export Excel</button>
        </FeatureGate>
      </div>
    </div>
  );
}

export default SalaryPage;
```

---

### **Step 7: Add Plans Page (For Upgrades)**

```javascript
// your-app/src/pages/Plans.jsx

import { useState } from 'react';
import { createPaymentOrder, verifyPayment } from '../services/licenseService';

function PlansPage() {
  const handleBuyPlan = async (plan) => {
    try {
      // Create order
      const order = await createPaymentOrder(plan);
      
      // Open Razorpay
      const options = {
        key: import.meta.env.VITE_RAZORPAY_KEY_ID,
        amount: order.amount,
        currency: order.currency,
        order_id: order.order_id,
        name: "SalaryPay HRMS",
        description: `${plan} Plan - Monthly`,
        handler: async function(response) {
          try {
            await verifyPayment({
              razorpay_order_id: response.razorpay_order_id,
              razorpay_payment_id: response.razorpay_payment_id,
              razorpay_signature: response.razorpay_signature,
            }, plan);
            
            alert('Payment successful! Plan activated.');
            window.location.reload();
          } catch (error) {
            alert('Payment verification failed');
          }
        },
        theme: {
          color: "#3498db"
        }
      };
      
      const rzp = new window.Razorpay(options);
      rzp.open();
      
    } catch (error) {
      alert('Order creation failed');
    }
  };
  
  return (
    <div className="plans-page">
      <h1>Choose Your Plan</h1>
      
      <div className="plans-grid">
        {/* Free Plan */}
        <div className="plan-card">
          <h2>Free</h2>
          <p className="price">₹0/month</p>
          <ul>
            <li>✅ 5 employees</li>
            <li>✅ Manual attendance</li>
            <li>✅ Basic salary</li>
            <li>❌ Face recognition</li>
            <li>❌ Tax calculations</li>
            <li>❌ PDF/Excel export</li>
          </ul>
          <button disabled>Current Plan</button>
        </div>
        
        {/* Basic Plan */}
        <div className="plan-card featured">
          <div className="badge">Most Popular</div>
          <h2>Basic</h2>
          <p className="price">₹499/month</p>
          <ul>
            <li>✅ 25 employees</li>
            <li>✅ Face recognition</li>
            <li>✅ Full salary + tax</li>
            <li>✅ PDF/Excel export</li>
            <li>✅ Basic reports</li>
            <li>✅ Email support</li>
          </ul>
          <button onClick={() => handleBuyPlan('basic')}>
            Buy Now
          </button>
        </div>
        
        {/* Premium Plan */}
        <div className="plan-card">
          <h2>Premium</h2>
          <p className="price">₹999/month</p>
          <ul>
            <li>✅ Unlimited employees</li>
            <li>✅ All features</li>
            <li>✅ Advanced reports</li>
            <li>✅ Loan management</li>
            <li>✅ Priority support</li>
            <li>✅ 30-day offline mode</li>
          </ul>
          <button onClick={() => handleBuyPlan('premium')}>
            Buy Now
          </button>
        </div>
      </div>
    </div>
  );
}

export default PlansPage;
```

---

### **Step 8: Update Navbar (Add User Menu)**

```javascript
// your-app/src/components/Navbar.jsx

import { useLicense } from '../context/LicenseContext';
import { useNavigate } from 'react-router-dom';

function Navbar() {
  const { license } = useLicense();
  const navigate = useNavigate();
  
  return (
    <nav className="navbar">
      <div className="navbar-left">
        <h1>Welcome to SalaryPay HRMS</h1>
      </div>
      
      <div className="navbar-right">
        {/* Show current plan */}
        <div className="plan-info">
          <span className={`plan-badge ${license?.plan}`}>
            {license?.plan || 'Free'}
          </span>
          {license?.days_remaining && (
            <span className="days-remaining">
              {license.days_remaining} days left
            </span>
          )}
        </div>
        
        {/* Upgrade button */}
        {license?.plan !== 'premium' && (
          <button 
            className="upgrade-btn"
            onClick={() => navigate('/plans')}
          >
            ⭐ Upgrade
          </button>
        )}
        
        {/* User menu */}
        <div className="user-menu">
          <img src="/avatar.png" alt="User" />
          <span>John Doe</span>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
```

---

## 🎨 Styling Integration

### Add to your global CSS:

```css
/* your-app/src/index.css or App.css */

/* Plan badges */
.plan-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
}

.plan-badge.trial {
  background: #fff3cd;
  color: #856404;
}

.plan-badge.free {
  background: #d1ecf1;
  color: #0c5460;
}

.plan-badge.basic {
  background: #d4edda;
  color: #155724;
}

.plan-badge.premium {
  background: #f8d7da;
  color: #721c24;
}

/* Upgrade button */
.upgrade-btn {
  padding: 8px 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: transform 0.3s;
}

.upgrade-btn:hover {
  transform: scale(1.05);
}

/* Sidebar divider */
.sidebar-divider {
  height: 1px;
  background: #e0e0e0;
  margin: 20px 0;
}

.sidebar-section-title {
  font-size: 12px;
  font-weight: 600;
  color: #6c757d;
  text-transform: uppercase;
  padding: 10px 20px;
}
```

---

## ✅ Integration Checklist

- [ ] **Step 1:** Copy all required files
- [ ] **Step 2:** Wrap App with LicenseProvider
- [ ] **Step 3:** Add admin route to App.jsx
- [ ] **Step 4:** Update Sidebar with menu item
- [ ] **Step 5:** Add TrialBanner to MainLayout
- [ ] **Step 6:** Lock features with FeatureGate
- [ ] **Step 7:** Create Plans page
- [ ] **Step 8:** Update Navbar with plan info
- [ ] **Step 9:** Add Razorpay script to index.html
- [ ] **Step 10:** Test everything!

---

## 🧪 Testing

### Test 1: Registration Flow
1. Open app
2. Should show registration page (if not registered)
3. Register new user
4. Should activate 7-day trial
5. Should redirect to dashboard

### Test 2: Feature Gating
1. Login as free user
2. Try to access face recognition → Should be locked
3. Try to export PDF → Should be locked
4. Upgrade to Basic
5. Features should unlock

### Test 3: Admin Dashboard
1. Login as admin
2. Click "License Dashboard" in sidebar
3. Should show all stats
4. Filter by plan → Should work
5. Change date range → Should update

### Test 4: Payment Flow
1. Click "Upgrade" button
2. Select Basic plan
3. Click "Buy Now"
4. Razorpay modal should open
5. Complete payment
6. Plan should upgrade
7. Features should unlock

---

## 🎯 Final Structure

```
your-salarypay-app/
├── src/
│   ├── components/
│   │   ├── Sidebar.jsx              ← Updated
│   │   ├── Navbar.jsx               ← Updated
│   │   └── common/
│   │       ├── FeatureGate.jsx      ← New
│   │       └── TrialBanner.jsx      ← New
│   ├── pages/
│   │   ├── Dashboard.jsx            ← Your existing
│   │   ├── Employees.jsx            ← Your existing
│   │   ├── Attendance.jsx           ← Updated (with locks)
│   │   ├── Salary.jsx               ← Updated (with locks)
│   │   ├── Plans.jsx                ← New
│   │   └── admin/
│   │       └── LicenseDashboard.jsx ← New
│   ├── layouts/
│   │   └── MainLayout.jsx           ← Updated
│   ├── services/
│   │   └── licenseService.js        ← New
│   ├── context/
│   │   └── LicenseContext.jsx       ← New
│   └── App.jsx                      ← Updated
└── public/
    └── index.html                   ← Updated (Razorpay script)
```

---

**Integration Complete! 🎉**

Tumcha license system aata tumchya main application madhye fully integrated ahe!
