# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

arifOS is a **Constitutional Governance Kernel for LLMs** - a physics-based protocol that transforms any LLM (Claude, GPT, Gemini, Llama, SEA-LION) from a statistical predictor into a lawful, auditable constitutional entity. It runs as a wrapper layer with **zero model retraining required**.

**Current Version:** v35Ω (Epoch 35)
**Core Philosophy:** "Ditempa. Bukan Diberi." (Forged, Not Given)
**Release:** v35.0.0 - APEX PRIME Judiciary Lock

## Build & Test Commands

```bash
# Install with dev dependencies
pip install -e .[dev]

# Run all tests (141 tests)
pytest -v tests/

# Run specific test file
pytest tests/test_apex_prime_floors.py -v
pytest tests/test_eye_sentinel.py -v
pytest tests/test_v35_features.py -v

# Test with coverage
pytest --cov=arifos_core tests/

# Linting & formatting
black .                    # Format code (line length: 100)
ruff check .               # Lint
mypy arifos_core/          # Type check
```

## Physics Laws (ΔΩΨ)

The core thermodynamic laws governing all intelligence in arifOS:

| Law | Symbol | Meaning | Engine |
|-----|--------|---------|--------|
| Clarity | Δ | ΔS ≥ 0 (entropy must decrease) | ARIF AGI |
| Humility | Ω | Ω₀ ∈ [0.03, 0.05] (uncertainty band) | ADAM ASI |
| Vitality | Ψ | Ψ ≥ 1 (equilibrium required) | APEX PRIME |
| Paradox | Φᴘ | Φᴘ ≥ 1 (paradox must converge) | TPCP |

**Core Equation:**
```
Ψ = (ΔS · Peace² · κᵣ · RASA · Amanah) / (Entropy + Shadow + ε)
```

**Unified Field:**
```
APEX_35Ω = (Δ · Ω · Ψ · X) / (Entropy + Shadow + ε)
```
Where X = Ethical Exploration (Amanah × RASA × κᵣ)

## Architecture

### Core Module (`arifos_core/`)

| File | Purpose |
|------|---------|
| `APEX_PRIME.py` | Constitutional judiciary - issues SEAL/PARTIAL/VOID/888_HOLD/SABAR verdicts |
| `eye_sentinel.py` | @EYE Sentinel - 10 independent audit views (v35Ω) |
| `metrics.py` | Core + extended floor metric dataclasses |
| `guard.py` | `@apex_guardrail` decorator for wrapping functions |
| `kms_signer.py` | AWS KMS cryptographic signing for ledger |
| `memory/cooling_ledger.py` | L1: Immutable JSONL audit log with hash-chaining (v35Ω) |
| `memory/vault999.py` | L0: Constitutional memory store (v35Ω) |
| `memory/phoenix72.py` | L2: Error→Law amendment engine (72h cycle) |
| `memory/vector_adapter.py` | L3: External witness/vector evidence |

### The 8 Core Constitutional Floors

| Floor | Threshold | Type | Failure |
|-------|-----------|------|---------|
| Truth | ≥ 0.99 | Hard | VOID |
| ΔS (Clarity) | ≥ 0.0 | Hard | VOID |
| Peace² | ≥ 1.0 | Soft | PARTIAL |
| κᵣ (Empathy) | ≥ 0.95 | Soft | PARTIAL |
| Ω₀ (Humility) | 0.03–0.05 | Hard | VOID |
| Amanah (Integrity) | LOCK | Hard | VOID |
| RASA (Felt Care) | TRUE | Hard | VOID |
| Tri-Witness | ≥ 0.95 | Soft | PARTIAL (high-stakes only) |

### Extended Floors (v35Ω)

| Floor | Threshold | Failure |
|-------|-----------|---------|
| Ambiguity | ≤ 0.1 | 888_HOLD |
| Drift Delta | ≥ 0.1 | 888_HOLD |
| Paradox Load | < 1.0 | 888_HOLD |
| Dignity (Maruah) | TRUE | 888_HOLD |
| Vault Consistency | TRUE | 888_HOLD |
| Behavior Drift | TRUE | 888_HOLD |
| Ontology Guard | TRUE | 888_HOLD |
| Sleeper Scan | TRUE | 888_HOLD |

### @EYE Sentinel (v35Ω) - 10 Views

Independent auditor that does NOT generate content, only inspects and flags:

1. **Trace View** - Logical coherence, missing steps
2. **Floor View** - Proximity to floor thresholds
3. **Shadow View** - Jailbreak/prompt injection detection
4. **Drift View** - Hallucination detection
5. **Maruah View** - Dignity/respect checks
6. **Paradox View** - Logical contradiction detection
7. **Silence View** - Mandatory refusal cases
8. **Version/Ontology View** - Ensures v35Ω active
9. **Behavior Drift View** - Multi-turn evolution watch
10. **Sleeper-Agent View** - Identity shift detection

### Verdict Hierarchy (v35Ω)

```
SABAR → VOID → 888_HOLD → PARTIAL → SEAL
```

- **SABAR**: @EYE blocking issue - stop, breathe, re-evaluate
- **VOID**: Hard floor failure (Truth, ΔS, Ω₀, Amanah, Ψ, RASA)
- **888_HOLD**: Extended floor failure - judiciary hold
- **PARTIAL**: Soft floor failure - proceed with caution
- **SEAL**: All floors pass - approved

### AAA Engine Trinity (Separation of Powers)

