#!/bin/bash
# SalaryPay License Server - Linux Auto Setup Script
# Run on Ubuntu/Debian VPS:
# bash scripts/linux_setup.sh

set -e

APP_DIR="/home/salarypay/app"
SERVICE_NAME="salarypay"
PORT=8661

echo "================================================"
echo "SalaryPay License Server - Linux Setup"
echo "================================================"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

ok()  { echo -e "${GREEN}✅ $1${NC}"; }
err() { echo -e "${RED}❌ $1${NC}"; exit 1; }
warn() { echo -e "${YELLOW}⚠️  $1${NC}"; }

# Check if running as root or sudo
if [ "$EUID" -ne 0 ]; then
    err "Please run as root: sudo bash scripts/linux_setup.sh"
fi

# ── Step 1: System Update ──────────────────────────────────
echo ""
echo "Step 1: Updating system..."
apt update -q && apt upgrade -y -q
ok "System updated"

# ── Step 2: Install Dependencies ──────────────────────────
echo ""
echo "Step 2: Installing dependencies..."
apt install -y -q python3 python3-pip python3-venv nginx git curl supervisor ufw

# Node.js 18
if ! node --version 2>/dev/null | grep -q "v18\|v20"; then
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
    apt install -y -q nodejs
fi
ok "Dependencies installed"

# ── Step 3: Create User ────────────────────────────────────
echo ""
echo "Step 3: Setting up user..."
if ! id "salarypay" &>/dev/null; then
    useradd -m -s /bin/bash salarypay
    ok "User 'salarypay' created"
else
    warn "User 'salarypay' already exists"
fi

# ── Step 4: Setup Application ─────────────────────────────
echo ""
echo "Step 4: Setting up application..."

# Create app directory
mkdir -p $APP_DIR
chown -R salarypay:salarypay /home/salarypay

# Copy current directory to app dir (if running from project)
if [ -f "requirements.txt" ]; then
    cp -r . $APP_DIR/
    chown -R salarypay:salarypay $APP_DIR
    ok "Files copied to $APP_DIR"
fi

# ── Step 5: Python Virtual Environment ────────────────────
echo ""
echo "Step 5: Setting up Python environment..."
cd $APP_DIR
sudo -u salarypay python3 -m venv venv
sudo -u salarypay $APP_DIR/venv/bin/pip install -r requirements.txt -q
ok "Python environment ready"

# ── Step 6: Environment File ───────────────────────────────
echo ""
echo "Step 6: Environment configuration..."
if [ ! -f "$APP_DIR/.env" ]; then
    cp $APP_DIR/.env.example $APP_DIR/.env
    chown salarypay:salarypay $APP_DIR/.env
    chmod 600 $APP_DIR/.env
    warn ".env file created - Please update with your values!"
    warn "Edit: nano $APP_DIR/.env"
else
    ok ".env file exists"
fi

# ── Step 7: Database Migrations ───────────────────────────
echo ""
echo "Step 7: Running database migrations..."
sudo -u salarypay bash -c "cd $APP_DIR && source venv/bin/activate && python -m alembic upgrade head"
ok "Database migrations complete"

# ── Step 8: Frontend Build ─────────────────────────────────
echo ""
echo "Step 8: Building frontend..."
sudo -u salarypay bash -c "cd $APP_DIR/frontend && npm install --silent && npm run build"
ok "Frontend built"

# ── Step 9: Systemd Service ────────────────────────────────
echo ""
echo "Step 9: Creating systemd service..."
cat > /etc/systemd/system/$SERVICE_NAME.service << EOF
[Unit]
Description=SalaryPay License Server
After=network.target

[Service]
Type=simple
User=salarypay
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 2
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable $SERVICE_NAME
systemctl start $SERVICE_NAME
sleep 3

if systemctl is-active --quiet $SERVICE_NAME; then
    ok "Service started successfully"
else
    err "Service failed to start. Check: journalctl -u $SERVICE_NAME -n 20"
fi

# ── Step 10: Nginx Configuration ──────────────────────────
echo ""
echo "Step 10: Configuring Nginx..."

# Get server IP
SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || hostname -I | awk '{print $1}')

cat > /etc/nginx/sites-available/$SERVICE_NAME << EOF
server {
    listen 80;
    server_name $SERVER_IP _;

    location / {
        proxy_pass http://127.0.0.1:$PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
        client_max_body_size 10M;
    }
}
EOF

ln -sf /etc/nginx/sites-available/$SERVICE_NAME /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

nginx -t && systemctl restart nginx && systemctl enable nginx
ok "Nginx configured"

# ── Step 11: Firewall ──────────────────────────────────────
echo ""
echo "Step 11: Configuring firewall..."
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable
ok "Firewall configured"

# ── Step 12: Invoices Directory ───────────────────────────
mkdir -p $APP_DIR/invoices
chown salarypay:salarypay $APP_DIR/invoices

# ── Final Status ───────────────────────────────────────────
echo ""
echo "================================================"
echo "✅ Setup Complete!"
echo "================================================"
echo ""
echo "Server IP: $SERVER_IP"
echo ""
echo "Access:"
echo "  Frontend:   http://$SERVER_IP"
echo "  Admin:      http://$SERVER_IP/admin"
echo "  API Docs:   http://$SERVER_IP/docs"
echo ""
echo "Next Steps:"
echo "  1. Update .env: nano $APP_DIR/.env"
echo "  2. Create admin: python scripts/setup_production.py"
echo "  3. Restart: sudo systemctl restart $SERVICE_NAME"
echo ""
echo "Useful Commands:"
echo "  Logs:    sudo journalctl -u $SERVICE_NAME -f"
echo "  Status:  sudo systemctl status $SERVICE_NAME"
echo "  Restart: sudo systemctl restart $SERVICE_NAME"
echo "  Backup:  cd $APP_DIR && python scripts/backup_database.py"
echo "================================================"
