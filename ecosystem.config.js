/**
 * PM2 Ecosystem Configuration
 * SalaryPay License Server - Production
 *
 * Usage:
 *   pm2 start ecosystem.config.js
 *   pm2 restart all
 *   pm2 status
 */

module.exports = {
  apps: [
    // ── Backend (FastAPI + Uvicorn) ──────────────────────
    {
      name: 'salarypay-backend',
      script: '/opt/license-manager/venv/bin/uvicorn',
      args: 'app.main:app --host 0.0.0.0 --port 8661 --workers 2',
      cwd: '/opt/license-manager',
      interpreter: 'none',
      env: {
        PATH: '/opt/license-manager/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin',
        PYTHONPATH: '/opt/license-manager'
      },
      watch: false,
      autorestart: true,
      max_restarts: 10,
      restart_delay: 5000,
      min_uptime: '10s',
      log_date_format: 'YYYY-MM-DD HH:mm:ss',
      error_file: '/var/log/salarypay/backend-error.log',
      out_file: '/var/log/salarypay/backend-out.log',
      merge_logs: true,
      time: true
    },

    // ── Frontend (Static Serve) ──────────────────────────
    {
      name: 'salarypay-frontend',
      script: 'serve',
      args: '-s dist -l 3441 --no-clipboard',
      cwd: '/opt/license-manager/frontend',
      interpreter: 'none',
      watch: false,
      autorestart: true,
      max_restarts: 10,
      restart_delay: 5000,
      min_uptime: '10s',
      log_date_format: 'YYYY-MM-DD HH:mm:ss',
      error_file: '/var/log/salarypay/frontend-error.log',
      out_file: '/var/log/salarypay/frontend-out.log',
      merge_logs: true,
      time: true
    },

    // ── Proxy Server (Single Domain) ─────────────────────
    {
      name: 'salarypay-proxy',
      script: 'proxy-server.js',
      cwd: '/opt/license-manager',
      watch: false,
      autorestart: true,
      max_restarts: 10,
      restart_delay: 3000,
      time: true
    }
  ]
}
