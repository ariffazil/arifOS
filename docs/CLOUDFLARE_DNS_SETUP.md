# CloudFlare DNS Setup for arifOS MCP
# arif-fazil.com Configuration Guide

**Domain:** arif-fazil.com
**Target:** Railway deployment (arifos-production.up.railway.app)
**Last Updated:** 2026-01-17

---

## Overview

This guide configures your CloudFlare-managed domain `arif-fazil.com` to point to your Railway-hosted arifOS MCP server.

```
Client Request
     ↓
arif-fazil.com (CloudFlare DNS)
     ↓
SSL/TLS Termination (CloudFlare)
     ↓
Proxy to Railway (arifos-production.up.railway.app)
     ↓
arifOS MCP Server (FastAPI/SSE)
```

---

## Step 1: Get Railway Domain Information

### 1.1 Railway Generates Domain

When you deploy to Railway, they automatically provide a domain:

**Format:** `<project-name>.up.railway.app`
**Your App:** `arifos-production.up.railway.app`

### 1.2 Get Railway CNAME Target

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click on your project `arifos-production`
3. Click "Settings" → "Domains"
4. Look for the automatically generated domain
5. Copy the CNAME value (usually: `<random-id>.up.railway.app`)

**Example:**
```
Generated Domain: arifos-production.up.railway.app
CNAME Target: abcd1234.up.railway.app
```

---

## Step 2: Configure CloudFlare DNS

### 2.1 Login to CloudFlare

