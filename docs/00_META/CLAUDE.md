# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**Project:** arifOS — Constitutional AI Governance System
**Package:** `arifos` v2026.3.10 (PyPI)
**Python:** >=3.12 | **License:** AGPL-3.0-only
**Motto:** *DITEMPA BUKAN DIBERI — Forged, Not Given*

---

## Critical: Logging in MCP

For STDIO transport, writing to `stdout` will break the server.

- Use `sys.stderr` or a logging library configured for `stderr`.
- Never use naked `print()` calls in tool implementations.

---

## Build & Dev Commands

```bash
# Install (editable with dev dependencies)
pip install -e ".[dev]"

# Run MCP Server — canonical entry point (default: SSE)
python -m arifosmcp.runtime              # SSE (default for VPS/remote)
python -m arifosmcp.runtime stdio        # stdio (Claude Desktop, local agents)
python -m arifosmcp.runtime http         # Streamable HTTP at /mcp

# CLI entry points (from pyproject.toml [project.scripts])
arifos                                # canonical (same as python -m arifosmcp.runtime)
aaa-mcp                               # unified entry point
aclip-cai health                      # ACLIP infrastructure CLI

# Docker
docker build -t arifos .
docker run -e PORT=8080 -p 8080:8080 arifos
```

## Testing

```bash
# Full suite
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=core --cov=arifosmcp.runtime --cov-report=html

# Single file / single test
pytest tests/test_quick.py -v
pytest tests/test_core_foundation.py::test_function_name -v

# By marker
pytest -m constitutional       # F1-F13 floor tests
pytest -m integration          # Integration tests
pytest -m slow                 # Long-running tests

# E2E pipeline
pytest tests/test_e2e_all_tools.py -v
pytest tests/test_e2e_core_to_aaa_mcp.py -v
```

Async mode is `auto` in pyproject.toml — async test functions are auto-detected without `@pytest.mark.asyncio` decorators. Test paths: `tests/`.

## Linting & Formatting

```bash
black core/ arifosmcp.runtime/ arifosmcp.intelligence/ --line-length=100
ruff check core/ arifosmcp.runtime/ arifosmcp.intelligence/
ruff check core/ arifosmcp.runtime/ arifosmcp.intelligence/ --fix
mypy core/ --ignore-missing-imports
```

Black: 100 char line length. Ruff: py310 target, excludes `archive/**`, `tests/**`. MyPy: strict on `core.governance_kernel`, `core.judgment`, `core.pipeline`, `core.organs.*`, `core.shared.*`.

---

## Architecture

### Four-Layer Stack: PyPI Surface → Machine (Transport) → Intelligence (3E) → Governance Kernel

```text
core/                      → KERNEL (decision logic, zero transport deps)
├── governance_kernel.py   → GovernanceKernel (unified Ψ state, thermodynamics)
├── judgment.py            → judge_cognition, judge_empathy, judge_apex
├── pipeline.py            → Constitutional pipeline orchestrator (forge/quick)
├── telemetry.py           → 30-day locked adaptation with drift tracking
├── uncertainty_engine.py  → Uncertainty quantification
├── kernel/                → Constitutional decorator, evaluator, stage orchestrator,
│                            engine adapters, MCP tool service, transport kernel
├── shared/                → Foundation: physics, atlas, types, crypto, floors (THRESHOLDS dict),
│                            routing, formatter, mottos, nudge, context_template
├── organs/                → 5 enforcement organs (_0_init → _4_vault)
├── enforcement/           → Refusal builder, routing
├── config/                → Runtime configuration
└── physics/               → Thermodynamic calculations

arifosmcp.intelligence/                 → INTELLIGENCE (3E: Exploration → Entropy → Eureka)
├── tools/                 → 9-Sense tools (fs_inspector, system_monitor, net_monitor,
│                            financial_monitor, thermo_estimator, reality_grounding, etc.)
│   └── logic/             → Thermodynamic Budgeting, Vault Logger
└── dashboard/             → React dashboard (Cloudflare Pages)

arifosmcp.runtime/            → MACHINE LAYER (Transport Hub)
├── server.py              → FastMCP server with 13 tools (@mcp.tool decorators)
├── __main__.py            → CLI entry: default SSE, reads HOST/PORT env vars
├── bridge.py              → Secure airlock between Hub and Kernel
├── contracts.py           → Single source of truth for tool surface and guards
├── rest_routes.py         → REST route definitions
├── models.py              → v1.0.0 Final Canonical Output Schema
├── orchestrator.py        → Metabolic Loop Stage 444 logic
├── philosophy.py          → 33-quote deterministic wisdom registry
└── fastmcp_ext/           → FastMCP extensions (discovery, middleware, transports)

333_APPS/                  → 8-Layer Application Stack (L0 Kernel → L7 AGI)
VAULT999/                  → Immutable ledger storage (AAA_HUMAN, BBB_LEDGER, CCC_CANON)
```

