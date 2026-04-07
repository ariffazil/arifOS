# 🔐 4-Stage Secret Migration Plan for arifosmcp
## From Scattered .env → Layered Unified Vault Architecture

**Authority:** 888_JUDGE | 999_SEAL  
**Status:** TIER 0 COMPLETE → TIER 1 READY  
**HOLD:** Migrate in slices, validate each container

---

## Current State (Post-Tier 0)

✅ **COMPLETE:**
- `/root/.secrets/vault.env` - Canonical master (600 perms, 14 keys)
- `vault` CLI - Human UX layer (set, get, list, export, load, backup)
- Shell auto-export - Keys available on login
- `.env` permissions fixed (644 → 600)
- 14 LLM keys migrated from `.env` to vault

---

## STAGE 1: High-Risk Agent Containers (Priority)
**Target:** `arifosmcp_server`, `agent_zero_reasoner`, `openclaw_gateway`, `civ03_evolution_api`
**Risk:** These are most agent-adjacent (direct LLM/API exposure)

### 1.1 arifosmcp_server
**Current:** Reads from `.env`  
**Target:** Docker Secrets + vault.env bridge

```yaml
# docker-compose.yml addition
services:
  arifosmcp_server:
    secrets:
      - source: arifos_api_key
        target: arifos_api_key
      - source: kimi_api_key
        target: kimi_api_key
    environment:
      # Fallback to env for backward compat during migration
      ARIFOS_API_KEY_FILE: /run/secrets/arifos_api_key
      KIMI_API_KEY_FILE: /run/secrets/kimi_api_key
```

```bash
# One-time setup (888 HOLD: verify before running)
docker swarm init 2>/dev/null || echo "Swarm already initialized"

# Create secrets from vault
cat /root/.secrets/vault.env | grep ARIFOS_API_KEY | cut -d'=' -f2- | docker secret create arifos_api_key -
cat /root/.secrets/vault.env | grep KIMI_API_KEY | cut -d'=' -f2- | docker secret create kimi_api_key -
```

### 1.2 agent_zero_reasoner
**Keys needed:** ANTHROPIC_API_KEY, OPENAI_API_KEY

### 1.3 openclaw_gateway
**Keys needed:** BRAVE_API_KEY, JINA_API_KEY, FIRECRAWL_API_KEY

### 1.4 civ03_evolution_api
**Keys needed:** EVOLUTION_API_KEY

**Validation per container:**
```bash
# After each migration:
docker compose ps <container>        # Check running
docker compose logs <container>      # Check no key errors
curl localhost:<port>/health         # If health endpoint exists
```

---

## STAGE 2: Infrastructure Services
**Target:** `arifos_postgres`, `arifos_redis`, `qdrant`
**Risk:** Database breaches = total compromise

### 2.1 Postgres
Already partially configured in `SECRETS.yml`:
```yaml
secrets:
  postgres_password:
    external: true
```

**Action:**
```bash
# Create if not exists
cat /root/.secrets/vault.env | grep -E "POSTGRES_PASSWORD|DATABASE_URL" | head -1 | cut -d'=' -f2- | \
  docker secret create postgres_password - 2>/dev/null || echo "Secret exists"
```

### 2.2 Redis
Similar pattern - password via Docker secret.

### 2.3 Qdrant
API key already defined in `SECRETS.yml`.

---

## STAGE 3: Integration Services
**Target:** `n8n`, `docmost`, `evolution_api`
**Risk:** Workflow automation with elevated privileges

### 3.1 n8n
Uses multiple API keys (NOTION, EVOLUTION, etc.).
Strategy: Mount vault as read-only file, n8n reads via env file path.

```yaml
services:
  n8n:
    volumes:
      - /root/.secrets/vault.env:/run/secrets/n8n_env:ro
    environment:
      N8N_ENCRYPTION_KEY_FILE: /run/secrets/n8n_env
```

### 3.2 docmost
Already has its own internal secret management.
Strategy: Keep isolated, document separately.

---

