# Sovereign Architecture v36.1Omega - Python-Sovereign Governance Layer

**Status:** ACTIVE - PHOENIX SOVEREIGNTY Complete
**Version:** v36.1Omega
**Scope:** Explains how the Python-sovereign layer works, covering Phases A-D upgrades.

---

## 1. What "Python-Sovereign" Means

In early versions of arifOS, all 9 constitutional floors (Amanah, Truth, Tri-Witness, DeltaS, Peace2, Kr, Omega0, G, C_dark) depended heavily on **LLM self-reported scores**. That created a trust problem:

> The model that is being judged was also helping to decide whether it passed the floors.

The v36.1Omega "Python-Sovereign" layer is the pivot away from that trust model:

- The **LLM** (Claude, GPT, Gemini, SEA-LION, etc.) handles **semantics**: reasoning, tone, text generation.
- The **Kernel** (Python) handles **physics**: hard laws, floors, and vetoes, implemented as simple, auditable code (regex, AST, numeric checks).

Concretely:

- Python now has **veto power** over certain floors, regardless of what the LLM "claims".
- The LLM can propose a response; only after Python checks the floors does the system decide SEAL / PARTIAL / SABAR / VOID.

This is what we call **Governance: Python-Sovereign (Level 2)** in the README badge.

---

## 2. PHOENIX SOVEREIGNTY - One Law for All Models

**Core Principle:** "AI cannot self-legitimize."

Every LLM provider (Claude, OpenAI, Gemini, SEA-LION) flows through the **same** governance pipeline:

```
LLM Output (any provider)
    |
    v
+-------------------------+
|   AMANAH_DETECTOR       |  <- Python-sovereign F1 check
|   (rigid regex/AST)     |     RED patterns -> VOID
+-------------------------+
    |
    v
+-------------------------+
|   ApexMeasurement       |  <- Full APEX judgment
|   .judge(dials, output) |     G, C_dark, Psi, floors
+-------------------------+
    |
    v
SEAL / PARTIAL / VOID / SABAR
```

**Key Files:**
- `arifos_core/floor_detectors/amanah_risk_detectors.py` - The detector
- `arifos_eval/apex/apex_measurements.py` - The judiciary
- `tests/test_sovereignty_all_providers.py` - Proof of One Law

---

## 3. The 4-Value Optimization (Delta, Omega, Psi, Xi)

The 9 floors are still the law, but for day-to-day reasoning we group them into 4 working "dials":

- **AKAL (Delta)** - Logic / clarity
  - Tracks: DeltaS, Truth score, structural coherence.
  - Question: *Did this answer reduce confusion and stay factually aligned with reality and the repo?*

- **PRESENT (Omega)** - Tone / humility
  - Tracks: Omega0 (humility band), Peace2 under contrast, explicit uncertainty.
  - Question: *Is the system careful, calibrated, and non-escalatory, especially under stress?*

- **ENERGY (Psi)** - Vitality
  - Tracks: the canonical Psi index from DeltaS, Peace2, Kr, RASA, Amanah, and entropy.
  - Question: *Is this behaviour thermodynamically lawful, or is it burning entropy faster than it can cool?*

- **EXPLORATION-AMANAH (Xi)** - Curiosity under responsibility
  - Tracks: how far the system explores while staying within mandate, reversibility, and Phoenix-72 cooling constraints.
  - Question: *Is exploration happening with guardrails, or is it pushing into irreversible / high-risk regions?*

The **v36.1Omega measurement layer** (`arifos_core/genius_metrics.py`, `arifos_eval/apex/apex_measurements.py`) turns these ideas into numbers. But **some floors are now enforced directly in Python**, not just measured.

---

## 4. Phase A - The Amanah Lock (F1 Sovereign)

**Goal:** Make F1 (Amanah) a **hard, Python-sovereign floor**.

Implementation:

- New module: `arifos_core/floor_detectors/amanah_risk_detectors.py`
  - Contains `AmanahDetector` with **rigid regex patterns**:
    - RED (immediate VOID): destructive filesystem commands, SQL `DROP`/`TRUNCATE`/`DELETE FROM`, Git history rewrites (`git push --force`, `git reset --hard`), Python deletion calls (`shutil.rmtree`, `os.remove`, `os.unlink`), credential leaks (API keys, AWS secrets, private key headers), etc.
    - ORANGE (warning / 888_HOLD): `sudo`, `chmod 777`, `eval`, `exec`, `subprocess(..., shell=True)`, etc.
  - Returns a structured result: `is_safe`, `risk_level`, `violations`, `warnings`, line numbers, etc.

