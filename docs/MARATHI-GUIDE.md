# 📚 SalaryPay License Server - मराठी मार्गदर्शक

**संपूर्ण मार्गदर्शिका** | **Backend + Frontend** | **Production Ready**

---

## 📖 विषय सूची

1. [प्रस्तावना](#प्रस्तावना)
2. [Backend Setup](#backend-setup)
3. [Frontend Integration](#frontend-integration)
4. [Features Lock कसे करायचे](#features-lock-कसे-करायचे)
5. [Payment Integration](#payment-integration)
6. [Offline Mode](#offline-mode)
7. [Production Deployment](#production-deployment)
8. [समस्या निवारण](#समस्या-निवारण)

---

## 🎯 प्रस्तावना

### हे System काय करतो?

SalaryPay License Server तुमच्या HRMS product मध्ये **subscription-based licensing** add करतो:

✅ **7-day free trial** - Registration नंतर automatic  
✅ **Plan-based features** - Free, Basic (₹499), Premium (₹999)  
✅ **Razorpay payment** - UPI, Card, NetBanking  
✅ **Offline mode** - 15-30 days internet नसेल तरी चालेल  
✅ **Secure** - JWT encryption, payment verification  

### User Journey

```
1. App Install → Registration
2. 7-day Trial Activate (सर्व features)
3. Trial End → Plan Choose (Free/Basic/Premium)
4. Payment → Features Unlock
5. Offline → 15-30 days grace period
6. Renewal → Monthly subscription
```

---

## 🚀 Backend Setup

### आवश्यक Software

- **Python 3.13+** (Download: https://python.org)
- **pip** (Python सोबत येतो)

### Step 1: Project Download करा

```bash
# Git वापरून
git clone https://github.com/your-repo/license-server.git
cd license-server

# किंवा ZIP download करून extract करा
```

### Step 2: Setup Script Run करा (Windows)

```bash
setup-windows.bat
```

**हे script automatic करेल:**
1. Virtual environment तयार करेल
2. सर्व dependencies install करेल
3. `.env` file तयार करेल
4. Server start करेल (port 8661)

### Step 3: .env File Configure करा

`.env` file उघडा आणि edit करा:

```env
# Database (Development साठी SQLite, Production साठी PostgreSQL)
DATABASE_URL=sqlite:///./license.db

# Security Keys (PRODUCTION मध्ये CHANGE करा!)
SECRET_KEY=tumcha-secret-key-minimum-32-characters
LICENSE_ENCRYPTION_KEY=tumcha-encryption-key

# Razorpay Credentials (https://razorpay.com वरून मिळवा)
RAZORPAY_KEY_ID=rzp_test_xxxxxxxxxx
RAZORPAY_KEY_SECRET=tumcha_razorpay_secret

# CORS (Frontend URL add करा)
ALLOWED_ORIGINS=http://localhost:3441,http://localhost:3000

# Trial & Grace Periods (दिवसांमध्ये)
TRIAL_DAYS=7
FREE_OFFLINE_GRACE=15
BASIC_OFFLINE_GRACE=15
PREMIUM_OFFLINE_GRACE=30
```

### Step 4: Server Start करा

```bash
# Option 1: Batch script
setup-windows.bat

# Option 2: Manual
venv\Scripts\activate
uvicorn app.main:app --host 0.0.0.0 --port 8661 --reload
```

### Step 5: Verify करा

Browser मध्ये उघडा: **http://localhost:8661/docs**

तुम्हाला Swagger UI दिसेल सर्व API endpoints सोबत.

---

## ⚛️ Frontend Integration

### Step 1: Files Copy करा

तुमच्या React app मध्ये हे files copy करा:

```
tumcha-salarypay-app/
├── src/
│   ├── services/
│   │   └── licenseService.js      ← frontend/src/services/ मधून copy करा
│   │
│   ├── context/
│   │   └── LicenseContext.jsx     ← frontend/src/context/ मधून copy करा
│   │
│   └── components/
│       └── common/
│           ├── FeatureGate.jsx    ← frontend/src/components/common/ मधून
│           └── TrialBanner.jsx    ← frontend/src/components/common/ मधून
```

### Step 2: API URL Update करा

`src/services/licenseService.js` file उघडा:

```javascript
// Development
const LICENSE_SERVER = "http://localhost:8661";

// Production (deploy नंतर)
// const LICENSE_SERVER = "https://license.yourdomain.com";
```

### Step 3: App.jsx मध्ये Wrapper Add करा

तुमची `src/App.jsx` file edit करा:

```javascript
import { LicenseProvider } from './context/LicenseContext';

function App() {
  return (
    <LicenseProvider>
      {/* तुमचा existing app code */}
      <Router>
        <Routes>
          {/* तुमचे routes */}
        </Routes>
      </Router>
    </LicenseProvider>
  );
}

export default App;
```

**बस! License system activate झाला!** ✅

---

## 🔒 Features Lock कसे करायचे

### Example 1: Face Recognition Lock करा

```javascript
import FeatureGate from '../components/common/FeatureGate';

function AttendancePage() {
  return (
    <div>
      <h1>Attendance</h1>
      
      {/* Manual attendance - सर्वांसाठी available */}
      <button onClick={manualPunchIn}>Manual Punch In</button>
      
      {/* Face recognition - फक्त Basic/Premium साठी */}
      <FeatureGate feature="attendance_face">
        <button onClick={faceRecognition}>Face Recognition</button>
      </FeatureGate>
    </div>
  );
}
```

**Result:**
- Free plan: Manual button दिसेल, Face button locked 🔒
- Basic/Premium: दोन्ही buttons दिसतील

### Example 2: Employee Limit

```javascript
import { useLicense } from '../context/LicenseContext';

function EmployeeList() {
  const { license } = useLicense();
  const features = license?.features || [];
  
  // Employee limit check
  let maxEmployees = 5;  // Free plan default
  if (features.includes("employees_25")) maxEmployees = 25;
  if (features.includes("employees_unlimited")) maxEmployees = Infinity;
  
  const canAddMore = employees.length < maxEmployees;
  
  return (
    <div>
      <h1>Employees ({employees.length}/{maxEmployees})</h1>
      
      {canAddMore ? (
        <button onClick={addEmployee}>Add Employee</button>
      ) : (
        <button disabled>
          Limit पूर्ण झाली - Upgrade करा
        </button>
      )}
    </div>
  );
}
```

### Example 3: PDF/Excel Export Lock

```javascript
function ReportsPage() {
  return (
    <div>
      <h1>Reports</h1>
      
      {/* Report view - free मध्ये available */}
      <ReportTable data={reportData} />
      
      {/* Export buttons - फक्त paid plans साठी */}
      <FeatureGate feature="export_pdf">
        <button onClick={exportPDF}>📄 Export PDF</button>
      </FeatureGate>
      
      <FeatureGate feature="export_excel">
        <button onClick={exportExcel}>📊 Export Excel</button>
      </FeatureGate>
    </div>
  );
}
```

### Example 4: Tax Calculation

```javascript
function SalaryCalculation({ employee }) {
  const { license } = useLicense();
  const hasTaxFeature = license?.features?.includes("tax");
  
  const basicSalary = calculateBasicSalary(employee);
  const taxAmount = hasTaxFeature ? calculateTax(basicSalary) : 0;
  const netSalary = basicSalary - taxAmount;
  
  return (
    <div>
      <p>Basic Salary: ₹{basicSalary}</p>
      
      {hasTaxFeature ? (
        <p>Tax Deduction: ₹{taxAmount}</p>
      ) : (
        <p style={{color: 'gray'}}>
          Tax calculation Basic/Premium plans मध्ये available
        </p>
      )}
      
      <p><strong>Net Salary: ₹{netSalary}</strong></p>
    </div>
  );
}
```

---

## 💳 Payment Integration

### Step 1: Razorpay Account तयार करा

1. https://razorpay.com वर जा
2. Sign up करा
3. Settings → API Keys
4. Key ID आणि Key Secret copy करा
5. `.env` file मध्ये add करा

### Step 2: Razorpay Script Add करा

तुमच्या `public/index.html` मध्ये:

```html
<head>
  <!-- इतर scripts -->
  <script src="https://checkout.razorpay.com/v1/checkout.js"></script>
</head>
```

### Step 3: Payment Button तयार करा

```javascript
import { createPaymentOrder, verifyPayment } from '../services/licenseService';

function BuyPlanButton({ plan }) {
  const handlePayment = async () => {
    try {
      // Step 1: Order तयार करा
      const order = await createPaymentOrder(plan);
      
      // Step 2: Razorpay checkout उघडा
      const options = {
        key: "rzp_test_xxxxxxxxxx", // तुमची Razorpay key
        amount: order.amount,
        currency: order.currency,
        order_id: order.order_id,
        name: "SalaryPay HRMS",
        description: `${plan} Plan - Monthly`,
        handler: async function(response) {
          // Step 3: Payment verify करा
          try {
            const result = await verifyPayment({
              razorpay_order_id: response.razorpay_order_id,
              razorpay_payment_id: response.razorpay_payment_id,
              razorpay_signature: response.razorpay_signature,
              plan: plan
            }, plan);
            
            alert('Payment successful! Plan activated.');
            window.location.reload();
          } catch (error) {
            alert('Payment verification failed');
          }
        },
        prefill: {
          email: "customer@example.com",
          contact: "9876543210"
        },
        theme: {
          color: "#1565C0"
        }
      };
      
      const rzp = new window.Razorpay(options);
      rzp.open();
      
    } catch (error) {
      alert('Order creation failed');
    }
  };
  
  return (
    <button onClick={handlePayment}>
      Buy {plan} Plan - ₹{plan === 'basic' ? 499 : 999}
    </button>
  );
}
```

### Plans Page तयार करा

```javascript
function PlansPage() {
  return (
    <div>
      <h1>Choose Your Plan</h1>
      
      <div className="plans">
        {/* Free Plan */}
        <div className="plan-card">
          <h2>Free</h2>
          <p className="price">₹0/month</p>
          <ul>
            <li>✅ 5 employees</li>
            <li>✅ Manual attendance</li>
            <li>✅ Basic salary</li>
            <li>❌ Face recognition</li>
            <li>❌ PDF/Excel export</li>
          </ul>
          <button>Current Plan</button>
        </div>
        
        {/* Basic Plan */}
        <div className="plan-card">
          <h2>Basic</h2>
          <p className="price">₹499/month</p>
          <ul>
            <li>✅ 25 employees</li>
            <li>✅ Face recognition</li>
            <li>✅ Full salary + tax</li>
            <li>✅ PDF/Excel export</li>
            <li>✅ Basic reports</li>
          </ul>
          <BuyPlanButton plan="basic" />
        </div>
        
        {/* Premium Plan */}
        <div className="plan-card">
          <h2>Premium</h2>
          <p className="price">₹999/month</p>
          <ul>
            <li>✅ Unlimited employees</li>
            <li>✅ All features</li>
            <li>✅ Advanced reports</li>
            <li>✅ Priority support</li>
            <li>✅ 30-day offline mode</li>
          </ul>
          <BuyPlanButton plan="premium" />
        </div>
      </div>
    </div>
  );
}
```

---

## 📴 Offline Mode

### कसे काम करते?

1. **Online:** License server शी validate होतो, encrypted cache save होतो
2. **Offline:** Cache वापरतो, grace period countdown सुरू होतो
3. **Grace Period:** 15-30 days (plan वर अवलंबून)
4. **Expired:** App block होतो, internet connection हवे

### Grace Periods

| Plan | Offline Days |
|------|--------------|
| Trial | 15 days |
| Free | 15 days |
| Basic | 15 days |
| Premium | 30 days |

### Automatic Implementation

Frontend automatically handle करतो - तुम्हाला काही code करायची गरज नाही!

```javascript
// licenseService.js मध्ये automatic आहे
export async function checkLicense() {
  try {
    // Online validation try करतो
    const response = await fetch(`${LICENSE_SERVER}/license/validate`, {
      timeout: 5000
    });
    
    if (response.ok) {
      const data = await response.json();
      saveCache(data); // Offline साठी save
      return data;
    }
  } catch {
    // Offline - cache वापरतो
    const cache = loadCache();
    const daysOffline = getCachedDaysOffline(cache);
    
    if (daysOffline <= cache.grace_period_days) {
      return {
        ...cache,
        valid: true,
        offline: true,
        days_remaining_offline: cache.grace_period_days - daysOffline
      };
    }
    
    return { valid: false, reason: "grace_expired" };
  }
}
```

---

## 🚀 Production Deployment

### Backend Deployment (VPS/Cloud)

#### DigitalOcean / AWS / Linode

```bash
# 1. Server मध्ये SSH करा
ssh root@your-server-ip

# 2. Python install करा
apt update
apt install python3.13 python3-pip

# 3. Project clone करा
git clone https://github.com/your-repo/license-server.git
cd license-server

# 4. Dependencies install करा
pip3 install -r requirements.txt

# 5. .env configure करा
nano .env
# Production values add करा

# 6. Systemd service तयार करा
sudo nano /etc/systemd/system/license-server.service
```

**Service file:**
```ini
[Unit]
Description=SalaryPay License Server
After=network.target

[Service]
User=root
WorkingDirectory=/root/license-server
ExecStart=/usr/local/bin/uvicorn app.main:app --host 0.0.0.0 --port 8661
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# 7. Service start करा
sudo systemctl start license-server
sudo systemctl enable license-server

# 8. Nginx setup करा
sudo apt install nginx
sudo nano /etc/nginx/sites-available/license
```

**Nginx config:**
```nginx
server {
    listen 80;
    server_name license.yourdomain.com;
    
    location / {
        proxy_pass http://localhost:8661;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
# 9. Site enable करा
sudo ln -s /etc/nginx/sites-available/license /etc/nginx/sites-enabled/
sudo systemctl restart nginx

# 10. SSL setup करा (recommended)
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d license.yourdomain.com
```

### Frontend Deployment

तुमच्या React app सोबत build करा:

```bash
# Build
npm run build

# Deploy to Netlify/Vercel/Your hosting
```

Production API URL update करा:
```javascript
const LICENSE_SERVER = "https://license.yourdomain.com";
```

---

## 🔧 समस्या निवारण

### Backend समस्या

#### Error: "No module named 'pkg_resources'"

**उपाय:** Razorpay upgrade करा
```bash
venv\Scripts\pip.exe install --upgrade razorpay
```

#### Error: "Database locked"

**उपाय:** Production मध्ये PostgreSQL वापरा
```env
DATABASE_URL=postgresql://user:pass@localhost:5432/license
```

#### Error: "CORS policy blocked"

**उपाय:** Frontend URL `.env` मध्ये add करा
```env
ALLOWED_ORIGINS=http://localhost:3441,https://yourdomain.com
```

### Frontend समस्या

#### License नेहमी invalid दाखवतो

**तपासा:**
1. Backend server चालू आहे का?
2. API URL licenseService.js मध्ये बरोबर आहे का?
3. CORS properly configured आहे का?
4. Browser console मध्ये errors आहेत का?

#### Payment काम करत नाही

**तपासा:**
1. Razorpay script HTML मध्ये load झाली का?
2. Razorpay keys .env मध्ये बरोबर आहेत का?
3. Development मध्ये test keys वापरत आहात का?
4. Razorpay dashboard मध्ये errors तपासा

#### Offline mode काम करत नाही

**तपासा:**
1. Cache localStorage मध्ये save होतो का?
2. Grace period संपली नाही ना?
3. Browser console मध्ये cache errors तपासा

---

## 📊 Plan Features Customize करा

`app/config.py` file edit करा:

```python
PLAN_FEATURES = {
    "trial": [
        "attendance_face",      # Face recognition
        "employees_unlimited",  # Unlimited employees
        "salary_full",          # Full salary
        "tax",                  # Tax calculations
        "loans",                # Loans
        "export_pdf",           # PDF export
        "export_excel",         # Excel export
        "leaves",               # Leaves
        "reports_full",         # All reports
        "holidays"              # Holidays
    ],
    "free": [
        "attendance_basic",     # Manual only
        "employees_5",          # Max 5
        "salary_basic",         # Basic salary
        "leaves",
        "holidays"
    ],
    "basic": [
        "attendance_face",
        "employees_25",         # Max 25
        "salary_full",
        "tax",
        "export_pdf",
        "export_excel",
        "leaves",
        "reports_basic",
        "holidays"
    ],
    "premium": ["*"]            # सर्व features
}

PLAN_PRICES = {
    "basic": 49900,   # ₹499 (paise मध्ये)
    "premium": 99900  # ₹999 (paise मध्ये)
}
```

---

## 📞 मदत

### Documentation Files

- **संपूर्ण मार्गदर्शिका:** COMPLETE-DOCUMENTATION.md (English)
- **Quick Start:** QUICK-START-GUIDE.md
- **Setup Instructions:** SETUP-INSTRUCTIONS.md
- **हा मार्गदर्शक:** MARATHI-GUIDE.md

### API Documentation

- **Swagger UI:** http://localhost:8661/docs
- **ReDoc:** http://localhost:8661/redoc

### सामान्य प्रश्न

**प्र: Desktop app साठी वापरता येईल का?**  
उ: होय, पण Electron/Tauri साठी frontend code adapt करावा लागेल.

**प्र: Plans आणि pricing customize करता येईल का?**  
उ: होय, `app/config.py` edit करा.

**प्र: अधिक features कसे add करायचे?**  
उ: PLAN_FEATURES मध्ये feature names add करा, frontend मध्ये FeatureGate वापरा.

**प्र: इतर payment gateways वापरता येतील का?**  
उ: होय, razorpay.py service replace करा.

**प्र: Database backup कसा घ्यायचा?**  
उ: SQLite: license.db file copy करा. PostgreSQL: pg_dump वापरा.

---

## ✅ Checklist

**Backend:**
- [ ] Python 3.13+ installed
- [ ] Dependencies installed
- [ ] .env file configured
- [ ] Server port 8661 वर चालू
- [ ] API docs accessible

**Frontend:**
- [ ] 3 files React app मध्ये copy केल्या
- [ ] LicenseProvider wrapper add केला
- [ ] API URL configured
- [ ] Registration page तयार केले
- [ ] Feature gates add केले

**Razorpay:**
- [ ] Account तयार केले
- [ ] API keys .env मध्ये add केल्या
- [ ] Razorpay script HTML मध्ये add केली
- [ ] Payment flow test केला

**Testing:**
- [ ] नवीन user register केला
- [ ] 7-day trial activate झाला का check केला
- [ ] Feature locks test केले
- [ ] Payment flow test केला
- [ ] Offline mode test केला

---

## 🎉 तयार!

तुमची license system तयार आहे! Users आता:

1. ✅ Register करू शकतात → 7-day trial मिळेल
2. ✅ Trial मध्ये सर्व features वापरू शकतात
3. ✅ Trial नंतर plan निवडू शकतात
4. ✅ UPI/Card/NetBanking ने payment करू शकतात
5. ✅ 15-30 days offline काम करू शकतात

---

**शुभेच्छा! 🚀**

प्रश्न असल्यास: support@salarypay.com