## STAGE 4: VAULT999 Bridge (Sovereign Layer)
**Target:** Attestation, encrypted backup, audit trail

### 4.1 Bridge Script: vault → VAULT999 L4
```python
#!/usr/bin/env python3
# core/vault999/bridge_from_vault.py

import json
import hashlib
import gnupg
from datetime import datetime
from pathlib import Path

VAULT_FILE = Path("/root/.secrets/vault.env")
L4_STORAGE = Path("/root/arifOS/core/vault999/layer4_survivability/cold_storage")

def attest_vault_state():
    """Create cryptographic attestation of vault state."""
    content = VAULT_FILE.read_bytes()
    checksum = hashlib.sha256(content).hexdigest()
    
    attestation = {
        "timestamp": datetime.utcnow().isoformat(),
        "vault_checksum": checksum,
        "key_count": len([l for l in content.decode().split('\n') if '=' in l]),
        "authority": "888_JUDGE",
        "seal": "999_SEAL"
    }
    
    # Write to L4
    L4_STORAGE.mkdir(parents=True, exist_ok=True)
    snapshot_file = L4_STORAGE / f"vault_snapshot_{datetime.now():%Y%m%d_%H%M%S}.json"
    snapshot_file.write_text(json.dumps(attestation, indent=2))
    
    return attestation

# Run daily via cron
```

### 4.2 Automated Backup to VAULT999
```bash
# Add to crontab (daily at 3 AM)
0 3 * * * /root/arifOS/core/vault999/bridge_from_vault.py && vault backup
```

### 4.3 Emergency Recovery
```bash
# If vault.env is corrupted/lost:
# 1. Check L4 cold storage for latest attested snapshot
# 2. Verify checksum matches your memory
# 3. Restore from backup or regenerate keys
```

---

## Implementation Commands (Ready to Execute)

### Immediate (Tier 0 verified)
```bash
# Verify vault is working
vault list
vault load
aider-kimi --help
```

### Stage 1 Slice (arifosmcp_server only)
```bash
# 888 HOLD: Run these one at a time, verify between each

# 1. Initialize swarm (if not done)
docker swarm init

# 2. Create secrets from vault
grep ARIFOS_API_KEY /root/.secrets/vault.env | cut -d'=' -f2- | docker secret create arifos_api_key -
grep KIMI_API_KEY /root/.secrets/vault.env | cut -d'=' -f2- | docker secret create kimi_api_key -

# 3. Update docker-compose.yml (manual edit or patch)
# 4. Redeploy
# docker stack deploy -c docker-compose.yml -c docker-compose.secrets.yml arifos
# 5. Validate
# docker service logs arifos_arifosmcp_server
```

### Stage 1 Rollback (if needed)
```bash
# Remove secrets
docker secret rm arifos_api_key kimi_api_key

# Revert to .env mode
docker compose up -d arifosmcp_server
```

---

## Files Modified/Created

| File | Purpose | Status |
|------|---------|--------|
| `/root/.secrets/vault.env` | Canonical master | ✅ Active |
| `/root/.secrets/backups/` | Timestamped backups | ✅ Active |
| `/usr/local/bin/vault` | Human CLI | ✅ Active |
| `/usr/local/bin/aider-*` | Aider wrappers | ✅ Active |
| `/root/arifOS/SECRETS.yml` | Docker Secrets overlay | 📋 Ready |
| `/root/arifOS/core/vault999/bridge_from_vault.py` | L4 attestation | 🔧 Create |

---

## Success Criteria

- [ ] Stage 1: arifosmcp_server runs with Docker secrets
- [ ] Stage 1: No secrets in process env (`docker exec <id> env`)
- [ ] Stage 2: Postgres, Redis use secrets
- [ ] Stage 3: n8n mounted vault read-only
- [ ] Stage 4: Daily attestation snapshots in VAULT999 L4
- [ ] All stages: 888_HOLD respected (no mass migrations)

---

*DITEMPA BUKAN DIBERI — 999 SEAL ALIVE*
