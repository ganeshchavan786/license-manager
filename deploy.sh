#!/bin/bash
# ================================================================
# SalaryPay License Server — Ubuntu VPS Deploy Script
# ================================================================
# वापर: sudo bash deploy.sh
# ================================================================

set -e  # Error आल्यावर थांबा

echo "🚀 SalaryPay License Server Deployment Starting..."

# ── 1. System Update ────────────────────────────────────────────
echo "📦 Updating system..."
apt update && apt upgrade -y
apt install -y python3.11 python3.11-venv python3-pip postgresql postgresql-contrib nginx certbot python3-certbot-nginx git curl

# ── 2. PostgreSQL Setup ─────────────────────────────────────────
echo "🗄️ Setting up PostgreSQL..."
systemctl start postgresql
systemctl enable postgresql

# Database आणि user create करा
sudo -u postgres psql <<EOF
CREATE USER salarypay WITH PASSWORD 'CHANGE_THIS_STRONG_PASSWORD';
CREATE DATABASE licensedb OWNER salarypay;
GRANT ALL PRIVILEGES ON DATABASE licensedb TO salarypay;
EOF

echo "✅ PostgreSQL ready"

# ── 3. App Directory Setup ──────────────────────────────────────
echo "📁 Setting up app directory..."
mkdir -p /opt/salarypay-license
cd /opt/salarypay-license

# ── 4. Python Virtual Environment ──────────────────────────────
echo "🐍 Setting up Python environment..."
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip

# requirements.txt install करा
pip install -r requirements.txt

echo "✅ Python dependencies installed"

# ── 5. Environment Variables ────────────────────────────────────
echo "⚙️ Creating .env file..."

# Random secret key generate करा
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
FERNET_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")

cat > .env <<ENVFILE
DATABASE_URL=postgresql://salarypay:CHANGE_THIS_STRONG_PASSWORD@localhost:5432/licensedb
SECRET_KEY=${SECRET_KEY}
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
LICENSE_ENCRYPTION_KEY=${FERNET_KEY}
RAZORPAY_KEY_ID=rzp_live_YOUR_KEY_HERE
RAZORPAY_KEY_SECRET=YOUR_SECRET_HERE
APP_NAME=SalaryPay License Server
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
TRIAL_DAYS=7
FREE_OFFLINE_GRACE=15
BASIC_OFFLINE_GRACE=15
PREMIUM_OFFLINE_GRACE=30
ENVFILE

echo "✅ .env file created"
echo "⚠️  .env मध्ये Razorpay keys update करायला विसरू नका!"

# ── 6. Systemd Service ──────────────────────────────────────────
echo "🔧 Creating systemd service..."

cat > /etc/systemd/system/salarypay-license.service <<SERVICE
[Unit]
Description=SalaryPay License Server
After=network.target postgresql.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/salarypay-license
Environment="PATH=/opt/salarypay-license/venv/bin"
ExecStart=/opt/salarypay-license/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8001 --workers 2
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
SERVICE

systemctl daemon-reload
systemctl enable salarypay-license
systemctl start salarypay-license

echo "✅ Service created and started"

# ── 7. Nginx Reverse Proxy ──────────────────────────────────────
echo "🌐 Setting up Nginx..."

cat > /etc/nginx/sites-available/salarypay-license <<NGINX
server {
    listen 80;
    server_name YOUR_DOMAIN_OR_IP;

    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 30;
        proxy_connect_timeout 30;
    }
}
NGINX

ln -sf /etc/nginx/sites-available/salarypay-license /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

echo "✅ Nginx configured"

# ── 8. Firewall ─────────────────────────────────────────────────
echo "🔒 Setting up firewall..."
ufw allow 22    # SSH
ufw allow 80    # HTTP
ufw allow 443   # HTTPS
ufw --force enable

echo "✅ Firewall configured"

# ── 9. Status Check ─────────────────────────────────────────────
echo ""
echo "============================================"
echo "✅ DEPLOYMENT COMPLETE!"
echo "============================================"
echo ""
echo "📌 Service status:"
systemctl status salarypay-license --no-pager
echo ""
echo "🌐 API Docs: http://YOUR_VPS_IP/docs"
echo ""
echo "⚠️  पुढे हे करा:"
echo "   1. /opt/salarypay-license/.env मध्ये Razorpay keys add करा"
echo "   2. Nginx config मध्ये YOUR_DOMAIN_OR_IP बदला"
echo "   3. SSL साठी: certbot --nginx -d yourdomain.com"
echo "   4. Razorpay dashboard मध्ये webhook URL set करा:"
echo "      https://yourdomain.com/payment/webhook"
echo ""
