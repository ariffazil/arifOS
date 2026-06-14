# Federation Agent Inventory — arifOS / AAA

> **Sealed:** 2026-05-25T05:43Z  
> **Scope:** All agent-like services, repos, runtimes, domains, endpoints on the VPS  
> **Purpose:** Canonical map before implementing identity tasks (identity.toml, /identity endpoint, /health identity_hash, Vault999 boot attestation, /.well-known/agent-card.json)

---

## 1. EXECUTIVE SUMMARY

| Node | Port | Systemd Unit | Status | Commit | Identity Claim | Agent-Card |
|------|------|--------------|--------|--------|----------------|------------|
| **arifOS** | 8088 | `arifos.service` | ✅ active | `341ccc6` | "arifOS-mcp" | ✅ `/root/arifOS/static/agent-card.json` |
| **arifosd** | 18081 | `arifosd.service` | ✅ active | `341ccc6` | "arifOS Constitutional Kernel — arifosd" | ❌ none |
| **A-FORGE** | 7071 | `a-forge.service` | ✅ active | `c4794df` | "A-FORGE-sense" | ❌ none (endpoint advertises `/.well-known/agent-card.json` but not verified) |
| **WEALTH** | 18082 | `wealth-organ.service` | ✅ active | `93f3d7e` | "wealth-mcp" | ✅ `/root/WEALTH/.well-known/agent-card.json` |
| **WELL** | 18083 | `well.service` | ✅ active | `e8e90eb` | "WELL" / "well-mcp" | ✅ `/root/WELL/.well-known/agent-card.json` |
| **Vault999 API** | 8100 | `vault999-api.service` | ✅ active | n/a | "vault_service_v2" | ❌ none |
| **Vault999 Writer** | 5001 | `vault999-writer.service` | ✅ active | n/a | n/a | ❌ none |
| **OpenClaw Gateway** | 18789 | `openclaw-gateway.service`* | ✅ active | n/a | "AAA Gateway" | ✅ `/root/.openclaw/workspace/agent-card.json` |
| **OpenClaw Agent-Card** | 18795 | `openclaw-agent-card.service` | ✅ active | n/a | "AAA Gateway" | ✅ served dynamically |
| **Hermes ASI Gateway** | ??? | `hermes-asi-gateway.service` | ✅ active | n/a | "Hermes" | ❌ none |
| **Webhook Receiver** | 18000 | none | ✅ running | n/a | n/a | ❌ none |
| **Ollama** | 11434 | `ollama.service` | ✅ active | n/a | n/a | n/a |
| **GEOX MCP** | 8081 | `geox-mcp.service` | ✅ active | n/a | n/a | ❌ none |
| **Caddy** | 80/443 | `caddy.service` | ✅ active | n/a | n/a | n/a |

\* `openclaw-gateway.service` is **active but NOT enabled** (will not survive reboot). The enabled unit is `openclaw-agent-card.service` + node process spawned by the secure script.

**Missing / Stale:**
- A-FORGE advertises `/.well-known/agent-card.json` in its contract but the endpoint was not verified (returned 404 on `/`).
- Hermes ASI Gateway has no known TCP listen port (only unix sockets or internal).
- **No `identity.toml` exists anywhere** on the system.

---

## 2. SYSTEMD UNITS (Full Detail)

### Active & Enabled

