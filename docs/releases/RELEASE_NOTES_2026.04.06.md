# arifOS Release Notes v2026.04.06
## Clean Architecture + Docker + ChatGPT Apps SDK

**Release Date:** 2026-04-06  
**Version:** 2026.4.6  
**Codename:** HORIZON-II.1-CLEAN  
**Build SHA:** 0bad3e1

---

## 🚀 Major Features

### 1. Clean MCP Architecture
Separated MCP primitives per the Model Context Protocol specification:

**New Package:** `arifosmcp.specs/`
- `contracts.py` — Shared JSON schemas (SessionAnchor, TelemetryEnvelope, VerdictRecord)
- `tool_specs.py` — 11 canonical tools with functional names
- `resource_specs.py` — 9 read-only resources  
- `prompt_specs.py` — 10 workflow prompt templates
- `chatgpt_subset.py` — Apps SDK-safe adapter

**Functional Naming:**
Tool names are now verbs (MCP best practice):
| Old (Symbolic) | New (Functional) | Purpose |
|----------------|------------------|---------|
| `apex_soul` | `judge_verdict` | Constitutional verdict |
| `init_anchor` | `init_session_anchor` | Session initialization |
| `arifOS_kernel` | `route_execution` | Query routing |
| `agi_mind` | `reason_synthesis` | Reasoning engine |
| `asi_heart` | `critique_safety` | Safety critique |

### 2. Docker Production Deployment

**New Files:**
- `deployments/af-forge/Dockerfile` — Multi-stage build with Python 3.11
- `deployments/af-forge/docker-compose.yml` — Full stack (MCP + Nginx + Qdrant + Redis)
- `deployments/af-forge/deploy.sh` — Automated deployment script
- `deployments/af-forge/nginx.conf` — Nginx with CSP headers for ChatGPT widget

**Features:**
- Non-root container user (`arifos`)
- Health checks built-in
- Build metadata injection (git SHA, timestamp)
- Widget static file serving with CSP

### 3. ChatGPT Apps SDK Integration

**Phase 1 (Current): Read-Only Health Checks**

Exposed Tools:
- `get_constitutional_health` — Returns floor scores, telemetry, verdict
- `render_vault_seal` — Renders interactive widget in ChatGPT UI
- `list_recent_verdicts` — Read-only vault audit log (last 100)

**Widget:** `https://mcp.af-forge.io/widget/vault-seal`
- CSP-compliant (`frame-ancestors https://chat.openai.com`)
- Displays: Truth Score, Humility Level, Entropy Delta, Harmony Ratio, Reality Index, Witness Strength
- BLS attestation visualization (3-of-5 juror quorum)

**Security:** 888_HOLD Compliance
- ❌ No vault write access from ChatGPT
- ❌ No VPS execution paths exposed
- ❌ No private keys in ChatGPT-facing container

**Phase 2 (Future):** Write-path with explicit F11/F13 human review

### 4. BLS12-381 Signature Aggregation (Phase A)

- 3-of-5 juror supermajority for seal attestation
- Juror pool: DELTA_MIND, OMEGA_HEART, PSI_SOUL, A_AUDITOR, A_VALIDATOR
- Aggregate signatures for O(1) verification
- Mock proofs in Phase 1 (real signing in hardened Vault999 boundary)

---

## 📊 System Metrics

| Metric | Value |
|--------|-------|
| **Tools** | 11 canonical (22 with aliases) |
| **Resources** | 9 read-only |
| **Prompts** | 10 workflow templates |
| **Floors** | 13 constitutional (F1-F13) |
| **Test Coverage** | 31 new spec tests |
| **Docker Image Size** | ~150MB (multi-stage) |

---

## 🔧 Technical Improvements

### Server Updates
- FastMCP Horizon alignment with clean specs
- Functional tool aliases in `server_horizon.py`
- Prompt aliases (`prompt_init_anchor`, `prompt_judge_verdict`, etc.)
- New resources: `vault/recent`, `bootstrap`, `contracts/context`

### Documentation
- **README.md** — ChatGPT SDK section, functional naming table, deployment updates
- **docs/AGENTS.md** — Tool table with functional names, ChatGPT section
- **docs/architecture/ARCHITECTURE.md** — System diagrams, floor matrix, API reference
- Deleted **NEXUS_HORIZON.md** (replaced with proper architecture doc)

### Code Quality
- Pydantic v2 ConfigDict migration (fixes deprecation warnings)
- 31 new tests for specs validation
- ChatGPT safety validation (`validate_chatgpt_safety()`)

---

## 🐛 Bug Fixes

- Fixed widget CSP headers for ChatGPT iframe
- Fixed widget domain (changed from `ui://` to `https://`)
- Fixed contracts.py imports (moved to `contracts_v2.py`)
- Fixed resource URI patterns to allow HTTPS

---

## 📝 Deployment Notes

### Quick Deploy
```bash
cd deployments/af-forge
export ARIFOS_BUILD_SHA=$(git rev-parse HEAD)
export ARIFOS_BUILD_TIME=$(date -u +%Y-%m-%dT%H:%M:%SZ)
docker compose up -d --build
```

### Verification
```bash
curl http://localhost:3000/health
curl http://localhost:3000/build
curl -I https://mcp.af-forge.io/widget/vault-seal | grep content-security
```

---

## 🔮 What's Next (Phase 2)

1. **Vault999 Write-Path** — Real BLS signing with HSM integration
2. **Mode Audit** — Verify all 42 modes match schemas
3. **Qdrant AAA Indexing** — Cross-agent constitutional RAG
4. **Second Adapter** — Anthropic or REST adapter
5. **Hardware Enclaves** — Nitro/SGX for root BLS keys

---

## 📦 Artifacts

| Artifact | Location |
|----------|----------|
| **PyPI Package** | `pip install arifosmcp` |
| **Docker Image** | `docker pull arifosmcp:latest` |
| **GitHub Release** | https://github.com/ariffazil/arifOS/releases |
| **Widget** | https://mcp.af-forge.io/widget/vault-seal |

---

## 👏 Contributors

- **Muhammad Arif bin Fazil** — Architecture, core implementation, BLS integration

---

**DITEMPA BUKAN DIBERI — Forged, Not Given**

*Release sealed: 2026-04-06 — 999 SEAL*
