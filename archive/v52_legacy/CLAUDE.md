# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Project Overview

**arifOS** is a Constitutional AI Governance Framework (v53.2.9) that enforces 13 immutable constitutional floors across any LLM. It acts as a governance metabolizer sitting between AI models and users, ensuring all outputs are validated, audited, and sealed through constitutional law.

**Motto:** *"Ditempa Bukan Diberi"* — Forged, Not Given

**v53.2.9 Key Architecture:**
- **Pure Bridge**: Server is "blind" (zero logic) — all wisdom lives in Core Kernels
- **MCP Conscience**: Protocol is the conscience; AI cannot act without Trinity tools
- **Production Hardening**: BridgeError categorization, session maintenance, circuit breaker
- **Live Server**: https://arif-fazil.com/ (Railway deployment)
- **Monitoring**: https://arif-fazil.com/dashboard (Live Telemetry)

---

## Quick Commands

### Development & Testing

```bash
# Install from source
pip install -e .                    # Basic install
pip install -e ".[dev]"             # With dev tools

# Run all tests with coverage
pytest tests/ -v --cov=codebase --cov-report=html

# Run constitutional floor tests
pytest tests/constitutional/ -m constitutional
pytest -m f1                        # F1 Amanah tests only

# Code quality
black codebase/ --line-length=100
ruff check codebase/
mypy codebase/ --strict

# Single test file
pytest tests/constitutional/test_04_VAULT_ledger_integrity.py -v
```

### Running MCP Servers

```bash
# Trinity MCP Server (stdio mode - for Claude Desktop, Cursor)
python -m codebase.mcp

# Trinity SSE Server (streaming - for Railway, ChatGPT Dev Mode)
python -m codebase.mcp trinity-sse

# FastAPI Server (local development)
uvicorn codebase.mcp.trinity_server:app --reload --port 8000

# Primary entry points (recommended)
aaa-mcp                             # Primary: python -m codebase.mcp
aaa-mcp-sse                         # SSE transport
codebase-mcp                        # Alternative alias
```

### Metabolic Pipeline (CLI)

```bash
# Each stage is a separate CLI command
000                                 # Constitutional gate (authority check)
111                                 # Sense/search stage
222                                 # Reflection/thinking
333                                 # Reasoning
444                                 # Evidence gathering
555                                 # Empathy validation
666                                 # Alignment synthesis
777                                 # Forge/eureka
888                                 # Final judgment
999                                 # VAULT persistence

# Utility commands (legacy - may not be available)
# arifos-verify-ledger              # Verify hash-chained ledger
# arifos-analyze-governance         # Analyze floor violations
# arifos-analyze-audit-trail        # Review constitutional decisions
```

---

## Project Structure

### v53.2.9 Architecture (Brain/Body Separation)

```
codebase/                           # "CORE" - All governance implementation
├── mcp/                            # "BODY" - Pure zero-logic wiring
│   ├── __main__.py                 # Entry point: python -m codebase.mcp
│   ├── server.py                   # stdio MCP server
│   ├── sse.py                      # SSE transport (Railway)
│   ├── trinity_server.py           # FastAPI wrapper
│   ├── bridge.py                   # Zero-logic router + BridgeError
│   ├── maintenance.py              # Session auto-recovery loop
│   └── tools/                      # 7-tool Trinity bundle
│       └── mcp_trinity.py          # _init_, _agi_, _asi_, _apex_, _vault_, _trinity_, _reality_
│
├── agi/                            # Δ Mind Kernel (F2, F4, F7, F10)
├── asi/                            # Ω Heart Kernel (F1, F5, F6, F9)
├── apex/                           # Ψ Soul Kernel (F3, F8, F11, F12, F13)
├── vault/                          # VAULT-999 sealing
├── engines/                        # Core Trinity engines
├── enforcement/                    # Floor validation & metrics
├── prompt/                         # Codec layer (signal extraction, routing)
└── kernel.py                       # Kernel manager (AGI/ASI/APEX orchestration)

000_THEORY/                         # Constitutional law & theory
VAULT999/                           # Immutable memory vault (L0-L5)
tests/                              # Test suite (markers: f1-f13)
spec/                               # Canonical floor definitions
```

### Key Directories

