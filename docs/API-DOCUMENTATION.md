# SalaryPay License Server - API Documentation

**Version:** 1.0.0  
**Base URL:** `http://localhost:8661`  
**Interactive Docs:** `http://localhost:8661/docs` (Swagger UI)

---

## Authentication

सर्व protected endpoints ला `Authorization: Bearer <token>` header लागतो.

### Token Types

| Type | Who | How to Get |
|------|-----|-----------|
| `customer` | SalaryPay customers | `POST /api/auth/login` |
| `admin` | License server admins | `POST /api/auth/admin/login` |

---

## 1. Analytics Endpoints

### Track Feature Usage
```
POST /api/analytics/track
Auth: Customer Token
```
**Request:**
```json
{
  "feature_name": "salary_processing",
  "metadata": { "employee_count": 50 }
}
```
**Response:**
```json
{ "success": true, "message": "Usage tracked successfully" }
```

---

### Get Analytics Dashboard
```
GET /api/analytics/dashboard?days=30
Auth: Customer Token
```
**Response:**
```json
{
  "total_usage": 150,
  "feature_breakdown": { "login": 50, "export": 30 },
  "daily_usage": { "2026-05-01": 10, "2026-05-02": 15 },
  "period_days": 30,
  "start_date": "2026-04-06T00:00:00Z",
  "end_date": "2026-05-06T00:00:00Z"
}
```

---

### Get Monthly Report
```
GET /api/analytics/monthly-report?year=2026&month=5
Auth: Customer Token
```
**Response:**
```json
{
  "customer_id": "uuid",
  "year": 2026,
  "month": 5,
  "total_usage_count": 200,
  "features_used": { "login": 50 },
  "daily_breakdown": { "2026-05-01": 10 },
  "generated_at": "2026-05-06T10:00:00Z"
}
```

---

### Admin: System-Wide Overview
```
GET /api/analytics/admin/overview?days=30
Auth: Admin Token
```
**Response:**
```json
{
  "total_usage": 5000,
  "unique_customers": 25,
  "feature_stats": {
    "login": { "usage_count": 1000, "unique_customers": 20 }
  },
  "top_features": { "login": { "usage_count": 1000 } },
  "period": { "start": "2026-04-06T00:00:00Z", "end": "2026-05-06T00:00:00Z" }
}
```

---

## 2. Promo Code Endpoints

### Validate Promo Code (Public)
```
POST /api/promo/validate
Auth: None
```
**Request:**
```json
{ "code": "SAVE20", "plan": "basic" }
```
**Response (Valid):**
```json
{
  "valid": true,
  "discount_type": "percentage",
  "discount_value": 20,
  "discount_amount": 9980,
  "base_amount": 49900,
  "final_amount": 39920
}
```
**Response (Invalid):**
```json
{ "valid": false, "reason": "Invalid promo code" }
```

---

### Admin: Create Promo Code
```
POST /api/promo/admin/create
Auth: Admin Token
```
**Request:**
```json
{
  "code": "LAUNCH50",
  "discount_type": "percentage",
  "discount_value": 50,
  "applicable_plans": ["basic", "premium"],
  "expiry_date": "2026-12-31T23:59:59Z",
  "usage_limit": 100,
  "is_multi_use": true
}
```

---

### Admin: List Promo Codes
```
GET /api/promo/admin/list?active_only=true
Auth: Admin Token
```
**Response:**
```json
{
  "promo_codes": [
    {
      "id": "uuid",
      "code": "LAUNCH50",
      "discount_type": "percentage",
      "discount_value": 50,
      "usage_count": 10,
      "usage_limit": 100,
      "is_active": true,
      "expiry_date": "2026-12-31T23:59:59Z"
    }
  ]
}
```

---

### Admin: Deactivate Promo Code
```
PUT /api/promo/admin/{promo_id}/deactivate
Auth: Admin Token
```
**Response:**
```json
{ "success": true, "message": "Promo code deactivated" }
```

---

## 3. Email Endpoints

### Admin: Get Email Queue
```
GET /api/email/admin/queue?status=pending&limit=50
Auth: Admin Token
```
**Response:**
```json
{
  "emails": [
    {
      "id": "uuid",
      "to_email": "customer@example.com",
      "subject": "Welcome to SalaryPay",
      "status": "pending",
      "retry_count": 0,
      "created_at": "2026-05-06T10:00:00Z"
    }
  ],
  "total": 5
}
```

---

### Admin: Retry Failed Email
```
POST /api/email/admin/retry/{email_id}
Auth: Admin Token
```
**Response:**
```json
{ "success": true, "message": "Email queued for retry" }
```

---

## 4. Invoice Endpoints

