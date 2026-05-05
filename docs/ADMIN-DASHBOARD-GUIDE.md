# 📊 Admin Dashboard Guide - SalaryPay License Server

**Complete Analytics** | **Customer Management** | **Revenue Tracking**

---

## 🎯 Overview

Admin Dashboard tumhala **complete business insights** deto:

✅ **Real-time Stats** - Total customers, plans, revenue  
✅ **Customer List** - All registered users with details  
✅ **Payment History** - All transactions  
✅ **Plan Distribution** - Visual charts  
✅ **Revenue Breakdown** - Plan-wise earnings  
✅ **Date Range Filters** - Today, Week, Month, Year, All Time  
✅ **Auto Refresh** - Every 30 seconds  

---

## 🚀 Setup

### Step 1: Copy Dashboard Files

```bash
# Copy to your React app
cp frontend/src/pages/admin/Dashboard.jsx your-app/src/pages/admin/
cp frontend/src/pages/admin/Dashboard.css your-app/src/pages/admin/
```

### Step 2: Add Route

Edit `your-app/src/App.jsx`:

```javascript
import AdminDashboard from './pages/admin/Dashboard';

function App() {
  return (
    <Router>
      <Routes>
        {/* Your existing routes */}
        <Route path="/admin/dashboard" element={<AdminDashboard />} />
      </Routes>
    </Router>
  );
}
```

### Step 3: Set Admin Key

Dashboard madhye admin key set kara:

```javascript
// Option 1: localStorage madhye save kara
localStorage.setItem('admin_key', 'your-secret-key-from-env');

// Option 2: Dashboard.jsx madhye hardcode kara (not recommended for production)
const API_URL = 'http://localhost:8661';
const ADMIN_KEY = 'your-secret-key-from-env';
```

**Admin Key kasa milel?**
- `.env` file madhun `SECRET_KEY` cha first 32 characters
- Example: If `SECRET_KEY=my-super-secret-key-12345678`, then admin key = `my-super-secret-key-12345678`

### Step 4: Access Dashboard

Browser madhye open kara:
```
http://localhost:3441/admin/dashboard
```

---

## 📊 Dashboard Features

### 1. **Stats Cards** (Top Section)

```
┌─────────────────────────────────────────────────────────────┐
│  👥 Total Customers    🎉 Active Trials    🆓 Free Plan     │
│     150                   25                  50             │
│                                                              │
│  💼 Basic Plan         ⭐ Premium Plan      💰 Revenue      │
│     60                    15                 ₹45,000        │
│                                                              │
│  💎 Total Revenue      📈 Conversion Rate                   │
│     ₹2,50,000             40%                               │
└─────────────────────────────────────────────────────────────┘
```

**What you see:**
- **Total Customers:** All registered users
- **Active Trials:** Users in 7-day trial
- **Free Plan:** Users on free tier
- **Basic Plan:** ₹499/month subscribers
- **Premium Plan:** ₹999/month subscribers
- **Revenue (Period):** Earnings in selected date range
- **Total Revenue:** All-time earnings
- **Conversion Rate:** Trial to paid conversion %

---

### 2. **Date Range Filter**

```
┌─────────────────────────────────────────────────────────────┐
│  [Today ▼]  [🔄 Refresh]                                    │
│   - Today                                                    │
│   - This Week                                                │
│   - This Month  ← Selected                                  │
│   - This Year                                                │
│   - All Time                                                 │
└─────────────────────────────────────────────────────────────┘
```

**How it works:**
- Select date range from dropdown
- Stats automatically update
- Revenue shows for selected period
- Payments filter by date

---

### 3. **Recent Registrations**

```
┌─────────────────────────────────────────────────────────────┐
│  📋 Recent Registrations                                    │
├─────────────────────────────────────────────────────────────┤
│  ✅ ABC Company registered                    2 hours ago   │
│  ✅ XYZ Corp registered                       5 hours ago   │
│  ✅ PQR Ltd registered                        1 day ago     │
└─────────────────────────────────────────────────────────────┘
```

**Shows:**
- Last 5 registrations
- Business name
- Time ago

---

### 4. **Recent Payments**

```
┌─────────────────────────────────────────────────────────────┐
│  💳 Recent Payments                                         │
├─────────────────────────────────────────────────────────────┤
│  Date       Customer    Plan    Amount   Status   Payment ID│
│  02-May-26  ABC Co.     basic   ₹499     captured pay_123  │
│  01-May-26  XYZ Corp    premium ₹999     captured pay_456  │
│  30-Apr-26  PQR Ltd     basic   ₹499     pending  pay_789  │
└─────────────────────────────────────────────────────────────┘
```

**Shows:**
- Last 10 payments
- Customer name
- Plan purchased
- Amount paid
- Payment status (captured/pending/failed)
- Razorpay payment ID

---

### 5. **All Customers Table**

