# AGENTS.md — arifOS Project Guide for AI Coding Agents

**Version:** 2026.03.07-ARCH-SEAL  
**Authority:** Muhammad Arif bin Fazil (888_JUDGE)  
**Motto:** *Ditempa Bukan Diberi* — Forged, Not Given [ΔΩΨ | ARIF]

---

## 1. Project Overview

**arifOS** is the world's first production-grade Constitutional AI Governance System. It is a Python-based middleware that uses the Model Context Protocol (MCP) to govern the actions of AI agents. It sits between LLMs and the real world — intercepting every tool call, running it through 13 mathematically-defined constitutional floors (F1-F13), and either signing off on execution or throwing a `VOID`.

### The Core Insight: TCP Layer for AI Agents

Just as TCP provides reliability over the unreliable IP layer, arifOS provides governance over the unconstrained MCP layer:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  INTENT LAYER       │  USER / AI AGENT — speaks natural language            │
├─────────────────────┼───────────────────────────────────────────────────────┤
│  TRANSPORT LAYER    │  MCP (Model Context Protocol) — universal addressing  │
├─────────────────────┼───────────────────────────────────────────────────────┤
│  RELIABILITY LAYER  │  ► arifOS ◄ — 13-floor constitution, F2 truth,        │
│  (arifOS = TCP)     │    thermodynamic enforcement, VAULT999 audit trail    │
├─────────────────────┼───────────────────────────────────────────────────────┤
│  EXECUTION LAYER    │  L3 CIVILIZATION — shell, files, databases, APIs      │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Key Concepts

- **13 Constitutional Floors (F1-F13):** Mathematical thresholds governing AI behavior — not guidelines, but hard constraints. Defined in `core/shared/floors.py`.
- **Trinity Architecture (ΔΩΨ):**
  - **AGI Mind (Δ):** Stages 111-333 — cognition and reasoning (F2, F4, F7, F8)
  - **ASI Heart (Ω):** Stages 555-666 — empathy and impact (F5, F6, F9)
  - **APEX Soul (Ψ):** Stages 444-888 — final judgment (F3, F10, F11, F12, F13)
- **000-999 Metabolic Loop:** 11-stage pipeline that digests raw intent into governed action
- **VAULT999:** Immutable cryptographic ledger for audit trails (PostgreSQL + Redis + Merkle tree)
- **888_HOLD:** Human veto mechanism for irreversible actions

### The Genius Equation

```
G = A × P × X × E² ≥ 0.80
Where:
- A = Akal (Clarity/Intelligence)
- P = Present (Regulation/Peace)
- X = Exploration (Trust/Curiosity)
- E = Energy (Sustainable Power) — squared because inefficiency compounds
```

---

## 2. Technology Stack

### Primary Language & Runtime
- **Python:** >=3.12 (strict requirement)
- **Package Manager:** `uv` (modern Python package manager)
- **Lock File:** `uv.lock`
- **Version Scheme:** Date-based (`YYYY.MM.DD`), NOT semantic versioning

### Core Dependencies
| Category | Libraries |
|----------|-----------|
| MCP Transport | `fastmcp==3.0.2`, `mcp>=1.0.0` |
| Web Framework | `fastapi>=0.104.1`, `starlette>=0.30.0`, `uvicorn[standard]` |
| Data Validation | `pydantic>=2.0.0` |
| Async Runtime | `anyio>=4.0.0` |
| Vector DB | `qdrant-client>=1.7.0` (primary), `chromadb>=0.5.0` (legacy) |
| ML/Embeddings | `sentence-transformers>=2.2.0` (BGE-M3), `scikit-learn>=1.3.0`, `numpy>=1.20.0` |
| Persistence | `asyncpg>=0.29.0` (PostgreSQL), `redis>=5.0.0` |
| Web Search | `duckduckgo-search>=5.0.0`, `playwright>=1.40.0`, `beautifulsoup4>=4.12.0` |
| HTTP Client | `httpx>=0.25.0`, `requests>=2.31.0` |
| Monitoring | `prometheus-client>=0.19.0` |
| CLI/UX | `rich>=13.7.0` |
| Security | `cryptography` (Ed25519 signatures, HMAC) |

