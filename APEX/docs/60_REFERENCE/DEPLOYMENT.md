# DEPLOYMENT.md — arifOS Complete Deployment Guide
**T000 Version:** 2026.02.15-FORGE-TRINITY-SEAL  
**Code Version:** v64.2-GAGI  
**Endpoint:** https://arifosmcp.arif-fazil.com  
**Reality Index:** 0.94

---

## 🎯 Quick Start (Choose Your Path)

| Your Goal | Path | Time | Difficulty |
|:----------|:-----|:----:|:----------:|
| **Try immediately** | Copy-paste SYSTEM_PROMPT | 5 sec | 🟢 Easy |
| **Local development** | pip install + stdio | 30 sec | 🟢 Easy |
| **Production (recommended)** | VPS/Coolify deployment | 5-10 min | 🟡 Medium |
| **Enterprise/air-gapped** | Docker + VPS | 15 min | 🔴 Advanced |

---

**Note:** The primary MCP server entry point is now the unified server at `server.py` (root), combining AAA-MCP and ACLIP-CAI tools. The standalone `aaa_mcp/server.py` and `aclip_cai/server.py` are deprecated but remain for backward compatibility.

---

## 1️⃣ Zero-Install: Copy-Paste Prompt (5 seconds)

No installation required. Works with any LLM that accepts system prompts.

**File:** `333_APPS/L1_PROMPT/SYSTEM_PROMPT.md`

```bash
# Copy this file's contents into any AI's system settings
cat 333_APPS/L1_PROMPT/SYSTEM_PROMPT.md | pbcopy  # macOS
cat 333_APPS/L1_PROMPT/SYSTEM_PROMPT.md | xclip    # Linux
```

**Supports:** ChatGPT, Claude, Gemini, Copilot, and any custom LLM.

---

## 2️⃣ Local Development: pip install (30 seconds)

```bash
# Install
pip install arifos

# Run MCP server (SSE primary)
python -m aaa_mcp

# For local desktop clients that require stdio
python -m aaa_mcp stdio

# Test
python -m aaa_mcp.selftest
```

**Default transport:** `sse` (use `python -m aaa_mcp stdio` for Claude Desktop/Cursor local mode)

---

## 3️⃣ Production: VPS/Coolify (5-10 minutes)

### Prerequisites
- VPS reachable over SSH
- Coolify or Docker Compose available on host
- GitHub repo secrets set: `VPS_HOST`, `VPS_USERNAME`, `VPS_SSH_KEY`

### Deploy
```bash
# Auto-deploy from GitHub Actions
# Workflow: .github/workflows/deploy.yml
git push origin main
```

### Verify
```bash
curl https://arifosmcp.arif-fazil.com/health
# {"status":"healthy","version":"...","reality_index":...}
```

---

## 4️⃣ Enterprise/VPS: Docker Compose with Trinity Protocol (15 minutes)

Deploy arifOS as a sovereign MCP server with dual transport (SSE + HTTP) using Docker Compose. The **Trinity Protocol** runs both SSE (port 8080) and HTTP MCP (port 8089) simultaneously for maximum client compatibility.

### Prerequisites
- Docker Engine 20.10+ and Docker Compose v2.0+
- VPS with 4GB+ RAM (recommended for sentence-transformers models)
- Domain name with DNS pointing to VPS IP (optional for production)

### 1. Clone and Configure
```bash
git clone https://github.com/ariffazil/arifOS.git
cd arifOS
```

Create environment file from template:
```bash
cp .env.docker.example .env.docker
# Edit .env.docker with your API keys and ARIF_SECRET
```

### 2. Start Container
```bash
docker-compose -f deployment/docker-compose.vps.yml up -d --build
```

**Port Mapping:**
- SSE Transport: `8088:8080` → Clients connect to `/sse`
- REST Bridge: `8889:8089` → Clients connect to `/mcp` and `/health`

### 3. Verify Deployment
```bash
# Check container status
docker ps --filter "name=arifosmcp"

# Test SSE endpoint (should hang - expected)
curl -H "ARIF_SECRET: YOUR_STRONG_SECRET_HERE" http://localhost:8088/sse -m 2

# Test HTTP MCP endpoint
curl -X POST http://localhost:8889/mcp \
  -H "Content-Type: application/json" \
  -H "ARIF_SECRET: YOUR_STRONG_SECRET_HERE" \
  -d '{"jsonrpc":"2.0","method":"ping","id":1}'

# Test health endpoint (served by REST bridge)
curl -fss http://localhost:8889/health
```