| Unit | ExecStart | WorkingDirectory | User | EnvFile | Port |
|------|-----------|------------------|------|---------|------|
| `arifos.service` | `/opt/arifos/venv/bin/python -m arifos.main` | `/opt/arifos/app` | `arifos` | `/etc/arifos/arifos.env` + `/etc/arifOS/secrets.env` | 8088 |
| `arifosd.service` | `/usr/bin/python3 /root/arifOS/arifosd.py` | `/root/arifOS` | `root` | — | 18081 |
| `wealth-organ.service` | `/usr/bin/python3 -m internal.monolith` | `/root/WEALTH` | `root` | `PORT=18082`, `PYTHONPATH=/root/WEALTH` | 18082 |
| `well.service` | `/usr/bin/python3 /root/WELL/server.py` | `/root/WELL` | `root` | `PORT=18083`, `ARIFOS_KERNEL_URL=http://localhost:8088`, `WELL_STATE_PATH=/root/WELL/state.json`, `WELL_EVENTS_PATH=/root/WELL/events.jsonl`, `WELL_VAULT_PATH=/root/WELL/vault_ledger.jsonl` | 18083 |
| `a-forge.service` | `/usr/bin/node /root/A-FORGE/dist/src/server.js` | `/root/A-FORGE` | `root` | `NODE_ENV=development`, `AF_FORGE_PORT=7071`, `OLLAMA_BASE_URL=http://localhost:11434`, `AF_FORGE_ENV=development` | 7071 |
| `hermes-asi-gateway.service` | `/usr/local/bin/hermes-gateway-secure.sh` | `/root` | `root` | `/root/AAA/agents/hermes-asi/runtime/.env` | ??? |
| `openclaw-agent-card.service` | `/usr/bin/python3 /opt/arifOS/a2a-adapters/openclaw-agent-card.py` | — | `root` | — | 18795 |
| `vault999-api.service` | `/usr/bin/python3 /root/compose/vault999/server.py` | `/root/compose/vault999` | `root` | `/etc/arifOS/vault999-api.env` | 8100 |
| `vault999-writer.service` | `/usr/bin/python3 /root/compose/vault999-writer/main.py` | `/root/compose/vault999-writer` | `root` | `/etc/arifOS/vault999-api.env` | 5001 |
| `geox-mcp.service` | `python3 -m geox_mcp.server --host 0.0.0.0 --port 8081` | `/root/geox` | `root` | — | 8081 |
| `ollama.service` | `/usr/local/bin/ollama serve` | — | `root` | — | 11434 |
| `caddy.service` | `/usr/bin/caddy run` | — | `root` | — | 80/443 |

### Active but NOT Enabled

| Unit | Notes |
|------|-------|
| `openclaw-gateway.service` | Runs `openclaw-gateway-secure.sh` (port 18789). Will not survive reboot. The node process on 18789 is currently running, but if it dies it won't auto-restart unless this unit is enabled. |

### Disabled / Stale Units (exist on disk, not active)

| Unit | Reason |
|------|--------|
| `openclaw-a2a.service` | **Removed** in prior hardening (NameError: PORT). Unit file deleted. |
| `arifos-geox-sot.service` | Unknown purpose, not active. |
| `arifos-mcp.service` | Likely legacy alias for `arifos.service`. |
| `arifos-sense.service` | Legacy. |
| `arifos-webhook.service` | Legacy. |
| `arif-heartbeat.service` | Legacy. |
| `arif-agent-worker.service` | Legacy. |
| `arifos-command-center.service` | Legacy. |
| `arifosmcp-network-heal.service` | One-shot heal script. |

---

## 3. NETWORK SURFACE

### Listening TCP Ports

| Port | Process | PID | Bound To | Identity |
|------|---------|-----|----------|----------|
| 80 | caddy | 1136 | 0.0.0.0 | Public HTTP |
| 443 | caddy | 1136 | 0.0.0.0 | Public HTTPS |
| 5001 | python3 (vault999-writer) | 986031 | 0.0.0.0 | Vault999 Writer |
| 7071 | node (A-FORGE) | 974317 | 0.0.0.0 | A-FORGE-sense |
| 8081 | python3 (geox-mcp) | 2140946 | 0.0.0.0 | GEOX MCP |
| 8088 | python (arifOS) | 996019 | 0.0.0.0 | arifOS-mcp |
| 8100 | python3 (vault999-api) | 985778 | 0.0.0.0 | vault_service_v2 |
| 8787 | node (OpenClaw) | 804118 | 127.0.0.1 | OpenClaw internal |
| 11434 | ollama | 812466 | 127.0.0.1 | Ollama API |
| 18000 | python3 (webhook-receiver) | 1081 | 127.0.0.1 | Webhook deploy receiver |
| 18081 | python3 (arifosd) | 4117 | 127.0.0.1 | arifosd / GEOX bridge |
| 18082 | python3 (WEALTH) | 460032 | 0.0.0.0 | wealth-mcp |
| 18083 | python3 (WELL) | 974661 | 0.0.0.0 | well-mcp |
| 18789 | node (OpenClaw) | 804118 | 127.0.0.1 | AAA Gateway |
| 18795 | python3 (openclaw-agent-card) | 1086 | 127.0.0.1 | AAA Gateway agent-card |
| 22888 | sshd | 1114 | 0.0.0.0 | SSH |

### Unix Sockets

