# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Project Overview

**arifOS** is a Constitutional AI Governance Framework (v52+) that enforces 13 immutable constitutional floors across any LLM. It acts as a governance metabolizer sitting between AI models and users, ensuring all outputs are validated, audited, and sealed through constitutional law.

**Motto:** *"Ditempa Bukan Diberi"* — Forged, Not Given

**v52 Key Architecture:**
- **Pure Bridge**: Server is "blind" (zero logic) — all wisdom lives in Core Kernels
- **MCP Conscience**: Protocol is the conscience; AI cannot act without Trinity tools
- **Live Server**: https://arifos.arif-fazil.com/ (Railway deployment)
- **Monitoring**: https://arifos.arif-fazil.com/dashboard (Live Telemetry)

---

## Quick Commands

### Development & Testing

```bash
# Install from source
pip install -e .                    # Basic install
pip install -e ".[dev]"             # With dev tools

# Run all tests with coverage
pytest tests/ -v --cov=arifos --cov-report=html

# Run constitutional floor tests
pytest tests/constitutional/ -m constitutional
pytest -m f1                        # F1 Amanah tests only

# Code quality
black arifos/ --line-length=100
ruff check arifos/
mypy arifos/core --strict

# Single test file
pytest tests/constitutional/test_04_VAULT_ledger_integrity.py -v
```

### Running MCP Servers

```bash
# Trinity MCP Server (stdio mode - for Claude Desktop, Cursor)
python -m arifos.mcp

# Trinity SSE Server (streaming - for Railway, ChatGPT Dev Mode)
python -m arifos.mcp trinity-sse

# FastAPI Server (local development)
uvicorn arifos.mcp.trinity_server:app --reload --port 8000

# Alternative entry points
arifos-mcp                          # Alias for python -m arifos.mcp
arifos-mcp-sse                      # SSE transport
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

# Utility commands
arifos-verify-ledger                # Verify hash-chained ledger
arifos-analyze-governance           # Analyze floor violations
arifos-analyze-audit-trail          # Review constitutional decisions
```

---

## Project Structure

### v52 Architecture (Brain/Body Separation)

```
arifos/
├── core/                           # "BRAIN" - All governance wisdom
│   ├── engines/
│   │   ├── agi/                    # Δ Mind Kernel (F2, F4, F7, F10)
│   │   │   ├── delta_kernel.py     # Core AGI logic
│   │   │   ├── entropy.py          # ΔS entropy calculations
│   │   │   └── floor_checks.py     # AGI floor enforcement
│   │   ├── asi/                    # Ω Heart Kernel (F1, F5, F6, F9)
│   │   │   ├── omega_kernel.py     # Core ASI logic
│   │   │   ├── empathy/            # F6 empathy detection
│   │   │   └── floor_checks.py     # ASI floor enforcement
│   │   └── apex/                   # Ψ Soul Kernel (F3, F8, F11, F12, F13)
│   │       ├── psi_kernel.py       # Core APEX logic
│   │       ├── governance/         # Merkle sealing, ledger crypto
│   │       └── floor_checks.py     # APEX floor enforcement
│   └── enforcement/                # Floor validation & metrics
│       ├── constitutional_constants_v46.py
│       ├── tcha_metrics.py         # TEACH metrics implementation
│       └── trinity_orchestrator.py # Tri-Witness consensus
│
├── mcp/                            # "BODY" - Pure zero-logic wiring
│   ├── __main__.py                 # Entry point: python -m arifos.mcp
│   ├── server.py                   # stdio MCP server
│   ├── sse.py                      # SSE transport (Railway)
│   ├── trinity_server.py           # FastAPI wrapper
│   ├── bridge.py                   # Zero-logic wire to kernels
│   └── tools/
│       ├── mcp_trinity.py          # 5-tool Trinity bundle
│       ├── mcp_agi_kernel.py       # agi_genius tool
│       ├── mcp_asi_kernel.py       # asi_act tool
│       └── mcp_apex_kernel.py      # apex_judge tool
│
├── clip/                           # CLI implementation (000-999)
│   └── aclip/cli/                  # Metabolic pipeline stages
│
└── constitutional_constants.py     # Floor thresholds

000_THEORY/                         # Constitutional law & theory
VAULT999/                           # Immutable memory vault (L0-L5)
tests/                              # Test suite (markers: f1-f12)
```

### Key Directories

- **`arifos/core/`** — All governance logic lives here (kernels, enforcement)
- **`arifos/mcp/`** — MCP servers are "blind" bridges; no governance logic
- **`spec/`** — Canonical floor definitions (`constitutional_floors.json`)
- **`VAULT999/`** — Hash-chained ledger (AAA_HUMAN, BBB_LEDGER, CCC_CANON)

---

## Architecture Patterns

### 1. The 5-Tool Trinity (MCP Interface)

v52 consolidates to 5 canonical MCP tools:

| Tool | Role | What It Does |
|------|------|--------------|
| `000_init` | Gate | Authority check, injection defense, session creation |
| `agi_genius` | Mind (Δ) | SENSE → THINK → ATLAS (F2, F4, F7, F10) |
| `asi_act` | Heart (Ω) | EVIDENCE → EMPATHY → ACT (F1, F5, F6, F9) |
| `apex_judge` | Soul (Ψ) | EUREKA → JUDGE → PROOF (F3, F8, F11, F12, F13) |
| `999_vault` | Seal | Merkle sealing + immutable ledger |

**Flow:** `000_init` → `agi_genius` → `asi_act` → `apex_judge` → `999_vault`

### 2. Trinity Engine Consensus

Three independent engines must agree (Tri-Witness ≥ 0.95):

- **AGI (Δ Mind):** Logic, truth, clarity — `arifos/core/engines/agi/`
- **ASI (Ω Heart):** Empathy, care, peace — `arifos/core/engines/asi/`
- **APEX (Ψ Soul):** Final judgment & sealing — `arifos/core/apex/`

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
| SECONDARY | `arifos/core/*.py` | Implementation reference |
| TERTIARY | `docs/*.md`, README | Informational (may lag) |

**NOT evidence:** grep results, code comments, this file

---

## Key Entry Points

### Python Classes (Core)

| Class | Location | Purpose |
|-------|----------|---------|
| `DeltaKernel` | `arifos/core/engines/agi/delta_kernel.py` | AGI Mind engine |
| `OmegaKernel` | `arifos/core/engines/asi/omega_kernel.py` | ASI Heart engine |
| `PsiKernel` | `arifos/core/apex/psi_kernel.py` | APEX Soul engine |
| `LiveMetricsService` | `arifos/core/integration/api/services/live_metrics_service.py` | Ledger telemetry |
| `TrinityOrchestrator` | `arifos/core/enforcement/trinity_orchestrator.py` | Tri-Witness consensus |

### MCP Entry Points

| Module | Purpose |
|--------|---------|
| `arifos.mcp.__main__` | CLI entry: `python -m arifos.mcp` |
| `arifos.mcp.server` | stdio MCP transport |
| `arifos.mcp.sse` | SSE transport (Railway) |
| `arifos.mcp.trinity_server` | FastAPI wrapper |
| `arifos.mcp.tools.mcp_trinity` | 5-tool bundle definition |

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

**Version:** v53.0.0-SEAL
**Last Updated:** January 2026
**Motto:** *"Ditempa Bukan Diberi"* — Forged, Not Given
