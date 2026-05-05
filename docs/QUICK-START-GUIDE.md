# ⚡ Quick Start Guide - SalaryPay License Server

**5 Minutes Setup** | **Zero Configuration** | **Production Ready**

---

## 🎯 What You'll Get

✅ **Backend API** running on port 8661  
✅ **Frontend UI** running on port 3441  
✅ **7-day trial system** automatic  
✅ **Payment gateway** integrated  
✅ **Offline mode** 15-30 days grace  

---

## 🚀 Backend Setup (2 Minutes)

### Windows

```bash
# Step 1: Run setup script
setup-windows.bat

# That's it! Server running on http://localhost:8661
```

### Manual Setup (Any OS)

```bash
# Step 1: Create virtual environment
python -m venv venv

# Step 2: Activate
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Step 3: Install dependencies
pip install -r requirements.txt

# Step 4: Start server
uvicorn app.main:app --host 0.0.0.0 --port 8661 --reload
```

**✅ Backend Ready!** Open http://localhost:8661/docs

---

## ⚛️ Frontend Setup (3 Minutes)

### Step 1: Copy Files

Copy these 3 files to your React app:

```
your-app/src/
├── services/licenseService.js      ← Copy from frontend/src/services/
├── context/LicenseContext.jsx      ← Copy from frontend/src/context/
└── components/common/
    └── FeatureGate.jsx             ← Copy from frontend/src/components/common/
```

### Step 2: Wrap Your App

Edit `src/App.jsx`:

```javascript
import { LicenseProvider } from './context/LicenseContext';

function App() {
  return (
    <LicenseProvider>
      {/* Your existing app */}
    </LicenseProvider>
  );
}
```

### Step 3: Lock Features

```javascript
import FeatureGate from './components/common/FeatureGate';

// Lock any feature
<FeatureGate feature="attendance_face">
  <FaceRecognitionButton />
</FeatureGate>
```

**✅ Frontend Ready!** License system active.

---

## 🎨 Usage Examples

### Example 1: Registration Page

```javascript
import { registerCustomer } from './services/licenseService';

function Register() {
  const handleSubmit = async (formData) => {
    const result = await registerCustomer(formData);
    // User gets 7-day trial automatically!
    alert('Trial activated!');
  };
  
  return <form onSubmit={handleSubmit}>...</form>;
}
```

### Example 2: Feature Lock

```javascript
// Free users see lock icon, paid users see button
<FeatureGate feature="export_pdf">
  <button>Export PDF</button>
</FeatureGate>
```

### Example 3: Check License

```javascript
import { useLicense } from './context/LicenseContext';

function Dashboard() {
  const { license } = useLicense();
  
  return (
    <div>
      <p>Plan: {license.plan}</p>
      <p>Days Left: {license.days_remaining}</p>
    </div>
  );
}
```

### Example 4: Payment

```javascript
import { createPaymentOrder, verifyPayment } from './services/licenseService';

function BuyButton({ plan }) {
  const handlePayment = async () => {
    // Create order
    const order = await createPaymentOrder(plan);
    
    // Open Razorpay
    const rzp = new Razorpay({
      key: "rzp_test_xxx",
      amount: order.amount,
      order_id: order.order_id,
      handler: async (response) => {
        // Verify payment
        await verifyPayment(response, plan);
        alert('Plan activated!');
      }
    });
    rzp.open();
  };
  
  return <button onClick={handlePayment}>Buy ₹499</button>;
}
```

---

## 🎯 Plan Features

### Trial (7 Days Free)
- ✅ All features unlocked
- ✅ Unlimited employees
- ✅ Face recognition
- ✅ Tax calculations
- ✅ PDF/Excel export

### Free (Forever)
- ✅ 5 employees max
- ✅ Manual attendance
- ✅ Basic salary
- ❌ Face recognition locked
- ❌ Export locked

### Basic (₹499/month)
- ✅ 25 employees
- ✅ Face recognition
- ✅ Tax calculations
- ✅ PDF/Excel export
- ❌ Advanced reports locked

### Premium (₹999/month)
- ✅ Everything unlocked
- ✅ Unlimited employees
- ✅ All features

---

## 🔧 Configuration

