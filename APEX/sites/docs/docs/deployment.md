---
id: deployment
title: Deployment
sidebar_position: 3
description: Deploy arifOS to VPS/Coolify, Docker, or run locally. Nginx, systemd, and health check guidance.
---

# Deployment

> Source: [`DEPLOYMENT.md`](https://github.com/ariffazil/arifOS/blob/main/DEPLOYMENT.md) . [`docker-compose.yml`](https://github.com/ariffazil/arifOS/blob/main/docker-compose.yml) . [`Dockerfile`](https://github.com/ariffazil/arifOS/blob/main/Dockerfile)

:::warning 888_HOLD - Review Before Executing
All deployment commands below should be reviewed before running. Do not copy-paste into production without understanding each step. Irreversible actions (firewall rules, DNS changes) are marked explicitly.
:::

---

## Quick Path Selection

| Your goal | Path | Time |
|:--|:--|:--|
| Try it right now | System prompt only | 5 sec |
| Local dev / Claude Desktop | `pip install` + stdio | 30 sec |
| Cloud (Railway) | `railway up` | 5 min |
| Enterprise / VPS + Docker | Docker Compose | 15 min |

---

## Path 1 - Local Development (stdio)

```bash
pip install arifos
python -m aaa_mcp               # stdio mode; connect via Claude Desktop or Cursor
```

Run the self-test to verify:

```bash
python -m aaa_mcp.selftest
```

---

## Path 2 - Railway (Cloud, 5 minutes)

Railway provides free tier with persistent volumes and automatic TLS.

```bash
# [888_HOLD] Review these commands before running
npm install -g @railway/cli
railway login
cd arifOS
railway init --name arifos-mcp
railway variables set PORT=8080 HOST=0.0.0.0
railway variables set AAA_MCP_TRANSPORT=sse
railway variables set ARIF_SECRET=your-strong-secret-here
railway up
railway domain                  # get your public URL
```

Verify:

```bash
curl https://your-app.up.railway.app/health
# {"status":"healthy","version":"2026.2.19","floors_passing":13}
```

---

## Path 3 - Docker Compose on VPS (recommended for production)

If you're on Hostinger’s **Ubuntu 24.04 with Coolify** template, start here first: [Hostinger Coolify VPS Template](./coolify-hostinger).

### 3.1 - Clone and configure

```bash
git clone https://github.com/ariffazil/arifOS.git
cd arifOS
cp .env.docker.example .env.docker
# Edit .env.docker: set ARIF_SECRET, BRAVE_API_KEY, DATABASE_URL
```

### 3.2 - Start the Trinity stack (SSE primary + MCP fallback)

```bash
# [888_HOLD] Starts containers; review docker-compose.vps.yml first
docker-compose -f deployment/docker-compose.vps.yml up -d --build
```

Port mapping after startup:

| Port | Transport | Connect via |
|:--|:--|:--|
| `8088` | SSE | `/sse` endpoint |
| `8889` | HTTP MCP fallback | `/mcp` endpoint |

### 3.3 - Verify containers

```bash
docker ps --filter "name=arifosmcp"
docker logs -f arifosmcp_server             # live logs

# Test SSE (expects connection to hang - that is correct)
curl -H "ARIF_SECRET: your-secret" http://localhost:8088/sse -m 2

# Test HTTP MCP
curl -X POST http://localhost:8889/mcp \
  -H "Content-Type: application/json" \
  -H "ARIF_SECRET: your-secret" \
  -d '{"jsonrpc":"2.0","method":"ping","id":1}'
```

### 3.4 - Coolify (Hostinger VPS + Traefik) — recommended routing

If you're deploying on a VPS running **Coolify** (Ubuntu 24.04 + Traefik), use the repo compose file
`deployment/docker-compose.vps.yml`. It already includes Traefik labels to route:

- `GET /sse` → in-container port `8080`
- `POST /mcp` and `GET /health` → in-container port `8089` (fallback sidecar)

#### 3.4.1 - DNS

- Create/confirm an `A` record: `arifosmcp.arif-fazil.com` → `<your-vps-ip>`.
- For early SSE debugging, keep Cloudflare **DNS-only (grey-cloud)** until stable.

#### 3.4.2 - Coolify resource (Docker Compose)

1. Coolify → Project → **Add Resource** → **Docker Compose**
2. Repo: `ariffazil/arifOS`
3. Compose path: `deployment/docker-compose.vps.yml`
4. Deploy

If deploy fails with `network not found`, create the external network once on the VPS, then redeploy:

```bash
docker network create coolify
```

#### 3.4.3 - Domain + HTTPS

- Resource → Domains → add `arifosmcp.arif-fazil.com`
- Enable HTTPS / Let’s Encrypt (Coolify-managed)

#### 3.4.4 - Verify (from your laptop)

```bash
# Health
curl -i https://arifosmcp.arif-fazil.com/health

# SSE (expects a hanging stream)
curl -N -H "Accept: text/event-stream" https://arifosmcp.arif-fazil.com/sse

# MCP Streamable HTTP
curl -sS https://arifosmcp.arif-fazil.com/mcp \
  -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'

# Optional: well-known discovery
curl -i https://arifosmcp.arif-fazil.com/.well-known/mcp/server.json
```

### 3.5 - Nginx reverse proxy (TLS termination)

Install Nginx and Certbot, then create `/etc/nginx/sites-available/arifosmcp`:

```nginx
server {
    listen 443 ssl;
    server_name arifosmcp.arif-fazil.com;

    ssl_certificate     /etc/letsencrypt/live/arifosmcp.arif-fazil.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/arifosmcp.arif-fazil.com/privkey.pem;

    # SSE transport
    location /sse {
        proxy_pass         http://127.0.0.1:8088/sse;
        proxy_http_version 1.1;
        proxy_set_header   Connection "";
        proxy_buffering    off;
        proxy_read_timeout 3600s;
    }

    # HTTP MCP transport
    location /mcp {
        proxy_pass         http://127.0.0.1:8889/mcp;
        proxy_http_version 1.1;
        proxy_set_header   Host $host;
    }

    # Health endpoint (served by MCP fallback sidecar)
    location /health {
        proxy_pass http://127.0.0.1:8889/health;
    }
}
```

```bash
# [888_HOLD] Symlink and reload Nginx
sudo ln -s /etc/nginx/sites-available/arifosmcp /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

### 3.6 - Obtain TLS certificate

```bash
# [888_HOLD] Modifies /etc/letsencrypt - review first
sudo certbot --nginx -d arifosmcp.arif-fazil.com
```

---

## Path 4 - Systemd Service (no Docker)

Create `/etc/systemd/system/arifos-mcp.service`:

```ini
[Unit]
Description=arifOS MCP Server
After=network.target

[Service]
Type=simple
User=arifos
WorkingDirectory=/opt/arifOS
ExecStart=/opt/arifOS/venv/bin/python -m aaa_mcp sse
Restart=always
RestartSec=5
EnvironmentFile=/opt/arifOS/.env

[Install]
WantedBy=multi-user.target
```

```bash
# [888_HOLD] Modifies systemd - review before running
sudo systemctl daemon-reload
sudo systemctl enable --now arifos-mcp
sudo systemctl status arifos-mcp
```

---

## Security Hardening

### Firewall (UFW)

```bash
# [888_HOLD] Modifies firewall rules
sudo ufw allow 22/tcp    comment 'SSH'
sudo ufw allow 80/tcp    comment 'HTTP (redirect)'
sudo ufw allow 443/tcp   comment 'HTTPS'
# Block direct container port access from internet:
sudo ufw deny 8088/tcp
sudo ufw deny 8889/tcp
sudo ufw enable
```

### Secret rotation

- Rotate `ARIF_SECRET` regularly
- Store API keys only in `.env.docker` (never commit to git)
- Use Docker secrets or HashiCorp Vault for enterprise deployments

---

## Monitoring & Backup

### Health monitoring

```bash
# Container health
docker inspect --format='{{.State.Health.Status}}' arifosmcp_server
docker stats arifosmcp_server

# Constitutional metrics
curl https://arifosmcp.arif-fazil.com/metrics.json
```

### VAULT999 backup

```bash
# Backup vault data volume
docker run --rm \
  -v arifos_data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/vault-$(date +%Y%m%d).tar.gz -C /data .
```

### CI/CD (GitHub Actions)

The repo ships `.github/workflows/deploy.yml` for auto-deploy on push to `main`. Set these secrets in your GitHub repository:

- `VPS_HOST` - VPS IP
- `VPS_USERNAME` - SSH user (typically `root`)
- `VPS_SSH_KEY` - Private SSH key

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|:--|:--|:--|
| `/health` returns 502 | Container not running | `docker ps`, `docker logs` |
| SSE connection drops immediately | Missing `ARIF_SECRET` header | Add `-H "ARIF_SECRET: ..."` |
| `VOID` on all tool calls | F12 injection threshold exceeded | Check query for prompt injection patterns |
| VAULT999 not persisting | No volume mount | Confirm `volumes:` in docker-compose |
| `13/13 floors passing: false` | Physics disabled or missing dep | `pip install arifos[full]` |
