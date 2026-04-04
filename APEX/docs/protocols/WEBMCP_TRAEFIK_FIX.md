# WebMCP Traefik Routing Fix

> **Status**: Fix Ready for Deployment  
> **Issue**: WebMCP container running internally but public endpoint returns 404  
> **Root Cause**: Traefik labels using separate hostname instead of path-based routing on main domain  
> **Fix**: PathPrefix-based routing with stripprefix middleware

---

## Problem Summary

```
Internal:  http://10.0.10.15:8081/webmcp  ✅ Working
Public:    https://arifosmcp.arif-fazil.com/webmcp  ❌ 404
```

**Traefik logs show no route detection** for `/webmcp` path because the original configuration used separate hostnames:
- Main MCP: `arifosmcp.arif-fazil.com`
- WebMCP: `aclip.arif-fazil.com` (separate subdomain)

This doesn't match the desired architecture of **both protocols on the same domain**.

---

## Solution: Path-Based Routing

Change Traefik labels to use `PathPrefix` rules on the main domain:

| Endpoint | Router | Service | Port | Middleware |
|----------|--------|---------|------|------------|
| `/mcp` | `arifosmcp` | arifosmcp | 8080 | None |
| `/webmcp` | `webmcp` | webmcp | 8081 | `webmcp-strip` (strips `/webmcp` prefix) |

---

## Changes Required in `docker-compose.yml`

### 1. Main MCP Service (arifosmcp)

**File**: `docker-compose.yml`  
**Lines**: 352-356

```yaml
labels:
  - "traefik.enable=true"
  # A2A MCP router - main domain + /mcp path
  - "traefik.http.routers.arifosmcp.rule=Host(`arifosmcp.arif-fazil.com`) && PathPrefix(`/mcp`)"
  - "traefik.http.routers.arifosmcp.entrypoints=websecure"
  - "traefik.http.routers.arifosmcp.tls.certresolver=letsencrypt"
  - "traefik.http.services.arifosmcp.loadbalancer.server.port=8080"
  - "traefik.http.services.arifosmcp.loadbalancer.healthcheck.path=/health"
  - "traefik.http.services.arifosmcp.loadbalancer.healthcheck.interval=10s"
  - "traefik.http.services.arifosmcp.loadbalancer.healthcheck.timeout=5s"
```

**Change**: Added `&& PathPrefix(`/mcp`)` to router rule.

### 2. WebMCP Service (aclip-cai)

**File**: `docker-compose.yml`  
**Lines**: 413-421

```yaml
labels:
  - "traefik.enable=true"
  # WebMCP router - path-based routing on main domain
  - "traefik.http.routers.webmcp.rule=Host(`arifosmcp.arif-fazil.com`) && PathPrefix(`/webmcp`)"
  - "traefik.http.routers.webmcp.entrypoints=websecure"
  - "traefik.http.routers.webmcp.tls.certresolver=letsencrypt"
  - "traefik.http.middlewares.webmcp-strip.stripprefix.prefixes=/webmcp"
  - "traefik.http.routers.webmcp.middlewares=webmcp-strip@docker"
  - "traefik.http.services.webmcp.loadbalancer.server.port=8081"
```

**Changes**:
1. Router name: `aclip` → `webmcp`
2. Rule: `Host(`aclip.arif-fazil.com`)` → `Host(`arifosmcp.arif-fazil.com`) && PathPrefix(`/webmcp`)`
3. Added stripprefix middleware to strip `/webmcp` before forwarding to container
4. Service name: `aclip` → `webmcp`

---

## Deployment Steps

Execute on VPS as `arifos` user:

```bash
# 1. Navigate to project directory
cd /opt/arifosmcp

# 2. Pull the updated docker-compose.yml
git pull origin main

# 3. Verify the changes are present
grep -A 5 "traefik.http.routers.webmcp.rule" docker-compose.yml

# 4. Recreate containers with new Traefik labels
docker compose up -d --no-deps --force-recreate arifosmcp aclip-cai

# 5. Restart Traefik to force route rediscovery
docker restart traefik_router

# 6. Wait for propagation
sleep 15

# 7. Verify routes are registered
docker logs traefik_router 2>&1 | grep -E "(arifosmcp|webmcp)"
```

---

## Verification Tests

