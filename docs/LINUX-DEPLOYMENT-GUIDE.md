# SalaryPay License Server - Linux VPS Deployment Guide
## Ubuntu/Debian - Without Docker

---

## Prerequisites

- Ubuntu 20.04+ किंवा Debian 11+
- Root किंवा sudo access
- Domain name (optional but recommended)
- Minimum: 1 CPU, 1GB RAM, 10GB disk

---

## Step 1: Server Initial Setup

```bash
# System update करा
sudo apt update && sudo apt upgrade -y

# Required packages install करा
sudo apt install -y \
    python3 python3-pip python3-venv \
    nodejs npm \
    nginx \
    git \
    curl \
    supervisor \
    ufw

# Node.js 18+ install करा (if needed)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Versions check करा
python3 --version   # 3.10+
node --version      # 18+
npm --version
nginx -v
```

---

## Step 2: Application User Create करा

```bash
# Dedicated user create करा (security साठी)
sudo useradd -m -s /bin/bash salarypay
sudo passwd salarypay

# sudo access द्या (optional)
sudo usermod -aG sudo salarypay

# salarypay user म्हणून login करा
sudo su - salarypay
```

---

## Step 3: Code Upload करा

### Option A: Git Clone
```bash
cd /home/salarypay
git clone https://github.com/yourusername/license-server.git app
cd app
```

### Option B: SCP Upload (Windows वरून)
```bash
# Windows terminal मध्ये run करा:
scp -r "D:\HR\license-server" salarypay@YOUR_SERVER_IP:/home/salarypay/app
```

### Option C: SFTP (FileZilla वापरा)
1. FileZilla open करा
2. Host: YOUR_SERVER_IP, Username: salarypay
3. `/home/salarypay/app` folder मध्ये files upload करा

---

## Step 4: Python Virtual Environment

```bash
cd /home/salarypay/app

# Virtual environment create करा
python3 -m venv venv

# Activate करा
source venv/bin/activate

# Dependencies install करा
pip install -r requirements.txt

# Verify
python -c "from app.main import app; print('✅ Backend OK')"
```

---

## Step 5: Environment Configuration

```bash
# .env file create करा
cp .env.example .env
nano .env
```

`.env` मध्ये हे update करा:
```env
# Database
DATABASE_URL=sqlite:////home/salarypay/app/license.db

# Security Keys (CHANGE THESE!)
SECRET_KEY=your-random-64-char-secret-key-here
LICENSE_ENCRYPTION_KEY=your-random-32-char-key-here
ENCRYPTION_KEY=your-fernet-key-here

# Razorpay (Live keys)
RAZORPAY_KEY_ID=rzp_live_xxx
RAZORPAY_KEY_SECRET=your_live_secret

# SMTP
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@yourdomain.com

# URLs
FRONTEND_URL=https://yourdomain.com
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Internal
INTERNAL_API_KEY=your-internal-key
```

**Production keys generate करा:**
```bash
# Secret key
python3 -c "import secrets; print(secrets.token_hex(32))"

# Fernet key
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

---

## Step 6: Database Setup

```bash
# Migrations run करा
source venv/bin/activate
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
    password_hash=hash_password('YOUR_STRONG_PASSWORD'),
    role='admin',
    is_active=True
)
db.add(admin)
db.commit()
print('✅ Admin created')
db.close()
"
```

---

## Step 7: Frontend Build

```bash
cd /home/salarypay/app/frontend

# Dependencies install करा
npm install

# Production build
npm run build

# Build verify करा
ls -la dist/
```

---

## Step 8: Systemd Service (Auto-start)

```bash
# Service file create करा
sudo nano /etc/systemd/system/salarypay.service
```

File content:
```ini
[Unit]
Description=SalaryPay License Server
After=network.target

[Service]
Type=simple
User=salarypay
WorkingDirectory=/home/salarypay/app
Environment="PATH=/home/salarypay/app/venv/bin"
ExecStart=/home/salarypay/app/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8661 --workers 2
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

