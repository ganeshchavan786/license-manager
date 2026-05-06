# SalaryPay License Server - Deployment Guide

## Requirements

- Python 3.10+
- Node.js 18+
- SQLite (default) किंवा PostgreSQL (production)

---

## Local Development Setup

### 1. Clone & Install

```bash
# Backend dependencies
pip install -r requirements.txt

# Frontend dependencies
cd frontend
npm install
cd ..
```

### 2. Environment Setup

```bash
# .env file create करा
copy .env.example .env
```

`.env` मध्ये update करा:
```env
SECRET_KEY=your-secret-key-minimum-32-chars
LICENSE_ENCRYPTION_KEY=your-encryption-key
RAZORPAY_KEY_ID=rzp_test_xxx
RAZORPAY_KEY_SECRET=your_secret
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your@gmail.com
SMTP_PASSWORD=your-app-password
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3441
```

### 3. Database Setup

```bash
# Migrations run करा
alembic upgrade head
```

### 4. Start Servers

**Backend:**
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8661 --reload
```

**Frontend (Development):**
```bash
cd frontend
npm run dev
```

**Frontend (Production Build):**
```bash
cd frontend
npm run build
```

---

## Production Deployment

### Environment Variables

```env
# Security (CHANGE THESE!)
SECRET_KEY=production-secret-key-minimum-32-chars-random
LICENSE_ENCRYPTION_KEY=production-encryption-key-32-chars
INTERNAL_API_KEY=production-internal-api-key

# Database
DATABASE_URL=sqlite:///./license.db
# किंवा PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost/salarypay

# Payment
RAZORPAY_KEY_ID=rzp_live_xxx
RAZORPAY_KEY_SECRET=live_secret_key

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=noreply@yourdomain.com
SMTP_PASSWORD=app-password

# URLs
FRONTEND_URL=https://app.yourdomain.com
ALLOWED_ORIGINS=https://app.yourdomain.com,https://admin.yourdomain.com
```

### Production Server Start

```bash
# Frontend build
cd frontend && npm run build && cd ..

# Backend (production)
python -m uvicorn app.main:app --host 0.0.0.0 --port 8661 --workers 4
```

### Nginx Configuration (Optional)

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location /api {
        proxy_pass http://localhost:8661;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        proxy_pass http://localhost:8661;
    }
}
```

---

## Database Migrations

```bash
# नवीन migration create करा
alembic revision --autogenerate -m "description"

# Latest migration apply करा
alembic upgrade head

# एक step rollback
alembic downgrade -1

# Migration history
alembic history
```

---

## Admin Account Create करणे

```bash
# First admin create
python -c "
from app.database import SessionLocal
from app.models import AdminUser
from app.services.auth import hash_password
db = SessionLocal()
admin = AdminUser(
    full_name='Admin',
    username='admin',
    password_hash=hash_password('your-password'),
    role='admin',
    is_active=True
)
db.add(admin)
db.commit()
print('Admin created!')
db.close()
"
```

---

## Testing

```bash
# Unit tests
python -m pytest tests/test_analytics.py tests/test_promo.py tests/test_invoice.py tests/test_email.py -q

# Integration tests
python -m pytest tests/test_api_analytics.py tests/test_api_promo.py tests/test_api_invoice.py -q

# All tests
python -m pytest tests/test_analytics.py tests/test_promo.py tests/test_invoice.py tests/test_email.py tests/test_api_analytics.py tests/test_api_promo.py tests/test_api_invoice.py -q
```

---

## Monitoring

### Health Check
```
GET /health
Response: { "status": "ok" }
```

### API Docs
```
GET /docs    → Swagger UI
GET /redoc   → ReDoc UI
```

### Logs
Backend logs console मध्ये दिसतात. Production मध्ये file logging add करा:

```python
# app/main.py मध्ये
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
```

---

## Backup

```bash
# Database backup
copy license.db license.db.backup.%date%

# किंवा script
python -c "import shutil, datetime; shutil.copy('license.db', f'license.db.backup.{datetime.date.today()}')"
```

---

## Troubleshooting

### Backend start होत नाही
```bash
python -c "from app.main import app; print('OK')"
```

### Database error
```bash
alembic upgrade head
```

### SMTP error
- Gmail: App Password वापरा (regular password नाही)
- Port 587: TLS enable करा
- Port 465: Direct SSL

### Frontend build error
```bash
cd frontend
rm -rf node_modules
npm install
npm run build
```
