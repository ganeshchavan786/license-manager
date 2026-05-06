# SalaryPay - VPS Production Deployment
## PM2 + Nginx Proxy Manager (Without Docker)

---

## Architecture

```
Internet (HTTPS)
       ↓
Nginx Proxy Manager (Port 80/443 + SSL)
       ↓                    ↓
app.vrushaliinfotech.com    api.vrushaliinfotech.com
       ↓                    ↓
Frontend :3441          Backend :8661
(PM2 + serve)          (PM2 + uvicorn)
```

---

## Step 1: VPS वर Prerequisites Install करा

```bash
# System update
sudo apt update && sudo apt upgrade -y

# Python 3.10+
sudo apt install -y python3 python3-pip python3-venv

# Node.js 18+
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# PM2 globally install करा
sudo npm install -g pm2

# serve (frontend static files serve करण्यासाठी)
sudo npm install -g serve

# Versions verify करा
python3 --version
node --version
pm2 --version
serve --version
```

---

## Step 2: Code Upload करा

```bash
# App directory create करा
mkdir -p /var/www/salarypay
cd /var/www/salarypay

# Option A: Git clone
git clone https://github.com/yourusername/license-server.git .

# Option B: SCP upload (Windows वरून)
# scp -r "D:\HR\license-server\*" user@YOUR_VPS_IP:/var/www/salarypay/
```

---

## Step 3: Backend Setup

```bash
cd /var/www/salarypay

# Virtual environment create करा
python3 -m venv venv

# Activate करा
source venv/bin/activate

# Dependencies install करा
pip install -r requirements.txt

# Verify
python -c "from app.main import app; print('✅ Backend OK')"

# Deactivate
deactivate
```

---

## Step 4: Environment Configuration

```bash
# .env file create करा
cp .env.example .env
nano .env
```

**.env मध्ये हे set करा:**
```env
# Database
DATABASE_URL=sqlite:////var/www/salarypay/license.db

# Security (CHANGE THESE - random strings)
SECRET_KEY=your-64-char-random-secret-key-here
LICENSE_ENCRYPTION_KEY=your-32-char-random-key-here
ENCRYPTION_KEY=your-fernet-key-here
INTERNAL_API_KEY=your-internal-key-here

# CORS - Nginx Proxy Manager domain
ALLOWED_ORIGINS=https://app.vrushaliinfotech.com,https://api.vrushaliinfotech.com

# Razorpay (Live)
RAZORPAY_KEY_ID=rzp_live_xxx
RAZORPAY_KEY_SECRET=your_live_secret

# SMTP
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@vrushaliinfotech.com

# URLs
FRONTEND_URL=https://app.vrushaliinfotech.com
SUPPORT_EMAIL=support@vrushaliinfotech.com
```

**Production keys generate करा:**
```bash
# Secret key
python3 -c "import secrets; print(secrets.token_hex(32))"

# Fernet key
source venv/bin/activate
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
deactivate
```

**File permissions secure करा:**
```bash
chmod 600 /var/www/salarypay/.env
```

---

## Step 5: Database Setup

```bash
cd /var/www/salarypay
source venv/bin/activate

# Migrations run करा
python -m alembic upgrade head

# Admin account create करा
python3 -c "
from app.database import SessionLocal, create_tables
from app.models import AdminUser
from app.services.auth import hash_password
create_tables()
db = SessionLocal()
admin = AdminUser(
    full_name='Admin',
    username='admin',
    password_hash=hash_password('YOUR_STRONG_PASSWORD_HERE'),
    role='admin',
    is_active=True
)
db.add(admin)
db.commit()
print('✅ Admin created')
db.close()
"

deactivate
```

---

## Step 6: Frontend Build

```bash
cd /var/www/salarypay/frontend

# frontend/.env update करा
echo "VITE_API_URL=https://api.vrushaliinfotech.com" > .env

# Dependencies install करा
npm install

# Production build
npm run build

# Verify
ls -la dist/
```

---

## Step 7: PM2 Ecosystem File

```bash
cd /var/www/salarypay
nano ecosystem.config.js
```

**ecosystem.config.js:**
```javascript
module.exports = {
  apps: [
    // ── Backend (FastAPI) ──────────────────────────────
    {
      name: 'salarypay-backend',
      script: '/var/www/salarypay/venv/bin/uvicorn',
      args: 'app.main:app --host 0.0.0.0 --port 8661 --workers 2',
      cwd: '/var/www/salarypay',
      interpreter: 'none',
      env: {
        PATH: '/var/www/salarypay/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
      },
      watch: false,
      autorestart: true,
      max_restarts: 10,
      restart_delay: 5000,
      log_file: '/var/log/salarypay/backend.log',
      error_file: '/var/log/salarypay/backend-error.log',
      out_file: '/var/log/salarypay/backend-out.log',
      time: true
    },

    // ── Frontend (Static Serve) ────────────────────────
    {
      name: 'salarypay-frontend',
      script: 'serve',
      args: '-s dist -l 3441',
      cwd: '/var/www/salarypay/frontend',
      interpreter: 'none',
      watch: false,
      autorestart: true,
      max_restarts: 10,
      restart_delay: 5000,
      log_file: '/var/log/salarypay/frontend.log',
      error_file: '/var/log/salarypay/frontend-error.log',
      out_file: '/var/log/salarypay/frontend-out.log',
      time: true
    }
  ]
}
```

