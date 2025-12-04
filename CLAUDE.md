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

# Run all tests (190 tests)
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

**APEX Gradient (Constitutional Learning):**
```
∇_APEX = G_TW · (ΔP · Ω_P · Ψ_P · κᵣ · RASA · Amanah) / (Z + ε)
```
Where G_TW = soft Tri-Witness gate, Z = 1 + Lₚ + Rₘ + Λ (shadow normalization)

## Architecture

### Core Module (`arifos_core/`)

| File | Purpose |
|------|---------|
| `APEX_PRIME.py` | Constitutional judiciary - issues SEAL/PARTIAL/VOID/888_HOLD/SABAR verdicts |
| `eye_sentinel.py` | @EYE Sentinel - 10 independent audit views (v35Omega) |
| `metrics.py` | Core + extended floor metric dataclasses |
| `guard.py` | `@apex_guardrail` decorator for wrapping functions |
| `pipeline.py` | 000-999 metabolic pipeline executor with Class A/B routing |
| `llm_interface.py` | LLM streaming interface with entropy monitoring + SABAR triggers |
| `kms_signer.py` | AWS KMS cryptographic signing for ledger |
| `adapters/llm_sealion.py` | SEA-LION adapter (local GPU, Colab) |
| `adapters/llm_openai.py` | OpenAI GPT adapter (API) |
| `adapters/llm_claude.py` | Anthropic Claude adapter (API) |
| `adapters/llm_gemini.py` | Google Gemini adapter (API) |
| `memory/cooling_ledger.py` | L1: Immutable JSONL audit log with hash-chaining |
| `memory/vault999.py` | L0: Constitutional memory store |
| `memory/phoenix72.py` | L2: Error→Law amendment engine (72h cycle) |
| `memory/vector_adapter.py` | L3: External witness/vector evidence |
| `memory/scars.py` | Scar memory - negative constraints from past failures |
| `memory/void_scanner.py` | VOID pattern detection for constitutional violations |

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
| APEX_TRINITY_v35Omega.md | canon/00_CANON/ | Unified Physics+Math+Language (Single Source of Truth) |
| APEX_GRADIENT_v35Omega.md | canon/00_CANON/ | Constitutional gradient / Scar Vector spec |
| ARIFOS_EUREKA_ARCHIVE_v35Omega.md | canon/00_CANON/ | Philosophical foundations & paradox map |
| DeltaOmegaPsi_Unified_Field_v35Omega.md | canon/00_CANON/ | Unified field theory (ANNEX) |
| PHYSICS_CODEX.md | docs/ | Full detailed physics (6 chapters) |
| ARIFOS_COMPLETE_CONTEXT_v35Omega.md | docs/ | Complete context guide for AI/Human onboarding |
| DOSSIER_v35Omega.md | root | Full repository map and status |

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
| Level 3 | Thinking Mode + Basic @EYE | **Complete** |
| Level 3.5 | Real NLP-based computation | Next |

### Level 3: Qwen-SEA-LION Integration (03 Dec 2025)

**Model:** `aisingapore/Qwen-SEA-LION-v4-32B-IT`
**Platform:** Google Colab A100 (40GB VRAM)
**Artifact:** `notebooks/arifOS_Level3_QwenSEALION_v35.ipynb`

**Key Learnings:**

| Config | Result |
|--------|--------|
| `temperature=0.0` (Greedy) | Model stalls in logic loops |
| `temperature=0.3-0.6` (Balanced) | Stable, deliberate output |
| `temperature>0.8` | Too chaotic, floor violations |

**Thinking Mode:**
- Token `151668` = `</think>` separator
- Use `enable_thinking=True` in `apply_chat_template()`
- Parse thinking trace vs final output for transparency

**Basic @EYE Checks:**
- Identity hallucination: "saya makan", "my body", physical claims
- Arrogance/Ω drift: "100%", "pasti", absolute certainty

See `docs/LEVEL3_EUREKA_LOG.md` for full journey documentation.

