#!/bin/bash
# SalaryPay License Server - Update Script
# Run on server to update to latest code:
# bash scripts/update_server.sh

set -e

APP_DIR="/home/salarypay/app"
SERVICE_NAME="salarypay"

echo "================================================"
echo "SalaryPay License Server - Update"
echo "================================================"

# Backup database first
echo "Creating database backup..."
cd $APP_DIR
sudo -u salarypay bash -c "cd $APP_DIR && source venv/bin/activate && python scripts/backup_database.py"

# Pull latest code (if using git)
if [ -d "$APP_DIR/.git" ]; then
    echo "Pulling latest code..."
    sudo -u salarypay git -C $APP_DIR pull origin main
fi

# Update Python dependencies
echo "Updating Python dependencies..."
sudo -u salarypay bash -c "cd $APP_DIR && source venv/bin/activate && pip install -r requirements.txt -q"

# Run migrations
echo "Running database migrations..."
sudo -u salarypay bash -c "cd $APP_DIR && source venv/bin/activate && python -m alembic upgrade head"

# Rebuild frontend
echo "Rebuilding frontend..."
sudo -u salarypay bash -c "cd $APP_DIR/frontend && npm install --silent && npm run build"

# Restart service
echo "Restarting service..."
systemctl restart $SERVICE_NAME
sleep 3

if systemctl is-active --quiet $SERVICE_NAME; then
    echo "✅ Update complete! Service is running."
else
    echo "❌ Service failed to start!"
    journalctl -u $SERVICE_NAME -n 20
    exit 1
fi

echo ""
echo "Health check..."
curl -s http://localhost:8661/health && echo ""
echo "✅ Server is healthy!"