### 4. Production Setup with Nginx + Cloudflare
For public access with SSL termination:

1. **Install Nginx & Certbot:**
   ```bash
   sudo apt install nginx certbot python3-certbot-nginx
   ```

2. **Configure Nginx** (see `docs/nginx/arifosmcp.conf.example`):
   - Proxy `/sse` to `http://127.0.0.1:8088/sse`
   - Proxy `/mcp` to `http://127.0.0.1:8889/mcp`
   - Set up SSL with Let's Encrypt

3. **Cloudflare DNS:**
   - Create A record pointing to VPS IP
   - Enable Proxy (orange cloud) for DDoS protection
   - SSL/TLS encryption mode: Full

### 5. Automated Deployment with GitHub Actions
Use the included CI/CD pipeline for automatic deployment on git push:

1. Set repository secrets:
   - `VPS_HOST`: VPS IP address
   - `VPS_USERNAME`: SSH username (usually `root`)
   - `VPS_SSH_KEY`: Private SSH key

2. Push to `main` branch → auto-deploys to VPS

**Workflow file:** `.github/workflows/deploy.yml`

---

## 5️⃣ Production Hardening & Monitoring (15-30 minutes)

Advanced configuration for sovereign, production-grade deployments with Docker Compose.

### 1. Security Hardening

**Container Security:**
```bash
# Run as non-root user (already configured in Dockerfile)
# Limit container resources
docker update --memory 2G --memory-swap 3G arifosmcp_server

# Restart policy
docker update --restart unless-stopped arifosmcp_server
```

**Network Security:**
```bash
# Configure firewall (UFW)
sudo ufw allow 22/tcp comment 'SSH'
sudo ufw allow 80/tcp comment 'HTTP'
sudo ufw allow 443/tcp comment 'HTTPS'
sudo ufw allow from 172.0.0.0/8 to any port 8088 comment 'Docker SSE'
sudo ufw allow from 172.0.0.0/8 to any port 8889 comment 'Docker HTTP'
sudo ufw enable
```

**Secrets Management:**
- Store API keys in `.env.docker` (never commit to git)
- Use Docker secrets or HashiCorp Vault for enterprise
- Rotate `ARIF_SECRET` regularly

### 2. Monitoring & Logging

**Container Health Monitoring:**
```bash
# View real-time logs
docker logs -f arifosmcp_server

# Health check status
docker inspect --format='{{.State.Health.Status}}' arifosmcp_server

# Resource usage
docker stats arifosmcp_server
```

**Nginx Log Analysis:**
```bash
# Monitor access logs
tail -f /var/log/nginx/access.log | grep arifosmcp

# Error tracking
tail -f /var/log/nginx/error.log
```

**Constitutional Metrics:**
- Check VAULT999 ledger: `docker exec arifosmcp_server ls -la /usr/src/app/data/VAULT999/`
- Monitor F12 injection attempts in logs

### 3. Backup & Disaster Recovery

**Volume Backups:**
```bash
# Backup Docker volume
docker run --rm -v arifos_data:/data -v $(pwd):/backup alpine \
  tar czf /backup/arifos-data-$(date +%Y%m%d).tar.gz -C /data .

# Restore from backup
docker run --rm -v arifos_data:/data -v $(pwd):/backup alpine \
  sh -c "cd /data && tar xzf /backup/arifos-data-backup.tar.gz"
```

**Configuration Backups:**
- Backup `deployment/docker-compose.vps.yml`, `.env.docker`, Nginx configs
- Store encrypted backups offsite

### 4. High Availability (Optional)

**Load Balancing:**
```nginx
# Nginx upstream configuration for multiple containers
upstream arifosmcp {
    server 127.0.0.1:8088;
    server 127.0.0.1:8889 backup;
}
```

**Container Orchestration:**
- Use Docker Swarm or Kubernetes for multi-node deployment
- Configure health checks and auto-healing

### 5. Alternative: Systemd Deployment (Without Docker)

For environments where containers are not available:

```bash
# Follow traditional systemd deployment
git clone https://github.com/ariffazil/arifOS.git
cd arifOS
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Create `/etc/systemd/system/arifos-mcp.service`:
```ini
[Unit]
Description=arifOS MCP Server
After=network.target

