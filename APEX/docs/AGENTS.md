# AGENTS.md — arifOS Constitutional MCP Server

> **Motto:** *Ditempa Bukan Diberi* — Forged, Not Given [ΔΩΨ | ARIF]

This file provides essential guidance for AI coding agents working with the arifOS MCP (Model Context Protocol) server codebase.

---

## Project Overview

**arifOS** is the world's first production-grade Constitutional AI Governance System. It provides mathematical enforcement of ethical constraints through 13 stationary constitutional floors (F1-F13), implementing the Trinity Architecture (Δ·Ω·Ψ) that separates AGI Mind, ASI Heart, and APEX Soul.

**Key Identity:**
- **Name:** arifOS MCP Server (`arifosmcp`)
- **Version:** 2026.3.12-FORGED (YYYY.MM.DD format)
- **License:** AGPL-3.0-only
- **Author:** Muhammad Arif bin Fazil
- **Repository:** https://github.com/ariffazil/arifosmcp
- **PyPI:** `pip install arifosmcp`

**Core Purpose:** arifOS acts as the "TCP layer for AI agents" — wrapping every MCP tool call in a mathematically enforced constitution, guaranteeing that what arrives at the real world is ordered, verified, and reversible.

---

## Value Proposition for CLI Coding Agents

What `arifosmcp` gives any CLI coding agent:

1. **Constitutional guardrails as a shared service**
   Every agent (Claude Code, Kimi, Gemini CLI, Antigravity) gets the same 13-floor validation layer via MCP — instead of each one having zero governance or implementing their own ad-hoc safety checks.

2. **Cross-agent audit trail (VAULT999)**
   Every tool call, decision, and checkpoint gets hash-chained into a single immutable ledger. You can trace which agent did what and why — across all your CLI tools, in one place.

3. **Structured reasoning tools on demand**
   The Gen3 tools (`reason_mind`, `critique_thought`, `eureka_forge`, `apex_judge`) give any agent a structured thinking pipeline it wouldn't otherwise have — useful before destructive ops like mass file changes, migrations, or deploys.

4. **F11 Command Auth — identity verification**
   High-stakes actions (git force-push, db migrations, secret access) get held at `888_HOLD` until explicitly confirmed. No agent can silently do irreversible things.

5. **Consistent behavior across agents**
   Right now Claude Code, Kimi, and Gemini CLI all behave differently on the same task. With `arifosmcp` as a shared MCP layer, they all run through the same constitutional floors — same truth threshold (F2 ≥ 0.99), same humility bound (F7 = 0.04), same anti-hallucination pressure.

6. **The agent doesn't need to be smart about safety — the MCP is**
   A weak or cheap model (Haiku, flash) calling `apex_judge` before committing gets the same governance as a frontier model. The intelligence lives in the server, not in the agent.

> **TL;DR:** It's a governance middleware — any CLI agent that connects gets reversibility checks, audit trails, and structured judgment without needing those capabilities baked in natively.

---


## Technology Stack

### Runtime Environment
- **Python:** 3.12+ (strict requirement)
- **Package Manager:** `uv` (preferred) or `pip`
- **Virtual Environment:** `.venv/` (managed by uv)

### Core Dependencies
| Category | Libraries |
|----------|-----------|
| **MCP Framework** | `fastmcp==3.1.0`, `mcp>=1.0.0` |
| **Web Framework** | `fastapi>=0.104.1`, `uvicorn[standard]>=0.24.0`, `starlette>=0.30.0` |
| **Data & Validation** | `pydantic>=2.0.0`, `numpy>=1.20.0` |
| **AI/ML** | `sentence-transformers>=2.2.0`, `scikit-learn>=1.3.0` |
| **Vector Stores** | `qdrant-client>=1.7.0` (primary), `chromadb>=0.5.0` (legacy) |
| **Databases** | `asyncpg>=0.29.0` (PostgreSQL), `redis>=5.0.0` |
| **Web Scraping** | `playwright>=1.40.0`, `beautifulsoup4>=4.12.0`, `duckduckgo-search>=5.0.0` |
| **Observability** | `prometheus-client>=0.19.0`, `rich>=13.7.0` |
| **HTTP Client** | `httpx>=0.25.0`, `requests>=2.31.0` |

