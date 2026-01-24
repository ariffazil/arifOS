# arifos — Constitutional AI Kernel

**Version:** v52.0.0-SEAL  
**Authority:** Track B (Constitutional Law)  
**Motto:** *DITEMPA BUKAN DIBERI* — Forged, Not Given

---

## What is `arifos`?

The `arifos` package is the **pure Python kernel** of arifOS — a constitutional AI governance system. It is the thermodynamic engine that converts raw LLM probability into **governed, auditable truth**.

```
┌─────────────────────────────────────────────────────────────────┐
│                      arifOS Architecture (v52)                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌───────────────────────┐       ┌───────────────────────┐     │
│   │     arifos.mcp       │       │   Claude / Cursor /   │     │
│   │  (MCP Server Layer)  │◄─────►│   GPT / Gemini        │     │
│   │  5 Trinity Tools     │       │   (AI Clients)        │     │
│   └───────────┬───────────┘       └───────────────────────┘     │
│               │ imports                                          │
│               ▼                                                  │
│   ┌───────────────────────────────────────────────────────┐     │
│   │                    arifos.core                        │     │
│   │                    The Brain Kernel                   │     │
│   ├───────────────────────────────────────────────────────┤   │
│   │  core/      - Trinity Engines, Metabolizer, Floors     │     │
│   │  mcp/       - MCP Server (v52 unified)                 │     │
│   │  api/       - DEPRECATED → core/integration/api        │     │
│   │  config/    - Configuration management                 │     │
│   │  spec/      - Constitutional specifications            │     │
│   └───────────────────────────────────────────────────────┘     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Package Structure

| Folder | Purpose | Status |
|--------|---------|--------|
| `core/` | Trinity Engines, Metabolizer, Constitutional Floors | ✅ Active |
| `mcp/` | MCP Server (v52 unified) | ✅ **Active** |
| `api/` | FastAPI server interfaces | ⚠️ **DEPRECATED** → `core/integration/api/` |
| `config/` | Configuration and settings | ✅ Active |
| `clip/` | aCLIP protocol handlers | ✅ Active |
| `spec/` | Constitutional specifications (JSON schemas) | ✅ Active |
| `ledger/` | Ledger interfaces | ✅ Active |
| `protocol/` | Protocol handlers | ✅ Active |

---

## The Core: Trinity Architecture (ΔΩΨ)

The `arifos.core` module is organized around the **Constitutional Trinity** — three irreducible engines that must agree for a verdict to SEAL.

| Engine | Symbol | Role | Stages | Floors |
|--------|--------|------|--------|--------|
| **AGI** | Δ (Delta) | The Mind — Cold Logic | 111 SENSE, 222 REFLECT, 333 REASON | F2, F6, F7 |
| **ASI** | Ω (Omega) | The Heart — Warm Empathy | 444 EVIDENCE, 555 EMPATHIZE, 666 ALIGN | F3, F4, F5 |
| **APEX** | Ψ (Psi) | The Soul — Final Judgment | 777 FORGE, 888 JUDGE, 889 PROOF | F1, F8, F9 |

### Metabolizer Pipeline (000 → 999)

```
000 VOID → 111 SENSE → 222 REFLECT → 333 REASON
                                        ↓
                                   444 EVIDENCE
                                        ↓
                                   555 EMPATHIZE
                                        ↓
                                   666 ALIGN
                                        ↓
777 FORGE → 888 JUDGE → 889 PROOF → 999 SEAL → Ledger
```

---

## Core Folder Map

```
arifos/core/
├── engines/           # Trinity Engines (agi_engine, asi_engine, apex_engine)
├── metabolism/        # 11 Pipeline Stages (000_void → 889_proof)
├── enforcement/       # Constitutional Law & Guards (floor_validators, rate_limiter)
├── memory/            # Ledger, Vault, Cooling Ledger
├── system/            # Orchestration (apex_prime, hypervisor, coordinator)
├── spec/              # Schema validators
├── utils/             # Telemetry, entropy, sentinel
└── metabolizer.py     # The State Machine
```

---

## Constitutional Floors (F1–F13)

Every output must pass **ALL floors** (AND logic). Fail any = VOID.

| Floor | Name | Threshold | Type |
|-------|------|-----------|------|
| **F1** | Amanah | Boolean | Hard (Kill-Switch) |
| **F2** | Truth (Δ) | ≥ 0.99 | Hard |
| **F3** | Tri-Witness | ≥ 0.95 | Hard |
| **F4** | Clarity (ΔS) | ≥ 0 | Hard |
| **F5** | Peace² | ≥ 1.0 | Soft |
| **F6** | Empathy (κᵣ) | ≥ 0.95 | Soft |
| **F7** | Humility (Ω₀) | [0.03, 0.05] | Hard |
| **F8** | Genius (G) | ≥ 0.80 | Derived |
| **F9** | C_dark | < 0.30 | Derived |
| **F10** | Ontology | Boolean | Hard |
| **F11** | CommandAuth | Boolean | Hard |
| **F12** | InjectionDefense | ≥ 0.85 | Hard |
| **F13** | Curiosity | ≥ 0.85 | Soft |

### The Ψ Formula

```
Ψ = (ΔS × Peace² × κᵣ × RASA × Amanah) / (Entropy + Shadow + ε)

Threshold: Ψ ≥ 1.0 → SEAL
```

---

## Usage

### As a Library (Recommended)

```python
from arifos.core.metabolizer import Metabolizer
from arifos.core.engines import AGIEngine, ASIEngine, APEXEngine
from arifos.core import apex_review

# High-level: APEX review
verdict = apex_review(task="Should I delete this file?", context={})
print(verdict.verdict)  # SEAL, VOID, SABAR

# Low-level: Metabolizer pipeline
m = Metabolizer()
m.initialize({"query": "What is 2+2?", "user_id": "u1"})
m.transition_to(111)  # SENSE
m.transition_to(222)  # REFLECT
# ... continue through 999
```

### Via MCP (v52 Unified)

```bash
# Standard I/O (Claude Desktop, Cursor)
python -m arifos.mcp trinity

# SSE mode (Railway, cloud)
python -m arifos.mcp trinity-sse
```

---

## Architecture Note (v52)

In v52, `arifos.mcp` is the unified MCP server (previously split as `AAA_MCP`).

| Component | Role | Status |
|-----------|------|--------|
| `arifos/` | Python kernel | ✅ Library |
| `arifos/mcp/` | MCP server | ✅ v52 Unified |
| `AAA_MCP/` | (archived) | 📦 Backup in `archive/` |

---

## Verification

```bash
# Smoke check imports
python -c "import arifos"
python -c "from arifos.core.metabolizer import Metabolizer"
python -c "from arifos.core.engines import AGIEngine"

# Run tests
pytest tests/ -v
```

---

## References

| Document | Location |
|----------|----------|
| **Core Architecture** | `arifos/core/README.md` |
| **AAA_MCP Application** | `AAA_MCP/README.md` |
| **Constitutional Canon** | `000_THEORY/` |
| **Agent Governance** | `000_THEORY/001_AGENTS.md` |

---

**DITEMPA BUKAN DIBERI.**