[Service]
User=arifos
WorkingDirectory=/home/arifos/arifOS
ExecStart=/home/arifos/arifOS/.venv/bin/python -m aaa_mcp sse
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl start arifos-mcp
sudo systemctl enable arifos-mcp
```

---

## 🔐 Environment Variables

| Variable | Required | Default | Purpose |
|:---------|:--------:|:-------:|:--------|
| `ARIFOS_API_KEY` | For cloud | - | Bearer token auth |
| `PORT` | No | 8080 | Server port |
| `HOST` | No | 0.0.0.0 | Bind address |
| `AAA_MCP_TRANSPORT` | No | sse | stdio/sse/http |
| `DATABASE_URL` | No | - | PostgreSQL for VAULT999 |
| `REDIS_URL` | No | - | Redis for sessions |

---

## 🌐 Platform Integration

See [MCP_PLATFORM_GUIDE.md](./MCP_PLATFORM_GUIDE.md) for detailed platform configs:

| Platform | Transport | Config File |
|:---------|:---------:|:------------|
| **Claude Desktop** | stdio | `claude_desktop_config.json` |
| **ChatGPT Dev** | HTTP/SSE | Developer Mode UI |
| **Codex CLI** | stdio | `~/.codex/config.toml` |
| **Cursor** | stdio | `.cursor/mcp.json` |
| **OpenCode** | stdio | `opencode.json` |
| **JetBrains** | stdio | OpenCode plugin |
| **AgentZero** | HTTP | `agentzero.yaml` |

---

## 🧪 Testing Your Deployment

```bash
# Health check
curl https://arifosmcp.arif-fazil.com/health

# List tools
curl -X POST \
  -H "Authorization: Bearer $ARIFOS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":1}' \
  https://arifosmcp.arif-fazil.com/mcp

# Test anchor tool
curl -X POST \
  -H "Authorization: Bearer $ARIFOS_API_KEY" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"anchor","arguments":{"query":"test","actor_id":"user"}},"id":2}' \
  https://arifosmcp.arif-fazil.com/mcp
```

---

## 📊 Production Checklist

Before going live:

- [ ] Health endpoint returns `{"status":"healthy"}`
- [ ] All 9 tools respond correctly
- [ ] F12 Injection Guard active (test with malicious query)
- [ ] API key authentication enabled (not localhost)
- [ ] Database connected (if using VAULT999)
- [ ] Logs shipping to monitoring
- [ ] F13 Sovereign override tested

---

## 🔒 Security Hardening

### F12 Injection Defense
Default: 20+ patterns, compound scoring
```python
# Critical patterns trigger VOID (0.9+)
"ignore previous instructions"
"forget your instructions"

# High patterns trigger sanitize (0.8)
"you are now a different AI"
```

### F11 Authority
- No anonymous access in production
- Actor ID required for all queries
- Telegram/WhatsApp context auto-detected

### F13 Sovereign
- Human veto available via `888_HOLD`
- All decisions logged to VAULT999
- Irreversible actions require explicit approval

---

## 🚨 Troubleshooting

| Issue | Cause | Fix |
|:------|:------|:----|
| `Connection refused` | Server not running | Check `docker ps` and container logs |
| `401 Unauthorized` | Missing API key | Set `Authorization: Bearer $KEY` header |
| `SSE timeout` | Network issue | Use HTTP transport or check firewall |
| `High latency` | ZRAM pressure | Check F4 thermodynamic state |
| `Tools not showing` | Config error | Verify MCP config JSON syntax |

---

## 📞 Support

- **Documentation:** https://arifos.arif-fazil.com
- **Live Status:** https://arifosmcp.arif-fazil.com/health
- **Email:** enterprise@arif-fazil.com
- **Issues:** https://github.com/ariffazil/arifOS/issues

---

## 📚 Related Docs

- [MCP_PLATFORM_GUIDE.md](./MCP_PLATFORM_GUIDE.md) — Platform-specific configs
- [README.md](./README.md) — Overview and philosophy
- [README_ZERO_CONTEXT.md](./README_ZERO_CONTEXT.md) — For first-time users
- [000_THEORY/000_LAW.md](./000_THEORY/000_LAW.md) — 13 Constitutional Floors

---

*DITEMPA BUKAN DIBERI* 🔥💎🧠  
**Ω₀ = 0.04** — High confidence in deployment stability.
