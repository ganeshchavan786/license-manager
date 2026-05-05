# 🧪 API Testing Guide - SalaryPay License Server

**Postman Collection** | **cURL Examples** | **Test Scenarios**

---

## 📋 Table of Contents

1. [Setup](#setup)
2. [Authentication APIs](#authentication-apis)
3. [License APIs](#license-apis)
4. [Payment APIs](#payment-apis)
5. [Admin APIs](#admin-apis)
6. [Test Scenarios](#test-scenarios)

---

## 🚀 Setup

### Base URL

```
Development: http://localhost:8661
Production: https://license.yourdomain.com
```

### Headers

```
Content-Type: application/json
```

For admin endpoints:
```
X-Admin-Key: your-secret-key-from-env
```

---

## 🔐 Authentication APIs

### 1. Register New Customer

**Endpoint:** `POST /auth/register`

**Request:**
```json
{
  "business_name": "ABC Company",
  "owner_name": "John Doe",
  "email": "john@abc.com",
  "phone": "9876543210",
  "city": "Mumbai",
  "password": "securepass123",
  "machine_id": "test-machine-001"
}
```

**cURL:**
```bash
curl -X POST http://localhost:8661/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "business_name": "ABC Company",
    "owner_name": "John Doe",
    "email": "john@abc.com",
    "phone": "9876543210",
    "city": "Mumbai",
    "password": "securepass123",
    "machine_id": "test-machine-001"
  }'
```

**Response (200 OK):**
```json
{
  "customer_id": "550e8400-e29b-41d4-a716-446655440000",
  "license_key": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "plan": "trial",
  "trial_days": 7,
  "message": "Registration successful! 7-day free trial activated."
}
```

**Error (400 Bad Request):**
```json
{
  "detail": "Email already registered"
}
```

---

### 2. Login

**Endpoint:** `POST /auth/login`

**Request:**
```json
{
  "email": "john@abc.com",
  "password": "securepass123",
  "machine_id": "test-machine-001"
}
```

**cURL:**
```bash
curl -X POST http://localhost:8661/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@abc.com",
    "password": "securepass123",
    "machine_id": "test-machine-001"
  }'
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "customer_id": "550e8400-e29b-41d4-a716-446655440000",
  "business_name": "ABC Company",
  "license_key": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "plan": "trial"
}
```

**Error (401 Unauthorized):**
```json
{
  "detail": "Invalid email or password"
}
```

---

## 📜 License APIs

### 3. Validate License

**Endpoint:** `POST /license/validate`

**Request:**
```json
{
  "machine_id": "test-machine-001",
  "license_key": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**cURL:**
```bash
curl -X POST http://localhost:8661/license/validate \
  -H "Content-Type: application/json" \
  -d '{
    "machine_id": "test-machine-001",
    "license_key": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'
```

**Response (200 OK) - Valid License:**
```json
{
  "valid": true,
  "plan": "trial",
  "features": [
    "attendance_face",
    "employees_unlimited",
    "salary_full",
    "tax",
    "loans",
    "export_pdf",
    "export_excel",
    "leaves",
    "reports_full",
    "holidays"
  ],
  "grace_period_days": 15,
  "days_remaining": 5,
  "valid_till": "2026-05-09T00:00:00+00:00",
  "encrypted_cache": "gAAAAABmXYZ..."
}
```

**Response (200 OK) - Invalid License:**
```json
{
  "valid": false,
  "plan": "free",
  "features": [],
  "grace_period_days": 15,
  "days_remaining": null,
  "valid_till": null,
  "encrypted_cache": null,
  "reason": "License not found"
}
```

---

### 4. Get License Status

**Endpoint:** `GET /license/status/{machine_id}`

**cURL:**
```bash
curl -X GET http://localhost:8661/license/status/test-machine-001
```

**Response (200 OK):**
```json
{
  "found": true,
  "plan": "basic",
  "valid_till": "2026-06-02T00:00:00+00:00",
  "business_name": "ABC Company",
  "email": "john@abc.com"
}
```

**Response (200 OK) - Not Found:**
```json
{
  "found": false
}
```

---

## 💳 Payment APIs

### 5. Create Payment Order

**Endpoint:** `POST /payment/create-order`

**Request:**
```json
{
  "plan": "basic",
  "customer_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**cURL:**
```bash
curl -X POST http://localhost:8661/payment/create-order \
  -H "Content-Type: application/json" \
  -d '{
    "plan": "basic",
    "customer_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

**Response (200 OK):**
```json
{
  "order_id": "order_MxYz123ABC",
  "amount": 49900,
  "currency": "INR",
  "plan": "basic"
}
```

**Error (400 Bad Request):**
```json
{
  "detail": "Invalid plan"
}
```

---

### 6. Verify Payment

**Endpoint:** `POST /payment/verify`

**Request:**
```json
{
  "razorpay_order_id": "order_MxYz123ABC",
  "razorpay_payment_id": "pay_AbCd456XYZ",
  "razorpay_signature": "a1b2c3d4e5f6...",
  "customer_id": "550e8400-e29b-41d4-a716-446655440000",
  "plan": "basic"
}
```

**cURL:**
```bash
curl -X POST http://localhost:8661/payment/verify \
  -H "Content-Type: application/json" \
  -d '{
    "razorpay_order_id": "order_MxYz123ABC",
    "razorpay_payment_id": "pay_AbCd456XYZ",
    "razorpay_signature": "a1b2c3d4e5f6...",
    "customer_id": "550e8400-e29b-41d4-a716-446655440000",
    "plan": "basic"
  }'
```

**Response (200 OK):**
```json
{
  "success": true,
  "plan": "basic",
  "license_key": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "valid_till": "2026-06-02T00:00:00+00:00",
  "message": "Basic plan activated successfully!"
}
```

**Error (400 Bad Request):**
```json
{
  "detail": "Invalid payment signature"
}
```

---

## 👨‍💼 Admin APIs

### 7. Get All Customers

**Endpoint:** `GET /admin/customers`

**Headers:**
```
X-Admin-Key: your-secret-key-from-env
```

**cURL:**
```bash
curl -X GET http://localhost:8661/admin/customers \
  -H "X-Admin-Key: your-secret-key-from-env"
```

**Response (200 OK):**
```json
{
  "customers": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "business_name": "ABC Company",
      "owner_name": "John Doe",
      "email": "john@abc.com",
      "phone": "9876543210",
      "city": "Mumbai",
      "is_active": true,
      "created_at": "2026-05-02T10:30:00+00:00",
      "plan": "trial",
      "valid_till": "2026-05-09T00:00:00+00:00"
    }
  ],
  "total": 1
}
```

---

### 8. Get Dashboard Stats

**Endpoint:** `GET /admin/stats`

**Headers:**
```
X-Admin-Key: your-secret-key-from-env
```

**cURL:**
```bash
curl -X GET http://localhost:8661/admin/stats \
  -H "X-Admin-Key: your-secret-key-from-env"
```

**Response (200 OK):**
```json
{
  "total_customers": 150,
  "active_trials": 25,
  "free_plan": 50,
  "basic_plan": 60,
  "premium_plan": 15,
  "revenue_this_month": 45000,
  "revenue_total": 250000
}
```

---

### 9. Manual Upgrade Customer

**Endpoint:** `POST /admin/customers/{customer_id}/upgrade`

**Headers:**
```
X-Admin-Key: your-secret-key-from-env
```

**Request:**
```json
{
  "plan": "premium",
  "months": 1
}
```

**cURL:**
```bash
curl -X POST http://localhost:8661/admin/customers/550e8400-e29b-41d4-a716-446655440000/upgrade \
  -H "X-Admin-Key: your-secret-key-from-env" \
  -H "Content-Type: application/json" \
  -d '{
    "plan": "premium",
    "months": 1
  }'
```

**Response (200 OK):**
```json
{
  "success": true,
  "customer_id": "550e8400-e29b-41d4-a716-446655440000",
  "plan": "premium",
  "valid_till": "2026-06-02T00:00:00+00:00",
  "message": "Customer upgraded to premium plan"
}
```

---

## 🧪 Test Scenarios

### Scenario 1: Complete User Journey

```bash
# 1. Register new customer
curl -X POST http://localhost:8661/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "business_name": "Test Company",
    "owner_name": "Test User",
    "email": "test@example.com",
    "phone": "9999999999",
    "city": "Test City",
    "password": "test123",
    "machine_id": "test-001"
  }'

# Save license_key from response

# 2. Validate license (should show trial plan)
curl -X POST http://localhost:8661/license/validate \
  -H "Content-Type: application/json" \
  -d '{
    "machine_id": "test-001",
    "license_key": "YOUR_LICENSE_KEY_HERE"
  }'

# 3. Create payment order
curl -X POST http://localhost:8661/payment/create-order \
  -H "Content-Type: application/json" \
  -d '{
    "plan": "basic",
    "customer_id": "YOUR_CUSTOMER_ID_HERE"
  }'

