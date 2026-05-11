# GEOX Deployment Guide — Earth Intelligence Core
## Version: v2026.04.10-EIC | Seal: DITEMPA BUKAN DIBERI

---

## Executive Summary

GEOX deploys as **3 planes**, not one monolith:

| Plane | Function | Deployment Unit | Runtime |
|-------|----------|-----------------|---------|
| **MCP Server** | Brain / authority / tools | Python FastMCP | Container |
| **MCP Apps** | Tool-bound UI resources | Static HTML/JS | CDN or same container |
| **Web Apps** | Human-first portals | Same as MCP Apps | Static hosting |

**Key Insight:** MCP Apps are not special software. They are web apps with MCP metadata contracts.

---

## 1. System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           USER / AI AGENT                                   │
│                   (Claude Desktop / Copilot / Custom)                       │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
                        JSON-RPC over HTTPS
                            (Streamable HTTP)
                                  │
┌─────────────────────────────────▼───────────────────────────────────────────┐
│  PLANE 1: MCP SERVER (Authority Layer)                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  GEOX Earth Intelligence Core                                        │   │
│  │  • 7 essential tools                                                 │   │
│  │  • AC_Risk calculation (ToAC)                                        │   │
│  │  • Constitutional enforcement (F1-F13)                               │   │
│  │  • 888_HOLD gates                                                    │   │
│  │                                                                      │   │
│  │  Transport: Streamable HTTP (port 8000)                              │   │
│  │  Health: /health, /health/details, /tools                            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    Docker Container                          │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
                    Serves static UI resources
                                  │
┌─────────────────────────────────▼───────────────────────────────────────────┐
│  PLANE 2: MCP APPS (Interactive UI Layer)                                   │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐   │
│  │ AC_Risk     │ │ Basin       │ │ Seismic     │ │ Well Context        │   │
│  │ Console     │ │ Explorer    │ │ Viewer      │ │ Desk                │   │
│  │             │ │             │ │             │ │                     │   │
│  │ • ToAC calc │ │ • Leaflet   │ │ • 2D/3D     │ │ • Log viewer        │   │
│  │ • Verdict   │ │ • Play fair │ │ • Contrast  │ │ • Petrophysics      │   │
│  │ • History   │ │ • Prospects │ │ • 888_HOLD  │ │ • AC_Risk widget    │   │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────────────┘   │
│                                                                              │
│  Access: geox.arif-fazil.com/apps/{app_name}/                               │
│  Hosting: Same container (simple) or CDN (scale)                            │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Deployment Modes

### A. Research Profile (Single Node)
**Use when:** Personal VPS, small team, human-governed (888_HOLD)

```yaml
# docker-compose.yml
version: '3.8'

services:
  geox:
    image: geox/eic:latest
    ports:
      - "8000:8000"  # MCP Server
    volumes:
      - ./data:/data:ro
    environment:
      - GEOX_MODE=research
      - F13_HUMAN_VETO=required
    restart: unless-stopped
```

**Characteristics:**
- Single container
- Local data volume
- Human-in-the-loop enforced
- No auto-scaling needed

### B. Enterprise Profile (HA Ready)
**Use when:** Multi-user, production workloads, audit requirements

```yaml
# docker-compose.enterprise.yml
version: '3.8'

services:
  geox-mcp:
    image: geox/eic:latest
    deploy:
      replicas: 2
    ports:
      - "8000:8000"
    environment:
      - GEOX_MODE=enterprise
      - REDIS_URL=redis://redis:6379
      - VAULT_ENDPOINT=https://vault.internal:8200
    restart: always

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro

volumes:
  redis_data:
```

**Characteristics:**
- 2+ MCP server replicas
- Redis for caching
- Nginx reverse proxy + SSL
- Ready for Kubernetes migration

---

## 3. MCP Server Deployment

### Transport: Streamable HTTP (Standard)

| Transport | Status | Use Case |
|-----------|--------|----------|
| `stdio` | Legacy | Local dev only |
| `HTTP/SSE` | Deprecated | Migration only |
| **Streamable HTTP** | ✅ Current | Production |

**MCP Server Endpoints:**

```
POST /mcp/v1/messages        # JSON-RPC tool calls
GET  /health                 # Liveness probe
GET  /health/details         # Full capabilities
GET  /tools                  # Tool registry
GET  /tools/{name}           # Tool metadata
```

### Container Build

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy canonical GEOX
COPY geox/ ./geox/
COPY data/ ./data/

# Non-root user
RUN useradd -m -u 1000 geox && chown -R geox:geox /app
USER geox

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "-m", "geox.server", "--transport", "http", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GEOX_MODE` | `research` | `research` or `enterprise` |
| `GEOX_VERSION` | `v2026.04.10-EIC` | Version override |
| `F13_HUMAN_VETO` | `required` | Human-in-the-loop enforcement |
| `AC_RISK_THRESHOLD_HOLD` | `0.60` | 888_HOLD trigger |
| `AC_RISK_THRESHOLD_VOID` | `0.75` | VOID trigger |
| `REDIS_URL` | `None` | Cache connection |
| `VAULT_ENDPOINT` | `None` | Audit log destination |

---

## 4. MCP Apps Deployment

### Option A: Same Container (Simple)

MCP Apps served from `/apps/` path on same server:

```python
# In geox/server.py
@mcp.custom_route("/apps/{app_name}/{path:path}", methods=["GET"])
async def serve_app(request: Request) -> Response:
    # Serve static files from geox/apps/{app_name}/
    pass
