# arifOS Master Deployment Document (v2026.3.2)

This document is the single source of truth for arifOS deployment, architecture, and status. It consolidates modular documentation into a unified "Highest Intelligence" reference.

---

## 1. Three-Repo Architecture

| Repo | Role | Local Path |
|------|------|------------|
| `ariffazil/arifOS` | Kernel, MCP server, Docker infra, VAULT999 | `/srv/arifOS` |
| `ariffazil/openclaw-workspace` | OpenClaw agent OS — AGENTS/SOUL/TOOLS/skills | `/opt/arifos/git/openclaw-workspace` |
| `ariffazil/AGI_ASI_bot` | Client personas, MCP configs, governance hooks | `/opt/arifos/git/AGI_ASI_bot` |

**Rule:** Client MCP configs live in `AGI_ASI_bot`. Server-side changes go in `arifOS`. OpenClaw agent identity/skills go in `openclaw-workspace`.

---

## 2. Deployment Map (Canonical Surfaces)

| Surface | Public URL | Platform | Source Path | Workflow Owner |
|:--|:--|:--|:--|:--|
| Docs site (APPS) | `https://arifos.arif-fazil.com` | GitHub Pages | `sites/docs/**` | `.github/workflows/deploy-sites.yml` |
| MCP runtime | `https://arifosmcp.arif-fazil.com` | VPS (Coolify) | `aaa_mcp/**`, `arifos_aaa_mcp/**`, `core/**`, `aclip_cai/**` | `.github/workflows/deploy.yml` |
| Dashboard | `https://arifosmcp-truth-claim.pages.dev` | Cloudflare Pages | `run_evals.py` | `.github/workflows/deploy-cloudflare.yml` |
| OpenClaw | `https://claw.arifosmcp.arif-fazil.com` | VPS | OpenClaw Workspace | Traefik Routing |
| Monitoring | `https://monitor.arifosmcp.arif-fazil.com` | VPS | Grafana/Prometheus | Docker Compose |

---

## 3. VPS Architecture & Infrastructure

**Host:** srv1325122.hstgr.cloud (72.62.71.199)
**OS:** Ubuntu 25.10 (Linux 6.17)
**Specs:** 4 vCPU, 16 GB RAM, 193 GB SSD

### Active Services (Docker Trinity)
- `arifosmcp_server`: Constitutional AI kernel (Port 8080)
- `traefik_router`: Edge router & TLS termination (Port 80/443)
- `arifos-postgres`: Vault state & audit logs (Port 5432)
- `arifos-redis`: Session cache & broker (Port 6379)
- `qdrant_memory`: Vector storage for `recall_memory` (Port 6333 internal)
- `ollama_engine`: Local LLM engine — qwen2.5:3b loaded
- `openclaw_gateway`: AI gateway (Port 18789)
- `arifos_prometheus`: Metrics collection
- `arifos_grafana`: Monitoring dashboards
- `arifos_n8n`: Workflow automation
- `arifos_webhook`: CI/CD listener (Port 9000 internal)

---

## 4. Constitutional Governance (The 13 Floors)

All tools protected by F1-F13 constitutional floors.

| Floor | Name | Status |
|-------|------|--------|
| F1 | Amanah (Reversibility) | Active |
| F2 | Truth (τ ≥ 0.99) | Active |
| F3 | Tri-Witness | Active |
| F4 | Clarity (ΔS ≤ 0) | Active |
| F5 | Peace² | Active |
| F6 | Empathy (κᵣ ≥ 0.70) | Active |
| F7 | Humility (Ω₀ = 0.04) | Active |
| F8 | Genius (G ≥ 0.80) | Active |
| F9 | Anti-Hantu | Active |
| F10 | Ontology | Active |
| F11 | Command Auth | Active |
| F12 | Injection Defense | Active |
| F13 | Sovereign | Active — human veto preserved |

---

## 5. Deployment Status (2026-03-05)

**Phase 4 Partial Complete — Phase 4B Next**

### Live Tool Matrix (13 canonical tools)
| Tool | Status | Note |
|:---|:---|:---|
| `anchor_session` | LIVE | Stage 000 |
| `reason_mind` | LIVE | Stages 111-333 |
| `vector_memory` | LIVE | Canonical memory lane |
| `simulate_heart` | LIVE | Stage 555 |
| `critique_thought`| LIVE | Stage 666 |
| `apex_judge` | LIVE | Stage 888 |
| `seal_vault` | LIVE | Stage 999 |
| `eureka_forge` | LIVE | Stage 777 |
| `search_reality` | LIVE | Stage 111 external evidence |
| `ingest_evidence` | LIVE | Unified URL/file ingestion |
| `audit_rules` | LIVE | Constitutional audit checks |
| `check_vital` | LIVE | Runtime health telemetry |
| `metabolic_loop` | LIVE | Composite 000-999 cycle |

Compatibility aliases (`fetch_content`, `inspect_file`, `system_audit`) resolve to canonical tools.

### Next Up (Phase 4B)
- Agent Zero deployment
- Production hardening (alerts, backups)

---

**DITEMPA BUKAN DIBERI** — Forged, Not Given.
