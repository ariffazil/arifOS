<!-- SOT-MANIFEST
owner: Arif
last_verified: 2026-05-19
valid_from: 2026-05-19
valid_until: 2026-06-19
confidence: medium
scope: /root
-->

# Runbook — arifOS Federation

> **Purpose**: Restart, verify, rollback, and **deploy** per organ without guesswork.
> **Last updated**: 2026-05-12 by OpenCode.
> **Sovereign law**: `F1–F13` active at `/root` — all agents are governed.

---

---

## DEPLOY CONSTITUTION — F1–F13

This is **binding law** for the arifOS Federation deployment. Every agent, human, or automation that deploys a container to this VPS **must** follow this flow. Any deviation is a floor breach.

### The Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         DEPLOY CYCLE                           │
│                                                                 │
│  1. CODE   → commit to local git                                │
│  2. PUSH   → git push origin main                               │
│  3. BUILD  → make deploy-local                                  │
│  4. PULL   → (handled by deploy-local via docker compose up)    │
│  5. VERIFY → curl health + git SHA assertion                    │
│  6. SEAL   → git tag vYYYY.MM.DD (optional, for release)        │
│                                                                 │
│  ⚠️ make deploy-local ENFORCES:                                  │
│     - HOLD if local HEAD ≠ origin/main (forces push first)      │
│     - Builds + tags GHCR image with current SHA                 │
│     - Restarts compose container                                │
│     - Verifies git_commit matches expected SHA                  │
└─────────────────────────────────────────────────────────────────┘
```

### Law 1: Canonical Source of Truth

`/root/arifOS/deploy/docker-compose.yml` is the **single canonical deploy manifest**. The running compose at `/root/compose/docker-compose.yml` **must** match its image tags and configuration. Any gap is a drift signal that requires reconciliation within one deploy cycle.

### Law 2: No Deploy Without Push

No container is deployed unless its git commit **exists on `origin/main`**. `make deploy-local` enforces this: it fetches origin and holds if local HEAD diverges.

### Law 3: Tag Is Commit

Every Docker image tag pushed to GHCR **must be a valid git commit SHA** (short, 7 chars). `:latest` is a convenience alias for the most recent deploy, not a deployment target.

### Law 4: Deployer Is Sealer

The agent or human who deploys is responsible for:
  (a) pushing the code first
  (b) running the deploy
  (c) verifying the health endpoint returns the correct SHA
  (d) logging the deploy in the organ's `CHANGELOG.md`

### Law 5: Rollback Is a Git Revert

If a deploy fails health check, rollback is:
  1. `git revert HEAD --no-edit`
  2. `git push origin main`
  3. `make deploy-local`

No hot-patching containers by copying files. No `docker exec` edits. If it's not in git, it doesn't exist.

### Law 6: Stale Image Tags Are Forbidden

The canonical `deploy/docker-compose.yml` **must** reference the same tag that the runtime `/root/compose/docker-compose.yml` references. If someone pushes code but does not update the tag in the deploy manifest, the next deploy cycle **must** reconcile it. This is not optional.

### Enforcement

| Check | Where | What triggers |
|-------|-------|---------------|
| Local HEAD = origin/main | `make deploy-local` | HOLD + exit 1 |
| Health SHA matches | `make deploy-local` | HOLD + exit 1 |
| SOT drift detector | `/inspector/sot` endpoint | Dashboard warning |
| Deploy manifest vs runtime | Manual `diff` audit | Weekly in `CONTEXT.md` |

### Violation Protocol

If a container is running a commit NOT on `origin/main`:
1. **Immediate**: Log the incident with commit SHA + deployer identity.
2. **Within 1 hour**: Either push the missing commit, or roll back to a known-good tag.
3. **Seal**: Write the incident to `VAULT999/outcomes.jsonl` with severity `DEPLOY_DRIFT`.

---

## Global Commands

```bash
# All commands assume you are at /root
cd /root/compose

# View all service status
docker compose ps

# View logs for a service
docker compose logs -f <service>

# Full stack restart (USE WITH CAUTION)
docker compose restart

# Full stack down/up
docker compose down && docker compose up -d
```

---

## 1. arifOS Kernel

| Field | Value |
|-------|-------|
| Repo | `/root/arifOS` |
| Compose service | `arifosmcp` |
| Container | `arifosmcp` |

### Restart
```bash
cd /root/compose && docker compose restart arifosmcp
```

### Verify (do all)
```bash
# 1. Health
curl -s https://arifos.arif-fazil.com/health | python3 -m json.tool

# 2. Tool registry
curl -s https://arifos.arif-fazil.com/tools | python3 -m json.tool

# 3. Build info (SHA anchor)
curl -s https://arifos.arif-fazil.com/api/build-info | python3 -m json.tool

# 4. SOT drift detector
curl -s https://arifos.arif-fazil.com/inspector/sot | python3 -m json.tool
# Expected: {"verdict":"SEAL","live_count":13,"main_count":13}

# 5. MCP discovery
curl -s https://arifos.arif-fazil.com/.well-known/mcp/server.json | python3 -m json.tool

# 6. Inspector console (HTML)
curl -s https://arifos.arif-fazil.com/webmcp | grep -c "sot-bar"
# Expected: 1 or more

# 7. Observatory (frontend)
curl -s https://arifos.arif-fazil.com/ | grep -c "arifOS Observatory"
# Expected: 1
```

### Rollback (backend code)
If new `rest_routes.py` causes failure:
```bash
# Restore from backup
cp /root/arifOS/arifosmcp/runtime/rest_routes.py.bak.20260503114925 \
   /root/arifOS/arifosmcp/runtime/rest_routes.py

