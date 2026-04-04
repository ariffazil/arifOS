# Cloudflare Pages Custom Domain Setup

**For**: arifOS Constitutional Dashboard  
**Current URL**: https://674a01a3.arifosmcp-truth-claim.pages.dev  
**Target**: `dashboard.arifos.arif-fazil.com` (example)

---

## Quick Setup (5 Minutes)

### Step 1: Choose Your Custom Domain

Pick a subdomain for your dashboard:
- `dashboard.arifos.arif-fazil.com`
- `truth.arifos.arif-fazil.com`
- `gov.arifos.arif-fazil.com`
- Or any other subdomain you prefer

---

### Step 2: Add Custom Domain in Cloudflare Pages

1. Go to [Cloudflare Pages Dashboard](https://dash.cloudflare.com/)
2. Select your project: **arifosmcp-truth-claim**
3. Click **Custom domains** tab
4. Click **Set up a custom domain**
5. Enter your chosen domain (e.g., `dashboard.arifos.arif-fazil.com`)
6. Click **Continue**

Cloudflare will automatically:
- Create the DNS record
- Provision SSL certificate (Let's Encrypt)
- Enable HTTPS redirect

---

### Step 3: Verify DNS Propagation

```bash
# Check if DNS is live (may take 1-5 minutes)
dig dashboard.arifos.arif-fazil.com

# Expected output:
# dashboard.arifos.arif-fazil.com. 300 IN CNAME arifosmcp-truth-claim.pages.dev.
```

---

### Step 4: Test Custom Domain

Visit your custom domain in a browser:
```
https://dashboard.arifos.arif-fazil.com
```

You should see your constitutional dashboard!

---

## Advanced: Manual DNS Configuration

If Cloudflare doesn't auto-configure DNS (rare):

### For Cloudflare-Managed Domains:

1. Go to **DNS** tab in Cloudflare dashboard
2. Add a **CNAME** record:
   - **Name**: `dashboard` (or your chosen subdomain)
   - **Target**: `arifosmcp-truth-claim.pages.dev`
   - **Proxy status**: ✅ Proxied (orange cloud)
   - **TTL**: Auto

### For External DNS Providers (GoDaddy, Namecheap, etc.):

1. Log into your DNS provider
2. Add a **CNAME** record:
   - **Host**: `dashboard`
   - **Points to**: `arifosmcp-truth-claim.pages.dev`
   - **TTL**: 3600 (or default)

3. **Important**: External domains require manual SSL setup in Cloudflare Pages

---

## SSL Certificate (Automatic)

Cloudflare Pages automatically provisions SSL certificates via Let's Encrypt.

**Timeline**:
- DNS configured → Certificate issued in 1-5 minutes
- HTTPS redirect enabled automatically

**Verify SSL**:
```bash
curl -I https://dashboard.arifos.arif-fazil.com
# Should return: HTTP/2 200
```

---

## Performance Optimization

### Enable Cloudflare Optimizations:

1. **Auto Minify** (Dashboard → Speed → Optimization)
   - ✅ JavaScript
   - ✅ CSS
   - ✅ HTML

2. **Brotli Compression** (Enabled by default)

3. **HTTP/3 (QUIC)** (Enabled by default)

4. **Caching**:
   - Static assets: 1 year cache
   - HTML: No cache (always fresh)

---

## Troubleshooting

### Issue: 404 Error on Custom Domain

**Solution**:
1. Verify DNS CNAME points to `arifosmcp-truth-claim.pages.dev`
2. Check Cloudflare Pages → Custom domains → Status should be "Active"
3. Wait 5 minutes for CDN propagation

### Issue: SSL Certificate Pending

**Solution**:
- Wait 5-10 minutes for Let's Encrypt validation
- Ensure DNS is fully propagated
- Check Cloudflare dashboard for certificate status

### Issue: Old Content Cached

**Solution**:
```bash
# Purge Cloudflare cache
curl -X POST "https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/purge_cache" \
  -H "Authorization: Bearer {API_TOKEN}" \
  -H "Content-Type: application/json" \
  --data '{"purge_everything":true}'
```

Or use Cloudflare Dashboard → Caching → Purge Everything

---

## Multiple Domains (Optional)

You can add multiple custom domains for the same dashboard:

```
dashboard.arifos.arif-fazil.com (primary)
truth.arifos.arif-fazil.com (alias)
gov.arifos.arif-fazil.com (alias)
```

All will serve the same content.

---

## Monitoring

### Check Dashboard Uptime:

1. **Cloudflare Analytics** (free):
   - Cloudflare Dashboard → Analytics
   - View: Requests, Bandwidth, Threats blocked

2. **External Monitoring** (optional):
   - UptimeRobot: https://uptimerobot.com/
   - StatusCake: https://www.statuscake.com/
   - Set alert for: `https://dashboard.arifos.arif-fazil.com`

---

## Security Hardening

### 1. Enable Cloudflare WAF (Web Application Firewall)

Cloudflare Dashboard → Security → WAF
- Enable managed rules
- Block common attacks (SQL injection, XSS)

### 2. Enable Bot Protection

Cloudflare Dashboard → Security → Bots
- Enable bot fight mode (free plan)
- Or enable Super Bot Fight Mode (paid plans)

### 3. Enable Rate Limiting (Paid)

Cloudflare Dashboard → Security → Rate Limiting
- Limit: 100 requests per 10 minutes per IP

---

## Cost

**Cloudflare Pages**: FREE (unlimited bandwidth)  
**Custom Domain**: FREE (if domain already on Cloudflare)  
**SSL Certificate**: FREE (auto-provisioned)

---

## Summary Checklist

- [ ] Choose custom subdomain
- [ ] Add custom domain in Cloudflare Pages dashboard
- [ ] Wait 1-5 minutes for DNS propagation
- [ ] Test `https://your-domain.com` in browser
- [ ] (Optional) Enable Cloudflare optimizations
- [ ] (Optional) Set up uptime monitoring
- [ ] Update README.md with new URL

---

**Ditempa Bukan Diberi** 🔥  
*Forged, Not Given*

Your constitutional dashboard is now on a professional custom domain!
