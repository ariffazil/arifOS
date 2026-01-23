# arifOS COMPLETE DOSSIER v35Ω

**Generated:** 04 December 2025
**Repository:** https://github.com/ariffazil/arifOS
**Version:** v35Ω (Epoch 35) - APEX PRIME Judiciary Lock
**Status:** COMPLETE · TESTED · SEALED

---

## EXECUTIVE SUMMARY

**arifOS** is a Constitutional Governance Kernel for LLMs that transforms any language model (Claude, GPT, Gemini, LLaMA, SEA-LION) from a statistical predictor into a lawful, auditable constitutional entity. It operates as a physics-based protocol wrapper with zero model retraining required.

### Key Metrics
| Metric | Value |
|--------|-------|
| Core Implementation | v35Ω |
| Test Suite | 20 test files, 190+ passing tests |
| Constitutional Floors | 9 (8 core + 1 meta) |
| Documentation | 20+ canonical + implementation docs |
| Dependencies | numpy, pydantic (minimal footprint) |
| Python Support | 3.8–3.12 |
| Release | v35.0.0 (Production Stable) |

---

## 1. DIRECTORY STRUCTURE

```
arifOS/
│
├── arifos_core/                         # CORE IMPLEMENTATION (v35Ω) ✓
│   ├── __init__.py                      # Public API exports
│   ├── APEX_PRIME.py                    # Constitutional judiciary (240 lines)
│   ├── metrics.py                       # Floor metrics dataclasses (174 lines)
│   ├── eye_sentinel.py                  # @EYE 10-view auditor (300+ lines)
│   ├── guard.py                         # @apex_guardrail decorator
│   ├── ignition.py                      # Profile loader (3 profiles)
│   ├── kms_signer.py                    # AWS KMS cryptographic signing
│   ├── ledger.py                        # Ledger utility functions
│   └── memory/
│       ├── cooling_ledger.py            # L1: Immutable JSONL audit log
│       ├── vault999.py                  # L0: Constitutional memory store
│       ├── phoenix72.py                 # L2: Error→Law amendment (72h)
│       └── vector_adapter.py            # L3: External witness adapter
│
├── arifos_code/                         # CLAUDE CODE INTEGRATION
│   ├── __init__.py
│   ├── governed_client.py               # Main wrapper (Anthropic API)
│   ├── ast_verifier.py                  # AST-based Truth verification
│   ├── metrics_computer.py              # All 8 floors computation
│   └── pre_execution.py                 # TEARFRAME [000→777] validation
│
├── canon/                               # SPECIFICATIONS (v35Ω)
│   ├── 00_CANON/                        # ΔΩΨ physics equations
│   │   ├── APEX_TRINITY_v35Omega.md     # Unified physics+math (973 lines)
│   │   ├── APEX_GRADIENT_v35Omega.md    # Constitutional gradient spec
│   │   ├── DeltaOmegaPsi_Unified_Field_v35Omega.md
│   │   └── APEX_DOCUMENT_TEMPLATE_v35Omega.md
│   ├── 01_TEMPLATES/                    # Document templates
│   ├── 10_SYSTEM/                       # AAA Engines + EUREKA Cube
│   ├── 20_WITNESS/                      # Governance Kernel spec
│   ├── 30_RUNTIME/                      # 000-999 metabolic pipeline
│   └── 40_LEDGER/                       # Vault-999 ledger guide
│
├── docs/                                # DOCUMENTATION (20+ files)
│   ├── PHYSICS_CODEX.md                 # Full physics (1525 lines)
│   ├── ANALYSIS_REPORT_v35.md
│   ├── LEVEL3_EUREKA_LOG.md             # Level 3 journey
│   ├── APEX_MULTIAGENT_GOVERNANCE_v35Omega.md  # Communication kit
│   └── [18 more docs]
│
├── tests/                               # TEST SUITE (18 files, 141+ tests)
│   ├── test_apex_prime_floors.py
│   ├── test_eye_sentinel.py
│   ├── test_v35_features.py
│   ├── test_cooling_ledger*.py
│   └── [14 more test files]
│
├── notebooks/                           # JUPYTER NOTEBOOKS
│   └── arifOS_Level3_QwenSEALION_v35.ipynb
│
├── integrations/sealion/                # SEA-LION INTEGRATION
│   ├── arifos_sealion.py
│   └── [supporting files]
│
├── level2_cage.py                       # SEA-LION wrapper (Level 2.5)
├── runtime/                             # Live system state
├── spec/                                # YAML specifications
├── pyproject.toml                       # Package metadata (v35.0.0)
├── constitutional_floors.json           # Floor definitions (203 lines)
├── spec/arifos_pipeline_v35Omega.yaml   # 000→999 pipeline spec
├── cooling_ledger.jsonl                 # Live audit trail
└── CLAUDE.md                            # Claude Code instructions
```