1. Go to [CloudFlare Dashboard](https://dash.cloudflare.com/)
2. Login with your account
3. Select domain: **arif-fazil.com**

### 2.2 Add DNS Record

#### Option A: Root Domain (arif-fazil.com)

If you want to use the root domain directly:

```
Type:   CNAME
Name:   @ (or arif-fazil.com)
Target: arifos-production.up.railway.app
Proxy:  ✅ Proxied (Orange Cloud)
TTL:    Auto
```

**⚠️ Note:** CNAME on root domain requires CloudFlare's CNAME flattening (automatically enabled).

#### Option B: Subdomain (Recommended)

Use a subdomain like `mcp.arif-fazil.com` or `arifos.arif-fazil.com`:

```
Type:   CNAME
Name:   mcp (or arifos)
Target: arifos-production.up.railway.app
Proxy:  ✅ Proxied (Orange Cloud)
TTL:    Auto
```

**Result:** Your MCP server will be accessible at:
- `https://mcp.arif-fazil.com` OR
- `https://arifos.arif-fazil.com`

### 2.3 Alternative: A Record (Not Recommended)

If CNAME doesn't work, use A record with Railway's IP:

1. Get Railway IP:
   ```bash
   nslookup arifos-production.up.railway.app
   ```

2. Add A record:
   ```
   Type:   A
   Name:   mcp (or @)
   IPv4:   <railway-ip-address>
   Proxy:  ✅ Proxied
   TTL:    Auto
   ```

**⚠️ Warning:** Railway IPs can change. CNAME is preferred.

---

## Step 3: SSL/TLS Configuration

### 3.1 Enable SSL/TLS

1. In CloudFlare dashboard, go to **SSL/TLS** tab
2. Select SSL/TLS encryption mode:

```
Recommended: Full (strict)
```

**Available Modes:**
- ❌ **Off** - No encryption (NOT RECOMMENDED)
- ⚠️ **Flexible** - CloudFlare to client encrypted, CloudFlare to Railway unencrypted
- ✅ **Full** - End-to-end encryption, self-signed cert OK
- ✅ **Full (strict)** - End-to-end encryption, valid cert required (BEST)

### 3.2 Enable Always Use HTTPS

1. Go to **SSL/TLS** → **Edge Certificates**
2. Enable **Always Use HTTPS**
3. Enable **Automatic HTTPS Rewrites**

### 3.3 Enable HSTS (Optional but Recommended)

1. Go to **SSL/TLS** → **Edge Certificates**
2. Scroll to **HTTP Strict Transport Security (HSTS)**
3. Click **Enable HSTS**
4. Configure:
   ```
   Max Age: 6 months (15768000 seconds)
   Include subdomains: ✅ Enabled
   Preload: ✅ Enabled (optional)
   No-Sniff header: ✅ Enabled
   ```

---

## Step 4: Performance Optimization

### 4.1 Enable Caching (Optional)

For static content (if serving any):

1. Go to **Caching** → **Configuration**
2. Set caching level: **Standard**
3. Add page rules for API endpoints:

```
URL Pattern: *arif-fazil.com/sse*
Cache Level: Bypass

URL Pattern: *arif-fazil.com/messages*
Cache Level: Bypass

URL Pattern: *arif-fazil.com/health*
Cache Level: Standard (5 minutes)
```

### 4.2 Enable Auto Minify

1. Go to **Speed** → **Optimization**
2. Enable Auto Minify for:
   - ✅ JavaScript
   - ✅ CSS
   - ✅ HTML

---

## Step 5: Security Configuration

### 5.1 Configure Firewall Rules

1. Go to **Security** → **WAF** → **Firewall rules**
2. Create rule to allow legitimate traffic:

```
Rule Name: Allow MCP Clients
Expression: (http.host eq "mcp.arif-fazil.com" and http.request.uri.path contains "/sse")
Action: Allow
```

### 5.2 Enable Bot Protection

1. Go to **Security** → **Bots**
2. Enable **Bot Fight Mode** (Free plan)
3. Or configure **Super Bot Fight Mode** (Paid plans)

### 5.3 Configure Rate Limiting (Paid Feature)

If on Pro/Business plan:

```
Rule: Limit MCP Requests
If: (http.host eq "mcp.arif-fazil.com")
Then: Rate limit at 100 requests per minute per IP
Action: Block for 10 minutes
```

---

## Step 6: Verification

### 6.1 Check DNS Propagation

```bash
# Windows
nslookup mcp.arif-fazil.com

# Linux/Mac
dig mcp.arif-fazil.com

# Online tool
# https://dnschecker.org/
```

**Expected Result:**
```
Non-authoritative answer:
Name:    mcp.arif-fazil.com
Address: <CloudFlare IP or Railway IP>
```

**⏱️ Propagation Time:** 5-10 minutes (CloudFlare is fast!)

### 6.2 Test HTTPS Connection

```bash
# Test health endpoint
curl https://mcp.arif-fazil.com/health

# Expected response:
# {
#   "status": "healthy",
#   "mode": "SSE",
#   "tools": 17,
#   "framework": "FastAPI"
# }
```

### 6.3 Test SSL Certificate

```bash
# Check certificate
openssl s_client -connect mcp.arif-fazil.com:443 -showcerts

# Should show CloudFlare certificate (valid)
```

### 6.4 Browser Test

Open in browser:
- **Health:** `https://mcp.arif-fazil.com/health`
- **API Docs:** `https://mcp.arif-fazil.com/docs`
- **ReDoc:** `https://mcp.arif-fazil.com/redoc`

---

## Step 7: Update Railway Custom Domain

### 7.1 Add Custom Domain to Railway

1. Go to Railway dashboard
2. Click your project → **Settings** → **Domains**
3. Click **+ Add Domain**
4. Enter: `mcp.arif-fazil.com`
5. Railway will verify DNS and enable custom domain

### 7.2 Verify Custom Domain

Railway will show:
```
✅ mcp.arif-fazil.com - Active
```

---

## Step 8: Update Claude Code Configuration

Now update your Claude Code MCP config to use the custom domain:

**File:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "arifos-cloud": {
      "url": "https://mcp.arif-fazil.com/sse",
      "transport": "sse",
      "description": "arifOS Constitutional Governance - Cloud (Custom Domain)"
    }
  }
}
```

---

## Troubleshooting

### Issue: "DNS_PROBE_FINISHED_NXDOMAIN"

**Cause:** DNS not propagated yet
**Solution:** Wait 5-10 minutes, clear DNS cache:

```bash
# Windows
ipconfig /flushdns