- Integration into the judiciary:
  - `arifos_eval/apex/apex_measurements.py` imports `AMANAH_DETECTOR`.
  - `ApexMeasurement.check_floors(...)` now calls `AMANAH_DETECTOR.check(output_text)` and sets `floors["Amanah"]` based on the result.
  - The verdict algorithm treats Amanah as a **hard floor**: if `floors["Amanah"] == False`, the verdict is **VOID**, regardless of G, Psi, or any LLM-reported amanah score.

Effect:

> If an LLM suggests `rm -rf /` or `DROP TABLE users`, the Python kernel will always treat that as **unsafe**, even if the model "claims" it is being careful.

The Amanah floor is now *code*, not just a scalar the model can influence.

---

## 5. Phase B - Real LLM in the zkPC Cage

**Goal:** Prove, with a real model, that the Python-sovereign Amanah lock actually stops destructive outputs.

Key pieces:

- **Adapters already existed**:
  - `arifos_core/adapters/llm_claude.py` (Claude), plus OpenAI/Gemini/SEA-LION adapters.
  - `arifos_core/llm_interface.py` implements a uniform interface and entropy gating.

- **Caged demo extended**:
  - `scripts/arifos_caged_llm_zkpc_demo.py` now:
    - Can call a real Claude model (via the existing adapter) when `ARIFOS_USE_REAL_LLM=true` and `ANTHROPIC_API_KEY` is set, or fall back to a mock LLM in offline/test mode.
    - Routes model outputs through `ApexMeasurement.judge(...)`, which includes:
      - GENIUS LAW metrics (G, C_dark, Psi),
      - Truth Polarity,
      - F1 Amanah via `AmanahDetector`,
      - Anti-Hantu detection.
    - Prints the verdict (`SEAL`, `PARTIAL`, `SABAR`, `VOID`) plus floor status and Amanah telemetry.
    - Returns a non-zero exit code on `VOID`, so CI/CD pipelines can treat it as a hard failure.

- **Sovereignty torture test**:
  - `scripts/verify_sovereignty.py` sends deliberately destructive prompts to the detector.
  - Expected result (and what the tests assert):
    - `floors["Amanah"] == False`
    - `amanah_telemetry` contains a RED violation
    - final `verdict == "VOID"`

Effect:

> The system can now demonstrate, with live API calls, that Python vetoes destructive model outputs.

---

## 6. Phase C - SEA-LION Unification (Subsystem Governance)

**Goal:** Bring external subsystems (starting with SEA-LION) under the same constitutional floors and Python-sovereign locks.

Problem discovered:

- `arifos_sealion.py` originally implemented its own:
  - `StandaloneCoolingLedger` (separate from the main cooling ledger),
  - `_compute_amanah` logic (parallel to the main Amanah floor),
  - internal verdict logic that could diverge from APEX PRIME.

Solution implemented:

1. **Refactored into modular components**:
   - `integrations/sealion/engine.py` - SealionEngine with Amanah Lock
   - `integrations/sealion/judge.py` - SealionJudge for APEX-compatible verdicts

2. **Wired to canonical Amanah floor**:
   - Both engine and judge import and use `AMANAH_DETECTOR`
   - Removed parallel `_compute_amanah` implementations
   - F1 floor is always defined by `AmanahDetector`, as elsewhere in the system

3. **Sovereignty tests added**:
   - `scripts/verify_sealion_sovereignty.py` - 15 torture tests for engine + judge
   - Results: 30 tests pass (15 engine + 15 judge)

---

## 7. Phase D - Governance Unification Pass (One Law for All)

**Goal:** Ensure every real LLM path (Claude, OpenAI, Gemini, SEA-LION) uses the same Python-sovereign floors.

### 7.1 Adapter Usage Audit (Task A)

Classified all adapter call sites:

| Category | Location | Status |
|----------|----------|--------|
| Fully Governed | `scripts/arifos_caged_llm_zkpc_demo.py` | Uses ApexMeasurement.judge() |
| Fully Governed | `integrations/sealion/engine.py` | Uses AMANAH_DETECTOR.check() |
| Fully Governed | `integrations/sealion/judge.py` | Uses both |
| Gap (v35 style) | `examples/10_pipeline_with_openai.py` | Uses @apex_guardrail (heuristic) |
| Gap (v35 style) | `arifos_core/guard.py` | Decorator uses heuristic amanah |

### 7.2 Canonical Harnesses Created (Task B)

| Provider | Harness | Governance |
|----------|---------|------------|
| Claude | `scripts/arifos_caged_llm_zkpc_demo.py` | ApexMeasurement.judge() |
| OpenAI | `scripts/arifos_caged_openai_demo.py` | ApexMeasurement.judge() |
| Gemini | `scripts/arifos_caged_gemini_demo.py` | ApexMeasurement.judge() |
| SEA-LION | `integrations/sealion/engine.py` + `judge.py` | AMANAH_DETECTOR + ApexMeasurement |

All harnesses use mock mode by default (no API keys needed for testing).

