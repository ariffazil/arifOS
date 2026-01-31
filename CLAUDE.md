# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

arifOS is a constitutional AI governance system implementing the **AAA Framework** (AGI/ASI/APEX) — a three-layer architecture that enforces 13 constitutional floors (F1-F13) on every AI decision. It exposes governance as an MCP server with 7 tools. The canonical codebase lives in `codebase/`, theoretical foundations in `000_THEORY/`, and implementation levels (L1-L7) in `333_APPS/`.

**Package name:** `aaa-mcp` (v53.2.9) | **Python:** >=3.10 | **License:** AGPL-3.0
**Live server:** https://arif-fazil.com | **Motto:** "DITEMPA BUKAN DIBERI" — Forged, Not Given

## Build & Development Commands

```bash
# Install (editable with dev deps)
pip install -e ".[dev]"

# Run MCP server (stdio - for Claude Desktop)
aaa-mcp-stdio

# Run MCP server (SSE - for HTTP clients)
aaa-mcp-sse

# Run MCP server (auto-detect mode)
aaa-mcp

# Docker
docker build -t arifos:latest .
docker run -e PORT=8000 -p 8000:8000 arifos:latest
```

## Testing

```bash
# Full test suite
pytest tests/ -v --cov=codebase --cov-report=html

# Single test file
pytest tests/mcp/test_mcp_quick.py -v

# By marker
pytest -m constitutional       # Floor-specific tests
pytest -m integration          # Integration tests
pytest -m slow                 # Long-running tests

# Quick MCP smoke test
pytest tests/mcp/test_mcp_quick.py -v

# Comprehensive MCP tool test
pytest tests/test_mcp_all_tools.py -v
```

Test paths configured in pyproject.toml: `tests/` and `arifos/tests/`. Async mode is `auto`.

## Linting & Formatting

```bash
black codebase/ --line-length=100       # Format
ruff check codebase/                     # Lint
ruff check codebase/ --fix               # Lint + autofix
mypy codebase/ --ignore-missing-imports  # Type check
bandit -c pyproject.toml codebase/ --exclude=tests/  # Security scan

# Pre-commit (runs all above + constitutional checks)
pre-commit install
pre-commit run --all-files
```

**Style:** Black (line-length=100), Ruff (target py310), MyPy with strict mode on core governance modules.

## Architecture: The AAA Trinity

The system processes every request through three engines in sequence:

```
000 (INIT)  →  AGI (Mind Δ)  →  ASI (Heart Ω)  →  APEX (Soul Ψ)  →  999 (VAULT)
   ↑           111-333            444-666            888              ↓
   └────────────────────── 000↔999 metabolic loop ──────────────────┘
```

### Three Engines (`codebase/`)

| Engine | Dir | Role | Key Files | Enforces |
|--------|-----|------|-----------|----------|
| **AGI (Δ)** | `codebase/agi/` | Reasoning — precision-weighted beliefs, hierarchical abstraction | `engine_hardened.py`, `precision.py`, `hierarchy.py`, `atlas.py` | F2 Truth, F4 Clarity, F7 Humility, F10 Ontology |
| **ASI (Ω)** | `codebase/asi/` | Safety — 3-Trinity empathy (Self→System→Society), stakeholder protection | `engine_hardened.py`, `asi_components.py` | F1 Amanah, F5 Peace², F6 Empathy, F9 Anti-Hantu |
| **APEX (Ψ)** | `codebase/apex/` | Judgment — 9-Paradox equilibrium solver, verdict assignment | `trinity_nine.py`, `equilibrium_finder.py`, `floor_checks.py` | F3 Tri-Witness, F8 Genius, F11 Authority, F12 Hardening |

### Supporting Modules

- **`codebase/mcp/`** — MCP server (stdio + SSE transports), 7 tools in `tools/`, rate limiting, session ledger
- **`codebase/system/`** — APEX PRIME judge (`apex_prime.py`), constitution enforcement, processing pipeline
- **`codebase/apex/governance/`** — Cryptographic layer: Merkle trees, ledger hashing, zero-knowledge proofs, VAULT-999
- **`codebase/enforcement/`** — Floor validators, emergency calibration, governance enforcement
- **`codebase/bundles.py`** — `DeltaBundle` (AGI output) and `OmegaBundle` (ASI output) canonical dataclasses
- **`codebase/kernel.py`** — Main orchestrator connecting all engines

### MCP Tools (7 total)

Tools are defined in `codebase/mcp/tools/` and registered via the server:

| Tool | Purpose | Entry Point |
|------|---------|-------------|
| `_init_` | Session gate + injection scan | `canonical_trinity.py` |
| `_agi_` | Mind engine (reasoning) | `agi_tool.py` |
| `_asi_` | Heart engine (safety/empathy) | `asi_tool.py` |
| `_apex_` | Soul engine (judgment + 9-paradox) | `apex_tool.py` |
| `_vault_` | Immutable ledger (Merkle-sealed) | `vault_tool.py` |
| `_trinity_` | Full 000→999 pipeline | `mcp_trinity.py` |
| `_reality_` | External fact-checker | `reality_grounding.py` |