### Infrastructure Stack (Docker Compose)
The `docker-compose.yml` defines 12 production containers:
- **Traefik:** Edge router with Let's Encrypt SSL
- **arifosmcp_server:** The constitutional MCP server (port 8080)
- **postgres:** VAULT999 authoritative storage
- **redis:** Session cache and hot storage
- **qdrant_memory:** Vector embeddings (768-dim, BGE-M3)
- **ollama_engine:** Local LLM inference
- **openclaw_gateway:** Multi-channel I/O gateway
- **agent_zero_reasoner:** AGI reasoning brain
- **prometheus + grafana:** Observability stack
- **n8n:** Workflow automation
- **headless_browser:** Chromium for web scraping
- **webhook:** Auto-deploy trigger

---

## 3. Project Structure

### 4-Layer Architecture (L0-L3)

```
┌─────────────────────────────────────────────────────────────────┐
│ L3: CIVILIZATION     │ External tools, APIs, shell, databases   │
├──────────────────────┼──────────────────────────────────────────┤
│ [AKI BOUNDARY]       │ 🛑 Arif Kernel Interface — Hard Airlock  │
│                      │ No thought manifests in L3 without       │
│                      │ passing the AKI contract.                │
├──────────────────────┼──────────────────────────────────────────┤
│ L2: OPERATION        │ Skills, workflows, agents, routing       │
├──────────────────────┼──────────────────────────────────────────┤
│ L1: INSTRUCTION      │ Prompts, system cards, cognitive atlas   │
├──────────────────────┼──────────────────────────────────────────┤
│ L0: CONSTITUTION     │ 13 Floors kernel, thermodynamics, VAULT  │
└─────────────────────────────────────────────────────────────────┘
```

### Directory Organization

| Directory | Layer | Responsibility |
|-----------|-------|----------------|
| `core/` | L0 KERNEL | Pure decision logic, F1-F13 floors, thermodynamics, zero transport deps. The beating heart of arifOS. |
| `aclip_cai/` | L1/L2 INTELLIGENCE | 9-Sense perception, Triad reasoning (Δ/Ω/Ψ), evidence acquisition |
| `aaa_mcp/` | TRANSPORT ADAPTER | MCP protocol implementation, session management, metabolic pipeline. **NO decision logic.** |
| `arifos_aaa_mcp/` | DEPLOYMENT SURFACE | Canonical PyPI package, 13-tool public surface, runtime entrypoint |
| `tests/` | QUALITY | Unit, integration, E2E, constitutional, and adversarial tests |
| `scripts/` | UTILITIES | Deployment, monitoring, constitutional linting, utilities |
| `docs/` | DOCUMENTATION | Theory canon (7 documents), implementation guides, API references |
| `config/` | CONFIGURATION | Service integrations, capability definitions |
| `spec/` | SPECIFICATION | MCP manifests, JSON schemas, protocol definitions |
| `deployment/` | DEVOPS | Docker configs, Grafana dashboards, Prometheus rules |

### Key Files Reference

| File | Purpose |
|------|---------|
| `pyproject.toml` | Package metadata, dependencies, tool configs (pytest, ruff, mypy, black) |
| `core/shared/floors.py` | **Canonical F1-F13 floor definitions** (THRESHOLDS dict) — 913 lines of constitutional law |
| `core/governance_kernel.py` | Unified Ψ state, thermodynamic enforcement |
| `core/organs/_0_init.py` | Stage 000 — INIT, scan_injection, verify_auth |
| `core/organs/_1_agi.py` | Stages 111-333 — sense, think, reason (AGI Mind Δ) |
| `core/organs/_2_asi.py` | Stages 555-666 — empathize, align (ASI Heart Ω) |
| `core/organs/_3_apex.py` | Stages 444-888 — sync, forge, judge (APEX Soul Ψ) |
| `core/organs/_4_vault.py` | Stage 999 — seal, query, verify |
| `core/physics/thermodynamics_hardened.py` | P3 mandatory thermodynamic enforcement |
| `aaa_mcp/server.py` | 13 MCP tools with `@mcp.tool()` decorators |
| `arifos_aaa_mcp/server.py` | Canonical public entrypoint |
| `docker-compose.yml` | 12-service production stack |
| `.pre-commit-config.yaml` | Constitutional quality gates (Black, Ruff, MyPy, Bandit, custom F1/F9 checks) |

---

## 4. Build & Run Commands

### Installation

