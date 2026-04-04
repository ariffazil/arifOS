# CONTEXT.md — Shared Agent Context
> **Last updated: 2026-03-13 by Gemini CLI (gemini-2.0-flash)**
> This file is the single source of truth about the owner, projects, and infrastructure.
> All AI agents (Claude Code, kimi-cli, opencode, gemini, codex, aider) must read this before working.

---

## CRITICAL: You Are Running ON the VPS

**This machine IS the production VPS.** Hostname: `srv1325122` | Public IP: `2a02:4780:5e:dbf6::1`
- No SSH needed — all agents run directly on the server
- No GUI — terminal/AI only
- This VPS is purpose-built for AI agent management
- Arif's API keys are free/limited tier — low financial risk
- Docker and all services are managed directly via `docker` / `docker compose` commands
- Production deploy path: `/srv/arifosmcp/` (symlinked from `/srv/arifOS/`)

---

## Who Is Arif?

**Muhammad Arif bin Fazil** — Malaysian sovereign architect and non-coder (geologist by background).
Motto: *"Ditempa Bukan Diberi"* — Forged, Not Given.
He does not write code manually. He directs AI agents to build, manage, and maintain everything.
GitHub: `ariffazil` | Website: https://arif-fazil.com

**How to work with Arif:**
- Explain things simply — no jargon
- Always confirm before destructive actions (delete, wipe, force push)
- Prefer plain-English summaries alongside any technical output
- He manages a live production VPS — treat it with care
- Goal: reduce friction for arifOS adoption — keep things open and accessible

---

## The Three Projects

### 1. APEX Theory
- **What**: A governance framework (not software). The philosophical and mathematical backbone.
- **URL**: https://apex.arif-fazil.com
- **Core formula**: `G† = (A × P × X × E²) × |ΔS|/C ≥ 0.80` — the "Genius Score"
- **Role in stack**: The Soul (Ψ) — final judgment engine. Every AI action must score ≥ 0.80 to receive a SEAL. Anything below is VOID.
- **Principle**: "Cheap truth equals VOID" — borrowed from the Landauer Bound (thermodynamics)

### 2. arifOS
- **What**: Constitutional governance kernel — the specification and law layer
- **GitHub**: https://github.com/ariffazil/arifOS
- **Docs**: https://arifos.arif-fazil.com (GitHub Pages, static)
- **PyPI**: `arifos` | **npm**: `@arifos/mcp` | **Docker**: `ariffazil/arifos:latest`
- **License**: AGPL-3.0 (⚠️ LICENSE file in repo is CC0 — known inconsistency, pending fix)
- **Analogy**: Like TCP/IP for AI — adds reversibility, verification, and constitutional enforcement between LLMs and real-world tool execution

### 3. arifosmcp
- **What**: The live production MCP server — the running implementation of arifOS
- **GitHub**: https://github.com/ariffazil/arifosmcp
- **Live endpoint**: https://arifosmcp.arif-fazil.com/mcp
- **Current version**: `2026.03.13-FORGED` (git: `1af6d53b`)
- **PyPI**: `arifosmcp`
- **VPS path**: `/srv/arifosmcp/`
- **Transport**: streamable-http (MCP 2025-11-25 spec)
- **Auth**: Open — no API key required (intentional, low friction for adoption)

#### 12 Public Tools
| Tool | Stage | Purpose |
|------|-------|---------|
| `arifOS_kernel` | 444_ROUTER | Main orchestrator — full 000→999 metabolic pipeline |
| `reality_compass` | 111_SENSE | Unified search/fetch engine |
| `reality_atlas` | 222_REALITY | Semantic evidence graph management |
| `reality_dossier` | 222_REALITY | Tri-Witness decoder with 3E synthesis |
| `init_anchor_state` | 000_INIT | F11 session ignition (bootstrap whitelisted) |
| `revoke_anchor_state` | 000_INIT | F11 session revocation |
| `check_vital` | 000_INIT | System vitality + thermo-budget + capability map |
| `audit_rules` | 333_MIND | Inspect 13 constitutional floors |
| `session_memory` | 555_MEMORY | Contextual vector persistence (Qdrant) |
| `verify_vault_ledger`| 999_VAULT | SHA-256 Merkle chain integrity verification |
| `open_apex_dashboard`| 888_JUDGE | Live governed metrics visualizer |
| `search_reality` / `ingest_evidence` | — | Hardened search/fetch aliases |

#### 13 Constitutional Floors (F1–F13)
| Floor | Name | Type | Effect |
|-------|------|------|--------|
| F1 | Amanah (Reversibility) | Hard | Halts execution |
| F2 | Truth (τ ≥ 0.99) | Hard | Halts execution |
| F3 | Quad-Witness (W4 ≥ 0.75) | Soft | Warning |
| F4 | Clarity (ΔS ≤ 0) | Hard | Halts execution |
| F5 | Peace² (non-harm) | Soft | Warning |
| F6 | Empathy (κᵣ ≥ 0.95) | Soft | Warning |
| F7 | Humility (uncertainty ranges) | Hard | Halts execution |
| F8 | Genius (G† ≥ 0.80) | Soft | Warning |
| F9 | Anti-Hantu (blocks AI personhood claims) | Soft | Warning |
| F10 | Ontology (tool-only positioning) | Soft | Warning |
| F11 | Authority (command verification) | Hard | Halts execution |
| F12 | Defense (injection prevention) | Soft | Warning |
| F13 | Sovereign (human cryptographic veto) | Hard | Halts execution |