### Backend (.env file)

```env
# Razorpay (Get from https://razorpay.com)
RAZORPAY_KEY_ID=rzp_test_xxxxxxxxxx
RAZORPAY_KEY_SECRET=your_secret

# Security (Change in production!)
SECRET_KEY=your-random-32-char-key
LICENSE_ENCRYPTION_KEY=your-encryption-key

# CORS (Add your frontend URL)
ALLOWED_ORIGINS=http://localhost:3441
```

### Frontend (licenseService.js)

```javascript
// Change API URL
const LICENSE_SERVER = "http://localhost:8661";  // Development
// const LICENSE_SERVER = "https://license.yourdomain.com";  // Production
```

---

## 📴 Offline Mode

**Automatic!** No code needed.

- Online: License validates with server
- Offline: Uses cached license
- Grace period: 15-30 days
- After grace: "Connect to internet" message

---

## 🎨 Customize Plans

Edit `app/config.py`:

```python
PLAN_FEATURES = {
    "free": [
        "attendance_basic",
        "employees_5",
        "salary_basic"
    ],
    "basic": [
        "attendance_face",
        "employees_25",
        "salary_full",
        "tax",
        "export_pdf"
    ],
    "premium": ["*"]  # All features
}

PLAN_PRICES = {
    "basic": 49900,   # ₹499 in paise
    "premium": 99900  # ₹999 in paise
}
```

---

## 🚀 Deploy to Production

### Backend (VPS/Cloud)

```bash
# 1. SSH to server
ssh root@your-server-ip

# 2. Clone project
git clone your-repo
cd license-server

# 3. Install
pip install -r requirements.txt

# 4. Configure .env with production values

# 5. Run with systemd/supervisor
uvicorn app.main:app --host 0.0.0.0 --port 8661
```

### Frontend

Build with your React app:

```bash
npm run build
# Deploy to Netlify/Vercel/Your hosting
```

Update API URL to production:
```javascript
const LICENSE_SERVER = "https://license.yourdomain.com";
```

---

## 🐛 Troubleshooting

### Backend not starting?

```bash
# Check Python version (need 3.13+)
python --version

# Reinstall dependencies
pip install --upgrade razorpay setuptools
```

### Frontend not connecting?

1. Check backend running: http://localhost:8661
2. Check CORS in .env: `ALLOWED_ORIGINS=http://localhost:3441`
3. Check API URL in licenseService.js

### Payment not working?

1. Add Razorpay script in HTML:
   ```html
   <script src="https://checkout.razorpay.com/v1/checkout.js"></script>
   ```
2. Check Razorpay keys in .env
3. Use test keys in development

---

## 📚 Full Documentation

- **Complete Guide:** [COMPLETE-DOCUMENTATION.md](./COMPLETE-DOCUMENTATION.md)
- **API Reference:** http://localhost:8661/docs
- **Setup Instructions:** [SETUP-INSTRUCTIONS.md](./SETUP-INSTRUCTIONS.md)

---

## ✅ Checklist

**Backend:**
- [ ] Python 3.13+ installed
- [ ] Dependencies installed
- [ ] .env file configured
- [ ] Server running on port 8661
- [ ] API docs accessible

**Frontend:**
- [ ] 3 files copied to React app
- [ ] LicenseProvider wrapper added
- [ ] API URL configured
- [ ] Registration page created
- [ ] Feature gates added

**Razorpay:**
- [ ] Account created
- [ ] API keys copied to .env
- [ ] Razorpay script added to HTML
- [ ] Payment flow tested

**Testing:**
- [ ] Register new user
- [ ] Check 7-day trial activated
- [ ] Test feature locks
- [ ] Test payment flow
- [ ] Test offline mode

---

## 🎉 You're Done!

Your license system is ready! Users can:

1. ✅ Register → Get 7-day trial
2. ✅ Use all features during trial
3. ✅ Choose plan after trial
4. ✅ Pay via UPI/Card/NetBanking
5. ✅ Work offline for 15-30 days

---

**Need Help?** Check [COMPLETE-DOCUMENTATION.md](./COMPLETE-DOCUMENTATION.md)

**Happy Coding! 🚀**