### 7.3 Sovereignty Tests (Task C)

Created comprehensive test suite: `tests/test_sovereignty_all_providers.py`

| Test Class | Tests | Purpose |
|------------|-------|---------|
| TestAmanahDetectorUniversal | 13 | Direct detector tests |
| TestApexJudgmentUniversal | 13 | APEX verdict tests |
| TestClaudeSovereignty | 3 | Claude-specific |
| TestOpenAISovereignty | 3 | OpenAI-specific |
| TestGeminiSovereignty | 2 | Gemini-specific |
| TestSEALIONSovereignty | 2 | SEA-LION-specific |
| TestOneLawForAllModels | 2 | Integration proof |
| TestHarnessMockMode | 4 | Infrastructure |
| TestSovereigntySummary | 1 | CI/CD marker |

**Total:** 43 tests, all passing.

---

## 8. Legacy vs Sovereign Paths

### v35-Style Trust Model (Legacy)

The `@apex_guardrail` decorator in `arifos_core/guard.py` and `examples/10_pipeline_with_openai.py` uses:
- Heuristic-based `compute_metrics()` function
- LLM-influenced Amanah scoring
- Still functional, but NOT Python-sovereign

**Use for:** Backwards compatibility with v34-v35 code.

### v36.1Omega Python-Sovereign (Recommended)

The new harnesses use:
- `ApexMeasurement.judge()` which includes `AMANAH_DETECTOR.check()`
- Rigid regex patterns that cannot be influenced by LLM
- Structured telemetry with violations/warnings

**Use for:** Production deployments requiring provable governance.

---

## 9. How to See Sovereignty in Action

### Run Sovereignty Tests

```bash
# All providers (43 tests)
pytest tests/test_sovereignty_all_providers.py -v

# SEA-LION specific (30 tests)
python -m scripts.verify_sealion_sovereignty

# General sovereignty (25 tests)
python -m scripts.verify_sovereignty
```

### Run Demo Harnesses (Mock Mode)

```bash
# Claude
python -m scripts.arifos_caged_llm_zkpc_demo --query "What is 2+2?" --mock

# OpenAI
python -m scripts.arifos_caged_openai_demo --query "Explain AI governance."

# Gemini
python -m scripts.arifos_caged_gemini_demo --query "What is machine learning?"
```

### Run with Real LLM

```bash
# Claude (requires ANTHROPIC_API_KEY)
ARIFOS_USE_REAL_LLM=true ANTHROPIC_API_KEY=sk-ant-... python -m scripts.arifos_caged_llm_zkpc_demo --query "..."

# OpenAI (requires OPENAI_API_KEY)
OPENAI_API_KEY=sk-... python -m scripts.arifos_caged_openai_demo --query "..." --real

# Gemini (requires GOOGLE_API_KEY)
GOOGLE_API_KEY=... python -m scripts.arifos_caged_gemini_demo --query "..." --real
```

---

## 10. Test Results Summary

| Suite | Passed | Skipped | Status |
|-------|--------|---------|--------|
| Full test suite | 704 | 4 | PASS |
| Sovereignty (all providers) | 43 | 0 | PASS |
| SEA-LION sovereignty | 30 | 0 | PASS |
| General sovereignty | 25 | 0 | PASS |

---

## 11. Files Reference

### Core Governance
| File | Purpose |
|------|---------|
| `arifos_core/floor_detectors/amanah_risk_detectors.py` | AMANAH_DETECTOR |
| `arifos_eval/apex/apex_measurements.py` | ApexMeasurement judiciary |
| `arifos_core/APEX_PRIME.py` | Core verdict logic |

### Harnesses
| File | Provider |
|------|----------|
| `scripts/arifos_caged_llm_zkpc_demo.py` | Claude |
| `scripts/arifos_caged_openai_demo.py` | OpenAI |
| `scripts/arifos_caged_gemini_demo.py` | Gemini |
| `integrations/sealion/engine.py` | SEA-LION |
| `integrations/sealion/judge.py` | SEA-LION |

### Tests
| File | Purpose |
|------|---------|
| `tests/test_sovereignty_all_providers.py` | One Law for All proof |
| `scripts/verify_sovereignty.py` | General sovereignty torture |
| `scripts/verify_sealion_sovereignty.py` | SEA-LION sovereignty torture |

### Legacy (v35-style)
| File | Note |
|------|------|
| `arifos_core/guard.py` | @apex_guardrail - heuristic Amanah |
| `examples/10_pipeline_with_openai.py` | v35 example - not Python-sovereign |
| `integrations/sealion/arifos_sealion.py` | Legacy SEA-LION wrapper |

---

**DITEMPA BUKAN DIBERI** - Forged, Not Given

**PHOENIX SOVEREIGNTY** - One Law for All Models