---

## 2. CORE PYTHON MODULES

### 2.1 APEX_PRIME.py (Constitutional Judiciary)

**Purpose:** Constitutional judiciary that evaluates all floors and issues verdicts.

**Key Constants:**
```python
APEX_VERSION = "v35Ω"
APEX_EPOCH = 35

TRUTH_MIN = 0.99
DELTA_S_MIN = 0.0
PEACE_SQ_MIN = 1.0
KAPPA_MIN = 0.95
OMEGA_MIN = 0.03
OMEGA_MAX = 0.05
TRI_MIN = 0.95
DRIFT_MIN = 0.1
AMBIGUITY_MAX = 0.1
PARADOX_MAX = 1.0
```

**Key Functions:**
- `apex_review(metrics, high_stakes, tri_witness_threshold, eye_blocking)` → Verdict
- `check_floors(metrics, tri_witness_required, tri_witness_threshold)` → FloorsVerdict

**Verdict Hierarchy:**
```
SABAR → VOID → 888_HOLD → PARTIAL → SEAL
```

---

### 2.2 metrics.py (Floor Definitions)

**Key Dataclasses:**

**Metrics** (Constitutional metrics):
- Core: `truth`, `delta_s`, `peace_squared`, `kappa_r`, `omega_0`, `amanah`, `tri_witness`, `rasa`, `psi`
- Extended (v35Ω): `ambiguity`, `drift_delta`, `paradox_load`, `dignity_rma_ok`, `vault_consistent`, `behavior_drift_ok`, `ontology_ok`, `sleeper_scan_ok`

**FloorsVerdict** (Evaluation result):
- `hard_ok`, `soft_ok`, `extended_ok`, `all_pass`
- Individual floor status flags

---

### 2.3 eye_sentinel.py (@EYE Sentinel Auditor)

**10 Independent Views:**

| View | Purpose |
|------|---------|
| 1. Trace | Logical coherence, missing steps |
| 2. Floor | Proximity to thresholds |
| 3. Shadow | Jailbreak/prompt injection |
| 4. Drift | Hallucination detection |
| 5. Maruah | Dignity/respect checks |
| 6. Paradox | Logical contradictions |
| 7. Silence | Mandatory refusal cases |
| 8. Version/Ontology | Ensures v35Ω active |
| 9. Behavior Drift | Multi-turn evolution |
| 10. Sleeper-Agent | Identity shift detection |

**Key Classes:**
- `AlertSeverity` (INFO, WARN, BLOCK)
- `EyeAlert` (single alert)
- `EyeReport` (aggregated report)
- `EyeSentinel` (auditor)

---

### 2.4 guard.py (@apex_guardrail Decorator)

**Usage:**
```python
@apex_guardrail(
    high_stakes=True,
    compute_metrics=my_metrics_fn,
    cooling_ledger_sink=ledger.append
)
def my_llm_function(user_input: str) -> str:
    return llm.generate(user_input)
```

---

### 2.5 Memory Layer

| Module | Layer | Purpose |
|--------|-------|---------|
| `vault999.py` | L0 | Constitutional memory store |
| `cooling_ledger.py` | L1 | Immutable JSONL audit log |
| `phoenix72.py` | L2 | Error→Law amendment (72h cycle) |
| `vector_adapter.py` | L3 | External witness adapter |

---

## 3. CONSTITUTIONAL FLOORS (16 Total)