```
┌─────────────────────────────────────────────────────────────┐
│  👥 All Customers                                           │
│  [All (150)] [Trial (25)] [Free (50)] [Basic (60)] [Premium (15)]│
├─────────────────────────────────────────────────────────────┤
│  Business   Owner    Email         Phone      Plan   Valid  │
│  ABC Co.    John     john@abc.com  9876543210 basic  02-Jun │
│  XYZ Corp   Jane     jane@xyz.com  9876543211 premium 15-Jun│
└─────────────────────────────────────────────────────────────┘
```

**Features:**
- Filter by plan (All, Trial, Free, Basic, Premium)
- Shows all customer details
- Plan badges with colors
- Valid till date
- Registration date

---

### 6. **Plan Distribution Chart**

```
┌─────────────────────────────────────────────────────────────┐
│  📊 Plan Distribution                                       │
├─────────────────────────────────────────────────────────────┤
│  Trial  ████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░  25     │
│  Free   ████████████████████████████░░░░░░░░░░░░░░  50     │
│  Basic  ████████████████████████████████████████░░  60     │
│  Premium ████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░  15     │
└─────────────────────────────────────────────────────────────┘
```

**Shows:**
- Visual bar chart
- Number of users per plan
- Percentage distribution

---

### 7. **Revenue Breakdown**

```
┌─────────────────────────────────────────────────────────────┐
│  💰 Revenue Breakdown                                       │
├─────────────────────────────────────────────────────────────┤
│  Basic Plan Revenue          Premium Plan Revenue           │
│  ₹29,940                     ₹14,985                        │
│  60 subscribers × ₹499       15 subscribers × ₹999          │
│                                                              │
│  Average Revenue Per User                                   │
│  ₹599.00                                                    │
│  ARPU                                                        │
└─────────────────────────────────────────────────────────────┘
```

**Shows:**
- Basic plan total revenue
- Premium plan total revenue
- Number of subscribers
- ARPU (Average Revenue Per User)

---

## 🔧 API Endpoints Used

### 1. GET /admin/stats

**Request:**
```bash
curl -X GET "http://localhost:8661/admin/stats?range=month" \
  -H "X-Admin-Key: your-admin-key"
```

**Response:**
```json
{
  "total_customers": 150,
  "active_trials": 25,
  "free_plan": 50,
  "basic_plan": 60,
  "premium_plan": 15,
  "revenue_total": 25000000,
  "revenue_this_period": 4500000,
  "basic_revenue": 2994000,
  "premium_revenue": 1498500,
  "arpu": 59900,
  "conversion_rate": 40.0,
  "recent_registrations": [...]
}
```

---

### 2. GET /admin/customers

**Request:**
```bash
curl -X GET "http://localhost:8661/admin/customers" \
  -H "X-Admin-Key: your-admin-key"
```

**Response:**
```json
{
  "total": 150,
  "customers": [
    {
      "id": "uuid-123",
      "business_name": "ABC Company",
      "owner_name": "John Doe",
      "email": "john@abc.com",
      "phone": "9876543210",
      "city": "Mumbai",
      "is_active": true,
      "plan": "basic",
      "valid_till": "2026-06-02T00:00:00",
      "created_at": "2026-05-02T10:30:00"
    }
  ]
}
```

---

### 3. GET /admin/payments

**Request:**
```bash
curl -X GET "http://localhost:8661/admin/payments?range=month" \
  -H "X-Admin-Key: your-admin-key"
```

**Response:**
```json
{
  "payments": [
    {
      "id": "uuid-456",
      "customer_id": "uuid-123",
      "business_name": "ABC Company",
      "plan": "basic",
      "amount": 49900,
      "status": "captured",
      "razorpay_payment_id": "pay_MxYz123",
      "created_at": "2026-05-02T11:00:00"
    }
  ]
}
```

---

## 📈 Key Metrics Explained

### 1. **Total Customers**
- All registered users
- Includes all plans (trial, free, basic, premium)

### 2. **Active Trials**
- Users currently in 7-day trial
- Trial not expired yet

### 3. **Conversion Rate**
- Formula: `(Paid Users / Total Trials) × 100`
- Example: 60 paid users / 150 trials = 40%
- Higher is better!

### 4. **ARPU (Average Revenue Per User)**
- Formula: `Total Revenue / Paid Users`
- Example: ₹44,925 / 75 users = ₹599
- Shows average earning per paying customer

### 5. **Revenue (Period)**
- Total earnings in selected date range
- Includes only captured payments
- Excludes pending/failed payments

### 6. **Total Revenue**
- All-time earnings
- Since first payment

---

## 🎯 Common Use Cases

### Use Case 1: Check Today's Signups

1. Select "Today" from date range
2. Check "Total Customers" stat
3. View "Recent Registrations" section

### Use Case 2: Monthly Revenue Report

