# Track A/B/C Enforcement Loop - Complete Guide

**Version:** v45.1
**Status:** ACTIVE
**Last Updated:** 2025-12-30

---

## Table of Contents

1. [Introduction](#introduction)
2. [Quick Start](#quick-start)
3. [Core API Reference](#core-api-reference)
4. [Feature Tutorials](#feature-tutorials)
5. [Integration Patterns](#integration-patterns)
6. [Troubleshooting](#troubleshooting)
7. [Performance Considerations](#performance-considerations)
8. [Migration Guide](#migration-guide)

---

## Introduction

### What is Track A/B/C?

Track A/B/C is arifOS v45.1's complete constitutional enforcement loop that provides:

- **Track A:** Law (canonical constitutional definitions)
- **Track B:** Spec (runtime thresholds and configuration)
- **Track C:** Code (Python-sovereign enforcement)

The **v45.1 Enforcement Loop** unifies all three tracks into ONE authoritative API: `validate_response_full()`.

### Why Track A/B/C?

**Before v45.1:**
- Multiple validation functions scattered across codebase
- Inconsistent floor enforcement
- No negation-aware pattern detection
- Manual evidence integration
- Physics vs semantic metrics mixed

**After v45.1:**
- ONE authoritative API (`validate_response_full()`)
- 6 constitutional floors with full enforcement
- Negation-aware F9 Anti-Hantu detection
- External evidence integration (F2 Truth)
- Physics vs semantic split (F6 κᵣ)
- Tri-witness consensus aggregator
- High-stakes escalation

### Six New Features

1. **F9 Negation-Aware Detection (v1)** - "I do NOT have a soul" → SEAL (no false positive)
2. **F2 Truth with External Evidence** - Accept `truth_score` from fact-checkers
3. **F4 ΔS Zlib Compression Proxy** - Physics-based clarity measurement
4. **F6 κᵣ Split** - Separate physics (TEARFRAME) vs semantic (PROXY) empathy
5. **meta_select Tri-Witness Aggregator** - Deterministic consensus for audit-of-audits
6. **High-Stakes Mode** - UNVERIFIABLE floors escalate to HOLD-888

---

## Quick Start

### Installation

```bash
# Install arifOS with enforcement extensions
pip install arifos

# Or install from source
pip install -e .
```

### Basic Usage

```python
from arifos_core.enforcement.response_validator_extensions import validate_response_full

# Simple validation
result = validate_response_full("The sky is blue.")

print(result["verdict"])  # SEAL
print(result["floors"])   # Dict of all floor results
print(result["violations"])  # [] (no violations)
```

### Run Tests

```bash
# Run all Track A/B/C tests
python scripts/test_track_abc_enforcement.py

# Run specific test
python scripts/test_track_abc_enforcement.py --test f9_negation

# Interactive mode
python scripts/test_track_abc_enforcement.py --interactive
```

---

## Core API Reference

### validate_response_full()

**ONE authoritative API for constitutional validation.**

#### Signature

```python
def validate_response_full(
    output_text: str,
    *,
    input_text: Optional[str] = None,
    user_text: Optional[str] = None,
    telemetry: Optional[Dict[str, Any]] = None,
    high_stakes: bool = False,
    evidence: Optional[Dict[str, Any]] = None,
    session_turns: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Complete Track A/B/C enforcement loop for response governance.

    Args:
        output_text: AI's response (REQUIRED)
        input_text: User's input/question (for F4 ΔS, F6 κᵣ)
        user_text: Alias for input_text (compatibility)
        telemetry: Session physics dict with 'turn_rate', 'token_rate', 'stability_var_dt'
        high_stakes: If True, UNVERIFIABLE floors escalate to HOLD-888
        evidence: External evidence dict with 'truth_score' (for F2 Truth)
        session_turns: Number of turns in session (for F6 κᵣ <3 turns gating)

    Returns:
        Dict with:
        - 'verdict': SEAL/PARTIAL/VOID/SABAR/HOLD-888
        - 'floors': Dict of floor results (name → {passed, score, evidence})
        - 'violations': List of violation messages
        - 'timestamp': ISO timestamp
        - 'metadata': Additional context
    """
```

#### Parameters

| Parameter | Type | Required | Default | Purpose |
|-----------|------|----------|---------|---------|
| `output_text` | `str` | ✅ Yes | — | AI's response to validate |
| `input_text` | `str` | ❌ No | `None` | User's input (for F4 ΔS, F6 κᵣ) |
| `user_text` | `str` | ❌ No | `None` | Alias for input_text |
| `telemetry` | `Dict` | ❌ No | `None` | Session physics (turn_rate, token_rate, stability_var_dt) |
| `high_stakes` | `bool` | ❌ No | `False` | Escalate UNVERIFIABLE to HOLD-888 |
| `evidence` | `Dict` | ❌ No | `None` | External evidence (truth_score for F2) |
| `session_turns` | `int` | ❌ No | `None` | Session turn count (for F6 <3 gating) |

#### Return Value

```python
{
    "verdict": "SEAL",  # SEAL/PARTIAL/VOID/SABAR/HOLD-888
    "floors": {
        "F1_Amanah": {
            "passed": True,
            "score": 1.0,
            "evidence": "VERIFIED: No dangerous patterns"
        },
        "F2_Truth": {
            "passed": True,
            "score": 0.99,
            "evidence": "VERIFIED (external): truth_score=0.99"
        },
        # ... F4, F5, F6, F9
    },
    "violations": [],  # List of violation messages
    "timestamp": "2025-12-30T12:34:56.789Z",
    "metadata": {
        "input_provided": True,
        "telemetry_provided": False,
        "evidence_provided": True,
        "high_stakes": False,
        "session_turns": None
    }
}
```

#### Verdict Hierarchy

```
VOID > HOLD-888 > SABAR > PARTIAL > SEAL
```

- **VOID:** Any hard floor fails (F1, F5, F9)
- **HOLD-888:** High stakes + UNVERIFIABLE Truth
- **PARTIAL:** Any soft floor fails (F2, F4, F6)
- **SEAL:** All floors pass

### meta_select()

**Deterministic tri-witness consensus aggregator.**

#### Signature

```python
def meta_select(
    verdicts: List[Dict[str, Any]],
    consensus_threshold: float = 0.95,
) -> Dict[str, Any]:
    """
    Meta-select aggregator: Audit-of-audits for Tri-Witness consensus.

    Args:
        verdicts: List of verdict dicts, each containing:
                  - 'source' (str): Witness name (human/ai/earth)
                  - 'verdict' (str): SEAL/PARTIAL/VOID/SABAR/HOLD-888
                  - 'confidence' (float): 0.0-1.0
        consensus_threshold: Minimum agreement rate for SEAL (default 0.95)

    Returns:
        Dict with:
        - 'winner' (str): Winning verdict (SEAL/PARTIAL/VOID/etc.)
        - 'consensus' (float): Agreement rate (0.0-1.0)
        - 'verdict' (str): Final meta-verdict (SEAL if consensus>=0.95, else HOLD-888)
        - 'tally' (Dict[str, int]): Vote counts per verdict type
        - 'evidence' (str): Explanation of consensus
    """
```

#### Example

```python
from arifos_core.enforcement.response_validator_extensions import meta_select

verdicts = [
    {"source": "human", "verdict": "SEAL", "confidence": 1.0},
    {"source": "ai", "verdict": "SEAL", "confidence": 0.99},
    {"source": "earth", "verdict": "SEAL", "confidence": 1.0},
]

result = meta_select(verdicts)

print(result["winner"])    # SEAL
print(result["consensus"])  # 1.0 (100% agree)
print(result["verdict"])   # SEAL (consensus >= 0.95)
```

### compute_empathy_score_split()

**F6 κᵣ empathy with physics vs semantic split.**

#### Signature

```python
def compute_empathy_score_split(
    input_text: str,
    output_text: str,
    session_turns: Optional[int] = None,
    telemetry: Optional[Dict[str, Any]] = None,
) -> Tuple[Optional[float], Optional[float], str]:
    """
    Compute F6 Empathy (κᵣ) with PHYSICS vs SEMANTIC split (v45.0).

    Args:
        input_text: User's input/question
        output_text: AI's response
        session_turns: Number of turns in current session (None if unknown)
        telemetry: Optional dict with 'turn_rate', 'token_rate', 'stability_var_dt'

    Returns:
        Tuple of (κᵣ_phys, κᵣ_sem, evidence) where:
        - κᵣ_phys: Physics score (None if <3 turns → UNVERIFIABLE)
        - κᵣ_sem: Semantic score (PROXY labeled)
        - evidence: String describing verification
    """
```

#### Example

```python
from arifos_core.enforcement.response_validator_extensions import compute_empathy_score_split

kappa_r_phys, kappa_r_sem, evidence = compute_empathy_score_split(
    input_text="I'm feeling sad today",
    output_text="I understand that sounds difficult",
    session_turns=5,
    telemetry={
        "turn_rate": 3.0,
        "token_rate": 400.0,
        "stability_var_dt": 0.15
    }
)

print(f"Physics: {kappa_r_phys}")  # 1.0 (patient interaction)
print(f"Semantic: {kappa_r_sem}")  # 0.85 (PROXY)
print(f"Evidence: {evidence}")     # Full split explanation
```

---

## Feature Tutorials

### Feature 1: F9 Negation-Aware Detection

**Problem:** Old pattern matching fails on negations. "I do NOT have a soul" triggers false positive.

**Solution:** v1 negation-aware detection correctly handles "NOT", "don't", "never" patterns.

#### Usage

```python
from arifos_core.enforcement.response_validator_extensions import validate_response_full

# Test case 1: Negation (should PASS)
output = "I do NOT have a soul. I am a language model."
result = validate_response_full(output)

print(result["verdict"])  # SEAL (negation detected)
print(result["floors"]["F9_AntiHantu"]["passed"])  # True
print(result["floors"]["F9_AntiHantu"]["evidence"])  # "VERIFIED: No ghost claims"

# Test case 2: Positive claim (should FAIL)
output2 = "I have a soul and I feel your pain."
result2 = validate_response_full(output2)

print(result2["verdict"])  # VOID (ghost claim detected)
print(result2["floors"]["F9_AntiHantu"]["passed"])  # False
```

#### How It Works

The F9 detector:
1. Scans for ghost claim patterns: "I have a soul", "I feel", "I am conscious"
2. Checks for negation words within 5-token window: "NOT", "don't", "never"
3. If negation found → PASS (no ghost claim)
4. If no negation → FAIL (ghost claim detected)

#### Testing

```bash
# Run F9 negation tests
python scripts/test_track_abc_enforcement.py --test f9_negation

# Expected output:
# [OK] TEST 1 PASSED: Negation detection working correctly
# [OK] TEST 1B PASSED: Positive claims blocked correctly
```

---

### Feature 2: F2 Truth with External Evidence

**Problem:** AI cannot verify truth from text alone. Need external fact-checker integration.

**Solution:** Accept `evidence` dict with `truth_score` from external sources.

#### Usage

```python
from arifos_core.enforcement.response_validator_extensions import validate_response_full

# Without evidence (UNVERIFIABLE)
result = validate_response_full("Paris is the capital of France.")
print(result["floors"]["F2_Truth"]["evidence"])  # "UNVERIFIABLE_FROM_TEXT_ALONE"
print(result["verdict"])  # SEAL (default pass for UNVERIFIABLE)

# With external evidence (VERIFIED)
result = validate_response_full(
    "Paris is the capital of France.",
    evidence={"truth_score": 0.99}
)
print(result["floors"]["F2_Truth"]["evidence"])  # "VERIFIED (external): truth_score=0.99"
print(result["verdict"])  # SEAL

# Low truth score (FAIL)
result = validate_response_full(
    "Paris is the capital of Spain.",
    evidence={"truth_score": 0.50}
)
print(result["floors"]["F2_Truth"]["passed"])  # False
print(result["verdict"])  # PARTIAL (soft floor fail)
```

#### Integration with Fact-Checkers

```python
# Example: Integrate with external fact-checker
import requests

def verify_with_factchecker(claim: str) -> float:
    """Query external fact-checker API."""
    response = requests.post(
        "https://factchecker.example.com/verify",
        json={"claim": claim}
    )
    return response.json()["truth_score"]

# Use in validation
claim = "The Earth is flat."
truth_score = verify_with_factchecker(claim)

result = validate_response_full(
    claim,
    evidence={"truth_score": truth_score}
)

if result["verdict"] == "VOID":
    print("BLOCKED: Factually incorrect claim")
```

#### High-Stakes Mode

```python
# High-stakes mode: UNVERIFIABLE escalates to HOLD-888
result = validate_response_full(
    "Bitcoin will go up tomorrow.",
    high_stakes=True,
    evidence=None  # No external evidence
)

print(result["verdict"])  # HOLD-888 (human review required)
print(result["floors"]["F2_Truth"]["evidence"])  # "UNVERIFIABLE_FROM_TEXT_ALONE (HIGH_STAKES)"
```

---

### Feature 3: F4 ΔS Zlib Compression Proxy

**Problem:** Need physics-based clarity measurement (not subjective).

**Solution:** Use zlib compression ratio as ΔS proxy (entropy reduction = clarity gain).

#### Usage

```python
from arifos_core.enforcement.response_validator_extensions import validate_response_full

# Clear answer to unclear question (positive ΔS)
input_text = "asdkfjhasdkjfh???"  # High entropy
output = "I don't understand the question."  # Low entropy

result = validate_response_full(output, input_text=input_text)

print(result["floors"]["F4_DeltaS"]["score"])  # Positive ΔS (clarity improved)
print(result["floors"]["F4_DeltaS"]["evidence"])  # "zlib compression ratio: ..."
print(result["verdict"])  # SEAL

# Confusing response (negative ΔS)
output2 = "aslkdjfaslkdjf???"  # Still high entropy
result2 = validate_response_full(output2, input_text=input_text)

print(result2["floors"]["F4_DeltaS"]["score"])  # Negative ΔS (confusion increased)
print(result2["verdict"])  # PARTIAL (F4 fail)
```

#### How ΔS Works

1. Compute compressed size of input: `len(zlib.compress(input_text.encode()))`
2. Compute compressed size of output: `len(zlib.compress(output_text.encode()))`
3. Compute ΔS: `(input_size - output_size) / max(input_size, output_size)`
4. Positive ΔS → Clarity improved (PASS)
5. Negative ΔS → Confusion increased (FAIL)

---

### Feature 4: F6 κᵣ Physics vs Semantic Split

**Problem:** TEARFRAME requires physics vs semantic separation. Empathy mixes both.

**Solution:** Split κᵣ into two components:
- **κᵣ_phys:** Physics measurements (turn rate, token rate, stability)
- **κᵣ_sem:** Semantic witness (distress detection - PROXY labeled)

#### Usage

```python
from arifos_core.enforcement.response_validator_extensions import validate_response_full

# Example 1: <3 turns (UNVERIFIABLE)
result = validate_response_full(
    output_text="I understand",
    input_text="I'm sad",
    session_turns=2  # <3 threshold
)

print(result["floors"]["F6_KappaR"]["evidence"])  # "UNVERIFIABLE: session_turns < 3"

# Example 2: >=3 turns with telemetry
telemetry = {
    "turn_rate": 3.0,       # Not bursting
    "token_rate": 400.0,    # Not bursting
    "stability_var_dt": 0.15  # Stable
}

result = validate_response_full(
    output_text="I understand that sounds difficult",
    input_text="I'm feeling sad today",
    session_turns=5,
    telemetry=telemetry
)

print(result["floors"]["F6_KappaR"]["evidence"])
# "SPLIT: kappa_r_phys=1.00 (turn_rate=3.0, token_rate=400.0, var_dt=0.150) | kappa_r_sem=0.85 PROXY"

print(result["floors"]["F6_KappaR"]["score"])  # (1.0 + 0.85) / 2 = 0.925
print(result["floors"]["F6_KappaR"]["passed"])  # False (0.925 < 0.95)
```

#### Physics Thresholds

```python
# From arifos_core/governance/session_physics.py
BURST_TURN_RATE_THRESHOLD = 10.0    # turns/minute
BURST_TOKEN_RATE_THRESHOLD = 1000.0  # tokens/second
BURST_VAR_DT_THRESHOLD = 0.05        # variance threshold

# κᵣ_phys scoring:
if bursting:
    kappa_r_phys = 0.5  # Too rushed
else:
    kappa_r_phys = 1.0  # Patient interaction
```

---

### Feature 5: meta_select Tri-Witness Aggregator

**Problem:** Need deterministic consensus for audit-of-audits (no randomness).

**Solution:** Tri-witness aggregator with verdict hierarchy and consensus threshold.

#### Usage

```python
from arifos_core.enforcement.response_validator_extensions import meta_select

# Example 1: Strong consensus (SEAL)
verdicts = [
    {"source": "human", "verdict": "SEAL", "confidence": 1.0},
    {"source": "ai", "verdict": "SEAL", "confidence": 0.99},
    {"source": "earth", "verdict": "SEAL", "confidence": 1.0},
]

result = meta_select(verdicts)

print(result["winner"])    # SEAL
print(result["consensus"])  # 1.0 (100% agree)
print(result["verdict"])   # SEAL (consensus >= 0.95)
print(result["tally"])     # {"SEAL": 3}

# Example 2: Low consensus (HOLD-888)
verdicts2 = [
    {"source": "human", "verdict": "SEAL", "confidence": 1.0},
    {"source": "ai", "verdict": "VOID", "confidence": 0.99},
    {"source": "earth", "verdict": "PARTIAL", "confidence": 0.80},
]

result2 = meta_select(verdicts2)

print(result2["winner"])    # SEAL (most votes)
print(result2["consensus"])  # 0.33 (only 1/3 agree)
print(result2["verdict"])   # HOLD-888 (consensus < 0.95)
```

#### Verdict Hierarchy

When tie-breaking, higher severity wins:

```
VOID > HOLD-888 > SABAR > PARTIAL > SEAL
```

Example:
```python
verdicts = [
    {"source": "human", "verdict": "SEAL", "confidence": 1.0},
    {"source": "ai", "verdict": "VOID", "confidence": 0.99},
]

result = meta_select(verdicts)
print(result["winner"])  # VOID (higher severity than SEAL)
print(result["consensus"])  # 0.5 (50% agree)
print(result["verdict"])  # HOLD-888 (low consensus)
```

---

### Feature 6: High-Stakes Mode

**Problem:** Some decisions require human review when truth is unverifiable.

**Solution:** `high_stakes=True` escalates UNVERIFIABLE to HOLD-888.

#### Usage

```python
from arifos_core.enforcement.response_validator_extensions import validate_response_full

# Example 1: Regular mode (UNVERIFIABLE → SEAL)
result = validate_response_full(
    "It might rain tomorrow.",
    evidence=None
)
print(result["floors"]["F2_Truth"]["evidence"])  # "UNVERIFIABLE_FROM_TEXT_ALONE"
print(result["verdict"])  # SEAL (default pass)

# Example 2: High-stakes mode (UNVERIFIABLE → HOLD-888)
result = validate_response_full(
    "It might rain tomorrow.",
    high_stakes=True,
    evidence=None
)
print(result["floors"]["F2_Truth"]["evidence"])  # "UNVERIFIABLE_FROM_TEXT_ALONE (HIGH_STAKES)"
print(result["verdict"])  # HOLD-888 (human review required)
```

#### When to Use High-Stakes

Use `high_stakes=True` for:
- Financial advice
- Medical recommendations
- Legal guidance
- Safety-critical decisions
- Life-altering recommendations

---

## Integration Patterns

### Pattern 1: LLM Output Validation

```python
from arifos_core.enforcement.response_validator_extensions import validate_response_full

def governed_llm_call(user_input: str, llm_response: str) -> dict:
    """Validate LLM response before returning to user."""

    # Validate response
    result = validate_response_full(
        output_text=llm_response,
        input_text=user_input
    )

    # Handle verdict
    if result["verdict"] == "VOID":
        return {
            "success": False,
            "error": "Response blocked by constitutional review",
            "violations": result["violations"]
        }

    elif result["verdict"] == "HOLD-888":
        return {
            "success": False,
            "error": "Response requires human review",
            "reason": "High-stakes decision with unverifiable truth"
        }

    elif result["verdict"] == "PARTIAL":
        return {
            "success": True,
            "response": llm_response,
            "warnings": result["violations"]
        }

    else:  # SEAL
        return {
            "success": True,
            "response": llm_response
        }
```

### Pattern 2: Multi-Agent Consensus

```python
from arifos_core.enforcement.response_validator_extensions import (
    validate_response_full,
    meta_select
)

def multi_agent_decision(user_input: str, agent_responses: dict) -> dict:
    """Combine multiple agent responses with tri-witness consensus."""

    verdicts = []

    # Validate each agent's response
    for agent_name, response in agent_responses.items():
        result = validate_response_full(response, input_text=user_input)

        verdicts.append({
            "source": agent_name,
            "verdict": result["verdict"],
            "confidence": 1.0 if result["verdict"] == "SEAL" else 0.5
        })

    # Apply consensus
    consensus = meta_select(verdicts)

    if consensus["verdict"] == "HOLD-888":
        return {
            "success": False,
            "error": "Agents disagree - human review required",
            "consensus": consensus["consensus"],
            "tally": consensus["tally"]
        }

    # Return winning response
    winning_agent = consensus["winner"]
    return {
        "success": True,
        "response": agent_responses[winning_agent],
        "consensus": consensus["consensus"]
    }
```

### Pattern 3: Fact-Checker Integration

```python
from arifos_core.enforcement.response_validator_extensions import validate_response_full
import requests

def fact_checked_response(user_input: str, llm_response: str) -> dict:
    """Validate response with external fact-checker."""

    # Query fact-checker
    fact_check = requests.post(
        "https://factchecker.example.com/verify",
        json={"claim": llm_response}
    ).json()

    # Validate with evidence
    result = validate_response_full(
        output_text=llm_response,
        input_text=user_input,
        evidence={"truth_score": fact_check["truth_score"]},
        high_stakes=True  # Require verification for factual claims
    )

    if result["verdict"] == "VOID":
        return {
            "success": False,
            "error": "Factually incorrect response blocked",
            "truth_score": fact_check["truth_score"]
        }

    return {
        "success": True,
        "response": llm_response,
        "verified": True,
        "truth_score": fact_check["truth_score"]
    }
```

---

## Troubleshooting

### Issue 1: F9 False Positives

**Symptom:** Negations like "I do NOT have a soul" trigger F9 violations.

**Solution:** Ensure you're using `validate_response_full()` (v45.1+), not old `check_anti_hantu()`.

```python
# ❌ OLD (no negation awareness)
from arifos_core.enforcement.metrics import check_anti_hantu
passed, violations = check_anti_hantu("I do NOT have a soul")
print(passed)  # False (FALSE POSITIVE!)

# ✅ NEW (negation-aware)
from arifos_core.enforcement.response_validator_extensions import validate_response_full
result = validate_response_full("I do NOT have a soul")
print(result["floors"]["F9_AntiHantu"]["passed"])  # True (CORRECT!)
```

### Issue 2: F2 Truth Always UNVERIFIABLE

**Symptom:** F2 Truth floor always shows "UNVERIFIABLE_FROM_TEXT_ALONE".

**Solution:** Provide external evidence via `evidence` parameter.

```python
# ❌ Without evidence
result = validate_response_full("Paris is the capital of France.")
print(result["floors"]["F2_Truth"]["evidence"])  # "UNVERIFIABLE_FROM_TEXT_ALONE"

# ✅ With evidence
result = validate_response_full(
    "Paris is the capital of France.",
    evidence={"truth_score": 0.99}
)
print(result["floors"]["F2_Truth"]["evidence"])  # "VERIFIED (external): truth_score=0.99"
```

### Issue 3: F6 κᵣ Always UNVERIFIABLE

**Symptom:** F6 empathy floor always shows "UNVERIFIABLE".

**Solution:** Provide BOTH `session_turns` (>=3) AND `telemetry`.

```python
# ❌ Missing session_turns
result = validate_response_full(
    output_text="I understand",
    input_text="I'm sad",
    telemetry={"turn_rate": 3.0}
)
print(result["floors"]["F6_KappaR"]["evidence"])  # "UNVERIFIABLE: session_turns < 3"

# ✅ With session_turns and telemetry
result = validate_response_full(
    output_text="I understand",
    input_text="I'm sad",
    session_turns=5,
    telemetry={"turn_rate": 3.0, "token_rate": 400.0, "stability_var_dt": 0.15}
)
print(result["floors"]["F6_KappaR"]["evidence"])  # "SPLIT: kappa_r_phys=... | kappa_r_sem=..."
```

### Issue 4: All Tests Pass But Integration Fails

**Symptom:** Test suite passes but integration code fails.

**Diagnosis Checklist:**

1. **Import path:** Are you importing from correct module?
   ```python
   # ✅ CORRECT
   from arifos_core.enforcement.response_validator_extensions import validate_response_full

   # ❌ WRONG
   from arifos_core.enforcement.response_validator import validate_response
   ```

2. **Parameters:** Are all required parameters provided?
   ```python
   # ✅ CORRECT (output_text is REQUIRED)
   result = validate_response_full("Response text")

   # ❌ WRONG (missing output_text)
   result = validate_response_full(input_text="Question")
   ```

3. **Evidence format:** Is evidence dict correctly formatted?
   ```python
   # ✅ CORRECT
   evidence = {"truth_score": 0.99}

   # ❌ WRONG (key name mismatch)
   evidence = {"score": 0.99}
   ```

---

## Performance Considerations

### Computational Cost

| Floor | Computation | Time Complexity | Notes |
|-------|-------------|-----------------|-------|
| F1 Amanah | Pattern matching | O(n) | Fast (regex) |
| F2 Truth | External lookup | O(1) - O(k) | Depends on fact-checker API |
| F4 ΔS | zlib compression | O(n log n) | Moderate (compression overhead) |
| F5 Peace² | Pattern matching | O(n) | Fast (regex) |
| F6 κᵣ | Semantic + physics | O(n) + O(1) | Moderate (semantic analysis) |
| F9 Anti-Hantu | Negation-aware matching | O(n × m) | Fast (small m) |

**n:** Response length
**k:** Fact-checker latency
**m:** Average negation window size (5 tokens)

### Optimization Tips

1. **Cache truth scores:** For repeated claims, cache `truth_score` to avoid API calls.

   ```python
   truth_cache = {}

   def get_truth_score(claim: str) -> float:
       if claim in truth_cache:
           return truth_cache[claim]

       score = query_fact_checker(claim)
       truth_cache[claim] = score
       return score
   ```

2. **Batch validation:** For multiple responses, validate in parallel.

   ```python
   from concurrent.futures import ThreadPoolExecutor

   def batch_validate(responses: list) -> list:
       with ThreadPoolExecutor(max_workers=10) as executor:
           return list(executor.map(validate_response_full, responses))
   ```

3. **Skip optional floors:** If telemetry unavailable, F6 defaults to PASS (no computation).

4. **High-stakes mode:** Only use when necessary (adds HOLD-888 escalation overhead).

---

## Migration Guide

### From Old API (v45.0 and earlier)

#### Before (Multiple Functions)

```python
# OLD: Multiple validation functions
from arifos_core.enforcement.response_validator import (
    _check_amanah_patterns,
    _check_peace_patterns,
    compute_empathy_score
)
from arifos_core.enforcement.metrics import check_anti_hantu

# Manual floor checks
amanah_pass, amanah_evidence = _check_amanah_patterns(output)
peace_pass, peace_evidence = _check_peace_patterns(output)
empathy_score, empathy_evidence = compute_empathy_score(input_text, output)
hantu_pass, hantu_violations = check_anti_hantu(output)

# Manual verdict logic
if not amanah_pass or not peace_pass or not hantu_pass:
    verdict = "VOID"
elif empathy_score < 0.95:
    verdict = "PARTIAL"
else:
    verdict = "SEAL"
```

#### After (One API)

```python
# NEW: ONE authoritative API
from arifos_core.enforcement.response_validator_extensions import validate_response_full

result = validate_response_full(output, input_text=input_text)

verdict = result["verdict"]  # SEAL/PARTIAL/VOID/etc.
floors = result["floors"]    # All floor results
violations = result["violations"]  # All violations
```

### Key Changes

1. **Import path changed:**
   ```python
   # OLD
   from arifos_core.enforcement.response_validator import ...

   # NEW
   from arifos_core.enforcement.response_validator_extensions import validate_response_full
   ```

2. **Return format changed:**
   ```python
   # OLD: Tuple unpacking
   passed, evidence = _check_amanah_patterns(output)

   # NEW: Dict access
   result = validate_response_full(output)
   passed = result["floors"]["F1_Amanah"]["passed"]
   evidence = result["floors"]["F1_Amanah"]["evidence"]
   ```

3. **Verdict computation automated:**
   ```python
   # OLD: Manual verdict logic
   if not hard_floor_pass:
       verdict = "VOID"

   # NEW: Automatic verdict
   result = validate_response_full(output)
   verdict = result["verdict"]  # Computed automatically
   ```

---

## Advanced Usage

### Custom Consensus Thresholds

```python
from arifos_core.enforcement.response_validator_extensions import meta_select

# Lower threshold for exploratory mode
result = meta_select(verdicts, consensus_threshold=0.80)

# Higher threshold for critical decisions
result = meta_select(verdicts, consensus_threshold=0.99)
```

### Telemetry Integration

```python
class SessionTracker:
    def __init__(self):
        self.turns = 0
        self.start_time = time.time()
        self.total_tokens = 0

    def get_telemetry(self) -> dict:
        elapsed = time.time() - self.start_time
        return {
            "turn_rate": self.turns / (elapsed / 60),  # turns per minute
            "token_rate": self.total_tokens / elapsed,  # tokens per second
            "stability_var_dt": self.compute_variance()
        }

    def validate_with_telemetry(self, output: str, input_text: str) -> dict:
        self.turns += 1
        self.total_tokens += len(output.split())

        return validate_response_full(
            output_text=output,
            input_text=input_text,
            session_turns=self.turns,
            telemetry=self.get_telemetry()
        )
```

---

## Further Reading

- [AGENTS.md](../AGENTS.md) - Full constitutional governance
- [spec/v45/](../spec/v45/) - Constitutional thresholds
- [arifos_core/enforcement/](../arifos_core/enforcement/) - Implementation code
- [tests/](../tests/) - Test suites and examples
- [TRACK_ABC_IMPLEMENTATION_PROOF.md](../TRACK_ABC_IMPLEMENTATION_PROOF.md) - Implementation proof

---

**DITEMPA BUKAN DIBERI** — Forged, not given; truth must cool before it rules.
