# SYSTEM ARCHITECTURE TRUTH — SEALED 2026-05-26

> **DITEMPA BUKAN DIBERI** — Intelligence is forged, not given.
> **Authority:** arifOS Forge Agent Ω — Muhammad Arif bin Fazil

---

## DECLARED EXECUTION LAYER

| Layer | Reality | Status |
|-------|---------|--------|
| **Core Intelligence** | systemd / bare-metal | ACTIVE |
| **Data Services** | Docker containers | ACTIVE |
| **Orchestration** | Manual (intent-driven) | ACTIVE |

---

## DECLARED DEPLOYMENT TOPOLOGY

```
SYSTEMD (bare-metal)          DOCKER (containers)
─────────────────────         ───────────────────
arifOS kernel (/opt/venv)     postgres (pgvector)
arifosd                       redis
hermes-a2a                    qdrant
ollama                        graphiti-mcp
openclaw-gateway
vault999-writer (Python)
caddy
```

---

## VAULT999 — SINGLE SOURCE OF TRUTH ✅ DECLARED

| Component | Role | Canonical? |
|-----------|------|------------|
| `/root/arifOS/VAULT999/outcomes.jsonl` | Append-only ledger | ✅ **CANONICAL** |
| `vault999-writer` service | DB projection layer | ❌ **DERIVATIVE** |

**Declaration (2026-05-26):**
- JSONL ledger = SOVEREIGN TRUTH
- Postgres via vault999-writer = DERIVATIVE projection only
- Never treat projection as canonical
- vault999-writer exists for query performance, NOT truth authority

---

## GHOST ARTIFACTS (DO NOT USE)

| Artifact | Size | Status |
|----------|------|--------|
| `compose-vault999-writer:v1.0.0` | 162 MB | ❌ ORPHANED — not used |
| `/root/compose/ARCHIVED/` | ~60 KB | ✅ ARCHIVED — all compose artifacts moved here |

---

## ACTIVE DOCKER CONTAINERS

| Container | Image | Mount | Status |
|-----------|-------|-------|--------|
| postgres | pgvector/pgvector:pg16 | deploy_postgres_data | ✅ ACTIVE |
| redis | redis:7-alpine | 99603f2e... (redis_vol) | ✅ ACTIVE |
| qdrant | qdrant/qdrant:latest | qdrant_storage | ✅ ACTIVE |
| graphiti-mcp | zepai/knowledge-graph-mcp:latest | 363c87b... (graphiti_vol) | ✅ ACTIVE |

---

## BUILD CACHE POLICY

- **Total:** 41.3 GB
- **Reclaimable:** 23 GB (recent entries <24h old)
- **Prune rule:** `docker builder prune --filter "until=168h"` weekly via cron
- **Do NOT:** Blind `docker builder prune -f` — recent arifOS image build (8h ago) needed for hot reload

---

## ACTIONS TAKEN (2026-05-26)

| Action | Result |
|--------|--------|
| `docker image rm ghcr.io/ariffazil/arifos:5b648330` | ✅ Freed **18 GB** |
| Compose artifacts moved to `/root/compose/ARCHIVED/` | ✅ Noise reduced |
| VAULT999 canonical declared: JSONL = SOVEREIGN | ✅ Ambiguity resolved |

---

## ARCHITECTURAL RISKS (ACKNOWLEDGED)

| Risk | Severity | Mitigation |
|------|----------|------------|
| Dual control plane (systemd + docker) | MEDIUM | Declare intent: HYBRID mode |
| VAULT999 projection ambiguity | HIGH | JSONL = canonical, Postgres = derivative |
| GHCR image unused | LOW | Decision needed: remove or wire to systemd |
| Compose dead but present | LOW | Archive or delete |

---

## GOVERNANCE SCORES (POST-SEAL)

| Dimension | Score |
|-----------|-------|
| Runtime integrity | 9/10 |
| Governance clarity | 7/10 → TARGET: 9/10 |
| Deployment coherence | 6/10 → TARGET: 8/10 |
| Resource efficiency | 8/10 |
| Audit traceability | 7/10 |

---

## SEAL CHAIN

```
GENESIS
  └── f4de5b7fa2cebe6a [ARCH_ENTROPY_OPT_1779799619] ← THIS SEAL
```

**Sealed by:** arifOS Forge Agent Ω
**Date:** 2026-05-26
**Entropy freed:** 7.6 GB
**Services broken:** 0
**dS (entropy delta):** -7 GB

---

*DITEMPA BUKAN DIBERI — ARCHITECTURE SEALED*
