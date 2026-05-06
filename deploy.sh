#!/bin/bash
# SalaryPay - Auto Deploy Script
# GitHub Webhook trigger करतो हे script

set -e

APP_DIR="/var/www/salarypay"
LOG_FILE="/var/log/salarypay/deploy.log"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a $LOG_FILE; }

log "🚀 Deploy started..."

cd $APP_DIR

# ── 1. Latest code pull ────────────────────────────────────
log "📥 Pulling latest code from GitHub..."
git pull origin main

# ── 2. Backend dependencies ────────────────────────────────
log "📦 Installing backend dependencies..."
source venv/bin/activate
pip install -r requirements.txt -q

# ── 3. Database migrations ─────────────────────────────────
log "🗄️  Running database migrations..."
python -m alembic upgrade head
deactivate

# ── 4. Frontend build ──────────────────────────────────────
log "🔨 Building frontend..."
cd $APP_DIR/frontend
npm install --silent
npm run build
cd $APP_DIR

# ── 5. PM2 restart ─────────────────────────────────────────
log "🔁 Restarting services..."
pm2 restart salarypay-backend
pm2 restart salarypay-frontend

log "✅ Deploy completed successfully!"
pm2 status