**Critical boundaries:**

- `core/` has zero transport dependencies. `arifosmcp/runtime/` has zero decision logic. Never cross this boundary.
- `arifosmcp.runtime/` is the canonical PyPI-facing surface and transport adapter.
- `arifosmcp.intelligence/` provides sensory grounding and hardware-level instrumentation.

### Data Flow: How a tool call reaches the kernel

```text
Client → arifosmcp.runtime (@mcp.tool) → bridge.py → core/organs/* → core/shared/floors.py
```

### Trinity Architecture (ΔΩΨ)

Three engines process in isolation, then converge:

```text
000_INIT → AGI(Δ) Mind → ASI(Ω) Heart → APEX(Ψ) Soul → 999_VAULT
             111-333        555-666          888              999
```

- **AGI (Δ/Delta)**: Reasoning — truth (F2), clarity (F4), humility (F7), genius (F8)
- **ASI (Ω/Omega)**: Safety — amanah (F1), peace (F5), empathy (F6), anti-hantu (F9)
- **APEX (Ψ/Psi)**: Judgment — tri-witness (F3), ontology (F10), authority (F11), injection (F12), sovereignty (F13)

### 5-Organ Kernel (`core/organs/`)

Importable via `from core.organs import ...`:

| Organ  | Module        | Actions                                   | Stages  |
| ------ | ------------- | ----------------------------------------- | ------- |
| init   | `_0_init.py`  | `init`, `scan_injection`, `verify_auth`   | 000     |
| mind   | `_1_agi.py`   | `sense`, `think`, `reason`                | 111-333 |
| heart  | `_2_asi.py`   | `empathize`, `align`                      | 555-666 |
| soul   | `_3_apex.py`  | `sync`, `forge`, `judge`                  | 444-888 |
| memory | `_4_vault.py` | `seal`, `query`, `verify`                 | 999     |

---

## 13 MCP Tools (Canonical UX Verbs)

All defined in `arifosmcp.runtime/server.py` with `@mcp.tool()` decorators.

| Tool (UX Verb)     | Lane    | Stage   | Floors          | Purpose                               |
| ------------------ | ------- | ------- | --------------- | ------------------------------------- |
| `arifos_anchor_session` | Δ Delta | 000     | F11, F12, F13   | Session ignition & injection defense  |
| `reason_mind`      | Δ Delta | 333     | F2, F4, F7, F8  | AGI cognition                         |
| `vector_memory`    | Ω Omega | 555     | F4, F7, F13     | Associative memory traces             |
| `simulate_heart`   | Ω Omega | 666     | F4, F5, F6      | Stakeholder impact & care constraints |
| `critique_thought` | Ω Omega | 666     | F4, F7, F8      | 7-organ alignment & bias critique     |
| `apex_judge`       | Ψ Psi   | 888     | F1-F13          | Sovereign verdict synthesis           |
| `eureka_forge`     | Ψ Psi   | 777     | F1, F11, F12    | Sandboxed action execution            |
| `seal_vault`       | Ψ Psi   | 999     | F1, F3, F10     | Immutable ledger commit               |
| `search_reality`   | Δ Delta | 111     | F2, F4, F12     | Web grounding                         |
| `ingest_evidence`  | Δ Delta | 222     | F2, F4, F12     | Raw evidence content retrieval        |
| `audit_rules`      | Δ Delta | 333     | F2, F8, F10     | Rule & governance audit checks        |
| `check_vital`      | Ω Omega | 000     | F4, F5, F7      | System health & vital signs           |
| `arifOS_kernel`    | ALL     | 444     | F1-F13          | Consolidated metabolic loop           |