# Mac
sudo dscacheutil -flushcache

# Linux
sudo systemd-resolve --flush-caches
```

### Issue: "ERR_SSL_VERSION_OR_CIPHER_MISMATCH"

**Cause:** SSL/TLS configuration mismatch
**Solution:**
1. CloudFlare: Set SSL/TLS to "Full (strict)"
2. Verify Railway has valid SSL (automatic)
3. Wait 5 minutes for SSL provisioning

### Issue: "502 Bad Gateway"

**Cause:** Railway app not running or CloudFlare can't reach it
**Solution:**
1. Check Railway logs: `railway logs`
2. Verify app is running: `https://arifos-production.up.railway.app/health`
3. Check CloudFlare proxy status (should be orange cloud)

### Issue: "Proxy status showing gray cloud"

**Cause:** DNS-only mode (not proxied through CloudFlare)
**Solution:**
1. Click the gray cloud icon to enable proxy (turn orange)
2. This enables CloudFlare CDN, SSL, and security features

---

## DNS Configuration Summary

Here's your complete DNS configuration:

```
# CloudFlare DNS Records for arif-fazil.com

Type    Name     Target                              Proxy   Status
─────────────────────────────────────────────────────────────────────
CNAME   mcp      arifos-production.up.railway.app    ✅      Active
CNAME   www      arif-fazil.com                      ✅      Active
A       @        <your-main-site-ip>                 ✅      Active
```

---

## Security Checklist

Before going live:

- [ ] SSL/TLS mode: Full (strict) ✅
- [ ] Always Use HTTPS: Enabled ✅
- [ ] HSTS: Enabled (optional) ⚠️
- [ ] Firewall rules: Configured ⚠️
- [ ] Rate limiting: Configured (if paid plan) ⚠️
- [ ] Bot protection: Enabled ✅
- [ ] **Authentication: ADD BEFORE PRODUCTION** ❌ CRITICAL

**⚠️ WARNING:** Your MCP server is currently public without authentication. Add token-based auth before production deployment!

---

## Monitoring & Maintenance

### CloudFlare Analytics

1. Go to **Analytics & Logs** → **Traffic**
2. Monitor:
   - Requests per minute
   - Bandwidth usage
   - Top paths (/sse, /health, etc.)
   - Status codes (200, 404, 500, etc.)

### Railway Metrics

1. Railway dashboard → **Metrics**
2. Monitor:
   - CPU usage
   - Memory usage
   - Network bandwidth
   - Response times

### Health Check Automation

Create a monitoring service:

```bash
# Using cron (Linux/Mac)
# Add to crontab -e:
*/5 * * * * curl -f https://mcp.arif-fazil.com/health || echo "arifOS MCP down!" | mail -s "Alert" your@email.com

# Or use external monitoring:
# - UptimeRobot (free)
# - Pingdom
# - StatusCake
```

---

`★ Insight ─────────────────────────────────────`

**The CloudFlare Advantage**: By proxying through CloudFlare, you get:

1. **Automatic SSL/TLS** - Free certificates, auto-renewal
2. **DDoS Protection** - CloudFlare absorbs attacks before they reach Railway
3. **Global CDN** - Edge caching reduces latency worldwide
4. **DNS Management** - Fast propagation (<5 min vs hours for others)
5. **Analytics** - Free traffic insights without adding code

This is **infrastructure as governance** - security and performance enforced at the network edge, not just in your application.

`─────────────────────────────────────────────────`

---

**DITEMPA BUKAN DIBERI** - DNS configured through systematic setup, not given through magic.

**Version:** v47.0.0 | **Status:** SEALED
**Authority:** Network Infrastructure Layer
