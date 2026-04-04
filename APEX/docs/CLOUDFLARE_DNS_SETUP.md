# Cloudflare DNS Setup for arif-fazil.com

## Required DNS Records

Add these A records to your Cloudflare DNS dashboard:

### Root Domain
| Type | Name | Content | Proxy Status | TTL |
|------|------|---------|--------------|-----|
| A | @ | <YOUR_SERVER_IP> | Proxied | Auto |
| A | www | <YOUR_SERVER_IP> | Proxied | Auto |

### Subdomains
| Type | Name | Content | Proxy Status | TTL |
|------|------|---------|--------------|-----|
| A | apex | <YOUR_SERVER_IP> | Proxied | Auto |
| A | arifos | <YOUR_SERVER_IP> | Proxied | Auto |
| A | mcp | <YOUR_SERVER_IP> | Proxied | Auto |

## SSL/TLS Settings

In Cloudflare Dashboard → SSL/TLS:

1. **Overview Tab**: Set to "Full (strict)"
2. **Edge Certificates**: Enable "Always Use HTTPS"
3. **Edge Certificates**: Enable "Automatic HTTPS Rewrites"

## Page Rules (Optional)

Create these page rules for better performance:

### Rule 1: Cache Static Assets
- URL: `*arif-fazil.com/static/*`
- Settings:
  - Cache Level: Cache Everything
  - Edge Cache TTL: 1 month

### Rule 2: MCP Endpoint Security
- URL: `mcp.arif-fazil.com/*`
- Settings:
  - Security Level: High
  - Browser Integrity Check: ON

## Getting Your Server IP

### If using Railway:
1. Go to Railway Dashboard → Your Project
2. Click on the service
3. Check "Public Networking" for the domain/IP
4. Note: Railway uses dynamic domains, use the provided railway.app domain in Caddyfile

### If using VPS (DigitalOcean, AWS, etc.):
1. Check your server dashboard for the public IP
2. Use that IP in the DNS A records above

## Verification

After setting up DNS, verify with:

```bash
# Check DNS propagation
nslookup arif-fazil.com
nslookup apex.arif-fazil.com
nslookup arifos.arif-fazil.com
nslookup mcp.arif-fazil.com

# Test HTTPS
curl -I https://arif-fazil.com
curl -I https://apex.arif-fazil.com
curl -I https://arifos.arif-fazil.com
curl -I https://mcp.arif-fazil.com/health
```

## Troubleshooting

### Error 522: Connection Timed Out
- Server is not running or firewall blocking port 443
- Check: `sudo systemctl status caddy`
- Check: `sudo ufw status` (should allow 80, 443)

### Error 526: Invalid SSL Certificate
- Cloudflare SSL mode is "Full (strict)" but server has no valid cert
- Fix: Set Cloudflare to "Full" (not strict) or ensure Caddy has valid certs

### DNS Not Propagating
- Wait 5-10 minutes for DNS propagation
- Check: `dig +short arif-fazil.com`
- Purge Cloudflare cache: Dashboard → Caching → Purge Everything