### Infrastructure (Docker Compose Stack)
| Service | Purpose |
|---------|---------|
| `arifosmcp` | Constitutional MCP kernel |
| `postgres` | VAULT999 ledger (PostgreSQL 16) |
| `redis` | Session persistence (Redis 7) |
| `qdrant` | Vector memory store |
| `traefik` | Edge router with auto SSL |
| `prometheus` | Metrics collection |
| `grafana` | Observability dashboards |
| `ollama` | Local LLM inference |
| `openclaw` | Multi-channel gateway |
| `n8n` | Workflow automation |
| `webhook` | Auto-deployment hooks |
| `headless_browser` | Browser-based reality fetching |

---

## Project Structure

```
arifosmcp/
├── arifosmcp/                 # Main Python package
│   ├── runtime/               # Machine layer runtime (FastMCP transport)
│   │   ├── server.py          # Canonical server entrypoint
│   │   ├── tools.py           # Core tool implementations
│   │   ├── orchestrator.py    # Metabolic loop router
│   │   ├── phase2_tools.py    # External capability tools
│   │   ├── prompts.py         # MCP prompts
│   │   ├── resources.py       # MCP resources
│   │   ├── rest_routes.py     # HTTP REST endpoints
│   │   └── __main__.py        # CLI entrypoint
│   ├── tools/                 # MCP tool definitions
│   │   └── lsp_tools.py       # LSP integration tools
│   ├── transport/             # Transport implementations
│   │   └── acp_server.py      # Agent Client Protocol
│   ├── intelligence/          # Intelligence (3E: Exploration, Entropy, Eureka)
│   ├── sites/                 # Static sites (APEX dashboard)
│   └── VAULT999/              # Local vault storage
│
├── core/                      # Constitutional kernel (pure logic)
│   ├── shared/                # Shared utilities
│   │   ├── floors.py          # 13 Constitutional Floors (F1-F13)
│   │   ├── physics.py         # Thermodynamic calculations
│   │   ├── verdict_contract.py# Verdict definitions
│   │   ├── crypto.py          # Cryptographic utilities
│   │   └── guards/            # Security guards (injection, ontology)
│   ├── governance_kernel.py   # Main governance engine
│   ├── pipeline.py            # Metabolic loop pipeline
│   ├── judgment.py            # Verdict rendering (888_JUDGE)
│   ├── organs/                # Trinity organs (AGI, ASI, APEX)
│   ├── physics/               # Physics engine
│   └── scheduler/             # Metabolic scheduler
│
├── tests/                     # Comprehensive test suite
│   ├── 00_unit/               # Unit tests (~2 min)
│   ├── 01_integration/        # Integration tests (~3 min)
│   ├── 02_mcp_protocol/       # MCP compliance (~2 min)
│   ├── 03_constitutional/     # F1-F13 enforcement (~5 min) ⚠️ CRITICAL
│   ├── 04_adversarial/        # Security tests (~3 min)
│   └── 05_e2e/                # End-to-end (~5 min)
│
├── spec/                      # API specifications
├── infrastructure/            # Docker/config files
├── deployment/                # Deployment scripts
├── scripts/                   # Utility scripts
├── skills/                    # Agent skills (SKILL.md files)
└── AGENTS/                    # Agent guidance hub

├── pyproject.toml             # Python package config
├── fastmcp.json               # FastMCP server config
├── docker-compose.yml         # Full civilization stack
├── Dockerfile.optimized       # Production Dockerfile
├── Makefile                   # Deployment commands
├── CONSTITUTION.md            # 13 Floors reference
└── README.md                  # Human documentation
```

---

## Build and Test Commands

### Development Setup
```bash
# Install with uv (recommended)
cd /c/arifosmcp
uv pip install -e ".[dev]"

# Or with pip
pip install -e ".[dev]"
```

