#!/bin/bash
# ============================================================
# SalaryPay License Server - Complete VPS Setup Script
# Run: bash scripts/vps_setup_complete.sh
# ============================================================

set -e
APP_DIR="/opt/license-manager"
GREEN='\033[0;32m'; RED='\033[0;31m'; YELLOW='\033[1;33m'; NC='\033[0m'
ok()   { echo -e "${GREEN}✅ $1${NC}"; }
err()  { echo -e "${RED}❌ $1${NC}"; exit 1; }
step() { echo -e "\n${YELLOW}━━━ $1 ━━━${NC}"; }

echo "================================================"
echo " SalaryPay License Server - Complete Setup"
echo "================================================"

cd $APP_DIR

# ── Step 1: Git pull (force) ───────────────────────────────
step "1. Pulling latest code"
git fetch origin main
git reset --hard origin/main
ok "Code updated"

# ── Step 2: Python venv + dependencies ────────────────────
step "2. Python dependencies"
source venv/bin/activate
pip install -r requirements.txt -q
ok "Python dependencies installed"

# ── Step 3: Database migrations ───────────────────────────
step "3. Database migrations"
# Stamp current state if alembic_version table doesn't exist
python3 -c "
from app.database import engine
from sqlalchemy import inspect, text
inspector = inspect(engine)
tables = inspector.get_table_names()
print(f'Existing tables: {tables}')
if 'alembic_version' not in tables and 'usage_analytics' in tables:
    # Tables exist but no alembic tracking - stamp as head
    with engine.connect() as conn:
        conn.execute(text('CREATE TABLE IF NOT EXISTS alembic_version (version_num VARCHAR(32) NOT NULL)'))
        conn.execute(text(\"INSERT OR IGNORE INTO alembic_version VALUES ('006add_settings_table')\"))
        conn.commit()
    print('Stamped existing database')
"
python -m alembic upgrade head 2>/dev/null || python -m alembic stamp head
ok "Migrations done"

# ── Step 4: Create admin if not exists ────────────────────
step "4. Admin account"
python3 -c "
from app.database import SessionLocal, create_tables
from app.models import AdminUser
from app.services.auth import hash_password
create_tables()
db = SessionLocal()
existing = db.query(AdminUser).filter(AdminUser.username == 'admin').first()
if existing:
    # Reset password to ensure correct hash
    existing.password_hash = hash_password('Admin@123')
    db.commit()
    print('Admin password reset: Admin@123')
else:
    admin = AdminUser(
        full_name='Super Admin',
        username='admin',
        password_hash=hash_password('Admin@123'),
        role='admin',
        is_active=True
    )
    db.add(admin)
    db.commit()
    print('Admin created: admin / Admin@123')
db.close()
"
deactivate
ok "Admin ready"

# ── Step 5: Frontend build ─────────────────────────────────
step "5. Frontend build"
cd $APP_DIR/frontend
echo "VITE_API_URL=https://license.vrushaliinfotech.com" > .env
npm install --silent
npm run build
cd $APP_DIR
ok "Frontend built"

# ── Step 6: Node dependencies (proxy) ─────────────────────
step "6. Node dependencies"
npm install --silent
ok "Node dependencies installed"

# ── Step 7: PM2 services ──────────────────────────────────
step "7. PM2 services"

# Stop existing
pm2 stop all 2>/dev/null || true
pm2 delete all 2>/dev/null || true

# Start backend
pm2 start venv/bin/uvicorn \
  --name backend \
  --interpreter none \
  -- app.main:app --host 0.0.0.0 --port 8661 --workers 2

# Start frontend
pm2 start serve \
  --name frontend \
  --interpreter none \
  -- -s dist -l 3441 --no-clipboard \
  --cwd $APP_DIR/frontend

# Start proxy
pm2 start proxy-server.js --name proxy

sleep 3
ok "PM2 services started"

# ── Step 8: Save PM2 ──────────────────────────────────────
step "8. PM2 auto-start"
pm2 save
ok "PM2 saved"

# ── Step 9: Health check ──────────────────────────────────
step "9. Health check"
sleep 2

if curl -s http://localhost:8661/health | grep -q "ok"; then
    ok "Backend healthy"
else
    echo -e "${RED}⚠️  Backend not responding${NC}"
fi

if curl -sI http://localhost:3441 | grep -q "200\|304"; then
    ok "Frontend running"
else
    echo -e "${RED}⚠️  Frontend not responding${NC}"
fi

if curl -sI http://localhost:8080 | grep -q "200\|301\|302\|304"; then
    ok "Proxy running"
else
    echo -e "${RED}⚠️  Proxy not responding${NC}"
fi

# ── Final Status ───────────────────────────────────────────
echo ""
echo "================================================"
pm2 status
echo "================================================"
echo ""
echo "🌐 URLs:"
echo "   https://license.vrushaliinfotech.com/          → Frontend"
echo "   https://license.vrushaliinfotech.com/api/      → Backend API"
echo "   https://license.vrushaliinfotech.com/docs      → Swagger UI"
echo "   https://license.vrushaliinfotech.com/admin     → Admin Dashboard"
echo ""
echo "🔐 Admin Login:"
echo "   Username: admin"
echo "   Password: Admin@123"
echo ""
echo "📋 Nginx Proxy Manager:"
echo "   license.vrushaliinfotech.com → localhost:8080"
echo ""
echo "📝 Commands:"
echo "   pm2 status          → Status check"
echo "   pm2 logs            → Logs"
echo "   pm2 restart all     → Restart all"
echo "================================================"
