# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**Project:** arifOS — Constitutional AI Governance System
**Package:** `arifos` v2026.2.28 (PyPI)
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
python -m arifos_aaa_mcp              # SSE (default for VPS/remote)
python -m arifos_aaa_mcp stdio        # stdio (Claude Desktop, local agents)
python -m arifos_aaa_mcp http         # Streamable HTTP at /mcp

# Compatibility shim (still supported, default: SSE)
python -m aaa_mcp                     # SSE
python -m aaa_mcp stdio               # stdio
python -m aaa_mcp rest                # REST API bridge

# CLI entry points (from pyproject.toml [project.scripts])
arifos                                # canonical (same as python -m arifos_aaa_mcp)
aaa-mcp                               # compat shim
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
pytest tests/ -v --cov=core --cov=aaa_mcp --cov-report=html

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
black aaa_mcp/ core/ arifos_aaa_mcp/ aclip_cai/ --line-length=100
ruff check aaa_mcp/ core/ arifos_aaa_mcp/ aclip_cai/
ruff check aaa_mcp/ core/ arifos_aaa_mcp/ aclip_cai/ --fix
mypy core/ --ignore-missing-imports
```

Black: 100 char line length. Ruff: py310 target, excludes `archive/**`, `tests/**`. MyPy: strict on `core.governance_kernel`, `core.judgment`, `core.pipeline`, `core.organs.*`, `core.shared.*`.

---

## Architecture

### Four-Layer Stack: PyPI Surface → Transport → Intelligence → Kernel

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

aclip_cai/                 → INTELLIGENCE (triad backend + 9-sense tools)
├── triad/                 → Trinity backend: delta/ (anchor, reason, integrate),
│                            omega/ (respond, validate, align), psi/ (forge, audit, seal)
├── core/                  → Lifecycle, Floor Audit, Vault Logger, Thermo-Budgeting,
│                            kernel, federation, eval suite, amendment, mcp_server
├── tools/                 → 9-Sense tools (fs_inspector, system_monitor, net_monitor,
│                            financial_monitor, thermo_estimator, reality_grounding, etc.)
└── dashboard/             → React dashboard (Cloudflare Pages)

aaa_mcp/                   → TRANSPORT ADAPTER (FastMCP surface, NO decision logic)
├── server.py              → FastMCP server with 13 tools (@mcp.tool decorators)
├── __main__.py            → CLI entry: stdio/sse/http dispatcher (compat shim, rest via rest.py)
├── rest.py                → REST API bridge
├── protocol/              → Tool registry, schemas, naming, capabilities, tool graph
├── external_gateways/     → brave_client.py, perplexity_client.py
├── guards/                → injection_guard, ontology_guard
├── sessions/              → Session ledger, dependency tracking
├── services/              → constitutional_metrics, redis_client
├── infrastructure/        → rate_limiter, logging, monitoring
└── vault/                 → Audit logging adapter

arifos_aaa_mcp/            → CANONICAL EXTERNAL PACKAGE (PyPI entry point)
├── server.py              → create_aaa_mcp_server() — imports aaa_mcp + aclip_cai
├── __main__.py            → CLI: default SSE, reads HOST/PORT env vars
├── governance.py          → 13-LAW catalog, tool-to-dial mappings, axioms
├── contracts.py           → require_session, validate_input
├── rest_routes.py         → REST route definitions
└── fastmcp_ext/           → FastMCP extensions (discovery, middleware, transports,
                             telemetry, contracts, dependencies)

333_APPS/                  → 8-Layer Application Stack (L0 Kernel → L7 AGI)
VAULT999/                  → Immutable ledger storage (AAA_HUMAN, BBB_LEDGER, CCC_CANON)
```

**Critical boundaries:**

- `core/` has zero transport dependencies. `aaa_mcp/` has zero decision logic. Never cross this boundary.
- `arifos_aaa_mcp/` is the canonical PyPI-facing surface; `aaa_mcp/` is the internal transport adapter.
- `aclip_cai/triad/` provides the actual backend functions that `aaa_mcp/server.py` calls.

### Data Flow: How a tool call reaches the kernel

```text
Client → arifos_aaa_mcp → aaa_mcp/server.py (@mcp.tool) → aclip_cai/triad/* → core/organs/* → core/shared/floors.py
```

`aaa_mcp/server.py` imports triad functions directly:

```python
from aclip_cai.triad import align, anchor, audit, forge, integrate, reason, respond, seal, validate
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

**Bundle isolation**: AGI and ASI cannot see each other's reasoning until stage 444 (TRINITY_SYNC). DeltaBundle and OmegaBundle are immutable after creation.

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

All defined in `aaa_mcp/server.py` with `@mcp.tool()` decorators. Backend logic in `aclip_cai/triad/`.

| Tool (UX Verb)     | Lane    | Stage   | Floors          | Purpose                               |
| ------------------ | ------- | ------- | --------------- | ------------------------------------- |
| `anchor_session`   | Δ Delta | 000     | F11, F12, F13   | Session ignition & injection defense  |
| `reason_mind`      | Δ Delta | 333     | F2, F4, F7, F8  | AGI cognition (Stage 222 THINK runs internally before Stage 333) |
| `recall_memory`    | Ω Omega | 555     | F4, F7, F13     | Associative memory traces             |
| `simulate_heart`   | Ω Omega | 555     | F4, F5, F6      | Stakeholder impact & care constraints |
| `critique_thought` | Ω Omega | 666     | F4, F7, F8      | 7-organ alignment & bias critique     |
| `apex_judge`       | Ψ Psi   | 888     | F1-F13          | Sovereign verdict synthesis           |
| `eureka_forge`     | Ψ Psi   | 777     | F1, F11, F12    | Sandboxed action execution            |
| `seal_vault`       | Ψ Psi   | 999     | F1, F3, F10     | Immutable ledger — requires `governance_token` from `apex_judge` |
| `search_reality`   | Δ Delta | 111     | F2, F4, F12     | Web grounding (Perplexity/Brave)      |
| `fetch_content`    | Δ Delta | 444     | F2, F4, F12     | Raw evidence content retrieval        |
| `inspect_file`     | Δ Delta | 111     | F1, F4, F11     | Filesystem inspection (read-only)     |
| `audit_rules`      | Δ Delta | 333     | F2, F8, F10     | Rule & governance audit checks        |
| `check_vital`      | Ω Omega | 555     | F4, F5, F7      | System health & vital signs           |

All tools return a standard envelope: `{verdict, stage, session_id, floors, truth, next_actions}`.

Alias compatibility:
- `apex_judge` -> `apex_judge`
- `eureka_forge` -> `eureka_forge`

**Verdicts:** `SEAL` (pass) | `PARTIAL` (soft floor warn) | `SABAR` (hold) | `VOID` (blocked) | `888_HOLD` (needs human)

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

**Execution order:** F12→F11 (Walls) → AGI Floors (F1,F2,F4,F7) → ASI Floors (F5,F6,F9) → Mirrors (F3,F8) → Ledger

**Verdict hierarchy:** `SABAR > VOID > 888_HOLD > PARTIAL > SEAL`

**Floor enforcement:** Two layers exist:

- `core/kernel/constitutional_decorator.py` — kernel-level floor enforcement with evaluator
- `aaa_mcp/core/constitutional_decorator.py` — transport-level decorator for MCP tools

**Floor definitions:** `core/shared/floors.py` (`THRESHOLDS` dict) is the canonical source. Guards in `core/shared/guards/` (injection_guard, ontology_guard).

---

## Key Conventions

### Import Namespacing

- `arifos_aaa_mcp.*` — canonical external package (PyPI surface)
- `aaa_mcp.*` — internal transport adapter
- `aclip_cai.*` — intelligence layer (triad, tools, core)
- `core.*` — kernel imports (`from core.shared.physics import W_3`)
- `core.organs` — organ actions (`from core.organs import sense, think, reason`)
- `mcp.*` — external MCP SDK. **Never** shadow with local modules
- `fastmcp.*` — FastMCP v3.0.2 framework

### Decorator Order (Critical)

```python
@mcp.tool()                    # OUTER — FastMCP registers this
@constitutional_floor("F2")   # INNER — enforcement runs at call time
async def my_tool(...):
```

If reversed, FastMCP registers the unwrapped function and enforcement never runs.

### Lazy Imports for Optional Dependencies

```python
try:
    import numpy as np
except ImportError:
    np = None
```

Never crash on import for optional deps.

### APEX Solver

Uses geometric mean (not arithmetic) for 9-paradox synthesis. GM punishes imbalance more harshly. Target: GM ≥ 0.85, std dev ≤ 0.10.

### Source Verification for Constitutional Claims

Before making constitutional claims, verify against PRIMARY sources:

1. **PRIMARY (Required):** `spec/*.json`, canon documents (SEALED status)
2. **SECONDARY:** `core/*.py`, `aaa_mcp/*.py` (implementation reference)
3. **TERTIARY:** `docs/*.md`, `README.md` (informational, may lag behind PRIMARY)

---

## Adding New Components

### New MCP Tool

1. Add `@mcp.tool()` definition in `aaa_mcp/server.py`
2. Create backend function in appropriate `aclip_cai/triad/` submodule
3. Wire kernel logic via `core/` imports (not inline decision logic)
4. Register floor mapping in `core/kernel/constitutional_decorator.py` FLOOR_ENFORCEMENT dict
5. Mirror in `arifos_aaa_mcp/server.py` and add to `AAA_TOOLS` list
6. Add tests in `tests/`

### New Constitutional Floor

1. Add to `core/shared/floors.py` THRESHOLDS dict
2. Implement guard logic in `core/shared/guards/` if needed
3. Register in `core/kernel/evaluator.py` (PRE_FLOORS, POST_FLOORS, etc.)
4. Add tests in `tests/constitutional/`

### New Core Organ

1. Create `core/organs/_X_name.py`
2. Import only from `core.shared.*` (no cross-organ deps)
3. Return ConstitutionalTensor with floor scores
4. Update `core/organs/__init__.py` exports
5. Add tests in `tests/core/`

---

## Known Gotchas

- **Stage 222 THINK is internal-only**: `think()` is NOT an `@mcp.tool()`. It runs inside `reason_mind` before Stage 333. External callers cannot call it directly. Raw delta drafts (sealed=False) must pass Stage 333 humility audit before they become valid output.
- **seal_vault is token-locked (Amanah Handshake)**: `seal_vault` no longer accepts a `verdict` parameter. Pass `governance_token` from `apex_judge`'s response. A missing or tampered token returns VOID — no ledger entry is written. `_GOVERNANCE_TOKEN_SECRET` in `aaa_mcp/server.py` is hardcoded for dev; must be env-var-sourced in production.
- **F4 (Clarity) is now a Hard floor**: Moved from SOFT_FLOORS to HARD_FLOORS in `core/kernel/evaluator.py`. Responses that increase entropy (ΔS > 0) now return VOID, not PARTIAL. This may cause new test failures in suites that relied on PARTIAL for high-entropy outputs.
- **Namespace collision**: Never name a local package `mcp`. Local code is `aaa_mcp/`. The `mcp/` directory at repo root (if present) is Docker configs, NOT the SDK.
- **Dual entry points**: `arifos_aaa_mcp` (canonical, default SSE) vs `aaa_mcp` (compat shim, default SSE). Both call `aaa_mcp/server.py` but `arifos_aaa_mcp` adds governance wrappers.
- **`codebase/` removed**: Was deleted in v2026.2.15 consolidation. All logic now lives in `core/`, `aclip_cai/`, and `aaa_mcp/`. Some docs/comments still reference it.
- **F4/F6 numbering**: Differs between some older docs and `core/shared/floors.py`. Verify against `aaa_mcp/server.py` floor mappings as source of truth.
- **Windows environment**: Use PowerShell. `$env:` syntax breaks in nested `-Command` strings.
- **pyproject.toml packages**: Must NOT include `mcp*` (would re-shadow the SDK).
- **`.mcp.json` (root)**: Deprecated. Active config is `.claude/mcp.json`.
- **Copilot instructions** (`.github/copilot-instructions.md`): References stale `codebase/` paths. Use this CLAUDE.md as source of truth.
- **vault_seal**: `result["seal"]` KeyError is pre-existing in some code paths.
- **vault999.jsonl is tracked**: Despite `VAULT999/*.jsonl` in `.gitignore`, `vault999.jsonl` is force-tracked (`git add -f`). It's the immutable constitutional ledger and must stay in version control. Use `git add -f VAULT999/vault999.jsonl` when committing new entries.
- **`remote_inspection/` is NOT arifOS**: Contains cloned external repos (e.g. OpenClaw with 5000+ node_modules files). Gitignored since v60.1. Never commit.
- **`rclone_token.txt`**: Contains secrets. Gitignored. Never commit.
- **`tests/archive/`**: ~100 legacy test files with broken imports (stale `mcp_trinity`, `mcp.core.bridge` references). Kept for reference only.

---

## 888_HOLD Triggers (High-Stakes Operations)

Require explicit user confirmation:

- **Database migrations** — Irreversible system changes
- **Production deployments** — Safety-critical operations
- **Credential/secret handling** — Identity verification required
- **Mass file operations (>10 files)** — Entropy management
- **Git history modification** — Remote authority required
- **User correction of constitutional claim** — Re-verify against PRIMARY sources
- **Conflicting evidence across source tiers** — Pause for consensus

**Protocol**: List consequences → State irreversibles → Ask "yes, proceed" → Wait for confirmation → Execute with logging.

---

## Deployment

| Target            | Command                                                      | Notes                        |
| ----------------- | ------------------------------------------------------------ | ---------------------------- |
| Local (stdio)     | `python -m arifos_aaa_mcp stdio`                             | Claude Desktop, Cursor IDE   |
| VPS/Coolify (SSE) | `python -m arifos_aaa_mcp`                                   | Default transport, port 8080 |
| Docker            | `docker build -t arifos . && docker run -p 8080:8080 arifos` |                              |

**Live endpoints:**

- Health: `https://arifosmcp.arif-fazil.com/health`
- SSE: `https://arifosmcp.arif-fazil.com/sse`
- MCP: `https://arifosmcp.arif-fazil.com/mcp`

**MCP config files:** `.claude/mcp.json` (active), `.agents/mcp.json` (agent mode)

**Environment variables:** `HOST` (default `0.0.0.0`), `PORT` (default `8080`), `AAA_MCP_TRANSPORT` (default `sse`), `AAA_MCP_OUTPUT_MODE` (`user`/`debug`), `ARIFOS_PHYSICS_DISABLED` (`0`/`1`), `PPLX_API_KEY`, `BRAVE_API_KEY`

---

**Version:** v2026.2.28 | **Repo:** <https://github.com/ariffazil/arifOS>
