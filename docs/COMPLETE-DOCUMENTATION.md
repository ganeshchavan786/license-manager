# 📚 SalaryPay License Server - Complete Documentation

**Version:** 1.0.0  
**Last Updated:** May 2, 2026  
**Author:** SalaryPay Development Team

---

## 📖 Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Backend Setup](#backend-setup)
4. [Frontend Integration](#frontend-integration)
5. [API Reference](#api-reference)
6. [Feature Gating](#feature-gating)
7. [Payment Integration](#payment-integration)
8. [Offline Mode](#offline-mode)
9. [Security](#security)
10. [Deployment](#deployment)
11. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

### What is SalaryPay License Server?

SalaryPay License Server ek **subscription-based licensing system** ahe jo tumchya HRMS product madhye integrate hoto. Ha system:

- ✅ **7-day free trial** automatically deto
- ✅ **Plan-based features** lock/unlock karto (Free, Basic, Premium)
- ✅ **Razorpay payment** integration
- ✅ **Offline mode** support (15-30 days grace period)
- ✅ **Machine-based licensing** (1 PC = 1 license)
- ✅ **Secure encryption** (JWT + Fernet)

### Key Features

| Feature | Description |
|---------|-------------|
| **Trial System** | 7-day automatic trial on registration |
| **Multi-tier Plans** | Free, Basic (₹499), Premium (₹999) |
| **Feature Gating** | Plan-based feature access control |
| **Offline Support** | 15-30 days grace period without internet |
| **Payment Gateway** | Razorpay integration for UPI/Card/NetBanking |
| **Security** | JWT tokens, encrypted cache, audit logs |
| **Admin Dashboard** | Customer management, analytics, reports |

---

## 🏗️ System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    USER'S BROWSER                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  React Frontend (Port 3441)                          │   │
│  │  - Registration UI                                   │   │
│  │  - License Context                                   │   │
│  │  - Feature Gates                                     │   │
│  │  - Payment UI                                        │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                          │
                          │ HTTP/HTTPS
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Backend (Port 8661)                    │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Routers:                                            │   │
│  │  - /auth (Registration, Login)                       │   │
│  │  - /license (Validation)                             │   │
│  │  - /payment (Razorpay)                               │   │
│  │  - /admin (Dashboard)                                │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Services:                                           │   │
│  │  - auth.py (Password hashing, JWT)                   │   │
│  │  - license.py (License generation, validation)       │   │
│  │  - razorpay.py (Payment processing)                  │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                  SQLite/PostgreSQL Database                 │
│  Tables:                                                    │
│  - customers (user accounts)                                │
│  - licenses (license keys, plans)                           │
│  - payments (transaction history)                           │
│  - subscriptions (recurring billing)                        │
│  - audit_logs (security tracking)                           │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    Razorpay API                             │
│  - Order creation                                           │
│  - Payment processing                                       │
│  - Webhook notifications                                    │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

**Backend:**
- FastAPI 0.115.0
- SQLAlchemy 2.0.36
- Python-Jose (JWT)
- Cryptography (Fernet encryption)
- Razorpay SDK 2.0.1
- Uvicorn (ASGI server)

**Frontend:**
- React 18.2.0
- React Router 6.22.0
- Axios (HTTP client)
- Vite (Build tool)

**Database:**
- SQLite (Development)
- PostgreSQL (Production recommended)

---

## 🚀 Backend Setup

### Prerequisites

- **Python 3.13+** installed
- **pip** package manager
- **Git** (optional)

### Step 1: Clone/Download Project

```bash
# Option 1: Git clone
git clone https://github.com/your-repo/license-server.git
cd license-server

# Option 2: Download ZIP and extract
```

### Step 2: Install Dependencies (Windows)

```bash
# Run setup script
setup-windows.bat
```

**Script automatically:**
1. Creates virtual environment
2. Installs all dependencies
3. Creates `.env` file (if not exists)
4. Starts the server on port 8661

### Step 3: Configure Environment Variables

Edit `.env` file:

```env
# Database
DATABASE_URL=sqlite:///./license.db

# Security Keys (CHANGE IN PRODUCTION!)
SECRET_KEY=your-secret-key-minimum-32-characters-long
LICENSE_ENCRYPTION_KEY=your-encryption-key-for-cache

# JWT Settings
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Razorpay Credentials
RAZORPAY_KEY_ID=rzp_test_xxxxxxxxxx
RAZORPAY_KEY_SECRET=your_razorpay_secret

# CORS Settings
ALLOWED_ORIGINS=http://localhost:3441,http://localhost:3000

# Trial & Grace Periods
TRIAL_DAYS=7
FREE_OFFLINE_GRACE=15
BASIC_OFFLINE_GRACE=15
PREMIUM_OFFLINE_GRACE=30
```

### Step 4: Start Backend Server

```bash
# Option 1: Using batch script
setup-windows.bat

# Option 2: Manual start
venv\Scripts\activate
uvicorn app.main:app --host 0.0.0.0 --port 8661 --reload
```

**Server will start at:**
- API: http://localhost:8661
- Docs: http://localhost:8661/docs
- ReDoc: http://localhost:8661/redoc

### Step 5: Verify Backend

Open browser: http://localhost:8661/docs

You should see Swagger UI with all API endpoints.

---

## ⚛️ Frontend Integration

### Step 1: Copy Required Files

Copy these files to your React project:

```
your-salarypay-app/
├── src/
│   ├── services/
│   │   └── licenseService.js      ← Copy from frontend/src/services/
│   │
│   ├── context/
│   │   └── LicenseContext.jsx     ← Copy from frontend/src/context/
│   │
│   └── components/
│       └── common/
│           ├── FeatureGate.jsx    ← Copy from frontend/src/components/common/
│           └── TrialBanner.jsx    ← Copy from frontend/src/components/common/
```

### Step 2: Update API URL

Edit `src/services/licenseService.js`:

```javascript
// Development
const LICENSE_SERVER = "http://localhost:8661";

// Production
const LICENSE_SERVER = "https://license.yourdomain.com";
```

### Step 3: Wrap App with LicenseProvider

Edit your `src/App.jsx`:

```javascript
import { LicenseProvider } from './context/LicenseContext';

function App() {
  return (
    <LicenseProvider>
      {/* Your existing app code */}
      <Router>
        <Routes>
          {/* Your routes */}
        </Routes>
      </Router>
    </LicenseProvider>
  );
}

export default App;
```

### Step 4: Add Registration Page

Create `src/pages/Register.jsx`:

```javascript
import { useState } from 'react';
import { registerCustomer } from '../services/licenseService';

export default function Register() {
  const [formData, setFormData] = useState({
    business_name: '',
    owner_name: '',
    email: '',
    phone: '',
    city: '',
    password: ''
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const result = await registerCustomer(formData);
      alert('Registration successful! 7-day trial activated.');
      // Redirect to dashboard
      window.location.href = '/dashboard';
    } catch (error) {
      alert('Registration failed: ' + error.message);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <h1>Register for SalaryPay HRMS</h1>
      
      <input
        type="text"
        placeholder="Business Name"
        value={formData.business_name}
        onChange={(e) => setFormData({...formData, business_name: e.target.value})}
        required
      />
      
      <input
        type="text"
        placeholder="Owner Name"
        value={formData.owner_name}
        onChange={(e) => setFormData({...formData, owner_name: e.target.value})}
        required
      />
      
      <input
        type="email"
        placeholder="Email"
        value={formData.email}
        onChange={(e) => setFormData({...formData, email: e.target.value})}
        required
      />
      
      <input
        type="tel"
        placeholder="Phone"
        value={formData.phone}
        onChange={(e) => setFormData({...formData, phone: e.target.value})}
        required
      />
      
      <input
        type="text"
        placeholder="City"
        value={formData.city}
        onChange={(e) => setFormData({...formData, city: e.target.value})}
      />
      
      <input
        type="password"
        placeholder="Password"
        value={formData.password}
        onChange={(e) => setFormData({...formData, password: e.target.value})}
        required
      />
      
      <button type="submit">Register & Start 7-Day Trial</button>
    </form>
  );
}
```

### Step 5: Use Feature Gates

Example - Lock face recognition feature:

```javascript
import FeatureGate from '../components/common/FeatureGate';

function AttendancePage() {
  return (
    <div>
      <h1>Attendance</h1>
      
      {/* Always available */}
      <button onClick={manualPunchIn}>Manual Punch In</button>
      
      {/* Only for Basic/Premium plans */}
      <FeatureGate feature="attendance_face">
        <button onClick={faceRecognition}>Face Recognition</button>
      </FeatureGate>
    </div>
  );
}
```

### Step 6: Check License Status

```javascript
import { useLicense } from '../context/LicenseContext';

function Dashboard() {
  const { license, loading } = useLicense();
  
  if (loading) return <div>Loading...</div>;
  
  if (!license?.valid) {
    return <div>Please register or renew your license</div>;
  }
  
  return (
    <div>
      <h1>Dashboard</h1>
      <p>Plan: {license.plan}</p>
      <p>Days Remaining: {license.days_remaining}</p>
    </div>
  );
}
```

---

## 📡 API Reference

### Authentication Endpoints

#### POST /auth/register

Register new customer and activate 7-day trial.

**Request:**
```json
{
  "business_name": "ABC Company",
  "owner_name": "John Doe",
  "email": "john@abc.com",
  "phone": "9876543210",
  "city": "Mumbai",
  "password": "securepassword123",
  "machine_id": "a1b2c3d4e5f6"
}
```

**Response:**
```json
{
  "customer_id": "uuid-123",
  "license_key": "TRIAL-ABC123-XYZ789",
  "plan": "trial",
  "trial_days": 7,
  "message": "Registration successful! 7-day free trial activated."
}
```

#### POST /auth/login

Customer login.

**Request:**
```json
{
  "email": "john@abc.com",
  "password": "securepassword123",
  "machine_id": "a1b2c3d4e5f6"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "customer_id": "uuid-123",
  "business_name": "ABC Company",
  "license_key": "TRIAL-ABC123-XYZ789",
  "plan": "trial"
}
```

---

### License Endpoints

#### POST /license/validate

Validate license and get features.

**Request:**
```json
{
  "machine_id": "a1b2c3d4e5f6",
  "license_key": "TRIAL-ABC123-XYZ789"
}
```

**Response:**
```json
{
  "valid": true,
  "plan": "trial",
  "features": [
    "attendance_face",
    "employees_unlimited",
    "salary_full",
    "tax",
    "export_pdf",
    "export_excel"
  ],
  "grace_period_days": 15,
  "days_remaining": 5,
  "valid_till": "2026-05-09T00:00:00",
  "encrypted_cache": "base64_encrypted_data..."
}
```

#### GET /license/status/{machine_id}

Get license status by machine ID.

**Response:**
```json
{
  "found": true,
  "plan": "basic",
  "valid_till": "2026-06-02T00:00:00",
  "business_name": "ABC Company",
  "email": "john@abc.com"
}
```

---

### Payment Endpoints

#### POST /payment/create-order

Create Razorpay order for payment.

**Request:**
```json
{
  "plan": "basic",
  "customer_id": "uuid-123"
}
```

**Response:**
```json
{
  "order_id": "order_MxYz123",
  "amount": 49900,
  "currency": "INR",
  "plan": "basic"
}
```

#### POST /payment/verify

Verify payment and upgrade license.

**Request:**
```json
{
  "razorpay_order_id": "order_MxYz123",
  "razorpay_payment_id": "pay_AbCd456",
  "razorpay_signature": "sha256_hash...",
  "customer_id": "uuid-123",
  "plan": "basic"
}
```

**Response:**
```json
{
  "success": true,
  "plan": "basic",
  "license_key": "BASIC-XYZ789-ABC123",
  "valid_till": "2026-06-02T00:00:00",
  "message": "Basic plan activated successfully!"
}
```

---

## 🎯 Feature Gating

### Plan Features Configuration

Edit `app/config.py`:

```python
PLAN_FEATURES = {
    "trial": [
        "attendance_face",      # Face recognition
        "employees_unlimited",  # No employee limit
        "salary_full",          # Full salary processing
        "tax",                  # Tax calculations
        "loans",                # Loan management
        "export_pdf",           # PDF export
        "export_excel",         # Excel export
        "leaves",               # Leave management
        "reports_full",         # All reports
        "holidays"              # Holiday calendar
    ],
    "free": [
        "attendance_basic",     # Manual attendance only
        "employees_5",          # Max 5 employees
        "salary_basic",         # Basic salary only
        "leaves",
        "holidays"
    ],
    "basic": [
        "attendance_face",
        "employees_25",         # Max 25 employees
        "salary_full",
        "tax",
        "export_pdf",
        "export_excel",
        "leaves",
        "reports_basic",
        "holidays"
    ],
    "premium": ["*"]            # All features
}
```

### Using FeatureGate Component

```javascript
// Simple lock
<FeatureGate feature="attendance_face">
  <FaceRecognitionButton />
</FeatureGate>

// With custom fallback
<FeatureGate 
  feature="export_pdf" 
  fallback={<p>Upgrade to export PDF</p>}
>
  <ExportPDFButton />
</FeatureGate>

// Without lock icon
<FeatureGate feature="tax" showLock={false}>
  <TaxCalculator />
</FeatureGate>
```

### Programmatic Feature Check

```javascript
import { useLicense } from '../context/LicenseContext';
import { hasFeature } from '../services/licenseService';

function SalaryPage() {
  const { license } = useLicense();
  const features = license?.features || [];
  
  const canCalculateTax = hasFeature(features, "tax");
  const maxEmployees = features.includes("employees_unlimited") ? Infinity :
                       features.includes("employees_25") ? 25 : 5;
  
  return (
    <div>
      <h1>Salary Processing</h1>
      <p>Max Employees: {maxEmployees}</p>
      
      {canCalculateTax && (
        <TaxCalculationSection />
      )}
    </div>
  );
}
```

---

## 💳 Payment Integration

### Step 1: Get Razorpay Credentials

1. Sign up at https://razorpay.com
2. Go to Settings → API Keys
3. Copy Key ID and Key Secret
4. Add to `.env` file

### Step 2: Add Razorpay Script

In your `public/index.html`:

```html
<script src="https://checkout.razorpay.com/v1/checkout.js"></script>
```

### Step 3: Create Payment Component

```javascript
import { createPaymentOrder, verifyPayment } from '../services/licenseService';

function BuyPlanButton({ plan }) {
  const handlePayment = async () => {
    try {
      // Step 1: Create order
      const order = await createPaymentOrder(plan);
      
      // Step 2: Open Razorpay checkout
      const options = {
        key: "rzp_test_xxxxxxxxxx", // Your Razorpay key
        amount: order.amount,
        currency: order.currency,
        order_id: order.order_id,
        name: "SalaryPay HRMS",
        description: `${plan} Plan - Monthly`,
        handler: async function(response) {
          // Step 3: Verify payment
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

---

## 📴 Offline Mode

### How It Works

1. **Online:** License validates with server, encrypted cache saved
2. **Offline:** Cache used, grace period countdown starts
3. **Grace Period:** 15-30 days based on plan
4. **Expired:** App blocks until internet connection

### Grace Periods

| Plan | Grace Period |
|------|--------------|
| Trial | 15 days |
| Free | 15 days |
| Basic | 15 days |
| Premium | 30 days |

### Implementation

Frontend automatically handles offline mode:

```javascript
// licenseService.js handles this automatically
export async function checkLicense() {
  try {
    // Try online validation
    const response = await fetch(`${LICENSE_SERVER}/license/validate`, {
      timeout: 5000
    });
    
    if (response.ok) {
      const data = await response.json();
      saveCache(data); // Save for offline use
      return data;
    }
  } catch {
    // Offline - use cache
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

## 🔐 Security

### Password Security

- **Bcrypt hashing** with automatic salt
- Passwords never stored in plain text
- Minimum 8 characters recommended

### License Key Security

- **JWT tokens** with HMAC SHA256 signature
- Contains: customer_id, machine_id, plan, valid_till
- Tamper-proof - any modification invalidates signature

### Payment Security

- **Razorpay signature verification** using HMAC SHA256
- Prevents fake payment attempts
- Server-side validation only

### Encrypted Cache

- **Fernet symmetric encryption** for offline cache
- AES 128-bit encryption
- Prevents cache tampering

### Audit Logs

All actions logged:
- Registration
- Login attempts
- License validations
- Payments
- Plan upgrades

Logs include:
- Timestamp
- IP address
- Machine ID
- Action details

---

## 🚀 Deployment

### Backend Deployment (VPS/Cloud)

#### Option 1: DigitalOcean/AWS/Linode

```bash
# 1. SSH into server
ssh root@your-server-ip

# 2. Install Python
apt update
apt install python3.13 python3-pip

# 3. Clone project
git clone https://github.com/your-repo/license-server.git
cd license-server

# 4. Install dependencies
pip3 install -r requirements.txt

# 5. Configure .env
nano .env
# Update with production values

# 6. Run with systemd
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
# 7. Start service
sudo systemctl start license-server
sudo systemctl enable license-server

# 8. Setup Nginx reverse proxy
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
# 9. Enable site
sudo ln -s /etc/nginx/sites-available/license /etc/nginx/sites-enabled/
sudo systemctl restart nginx

# 10. Setup SSL (optional but recommended)
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d license.yourdomain.com
```

#### Option 2: Docker Deployment

Create `Dockerfile`:

```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8661"]
```

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8661:8661"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/license
    depends_on:
      - db
    restart: always
  
  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=license
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always

volumes:
  postgres_data:
```

Deploy:
```bash
docker-compose up -d
```

### Frontend Deployment

Build and deploy with your existing React app:

```bash
# Build
npm run build

# Deploy to Netlify/Vercel/Your hosting
```

Update API URL in production:
```javascript
const LICENSE_SERVER = "https://license.yourdomain.com";
```

---

## 🔧 Troubleshooting

### Backend Issues

#### Error: "No module named 'pkg_resources'"

**Solution:** Upgrade razorpay package
```bash
venv\Scripts\pip.exe install --upgrade razorpay
```

#### Error: "Database locked"

**Solution:** Use PostgreSQL in production instead of SQLite
```env
DATABASE_URL=postgresql://user:pass@localhost:5432/license
```

#### Error: "CORS policy blocked"

**Solution:** Add frontend URL to ALLOWED_ORIGINS in `.env`
```env
ALLOWED_ORIGINS=http://localhost:3441,https://yourdomain.com
```

### Frontend Issues

#### License always shows invalid

**Check:**
1. Backend server running?
2. API URL correct in licenseService.js?
3. CORS configured properly?
4. Check browser console for errors

#### Payment not working

**Check:**
1. Razorpay script loaded in HTML?
2. Razorpay keys correct in .env?
3. Using test keys in development?
4. Check Razorpay dashboard for errors

#### Offline mode not working

**Check:**
1. Cache being saved in localStorage?
2. Grace period not expired?
3. Check browser console for cache errors

### Database Issues

#### Reset database

```bash
# Delete database file
rm license.db

# Restart server (tables will be recreated)
venv\Scripts\uvicorn.exe app.main:app --reload
```

#### View database

```bash
# Install SQLite browser
# Or use command line
sqlite3 license.db
.tables
SELECT * FROM customers;
```

---

## 📞 Support

### Documentation

- **API Docs:** http://localhost:8661/docs
- **This Guide:** COMPLETE-DOCUMENTATION.md
- **Setup Guide:** SETUP-INSTRUCTIONS.md

### Common Questions

**Q: Can I use this with desktop apps?**  
A: Yes, but you'll need to adapt the frontend code for Electron/Tauri.

**Q: Can I customize plans and pricing?**  
A: Yes, edit `app/config.py` - PLAN_FEATURES and PLAN_PRICES.

**Q: How to add more features?**  
A: Add feature names to PLAN_FEATURES in config.py, then use FeatureGate in frontend.

**Q: Can I use other payment gateways?**  
A: Yes, replace razorpay.py service with your gateway's SDK.

**Q: How to backup database?**  
A: SQLite: Copy license.db file. PostgreSQL: Use pg_dump.

---

## 📝 Changelog

### Version 1.0.0 (May 2, 2026)
- Initial release
- 7-day trial system
- Multi-tier plans (Free, Basic, Premium)
- Razorpay integration
- Offline mode with grace period
- Feature gating system
- Admin dashboard
- Audit logging

---

## 📄 License

Copyright © 2026 SalaryPay Development Team. All rights reserved.

---

**Happy Coding! 🚀**

For questions or support, contact: support@salarypay.com