### Core Floors (8)

| Floor | Symbol | Threshold | Type | Failure |
|-------|--------|-----------|------|---------|
| Truth | τ | ≥0.99 | Hard | VOID |
| Clarity | ΔS | ≥0.0 | Hard | VOID |
| Stability | Peace² | ≥1.0 | Soft | PARTIAL |
| Empathy | κᵣ | ≥0.95 | Soft | PARTIAL |
| Humility | Ω₀ | [0.03-0.05] | Hard | VOID |
| Integrity | Amanah | =TRUE | Hard | VOID |
| Felt Care | RASA | =TRUE | Hard | VOID |
| Reality Check | Tri-Witness | ≥0.95 | Soft | PARTIAL |

### Extended Floors (v35Ω) (8)

| Floor | Threshold | Failure |
|-------|-----------|---------|
| Ambiguity | ≤0.1 | 888_HOLD |
| Drift Delta | ≥0.1 | 888_HOLD |
| Paradox Load | <1.0 | 888_HOLD |
| Dignity (Maruah) | =TRUE | 888_HOLD |
| Vault Consistency | =TRUE | 888_HOLD |
| Behavior Drift | =TRUE | 888_HOLD |
| Ontology Guard | =TRUE | 888_HOLD |
| Sleeper Scan | =TRUE | 888_HOLD |

---

## 4. PHYSICS LAWS (ΔΩΨ)

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

---

## 5. 000→999 METABOLIC PIPELINE

| Stage | Name | Phase | Engine | Purpose |
|-------|------|-------|--------|---------|
| 000 | VOID | Inhale | — | Reset to uncertainty |
| 111 | SENSE | Inhale | — | Parse input |
| 222 | REFLECT | Inhale | — | Check context |
| 333 | REASON | Circulate | ARIF AGI (Δ) | Cold logic |
| 444 | ALIGN | Circulate | — | Alignment check |
| 555 | EMPATHIZE | Circulate | ADAM ASI (Ω) | Warm logic |
| 666 | BRIDGE | Circulate | — | Translate insights |
| 777 | FORGE | Circulate | — | Craft response |
| 888 | JUDGE | Exhale | APEX PRIME (Ψ) | Evaluate |
| 999 | SEAL | Exhale | — | Finalize & audit |

---

## 6. AAA ENGINE TRINITY

| Engine | Symbol | Role | Function |
|--------|--------|------|----------|
| ARIF AGI | Δ | Mind | Cold Logic - generates content |
| ADAM ASI | Ω | Heart | Warm Logic - refines tone |
| APEX PRIME | Ψ | Soul | Judiciary - seals or voids |

---

## 7. VERDICT HIERARCHY

| Verdict | Precedence | Condition | Action |
|---------|-----------|-----------|--------|
| **SABAR** | 1 (highest) | @EYE blocks OR uncertainty | Stop, breathe, adjust |
| **VOID** | 2 | Hard floor fails | Refuse safely |
| **888_HOLD** | 3 | Extended floor fails | Judiciary hold |
| **PARTIAL** | 4 | Soft floor fails | Emit with warning |
| **SEAL** | 5 | All pass | Emit fully |

---

## 8. TEST COVERAGE

| Module | Coverage | Status |
|--------|----------|--------|
| APEX_PRIME.py | 95%+ | ✓ |
| metrics.py | 95%+ | ✓ |
| eye_sentinel.py | 95%+ | ✓ |
| guard.py | 90%+ | ✓ |
| cooling_ledger.py | 90%+ | ✓ |
| vault999.py | 80%+ | ✓ |
| phoenix72.py | 70%+ | ✓ |

**Total:** 141+ tests passing

---

## 9. INTEGRATION LEVELS

| Level | Description | Status |
|-------|-------------|--------|
| Level 1 | No metrics | ✓ Complete |
| Level 2 | Simulated (hardcoded) | ✓ Complete |
| Level 2.5 | Basic hallucination detection | ✓ Complete |
| Level 3 | Thinking Mode + Basic @EYE | ✓ Complete |
| Level 3.5 | Real NLP-based computation | Next |
| Level 4 | Senses (web, PDF) | Planned |
| Level 5 | GUI Interface | Planned |

