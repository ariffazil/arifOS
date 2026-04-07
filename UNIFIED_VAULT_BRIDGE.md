# 🔐 UNIFIED VAULT BRIDGE
## Bridging VAULT999 Philosophy with Pragmatic Secret Management

### The Problem You Have
- 42 API keys in dual .env files (duplication)
- VAULT999 exists but is philosophy-heavy
- Docker Secrets defined but unused
- My aider vault is separate (fragmentation)
- .env was world-readable until just now

### The Solution: Hierarchical Secret Management

```
┌─────────────────────────────────────────────────────────────────┐
│  TIER 4: VAULT999 Sovereign (Constitutional)                    │
│  └─ governance_secret, session_secret                           │
│     └─ Stored in: Docker Secrets (production)                   │
│     └─ Stored in: /root/.arifos/vault/ (constitutional anchor)  │
├─────────────────────────────────────────────────────────────────┤
│  TIER 3: Infrastructure Secrets (Database, Cache)               │
│  └─ postgres_password, redis_password, qdrant_api_key          │
│     └─ Stored in: Docker Secrets                               │
│     └─ Rotated via: SECRETS.yml workflow                       │
├─────────────────────────────────────────────────────────────────┤
│  TIER 2: LLM Provider Keys (AI APIs)                            │
│  └─ KIMI_API_KEY, ANTHROPIC_API_KEY, GEMINI_API_KEY, etc.      │
│     └─ Stored in: /root/.secrets/vault.env (unified)           │
│     └─ Accessed via: `vault` CLI                               │
│     └─ Used by: aider, arifosmcp, n8n                          │
├─────────────────────────────────────────────────────────────────┤
│  TIER 1: Application Runtime (Ephemeral)                        │
│  └─ ARIFOS_DEV_MODE, DATABASE_URL, etc.                        │
│     └─ Stored in: .env (single source)                         │
│     └─ No secrets - only configuration                         │
└─────────────────────────────────────────────────────────────────┘
```

### Migration Path

#### Phase 1: Consolidate LLM Keys (Today)
1. Move all LLM keys from .env → /root/.secrets/vault.env
2. Update .env to reference: `KIMI_API_KEY_FILE=/root/.secrets/vault.env`
3. Use `vault load` before starting arifOS

#### Phase 2: Docker Secrets (This Week)
1. Create actual secret files in /root/arifOS/secrets/
2. Deploy with docker-compose.secrets.yml overlay
3. Remove secrets from .env entirely

#### Phase 3: VAULT999 Integration (Ongoing)
1. Use VAULT999 for constitutional secrets only
2. Keep philosophy, add pragmatism

### File Locations After Unification

| Purpose | Location | Permissions | Managed By |
|---------|----------|-------------|------------|
| LLM API Keys | `/root/.secrets/vault.env` | 600 | `vault` CLI |
| DB/Cache Secrets | `/root/arifOS/secrets/*.txt` | 600 | Docker Secrets |
| Gov/Session Secrets | Docker Swarm Secrets | N/A (in-memory) | SECRETS.yml |
| Config Only | `/root/arifOS/.env` | 600 | Manual edit |
| Constitutional | `/root/arifOS/core/vault999/` | 600 | VAULT999 system |

### Quick Commands

```bash
# Add LLM key to unified vault
vault set kimi sk-your-key-here

# Load all keys for arifOS
vault load && cd /root/arifOS && docker compose up -d

# Check what's configured
vault list

# Backup everything
vault-backup
cp /root/arifOS/.env /root/arifOS/.env.backup.$(date +%Y%m%d)
```
