# Security Hardening — Concrete Implementation Checklist
**Date:** 2026-03-21  
**Status:** DESIGNED → Ready for F13 Activation  
**Files Created:** 5 new configs + 2 updated docs

---

## ✅ COMPLETED: Phase 1 — Gödel Lock

| Item | Status | File |
|------|--------|------|
| Three-Ring model defined | ✅ | `GÖDEL_LOCK.md` |
| Tool inventory (Ring 0/1/2) | ✅ | `AGENTS.md` (Tool Ring Map) |
| Runtime enforcement script | ✅ | `scripts/gödel-shim.sh` |
| Hardened OpenClaw config | ✅ | `openclaw.json.secure.v2` |
| Security event logging | ✅ | `logs/security.jsonl` (template) |
| AGENTS.md updated | ✅ | Section 2 + Tool Ring Map |

**Key Point:** AgentZero is in **Ring 1** — fully accessible, logged but not blocked.

---

## 🔄 PENDING: Phase 2 — Traefik + HTTPS Hardening

### 2.1 Traefik Configuration Files

| File | Purpose | Status |
|------|---------|--------|
| `traefik-hardened.yml` | Static config with security headers | ✅ Created |
| `dynamic-hardened.yml` | Router/service definitions | ✅ Created |

### 2.2 What Changes

**Current State:**
```yaml
# traefik.yml (current)
entryPoints:
  web:
    address: ":80"
  websecure:
    address: ":443"
# No global security headers
# No rate limiting
```

**Hardened State:**
```yaml
# traefik-hardened.yml
entryPoints:
  web:
    address: ":80"
    http:
      redirections:
        entryPoint:
          to: websecure
          scheme: https
          permanent: true
  websecure:
    address: ":443"
    http:
      middlewares:
        - security-headers@file  # HSTS, CSP, X-Frame-Options

certificatesResolvers:
  letsencrypt:
    acme:
      tlsChallenge: {}  # Auto TLS
```

### 2.3 Security Headers Applied

| Header | Value |
|--------|-------|
| Strict-Transport-Security | max-age=31536000; includeSubDomains; preload |
| X-Frame-Options | DENY |
| X-Content-Type-Options | nosniff |
| X-XSS-Protection | 1; mode=block |
| Referrer-Policy | strict-origin-when-cross-origin |
| Content-Security-Policy | default-src 'self'; ... |
| Permissions-Policy | camera=(), microphone=(), geolocation=() |

### 2.4 Service Exposure Matrix

| Service | Public? | Auth | Domain |
|---------|---------|------|--------|
| arifOS MCP | ✅ Public | API token | `arifosmcp.arif-fazil.com` |
| AgentZero | ✅ Public | None (rate limited) | `agentzero.arif-fazil.com` |
| n8n | ⚠️ Internal | IP whitelist | `flow.arif-fazil.com` |
| Grafana | ⚠️ Internal | Basic auth | `metrics.arif-fazil.com` |
| OpenClaw | 🔒 Private | IP whitelist | `claw.internal.arif-fazil.com` |
| Prometheus | 🔒 Private | IP whitelist | `prometheus.internal.arif-fazil.com` |
| Qdrant | 🔒 Private | IP whitelist | `qdrant.internal.arif-fazil.com` |

---

## 🛠️ CONCRETE NEXT STEPS

### Step 1: Activate Gödel Lock (888_HOLD — Confirm First)

```bash
# SSH into host (srv1325122.hstgr.cloud)
ssh root@srv1325122.hstgr.cloud

# Backup current config
cp /opt/arifos/data/openclaw/openclaw.json.secure \
   /opt/arifos/data/openclaw/openclaw.json.secure.pre-gödel

# Apply hardened config
cp /opt/arifos/configs/openclaw/openclaw.json.secure.v2 \
   /opt/arifos/data/openclaw/openclaw.json.secure

# Ensure .env.docker has all required vars
cat /mnt/arifos/.env.docker | grep -E "^(TELEGRAM|KIMI|OPENCLAW)"

# Restart OpenClaw
docker compose -f /mnt/arifos/docker-compose.yml restart openclaw

# Verify
docker logs openclaw_gateway --tail 20
```

### Step 2: Apply Traefik Hardening

```bash
# Backup current Traefik config
cp /mnt/arifos/infrastructure/traefik.yml \
   /mnt/arifos/infrastructure/traefik.yml.pre-harden

cp /mnt/arifos/infrastructure/dynamic.yml \
   /mnt/arifos/infrastructure/dynamic.yml.pre-harden

# Apply hardened configs
cp /mnt/arifos/infrastructure/traefik-hardened.yml \
   /mnt/arifos/infrastructure/traefik.yml

cp /mnt/arifos/infrastructure/dynamic-hardened.yml \
   /mnt/arifos/infrastructure/dynamic.yml

# Create .htpasswd for dashboard auth (CHANGE PASSWORD!)
# Run on host:
docker run --rm httpd:alpine htpasswd -Bbn arif YOUR_STRONG_PASSWORD \
  > /mnt/arifos/infrastructure/.htpasswd

# Restart Traefik
docker compose -f /mnt/arifos/docker-compose.yml restart traefik

# Verify
docker logs traefik_router --tail 20
```

### Step 3: Verify HTTPS Endpoints