---

## Repository Status Map (04 Dec 2025)

### Module Implementation Status

| Module | Path | Status | Coverage |
|--------|------|--------|----------|
| APEX PRIME | `arifos_core/APEX_PRIME.py` | ✓ COMPLETE | 95%+ |
| Metrics | `arifos_core/metrics.py` | ✓ COMPLETE | 95%+ |
| @EYE Sentinel | `arifos_core/eye_sentinel.py` | ✓ COMPLETE | 95%+ |
| Guard Decorator | `arifos_core/guard.py` | ✓ COMPLETE | 90%+ |
| Ignition | `arifos_core/ignition.py` | ✓ COMPLETE | 80%+ |
| KMS Signer | `arifos_core/kms_signer.py` | ✓ COMPLETE | 85%+ |
| Cooling Ledger | `arifos_core/memory/cooling_ledger.py` | ✓ COMPLETE | 90%+ |
| Vault-999 | `arifos_core/memory/vault999.py` | ✓ COMPLETE | 80%+ |
| Phoenix-72 | `arifos_core/memory/phoenix72.py` | ✓ COMPLETE | 70%+ |
| Vector Adapter | `arifos_core/memory/vector_adapter.py` | ✓ COMPLETE | 80%+ |
| **Pipeline** | `arifos_core/pipeline.py` | ✓ **NEW** | 90%+ |
| **LLM Interface** | `arifos_core/llm_interface.py` | ✓ **NEW** | 85%+ |
| **Scars Memory** | `arifos_core/memory/scars.py` | ✓ **NEW** | 80%+ |
| **VOID Scanner** | `arifos_core/memory/void_scanner.py` | ✓ **NEW** | 75%+ |
| **LLM Adapters** | `arifos_core/adapters/` | ✓ **NEW** | 85%+ |
| Claude Code Client | `arifos_code/governed_client.py` | ⚠ IN PROGRESS | 50% |
| AST Verifier | `arifos_code/ast_verifier.py` | ⚠ IN PROGRESS | 40% |
| Metrics Computer | `arifos_code/metrics_computer.py` | ⚠ IN PROGRESS | 40% |

### Directory Map

```
arifos_core/           ✓ COMPLETE - Core constitutional runtime
├── APEX_PRIME.py      ✓ Judiciary (240 lines)
├── metrics.py         ✓ Floor definitions (174 lines)
├── eye_sentinel.py    ✓ 10-view auditor (300+ lines)
├── guard.py           ✓ @apex_guardrail decorator
├── ignition.py        ✓ Profile loader (3 profiles)
├── kms_signer.py      ✓ AWS KMS signing
├── pipeline.py        ✓ 000-999 metabolic pipeline executor (NEW)
├── llm_interface.py   ✓ LLM streaming + entropy monitoring (NEW)
├── adapters/          ✓ LLM backend adapters (NEW)
│   ├── __init__.py    ✓ Adapter registry
│   ├── llm_sealion.py ✓ SEA-LION (local GPU)
│   ├── llm_openai.py  ✓ OpenAI API
│   ├── llm_claude.py  ✓ Anthropic Claude API
│   └── llm_gemini.py  ✓ Google Gemini API
└── memory/            ✓ L0-L3 memory layers
    ├── vault999.py    ✓ L0: Constitutional store
    ├── cooling_ledger.py ✓ L1: Audit log
    ├── phoenix72.py   ✓ L2: Amendment engine
    ├── vector_adapter.py ✓ L3: Witness adapter
    ├── scars.py       ✓ Scar memory (negative constraints) (NEW)
    └── void_scanner.py ✓ VOID pattern detection (NEW)

arifos_code/           ⚠ IN PROGRESS - Claude Code integration
├── governed_client.py ⚠ Main wrapper (framework done)
├── ast_verifier.py    ⚠ AST Truth verification
├── metrics_computer.py ⚠ Floor computation
└── pre_execution.py   ⚠ TEARFRAME validation

canon/                 ✓ COMPLETE - Specifications (12 files)
├── 00_CANON/          ✓ Physics (APEX_TRINITY is source of truth)
├── 01_TEMPLATES/      ✓ Document templates
├── 10_SYSTEM/         ✓ AAA Engines + EUREKA Cube
├── 20_WITNESS/        ✓ Governance Kernel spec
├── 30_RUNTIME/        ✓ 000-999 metabolic pipeline
└── 40_LEDGER/         ✓ Vault-999 guide

docs/                  ✓ COMPLETE - Documentation (20+ files)
├── PHYSICS_CODEX.md   ✓ Full physics (1525 lines, 6 chapters)
├── LEVEL3_EUREKA_LOG.md ✓ Level 3 journey
├── APEX_MULTIAGENT_GOVERNANCE_v35Omega.md ✓ Communication kit
└── [17 more docs]

notebooks/             ✓ COMPLETE - Colab demos (NEW)
├── arifos_v35_sealion_demo.ipynb    ✓ SEA-LION + full pipeline
└── arifos_v35_max_context_demo.ipynb ✓ API-based LLM demo

tests/                 ✓ COMPLETE - 20 files, 190+ tests
integrations/sealion/  ✓ COMPLETE - SEA-LION wrapper
```