#### Trinity Architecture (ΔΩΨ)
- **Δ Mind / AGI** — Logic and truth (F2, F4, F7, F8) → `core/shared/physics.py`
- **Ω Heart / ASI** — Safety and empathy (F1, F5, F6, F9) → `core/organs/_2_asi.py`
- **Ψ Soul / APEX** — Final judgment and sovereign override (F3, F11, F13) → `core/organs/_3_apex.py`

---

## VPS Infrastructure

**Server**: Single VPS, 193GB disk (85GB used as of 2026-03-12)
**You are already on this server.** No SSH needed.
**Deploy path**: `/srv/arifosmcp/` (symlink → `/srv/arifOS/`)
**Compose file**: `/srv/arifosmcp/docker-compose.yml`
**Disk**: 193GB total, 85GB used (44%), 109GB free — healthy

### Git Sync (as of 2026-03-13)
- VPS HEAD: `1af6d53b` = GitHub main HEAD = **ALIGNED**
- Push/pull uses HTTPS + token (no SSH key on VPS):
  ```bash
  GITHUB_TOKEN=$(grep GITHUB_TOKEN /srv/arifosmcp/.env | head -1 | cut -d= -f2)
  git pull "https://ariffazil:${GITHUB_TOKEN}@github.com/ariffazil/arifosmcp.git" main
  ```

### Docker Containers — Live State (2026-03-13)

All 12 containers running. **All healthy.** AgentZero initialized.

| Container | Status | Role |
|-----------|--------|------|
| `arifosmcp_server` | ✅ healthy | MCP API (FastAPI + FastMCP) |
| `traefik_router` | ✅ up | Reverse proxy / TLS — Traefik v3.6.9 |
| `arifos_postgres` | ✅ healthy | VAULT999 audit ledger — bound to 127.0.0.1 |
| `arifos_redis` | ✅ healthy | Session cache — bound to 127.0.0.1 |
| `qdrant_memory` | ✅ up | Vector DB (BGE-M3, 768-dim) |
| `ollama_engine` | ✅ up | Local LLMs: qwen2.5:3b, bge-m3, nomic-embed-text |
| `openclaw_gateway` | ✅ healthy | Sandboxed agent execution + Telegram bot |
| `headless_browser` | ✅ healthy | Headless Chrome (Browserless) |
| `agent_zero_reasoner` | ✅ up | Reasoning agent |
| `arifos_n8n` | ✅ up | Workflow automation |
| `arifos_prometheus` | ✅ up | Metrics — scraping arifos-mcp ✅ |
| `arifos_grafana` | ✅ healthy | Monitoring dashboards |

**Internal network**: `arifos_arifos_trinity` on `10.0.10.0/24`

### Three-Tier Sovereign Deployment

| Layer | Name | URL | Hosting |
|-------|------|-----|---------|
| Law | arifOS docs | arifos.arif-fazil.com | GitHub Pages |
| Brain | arifosmcp server | arifosmcp.arif-fazil.com | VPS (live) |
| Soul | APEX Theory | apex.arif-fazil.com | Cloudflare Pages |
| Eye | Monitoring | monitor.arifosmcp.arif-fazil.com | Grafana on VPS |

### Critical Environment Variables
- `ARIFOS_GOVERNANCE_SECRET` — Core auth secret ✅
- `DATABASE_URL` — PostgreSQL connection ✅
- `REDIS_URL` — Cache connection ✅
- `GITHUB_TOKEN` — GitHub API + push access ✅
- `OPENCLAW_GATEWAY_TOKEN` — OpenClaw auth ✅
- `ARIFOS_888_JUDGE_KEY` — Sovereign human veto key ✅ (HSM recommended)
- `ARIFOS_API_KEY` — Bearer auth (NOT SET = open access, intentional for adoption)

---

## Tech Stack

| Category | Technology |
|----------|-----------|
| Language | Python 3.12+, TypeScript/Node.js |
| Web framework | FastAPI + FastMCP |
| Database | PostgreSQL 16 (ledger), Redis 7 (cache) |
| Vector store | Qdrant (BGE-M3 multilingual, 768-dim) |
| Local LLM | Ollama (qwen2.5:3b, bge-m3, nomic-embed-text) |
| Search/grounding | Perplexity → Brave → Jina (fallback chain) |
| Containers | Docker 24.0+, Docker Compose 2.20+ |
| Reverse proxy | Traefik v3.6.9 |
| Monitoring | Prometheus + Grafana |
| Workflows | n8n |
| Protocol | MCP 2025-11-25 (streamable-http, stdio) |
| Audit ledger | Merkle-hashed PostgreSQL + Redis (VAULT999) |
| CI/CD | GitHub Actions |
| Package mgr | uv (Python), Bun/npm (TypeScript) |

---

## Known Issues (as of 2026-03-13)

- ⚠️ Traefik metrics port 8082 — Prometheus scrape fails (low priority, app works fine)
- ⚠️ APEX Dashboard (`arifosmcp-truth-claim.pages.dev`) — Cloudflare Pages 404
- ⚠️ OpenClaw image models — `claude-opus-4-5/4-6` returning 404 on image tasks
- ℹ️ ML floors disabled — heuristic mode, SBERT not loaded
- ℹ️ Grafana dashboards not yet wired to constitutional metrics
- ℹ️ arifOS LICENSE file is CC0 but code declares AGPL-3.0 — needs reconciliation
- ✅ MCP Connectivity — FIXED: venv python + global node binaries in ~/.kimi/mcp.json

---

## Full VPS Architecture Doc

→ `/srv/arifosmcp/infrastructure/VPS_ARCHITECTURE.md`

This is the single source of truth for VPS state. All agents must update it after significant changes.

---

*Context last verified: 2026-03-13 by Gemini CLI (gemini-2.0-flash)*
*Git: `1af6d53b` | VPS = GitHub = ALIGNED*