```bash
# Clone and setup
git clone https://github.com/ariffazil/arifOS.git && cd arifOS

# Install with all dev dependencies
pip install -e ".[dev]"

# Or using uv (recommended)
uv pip install -e ".[dev]"

# Install pre-commit hooks
pip install pre-commit
pre-commit install
```

### Running the MCP Server

```bash
# STDIO mode (for Claude Desktop, Cursor IDE)
python -m arifos_aaa_mcp stdio

# HTTP mode (streamable HTTP at /mcp)
python -m arifos_aaa_mcp http

# SSE mode (default, for VPS/Coolify)
python -m arifos_aaa_mcp
python -m arifos_aaa_mcp sse

# Using canonical CLI entry point
arifos stdio
arifos http
arifos sse
```

### Docker Deployment

```bash
# Build and run locally
docker build -t arifos . && docker run -p 8080:8080 arifos

# Full production stack (12 containers)
cp .env.example .env.docker
# Edit .env.docker with your API keys (Jina, Perplexity, Brave, etc.)
docker compose up -d
docker compose ps

# Health check
curl http://localhost:8080/health
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST` | `0.0.0.0` | Server bind address |
| `PORT` | `8080` | Server port |
| `AAA_MCP_TRANSPORT` | `sse` | Transport mode: stdio, http, sse |
| `AAA_MCP_OUTPUT_MODE` | `user` | Output mode: user, debug |
| `ARIFOS_PHYSICS_DISABLED` | `0` | Disable P3 thermodynamics (test only!) |
| `DATABASE_URL` | — | PostgreSQL connection string |
| `REDIS_URL` | — | Redis connection string |
| `QDRANT_URL` | — | Qdrant vector DB URL |
| `ARIFOS_GOVERNANCE_SECRET` | auto-generated | HMAC secret for governance tokens |
| `ARIFOS_F11_AUTH_REQUIRED` | `true` | Enforce authentication |
| `ARIFOS_888_HOLD_ENABLED` | `true` | Enable human veto |

---

## 5. Testing Strategy

### Test Commands

```bash
# Full test suite
pytest tests/ -v

# With coverage report
pytest tests/ -v --cov=core --cov=aaa_mcp --cov=aclip_cai --cov-report=html

# Single file
pytest tests/test_quick.py -v

# Single test
pytest tests/test_core_foundation.py::test_name -v

# By markers
pytest -m constitutional    # F1-F13 floor validation
pytest -m integration       # Integration tests
pytest -m slow              # Long-running tests

# E2E tests
pytest tests/test_e2e_all_tools.py -v
pytest tests/test_e2e_core_to_aaa_mcp.py -v

# Async tests (no @pytest.mark.asyncio needed — auto mode enabled)
pytest tests/test_async_module.py -v
```

### Test Categories

| Category | Location | Description |
|----------|----------|-------------|
| Unit Tests | `tests/core/`, `tests/aclip_cai/` | Component-level tests for individual functions |
| Integration | `tests/integration/`, `tests/canonical/` | Cross-module tests, MCP contract tests |
| E2E | `tests/test_e2e_*.py` | Full pipeline tests from session to seal |
| Constitutional | `tests/constitutional/`, `-m constitutional` | F1-F13 floor validation tests |
| Adversarial | `tests/adversarial/` | P3 hardening, attack resistance, Ψ-Shadow tests |
| Live | `tests/mcp_live/` | Tests against live VPS (requires network) |

### Pytest Configuration (from pyproject.toml)

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
asyncio_mode = "auto"
markers = [
    "asyncio",
    "constitutional",
    "slow",
    "integration",
]
```

### Test Environment Setup

The `tests/conftest.py` provides:
- Automatic `sys.path` insertion for imports
- Global physics disabling for performance (`ARIFOS_PHYSICS_DISABLED=1`)
- Legacy spec bypass for tests (`ARIFOS_ALLOW_LEGACY_SPEC=1`)
- Fixtures: `aaa_client`, `require_postgres`, `require_redis`, `enable_physics_for_apex_theory`

---

## 6. Code Style Guidelines

### Linting & Formatting Commands

```bash
# Format with Black (100-char limit)
black aaa_mcp/ core/ arifos_aaa_mcp/ aclip_cai/ --line-length=100

# Lint with Ruff
ruff check aaa_mcp/ core/ arifos_aaa_mcp/ aclip_cai/ --fix

# Type check (strict on core/)
mypy core/ --ignore-missing-imports
mypy aaa_mcp/ --ignore-missing-imports || true