| Socket | Process | Purpose |
|--------|---------|---------|
| `/run/arifos.sock` | arifosd (PID 4117) | arifosd local control socket |
| `/var/run/caddy-admin.sock` | caddy | Caddy admin API |
| `/var/run/docker.sock` | dockerd | Docker daemon |

---

## 4. CADDY WEB ROUTING — STALE PORT AUDIT

**CRITICAL:** Caddy routes several federation domains to **dead ports**. These were fixed in health manifests but the Caddyfile was never updated.

| Domain | Caddy Routes To | Actual Live Port | Status |
|--------|----------------|------------------|--------|
| `arifos.arif-fazil.com` | `127.0.0.1:8080` | 8088 | **BROKEN** — 404/connection refused |
| `mcp.arif-fazil.com` | `127.0.0.1:8080` | 8088 | **BROKEN** — 404/connection refused |
| `geox.arif-fazil.com` | `127.0.0.1:8081` | 8081 | ✅ WORKING |
| `wealth.arif-fazil.com` | `127.0.0.1:8082` | 18082 | **BROKEN** — 404/connection refused |
| `well.arif-fazil.com` | `127.0.0.1:8083` | 18083 | **BROKEN** — 404/connection refused |
| `arifos.arif-fazil.com` (vault) | `127.0.0.1:50001` | 8100 / 5001 | **BROKEN** — 50001 not listening |
| `*.arif-fazil.com` (apex) | `127.0.0.1:8443` | ??? | **BROKEN** — 8443 not listening |
| `ollama.arif-fazil.com` | `ollama-engine-prod:11434` | 127.0.0.1:11434 | **BROKEN** — DNS name `ollama-engine-prod` does not resolve |
| `aaa.arif-fazil.com` | `127.0.0.1:18789` (OpenClaw) + `127.0.0.1:8787` + `127.0.0.1:18795` | mixed | **PARTIAL** — routes exist but AAA itself has no dedicated runtime; OpenClaw acts as gateway |
| `arif-fazil.com` (webhook) | `127.0.0.1:18000` | 18000 | ✅ WORKING |

**Policy constraint:** Do NOT modify Caddyfile without explicit human approval (Sovereign constraint). Documented here for awareness.

---

## 5. REPOSITORIES

| Repo | Path | Branch | Commit | Dirty | Remote | Language |
|------|------|--------|--------|-------|--------|----------|
| **arifOS** | `/root/arifOS` | `main` | `341ccc6` | dirty | `git@github.com:ariffazil/arifos.git` | Python 3.12+ |
| **A-FORGE** | `/root/A-FORGE` | `main` | `c4794df` | dirty | `git@github.com:ariffazil/A-FORGE.git` | TypeScript 5.8+ |
| **AAA** | `/root/AAA` | `main` | `4311743` | dirty | `git@github.com:ariffazil/AAA.git` | TypeScript 5.9+ / React 19 |
| **geox** | `/root/geox` | `main` | `140e3b8` | dirty | `git@github.com:ariffazil/geox.git` | Python 3.11+ |
| **WEALTH** | `/root/WEALTH` | `main` | `93f3d7e` | dirty | `git@github.com:ariffazil/wealth.git` | Python 3.12+ / Node 22 |
| **WELL** | `/root/WELL` | `main` | `e8e90eb` | dirty | `git@github.com:ariffazil/well.git` | Python 3.12+ |
| **APEX** | `/root/APEX` | `apex` | `6b25863` | clean | **no-remote** | JavaScript (CommonJS) |
| **HERMES** | `/root/HERMES` | — | — | — | **no-git** | Node.js |
| **arif-sites** | `/root/arif-sites` | `main` | `f543a36` | clean | `https://github.com/ariffazil/arif-sites.git` | Shell / React |

**Deployment paths:**
- arifOS deployed to `/opt/arifos/app/` (copied from `/root/arifOS/` at build time)
- All other services run directly from `/root/<repo>/`

---

## 6. EXISTING AGENT-CARD FILES

| File | Service | Name Claim | Version |
|------|---------|------------|---------|
| `/root/arifOS/static/agent-card.json` | arifOS | "arifOS Constitutional MCP Kernel" | `2026.4.13` |
| `/root/WELL/.well-known/agent-card.json` | WELL | "WELL Biological Substrate" | `2026.05.08-REFORGED` |
| `/root/WEALTH/.well-known/agent-card.json` | WEALTH | "WEALTH Capital Intelligence" | `2026.05.01` |
| `/root/.openclaw/workspace/agent-card.json` | OpenClaw/AAA | "AAA Gateway" | `1.0.0` |
| `/root/AAA/dist/.well-known/agent-card.json` | AAA | "AAA Gateway" | `0.1.0` |
| `/root/geox/skills/*/agent-card.json` | GEOX (skills) | various skill names | various |