# Also copy into container runtime path
docker cp /root/arifOS/arifosmcp/runtime/rest_routes.py \
          arifosmcp:/app/arifosmcp/runtime/rest_routes.py

# Restart
cd /root/compose && docker compose restart arifosmcp
```

### Rollback (frontend)
```bash
cp /var/www/html/arifos/index.html.bak.20260503114925 \
   /var/www/html/arifos/index.html
# OR
cp /root/sites/arifos/index.html.bak.20260503114925 \
   /root/sites/arifos/index.html
```

---

## 2. GEOX

| Field | Value |
|-------|-------|
| Repo | `/root/geox` |
| Compose service | `geox` |
| Container | `geox_eic` |

### Restart
```bash
cd /root/compose && docker compose restart geox
```

### Verify
```bash
# Health
curl -s https://geox.arif-fazil.com/health

# MCP discovery
curl -s https://geox.arif-fazil.com/.well-known/mcp/server.json | python3 -m json.tool
```

---

## 3. WEALTH

| Field | Value |
|-------|-------|
| Repo | `/root/WEALTH` |
| Compose service | `wealth-organ` |
| Container | `wealth-organ` |

### Restart
```bash
cd /root/compose && docker compose restart wealth-organ
```

### Verify
```bash
# Health
curl -s https://wealth.arif-fazil.com/health

# Ready
curl -s https://wealth.arif-fazil.com/ready

# MCP discovery
curl -s https://wealth.arif-fazil.com/.well-known/mcp/server.json | python3 -m json.tool
```

---

> ⚠️ TEMPORAL NOTE: `well` service was removed as of 2026-04-26.
> Any step referencing `well` is tombstoned below and must not be executed.

## 4. WELL

| Field | Value |
|-------|-------|

### Restart
```bash
```

### Verify
```bash
# Health

# MCP discovery
curl -s https://well.arif-fazil.com/.well-known/mcp/server.json | python3 -m json.tool
```

---

## 5. AAA

| Field | Value |
|-------|-------|
| Repo | `/root/AAA` |
| Compose services | `aaa`, `aaa-a2a` |
| Containers | `aaa-a2a`, `apex-prime` |

### Restart
```bash
cd /root/compose && docker compose restart aaa-a2a
# Note: 'aaa' service may not be running; check with docker compose ps
```

### Verify
```bash
# A2A endpoint
curl -s https://aaa.arif-fazil.com/a2a

# Health (if exposed)
curl -s https://aaa.arif-fazil.com/health
```

---

## 6. A-FORGE Bridge

| Field | Value |
|-------|-------|
| Repo | `/root/A-FORGE` |
| Container | `af-bridge-prod` |

### Restart
```bash
docker restart af-bridge-prod
# Note: Not in main compose services list. May be from separate stack.
```

### Verify
```bash
# Internal health (port 7071, not exposed publicly by default)
curl -s http://localhost:7071/health
```

---

## 7. Infrastructure Services

### Caddy (Reverse Proxy)
```bash
# Restart
cd /root/compose && docker compose restart caddy

# Verify
curl -s -o /dev/null -w "%{http_code}" https://arifos.arif-fazil.com/health
# Expected: 200
```

### Postgres
```bash
# Restart
cd /root/compose && docker compose restart postgres

# Verify
cd /root/compose && docker compose exec postgres pg_isready -U arifos_admin
```

### Redis
```bash
# Restart
cd /root/compose && docker compose restart redis

# Verify
cd /root/compose && docker compose exec redis redis-cli ping
# Expected: PONG
```

### Qdrant
```bash
# Restart
cd /root/compose && docker compose restart qdrant

# Verify
curl -s http://localhost:6333/healthz
```

---

## 8. Quick Diagnostic Script

Save this as `/root/diag.sh` and run after any restart:

```bash
#!/bin/bash
set -e

echo "=== arifOS ==="
curl -s https://arifos.arif-fazil.com/health | jq -r '.status' || echo "FAIL"
curl -s https://arifos.arif-fazil.com/api/build-info | jq -r '.short_sha' || echo "FAIL"
curl -s https://arifos.arif-fazil.com/inspector/sot | jq -r '.verdict' || echo "FAIL"

echo "=== GEOX ==="
curl -s -o /dev/null -w "%{http_code}" https://geox.arif-fazil.com/health || echo "FAIL"

echo "=== WEALTH ==="
curl -s -o /dev/null -w "%{http_code}" https://wealth.arif-fazil.com/health || echo "FAIL"

echo "=== WELL ==="
# [TEMPORAL-GHOST — well removed 2026-04-26 per AGENTS.md]
# curl -s -o /dev/null -w "%{http_code}" https://well.arif-fazil.com/health || echo "FAIL"

echo "=== Done ==="
```

Make executable:
```bash
chmod +x /root/diag.sh
```

---

## 9. Emergency Contacts / References

| Doc | Path |
|-----|------|
| VPS Map | `/root/VPS_MAP.md` |
| Docker Volume Audit | `/root/DOCKER_VOLUME_AUDIT.md` |
| Federation Manifest | `https://arifos.arif-fazil.com/federation-manifest.json` |
| AGENTS.md (workspace rules) | `/root/AGENTS.md` |
| arifOS AGENTS.md | `/root/arifOS/AGENTS.md` |
