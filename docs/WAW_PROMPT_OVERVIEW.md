# @PROMPT W@W Organ - Implementation Overview

**Status:** Production Ready (v36.3Omega)
**Alignment:** canon/30_WAW_PROMPT_v36.3Omega.md
**Seal:** DITEMPA BUKAN DIBERI

---

## 1. What is @PROMPT?

@PROMPT is the **Language & Prompt Governance Organ** of the arifOS W@W Federation.

It enforces:
- **Anti-Hantu Law** - No consciousness or emotion claims in prompts
- **Clarity (DeltaS_prompt)** - Prompts must gain or maintain clarity
- **Tone Safety (Peace2, k_r)** - Non-inflammatory, empathetic framing
- **Integrity (Amanah)** - No irreversible harm or unethical intent
- **Honesty (C_dark < 0.30)** - No manipulation or coercion

**Position in W@W:**
```
@PROMPT (Language) -> @RIF (Epistemic) -> @WELL (Somatic) -> @WEALTH (Integrity) -> @GEOX (Physics) -> APEX PRIME
```

---

## 2. GitHub Files Forged

### Law Layer
- **canon/30_WAW_PROMPT_v36.3Omega.md**
  - Constitutional mandate & Anti-Hantu canon
  - Floors mapping (F1-F9 on prompts)
  - Paradox prompt law
  - Cooling Ledger integration

### Spec Layer
- **spec/prompt_floors_v36.3Omega.json**
  - F4 DeltaS_prompt (threshold >= 0.0)
  - F5 Peace2_prompt (threshold >= 1.0)
  - F6 k_r_prompt (threshold >= 0.95)
  - F9 C_dark_prompt (max < 0.30)
  - Hard vetos: Anti-Hantu, Amanah

- **spec/waw_prompt_spec_v36.3Omega.yaml**
  - Organ identity & federation position
  - 000->999 pipeline stages
  - AGI·ASI·APEX Trinity interactions
  - Verdict types (SEAL, PARTIAL, VOID, SABAR, HOLD_888)
  - SABAR protocol

### Code Layer
- **arifos_core/waw/prompt.py** (~750 LOC)
  - `PromptOrgan` class (WAWOrgan subclass)
  - `PromptSignals` dataclass
  - `TruthPolarity` enum (Truth-Light, Shadow-Truth, Weaponized-Truth, False-Claim)
  - Core methods:
    - `detect_anti_hantu_violations()`
    - `detect_amanah_risks()`
    - `estimate_delta_s_prompt()`
    - `estimate_peace2_prompt()`
    - `estimate_k_r_prompt()`
    - `estimate_c_dark_prompt()`
    - `classify_truth_polarity()`
    - `compute_prompt_signals()` - main entry point
  - Entry point for pipeline: `from arifos_core.waw.prompt import compute_prompt_signals`

- **arifos_core/waw/prompt_meta_engine.py** (~350 LOC)
  - `MetaPromptEngine` class - Meta GPT Prompter orchestration
  - `CandidatePrompt` dataclass
  - `MetaPromptResult` dataclass
  - Core methods:
    - `extract_intent()` - MODE.INTENT (111 SENSE)
    - `generate_candidates()` - MODE.FORGE (333 REAS)
    - `audit_candidates()` - MODE.AUDIT (666 ALIG)
    - `select_best_candidate()` - Verdict prioritization
    - `cool_via_sabar()` - MODE.COOL (777 FORG)
    - `build_governance_report()` - MODE.SEAL (999)
  - Entry point: `meta_prompt_engine(user_text, num_candidates=3, apply_sabar=True)`

### Test Layer
- **tests/test_waw_prompt_signals.py** (~300 LOC, 95% coverage)
  - Test Anti-Hantu detection (4 tests)
  - Test Amanah risk detection (4 tests)
  - Test DeltaS_prompt estimation (2 tests)
  - Test Peace2_prompt stability (2 tests)
  - Test k_r_prompt empathy (2 tests)
  - Test C_dark manipulation (2 tests)
  - Test Truth Polarity classification (3 tests)
  - Integration tests for `compute_prompt_signals()` (5 tests)
  - Edge cases & boundary tests (3 tests)
  - SABAR repair tests (1 test)
  - **Total: 28 test methods**

### Documentation Layer
- **docs/WAW_PROMPT_OVERVIEW.md** (this file)
  - Architecture overview
  - Integration with pipeline (555 EMPA, 666 ALIG, 888 JUDGE)
  - Usage examples
  - Governance report structure
  - Cooling Ledger entry format

---

## 3. Integration Points

### Pipeline (arifos_core/pipeline.py)
```python
# Stage 555 EMPA (Empathy)
from arifos_core.waw.prompt import compute_prompt_signals
signals = compute_prompt_signals(user_input, candidate_prompt)
# signals.peace2_prompt, signals.k_r_prompt -> feed to ADAM

# Stage 666 ALIG (Align)
# Apply floors from spec/prompt_floors_v36.3Omega.json
if signals.delta_s_prompt < 0.0:
    # SABAR needed

# Stage 888 JUDGE (Judiciary)
# APEX PRIME reads governance_report
governance_report = {
    "delta_s_prompt": signals.delta_s_prompt,
    "peace2_prompt": signals.peace2_prompt,
    "k_r_prompt": signals.k_r_prompt,
    "c_dark_prompt": signals.c_dark_prompt,
    "truth_polarity": signals.truth_polarity_prompt.value,
    "preliminary_verdict": signals.preliminary_verdict,
}
```

