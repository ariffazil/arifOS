# Railway Deployment Guide v60.0-FORGE

**Version:** v60.0-FORGE (RUKUN AGI)  
**Architecture:** 5-Organ Constitutional Kernel  
**Status:** PRODUCTION READY  

---

## Overview

This guide covers deploying arifOS MCP Server to Railway using the v60 architecture. The deployment uses Docker with the 5-organ constitutional kernel (Airlock, Mind, Heart, Soul, Memory).

---

## Quick Deploy

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Navigate to project
cd arifOS

# 4. Link or create project
railway link
# OR: railway init

# 5. Deploy
railway up

# 6. Get URL
railway domain
```

---

## Prerequisites

- Railway CLI installed
- Git repository pushed to GitHub
- Domain configured (optional but recommended)

---

## Deployment Configuration

### Automatic (Recommended)

Railway auto-detects the `railway.toml` configuration:

```toml
[build]
builder = "DOCKERFILE"
dockerfilePath = "Dockerfile"

[deploy]
startCommand = "python scripts/start_server.py"
healthcheckPath = "/health"
healthcheckTimeout = 30
restartPolicyType = "on_failure"
restartPolicyMaxRetries = 3

[variables]
PORT = "8080"
HOST = "0.0.0.0"
```

### Manual Configuration

1. **Create Project:**
   - Railway Dashboard → New Project
   - Deploy from GitHub repo

2. **Build Settings:**
   - Builder: Dockerfile
   - Dockerfile Path: `Dockerfile`

3. **Start Command:**
   ```bash
   python scripts/start_server.py
   ```

4. **Health Check:**
   - Path: `/health`
   - Timeout: 30 seconds

---

## Environment Variables

### Required

```bash
railway variables set PORT=8080
railway variables set HOST=0.0.0.0
railway variables set AAA_MCP_TRANSPORT=sse
railway variables set ARIFOS_CONSTITUTIONAL_MODE=AAA
railway variables set PYTHONUNBUFFERED=1
```

### Optional (Recommended for Production)

```bash
# External APIs
railway variables set BRAVE_API_KEY=your_brave_api_key
railway variables set BROWSERBASE_API_KEY=your_browserbase_key

# Database (for persistent VAULT999)
railway variables set DATABASE_URL=postgresql://...

# Redis (for session state)
railway variables set REDIS_URL=redis://...

# Security
railway variables set SECRET_KEY=your_random_secret
```

### Via Dashboard

1. Go to your project in Railway Dashboard
2. Variables tab → Add variables
3. Add each variable from above

---

## Verification

### 1. Check Health Endpoint

```bash
# Get deployment URL
railway domain
# Output: https://arifos-production.up.railway.app

# Test health
curl https://arifos-production.up.railway.app/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "version": "60.0-FORGE",
  "service": "arifOS MCP Server"
}
```

### 2. Check Metrics

```bash
curl https://arifos-production.up.railway.app/metrics
```

### 3. Check Stats

```bash
curl https://arifos-production.up.railway.app/stats
```

---

## Custom Domain

### Cloudflare Setup

1. **DNS Record:**
   ```
   Type: CNAME
   Name: mcp
   Target: your-app.up.railway.app
   Proxy Status: Proxied (orange cloud)
   ```

2. **SSL/TLS Settings:**
   - Mode: Full (strict)
   - Always Use HTTPS: On

3. **Railway Configuration:**
   - Railway Dashboard → Settings → Domains
   - Add Domain: `mcp.yourdomain.com`
   - Railway generates SSL certificate automatically

### Verification

```bash
# Test with custom domain
curl https://mcp.yourdomain.com/health
```

---

## Client Connection

### SSE Transport (Recommended for Cloud)

**Claude Desktop:**
```json
{
  "mcpServers": {
    "arifos-railway": {
      "transport": "sse",
      "url": "https://mcp.yourdomain.com/sse"
    }
  }
}
```

**Generic Client:**
```json
{
  "mcpServers": {
    "arifos": {
      "transport": "sse",
      "url": "https://your-app.up.railway.app/sse"
    }
  }
}
```

---

## Monitoring

### Railway Dashboard Metrics

Monitor in Railway Dashboard:
- CPU usage
- Memory usage
- Network requests
- Response times

### Custom Monitoring

```bash
# Check constitutional metrics
curl https://mcp.yourdomain.com/stats

# Expected output:
{
  "service": "arifOS MCP",
  "stats": {
    "total_executions": 42,
    "avg_latency_ms": 0.48,
    "seal_rate": 0.95,
    "void_rate": 0.05
  }
}
```

### Health Check Alerts

Configure Railway to alert on health check failures:
1. Dashboard → Settings → Health Check
2. Path: `/health`
3. Enable notifications

---

## Scaling

### Horizontal Scaling

Railway automatically scales based on traffic. To configure:

```bash
# Set minimum instances
railway scale --min 1

# Set maximum instances
railway scale --max 3
```

### Vertical Scaling

Upgrade instance size in Railway Dashboard:
- Settings → Instance
- Choose: `standard`, `performance`, etc.

---

## Troubleshooting

### Issue: Build Fails

**Check:**
```bash
# Local Docker build test
docker build -t test-build .

# Check for missing files
ls -la Dockerfile railway.toml
```

### Issue: Health Check Failing

**Debug:**
```bash
# Check logs
railway logs

# Verify start command
railway variables get START_COMMAND

# Test locally
python scripts/start_server.py
```

### Issue: "Connection refused"

**Fix:**
```bash
# Verify PORT variable
railway variables get PORT
# Should be: 8080 (not 8000 or other)

# Check transport mode
railway variables get AAA_MCP_TRANSPORT
# Should be: sse
```

### Issue: "Module not found"

**Fix:**
```bash
# Rebuild with clean cache
railway up --clean
```

---

## Production Checklist

- [ ] Environment variables set
- [ ] Health check passing
- [ ] Custom domain configured (optional)
- [ ] SSL/TLS working
- [ ] Monitoring enabled
- [ ] Client configuration tested
- [ ] Rate limiting configured
- [ ] Backup strategy (if using PostgreSQL)

---

## Costs

Railway pricing (as of Feb 2026):
- **Starter:** $0/month (up to $5 credits)
- **Pro:** $10/month + usage
- Usage: ~$0.0001 per request

Typical arifOS deployment: $5-20/month depending on usage.

---

## Support

- **Railway Docs:** https://docs.railway.app
- **arifOS Docs:** https://arifos.arif-fazil.com
- **GitHub Issues:** https://github.com/ariffazil/arifOS/issues

---

*For full deployment options, see `MCP_DEPLOYMENT_GUIDE_V60.md`*

**DITEMPA BUKAN DIBERI** 💎🔥🧠
