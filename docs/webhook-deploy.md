## arifOS Webhook Deploy — Setup & Architecture

### What is this?

A FastAPI webhook server that runs on your VPS (af-forge) and listens for GitHub webhooks. When a push/release comes in, it validates the HMAC-SHA256 signature, runs the existing `deploy_arifosmcp.sh`, and reports the result.

```
GitHub Push/Release → HTTPS webhook → VPS:8443 → Signature validated → deploy_arifosmcp.sh → health check
```

### Why vs GitHub Actions?

| Approach | Pros | Cons |
|----------|------|------|
| **GitHub Actions** (current) | Managed runners, no infra | Requires SSH secrets, starts from cold |
| **VPS Webhook** (this) | No cold start, full control | VPS exposed, needs own auth |

Both are valid. This gives you a direct alternative.

---

## Setup

### Step 1: Generate webhook secret

```bash
# On VPS
export ARIFOS_WEBHOOK_SECRET=$(openssl rand -hex 32)
echo $ARIFOS_WEBHOOK_SECRET   # copy this — needed for GitHub
```

### Step 2: Start the webhook server

```bash
# Option A: Direct
export ARIFOS_WEBHOOK_SECRET=<secret>
export ARIFOS_DEPLOY_SCRIPT=/root/arifOS/scripts/deploy_arifosmcp.sh
python3 /root/arifOS/scripts/webhook_deploy_server.py --port 8443 --host 127.0.0.1

# Option B: Via systemd
systemctl enable arifos-webhook
systemctl start arifos-webhook
```

### Step 3: Configure Cloudflare or Caddy

Cloudflare: proxy `https://arifOS.arif-fazil.com/webhook/github` → `http://127.0.0.1:8443/webhook/github`

Or Caddy (in your existing Caddyfile):
```
arifOS.arif-fazil.com {
    handle /webhook/github* {
        reverse_proxy localhost:8443
    }
    # ... rest of existing config
}
```

### Step 4: Register webhook in GitHub

Go to: **GitHub repo → Settings → Webhooks → Add webhook**
```
Payload URL:     https://arifOS.arif-fazil.com/webhook/github
Content type:    application/json
Secret:          <your ARIFOS_WEBHOOK_SECRET>
Events:          Pushes, Releases, Repository dispatch
Active:          ✓
```

---

## Security Model (Constitutional Floors)

| Floor | Role | Enforcement |
|-------|------|-------------|
| F1 Amanah | Pre-flight check | Script must exist + be executable |
| F2 Truth | Signature validation | HMAC-SHA256 before any execution |
| F5 Humility | Rate limiting | 10 req / 5 min per IP |
| F7 Adaptation | Deploy cooldown | 60s between deploys |
| F11 Authority | Webhook secret | Human-set, machine cannot bypass |
| F13 Sovereign | Final veto | Human owns the secret |

---

## Docker Compose Addition

```yaml
arifos-webhook:
  image: python:3.12-slim
  container_name: arifos-webhook
  restart: unless-stopped
  ports:
    - "127.0.0.1:8443:8443"
  environment:
    - ARIFOS_WEBHOOK_SECRET=${ARIFOS_WEBHOOK_SECRET}
    - ARIFOS_DEPLOY_SCRIPT=/app/deploy_arifosmcp.sh
    - WEBHOOK_PORT=8443
  volumes:
    - /root/arifOS/scripts:/app:ro
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8443/health"]
    interval: 30s
    timeout: 5s
    retries: 3
  networks: [arifos_core]
```

---

## Monitoring

```bash
curl http://localhost:8443/health   # quick health
curl http://localhost:8443/status  # last deploy time + status
tail -f /var/log/arifos/webhook.log
```

---

## For AAA repo

Create a separate deploy script:
```bash
# /root/AAA/scripts/webhook_deploy.sh
#!/bin/bash
set -euo pipefail
cd /root/AAA && git pull origin main
```

Then use `ARIFOS_DEPLOY_SCRIPT=/root/AAA/scripts/webhook_deploy.sh` in the AAA webhook service.