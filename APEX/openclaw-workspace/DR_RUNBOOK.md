# DR Runbook — arifOS_bot Disaster Recovery
**Version:** 2026.03.07
**Agent:** arifOS_bot | **Authority:** Muhammad Arif bin Fazil (F13)

> F1 (Amanah / Reversibility): DR is a reversible operation. Restore, verify, then proceed.
> Never destroy old state before new state is confirmed healthy.

---

## Scenario A — openclaw_gateway container killed/crashed

### Symptoms
- Telegram bot @arifOS_bot not responding
- `docker ps` shows `openclaw_gateway` as `Exited` or `Restarting`

### Recovery (< 2 minutes)
```bash
# 1. Check why it died
docker logs openclaw_gateway --tail 50

# 2. Restart from compose
cd /srv/arifOS
docker compose restart openclaw

# 3. Wait for healthy
watch -n2 "docker inspect --format='{{.State.Health.Status}}' openclaw_gateway"

# 4. Verify Telegram bot online
# Send /start to @arifOS_bot — should respond within 30 seconds
```

### If compose file lost
```bash
# Pull from git
git pull origin main
docker compose up -d openclaw
```

---

## Scenario B — Full VPS wipe / migration to new server

### Prerequisites
- New VPS with Ubuntu 24.04+, Docker, Docker Compose
- Access to: `https://github.com/ariffazil/arifOS` (main repo)
- Access to: `https://github.com/ariffazil/openclaw-workspace` (workspace backup)
- All API keys (store in Bitwarden/password manager — NOT in git)

### Step 1 — Clone repos
```bash
cd /srv && git clone git@github.com:ariffazil/arifOS.git arifOS
mkdir -p /opt/arifos/data/openclaw
cd /opt/arifos/data/openclaw
git clone https://github.com/ariffazil/openclaw-workspace.git workspace
```

### Step 2 — Restore .env secrets
```bash
# These are NOT in git. Restore manually from password manager:
cp /path/to/backup/.env /srv/arifOS/.env
# Required keys: KIMI_API_KEY, ANTHROPIC_API_KEY, OPENROUTER_API_KEY,
# VENICE_API_KEY, FIRECRAWL_API_KEY, GH_TOKEN, BROWSERLESS_URL, OLLAMA_URL,
# REDIS_URL, OPENCLAW_GATEWAY_TOKEN, OPENCLAW_GATEWAY_AUTH_TOKEN
```

### Step 3 — Restore openclaw.json
```bash
# openclaw.json is NOT in workspace git (contains auth token).
# Restore from the backup copy or recreate from template:
# Template: see docs/VPS_ARCHITECTURE_MASTER_DOSSIER.md → openclaw.json reference
# CRITICAL keys to set:
#   gateway.auth.token = your gateway token
#   hooks.token = distinct value (must NOT match gateway.auth.token)
#   models.providers.*.apiKey = ${ENV_VAR} references
```

### Step 4 — Restore Postgres (if backed up)
```bash
# Start postgres first
docker compose -f /srv/arifOS/docker-compose.yml up -d arifos-postgres

# Wait for healthy
sleep 10

# Restore from backup (if 5A backup exists)
gunzip -c /backup/pg_YYYYMMDD.sql.gz | docker exec -i arifos-postgres psql -U postgres
```

### Step 5 — Restore Qdrant vectors (if backed up)
```bash
docker compose -f /srv/arifOS/docker-compose.yml up -d qdrant_memory
sleep 10
# Restore snapshot if available:
# curl -X POST http://localhost:6333/collections/arifos/snapshots/recover \
#   -d '{"location": "file:///backups/arifos-snapshot"}'
```

### Step 6 — Pull Ollama models
```bash
docker compose -f /srv/arifOS/docker-compose.yml up -d ollama_engine
docker exec ollama_engine ollama pull qwen2.5:3b    # Fast (1.9GB)
docker exec ollama_engine ollama pull bge-m3         # Embeddings (1.2GB)
docker exec ollama_engine ollama pull nomic-embed-text  # Embeddings (274MB)
# Optional (9GB, needs 12GB RAM under load):
# docker exec ollama_engine ollama pull qwen2.5:14b
```

### Step 7 — Start full stack
```bash
cd /srv/arifOS
docker compose up -d
docker compose -f docker-compose.phase1.yml up -d
sleep 30
docker ps --format "table {{.Names}}\t{{.Status}}"
```

### Step 8 — Verify arifOS_bot
```bash
curl -sf http://localhost:8080/health | jq
# Expected: {"status":"healthy","tools_loaded":13}
# Then test Telegram: send /start to @arifOS_bot
```

---

## Scenario C — OpenClaw auth token lost / gateway locked

### Recovery
```bash
# 1. Stop container
docker compose stop openclaw

# 2. Edit openclaw.json
sudo nano /opt/arifos/data/openclaw/openclaw.json
# Update: gateway.auth.token = new_token
# Update: hooks.token = different_new_token (must not match auth token)

# 3. Restart
docker compose up -d openclaw

# 4. Update any clients using old token (claude.ai MCP config, etc.)
```

---

## Scenario D — Workspace files lost (skills, SPEC.md, etc.)

### Recovery
```bash
# Workspace is backed up nightly to GitHub
cd /opt/arifos/data/openclaw
rm -rf workspace
git clone https://github.com/ariffazil/openclaw-workspace.git workspace
chown -R ubuntu:docker workspace  # adjust owner as needed

# Restart openclaw to pick up restored workspace
docker compose restart openclaw
```

---

## Scenario E — Disk full (>95%)

```bash
# Emergency cleanup sequence (F1: all reversible)
docker builder prune -f              # Build cache (usually 10–50GB)
docker image prune -f                # Dangling images
docker container prune -f            # Stopped containers

# If still full — check Ollama models
docker exec ollama_engine ollama list
# Remove the largest model NOT needed for daily ops:
# docker exec ollama_engine ollama rm qwen2.5:14b  # Frees 9GB

# Check logs
du -sh /opt/arifos/data/openclaw/logs/ /var/log/
journalctl --vacuum-size=500M
```

---

## Key Files Reference

| File | Path | In Git? | Notes |
|------|------|---------|-------|
| docker-compose.yml | `/srv/arifOS/docker-compose.yml` | YES | Main compose |
| .env (secrets) | `/srv/arifOS/.env` | NO | Manual backup required |
| openclaw.json | `/opt/arifos/data/openclaw/openclaw.json` | NO | Manual backup required |
| Workspace (skills/docs) | `/opt/arifos/data/openclaw/workspace/` | YES | GitHub: openclaw-workspace |
| arifOS repo | `/srv/arifOS/` | YES | GitHub: ariffazil/arifOS |
| VAULT999 ledger | `/srv/arifOS/VAULT999/vault999.jsonl` | YES (force-tracked) | Constitutional audit log |
| Postgres data | Docker volume `arifos_postgres_data` | NO | Phase 5A backup pending |
| Qdrant data | Docker volume `arifos_qdrant_storage` | NO | Phase 5A backup pending |

---

*arifOS_bot DR Runbook — DITEMPA BUKAN DIBERI*