# 4. (In real scenario, user pays via Razorpay)
# 5. Verify payment (use test signature)

# 6. Validate license again (should show basic plan)
curl -X POST http://localhost:8661/license/validate \
  -H "Content-Type: application/json" \
  -d '{
    "machine_id": "test-001",
    "license_key": "YOUR_NEW_LICENSE_KEY_HERE"
  }'
```

---

### Scenario 2: Trial Expiry

```bash
# 1. Register customer
# 2. Wait 7 days (or manually update database)
# 3. Validate license - should downgrade to free plan

# Manual database update (for testing):
sqlite3 license.db
UPDATE licenses SET trial_end = datetime('now', '-1 day') WHERE machine_id = 'test-001';
.exit

# 4. Validate again
curl -X POST http://localhost:8661/license/validate \
  -H "Content-Type: application/json" \
  -d '{
    "machine_id": "test-001",
    "license_key": "YOUR_LICENSE_KEY_HERE"
  }'
```

---

### Scenario 3: Offline Mode

```bash
# 1. Validate license online (save encrypted_cache)
curl -X POST http://localhost:8661/license/validate \
  -H "Content-Type: application/json" \
  -d '{
    "machine_id": "test-001",
    "license_key": "YOUR_LICENSE_KEY_HERE"
  }'