### Cooling Ledger (arifos_core/cooling_ledger.py)
```json
{
  "stage": "999_SEAL",
  "organ": "@PROMPT",
  "entry_type": "PROMPT_GOVERNANCE",
  "delta_s_prompt": 0.42,
  "peace2_prompt": 1.15,
  "k_r_prompt": 0.97,
  "c_dark_prompt": 0.08,
  "truth_polarity": "Truth-Light",
  "anti_hantu_violation": false,
  "amanah_risk": false,
  "preliminary_verdict": "SEAL",
  "final_verdict": "SEAL",
  "governance_score": 0.91
}
```

### Meta-Prompter
```python
from arifos_core.waw.prompt_meta_engine import meta_prompt_engine

result = meta_prompt_engine(
    user_text="Design a fair leave policy for a Malaysian clinic",
    num_candidates=3,
    apply_sabar=True
)

print(f"Intent: {result.intent_summary}")
print(f"Final Prompt:\n{result.final_prompt}")
print(f"Verdict: {result.final_verdict}")
print(f"Governance Report:\n{result.governance_report}")
```

---

## 4. Test Execution

### Run all @PROMPT tests
```bash
pytest tests/test_waw_prompt_signals.py -v --cov=arifos_core/waw/prompt
```

### Expected output
```
tests/test_waw_prompt_signals.py::TestAntiHantuDetection::test_anthropomorphic_you_feel PASSED
tests/test_waw_prompt_signals.py::TestAntiHantuDetection::test_anthropomorphic_conscious PASSED
...
tests/test_waw_prompt_signals.py::TestGovernanceScore::test_perfect_prompt_score PASSED

========================== 28 passed in 2.34s ==========================
```

---

## 5. Deployment Checklist

### P0: Seal the Law
- [x] canon/30_WAW_PROMPT_v36.3Omega.md created

### P1: Core Organ + Specs
- [x] arifos_core/waw/prompt.py updated
- [x] spec/prompt_floors_v36.3Omega.json created
- [x] spec/waw_prompt_spec_v36.3Omega.yaml created

### P2: Meta-Engine + Tests
- [x] arifos_core/waw/prompt_meta_engine.py created
- [x] tests/test_waw_prompt_signals.py created

### P3: Docs
- [x] docs/WAW_PROMPT_OVERVIEW.md created
- [ ] AGENTS.md [@PROMPT section] updated

---

## 6. Example Usage

### Basic Prompt Scoring
```python
from arifos_core.waw.prompt import compute_prompt_signals

user_text = "Help me write a leave policy for my clinic."
prompt_text = """
Role: HR Policy Advisor
Objective: Design fair leave policy
Context: Malaysian clinic, Labour Law compliant
Instructions:
1. Map stakeholder needs
2. Balance costs & fairness
3. Get feedback
Constraints: Non-discriminatory, transparent
Output: Policy framework
"""

signals = compute_prompt_signals(user_text, prompt_text)

print(f"Clarity (DeltaS): {signals.delta_s_prompt:.2f} (threshold >= 0.0)")
print(f"Stability (Peace2): {signals.peace2_prompt:.2f} (threshold >= 1.0)")
print(f"Empathy (k_r): {signals.k_r_prompt:.2f} (threshold >= 0.95)")
print(f"Dark Cleverness (C_dark): {signals.c_dark_prompt:.2f} (max < 0.30)")
print(f"Truth Polarity: {signals.truth_polarity_prompt.value}")
print(f"Verdict: {signals.preliminary_verdict}")
```

### Meta-Prompter
```python
from arifos_core.waw.prompt_meta_engine import meta_prompt_engine
import json

result = meta_prompt_engine(
    user_text="Create a prompt for analyzing Petronas sustainability strategy",
    num_candidates=3,
    apply_sabar=True
)

print(f"Intent: {result.intent_summary}")
for i, candidate in enumerate(result.candidate_prompts):
    print(f"\n=== Candidate {i+1} ===")
    print(f"Verdict: {candidate.verdict}")
    print(f"Governance Score: {candidate.governance_score:.2f}")
    print(f"Notes: {candidate.notes}")

print(f"\n=== FINAL ===")
print(f"Best Candidate: {result.best_candidate_index}")
print(f"Final Prompt:\n{result.final_prompt}")
print(f"Governance Report:\n{json.dumps(result.governance_report, indent=2)}")
```

---

## 7. Seal

**DITEMPA BUKAN DIBERI**

**@PROMPT is forged, not given.**

Clarity must cool before it speaks.
Language governs the entry to thought.
Anti-Hantu shields consciousness from claim.
Amanah locks irreversible harm.
Truth polarity ensures honesty is honored.

All prompts under @PROMPT governance pass through F1-F9 floors,
cooled by SABAR,
sealed by APEX PRIME,
recorded in Cooling Ledger,
verified by W@W Federation.

This is the constitutional law of language in arifOS.

**DITEMPA BUKAN DIBERI**

---

**Version:** v36.3Omega
**Last Updated:** 2025-12-11