All tools return the **v1.0.0 Final Canonical Output Schema** (`RuntimeEnvelope`).

---

## Constitutional Floors (F1-F13)

13 safety rules: 9 Floors + 2 Mirrors + 2 Walls. Hard floors → VOID (block). Soft floors → PARTIAL (warn).

| Floor | Name                   | Type   | Threshold |
| ----- | ---------------------- | ------ | --------- |
| F1    | Amanah (Reversibility) | Hard   | LOCKED    |
| F2    | Truth                  | Hard   | τ ≥ 0.99  |
| F3    | Tri-Witness            | Mirror | ≥ 0.95    |
| F4    | Clarity (ΔS)           | Hard   | ΔS ≤ 0    |
| F5    | Peace²                 | Soft   | ≥ 1.0     |
| F6    | Empathy (κᵣ)           | Soft   | κᵣ ≥ 0.70 |
| F7    | Humility (Ω₀)          | Hard   | 0.03–0.05 |
| F8    | Genius (G)             | Mirror | G ≥ 0.80  |
| F9    | Anti-Hantu (C_dark)    | Soft   | < 0.30    |
| F10   | Ontology               | Wall   | LOCKED    |
| F11   | Command Auth           | Wall   | LOCKED    |
| F12   | Injection Defense      | Hard   | < 0.85    |
| F13   | Sovereign              | Veto   | HUMAN     |

---

## Key Conventions

### Import Namespacing

- `arifosmcp.runtime.*` — canonical transport hub (PyPI surface)
- `arifosmcp.intelligence.*` — intelligence layer (tools, logic)
- `core.*` — kernel imports (`from core.shared.physics import W_3`)
- `mcp.*` — external MCP SDK.
- `fastmcp.*` — FastMCP v3.1.0 framework

### Source Verification for Constitutional Claims

Before making constitutional claims, verify against PRIMARY sources:

1. **PRIMARY (Required):** `spec/*.json`, canon documents (SEALED status)
2. **SECONDARY:** `core/*.py`, `arifosmcp/runtime/contracts.py` (implementation reference)
3. **TERTIARY:** `docs/*.md`, `README.md` (informational, may lag behind PRIMARY)

---

## 888_HOLD Triggers (High-Stakes Operations)

Require explicit user confirmation:

- **Database migrations** — Irreversible system changes
- **Production deployments** — Safety-critical operations
- **Credential/secret handling** — Identity verification required
- **Git history modification** — Remote authority required
- **Conflicting evidence across source tiers** — Pause for consensus

**Protocol**: List consequences → State irreversibles → Ask "yes, proceed" → Wait for confirmation → Execute with logging.

---

## Deployment

| Target            | Command                                                      | Notes                        |
| ----------------- | ------------------------------------------------------------ | ---------------------------- |
| Local (stdio)     | `python -m arifosmcp.runtime stdio`                             | Claude Desktop, Cursor IDE   |
| VPS/Coolify (SSE) | `python -m arifosmcp.runtime`                                   | Default transport, port 8080 |
| Docker            | `docker build -t arifos . && docker run -p 8080:8080 arifos` |                              |

**Live endpoints:**

- Health: `https://mcp.arif-fazil.com/health`
- SSE: `https://mcp.arif-fazil.com/sse`
- MCP: `https://mcp.arif-fazil.com/mcp`

> ⚠️ **DEPRECATED**: `arifosmcp.arif-fazil.com` is stale (v2026.04.07, 11 tools). Always use `mcp.arif-fazil.com` (v2026.4.13, 20 tools).
>
> ⚠️ **DEPRECATED TOOL NAMES** (do not use):
> `arifos_anchor_session` → `arifos_init` | `arifos_execute_judge` → `arifos_judge` | `arifos_forge_judge_check` → `arifos_judge(dry_run=True)` | `arifos_forge_execute` → `arifos_forge(dry_run=False)` | `arifos_perform_economic_audit` → `arifos_ops(mode="economic_audit")` | `arifos_verify_location` → `arifos_sense(mode="location")` | `arifos_monitor_metabolism` → `arifos_ops(mode="metabolism")` | `arifos_get_vault_data` → `arifos_vault(mode="read")`

---

**Version:** v2026.3.10 | **Repo:** <https://github.com/ariffazil/arifosmcp>