```

**Pros:** Single deploy, simple networking
**Cons:** MCP server restart affects UIs

### Option B: CDN / Static Hosting (Recommended)

MCP Apps hosted separately, referenced by absolute URL:

```json
// geox/apps/ac_risk_console/manifest.json
{
  "app_id": "geox.ac_risk.console",
  "ui_entry": {
    "resource_uri": "https://apps.geox.arif-fazil.com/ac_risk_console/",
    "mode": "inline-or-external"
  }
}
```

**Pros:** Independent scaling, edge caching, zero-downtime updates
**Cons:** Slightly more complex initial setup

**Recommended for:** Basin Explorer (maps), Seismic Viewer (tiles)

---

## 5. Security & Governance

### Constitutional Floors → Deployment Controls

| Floor | Deployment Control | Implementation |
|-------|-------------------|----------------|
| **F1 Amanah** | Append-only audit | All operations logged to 999_VAULT |
| **F2 Truth** | Uncertainty propagation | AC_Risk in every response |
| **F4 Clarity** | Input validation | Schema enforcement on all inputs |
| **F7 Humility** | Confidence caps | Hard limits in code (max 15%) |
| **F9 Anti-Hantu** | Physics firewall | RATLAS validation on outputs |
| **F11 Authority** | Provenance chain | Digital signatures on data |
| **F13 Sovereign** | Human approval gates | 888_HOLD on AC_Risk ≥ 0.60 |

### Network Security

```yaml
# nginx.conf — security headers
server {
    listen 443 ssl http2;
    server_name geox.arif-fazil.com;

    # SSL
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.3;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline';" always;

    # MCP endpoints
    location / {
        proxy_pass http://geox-mcp:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 6. Operational Procedures

### Health Monitoring

```bash
# Liveness probe
curl https://geox.arif-fazil.com/health
# → OK

# Detailed status
curl https://geox.arif-fazil.com/health/details | jq .
# → {"ok": true, "tools": [...], "constitutional_floors": [...]}

# Tool registry
curl https://geox.arif-fazil.com/tools | jq '.tools[].name'
```

### Backup & Recovery

```bash
# Backup audit logs
docker exec geox-mcp tar czf - /data/999_vault > vault_backup_$(date +%Y%m%d).tar.gz

# Backup tool registry state
curl https://geox.arif-fazil.com/tools > tool_registry_backup.json
```

### Upgrade Procedure

```bash
# Zero-downtime upgrade (Enterprise)
docker-compose pull
docker-compose up -d --no-deps --scale geox-mcp=3 geox-mcp
sleep 10
docker-compose up -d --no-deps --scale geox-mcp=2 geox-mcp

# Simple upgrade (Research)
docker-compose pull
docker-compose up -d
```

---

## 7. Troubleshooting

### MCP Client Can't Connect

```bash
# Check server is running
curl http://localhost:8000/health

# Verify CORS headers
curl -I -X OPTIONS http://localhost:8000/mcp/v1/messages

# Check logs
docker logs geox-mcp --tail 100
```

### AC_Risk Not Calculating

```bash
# Test directly
curl -X POST http://localhost:8000/mcp/v1/messages \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "geox_compute_ac_risk",
    "params": {"u_phys": 0.5, "transform_stack": ["linear"]},
    "id": 1
  }'
```

### MCP Apps Not Loading

1. Verify manifest.json is valid JSON
2. Check `resource_uri` is reachable from client
3. Ensure CSP headers allow iframe embedding
4. Validate CORS preflight responses

---

## 8. Migration Path

### From Research → Enterprise

1. **Add Redis** for caching layer
2. **Add Nginx** for SSL termination
3. **Scale replicas** to 2+
4. **Externalize** MCP Apps to CDN
5. **Add monitoring** (Prometheus/Grafana)
6. **Migrate to Kubernetes** when >50 concurrent users

---

## 9. Checklist: Seal-Grade Deployment

- [ ] MCP Server health endpoint responding
- [ ] All 7 tools registered and callable
- [ ] AC_Risk calculation verified
- [ ] MCP Apps accessible via HTTPS
- [ ] 888_HOLD gates tested
- [ ] Audit logs writing to 999_VAULT
- [ ] SSL certificates valid
- [ ] Container running as non-root
- [ ] Backups configured
- [ ] F13 Sovereign enforced (human approval)

---

## Appendix A: File Structure (Canonical)

```
/opt/geox/
├── docker-compose.yml          # This deployment
├── Dockerfile                  # Container build
├── nginx.conf                  # Reverse proxy
├── geox/                       # Python package (read-only)
│   ├── server.py              # MCP entry point
│   ├── core/                  # AC_Risk, ToolRegistry
│   └── apps/                  # 4 MCP Apps
├── data/                       # Sample data (read-only)
├── 999_vault/                  # Audit logs (append-only)
└── ssl/                        # Certificates
```

---

## Appendix B: Quick Commands

```bash
# Deploy
docker-compose up -d

# Status
docker-compose ps
curl http://localhost:8000/health/details

# Logs
docker-compose logs -f

# Stop
docker-compose down

# Full reset (keeps vault)
docker-compose down -v
docker-compose up -d
```

---

*DITEMPA BUKAN DIBERI — Forged, Not Given*
*Enterprise Deployment: Sealed*