All tools accept `{"action": "...", "query": "...", "session_id": "..."}` and return `{"verdict": "SEAL|PARTIAL|VOID|888_HOLD|SABAR", "response": "...", ...}`.

## Constitutional Floors (F1-F13)

Hard floors fail → VOID (blocked). Soft floors fail → SABAR (paused for review).

| # | Floor | Threshold | Type |
|---|-------|-----------|------|
| F1 | Amanah (Trust) | Reversible=true | Hard |
| F2 | Truth | ≥0.99 | Hard |
| F3 | Tri-Witness | ≥0.95 | Soft |
| F4 | Clarity (ΔS) | ≤0 entropy | Hard |
| F5 | Peace² | ≥1.0 | Hard |
| F6 | Empathy (κᵣ) | ≥0.95 | Soft |
| F7 | Humility (Ω₀) | 0.03-0.05 | Soft |
| F8 | Genius (G) | ≥0.80 | Soft |
| F9 | Anti-Hantu | Φ≤0.30 | Hard |
| F10 | Ontology | Symbol mode | Hard |
| F11 | Authority | Verified token | Hard |
| F12 | Hardening | ≥0.85 detection | Hard |
| F13 | Curiosity | Alternatives>0 | Guide |

**Verdict hierarchy:** SABAR > VOID > 888_HOLD > PARTIAL > SEAL

## Key Conventions

### Code-Level Floor Compliance (from `.github/copilot-instructions.md`)

When writing code in this repo, these patterns are enforced:

- **F1 (Amanah):** Pure functions preferred. No silent mutations of inputs. Irreversible operations require explicit flags.
- **F2 (Truth):** Use `None`/empty when data doesn't exist. Never fabricate metrics or stages that didn't run.
- **F3 (Tri-Witness):** Code must match established contracts. Use canonical interfaces from `codebase/bundles.py`.
- **F4 (Clarity):** Named constants instead of magic numbers. Clear parameter names. Self-documenting code.
- **F5 (Peace²):** Safe defaults. Backup before overwrite. No destructive default arguments.
- **F9 (Anti-Hantu):** Never generate text claiming consciousness, feelings, or sentience. See forbidden phrases in global CLAUDE.md.

### Source Authority Hierarchy

1. **PRIMARY:** `spec/*.json`, `canon/*_v38Omega.md` (SEALED) — authoritative for constitutional claims
2. **SECONDARY:** `codebase/*.py` — runtime implementation reference
3. **TERTIARY:** `docs/*.md`, `README.md` — informational, may lag behind PRIMARY
4. **NOT EVIDENCE:** grep results, code comments, this file

### Processing Pipeline Stages

Canonical spine: `000 (init) → 444 (read) → 666 (act) → 888 (review) → 999 (seal)`
Legacy stages (111-777) map to this spine but prefer canonical numbering in new code.

### Separation of Powers

- **Architect (Δ):** Plans via 000/444/666/888/999
- **Engineer (Ω):** Implements from handoff
- **Auditor (Ψ):** Reviews engineer output
- **KIMI (Κ):** Final SEAL/VOID/HOLD meta-judge

## Environment Variables

```bash
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=info
GOVERNANCE_MODE=HARD          # HARD|SOFT
VAULT_PATH=./VAULT999
GATEWAY_PORT=9000
```

## Pre-commit Constitutional Hooks

Beyond standard linting, commits are checked for:
- **Constitutional Floor Validation** (F1-F12) via `scripts/check_track_alignment_v46.py`
- **F9 Anti-Hantu:** Rejects Python files containing consciousness claims ("I feel", "I am conscious")
- **F1 Amanah:** Rejects files containing `shutil.rmtree`, `os.remove`, `DROP TABLE`, `DELETE FROM`

## Documentation Structure

- `000_THEORY/` — Constitutional law and foundations (source of truth for governance)
- `333_APPS/` — Implementation levels L1 (Prompt) through L7 (AGI)
- `docs/` — User-facing architecture docs, API reference, deployment guide
- `docs/KIMI AUDIT/` — v55.0 audit deliverables and roadmap

## Entry Points

Defined in `pyproject.toml` under `[project.scripts]`:
- `aaa-mcp` / `codebase-mcp` → `codebase.mcp.__main__:main` (auto-detect)
- `aaa-mcp-stdio` / `codebase-mcp-stdio` → `codebase.mcp.server:main_stdio`
- `aaa-mcp-sse` / `codebase-mcp-sse` → `codebase.mcp.sse:main`
