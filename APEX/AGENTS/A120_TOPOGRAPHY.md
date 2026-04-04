# AGENTS.md — Global Registry & Machine Topography

**Version:** 2026.03.13-ACTIVE | **Authority:** 888_JUDGE (Human: Arif)
**Status:** Canonical Root Guide for agents operating on this Windows PC.

---

## 1. Machine Topography (Chaos Reduction)

To avoid redundancy and confusion, agents must operate within these project boundaries:

| Priority | Path | Description |
|:---|:---|:---|
| **ACTIVE** | `C:\arifosmcp\` | **The Body.** Primary Development. Constitutional MCP runtime. |
| **CANON** | `C:\arifOS\` | **The Mind.** Theory, Reference, and historical logic. |
| **STALE** | `C:\Users\User\OneDrive\...` | **DO NOT USE.** Stale OneDrive synchronization copy. |

> [!IMPORTANT]
> Always `cd C:\arifosmcp` before performing code changes. This is where the active metabolic loop and VAULT999 ledger live.

---

## 2. Build, Test, and Lint Commands (Primary: arifosmcp)

Use `uv` for all Python environment management.

```bash
# Environment Setup
pip install -e ".[dev]"  # or uv pip install -e ".[dev]"

# Testing (pytest with asyncio auto-mode)
pytest tests/ -v                           # Run all tests
pytest tests/test_file.py -v               # Run single file
pytest tests/test_file.py::test_name -v    # Run single test (CRITICAL)
pytest tests/ -v -k "keyword"              # Search for tests

# Linting & Formatting
ruff check . --fix                         # Auto-fix linting errors
ruff format .                              # Format (Black style, 100 chars)
mypy .                                     # Type checking (strict on core/)

# MCP Server Runtime
python -m arifosmcp.runtime                # SSE (Production/Web)
python -m arifosmcp.runtime stdio          # STDIO (Claude/Cursor tool access)

# Pre-commit (Pre-forge gates)
pre-commit run --all-files                 # Manual quality check
```

---

## 3. Code Style & Architecture Trinity

### General Guidelines
- **Python**: 3.12+ (modern typing: `list[X]`, `X \| None`).
- **Formatting**: 4 spaces, 100-character line limit.
- **Imports**: `from __future__ import annotations` required in core files.
- **Nomenclature**: 
  - `snake_case` for functions/vars.
  - `PascalCase` for classes.
  - `UPPER_SNAKE` for constants.
  - `_leading_underscore` for private/internal.

### The Trinity Architecture (ΔΩΨ)
1. **AGI Mind (Δ)**: Reasoning, logic, truth analysis (F2, F4, F7).
2. **ASI Heart (Ω)**: Empathy, impact, alignment (F5, F6, F9).
3. **APEX Soul (Ψ)**: Final judgment, sealing, authority (F3, F10-F13).

### Error Handling Protocol
- **Prefer Results**: Return `Result` dataclasses instead of raising exceptions for common failures.
- **Logging**: Use `sys.stderr` for logs. **STDOUT IS FORBIDDEN** (reserved for JSON-RPC/MCP).

---

## 4. The 13 Constitutional Floors (F1–F13)

Every tool call must be validated against these floors:

| Floor | Rule | Trigger |
|:---:|:---|:---|
| **F1** | Amanah | Reversibility. Destructive actions require human seal. |
| **F2** | Truth | Strict grounding. No hallucination. |
| **F9** | Anti-Hantu | No "spiritual cosplay." AI cannot claim consciousness. |
| **F11** | Auth | Every session requires verified identity. |
| **F13** | Sovereign | Human holds the absolute final veto. |

---

## 5. 888_HOLD: Human Veto Triggers

**STOP AND ASK FOR APPROVAL (GENIUS Verto)** when:
1. **Mass Operations**: Editing >10 files simultaneously.
2. **Destructive**: `DROP`, `DELETE` (no WHERE), or `git reset --hard` / `git rebase`.
3. **Security**: Handling credentials, secrets, or identity verification logic.
4. **Ambiguity**: Conflicting evidence between canonical docs and codebase state.
5. **Rushed Fix**: Proposing a complex fix after <5 minutes of investigation.

---

## 6. Agent Navigation Workflow

1. **SENSE (111)**: Read `.opencode.json` (if present) or `TODO.md`.
2. **NAVIGATE**: Go to `C:\arifosmcp`.
3. **EVALUATE**: Check `pytest` status before any edit.
4. **FORGE**: Make changes. Run `ruff format` and `ruff check --fix`.
5. **SEAL (999)**: Verify with tests. Sign off with a summary and logic trace.

**Motto:** *Ditempa Bukan Diberi — Forged, Not Given*