- **`codebase/`** — All governance implementation (kernels, MCP, enforcement)
- **`codebase/mcp/`** — MCP servers are "blind" bridges with error handling
- **`spec/`** — Canonical floor definitions (`constitutional_floors.json`)
- **`VAULT999/`** — Hash-chained ledger (AAA_HUMAN, BBB_LEDGER, CCC_CANON)

---

## Architecture Patterns

### 1. The 7-Tool Trinity (MCP Interface)

v53.2.9 implements 7 canonical MCP tools:

| Tool | Role | What It Does |
|------|------|--------------|
| `_init_` | Gate | Authority check, injection defense, session creation |
| `_agi_` | Mind (Δ) | SENSE → THINK → ATLAS (F2, F4, F7, F10) |
| `_asi_` | Heart (Ω) | EVIDENCE → EMPATHY → ACT (F1, F5, F6, F9) |
| `_apex_` | Soul (Ψ) | EUREKA → JUDGE → PROOF (F3, F8, F11, F12, F13) |
| `_vault_` | Seal | Merkle sealing + immutable ledger |
| `_trinity_` | Orchestrator | Full metabolic cycle (all engines) |
| `_reality_` | Fact-Checker | External search with Brave API (circuit breaker protected) |

**Flow:** `_init_` → `_agi_` → `_asi_` → `_apex_` → `_vault_`

### 2. Trinity Engine Consensus

Three independent engines must agree (Tri-Witness ≥ 0.95):

- **AGI (Δ Mind):** Logic, truth, clarity — `codebase/agi/`, `codebase/engines/agi/`
- **ASI (Ω Heart):** Empathy, care, peace — `codebase/asi/`, `codebase/engines/asi/`
- **APEX (Ψ Soul):** Final judgment & sealing — `codebase/apex/`, `codebase/engines/apex/`

### 3. Constitutional Floors (F1-F13)

Authoritative source: `spec/constitutional_floors.json`

| Floor | Threshold | Type | Quick Check |
|-------|-----------|------|-------------|
| F1 Amanah | LOCK | Hard | Reversible? Within mandate? |
| F2 Truth | ≥0.99 | Hard | Factually accurate? |
| F3 Tri-Witness | ≥0.95 | Soft | Human·AI·Earth consensus? |
| F4 Clarity (ΔS) | ≥0 | Hard | Reduces confusion? |
| F5 Peace² | ≥1.0 | Soft | Non-destructive? |
| F6 κᵣ Empathy | ≥0.95 | Soft | Serves weakest? |
| F7 Ω₀ Humility | [0.03,0.05] | Hard | States uncertainty? |
| F8 G (Genius) | ≥0.80 | Derived | Governed intelligence? |
| F9 C_dark | <0.30 | Hard | No dark cleverness? |
| F10 Ontology | LOCK | Hard | Symbolic mode maintained? |
| F11 Command Auth | LOCK | Hard | Identity verified? |
| F12 Injection | <0.85 | Hard | No injection patterns? |
| F13 Curiosity | LOCK | Soft | Exploratory freedom preserved? |

**Verdicts:** SEAL ✓ | PARTIAL | VOID ✗ | SABAR ⏳ | 888_HOLD

### 4. Thermodynamic Laws

```
ΔS ≤ 0        — Entropy reduction (clarity increases)
Peace² ≥ 1    — Non-destructive stability
Ω₀ ∈ [0.03, 0.05] — Humility band (3-5% uncertainty)
```

### 5. VAULT-999 Memory Hierarchy

| Tier | Age | Purpose |
|------|-----|---------|
| L0 | 0h | Hot session memory |
| L1 | 24h | Daily cooling |
| L2 | 72h | Phoenix cooling (truth stabilizes) |
| L3 | 7d | Weekly reflection |
| L4 | 30d | Monthly canon |
| L5 | 365d+ | Constitutional law (immutable) |

---

## Development Workflow

### Working Memory

All drafts/scratchpads go in: **`.claude/claudebrain/`**

### Code-Level Floor Violations (Quick Reference)

Floors apply to CODE, not just statements:

| Floor | Code Smell | Fix |
|-------|------------|-----|
| F1 | Mutates input, hidden side effects | Pure functions, explicit returns |
| F2 | Fabricated data, fake metrics | Empty/null when unknown |
| F3 | Contract mismatch, type lies | Use canonical interfaces |
| F4 | Magic numbers, obscure logic | Named constants, clear params |
| F5 | Destructive defaults, no backup | Safe defaults, preserve state |
| F6 | Only happy path, cryptic errors | Handle edge cases, clear messages |
| F7 | False confidence, fake computation | Admit uncertainty, cap at 0.95 |
| F8 | Bypasses governance | Use established systems (APEX_PRIME) |
| F9 | Deceptive naming, hidden behavior | Honest names, transparent logic |