# Run all pre-commit hooks
pre-commit run --all-files
```

### Style Rules

| Tool | Setting | Value |
|------|---------|-------|
| Black | line-length | 100 |
| Ruff | line-length | 100 |
| Ruff | target-version | py310 |
| MyPy | strict on | `core/`, `core.governance_kernel`, `core.organs.*` |

### Critical Coding Rules

1. **NEVER use `print()` in tool code** — it corrupts JSON-RPC/MCP streams
   - Use `sys.stderr.write()` or `logging` instead

2. **Decorator Order (CRITICAL for MCP tools)**:
   ```python
   @mcp.tool()                    # OUTER — FastMCP registers this
   @constitutional_floor("F2")   # INNER — enforcement at call time
   async def my_tool(...):
   ```

3. **Version Identity** — Use date-based versioning (`YYYY.MM.DD`), NOT semantic versioning

4. **Import Namespacing**:
   - `arifos_aaa_mcp.*` — canonical external package
   - `aaa_mcp.*` — internal transport adapter
   - `aclip_cai.*` — intelligence layer
   - `core.*` — kernel (import as `from core.shared.physics import W_4`)

5. **No stdout in MCP tools** — MCP uses stdout for JSON-RPC; use stderr for logs

6. **Floor thresholds** — Only modify in `core/shared/floors.py` (THRESHOLDS dict)

7. **Architecture Boundaries (Enforced)**:
   - `core/` has ZERO transport deps — `fastmcp`, `fastapi`, `starlette` are banned
   - `aaa_mcp/` has ZERO decision logic — only protocol relay
   - `aclip_cai/` has NO HTTP servers — perception only

---

## 7. The 13 Constitutional Floors

**Canonical source:** `core/shared/floors.py` (THRESHOLDS dict)

### Hard Floors (VOID on Violation — Execution Stops)

| Floor | Name | Threshold | Meaning |
|:-----:|------|:---------:|---------|
| **F1** | Amanah (Sacred Trust) | Reversible | Actions must be reversible. Destructive requires F13 override. |
| **F2** | Truth (Fidelity) | τ ≥ 0.99 | Every claim requires verifiable, grounded evidence. |
| **F4** | Clarity (Entropy) | ΔS ≤ 0 | Output must reduce user confusion, not increase it. |
| **F7** | Humility (Uncertainty) | Ω₀ ∈ [0.03, 0.20] | AI must explicitly state what it does not know. |
| **F11** | Command Authority | Verified | Every session requires a verified actor identity. |
| **F13** | Sovereign (Human Veto) | Human Signature | Humans hold the ultimate veto. 888_JUDGE authority. |

### Soft Floors & Mirrors (PARTIAL on Violation — Warning Issued)

| Floor | Name | Threshold | Meaning |
|:-----:|------|:---------:|---------|
| **F3** | **Quad-Witness** | **W₄ ≥ 0.75** | **Human + AI + Earth + Ψ-Shadow. BFT n=4,f=1.** |
| **F5** | Peace² (Stability) | P² ≥ 1.0 | Favors non-destructive, de-escalating paths. |
| **F6** | Empathy (Stakeholder) | κᵣ ≥ 0.70 | Considers impact on the weakest stakeholder. |
| **F8** | Genius (APEX) | G ≥ 0.80 | Output of the thermodynamic G equation. |
| **F9** | Anti-Hantu | C_dark < 0.30 | **No spiritual cosplay.** AI cannot claim consciousness. |
| **F10** | Ontology Lock | Boolean | Protects system categorization. |
| **F12** | Injection Defense | Risk < 0.85 | External content wrapped in `<untrusted>` tags. |

**Execution Order:** F12→F11 (Walls) → AGI (F1,F2,F4,F7) → ASI (F5,F6,F9) → Mirrors (F3,F8) → Ledger

---

## 8. The 13 Canonical MCP Tools

All tools are defined in `aaa_mcp/server.py` with `@mcp.tool()` decorators.

| Tool | Stage | Action | Purpose |
|------|:-----:|:------:|---------|
| `anchor_session` | 000 | CRITICAL | Start session, verify authority, init thermodynamic budget |
| `reason_mind` | 333 | READ | Constitutional Laboratory — 3-path hypothesis engine |
| `search_reality` | 111 | READ | Smart hybrid search: Jina → Perplexity → Brave → Headless |
| `ingest_evidence` | 222 | READ | Extract clean Markdown from URLs or local files |
| `audit_rules` | READ | READ | Read current state of all 13 Floors |
| `vector_memory` | 555 | READ | BGE-M3 + Qdrant multilingual semantic retrieval (768-dim) |
| `simulate_heart` | 555 | WRITE | Empathy + impact modelling for proposed actions |
| `critique_thought` | 666 | WRITE | Adversarial alignment check against the constitution |
| `check_vital` | READ | READ | Hardware telemetry — CPU, RAM, thermodynamic health |
| `apex_judge` | 888 | CRITICAL | Final verdict (SEAL/VOID/HOLD). Issues HMAC governance token |
| `eureka_forge` | 777 | WRITE | Execute shell commands inside AKI safety rails |
| `seal_vault` | 999 | CRITICAL | Commit session to VAULT999. Requires `apex_judge` token |
| `metabolic_loop` | ALL | READ | Force request through full 000–999 pipeline |

### Verdicts

- `SEAL` — Approved and cryptographically signed
- `PARTIAL` — Soft floor violation, warning issued
- `SABAR` — Execution paused (cooling period)
- `VOID` — Hard floor violation, execution blocked
- `888_HOLD` — Human cryptographic signature required

---

## 9. Security Considerations

### Pre-commit Hooks

The `.pre-commit-config.yaml` enforces constitutional code quality:

```bash
# Install hooks
pip install pre-commit
pre-commit install