### Running Tests
```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_constitutional_core.py -v

# Single test
pytest tests/test_constitutional_core.py::test_f2_truth_threshold -v

# With coverage
pytest tests/ --cov=core --cov=arifosmcp --cov-report=html --cov-report=term

# Fast unit tests only
pytest tests/00_unit/ -v --tb=short

# Constitutional tests (CRITICAL - must pass)
pytest tests/03_constitutional/ -v

# Skip slow/integration tests
pytest tests/ -v -m "not slow and not integration"
```

### Running the Server
```bash
# Development mode (stdio)
python -m arifosmcp.runtime stdio

# HTTP mode
python -m arifosmcp.runtime http

# With custom port
PORT=8080 python -m arifosmcp.runtime http
```

### Docker Deployment
```bash
# Quick start with Docker
docker compose up -d

# Check health
curl http://localhost:8080/health

# View logs
docker logs -f arifosmcp_server

# Makefile shortcuts
make fast-deploy      # Fast redeploy (2-3 min)
make reforge          # Full rebuild (10-15 min)
make hot-restart      # Config-only restart (10s)
make health           # Health check
make logs             # Follow logs
```

---

## Code Style Guidelines

### Python Style
- **Line Length:** 100 characters (configured in pyproject.toml)
- **Formatter:** `ruff` (preferred) or `black`
- **Linter:** `ruff` with E, F, I, UP, N, B rules enabled
- **Type Checker:** `mypy` (strict for core governance modules)

### Running Linting
```bash
# Lint with ruff
ruff check arifosmcp/runtime core tests/

# Format with ruff
ruff format arifosmcp/runtime core tests/

# Type check with mypy
mypy arifosmcp/transport tests
```

### Import Conventions
```python
from __future__ import annotations  # Always first

# Standard library
import os
from pathlib import Path

# Third-party
from fastmcp import FastMCP
from pydantic import BaseModel

# arifOS modules
from core.shared.floors import THRESHOLDS
from arifosmcp.runtime.tools import register_tools
```

### Naming Conventions
- **Files:** `snake_case.py`
- **Classes:** `PascalCase`
- **Functions/Variables:** `snake_case`
- **Constants:** `UPPER_SNAKE_CASE`
- **Private:** `_leading_underscore`

---

## Testing Instructions

### Test Philosophy
Every test must answer: **"Does the system govern AI correctly?"**

Tests verify that arifOS's 13 Constitutional Floors are actually enforced, not just that code runs.

### Critical Test Categories

#### 1. Constitutional Tests (MUST PASS)
Located in `tests/03_constitutional/`. These verify F1-F13 enforcement:
- `test_f1_amanah.py` — Reversibility enforcement
- `test_f2_truth.py` — Anti-hallucination
- `test_f7_humility.py` — Gödel uncertainty band [0.03, 0.05]
- `test_f12_defense.py` — Injection protection

#### 2. Unit Tests
Located in `tests/00_unit/`. Fast, isolated tests for individual components.

#### 3. Integration Tests
Located in `tests/01_integration/`. Component interaction tests.

#### 4. MCP Protocol Tests
Located in `tests/02_mcp_protocol/`. Transport and protocol compliance.

#### 5. Adversarial Tests
Located in `tests/04_adversarial/`. Security and attack resistance.

### Writing Meaningful Tests

**❌ Bad Test (Meaningless):**
```python
def test_imports():
    import arifosmcp
    assert True
```

**✅ Good Test (Meaningful):**
```python
def test_ungrounded_claim_gets_void():
    """F2: Claims without evidence must be VOIDed."""
    engine = JudgmentEngine()
    verdict = engine.evaluate({
        "action": "search_reality",
        "query": "The moon is made of cheese",
        "evidence": []
    })
    assert verdict.status == "VOID"
    assert "F2_TRUTH" in verdict.violations
```

### Coverage Requirements
- **Minimum:** 80% coverage
- **Core Governance:** 95% coverage (`governance_kernel.py`, `judgment.py`)
- **Constitutional Tests:** Must ALL pass for deployment