```bash
# Service enable आणि start करा
sudo systemctl daemon-reload
sudo systemctl enable salarypay
sudo systemctl start salarypay

# Status check करा
sudo systemctl status salarypay

# Logs पाहा
sudo journalctl -u salarypay -f
```

---

## Step 9: Nginx Configuration

```bash
# Nginx config create करा
sudo nano /etc/nginx/sites-available/salarypay
```

**Without Domain (IP only):**
```nginx
server {
    listen 80;
    server_name YOUR_SERVER_IP;

    # Frontend static files
    location / {
        proxy_pass http://127.0.0.1:8661;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
    }

    # API endpoints
    location /api {
        proxy_pass http://127.0.0.1:8661;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 300;
    }

    # File uploads size
    client_max_body_size 10M;
}
```

**With Domain + SSL:**
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8661;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300;
        client_max_body_size 10M;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/salarypay /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test config
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

---

## Step 10: SSL Certificate (Free - Let's Encrypt)

```bash
# Certbot install करा
sudo apt install -y certbot python3-certbot-nginx

# Certificate generate करा
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal test
sudo certbot renew --dry-run
```

---

## Step 11: Firewall Setup

```bash
# UFW configure करा
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# Status check
sudo ufw status
```

---

## Step 12: Verify Deployment

```bash
# Service status
sudo systemctl status salarypay
sudo systemctl status nginx

# Health check
curl http://localhost:8661/health

# Logs
sudo journalctl -u salarypay --since "5 minutes ago"
```

**Browser मध्ये:**
- `http://YOUR_SERVER_IP` → Frontend
- `http://YOUR_SERVER_IP/docs` → API docs
- `http://YOUR_SERVER_IP/admin` → Admin dashboard

---

## Maintenance Commands

```bash
# Service restart
sudo systemctl restart salarypay

# Logs पाहा
sudo journalctl -u salarypay -f --lines=100

# Database backup
cd /home/salarypay/app
source venv/bin/activate
python scripts/backup_database.py

# Code update करा
cd /home/salarypay/app
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python -m alembic upgrade head
cd frontend && npm run build && cd ..
sudo systemctl restart salarypay
```

---

## Troubleshooting

### Service start होत नाही
```bash
sudo journalctl -u salarypay -n 50
# Error message पाहा
```

### Port already in use
```bash
sudo lsof -i :8661
sudo kill -9 PID
```

### Permission error
```bash
sudo chown -R salarypay:salarypay /home/salarypay/app
chmod 755 /home/salarypay/app
```

### Nginx 502 Bad Gateway
```bash
# Backend running आहे का?
sudo systemctl status salarypay
curl http://localhost:8661/health
```

### Database locked
```bash
# SQLite lock issue
sudo systemctl restart salarypay
```

---

## Performance Tuning

### Multiple Workers (High Traffic)
```ini
# /etc/systemd/system/salarypay.service मध्ये
ExecStart=.../uvicorn app.main:app --host 0.0.0.0 --port 8661 --workers 4
```

### PostgreSQL (Production Recommended)
```bash
# PostgreSQL install
sudo apt install -y postgresql postgresql-contrib

# Database create
sudo -u postgres psql
CREATE DATABASE salarypay;
CREATE USER salaypay_user WITH PASSWORD 'strong_password';
GRANT ALL PRIVILEGES ON DATABASE salarypay TO salaypay_user;
\q

# .env update
DATABASE_URL=postgresql://salaypay_user:strong_password@localhost/salarypay

# Migrations run
python -m alembic upgrade head
```

---

## Security Checklist

- [ ] Strong SECRET_KEY (64+ chars)
- [ ] Strong LICENSE_ENCRYPTION_KEY (32+ chars)
- [ ] Firewall enabled (UFW)
- [ ] SSL certificate installed
- [ ] Regular database backups
- [ ] Log monitoring
- [ ] .env file permissions: `chmod 600 .env`
- [ ] Razorpay live keys configured
- [ ] SMTP configured and tested