1. Select "This Month" from date range
2. Check "Revenue (Period)" stat
3. View "Revenue Breakdown" section
4. Export payments table (copy to Excel)

### Use Case 3: Find Specific Customer

1. Go to "All Customers" section
2. Use browser search (Ctrl+F)
3. Search by business name, email, or phone

### Use Case 4: Check Trial Conversions

1. Check "Active Trials" stat
2. Check "Conversion Rate" stat
3. Filter customers by "Trial" plan
4. See who's about to expire

### Use Case 5: Plan Distribution Analysis

1. View "Plan Distribution" chart
2. Check which plan is most popular
3. Adjust marketing strategy accordingly

---

## 🔐 Security

### Admin Key Protection

**DO NOT:**
- ❌ Hardcode admin key in frontend code
- ❌ Commit admin key to Git
- ❌ Share admin key publicly

**DO:**
- ✅ Store in localStorage (for development)
- ✅ Use environment variables (for production)
- ✅ Implement proper authentication (for production)

### Production Security

For production, implement proper authentication:

```javascript
// Add login page
function AdminLogin() {
  const [password, setPassword] = useState('');
  
  const handleLogin = () => {
    if (password === 'your-admin-password') {
      localStorage.setItem('admin_key', 'your-admin-key');
      navigate('/admin/dashboard');
    }
  };
  
  return <form onSubmit={handleLogin}>...</form>;
}
```

---

## 🎨 Customization

### Change Colors

Edit `Dashboard.css`:

```css
/* Change stat card colors */
.stat-card.trial .stat-icon { background: #your-color; }
.stat-card.basic .stat-icon { background: #your-color; }

/* Change plan badge colors */
.plan-badge.basic {
  background: #your-color;
  color: #your-text-color;
}
```

### Add More Stats

Edit `Dashboard.jsx`:

```javascript
// Add new stat card
<div className="stat-card custom">
  <div className="stat-icon">🎯</div>
  <div className="stat-content">
    <h3>Your Custom Stat</h3>
    <p className="stat-number">{stats?.your_stat || 0}</p>
    <span className="stat-label">Description</span>
  </div>
</div>
```

### Change Auto-Refresh Interval

Edit `Dashboard.jsx`:

```javascript
// Change from 30 seconds to 60 seconds
const interval = setInterval(fetchDashboardData, 60000);
```

---

## 📱 Mobile Responsive

Dashboard is fully responsive:

- **Desktop:** Full table view
- **Tablet:** Scrollable tables
- **Mobile:** Stacked cards, horizontal scroll

---

## 🐛 Troubleshooting

### Dashboard not loading?

**Check:**
1. Backend server running? http://localhost:8661
2. Admin key correct?
3. CORS configured? (ALLOWED_ORIGINS in .env)
4. Browser console for errors

### Stats showing 0?

**Check:**
1. Database has data?
2. API endpoints working? (test with cURL)
3. Date range filter correct?

### Payments not showing?

**Check:**
1. Payments table has data?
2. Payment status = "captured"?
3. Date range includes payment date?

---

## 📊 Sample Data (For Testing)

Want to test dashboard with sample data?

```sql
-- Add sample customers (SQLite)
INSERT INTO customers (id, business_name, owner_name, email, phone, city, password_hash, is_active, created_at)
VALUES 
  ('test-1', 'Test Company 1', 'John Doe', 'test1@example.com', '9876543210', 'Mumbai', 'hash', 1, datetime('now')),
  ('test-2', 'Test Company 2', 'Jane Smith', 'test2@example.com', '9876543211', 'Pune', 'hash', 1, datetime('now'));

-- Add sample licenses
INSERT INTO licenses (id, customer_id, machine_id, license_key, plan, is_active, valid_till, created_at)
VALUES
  ('lic-1', 'test-1', 'machine-1', 'key-1', 'basic', 1, datetime('now', '+30 days'), datetime('now')),
  ('lic-2', 'test-2', 'machine-2', 'key-2', 'premium', 1, datetime('now', '+30 days'), datetime('now'));

-- Add sample payments
INSERT INTO payments (id, customer_id, razorpay_payment_id, plan, amount, status, created_at)
VALUES
  ('pay-1', 'test-1', 'pay_test_123', 'basic', 49900, 'captured', datetime('now')),
  ('pay-2', 'test-2', 'pay_test_456', 'premium', 99900, 'captured', datetime('now'));
```

---

## ✅ Checklist

Before using dashboard:

- [ ] Backend server running
- [ ] Admin key configured
- [ ] Dashboard files copied
- [ ] Route added to App.jsx
- [ ] CORS configured
- [ ] Tested with sample data

---

## 📞 Support

**Need help?**
- Check API docs: http://localhost:8661/docs
- Review backend logs
- Test APIs with cURL
- Check browser console

---

**Dashboard Ready! 📊**

Access at: http://localhost:3441/admin/dashboard