### Test Fixtures
Key fixtures in `conftest.py`:
- `disable_physics_globally` — Disables physics for performance
- `aaa_client` — In-memory MCP client for testing
- `require_postgres` — Skips if PostgreSQL unavailable
- `require_redis` — Skips if Redis unavailable

---

## arifosmcp — Complete Canon (v2026.03.14)

### Two MCP Servers
| Server | Entry | Purpose |
| :--- | :--- | :--- |
| **arifos** | `arifosmcp.runtime` | Constitutional governance kernel |
| **aclip-cai** | `arifosmcp.intelligence.cli` | Local ops console for AI agents |

### 11 Canonical Mega-Tools

All capability is consolidated into **11 Mega-Tools** across three layers. Each mega-tool exposes multiple modes via the `mode` parameter.

| Layer | Mega-Tool | Stage | Trinity | Modes | What it does |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **⚖️ GOVERNANCE** | **`init_anchor`** | `000_INIT` | Ψ PSI | `init`, `revoke`, `refresh` | Constitutional Airlock — establish, revoke, or refresh governed session |
| | **`arifOS_kernel`** | `444_ROUTER` | Δ/Ψ | `kernel`, `status` | Metabolic Conductor — primary entry point for complex queries |
| | **`apex_soul`** | `888_JUDGE` | Ψ PSI | `judge`, `rules`, `validate`, `hold`, `armor`, `notify`, `probe` | Final Authority — verdicts, defense, floor inspection |
| | **`vault_ledger`** | `999_VAULT` | Ψ PSI | `seal`, `verify` | Immutable Memory — permanent decision recording |
| **🧠 INTELLIGENCE** | **`agi_mind`** | `333_MIND` | Δ DELTA | `reason`, `reflect`, `forge` | Logic & Synthesis — core reasoning and hypothesis generation |
| | **`asi_heart`** | `666_HEART` | Ω OMEGA | `critique`, `simulate` | Ethics & Simulation — safety, empathy, consequence modeling |
| | **`engineering_memory`** | `555_MEMORY` | Ω OMEGA | `engineer`, `query`, `recall`, `write`, `generate` | Technical Execution — governed autonomous engineering |
| **⚙️ MACHINE** | **`physics_reality`** | `111_SENSE` | Δ DELTA | `search`, `ingest`, `compass`, `atlas` | Environmental Grounding — Earth-Witness fact acquisition |
| | **`math_estimator`** | `444_ROUTER` | Δ DELTA | `cost`, `health`, `vitals` | Thermodynamic Vitals — quantitative health metrics |
| | **`code_engine`** | `M-3_EXEC` | ALL | `fs`, `process`, `net`, `tail`, `replay` | Computational Execution — system-level hygiene |
| | **`architect_registry`** | `M-4_ARCH` | Δ DELTA | `register`, `list`, `read` | System Definition — tool and resource discovery |

> **Total:** 11 Mega-Tools enforcing all 13 Constitutional Floors (F1-F13) through the Trinity Architecture (ΔΩΨ).

> **Legacy Tools:** The previous 26-tool surface has been consolidated into the 11 Mega-Tools above. Legacy names (e.g., `apex_judge`, `vault_seal`, `agi_reason`) are redirected to the appropriate mega-tool modes.

### 10 Canonical Resources

| URI | Auth | What it exposes |
| :--- | :--- | :--- |
| `arifos://status/vitals` | None | Current health, capability map, degraded components |
| `arifos://governance/floors` | None | Constitutional F1-F13 thresholds and doctrine hooks |
| `arifos://bootstrap/guide` | None | Startup path, canonical sequence, example payloads |
| `arifos://contracts/tools` | None | Tool contract table: risk, auth, mutability |
| `arifos://caller/state` | Anchored | Current caller state, allowed/blocked tools |
| `schema://tools/input` | None | Canonical JSON Schema input specs |
| `schema://tools/output` | None | Canonical RuntimeEnvelope output schema |

> **Legacy Aliases:** `canon://index`, `canon://contracts`, `canon://states` maintained for backward compatibility.

> **Full Specification:** See [SPEC.md](./SPEC.md) for normative protocol profile.

### 4 Prompt Templates
One per public tool — each describes when and how to invoke it.