### Test 1: Health Check
```bash
curl -s https://arifosmcp.arif-fazil.com/mcp/health
curl -s https://arifosmcp.arif-fazil.com/webmcp/health
```

**Expected**: Both return `{"status":"ok",...}`

### Test 2: Vitals Endpoint
```bash
curl -s https://arifosmcp.arif-fazil.com/webmcp/vitals | jq .
```

**Expected**:
```json
{
  "service": "arifOS WebMCP",
  "version": "2026.03.14-VALIDATED",
  "motto": "Ditempa Bukan Diberi — Forged, Not Given",
  "trinity": "ΔΩΨ",
  "floors": 13,
  "tools": 25
}
```

### Test 3: Session Initialization
```bash
curl -X POST https://arifosmcp.arif-fazil.com/webmcp/init \
  -H "Content-Type: application/json" \
  -d '{"actor_id": "test_user", "context": "WebMCP deployment verification"}'
```

**Expected**: Returns JSON with `session_id` and `auth_context`.

### Test 4: Tool List
```bash
curl -s https://arifosmcp.arif-fazil.com/webmcp/tools | jq '.tools | length'
```

**Expected**: Returns `25` (number of public tools)

---

## Troubleshooting

### Issue: Still getting 404 after deployment

**Check 1: Traefik route detection**
```bash
docker logs traefik_router 2>&1 | grep -E "(Adding route|Provider configuration)"
```

Should see lines like:
```
Adding route for webmcp on Host(`arifosmcp.arif-fazil.com`) && PathPrefix(`/webmcp`)
```

**Check 2: Container labels applied**
```bash
docker inspect aclip_cai_server | grep -A 30 Labels
```

Should contain:
```json
"traefik.http.routers.webmcp.rule=Host(`arifosmcp.arif-fazil.com`) && PathPrefix(`/webmcp`)"
```

**Check 3: Cloudflare cache**
If Traefik shows routes but public still 404, purge Cloudflare cache:
```bash
# Via Cloudflare Dashboard > Caching > Purge Everything
# Or via API (requires ZONE_ID and CF_TOKEN)
curl -X POST "https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/purge_cache" \
  -H "Authorization: Bearer {CF_TOKEN}" \
  -d '{"purge_everything":true}'
```

**Check 4: Force full redeploy**
```bash
docker compose down
docker compose up -d
docker restart traefik_router
```

---

## Architecture After Fix

```
                    Cloudflare (SSL)
                           │
                           ▼
            arifosmcp.arif-fazil.com
                           │
                    Traefik Router
                    ┌─────────────┐
                    │  ┌───────┐  │
          ┌─────────┤  │ /mcp  │  ├─────────┐
          │         │  └───┬───┘  │         │
          │         │      │      │         │
          │         │  ┌───┴───┐  │         │
          │         │  │/webmcp│  │         │
          │         │  └───┬───┘  │         │
          │         └──────┼──────┘         │
          │                │                │
          ▼                ▼                ▼
    ┌──────────┐    ┌──────────┐    ┌──────────┐
    │arifosmcp │    │stripprefix│   │ aclip    │
    │:8080     │    │middleware │   │:8081     │
    └──────────┘    └──────────┘    └──────────┘
         │                                  │
         │    A2A MCP (SSE)                 │    WebMCP (HTTP+WS)
         │    23 tools                      │    25 tools
         │                                  │
    ┌──────────┐                       ┌──────────┐
    │ AI Agents│                       │  Humans  │
    │(Kimi,    │                       │(Browsers)│
    │Claude)   │                       │          │
    └──────────┘                       └──────────┘
```

---

## Result

Once deployed, you'll have:

| Protocol | URL | Purpose | Audience |
|----------|-----|---------|----------|
| **A2A MCP** | `https://arifosmcp.arif-fazil.com/mcp` | Agent-to-Agent SSE | AI Agents (Kimi, Claude, etc.) |
| **WebMCP** | `https://arifosmcp.arif-fazil.com/webmcp` | Browser HTTP/WebSocket | Human Users |

**Same domain. Same SSL. Same VAULT999. Dual-surface constitutional AI.**

---

*arifOS v2026.03.14 | Ditempa Bukan Diberi — Forged, Not Given [ΔΩΨ | ARIF]*