```bash
# Test each endpoint
curl -I https://arifosmcp.arif-fazil.com/health
curl -I https://agentzero.arif-fazil.com/health

# Check security headers
curl -I https://arifosmcp.arif-fazil.com | grep -i "strict-transport\|x-frame\|content-security"

# Verify redirect from HTTP to HTTPS
curl -I http://arifosmcp.arif-fazil.com  # Should return 301
```

### Step 4: Test Gödel Lock

```bash
# Ring 0: Should work
read ~/.openclaw/workspace/AGENTS.md  # ✅ Auto-execute

# Ring 1: Should work + log
docker ps  # ✅ Execute + log to security.jsonl
sessions_spawn(task="test", mode="run")  # ✅ Execute + log

# Ring 2: Should BLOCK + alert
docker exec ... --privileged  # 🚫 BLOCKED
curl -X POST ... -d "sk-..."  # 🚫 BLOCKED
```

### Step 5: Enable Security Logging

```bash
# Ensure log directory exists
docker exec openclaw_gateway mkdir -p /root/.openclaw/workspace/logs

# Set up log rotation (on host)
cat > /etc/logrotate.d/openclaw-security << 'EOF'
/opt/arifos/data/openclaw/workspace/logs/security.jsonl {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 0600 root root
}
EOF
```

---

## 🔐 SECRETS MIGRATION CHECKLIST

Move these from hardcoded config to `.env.docker`:

| Secret | Current Location | Target Env Var | Status |
|--------|-----------------|----------------|--------|
| Telegram bot token | `openclaw.json` | `TELEGRAM_BOT_TOKEN` | ⚠️ Move |
| Kimi API key | `openclaw.json` | `KIMI_API_KEY` | ⚠️ Move |
| Venice API key | `openclaw.json` | `VENICE_API_KEY` | ⚠️ Move |
| OpenClaw gateway token | `openclaw.json` | `OPENCLAW_GATEWAY_TOKEN` | ⚠️ Move |
| Anthropic API key | `openclaw.json` | `ANTHROPIC_API_KEY` | ⚠️ Move |
| OpenRouter API key | `openclaw.json` | `OPENROUTER_API_KEY` | ⚠️ Move |

**Migration command:**
```bash
# Extract and move to .env.docker
cat >> /mnt/arifos/.env.docker << 'EOF'
TELEGRAM_BOT_TOKEN=[REDACTED-TELEGRAM-TOKEN]
KIMI_API_KEY=sk-kimi-UmOZSyoLhaEK4bRCyN3JixVWvzFcWMxZRvEBaORwOMIacNkK6QSTnHi4WyOdPqby
VENICE_API_KEY=VENICE_ADMIN_KEY_2YbMspMkLPwfIdVTvTB2hs-ts5xVvRvlbaVSi9DpRD
OPENCLAW_GATEWAY_TOKEN=openclaw-token-2026-arifos
ANTHROPIC_API_KEY=sk-ant-...
OPENROUTER_API_KEY=sk-or-...
EOF

# Then: chmod 600 /mnt/arifos/.env.docker
```

---

## 🧪 VERIFICATION TESTS

Run these after activation:

### Test 1: AgentZero Access
```python
# Should succeed (Ring 1)
sessions_spawn(
    task="Analyze this data",
    runtime="acp",
    agentId="agent-zero",  # or default to agent-zero
    mode="run"
)
```

### Test 2: Security Block
```bash
# Should BLOCK with Telegram alert
docker run --privileged ubuntu echo "test"  # 🚫 Gödel Lock
```

### Test 3: HTTPS Headers
```bash
# Should show HSTS
curl -s -I https://arifosmcp.arif-fazil.com | grep strict-transport
# Expected: Strict-Transport-Security: max-age=31536000;...
```

### Test 4: OpenClaw Bound to Localhost
```bash
# From outside VPS, should NOT connect
curl http://YOUR_VPS_IP:18789  # Should fail/timeout

# Via Traefik HTTPS, should work
curl https://claw.internal.arif-fazil.com  # If on allowed IP
```

---

## 📊 ROLLBACK PLAN

If anything breaks:

```bash
# 1. Restore OpenClaw config
cp /opt/arifos/data/openclaw/openclaw.json.secure.pre-gödel \
   /opt/arifos/data/openclaw/openclaw.json.secure
docker restart openclaw_gateway

# 2. Restore Traefik config
cp /mnt/arifos/infrastructure/traefik.yml.pre-harden \
   /mnt/arifos/infrastructure/traefik.yml
docker restart traefik_router

# 3. Verify
openclaw status
docker ps
```

---

## 🎯 AGENT CAPABILITIES PRESERVED

The Gödel lock **DOES NOT RESTRICT** these operations:

| Capability | Ring | Status |
|------------|------|--------|
| Spawn AgentZero | 1 | ✅ Full access |
| Spawn Claude/Codex | 1 | ✅ Full access |
| Docker exec (non-privileged) | 1 | ✅ Full access |
| File read/write (workspace) | 0/1 | ✅ Full access |
| Browser automation | 1 | ✅ Full access |
| arifOS MCP tools | 1 | ✅ Full access |
| Message (Telegram) | 1 | ✅ Full access |
| Cron jobs | 1 | ✅ Full access |
| Sub-agent orchestration | 1 | ✅ Full access |

---

*Awaiting F13 confirmation to proceed with activation.*

**Sealed:** 2026-03-21 | arifOS_bot | DITEMPA BUKAN DIBERI
