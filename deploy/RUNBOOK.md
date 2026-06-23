# Runbook — arifOS Federation

> **Purpose**: Restart, verify, rollback, and **deploy** per organ without guesswork.
> **Last updated**: 2026-06-06 by Ω — Entropy reduction sweep: renamed L1–L13 → L1–L13, documented public MCP status codes.
> **Sovereign law**: `L1–L13` (was `L1–L13`) active at `/root` — all agents are governed. See [`000_CONSTITUTION.md`](https://github.com/ariffazil/arifos/blob/main/static/arifos/theory/000/000_CONSTITUTION.md).

---

## ARCHITECTURE OVERVIEW

```
Bare-metal systemd (ports exposed via Caddy or Cloudflare Tunnel)
├── arifOS MCP        → :8088   (constitutional kernel)  ← Tunnel ingress
├── arifosd           → :18081  (constitutional daemon)
├── WEALTH            → :18082  (FastMCP monolith, 44 tools)
├── WELL              → :18083  (human readiness)
├── GEOX MCP          → :8081   (earth intelligence)
├── A-FORGE           → :7071   (TypeScript execution shell)
├── AAA a2a           → :3001   (control plane / React cockpit)
├── Hermes ASI        → Telegram bot (@ASI_arifos_bot)
├── Hermes A2A        → :18001  (A2A bridge)
├── OpenClaw GW       → :18789  (A2A mesh gateway)
├── cn-organ          → :18795  (Continue CLI organ gateway)
├── APEX Prime        → :3002   (888 JUDGE deliberative relay)
├── vault999-api      → :8100   (vault read API)
├── vault999-writer   → :5001   (vault write API — internal only)
├── NATS              → :4222/:8222 (event bus + JetStream)
├── Prometheus        → :9090
├── Grafana           → :3000
├── Ollama            → :11434
├── Node Exporter     → :9100
├── Caddy             → :80/:443 (TLS reverse proxy)
├── cloudflared       → —       (Cloudflare Tunnel for arifos.arif-fazil.com)
├── earlyoom          → —       (memory guardian)

Docker (supporting services only)
├── postgres  → :5432  (vault999, Supabase pooler)
├── redis     → :6379  (session cache, federation memory broker)
├── qdrant    → :6333  (L3 semantic memory)
├── falkordb  → :8000  (L5 entity extraction / Graphiti backend)
├── temporal  → :7233  (workflow engine)
└── temporal-ui → :8233
```

### Ingress Topology

| Site | DNS | Path |
|------|-----|------|
| `arif-fazil.com` | A → `72.62.71.199` | Direct → Caddy :443 → static |
| `arifos.arif-fazil.com` | CNAME → Tunnel | Cloudflare Tunnel → `localhost:8088` (bypasses Caddy) |
| `aaa.arif-fazil.com` | A → `72.62.71.199` | Direct → Caddy :443 → `localhost:3001` |
| `geox.arif-fazil.com` | A → `72.62.71.199` | Direct → Caddy :443 → `localhost:8081` |
| `wealth.arif-fazil.com` | wildcard → `arif-fazil.com` | Direct → Caddy :443 → `localhost:18082` |
| `well.arif-fazil.com` | wildcard → `arif-fazil.com` | Direct → Caddy :443 → `localhost:18083` |

**Cloudflare Tunnel:**
- Tunnel name: `arifos-mcp`
- Tunnel ID: `ea84faf9-8dd3-4185-8444-c9033c1b2473`
- Config: `/root/.cloudflared/config.yml`
- Credentials: `/root/.cloudflared/ea84faf9-8dd3-4185-8444-c9033c1b2473.json`
- Service: `systemctl status cloudflared`
- DNS managed by: `cloudflared tunnel route dns`

---

## FEDERATION CORE — systemd

All core organs run as systemd services. **No Docker compose for core services.**

### 1. arifOS Kernel

| Field | Value |
|-------|-------|
| Repo | `/root/arifOS` |
| Service | `arifos.service` |
| Port | 8088 |
| Runtime version | `kanon-5be8851` (dynamic, from `git describe`) |

#### Mandatory Post-Change Reality Gate (7-tool facade — 2026-06-23)
**After ANY edit to the public facade:**
1. Commit/push (HEAD must match origin/main for make deploy-local).
2. `make deploy-local` **or** manual rsync + `systemctl restart arifos.service`.
3. `./deploy/check_reality.sh` — **must exit 0** (code + live == exactly 7).
4. **Only after PASS** may you edit docs, manifests, or run generators.

#### Restart + Gate (the flow)
```bash
systemctl restart arifos
./deploy/check_reality.sh
```

#### Verify (all of these)
```bash
# 1. Health + identity
curl -s http://localhost:8088/health | python3 -m json.tool

# 2. Tool registry (exactly the 7 public verbs)
curl -s http://localhost:8088/tools | python3 -m json.tool

# 3. Reality gate (the one that matters)
./deploy/check_reality.sh || echo "REALITY FAIL — restart or filter not effective"

# 4. MCP discovery (should list only the 7)
curl -s http://localhost:8088/.well-known/mcp/server.json | python3 -m json.tool | grep -E '"name":|count'
```

#### Rollback
arifOS deploys via bare-metal systemd from `/root/arifOS` repo. To roll back:
```bash
# 1. Identify last good commit
git -C /root/arifOS log --oneline -10

# 2. Checkout previous commit and restart:
git -C /root/arifOS checkout <last-good-sha>
# Or edit WorkingDirectory in /etc/systemd/system/arifos.service, then:
systemctl daemon-reload
systemctl restart arifos

# 3. Verify
curl -s http://localhost:8088/health | python3 -m json.tool | grep runtime_drift
# Should be: "runtime_drift": false
```

---

### 2. arifosd (Constitutional Daemon)

| Field | Value |
|-------|-------|
| Repo | `/root/arifOS` |
| Service | `arifosd.service` |
| Port | 18081 |

#### Restart
```bash
systemctl restart arifosd
```

#### Verify
```bash
curl -s http://localhost:18081/health | python3 -m json.tool
# Expected: {"status":"ok","daemon_up":true,"storage_writable":true}
```

---

### 3. WEALTH

| Field | Value |
|-------|-------|
| Repo | `/root/WEALTH` |
| Service | `wealth-organ.service` |
| Port | 18082 |

#### Restart
```bash
systemctl restart wealth-organ
```

#### Verify
```bash
curl -s http://localhost:18082/health | python3 -m json.tool
curl -s http://localhost:18082/ready | python3 -m json.tool
```

#### Rollback
```bash
git -C /root/WEALTH log --oneline -5
# Redeploy via: make deploy-local in /root/WEALTH (if GHCR configured)
# Or restart service to pick up last deployed image
systemctl restart wealth-organ
```

---

### 4. WELL

| Field | Value |
|-------|-------|
| Repo | `/root/WELL` |
| Service | `well.service` |
| Port | 18083 |

#### Restart
```bash
systemctl restart well
```

#### Verify
```bash
curl -s http://localhost:18083/health | python3 -m json.tool
```

#### Note
WELL state is **RED** (stale ~703h). Sovereign biometric injection required via `well_log_state` tool or direct `state.json` update at `/root/WELL/state.json`.

---

### 5. GEOX

| Field | Value |
|-------|-------|
| Repo | `/root/geox` |
| Service | `geox-mcp.service` |
| Port | 8081 |

#### Restart
```bash
systemctl restart geox-mcp
```

#### Verify
```bash
curl -s http://localhost:8081/health | python3 -m json.tool
curl -s http://localhost:8081/.well-known/mcp/server.json | python3 -m json.tool
```

---

### 6. A-FORGE

| Field | Value |
|-------|-------|
| Repo | `/root/A-FORGE` |
| Service | `a-forge.service` |
| Port | 7071 |

#### Restart
```bash
systemctl restart a-forge
```

#### Verify
```bash
curl -s http://localhost:7071/health | python3 -m json.tool
```

---

## OBSERVABILITY STACK

### Prometheus

| Field | Value |
|-------|-------|
| Service | `prometheus.service` |
| Port | 9090 |
| Targets | arifOS, A-FORGE, Graphiti, NATS, Node Exporter, Prometheus self |

#### Restart
```bash
systemctl restart prometheus
```

#### Verify
```bash
curl -s http://localhost:9090/api/v1/targets | python3 -m json.tool | grep -c '"health":"up"'
# Expected: 6
```

---

### Grafana

| Field | Value |
|-------|-------|
| Service | `grafana-server.service` |
| Port | 3000 |

#### Restart
```bash
systemctl restart grafana-server
```

#### Verify
```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/api/health
# Expected: 200
```

---

### Node Exporter

| Field | Value |
|-------|-------|
| Service | `node_exporter.service` |
| Port | 9100 |

#### Restart
```bash
systemctl restart node_exporter
```

---

### NATS + JetStream

| Field | Value |
|-------|-------|
| Service | `nats-server.service` |
| Ports | 4222 (client), 8222 (monitoring) |
| JetStream | Enabled (domain=arifos, 256MB mem, 1GB disk) |

#### Verify
```bash
# Server info
nats -s localhost server info

# JetStream domains
nats -s localhost js domains

# Stream list
nats -s localhost js stream list

# Consumer list (arifos-governance)
nats -s localhost js consumer list arifos-governance
```

#### Restart
```bash
systemctl restart nats-server
```

---

### arifOS NATS Heartbeat Publisher

Publishes organ heartbeats to NATS every 60s.

| Field | Value |
|-------|-------|
| Service | `arifOS-NATS-heartbeat.service` |
| Script | `/opt/arifos/app/arifOS-NATS-heartbeat.py` |

#### Restart
```bash
systemctl restart arifOS-NATS-heartbeat
```

#### Verify
```bash
# Check journal
journalctl -u arifOS-NATS-heartbeat -n 20 --no-pager
```

---

### NATS Prometheus Exporter

Exposes NATS metrics on port 9222 for Prometheus scraping.

| Field | Value |
|-------|-------|
| Service | `nats-prometheus-exporter.service` |
| Port | 9222 |
| Script | `/opt/arifos/app/nats_prometheus_exporter.py` |

#### Restart
```bash
systemctl restart nats-prometheus-exporter
```

---

## AGENTS & GATEWAYS

### Hermes ASI (Telegram)

| Field | Value |
|-------|-------|
| Service | `hermes-asi-gateway.service` |
| Bot | @ASI_arifos_bot |
| Config | `/root/HERMES/config.yaml` |
| SOUL | `~/.hermes/SOUL.md` |

#### Restart
```bash
systemctl restart hermes-asi-gateway
```

#### Verify
```bash
journalctl -u hermes-asi-gateway -n 10 --no-pager
```

---

### Hermes A2A Bridge

| Field | Value |
|-------|-------|
| Service | `hermes-a2a.service` |
| Port | 18001 |

#### Restart
```bash
systemctl restart hermes-a2a
```

---

### OpenClaw Gateway

| Field | Value |
|-------|-------|
| Service | `openclaw-gateway.service` |
| Port | 18789 |
| Agent Card | `http://localhost:18789/.well-known/agent-card.json` |

#### Restart
```bash
systemctl restart openclaw-gateway
```

#### Verify
```bash
curl -s http://localhost:18789/health | python3 -m json.tool
curl -s http://localhost:18789/.well-known/agent-card.json | python3 -m json.tool
```

---

### cn-organ (Continue CLI Gateway)

| Field | Value |
|-------|-------|
| Service | `cn-organ.service` |
| Port | 18795 |
| Agent Card | `http://localhost:18795/.well-known/agent-card.json` |

#### Restart
```bash
systemctl restart cn-organ
```

#### Verify
```bash
curl -s http://localhost:18795/health | python3 -m json.tool
curl -s http://localhost:18795/.well-known/agent-card.json | python3 -m json.tool
```

---

### APEX Prime (888 JUDGE)

| Field | Value |
|-------|-------|
| Service | `apex-prime.service` |
| Port | 3002 |

#### Restart
```bash
systemctl restart apex-prime
```

#### Verify
```bash
curl -s http://localhost:3002/health | python3 -m json.tool
```

---

### vault999-api

| Field | Value |
|-------|-------|
| Service | `vault999-api.service` (or via Caddy at vault999.arif-fazil.com) |
| Port | 8100 |

#### Restart
```bash
systemctl restart vault999-api
# or if managed by Python supervisor:
pkill -f vault999-api; sleep 1; nohup python3 /opt/arifOS/vault999-api.py &
```

#### Verify
```bash
curl -s http://localhost:8100/health | python3 -m json.tool
```

---

### vault999-writer

| Field | Value |
|-------|-------|
| Service | `vault999-writer.service` (internal write API) |
| Port | 5001 |
| Note | Internal only — not exposed via Caddy |

#### Restart
```bash
systemctl restart vault999-writer
# or if managed by Python supervisor:
pkill -f vault999-writer; sleep 1; nohup python3 /opt/arifOS/vault999-writer.py &
```

#### Verify
```bash
curl -s http://localhost:5001/health | python3 -m json.tool
```

---

## DOCKER SERVICES (Supporting Only)

Core federation is **bare-metal systemd**. Docker runs only supporting services:

### Restart Docker services
```bash
# All at once
docker ps --format "{{.Names}}" | xargs -I{} docker restart {}

# Individual
docker restart falkordb
docker restart postgres
docker restart redis
docker restart qdrant
docker restart temporal
docker restart temporal-ui
```

### Verify Docker services
```bash
docker ps --format "{{.Names}}\t{{.Status}}"

# postgres
docker exec postgres pg_isready -U arifos_admin

# redis
docker exec redis redis-cli ping

# qdrant
curl -s http://localhost:6333/healthz

# falkordb (Graphiti L5 backend)
curl -s http://localhost:8000/health

# temporal
curl -s http://localhost:7233/health | python3 -m json.tool
```

---

## FULL FEDERATION HEALTH CHECK

Run all verifications in one shot:

```bash
#!/bin/bash
set -e

echo "=== arifOS ==="
curl -s http://localhost:8088/health | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Status: {d[\"status\"]} | Drift: {d.get(\"runtime_drift\",\"?\")} | Tools: {d.get(\"tools_loaded\",\"?\")}')"

echo "=== arifosd ==="
curl -s http://localhost:18081/health | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Daemon up: {d[\"daemon_up\"]} | Uptime: {d.get(\"uptime_seconds\",\"?\")}s')"

echo "=== WEALTH ==="
curl -s http://localhost:18082/health | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Status: {d[\"status\"]} | Tools: {d.get(\"public_surface_count\",\"?\")}')"

echo "=== WELL ==="
curl -s http://localhost:18083/health | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Verdict: {d[\"verdict\"]} | State age: {d.get(\"state_age_hours\",\"?\")}h | Freshness: {d[\"freshness\"][\"status\"]}')"

echo "=== GEOX ==="
curl -s http://localhost:8081/health | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Status: {d[\"status\"]} | Registry: {d[\"registry_truth\"]}')"

echo "=== A-FORGE ==="
curl -s http://localhost:7071/health | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'OK: {d[\"ok\"]} | Service: {d[\"service\"]}')"

echo "=== AAA a2a ==="
curl -s http://localhost:3001/health | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'OK: {d.get(\"ok\",\"?\")} | Vault: {d.get(\"vault\",\"?\")}')"

echo "=== OpenClaw ==="
curl -s http://localhost:18789/health | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'OK: {d.get(\"ok\",\"?\")}')"

echo "=== cn-organ ==="
curl -s http://localhost:18795/health | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'OK: {d.get(\"ok\",\"?\")}')"

echo "=== APEX Prime ==="
curl -s http://localhost:3002/health | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'OK: {d.get(\"ok\",\"?\")}')"

echo "=== vault999-api ==="
curl -s http://localhost:8100/health | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'OK: {d.get(\"ok\",\"?\")} | Vault: {d.get(\"vault\",\"?\")}')"

echo "=== vault999-writer ==="
curl -s http://localhost:5001/health | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Seals: {d.get(\"vault_seals_count\",\"?\")} | Chain: {d.get(\"chain_height\",\"?\")} | Pending: {d.get(\"pending_holds\",\"?\")}')"

echo "=== Hermes A2A ==="
curl -s http://localhost:18001/health | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'OK: {d.get(\"ok\",\"?\")}')" || echo "Hermes A2A: no /health endpoint (A2A bridge)"

echo "=== Prometheus ==="
curl -s http://localhost:9090/api/v1/targets | python3 -c "import sys,json; d=json.load(sys.stdin); ups=[t for t in d['data']['activeTargets'] if t['health']=='up']; print(f'Up: {len(ups)}/6')"

echo "=== NATS ==="
nats -s localhost server info 2>/dev/null | head -5 || echo "NATS: FAIL"

echo "=== Grafana ==="
curl -s -o /dev/null -w "HTTP %{http_code}" http://localhost:3000/api/health

echo ""
echo "=== Done ==="
```

---

## PUBLIC MCP ENDPOINT VERIFICATION

Verify the 4 federation MCP surfaces from the public internet:

```bash
#!/bin/bash
set -e

echo "=== arifOS MCP (Tunnel) ==="
curl -sS --max-time 10 -X POST https://arifos.arif-fazil.com/mcp \
  -H 'Content-Type: application/json' -H 'Accept: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"probe","version":"1.0"}}}' \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'OK: {d[\"result\"][\"serverInfo\"][\"name\"]}')

echo "=== GEOX MCP ==="
curl -sS --max-time 10 -X POST https://geox.arif-fazil.com/mcp \
  -H 'Content-Type: application/json' -H 'Accept: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"probe","version":"1.0"}}}' \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'OK: {d[\"result\"][\"serverInfo\"][\"name\"]}')

echo "=== WEALTH MCP ==="
curl -sS --max-time 10 -X POST https://wealth.arif-fazil.com/mcp \
  -H 'Content-Type: application/json' -H 'Accept: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"probe","version":"1.0"}}}' \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'OK: {d[\"result\"][\"serverInfo\"][\"name\"]}')

echo "=== WELL MCP ==="
curl -sS --max-time 10 -X POST https://well.arif-fazil.com/mcp \
  -H 'Content-Type: application/json' -H 'Accept: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"probe","version":"1.0"}}}' \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'OK: {d[\"result\"][\"serverInfo\"][\"name\"]}')

echo "=== Done ==="
```

**Expected:** All 4 return `OK: <server name>`.

**Expected behavior on raw HTTP probes (without proper JSON-RPC `initialize` payload):**
| Endpoint | Expected status | Why |
|----------|-----------------|-----|
| `https://arifos.arif-fazil.com/mcp` | `406 Not Acceptable` | arifOS MCP enforces JSON-RPC over POST; raw GET/POST without `Accept: application/json` returns 406 |
| `https://geox.arif-fazil.com/mcp` | `307 Temporary Redirect` → `/mcp/` | Caddy rewrites `/mcp` → `/mcp/` (FastMCP serves at trailing slash). Follow the redirect. |
| `https://wealth.arif-fazil.com/mcp` | `200 OK` | Standard FastMCP — accepts POST JSON-RPC |
| `https://well.arif-fazil.com/mcp` | `200 OK` | Standard FastMCP — accepts POST JSON-RPC |
| `https://aaa.arif-fazil.com/mcp` (A2A) | `405 Method Not Allowed` | AAA is A2A protocol, not MCP JSON-RPC; use A2A envelope |

**Spec-correct behavior (per [MCP Streamable HTTP transport](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports)):**

For all 4 organs (arifOS, GEOX, WEALTH, WELL), the MCP endpoint must respond per spec:

| HTTP Method | Headers | Expected Response | Status |
|-------------|---------|-------------------|--------|
| `POST /mcp` | `Content-Type: application/json`, `Accept: application/json, text/event-stream` | 200 (JSON or SSE) | ✓ All 4 organs |
| `POST /mcp` | `Content-Type: application/json` (no Accept) | Server's choice — may be 200 (permissive) or 406 (strict). arifOS returns 406 (strict); others 200. | ✓ spec-compliant |
| `GET /mcp` | `Accept: text/event-stream` | 200 (SSE stream) OR 405 (no SSE offered) | ✓ arifOS/GEOX/WELL=405, WEALTH=200 (informational JSON) |
| `GET /mcp` | (no Accept) | 405 Method Not Allowed | ✓ arifOS/GEOX/WELL. WEALTH returns 200 (informational) — minor deviation |
| `Origin: <untrusted>` | any | 403 Forbidden (DNS rebinding protection per SEP-2243) | ✓ All 4 organs |

**Note (arifOS source has been updated 2026-06-06):**
The arifOS live build returns `400` (with JSON-RPC "Missing session ID" error) on GET instead of the spec-correct 405. This is because the live runtime was deployed before the spec-compliance patch landed. **Source fix in commit `7facaeff` (applied 2026-06-06)**; live arifOS will return 405 after the next image rebuild + redeploy (F13 territory — see "Production deployment without verified build + test pass" in `AGENTS.md`).

**Common failures (real outages, not expected behavior above):**
- `arifOS` 522 → Cloudflare Tunnel down; check `systemctl status cloudflared`
- `GEOX` 307 followed by 5xx → Caddy rewrite broken; verify Caddyfile has `rewrite * /mcp/` in the `/mcp` handle block
- `WEALTH`/`WELL` timeout → organ service down; check `systemctl status wealth-organ` / `systemctl status well`
- `Origin` 403 on `/mcp*` → expected; non-matching origin blocked by `OriginValidationMiddleware`. Use matching `Origin: https://<subdomain>.arif-fazil.com` or call from Tunnel.

---

## QUICK DIAGNOSTIC — Common Failures

### Service won't start
```bash
# Check why
systemctl status <service> --no-pager -l
journalctl -u <service> -n 50 --no-pager

# Common fixes
systemctl daemon-reload
systemctl restart <service>
```

### Runtime drift (arifOS)
```bash
# Check which commits differ
curl -s http://localhost:8088/health | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Build: {d.get(\"build_commit\",\"?\")} | Live: {d.get(\"live_commit\",\"?\")}')"

# Redeploy arifOS (push commit → GHCR → restart)
# Or sync runtime: systemctl restart arifos
```

### WELL stale state
```bash
# WELL health shows RED — state.json needs sovereign injection
curl -s http://localhost:18083/health | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'State age: {d.get(\"state_age_hours\",0):.1f}h')"
# Arif must update /root/WELL/state.json or call well_log_state tool
```

### JetStream missing streams
```bash
nats -s localhost js stream list
# If empty: check /etc/nats-server.conf has JetStream enabled
# Then: systemctl restart nats-server
```

### Prometheus targets down
```bash
curl -s http://localhost:9090/api/v1/targets | python3 -m json.tool | grep '"health":"up"'
# If < 6: check individual service is running + port is correct
# If NATS target down: systemctl restart nats-prometheus-exporter
```

---

## DEPLOY CONSTITUTION (for systemd services)

### Git-first rule
All production changes must be committed and pushed to `origin/main` before deploying.

### arifOS deploy
```bash
cd /root/arifOS
git log --oneline -3  # confirm clean
# Edit version in Makefile or deploy script, then:
make deploy-local   # or equivalent GHCR push + restart
systemctl restart arifos
curl -s http://localhost:8088/health | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Build: {d[\"build_commit\"]} | Live: {d[\"live_commit\"]}')"
```

### Rollback (any systemd service)
```bash
git -C /root/<repo> log --oneline -5
git -C /root/<repo> revert HEAD --no-edit
git -C /root/<repo> push origin main
# Redeploy
systemctl restart <service>
```

### Rollback (arifOS specifically)
Since arifOS deploys from GHCR, rollback to a previous image:
```bash
# Find previous image tag from git history
git -C /root/arifOS log --oneline

# Edit the image tag in the systemd unit override
systemctl edit arifos --full   # change ghcr.io/ariffazil/arifos:<sha>
systemctl daemon-reload
systemctl restart arifos
```

---

## EMERGENCY CONTACTS / REFERENCES

| Doc | Path |
|-----|------|
| VPS Map | `/root/VPS_MAP.md` |
| Federation Manifest | `https://arifos.arif-fazil.com/federation-manifest.json` |
| AGENTS.md | `/root/AGENTS.md` |
| arifOS AGENTS.md | `/root/arifOS/AGENTS.md` |
| CONTEXT.md | `/root/CONTEXT.md` |
| Secrets | `/root/.secrets/all-secrets.md` |

---

*DITEMPA BUKAN DIBERI — Forged, Not Given*
*999 SEAL | arifOS Federation Runbook | 2026-05-29*