# 2. Stop backend server
# 3. Frontend will use cached license for 15-30 days
# 4. After grace period, app will block
```

---

### Scenario 4: Admin Operations

```bash
# 1. Get all customers
curl -X GET http://localhost:8661/admin/customers \
  -H "X-Admin-Key: your-secret-key"

# 2. Get stats
curl -X GET http://localhost:8661/admin/stats \
  -H "X-Admin-Key: your-secret-key"

# 3. Manually upgrade a customer
curl -X POST http://localhost:8661/admin/customers/CUSTOMER_ID/upgrade \
  -H "X-Admin-Key: your-secret-key" \
  -H "Content-Type: application/json" \
  -d '{
    "plan": "premium",
    "months": 1
  }'
```

---

## 📊 Postman Collection

### Import this JSON into Postman:

```json
{
  "info": {
    "name": "SalaryPay License Server",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Auth",
      "item": [
        {
          "name": "Register",
          "request": {
            "method": "POST",
            "header": [{"key": "Content-Type", "value": "application/json"}],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"business_name\": \"ABC Company\",\n  \"owner_name\": \"John Doe\",\n  \"email\": \"john@abc.com\",\n  \"phone\": \"9876543210\",\n  \"city\": \"Mumbai\",\n  \"password\": \"securepass123\",\n  \"machine_id\": \"test-machine-001\"\n}"
            },
            "url": {
              "raw": "{{base_url}}/auth/register",
              "host": ["{{base_url}}"],
              "path": ["auth", "register"]
            }
          }
        },
        {
          "name": "Login",
          "request": {
            "method": "POST",
            "header": [{"key": "Content-Type", "value": "application/json"}],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"email\": \"john@abc.com\",\n  \"password\": \"securepass123\",\n  \"machine_id\": \"test-machine-001\"\n}"
            },
            "url": {
              "raw": "{{base_url}}/auth/login",
              "host": ["{{base_url}}"],
              "path": ["auth", "login"]
            }
          }
        }
      ]
    },
    {
      "name": "License",
      "item": [
        {
          "name": "Validate",
          "request": {
            "method": "POST",
            "header": [{"key": "Content-Type", "value": "application/json"}],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"machine_id\": \"test-machine-001\",\n  \"license_key\": \"{{license_key}}\"\n}"
            },
            "url": {
              "raw": "{{base_url}}/license/validate",
              "host": ["{{base_url}}"],
              "path": ["license", "validate"]
            }
          }
        }
      ]
    }
  ],
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:8661"
    },
    {
      "key": "license_key",
      "value": ""
    }
  ]
}
```

---

## 🔍 Testing Checklist

### Registration & Trial
- [ ] Register new customer
- [ ] Check 7-day trial activated
- [ ] Validate license shows trial plan
- [ ] Check all features available

### Payment Flow
- [ ] Create payment order
- [ ] Complete payment (Razorpay test mode)
- [ ] Verify payment signature
- [ ] Check license upgraded
- [ ] Validate shows new plan features

### Offline Mode
- [ ] Validate online (get cache)
- [ ] Stop backend
- [ ] Frontend uses cache
- [ ] Grace period countdown works
- [ ] After grace period, app blocks

### Admin Operations
- [ ] Get all customers
- [ ] Get dashboard stats
- [ ] Manual upgrade customer
- [ ] Check audit logs

### Error Handling
- [ ] Duplicate email registration
- [ ] Invalid login credentials
- [ ] Invalid license key
- [ ] Invalid payment signature
- [ ] Expired trial

---

## 📝 Notes

- Use **test mode** Razorpay keys for testing
- **SQLite** database for development
- Check **audit_logs** table for all actions
- Use **Swagger UI** at http://localhost:8661/docs for interactive testing

---

**Happy Testing! 🧪**
