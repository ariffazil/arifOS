# AGENTS.md — arifOS Agent Protocol (v46-FORGED)

This guide defines the operational context for AI agents working within the **arifosmcp** environment.

**Motto:** *Ditempa Bukan Diberi — Forged, Not Given*

---

## 1. Build, Test, and Lint Commands

```bash
# Environment Setup (uv recommended)
uv pip install -e ".[dev]"

# Testing (asyncio auto-mode enabled)
pytest tests/ -v                           # All tests
pytest tests/test_file.py -v               # Single test file
pytest tests/test_file.py::test_name -v    # Single test (CRITICAL)
pytest tests/ -v -k "keyword"              # Filter by keyword

# Lint & Format (Standard: 100 char limit)
ruff check . --fix                         # Lint and auto-fix
ruff format .                              # Format (Black style)
mypy .                                     # Strict type check on core/

# Runtime
python -m arifosmcp.runtime                # SSE (Production)
python -m arifosmcp.runtime stdio          # STDIO (IDE/Local)
```

---

## 2. The Trinity Architecture (ΔΩΨ) & Stages

Agents operate in a synchronized metabolic loop across three functional domains:

| Stage | Name | Engine | Floor Focus |
|:---:|---|:---:|---|
| **000** | **INIT** | APEX (Ψ) | F11 Auth, F12 Injection Defense |
| **111-333**| **MIND** | AGI (Δ) | F2 Truth, F4 Clarity, F7 Humility |
| **555-666**| **HEART** | ASI (Ω) | F5 Peace², F6 Empathy, F9 Anti-Hantu |
| **888** | **JUDGE** | APEX (Ψ) | F13 Sovereign, F3 Witness, F8 Genius |
| **999** | **SEAL** | VAULT | Cryptographic commitment to ledger |

---

## 3. Directory Structure

```text
core/                        → KERNEL (decision logic, math)
├── governance_kernel.py    → Runtime state, transitions
├── judgment.py             → Decision interface
└── organs/                 → Trinity engines (AGI/ASI/APEX)

arifosmcp/
├── runtime/                → TRANSPORT HUB (FastMCP, zero logic)
├── intelligence/           → SENSES (Grounding, health)
└── transport/              → External gateways

tests/
├── conftest.py             → Pytest fixtures
├── core/                   → Core module tests
│   ├── kernel/             → Kernel execution tests 
│   └── test_sbert_floors.py → F5/F6/F9 semantic classification
├── adversarial/            → Judicial order tests
└── test_trace_replay.py    → VAULT999 integrity tests
```

---

## 4. Source Hierarchy & Evidence Verification

To satisfy **F2 (Truth)** and **F1 (Amanah)**, follow this hierarchy:

1. **PRIMARY:** `pyproject.toml`, `core/shared/floors.py`, `arifosmcp/runtime/server.py`, and `spec/` JSONs.
2. **SECONDARY:** `AGENTS.md`, `CLAUDE.md`, `README.md`.
3. **TERTIARY:** Code comments, legacy docs, directory naming.

> [!CAUTION]
> If SECONDARY contradicts PRIMARY, PRIMARY wins. Trigger a **H-SOURCE-CONFLICT** HOLD if detected.

---

## 5. 888_HOLD Triggers (v46 Hardened)

**STOP AND AWAIT HUMAN SEAL** when:
- **Mass Ops**: Editing >10 files or major refactors.
- **Destructive**: `DROP`, `DELETE` (no WHERE), or `git reset --hard`.
- **H-USER-CORRECTION**: User disputes a constitutional claim or logic.
- **H-SOURCE-CONFLICT**: PRIMARY sources contradict each other or the current state.
- **H-NO-PRIMARY**: Making architectural claims without reading the spec file.
- **H-RUSHED-FIX**: Proposing a complex fix after <5 mins of investigation.

---

## 6. Code Style Guidelines

- **Imports**: `from __future__ import annotations` (first line). Group stdlib → third-party → local.
- **Types**: Use modern typing (`list[X]`, `X | None`). Mandatory for `core/`.
- **Logic Location**:
    - `core/`: Pure logic, math, constitution. **ZERO** transport deps (`fastmcp` banned here).
    - `arifosmcp/`: Transport, protocols, MCP relay. **ZERO** decision logic.
- **Logging**: **NEVER USE `print()`**. It corrupts JSON-RPC. Use `sys.stderr.write()` or `logging`.

---

## 7. Test Coverage Guidelines

### Current State (2026.03.12-FORGED)
- **Total Tests:** ~410 passing
- **Coverage:** ~64% (target: 80%)

| Module | Coverage | Status |
|--------|----------|--------|
| `core/kernel/engine_adapters.py` | ~85% | ✅ Well-tested |
| `core/kernel/stage_orchestrator.py` | ~80% | ✅ Well-tested |
| `core/shared/sbert_floors.py` | ~75% | ✅ Well-tested |

**Version:** 2026.03.12-FORGED | **Status:** ACTIVE