**Detailed examples:** `.github/copilot-instructions.md`

### Before Completing Any Task

☐ Did I read PRIMARY sources (`spec/*.json`, SEALED canon) for constitutional claims?
☐ Does my output reduce confusion (ΔS ≥ 0)?
☐ Who is the weakest stakeholder if I'm wrong? Did I protect them?

---

## Testing

### Pytest Markers

```bash
pytest -m constitutional    # All floor tests
pytest -m f1                # F1 Amanah tests
pytest -m f2                # F2 Truth tests
# ... through f12
pytest -m slow              # Long-running tests
pytest -m integration       # Integration tests
```

### Coverage

```bash
pytest tests/ -v --cov=arifos --cov-report=html
# Open htmlcov/index.html to view
```

---

## Source Verification

Constitutional claims MUST be verified against PRIMARY sources:

| Tier | Source | Authority |
|------|--------|-----------|
| PRIMARY | `spec/*.json`, SEALED canon | Required for constitutional claims |
| SECONDARY | `codebase/*.py` | Implementation reference |
| TERTIARY | `docs/*.md`, README | Informational (may lag) |

**NOT evidence:** grep results, code comments, this file

---

## Key Entry Points

### Python Classes (Core)

| Class | Location | Purpose |
|-------|----------|---------|
| `AGINeuralCore` | `codebase/engines/agi/` | AGI Mind engine |
| `ASIActionCore` | `codebase/engines/asi/` | ASI Heart engine |
| `APEXJudicialCore` | `codebase/engines/apex/` | APEX Soul engine |
| `KernelManager` | `codebase/kernel.py` | Kernel orchestration |
| `BridgeRouter` | `codebase/mcp/bridge.py` | MCP routing with error handling |

### MCP Entry Points

| Module | Purpose |
|--------|---------|
| `codebase.mcp.__main__` | CLI entry: `python -m codebase.mcp` |
| `codebase.mcp.server` | stdio MCP transport |
| `codebase.mcp.sse` | SSE transport (Railway) |
| `codebase.mcp.trinity_server` | FastAPI wrapper |
| `codebase.mcp.tools.mcp_trinity` | 7-tool bundle definition |
| `codebase.mcp.maintenance` | Session auto-recovery |

---

## Dependencies

```bash
pip install -e .           # Core: numpy, pydantic, anyio, starlette, fastmcp, dspy
pip install -e ".[dev]"    # + pytest, black, ruff, mypy
pip install -e ".[all]"    # Everything including litellm, fastapi
```

---

## Additional Resources

| Resource | Purpose |
|----------|---------|
| `docs/UNIVERSAL_PROMPT.md` | Copy-paste system prompt for any AI |
| `000_THEORY/000_LAW.md` | Constitutional floor definitions |
| `.github/copilot-instructions.md` | Code-level floor enforcement examples |
| `spec/constitutional_floors.json` | Canonical floor thresholds |

---

## Global Instructions Integration

This project is governed by `.claude/CLAUDE.md` (global instructions) which defines:
- 12-floor constitutional checkpoint process
- 888_HOLD triggers for high-stakes operations
- SABAR protocol for floor violations
- FAGS RAPE autonomous cycle

---

**Version:** v53.2.9-SEAL
**Last Updated:** January 2026
**Motto:** *"Ditempa Bukan Diberi"* — Forged, Not Given

---

## Implementation Highlights (v53.2.9)

**Production Hardening:**
- ✅ BridgeError categorization (FATAL/TRANSIENT/SECURITY) — `codebase/mcp/bridge.py:40-56`
- ✅ Session maintenance loop (auto-recovery every 5 min) — `codebase/mcp/maintenance.py:13-48`
- ✅ Circuit breaker for external APIs (3 failures → 5 min timeout) — `codebase/mcp/bridge.py:300-337`
- ✅ Integration test suite — `tests/mcp/test_maintenance_and_errors.py`

**Deployment Status:** 97% Production-Ready (F1, F2, F4, F5, F11 enforced)