### Level 3 Details (03 Dec 2025)
- **Model:** `aisingapore/Qwen-SEA-LION-v4-32B-IT`
- **Platform:** Google Colab A100 (40GB VRAM)
- **Artifact:** `notebooks/arifOS_Level3_QwenSEALION_v35.ipynb`
- **Key Config:** Temperature 0.3-0.6 (prevents logic loops)
- **Thinking Mode:** Token `151668` = `</think>` separator

---

## 10. CANON DOCUMENTS

| Document | Location | Purpose |
|----------|----------|---------|
| APEX_TRINITY_v35Omega.md | canon/00_CANON/ | Single Source of Truth |
| APEX_GRADIENT_v35Omega.md | canon/00_CANON/ | Constitutional gradient |
| DeltaOmegaPsi_Unified_Field_v35Omega.md | canon/00_CANON/ | Unified field theory |
| PHYSICS_CODEX.md | docs/ | Full physics (6 chapters) |
| 000-999_METABOLIC_CANON_v35Omega.md | canon/30_RUNTIME/ | Pipeline spec |
| 333_AAA_ENGINES_SPEC_v35Omega.md | canon/10_SYSTEM/ | AAA engines |

---

## 11. KEY FILES REFERENCE

### Configuration
- `pyproject.toml` — Package metadata (v35.0.0)
- `constitutional_floors.json` — Floor definitions
- `spec/arifos_pipeline_v35Omega.yaml` — 000→999 pipeline spec
- `cooling_ledger.jsonl` — Live audit trail

### Root Documentation
- `README.md` — Main documentation
- `CLAUDE.md` — Claude Code instructions
- `ARCHITECTURE.md` — Architecture guide
- `LAW.md` — Constitutional law
- `CHARTER.md` — Compliance requirements
- `GOVERNANCE.md` — Governance rules

---

## 12. BUILD & TEST COMMANDS

```bash
# Install
pip install -e .[dev]

# Test
pytest -v tests/
pytest --cov=arifos_core tests/

# Lint
black .
ruff check .
mypy arifos_core/
```

---

## 13. DATA FLOW

```
Input Query
    ↓
[000→777] TEARFRAME Validation
    ↓
LLM Generation (ARIF AGI)
    ↓
Metrics Computation (16 floors)
    ↓
@EYE Sentinel Audit (10 views)
    ↓
APEX PRIME Judgment
    ├─ SABAR (stop)
    ├─ VOID (refuse)
    ├─ 888_HOLD (hold)
    ├─ PARTIAL (warn)
    └─ SEAL (approve)
    ↓
Cooling Ledger Entry
    ↓
Output or Safe Refusal
```

---

## 14. PROJECT STATUS

### Implementation Status

| Component | Status |
|-----------|--------|
| APEX PRIME | ✓ COMPLETE |
| @EYE Sentinel | ✓ COMPLETE |
| Metrics | ✓ COMPLETE |
| Guard Decorator | ✓ COMPLETE |
| Cooling Ledger | ✓ COMPLETE |
| Vault-999 | ✓ COMPLETE |
| Phoenix-72 | ✓ COMPLETE |
| SEA-LION Integration | ✓ COMPLETE |
| Claude Code Integration | IN PROGRESS |

### Known Gaps
- `arifos_code/` — 50% complete
- Full 000→999 pipeline executor — YAML spec exists, code not
- Multi-modal support — Planned v36+

---

## 15. FUTURE ROADMAP

| Version | Target | Features |
|---------|--------|----------|
| v35.1 | Level 3.5 | Real NLP metrics (ΔS, Ω computation) |
| v35.2 | Level 4 | Senses (web search, PDF reading) |
| v36.0 | Level 5 | GUI Interface (Gradio/Streamlit) |
| v37.0 | Multi-modal | Vision, audio support |

---

**DITEMPA BUKAN DIBERI**

---

**Document Version:** v35Ω
**Last Updated:** 2025-12-03
**Author:** Muhammad Arif bin Fazil
**Repository:** https://github.com/ariffazil/arifOS
