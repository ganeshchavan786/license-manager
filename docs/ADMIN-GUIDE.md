# SalaryPay License Server - Admin Guide

## Admin Dashboard Access

**URL:** `http://localhost:3441/admin`  
**Login:** `http://localhost:3441/admin/login`

---

## Dashboard Tabs

### 1. Dashboard (Overview)
मुख्य statistics:
- **Total Customers** - एकूण registered customers
- **Trials** - Active trial users
- **Premium** - Premium plan users
- **Revenue** - एकूण revenue (₹)

**Recent Activity** - नवीन registrations list  
**Conversion Rate** - Trial to paid conversion %  
**ARPU** - Average Revenue Per User

---

### 2. Customers
सर्व customers ची list:
- Business name, email, join date
- Current plan (trial/free/basic/premium)
- Status (Active/Blocked)
- **Actions:**
  - Toggle status (block/unblock)
  - Manual upgrade (plan change)

**Search:** Business name किंवा email ने search करा

---

### 3. Payments
सर्व payments ची history:
- Business name, amount, status, date
- Status: `captured` (success) / `failed`

---

### 4. Invoices
सर्व invoices:
- Invoice number, customer, plan, amount, date
- **Download PDF** button
- Email status indicator (sent/not sent)

---

### 5. Analytics
System-wide usage analytics:
- Total usage across all customers
- Unique active customers
- Top 10 most-used features
- Feature statistics table

**Time Filter:** Last 7/30/90/365 days

---

### 6. Promo Codes
Discount codes manage करा:

**Create Promo Code:**
1. Code name (e.g., LAUNCH50)
2. Discount type: Percentage (%) किंवा Fixed (₹)
3. Discount value
4. Applicable plans (Basic/Premium)
5. Expiry date (optional)
6. Usage limit (optional)
7. Multi-use toggle

**Deactivate:** Active promo code बंद करा

---

### 7. Settings

#### SMTP Email Tab
Email configuration:
- SMTP Host (e.g., smtp.gmail.com)
- Port (587 for TLS, 465 for SSL)
- Username & Password (encrypted)
- From Email
- **Test Connection** button

**Gmail Setup:**
1. Google Account → Security → 2-Step Verification enable करा
2. App Passwords → Generate new password
3. 16-character password इथे वापरा

#### Business Info Tab
- Company name, address, GST number
- Support email, phone
- Invoice footer text

#### Plans & Pricing Tab
- Trial period (days)
- Grace periods per plan
- Basic/Premium prices (₹)

#### Plan Features Tab
प्रत्येक plan साठी features:
- Trial, Free, Basic, Premium
- Features add/remove करा
- `*` = सर्व features (Premium)

#### Payment Gateway Tab
Razorpay credentials:
- Key ID (rzp_test_xxx किंवा rzp_live_xxx)
- Key Secret (encrypted)
- Mode: Test/Live
- Enable/Disable toggle

#### CORS Origins Tab
Allowed domains:
- Development: http://localhost:3000
- Production: https://app.yourdomain.com

#### System Tab
- Token expiry (minutes)
- Max login attempts
- Session timeout
- Maintenance mode

---

## Common Admin Tasks

### New Customer Block करणे
1. Customers tab → Customer शोधा
2. Status button वर click करा → "Blocked"

### Manual Plan Upgrade
1. Customers tab → Customer शोधा
2. "Upgrade" button → Months enter करा

### Promo Code Create करणे
1. Promo Codes tab → "Create Promo Code"
2. Details fill करा → Submit

### Invoice Download
1. Invoices tab → Invoice शोधा
2. Download icon वर click करा

### SMTP Test
1. Settings → SMTP Email tab
2. Credentials enter करा
3. "Test Connection" click करा

---

## Logout
Sidebar च्या खाली "Logout" button वर click करा.
