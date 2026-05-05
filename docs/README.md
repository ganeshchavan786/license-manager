# 🔐 SalaryPay License Server

**Subscription-Based Licensing System** | **7-Day Trial** | **Razorpay Integration** | **Offline Support**

---

## � **[START HERE](./START-HERE.md)** ← Click to begin!

---

## �📚 Documentation

| Document | Description | Language |
|----------|-------------|----------|
| **[QUICK-START-GUIDE.md](./QUICK-START-GUIDE.md)** | 5-minute setup guide | English |
| **[COMPLETE-DOCUMENTATION.md](./COMPLETE-DOCUMENTATION.md)** | Full technical documentation | English |
| **[MARATHI-GUIDE.md](./MARATHI-GUIDE.md)** | संपूर्ण मार्गदर्शिका | मराठी |
| **[SETUP-INSTRUCTIONS.md](./SETUP-INSTRUCTIONS.md)** | Setup commands | English |
| **[API-TESTING-GUIDE.md](./API-TESTING-GUIDE.md)** | API testing with cURL & Postman | English |
| **[ADMIN-DASHBOARD-GUIDE.md](./ADMIN-DASHBOARD-GUIDE.md)** | Admin dashboard setup & usage | English |
| **[DASHBOARD-PREVIEW.md](./DASHBOARD-PREVIEW.md)** | Dashboard visual preview | English |
| **[INTEGRATION-GUIDE.md](./INTEGRATION-GUIDE.md)** | Integrate with your main app | English |

---

## ⚡ Quick Start

### Backend (2 Minutes)

```bash
# Windows
setup-windows.bat

# Linux/Mac
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8661 --reload
```

**✅ Backend Ready:** http://localhost:8661/docs

### Frontend (3 Minutes)

1. Copy 3 files to your React app:
   - `frontend/src/services/licenseService.js`
   - `frontend/src/context/LicenseContext.jsx`
   - `frontend/src/components/common/FeatureGate.jsx`

2. Wrap your app:
   ```javascript
   import { LicenseProvider } from './context/LicenseContext';
   
   function App() {
     return <LicenseProvider>{/* your app */}</LicenseProvider>;
   }
   ```

3. Lock features:
   ```javascript
   <FeatureGate feature="attendance_face">
     <FaceRecognitionButton />
   </FeatureGate>
   ```

**✅ Frontend Ready!** License system active.

---

## 🎯 Features

✅ **7-Day Free Trial** - Automatic on registration  
✅ **Multi-Tier Plans** - Free, Basic (₹499), Premium (₹999)  
✅ **Feature Gating** - Lock/unlock features by plan  
✅ **Razorpay Integration** - UPI, Card, NetBanking  
✅ **Offline Mode** - 15-30 days grace period  
✅ **Secure** - JWT encryption, payment verification  
✅ **Admin Dashboard** - Customer management, analytics  

---

## 📁 Project Structure
```
license-server/
├── app/
│   ├── main.py              # Entry point
│   ├── config.py            # Settings
│   ├── database.py          # DB connection
│   ├── models/__init__.py   # DB Tables
│   ├── routers/
│   │   ├── auth.py          # Register + Login
│   │   ├── license.py       # Validate API
│   │   ├── payment.py       # Razorpay
│   │   └── admin.py         # Your dashboard
│   └── services/
│       ├── license.py       # Core logic
│       ├── razorpay.py      # Payment
│       └── auth.py          # JWT
├── frontend/src/
│   ├── services/licenseService.js    # Existing app मध्ये copy करा
│   ├── context/LicenseContext.jsx   # Existing app मध्ये copy करा
│   ├── components/common/
│   │   ├── FeatureGate.jsx          # Feature lock/unlock
│   │   └── TrialBanner.jsx          # Trial countdown
│   └── pages/subscription/
│       ├── Plans.jsx                # Plans page
│       └── Register.jsx             # Registration
├── deploy.sh                        # Ubuntu VPS deploy
└── .env.example                     # Environment template
```

---

## 🚀 Production Deployment

### VPS Deployment (Ubuntu/Debian)

```bash
# 1. Upload files
scp -r license-server/ root@YOUR_VPS_IP:/opt/salarypay-license/

# 2. SSH and deploy
ssh root@YOUR_VPS_IP
cd /opt/salarypay-license
chmod +x deploy.sh
sudo bash deploy.sh

# 3. Configure .env
nano .env
# Add Razorpay keys and production settings

# 4. Restart service
systemctl restart salarypay-license

# 5. Setup SSL
certbot --nginx -d yourdomain.com
```

**✅ Production Ready:** https://yourdomain.com

---

## 🔗 Integration with Your App

### Step 1: Copy Files

Copy these files to your React app:

```
frontend/src/services/licenseService.js    → your-app/src/services/
frontend/src/context/LicenseContext.jsx   → your-app/src/context/
frontend/src/components/common/FeatureGate.jsx  → your-app/src/components/common/
frontend/src/components/common/TrialBanner.jsx  → your-app/src/components/common/
frontend/src/pages/subscription/Plans.jsx       → your-app/src/pages/subscription/
frontend/src/pages/subscription/Register.jsx    → your-app/src/pages/subscription/
```

### Step 2: Update API URL

Edit `licenseService.js`:

```javascript
const LICENSE_SERVER = "https://yourdomain.com";  // Production
// const LICENSE_SERVER = "http://localhost:8661";  // Development
```

### Step 3: Wrap Your App

Edit `App.jsx`:

```jsx
import { LicenseProvider } from './context/LicenseContext';

function App() {
  return (
    <LicenseProvider>
      {/* Your existing app */}
      <Router>
        <Routes>
          {/* Your routes */}
        </Routes>
      </Router>
    </LicenseProvider>
  );
}
```

### Step 4: Add Trial Banner

Edit your admin layout:

```jsx
import TrialBanner from '../components/common/TrialBanner';

function AdminLayout({ children }) {
  return (
    <div>
      <TrialBanner />  {/* Shows trial countdown */}
      <Sidebar />
      {children}
    </div>
  );
}
```

### Step 5: Lock Features

Use `FeatureGate` component:

```jsx
import FeatureGate from '../components/common/FeatureGate';

// Lock face recognition
<FeatureGate feature="attendance_face">
  <FaceAttendanceButton />
</FeatureGate>

// Lock PDF export
<FeatureGate feature="export_pdf">
  <ExportPDFButton />
</FeatureGate>

// Lock loans module
<FeatureGate feature="loans">
  <LoansSection />
</FeatureGate>
```

### Step 6: Add Razorpay

Add to `public/index.html`:

```html
<script src="https://checkout.razorpay.com/v1/checkout.js"></script>
```

Add to `.env`:

```env
VITE_RAZORPAY_KEY_ID=rzp_live_xxxxxxxxxx
```

---

## 📡 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /auth/register | नवीन customer + auto trial |
| POST | /auth/login | Login |
| POST | /license/validate | App start वर license check |
| GET | /license/status/{machine_id} | Status check |
| POST | /payment/create-order | Razorpay order |
| POST | /payment/verify | Payment verify |
| POST | /payment/webhook | Razorpay webhook |
| GET | /admin/customers | सर्व customers (Admin only) |
| GET | /admin/stats | Dashboard stats |
| POST | /admin/customers/{id}/upgrade | Manual upgrade |

**Admin API Key**: `.env` च्या `SECRET_KEY` चे पहिले 32 characters
Header: `X-Admin-Key: your-key-here`

---

## 🔒 Features List (FeatureGate मध्ये वापरा)

| Feature Name | Free | Basic | Premium |
|---|---|---|---|
| attendance_basic | ✅ | ✅ | ✅ |
| attendance_face | ❌ | ✅ | ✅ |
| employees_5 | ✅ | ❌ | ❌ |
| employees_25 | ❌ | ✅ | ❌ |
| employees_unlimited | ❌ | ❌ | ✅ |
| salary_basic | ✅ | ❌ | ❌ |
| salary_full | ❌ | ✅ | ✅ |
| tax | ❌ | ✅ | ✅ |
| loans | ❌ | ❌ | ✅ |
| export_pdf | ❌ | ✅ | ✅ |
| export_excel | ❌ | ✅ | ✅ |
| leaves | ✅ | ✅ | ✅ |
| reports_basic | ❌ | ✅ | ❌ |
| reports_full | ❌ | ❌ | ✅ |
| holidays | ✅ | ✅ | ✅ |

---

## 🔐 Security Features

- **Password Hashing:** Bcrypt with automatic salt
- **License Keys:** JWT tokens with HMAC SHA256 signature
- **Payment Verification:** Razorpay signature validation
- **Encrypted Cache:** Fernet symmetric encryption for offline mode
- **Audit Logs:** All actions tracked with IP, timestamp, machine ID

---

## 📞 Support

### Documentation
- **Quick Start:** [QUICK-START-GUIDE.md](./QUICK-START-GUIDE.md)
- **Complete Guide:** [COMPLETE-DOCUMENTATION.md](./COMPLETE-DOCUMENTATION.md)
- **Marathi Guide:** [MARATHI-GUIDE.md](./MARATHI-GUIDE.md)
- **API Docs:** http://localhost:8661/docs

### Common Issues

**Backend not starting?**
```bash
pip install --upgrade razorpay setuptools
```

**Frontend not connecting?**
- Check backend running: http://localhost:8661
- Check CORS in .env: `ALLOWED_ORIGINS=http://localhost:3441`
- Check API URL in licenseService.js

**Payment not working?**
- Add Razorpay script to HTML
- Check Razorpay keys in .env
- Use test keys in development

---

## 📝 License

Copyright © 2026 SalaryPay Development Team. All rights reserved.

---

**Made with ❤️ for SalaryPay HRMS**