### Key Artifacts

| Artifact | Path | Purpose |
|----------|------|---------|
| SEA-LION Demo | `notebooks/arifos_v35_sealion_demo.ipynb` | SEA-LION + full pipeline (Colab) |
| Max-Context Demo | `notebooks/arifos_v35_max_context_demo.ipynb` | API LLM + full pipeline (Colab) |
| Level 3 Notebook | `notebooks/arifOS_Level3_QwenSEALION_v35.ipynb` | Qwen-SEA-LION integration |
| Floor Definitions | `constitutional_floors.json` | Machine-readable floors |
| Pipeline Spec | `arifos_pipeline.yaml` | 000→999 stages |
| Audit Trail | `cooling_ledger.jsonl` | Live ledger |
| Full Dossier | `DOSSIER_v35Omega.md` | Complete repo map (local) |

### What's Next (Roadmap)

| Version | Target | Description |
|---------|--------|-------------|
| v35.1 | Level 3.5 | Real NLP metrics (semantic ΔS, confidence Ω) |
| v35.2 | Level 4 | Senses (web search, PDF reading) |
| v36.0 | Level 5 | GUI Interface (Gradio/Streamlit) |

### Known Gaps

1. **`arifos_code/`** — Claude Code integration 50% complete
2. **SABAR handler** — Function stubs exist, full implementation pending

---

## LLM Adapters

### SEA-LION (Local GPU)
```python
from arifos_core.adapters.llm_sealion import make_llm_generate, SEALION_MODELS

# Available models (verified on Hugging Face Dec 2024):
# - "llama-8b": aisingapore/Llama-SEA-LION-v3-8B-IT (T4 compatible)
# - "qwen-32b": aisingapore/Qwen-SEA-LION-v4-32B-IT (A100 required)
# - "qwen-32b-4bit": aisingapore/Qwen-SEA-LION-v4-32B-IT-4BIT (quantized)
# - "gemma-27b": aisingapore/Gemma-SEA-LION-v4-27B-IT

generate = make_llm_generate(model="llama-8b")
response = generate("Apa khabar?")
```

### API-based LLMs
```python
# OpenAI
from arifos_core.adapters.llm_openai import make_llm_generate
generate = make_llm_generate(api_key="sk-...")

# Claude
from arifos_core.adapters.llm_claude import make_llm_generate
generate = make_llm_generate(api_key="sk-ant-...")

# Gemini
from arifos_core.adapters.llm_gemini import make_llm_generate
generate = make_llm_generate(api_key="...")
```

---

**Last Updated:** 2025-12-04
**Version:** v35Omega Judiciary Lock
**Tag:** v35.0.0
**Tests:** 190 passing