---

## ⚖️ The 13 Constitutional Floors

| # | Name | Type | Threshold | Enforces |
|---|------|------|-----------|----------|
| **F1** | Amanah | Hard | ≥ 0.5 | Reversibility / audit mandate |
| **F2** | Truth | Hard | ≥ 0.99 | Information fidelity |
| **F3** | Tri-Witness | Mirror | ≥ 0.95 | Human·AI·Earth consensus |
| **F4** | ΔS Clarity | Hard | ≤ 0 | Entropy reduction |
| **F5** | Peace² | Soft | ≥ 1.0 | Non-destructive power |
| **F6** | κᵣ Empathy | Soft | ≥ 0.70 | Serves weakest stakeholder |
| **F7** | Ω₀ Humility | Hard | 0.03–0.20 | States uncertainty |
| **F8** | G Genius | Mirror | ≥ 0.80 | Internal coherence $A \times P \times X \times E^2$ |
| **F9** | C_dark | Hard | < 0.30 | Dark cleverness limit |
| **F10** | Ontology | Wall | LOCK | No consciousness/soul claims |
| **F11** | Command Auth | Hard | LOCK | Nonce-verified identity |
| **F12** | Injection | Wall | < 0.85 | Block adversarial control |
| **F13** | Sovereign | Veto | HUMAN | Human final authority |

---

## 🧬 Trinity Architecture (ΔΩΨ)

| Engine | Stages | Floors | Personas | Role |
| :--- | :--- | :--- | :--- | :--- |
| **Δ Delta (AGI Mind)** | 000, 111, 333 | F2, F4, F7, F8 | **ARCHITECT**, **ENGINEER** | Reason, sense, ground |
| **Ω Omega (ASI Heart)** | 555, 666 | F5, F6, F9 | **AUDITOR** | Empathy, memory, ethics |
| **Ψ Psi (APEX Soul)** | 777, 888, 999 | F1, F3, F10, F11, F13 | **VALIDATOR**, **ORCHESTRATOR** | Forge, judge, seal |

### The Five Governance Personas
Each persona carries a specific **Scar-Weight ($W_{beban}$)** to protect the system:
- **ARCHITECT:** "Should this exist?" — Protects coherence and long-term truth.
- **ENGINEER:** "Can we make it work?" — Protects execution reality.
- **AUDITOR:** "What could break?" — Protects integrity and compliance.
- **VALIDATOR:** "Is it actually true?" — Protects evidence and reproducibility.
- **ORCHESTRATOR:** "In what order?" — Protects flow control and reversibility.

### VAULT999 — Merkle Ledger
Append-only JSONL. Every entry: `session_id` → `seal_hash` (SHA-256) → `chain_hash` (prev + seal). Tamper = chain break. `verify_vault_ledger` detects it.

---

## 🦾 Effect on CLI Agents, LLMs, and Humans

### For CLI Agents (Claude Code, Gemini CLI, Kimi)
- **Pre-Validation**: Every tool call can be pre-validated through `arifOS_kernel` before execution.
- **888_HOLD**: Irreversible ops (delete, force-push, drop tables) are physically gated.
- **Persistent Context**: `session_memory` provides governed continuity across restarts.

### For LLMs (Any Model, Any Tier)
- **Server-Side Intelligence**: A Haiku model calling `apex_judge` gets the same constitutional verdict as a frontier model.
- **Reduced Hallucination**: F2 (truth) and F7 (humility) floors structurally suppress fabrication.
- **Ontology Lock**: F10 wall blocks models from claiming consciousness or making existential assertions.

### For Humans
- **F13 Sovereign**: Human veto is structurally final, not advisory.
- **Full Accountability**: Every AI action leaves a tamper-evident ledger entry in VAULT999.
- **Consensus**: Tri-Witness (Human·AI·Earth) means no unilateral AI decision can be sealed without human witness.

---

*Ditempa Bukan Diberi — Forged, Not Given [ΔΩΨ | ARIF]*

**Version:** 2026.03.14-CANON  
**Constitutional Status:** 13/13 Floors Enforced