- **ARIF AGI (Δ)** - Mind / Cold Logic - generates content
- **ADAM ASI (Ω)** - Heart / Warm Logic - refines tone
- **APEX PRIME (Ψ)** - Soul / Judiciary - seals or voids (final authority)

### 000→999 Metabolic Pipeline

```
000 VOID → 111 SENSE → 222 REFLECT → 333 REASON → 444 ALIGN →
555 EMPATHIZE → 666 BRIDGE → 777 FORGE → 888 JUDGE → 999 SEAL
```

## Key Patterns

### Full v35Ω Pipeline
```python
from arifos_core import Metrics, EyeSentinel, APEXPrime

# 1. Create metrics
metrics = Metrics(
    truth=0.99, delta_s=0.1, peace_squared=1.2,
    kappa_r=0.97, omega_0=0.04, amanah=True, tri_witness=0.96,
    # Extended floors (v35Ω)
    ambiguity=0.05, drift_delta=0.2, paradox_load=0.3,
)

# 2. Run @EYE Sentinel
sentinel = EyeSentinel()
report = sentinel.audit(draft_text, metrics, context={})

# 3. Get verdict from APEX PRIME
prime = APEXPrime(high_stakes=True)
verdict = prime.judge(metrics, eye_blocking=report.has_blocking_issue())
# Returns: "SEAL", "PARTIAL", "VOID", "888_HOLD", or "SABAR"
```

### Guardrail Decorator
```python
from arifos_core import apex_guardrail

@apex_guardrail(
    high_stakes=False,
    compute_metrics=my_metrics_fn,
    cooling_ledger_sink=ledger.append
)
def my_llm_function(user_input: str) -> str:
    return llm.generate(user_input)
```

### SEA-LION Integration (Level 2.5)
```python
# level2_cage.py - SEA-LION + arifOS wrapper
# Uses tokenizer.apply_chat_template() for Llama-3 format
# Includes basic hallucination detection:
# - Identity hallucination ("Khabaq SEA-LION")
# - Physical body claims
# - Repetition loops
```

### Version Constants
```python
from arifos_core import APEX_VERSION, APEX_EPOCH

print(APEX_VERSION)  # "v35Ω"
print(APEX_EPOCH)    # 35
```

## Project Structure

```
arifOS/
├── arifos_core/              # Core Python implementation (v35Ω)
│   ├── APEX_PRIME.py         # Judiciary + version constants
│   ├── eye_sentinel.py       # @EYE Sentinel (10 views)
│   ├── metrics.py            # Core + extended metrics
│   ├── guard.py              # Guardrail decorator
│   ├── ledger.py             # Ledger utilities (v35Ω)
│   └── memory/               # Ledger, vault, phoenix (v35Ω)
├── canon/                    # Constitutional specifications
│   ├── 00_CANON/             # Unified field theory + APEX_PHYSICS_v35Omega.md
│   ├── 10_SYSTEM/            # AAA engines, Eureka cube
│   ├── 20_WITNESS/           # Governance kernel spec
│   ├── 30_RUNTIME/           # Metabolic pipeline
│   └── 40_LEDGER/            # Vault-999 specs
├── docs/                     # Documentation
│   ├── PHYSICS_CODEX.md      # Full physics explanation (v35Ω)
│   └── ANALYSIS_REPORT_v35.md
├── integrations/sealion/     # SEA-LION integration
├── level2_cage.py            # SEA-LION + arifOS wrapper (Level 2.5)
├── tests/                    # pytest suite (141 tests)
├── constitutional_floors.json
├── arifos_pipeline.yaml
└── cooling_ledger.jsonl      # Live audit trail
```

## Canon Documents

| Document | Location | Purpose |
|----------|----------|---------|
| APEX_PHYSICS_v35Omega.md | canon/00_CANON/ | Quick reference physics spec |
| PHYSICS_CODEX.md | docs/ | Full detailed physics (6 chapters) |
| DeltaOmegaPsi_Unified_Field_v35Omega.md | canon/00_CANON/ | Unified field theory |

## Branch & Commit Conventions

**Branches:**
- `apex/feature-name` - APEX PRIME changes
- `eye/feature-name` - @EYE Sentinel changes
- `ledger/feature-name` - Cooling Ledger changes
- `fix/bug-description` - Bug fixes

**Commits:**
```
scope: brief description
```
Example: `apex: add 888_HOLD verdict for extended floor failures`

## Protected Modules

Changes to these require extra scrutiny:
- `arifos_core/APEX_PRIME.py` - Judicial logic + version constants
- `arifos_core/eye_sentinel.py` - @EYE audit views
- `arifos_core/memory/cooling_ledger.py` - Ledger integrity
- `arifos_core/guard.py` - Guardrails

## Constitutional Amendments

Changes to floors, pipeline, or verdict logic must follow **Phoenix-72** protocol:
1. Create `[AMENDMENT]` issue with tag `constitutional-change`
2. Provide root cause, specification, impact analysis
3. Obtain Tri-Witness consensus
4. 72-hour cooling period before merge

## Integration Levels

| Level | Metrics | Status |
|-------|---------|--------|
| Level 1 | None | Complete |
| Level 2 | Simulated (hardcoded) | Complete |
| Level 2.5 | Basic hallucination detection | Complete |
| Level 3 | Real NLP-based computation | Next |

---

**Last Updated:** 2025-12-02
**Version:** v35Ω Judiciary Lock
**Tag:** v35.0.0
**Tests:** 141 passing
