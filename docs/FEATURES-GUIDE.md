# SalaryPay License Server - Features Guide

## Overview

SalaryPay License Server हे एक subscription management system आहे जे SalaryPay HRMS product साठी licenses manage करते.

---

## Feature 1: Usage Analytics

### काय आहे?
Customers कोणते features किती वेळा वापरतात ते track करते.

### Customer साठी:
- Daily usage trend chart
- Feature breakdown chart
- Monthly reports
- Time period filter (7/30/90/365 days)

### Admin साठी:
- System-wide usage overview
- Top 10 features
- Unique customer counts
- Feature statistics

### API:
```
POST /api/analytics/track          → Feature usage track करा
GET  /api/analytics/dashboard      → Customer dashboard
GET  /api/analytics/monthly-report → Monthly report
GET  /api/analytics/admin/overview → Admin overview
```

---

## Feature 2: Promo Codes

### काय आहे?
Marketing campaigns साठी discount codes.

### Types:
- **Percentage:** 20% off (e.g., SAVE20)
- **Fixed:** ₹100 off (e.g., FLAT100)

### Features:
- Expiry date
- Usage limit
- Plan-specific (Basic only / Premium only / Both)
- Multi-use toggle
- Real-time validation

### Checkout Flow:
1. Customer checkout page वर promo code enter करतो
2. "Apply" click करतो
3. Discount calculate होतो
4. Final amount दिसतो
5. Payment होतो

### Admin:
- Create/Deactivate promo codes
- Usage statistics पाहणे

---

## Feature 3: Email Notifications

### Automatic Emails:
1. **Welcome Email** - Registration नंतर
2. **Trial Reminder** - Trial संपण्याच्या 3 दिवस आणि 1 दिवस आधी
3. **Renewal Confirmation** - Payment successful नंतर
4. **Invoice Email** - Invoice generate झाल्यावर

### Email Queue:
- सर्व emails queue मध्ये जातात
- APScheduler दर 1 minute ने process करतो
- Failed emails 3 वेळा retry होतात
- Admin queue पाहू शकतो

### Templates:
- `app/templates/emails/welcome.html`
- `app/templates/emails/trial_reminder.html`
- `app/templates/emails/renewal_confirmation.html`

---

## Feature 4: Invoice Generation

### Auto-Generation:
Payment successful झाल्यावर automatically invoice generate होतो.

### Invoice Contains:
- Sequential number (INV-YYYYMM-XXXX)
- Company details (from Settings)
- Customer details
- Plan details
- Base amount
- GST (18%)
- Discount (if promo code used)
- Total amount

### PDF:
- ReportLab ने generate होतो
- `invoices/` folder मध्ये save होतो
- Customer download करू शकतो
- Admin कोणाचाही download करू शकतो

---

## Feature 5: Dynamic Settings

### काय आहे?
Admin settings database मध्ये save होतात - server restart नको.

### Settings Categories:

#### SMTP Email
Email server configuration. Password encrypted (AES-128).

#### Business Info
Company details invoices मध्ये वापरले जातात.

#### Plans & Pricing
Trial days, grace periods, plan prices.

#### Plan Features
कोणत्या plan मध्ये कोणते features - UI मधून change करता येतात.

#### Payment Gateway
Razorpay credentials encrypted. Test/Live mode toggle.

#### CORS Origins
Allowed domains - multi-domain support.

#### System
Token expiry, login attempts, maintenance mode.

---

## Security Features

### Encryption:
- SMTP Password: AES-128 (Fernet)
- Razorpay Secret: AES-128 (Fernet)
- License Keys: Custom encryption
- Passwords: bcrypt/pbkdf2

### Authentication:
- JWT tokens (HS256)
- Separate customer/admin tokens
- Token expiry configurable

### Authorization:
- Customer: फक्त स्वतःचा data
- Admin: सर्व data

---

## Scheduled Jobs

APScheduler automatically run करतो:

| Job | Frequency | What |
|-----|-----------|------|
| Email Queue | Every 1 minute | Pending emails send करतो |
| Trial Reminders | Daily 9 AM | 3-day/1-day reminders |

---

## Plan Limits

| Plan | Price | Features |
|------|-------|---------|
| Trial | Free | सर्व features, 7 days |
| Free | Free | Basic features only |
| Basic | ₹499/month | Standard features |
| Premium | ₹999/month | सर्व features |

---

## Database Tables

| Table | Purpose |
|-------|---------|
| `customers` | Customer accounts |
| `licenses` | License records |
| `payments` | Payment history |
| `invoices` | Invoice records |
| `promo_codes` | Discount codes |
| `promo_code_usage` | Promo usage tracking |
| `email_queue` | Email queue |
| `usage_analytics` | Feature usage data |
| `settings` | Dynamic settings |
| `admin_users` | Admin accounts |
| `audit_logs` | Audit trail |
