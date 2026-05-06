#!/bin/bash
# SalaryPay - VPS Production Deploy Script
# Run: bash scripts/vps_deploy.sh

set -e

APP_DIR="/var/www/salarypay"
GREEN='\033[0;32m'; RED='\033[0;31m'; YELLOW='\033[1;33m'; NC='\033[0m'
ok()   { echo -e "${GREEN}✅ $1${NC}"; }
err()  { echo -e "${RED}❌ $1${NC}"; exit 1; }
warn() { echo -e "${YELLOW}⚠️  $1${NC}"; }
step() { echo -e "\n${YELLOW}── $1 ──${NC}"; }

echo "================================================"
echo " SalaryPay VPS Deploy (PM2 + No Docker)"
echo "================================================"

# ── Step 1: Prerequisites ──────────────────────────────────
step "Checking prerequisites"
command -v python3 >/dev/null || err "Python3 not found"
command -v node    >/dev/null || err "Node.js not found"
command -v pm2     >/dev/null || err "PM2 not found. Run: sudo npm install -g pm2"
command -v serve   >/dev/null || err "serve not found. Run: sudo npm install -g serve"
ok "All prerequisites found"

# ── Step 2: Log directory ──────────────────────────────────
step "Creating log directory"
sudo mkdir -p /var/log/salarypay
sudo chown $USER:$USER /var/log/salarypay
ok "Log directory ready"

# ── Step 3: Python venv ────────────────────────────────────
step "Setting up Python environment"
cd $APP_DIR
if [ ! -d "venv" ]; then
    python3 -m venv venv
    ok "Virtual environment created"
fi
source venv/bin/activate
pip install -r requirements.txt -q
ok "Python dependencies installed"

# ── Step 4: Database migrations ───────────────────────────
step "Running database migrations"
python -m alembic upgrade head
ok "Migrations complete"
deactivate

# ── Step 5: Frontend build ─────────────────────────────────
step "Building frontend"
cd $APP_DIR/frontend
npm install --silent
npm run build
ok "Frontend built"
cd $APP_DIR

# ── Step 6: PM2 start/restart ─────────────────────────────
step "Starting services with PM2"
if pm2 list | grep -q "salarypay"; then
    pm2 restart ecosystem.config.js
    ok "Services restarted"
else
    pm2 start ecosystem.config.js
    ok "Services started"
fi

# Auto-start on reboot
pm2 save
ok "PM2 startup saved"

# ── Step 7: Health check ───────────────────────────────────
step "Health check"
sleep 3
if curl -s http://localhost:8661/health | grep -q "ok"; then
    ok "Backend is healthy"
else
    warn "Backend health check failed - check logs: pm2 logs salarypay-backend"
fi

if curl -sI http://localhost:3441 | grep -q "200\|304"; then
    ok "Frontend is running"
else
    warn "Frontend check failed - check logs: pm2 logs salarypay-frontend"
fi

# ── Final Status ───────────────────────────────────────────
echo ""
echo "================================================"
pm2 status
echo "================================================"
echo ""
echo "🌐 URLs (via Nginx Proxy Manager):"
echo "   Frontend: https://app.vrushaliinfotech.com"
echo "   Backend:  https://api.vrushaliinfotech.com"
echo "   API Docs: https://api.vrushaliinfotech.com/docs"
echo ""
echo "📋 Useful commands:"
echo "   pm2 status"
echo "   pm2 logs"
echo "   pm2 restart all"
echo "================================================"
