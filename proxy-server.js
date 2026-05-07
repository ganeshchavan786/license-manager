/**
 * proxy-server.js
 * License Server - Single Domain Proxy
 *
 * Routing:
 *   /api/*    → http://localhost:8661  (FastAPI backend)
 *   /docs     → http://localhost:8661  (Swagger UI)
 *   /redoc    → http://localhost:8661  (ReDoc)
 *   /openapi* → http://localhost:8661  (OpenAPI schema)
 *   /health   → http://localhost:8661  (Health check)
 *   /*        → http://localhost:3441  (React Frontend)
 */

const http = require('http')
const httpProxy = require('http-proxy')
const fs = require('fs')
const path = require('path')

const PORT = 8080

const TARGETS = {
  api:      'http://localhost:8661',
  frontend: 'http://localhost:3441',
}

const proxy = httpProxy.createProxyServer({ ws: true, changeOrigin: true })

proxy.on('error', (err, req, res) => {
  console.error(`[proxy] Error: ${req.method} ${req.url} — ${err.message}`)
  if (res && !res.headersSent) {
    res.writeHead(502, { 'Content-Type': 'application/json' })
    res.end(JSON.stringify({ error: 'upstream unavailable' }))
  }
})

// No-cache for API responses
proxy.on('proxyRes', (proxyRes, req) => {
  if (req.url && (req.url.startsWith('/api/') || req.url === '/api')) {
    proxyRes.headers['cache-control'] = 'no-store, no-cache, must-revalidate'
    proxyRes.headers['pragma'] = 'no-cache'
    proxyRes.headers['expires'] = '0'
  }
})

const server = http.createServer((req, res) => {
  const reqUrl = req.url || '/'

  // API / docs / health → Backend
  if (
    reqUrl.startsWith('/api/') || reqUrl === '/api' ||
    reqUrl === '/docs' || reqUrl.startsWith('/docs/') ||
    reqUrl === '/redoc' || reqUrl.startsWith('/redoc/') ||
    reqUrl.startsWith('/openapi') || reqUrl === '/health'
  ) {
    req.headers['x-forwarded-for'] = req.socket.remoteAddress || 'unknown'
    req.headers['host'] = 'localhost:8661'
    proxy.web(req, res, { target: TARGETS.api })
    return
  }

  // Everything else → Frontend
  req.headers['x-forwarded-for'] = req.socket.remoteAddress || 'unknown'
  req.headers['host'] = 'localhost:3441'
  proxy.web(req, res, { target: TARGETS.frontend })
})

// WebSocket support (for Vite HMR in dev)
server.on('upgrade', (req, socket, head) => {
  const reqUrl = req.url || '/'
  if (
    reqUrl.startsWith('/api/') ||
    reqUrl === '/docs' ||
    reqUrl === '/health'
  ) {
    proxy.ws(req, socket, head, { target: TARGETS.api }, (err) => {
      if (err) { console.error('[proxy] WS error (api):', err.message); socket.destroy() }
    })
    return
  }
  proxy.ws(req, socket, head, { target: TARGETS.frontend }, (err) => {
    if (err) { console.error('[proxy] WS error (frontend):', err.message); socket.destroy() }
  })
})

server.on('error', (err) => {
  if (err.code === 'EADDRINUSE') {
    console.error(`[proxy] Port ${PORT} already in use.`)
    process.exit(1)
  }
  throw err
})

server.listen(PORT, () => {
  console.log(`\n✅ License Server Proxy running on http://localhost:${PORT}`)
  console.log(`   /api/*  → ${TARGETS.api}  (FastAPI Backend)`)
  console.log(`   /docs   → ${TARGETS.api}  (Swagger UI)`)
  console.log(`   /*      → ${TARGETS.frontend}  (React Frontend)`)
  console.log(`\n   Domain: https://license.vrushaliinfotech.com`)
})

module.exports = { TARGETS }