**Note:** GEOX root-level agent-card is **malformed JSON** (line 49 error). A-FORGE advertises `/.well-known/agent-card.json` but no file was found on disk and the endpoint was not verified.

---

## 7. IDENTITY CLAIMS IN HEALTH ENDPOINTS

### arifOS (`/health` on 8088)
```json
{
  "status": "healthy",
  "service": "arifOS-mcp",
  "version": "kanon-0f88747",
  "git_commit": "0f887477c",
  "git_branch": "main",
  "tools_loaded": 13,
  "floors_active": 13,
  "runtime_drift": false,
  "live_commit": "0f887477c",
  "vault999_health": "healthy"
}
```

### A-FORGE (`/health` on 7071)
```json
{
  "ok": true,
  "service": "A-FORGE-sense",
  "version": "0.1.0"
}
```

### GEOX (`/health` on 8081)
```json
{
  "status": "healthy",
  "registry_truth": "VERIFIED"
}
```

### arifosd (`/health` on 18081)
```json
{
  "status": "ok",
  "daemon_up": true,
  "uptime_seconds": 116967
}
```
*(No explicit identity field; daemon name inferred from codebase.)*

### WEALTH (`/health` on 18082)
```json
{
  "status": "healthy",
  "service": "wealth-mcp",
  "version": "2026.05.02",
  "final_authority": "ARIF"
}
```

### WELL (`/health` on 18083)
```json
{
  "identity": "WELL",
  "role": "Body / Human Intelligence",
  "authority": "REFLECT_ONLY",
  "service": "well-mcp",
  "truth_status": "VERIFIED",
  "freshness_band": "FRESH"
}
```

### Vault999 API (`/health` on 8100)
```json
{
  "status": "healthy",
  "vault": "connected",
  "service": "vault_service_v2"
}
```

---

## 8. MISSING RUNTIMES

### AAA Dedicated Runtime
- **Expected:** AAA A2A Hub on port 3001 (from codebase) or React dev server
- **Actual:** No dedicated AAA runtime. `aaa.arif-fazil.com` is proxied to OpenClaw (18789/8787/18795).
- **Impact:** AAA control plane is static HTML only (built to `/var/www/html/aaa` or similar).

### APEX
- **Expected:** Node.js Express on some port (configurable)
- **Actual:** No APEX process found. Port 8443 (Caddy route) is dead.
- **Impact:** APEX constitutional verdict engine is not running.

---

## 9. IDENTITY FOUNDATION GAPS

| Requirement | Status | Owner |
|-------------|--------|-------|
| `identity.toml` per service | ❌ None exist | All repos |
| `/identity` endpoint | ❌ Not implemented | All repos |
| `/health` includes `identity_hash` | ❌ Not implemented | All repos |
| Vault999 boot attestation | ❌ Not implemented | arifOS |
| `/.well-known/agent-card.json` served live | ⚠️ Partial (some files exist but not served correctly) | All repos |
| Forbidden identity firewall (no Grok/Claude/etc) | ✅ Enforced in code | arifOS |

---

## 10. NEXT STEPS (Identity Tasks)

1. **Create `identity.toml` templates** for each active service (arifOS, arifosd, A-FORGE, WEALTH, WELL, Vault999, OpenClaw).
2. **Add `/identity` REST endpoint** to each runtime that returns canonical identity envelope.
3. **Augment `/health`** with `identity_hash` (BLAKE3 of `identity.toml`).
4. **Vault999 boot attestation** — on service start, write a `BOOT` seal to Vault999 with identity hash + git commit + timestamp.
5. **Fix `/.well-known/agent-card.json`** serving for services that have the file but don't expose it (A-FORGE, Vault999).
6. **Standardize agent-card schema** across all services (currently 3 different schemas: arifOS custom, A2A v1.0.0, AAA v0.3.0).
7. **Fix arifOS runtime drift** — rebuild `arifOS` container to sync `1efd99e` with live `8ac6fbb`.
8. **Caddy reconciliation** — when approved, update all stale reverse_proxy ports.

---

*Document generated by A-FORGE Constitutional Clerk during Forge Agent inventory phase.*