### List Customer Invoices
```
GET /api/invoices/list?limit=20&offset=0
Auth: Customer Token
```
**Response:**
```json
{
  "invoices": [
    {
      "id": "uuid",
      "invoice_number": "INV-202605-0001",
      "plan": "basic",
      "base_amount": 49900,
      "gst_amount": 8982,
      "total_amount": 58882,
      "discount_amount": 0,
      "invoice_date": "2026-05-06T10:00:00Z",
      "pdf_available": true,
      "is_emailed": true
    }
  ],
  "total": 3
}
```

---

### Get Invoice Detail
```
GET /api/invoices/{invoice_id}
Auth: Customer Token
```

---

### Download Invoice PDF
```
GET /api/invoices/{invoice_id}/download
Auth: Customer Token
Response: PDF file (application/pdf)
```

---

### Email Invoice to Customer
```
POST /api/invoices/{invoice_id}/email
Auth: Customer Token
```
**Response:**
```json
{ "success": true, "message": "Invoice emailed successfully" }
```

---

### Admin: List All Invoices
```
GET /api/invoices/admin/list?customer_id=uuid&limit=100
Auth: Admin Token
```

---

### Admin: Download Any Invoice
```
GET /api/invoices/admin/{invoice_id}/download
Auth: Admin Token
Response: PDF file (application/pdf)
```

---

## 5. Settings Endpoints

### Get SMTP Settings
```
GET /api/admin/settings/smtp
Auth: Admin Token
```
**Response:**
```json
{
  "smtp_host": "smtp.gmail.com",
  "smtp_port": 587,
  "smtp_username": "your@gmail.com",
  "smtp_password": "yo***",
  "smtp_from_email": "noreply@salarypay.com",
  "smtp_use_tls": true
}
```

---

### Save SMTP Settings
```
POST /api/admin/settings/smtp
Auth: Admin Token
```
**Request:**
```json
{
  "smtp_host": "smtp.gmail.com",
  "smtp_port": 587,
  "smtp_username": "your@gmail.com",
  "smtp_password": "your-app-password",
  "smtp_from_email": "noreply@salarypay.com",
  "smtp_use_tls": true
}
```

---

### Test SMTP Connection
```
POST /api/admin/settings/smtp/test
Auth: Admin Token
```
**Request:**
```json
{
  "smtp_host": "smtp.gmail.com",
  "smtp_port": 587,
  "smtp_username": "your@gmail.com",
  "smtp_password": "your-app-password",
  "smtp_use_tls": true
}
```
**Response:**
```json
{ "success": true, "message": "✅ SMTP connection and authentication successful!" }
```

---

### Get/Save Business Settings
```
GET  /api/admin/settings/business
POST /api/admin/settings/business
Auth: Admin Token
```
**Fields:** `app_name`, `support_email`, `frontend_url`, `company_address`, `company_gst`, `company_phone`, `invoice_footer`

---

### Get/Save Plan Settings
```
GET  /api/admin/settings/plans
POST /api/admin/settings/plans
Auth: Admin Token
```
**Fields:** `trial_days`, `free_offline_grace`, `basic_offline_grace`, `premium_offline_grace`, `basic_price`, `premium_price`

---

### Get/Save Plan Features
```
GET  /api/admin/settings/plans/features
POST /api/admin/settings/plans/features
Auth: Admin Token
```
**Request:**
```json
{
  "trial": ["attendance_face", "employees_unlimited", "salary_full"],
  "free": ["attendance_basic", "employees_5"],
  "basic": ["attendance_face", "employees_25", "salary_full"],
  "premium": ["*"]
}
```

---

### Get/Save Payment Gateway Settings
```
GET  /api/admin/settings/payment-gateway
POST /api/admin/settings/payment-gateway
Auth: Admin Token
```
**Request:**
```json
{
  "razorpay_key_id": "rzp_test_xxx",
  "razorpay_key_secret": "secret_key",
  "payment_gateway_enabled": true,
  "payment_gateway_mode": "test"
}
```

---

### Get/Save CORS Origins
```
GET  /api/admin/settings/cors/origins
POST /api/admin/settings/cors/origins
Auth: Admin Token
```
**Request:**
```json
{ "origins": ["http://localhost:3000", "https://app.example.com"] }
```

---

### Get/Save System Settings
```
GET  /api/admin/settings/system
POST /api/admin/settings/system
Auth: Admin Token
```
**Fields:** `access_token_expire_minutes`, `maintenance_mode`, `max_login_attempts`, `session_timeout_minutes`

---

## Error Responses

| Status | Meaning |
|--------|---------|
| `400` | Bad Request - Invalid input |
| `401` | Unauthorized - Missing or invalid token |
| `403` | Forbidden - Insufficient permissions |
| `404` | Not Found - Resource doesn't exist |
| `422` | Validation Error - Request body invalid |
| `500` | Server Error - Internal error |

**Error Format:**
```json
{ "detail": "Error message here" }
```

---

## Rate Limits

Currently no rate limiting. Recommended for production:
- Analytics track: 100 req/min per customer
- Promo validate: 20 req/min per IP
- Invoice download: 10 req/min per customer