---

## Step 8: Log Directory Create करा

```bash
sudo mkdir -p /var/log/salarypay
sudo chown $USER:$USER /var/log/salarypay
```

---

## Step 9: PM2 Start करा

```bash
cd /var/www/salarypay

# Start both services
pm2 start ecosystem.config.js

# Status check करा
pm2 status

# Logs पाहा
pm2 logs

# Server reboot नंतर auto-start enable करा
pm2 startup
# (वरील command एक sudo command देईल - ती run करा)

pm2 save
```

**Expected output:**
```
┌─────────────────────────┬────┬─────────┬──────┬───────┐
│ name                    │ id │ status  │ cpu  │ mem   │
├─────────────────────────┼────┼─────────┼──────┼───────┤
│ salarypay-backend       │ 0  │ online  │ 0%   │ 80mb  │
│ salarypay-frontend      │ 1  │ online  │ 0%   │ 30mb  │
└─────────────────────────┴────┴─────────┴──────┴───────┘
```

---

## Step 10: Nginx Proxy Manager Setup

Nginx Proxy Manager च्या dashboard मध्ये:

### Backend Proxy Host:
```
Domain Names: api.vrushaliinfotech.com
Scheme: http
Forward Hostname/IP: localhost
Forward Port: 8661
SSL: Enable (Let's Encrypt)
Force SSL: Yes
```

### Frontend Proxy Host:
```
Domain Names: app.vrushaliinfotech.com
Scheme: http
Forward Hostname/IP: localhost
Forward Port: 3441
SSL: Enable (Let's Encrypt)
Force SSL: Yes
```

---

## Step 11: Firewall (Optional)

```bash
# Public ports block करा (Nginx Proxy Manager handles 80/443)
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
# 8661 आणि 3441 public ला expose करू नका
sudo ufw enable
```

---

## Step 12: Verify करा

```bash
# PM2 status
pm2 status

# Backend health
curl http://localhost:8661/health

# Frontend
curl -I http://localhost:3441

# Logs
pm2 logs salarypay-backend --lines 20
pm2 logs salarypay-frontend --lines 20
```

**Browser मध्ये:**
- https://app.vrushaliinfotech.com → Frontend
- https://api.vrushaliinfotech.com/docs → API Docs
- https://app.vrushaliinfotech.com/admin → Admin Dashboard

---

## Daily Commands

```bash
# Status पाहा
pm2 status

# Restart करा
pm2 restart salarypay-backend
pm2 restart salarypay-frontend
pm2 restart all

# Stop करा
pm2 stop all

# Logs पाहा (live)
pm2 logs
pm2 logs salarypay-backend
pm2 logs salarypay-frontend

# Logs clear करा
pm2 flush

# Monitoring dashboard
pm2 monit
```

---

## Code Update करण्यासाठी

```bash
cd /var/www/salarypay

# 1. Database backup
source venv/bin/activate
python scripts/backup_database.py
deactivate

# 2. Code pull (git वापरत असाल तर)
git pull origin main

# 3. Backend dependencies update
source venv/bin/activate
pip install -r requirements.txt
python -m alembic upgrade head
deactivate

# 4. Frontend rebuild
cd frontend
echo "VITE_API_URL=https://api.vrushaliinfotech.com" > .env
npm install
npm run build
cd ..

# 5. Restart services
pm2 restart all

# 6. Verify
pm2 status
curl http://localhost:8661/health
```

---

## Troubleshooting

### Backend start होत नाही
```bash
pm2 logs salarypay-backend --lines 50
# Error message पाहा
```

### Frontend 404 येतो
```bash
# dist folder आहे का?
ls /var/www/salarypay/frontend/dist/
# नसेल तर rebuild करा
cd /var/www/salarypay/frontend && npm run build
pm2 restart salarypay-frontend
```

### CORS Error
```bash
# .env मध्ये ALLOWED_ORIGINS check करा
cat /var/www/salarypay/.env | grep ALLOWED_ORIGINS
# Update करा आणि restart करा
pm2 restart salarypay-backend
```

### Database Error
```bash
# Migrations run झाल्या आहेत का?
cd /var/www/salarypay
source venv/bin/activate
python -m alembic current
python -m alembic upgrade head
deactivate
pm2 restart salarypay-backend
```

---

## Security Best Practices

```bash
# .env permissions
chmod 600 /var/www/salarypay/.env

# Database permissions
chmod 600 /var/www/salarypay/license.db

# Log rotation (optional)
sudo nano /etc/logrotate.d/salarypay
```

logrotate config:
```
/var/log/salarypay/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
```

---

## Summary

| Service | Port | PM2 Name | URL |
|---------|------|----------|-----|
| Backend | 8661 | salarypay-backend | https://api.vrushaliinfotech.com |
| Frontend | 3441 | salarypay-frontend | https://app.vrushaliinfotech.com |