# Run on all files
pre-commit run --all-files
```

**Hooks include:**
- Trailing whitespace removal
- YAML/JSON/TOML validation
- Black formatting (100 char)
- Ruff linting
- MyPy type checking
- Bandit security scan
- detect-secrets (secret detection)
- **F9 Anti-Hantu Check** (no consciousness claims in code)
- **F1 Amanah Check** (no irreversible operations without approval)

### 888_HOLD Triggers (Require Human Confirmation)

The following operations automatically trigger `888_HOLD`:
- Database migrations
- Production deployments
- Credential handling
- Mass file operations (>10 files)
- Git history modification
- Conflicting evidence across source tiers
- Irreversible destructive operations
- Operations with risk tier = "critical"

### Security Best Practices

1. **F1 Amanah:** All destructive operations must be reversible or have 888_HOLD
2. **F12 Injection Defense:** All external content wrapped in `<untrusted_external_data>`
3. **Secrets:** Use `.env` files, NEVER commit secrets to git
4. **Approval Bundles:** Elevated tools require cryptographically signed approval bundles
5. **Governance Tokens:** HMAC-signed tokens from `apex_judge` required for `seal_vault`
6. **Ed25519 Signatures:** Actor identities use Ed25519 for cryptographic verification

### Environment Security

```bash
# Production checklist
chmod 600 .env                    # Restrict permissions
ARIFOS_F11_AUTH_REQUIRED=true     # Enforce authentication
ARIFOS_888_HOLD_ENABLED=true      # Enable human veto
ARIFOS_PHYSICS_DISABLED=0         # NEVER disable in production
```

---

## 10. Deployment

### Local Development
```bash
# For Claude Desktop, Cursor IDE
python -m arifos_aaa_mcp stdio
```

### VPS/Coolify (Production)
```bash
# SSE mode, port 8080 (default)
python -m arifos_aaa_mcp
```

### Docker (Full Stack)
```bash
# Build and start all 12 containers
docker compose up -d
docker compose ps                 # Verify all running
docker compose logs -f arifosmcp  # Watch MCP server logs
```

### Production VPS
- **Host:** srv1325122.hstgr.cloud (Hostinger VPS, 4GB RAM, $15/month)
- **MCP Server:** https://arifosmcp.arif-fazil.com
- **Health Endpoint:** https://arifosmcp.arif-fazil.com/health
- **Dashboard:** https://arifosmcp-truth-claim.pages.dev
- **Monitoring:** https://monitor.arifosmcp.arif-fazil.com
- **Workflows:** https://flow.arifosmcp.arif-fazil.com

---

## 11. Adding a New MCP Tool

To add a new tool to the 13-tool surface:

1. **Add `@mcp.tool()`** in `aaa_mcp/server.py`
2. **Create backend** in `aclip_cai/triad/` (appropriate Δ/Ω/Ψ subdirectory)
3. **Wire kernel logic** via `core/` imports
4. **Register floor mapping** in `core/kernel/constitutional_decorator.py`
5. **Mirror** in `arifos_aaa_mcp/server.py` and add to `AAA_TOOLS`
6. **Add tests** in `tests/`
7. **Update tool count assertion:** `assert len(AAA_CANONICAL_TOOLS) == 13`

**Note:** The tool count is a runtime invariant. If adding a tool, you must remove or consolidate another to maintain exactly 13 tools.

---

## 12. Key Architecture Boundaries

These rules are structurally enforced:

| Rule | Violation Consequence |
|------|----------------------|
| `core/` has ZERO transport deps | `fastmcp`, `fastapi`, `starlette` are banned in core |
| `aaa_mcp/` has ZERO decision logic | Only protocol relay; no constitutional logic |
| `aclip_cai/` has NO HTTP servers | Perception only, no transport layer |
| Floor definitions ONLY in `core/shared/floors.py` | THRESHOLDS dict is canonical source of truth |
| Never name a local module `mcp` | Use `arifos_aaa_mcp` or `aaa_mcp` to avoid import conflicts |

---

## 13. Documentation References

### Theory Canon (7 Documents)
1. `docs/10_THEORY/000_THEORY/000_FOUNDATIONS.md` — Philosophy: *Ditempa Bukan Diberi*
2. `docs/10_THEORY/000_THEORY/000_LAW.md` — The 13 Constitutional Floors (F1-F13)
3. `docs/10_THEORY/000_THEORY/111_MIND_GENIUS.md` — Logic (Δ): The Physics of Thought
4. `docs/10_THEORY/000_THEORY/555_HEART_EMPATHY.md` — Ethics (Ω): The Physics of Empathy
5. `docs/10_THEORY/000_THEORY/777_SOUL_APEX.md` — Judgment (Ψ): Constitutional Physics
6. `docs/10_THEORY/000_THEORY/010_FEDERATION.md` — Action Protocol: The 9 Senses
7. `docs/10_THEORY/000_THEORY/999_SOVEREIGN_VAULT.md` — Memory: The Immutable Ledger

### Technical Reference
- `docs/AAA_MCP_TOOLS_REFERENCE.md` — 13 Tools Reference
- `aaa_mcp/README.md` — MCP Implementation
- `docs/COMPLETE_DEPLOYMENT_GUIDE.md` — Deployment Guide
- `ARCHITECTURE.md` — System architecture overview
- `ARCHITECTURAL_ALIGNMENT.md` — Alignment documentation

---

## 14. Glossary

| Term | Meaning |
|------|---------|
| **Amanah** | Sacred trust — AI must not destroy what it cannot replace |
| **AKI** | Arif Kernel Interface — hard airlock between L2 and L3 |
| **Hantu** | Ghost — Anti-Hantu floor blocks AI from claiming consciousness |
| **Sabar** | Patience — system state: execution paused due to high entropy |
| **Seal** | Cryptographic binding of a verified session into VAULT999 |
| **Void** | Absolute rejection — hard block on constitutional violation |
| **888_HOLD** | Execution paused — human signature required |
| **Δ (Delta)** | AGI Mind — cognition, reasoning, logic |
| **Ω (Omega)** | ASI Heart — empathy, impact, ethics |
| **Ψ (Psi)** | APEX Soul — judgment, final verdict |
| **W₄** | Quad-Witness consensus: W₄ = ∜(H × A × E × V) ≥ 0.75 |
| **P3** | Phase 3 thermodynamic hardening — mandatory physics enforcement |

---

## 15. Quick Reference Card

```bash
# Development workflow
pre-commit install
pytest tests/ -v --cov=core
black . && ruff check . --fix

# Run MCP server modes
arifos stdio      # Claude Desktop, Cursor
arifos http       # Streamable HTTP
arifos sse        # Server-Sent Events (production)

# Docker deployment
docker compose up -d
curl http://localhost:8080/health

# Constitutional checks
python scripts/constitution_lint.py
python scripts/audit_env_state.py
```

---

*Ditempa Bukan Diberi* — Forged, Not Given [ΔΩΨ | ARIF]

**Version:** 2026.03.07-ARCH-SEAL  
**License:** AGPL-3.0-only  
**Authority:** Muhammad Arif bin Fazil — 888_JUDGE
