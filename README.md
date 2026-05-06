# SalaryPay License Server

SalaryPay HRMS product साठी subscription आणि license management system.

## Quick Start

```bash
# 1. Dependencies install करा
pip install -r requirements.txt
cd frontend && npm install && cd ..

# 2. Environment setup
copy .env.example .env
# .env मध्ये credentials update करा

# 3. Database setup
alembic upgrade head

# 4. Backend start करा
python -m uvicorn app.main:app --host 0.0.0.0 --port 8661 --reload

# 5. Frontend start करा (new terminal)
cd frontend && npm run dev
```

**Admin Dashboard:** http://localhost:3441/admin  
**API Docs:** http://localhost:8661/docs

---

## Features

| Feature | Status | Description |
|---------|--------|-------------|
| Usage Analytics | ✅ | Feature usage tracking & dashboards |
| Promo Codes | ✅ | Discount codes for marketing |
| Email Notifications | ✅ | Welcome, trial reminders, invoices |
| Invoice Generation | ✅ | PDF invoices with GST |
| Dynamic Settings | ✅ | Database-stored configuration |

---

## Tech Stack

**Backend:** Python, FastAPI, SQLAlchemy, SQLite  
**Frontend:** React, Vite, TailwindCSS, Chart.js  
**Email:** aiosmtplib, APScheduler  
**PDF:** ReportLab  
**Auth:** JWT (python-jose)  
**Payments:** Razorpay

---

## Documentation

| Doc | Description |
|-----|-------------|
| [API Documentation](docs/API-DOCUMENTATION.md) | All API endpoints |
| [Admin Guide](docs/ADMIN-GUIDE.md) | Admin dashboard usage |
| [Features Guide](docs/FEATURES-GUIDE.md) | Feature details |
| [Deployment Guide](docs/DEPLOYMENT-GUIDE.md) | Setup & deployment |
| [Database Migrations](docs/DATABASE-MIGRATIONS.md) | Migration guide |

---

## Project Structure

```
license-server/
├── app/
│   ├── main.py          # FastAPI app
│   ├── config.py        # Configuration
│   ├── database.py      # DB connection
│   ├── models/          # SQLAlchemy models
│   ├── routers/         # API endpoints
│   ├── services/        # Business logic
│   └── templates/       # Email templates
├── frontend/
│   └── src/
│       ├── pages/       # React pages
│       └── components/  # Reusable components
├── alembic/             # DB migrations
├── tests/               # Test files
├── docs/                # Documentation
└── invoices/            # Generated PDFs
```

---

## Running Tests

```bash
python -m pytest tests/test_analytics.py tests/test_promo.py tests/test_invoice.py tests/test_email.py tests/test_api_analytics.py tests/test_api_promo.py tests/test_api_invoice.py -q
```

**Result:** 70 tests, 100% passing ✅
