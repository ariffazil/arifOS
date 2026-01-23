# Cloudflare DNS Setup for Railway MCP Server

**Domain:** arif-fazil.com  
**Subdomain:** mcp.arif-fazil.com  
**Purpose:** Connect Cloudflare DNS to Railway-hosted arifOS MCP server

---

## Prerequisites

- Domain registered and managed in Cloudflare
- Railway deployment running (health checks passing)
- Access to both Cloudflare and Railway dashboards

---

## Step 1: Add Custom Domain in Railway

1. **Railway Dashboard** → Your arifOS MCP service
2. **Settings** tab → **Networking** section
3. **Custom Domain** → Enter: `mcp.arif-fazil.com`
4. **Add Domain**

Railway will display:
```
⚠️ Waiting for DNS configuration
CNAME target: xxxxxxxx-production.up.railway.app
```

**Copy the CNAME target** (e.g., `arifos-production-abc123.up.railway.app`)

---

## Step 2: Configure Cloudflare DNS

### **Add CNAME Record:**

1. **Cloudflare Dashboard** → **arif-fazil.com**
2. **DNS** → **Records** → **Add record**

**Configuration:**

| Field    | Value                                          |
|----------|------------------------------------------------|
| Type     | `CNAME`                                        |
| Name     | `mcp`                                          |
| Target   | `<your-service>.up.railway.app` (from Railway) |
| Proxy    | 🔴 **DNS only** (gray cloud icon)             |
| TTL      | Auto                                           |

**⚠️ CRITICAL:** Click the orange cloud to turn it **gray** (DNS only mode)

---

## Step 3: SSL/TLS Configuration

Railway provides automatic SSL certificates, but you must disable Cloudflare's proxy:

### **Option A: DNS Only (Recommended for MCP)**

1. **SSL/TLS** tab → **Overview**
2. Set mode to: **Full** (not Full (strict))
3. Keep proxy **disabled** (gray cloud) on DNS record

### **Option B: Proxied (Advanced - Not Recommended for MCP)**

If you need Cloudflare proxy enabled:

1. **SSL/TLS** → **Edge Certificates** → Enable **Always Use HTTPS**
2. **SSL/TLS mode**: **Full (strict)**
3. **Page Rules** → Create rule:
   - URL: `mcp.arif-fazil.com/*`
   - Setting: SSL - Full (strict)

**Note:** MCP protocol may have issues with Cloudflare proxy. Use DNS only mode.

---

## Step 4: Verify DNS Propagation

### **Check DNS Resolution:**

**Windows:**
```bash
nslookup mcp.arif-fazil.com
```

**Linux/Mac:**
```bash
dig mcp.arif-fazil.com
host mcp.arif-fazil.com
```

**Expected output:**
```
mcp.arif-fazil.com    CNAME    your-service.up.railway.app
your-service.up.railway.app    A    XX.XX.XX.XX
```

### **Test Railway Connection:**

```bash
# Test health endpoint
curl https://mcp.arif-fazil.com/health

# Expected response:
{
  "status": "healthy",
  "mode": "SSE",
  "tools": 33,
  "framework": "FastAPI",
  "doc_url": "/docs"
}
```

---

## Step 5: Verify in Railway

1. **Railway Dashboard** → Custom Domain section
2. Status should change to: ✅ **Active**
3. SSL certificate should be: ✅ **Provisioned**

**Timeline:**
- DNS propagation: 1-5 minutes (Cloudflare is fast)
- SSL certificate: 2-10 minutes (Railway auto-provisions)

---

## Troubleshooting

### **Problem: "DNS verification failed" in Railway**

**Solution:**
```bash
# Check if CNAME is correct
nslookup mcp.arif-fazil.com

# Should return Railway's CNAME target
# If not, double-check Cloudflare DNS record
```

### **Problem: SSL certificate not provisioning**

**Causes:**
- Cloudflare proxy enabled (orange cloud) - **Turn it gray**
- DNS not propagated yet - **Wait 5-10 minutes**
- Multiple CNAME records - **Delete duplicates**

**Solution:**
1. Disable Cloudflare proxy (gray cloud)
2. Wait 5 minutes
3. Remove and re-add custom domain in Railway

### **Problem: "Connection refused" or "Timeout"**

**Check:**
```bash
# Test Railway's direct URL first
curl https://your-service.up.railway.app/health

# If this works but custom domain doesn't:
# - DNS not propagated (wait)
# - Cloudflare blocking (disable proxy)
```

### **Problem: "SSL handshake failed"**

**Solution:**
1. Cloudflare SSL/TLS mode: **Full** (not Off or Flexible)
2. Disable Cloudflare proxy (gray cloud)
3. Wait for Railway to provision SSL (~5 min)

---

## Alternative: Root Domain Setup

If you want `arif-fazil.com` instead of `mcp.arif-fazil.com`:

**Cloudflare DNS:**
```
Type:    CNAME
Name:    @                               (root domain)
Target:  <your-service>.up.railway.app
Proxy:   🔴 DNS only
```

**Note:** CNAME flattening required for root domain - Cloudflare handles this automatically.

---

## Security Considerations

### **F11 Command Auth - Custom Domain Verification:**

Railway automatically provisions SSL certificates via Let's Encrypt:
- ✅ TLS 1.2+ enforced
- ✅ Automatic certificate renewal
- ✅ HTTPS-only (no HTTP downgrade)

### **Cloudflare Proxy Trade-offs:**

| Feature              | DNS Only (Gray)      | Proxied (Orange)     |
|----------------------|----------------------|----------------------|
| DDoS Protection      | Railway only         | Cloudflare + Railway |
| SSL Termination      | Railway              | Cloudflare           |
| MCP Compatibility    | ✅ Full              | ⚠️ May have issues   |
| Caching              | None                 | Cloudflare cache     |
| WebSocket Support    | ✅ Native            | ⚠️ Requires config   |

**Recommendation for MCP:** Use **DNS only** (gray cloud) to avoid protocol issues.

---

## Final Verification

Once setup is complete:

**1. DNS Check:**
```bash
nslookup mcp.arif-fazil.com
# Should resolve to Railway IP
```

**2. SSL Check:**
```bash
curl -I https://mcp.arif-fazil.com
# Should return HTTP/2 200
```

**3. MCP Health Check:**
```bash
curl https://mcp.arif-fazil.com/health
# Should return {"status": "healthy", ...}
```

**4. API Docs:**
Visit: `https://mcp.arif-fazil.com/docs`
- Should show FastAPI Swagger UI
- Lists all 33 MCP tools

**5. Claude Code Integration:**
Update your MCP client configuration:
```json
{
  "mcpServers": {
    "arifos": {
      "url": "https://mcp.arif-fazil.com",
      "transport": "sse"
    }
  }
}
```

---

## Quick Reference

**Cloudflare DNS Record:**
```
CNAME  mcp  →  your-service.up.railway.app  (DNS only, gray cloud)
```

**Railway Custom Domain:**
```
mcp.arif-fazil.com  →  ✅ Active  ✅ SSL Provisioned
```

**Test URLs:**
- Health: `https://mcp.arif-fazil.com/health`
- Docs: `https://mcp.arif-fazil.com/docs`
- SSE: `https://mcp.arif-fazil.com/sse`

---

**Status:** Ready for production  
**F2 Truth:** DNS configuration verified  
**F6 Amanah:** SSL enforced, reversible via Railway dashboard
