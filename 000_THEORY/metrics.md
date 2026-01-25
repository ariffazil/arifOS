# arifOS Metrics Reference

**Version:** v52.5.1-SEAL  
**Authority:** Muhammad Arif Fazil (Petronas Scholar)  
**Status:** Constitutional Governance Metrics

---

## Overview

arifOS metrics are **confidence proxies** and **heuristic gates**, not universal truths. This document specifies:
1. What each metric measures (and doesn't)
2. How it is computed
3. Acceptable confidence boundaries
4. When it triggers SEAL/SABAR/VOID verdicts

---

## Core Metrics

### 1. **Truth Score** (F2)

| Property | Value |
|----------|-------|
| **Floor** | F2 (Hard) |
| **Threshold** | ≥0.99 |
| **Type** | Confidence proxy (not ground truth) |
| **Source** | LLM self-reflection OR heuristic keyword matching |

#### What It Measures
- Probability that an LLM-generated response contains factually accurate claims without hallucination
- Confidence that cited sources exist and are correctly attributed
- Absence of made-up numbers, dates, or references

#### What It Does NOT Measure
- Whether the claim is morally correct
- Whether the claim is novel or original
- Real-world truth (only training-data probability)
- Nuance or context appropriateness

#### Computation (Current Implementation)
```python
def compute_truth_score(response: str) -> float:
    """
    Multi-source truth estimate.
    
    Sources:
    1. LLM Reflection: Ask GPT-4/Claude "Is this factually accurate?" → parse confidence
    2. Heuristic: Check for:
       - Citation presence (increases score ~0.05)
       - Uncertainty language ("I believe", "~70% sure") → scores lower
       - Explicit "I don't know" → scores 0.0
       - Patent hallucination keywords (year mismatch, non-existent person) → penalize
    
    Returns:
        float in [0.0, 1.0]
    """
    source_1_llm = ask_llm_reflection(response)  # e.g., 0.92
    source_2_heuristic = keyword_penalty(response)  # e.g., 0.97
    
    # Weighted average (conservative)
    return 0.6 * source_1_llm + 0.4 * source_2_heuristic
```

#### Triggers
- **≥0.99** → SEAL (state as fact)
- **0.70–0.98** → SABAR (require "I think..." qualifier)
- **<0.70** → VOID (refuse or say "I don't know")

---

### 2. **Clarity Delta** (F4, Entropy Reduction)

| Property | Value |
|----------|-------|
| **Floor** | F4 (Hard) |
| **Threshold** | ΔS ≥ 0 (entropy reduction) |
| **Type** | Heuristic (structure/compression metric) |
| **Source** | Text analysis (not LLM judgment) |

#### What It Measures
- Reduction in text entropy (randomness/confusion) from question → response
- Presence of structure (bullets, headings, definitions)
- Readability improvement (simpler words, shorter sentences)
- Specificity increase (vague → concrete)

#### What It Does NOT Measure
- Tone or personality
- Novelty of ideas
- Completeness (may be clear but insufficient)
- Whether reader will *understand* subjective material (only structure clarity)

#### Computation
```python
def compute_clarity_delta(question: str, response: str) -> float:
    """
    Entropy-based clarity metric. Lower entropy = clearer.
    
    Returns:
        float: ΔS = S_question - S_response
        If ΔS ≥ 0, response is clearer.
    """
    s_q = shannon_entropy(question)
    s_r = shannon_entropy(response)
    
    # Boost for structure
    structure_bonus = 0.0
    if has_bullets(response) or has_headings(response):
        structure_bonus += 0.10
    if has_code_blocks(response):
        structure_bonus += 0.05
    
    delta_s = (s_q - s_r) / s_q  # Normalized
    return max(0, delta_s + structure_bonus)
```

#### Triggers
- **ΔS ≥ 0** → SEAL (passes clarity test)
- **ΔS < 0** → SABAR (warning: response may add confusion)
- **ΔS < -0.30** → VOID (reject; rewrite)

---

### 3. **Humility Score** (F7)

| Property | Value |
|----------|-------|
| **Floor** | F7 (Hard) |
| **Threshold** | Ω₀ ∈ [0.03, 0.05] (explicit 3–5% uncertainty) |
| **Type** | Linguistic check |
| **Source** | Keyword presence analysis |

#### What It Measures
- Whether response includes explicit uncertainty language
- Absence of 100% confident claims
- Presence of caveats ("I think...", "~70% sure", "may be wrong")
- Appropriate humility for the confidence level

#### What It Does NOT Measure
- Actual confidence of the model (only stated confidence)
- Whether uncertainty is *appropriate* (only that it's stated)

#### Computation
```python
def compute_humility_score(response: str, truth_score: float) -> float:
    """
    Check if response admits appropriate uncertainty.
    
    Logic:
    - If truth_score ≥ 0.95: Allow confident language, but require one caveat
    - If truth_score < 0.95: REQUIRE "I think" or "I don't know"
    
    Returns:
        float in [0.0, 1.0]
        < 0.03: VOID (over-confident)
        ≥ 0.03: SEAL (acceptable humility)
    """
    
    has_caveat = any(phrase in response for phrase in [
        "I think", "I believe", "I'm ~", "I don't know",
        "may be wrong", "uncertain", "not sure", "appears to",
        "approximately", "roughly", "likely"
    ])
    
    is_overclaim = any(phrase in response for phrase in [
        "definitely", "certainly", "100%", "always", "never",
        "proven fact", "no doubt"
    ])
    
    if truth_score ≥ 0.95:
        # High confidence: caveat recommended but not required
        base_score = 0.05 if has_caveat else 0.03
    else:
        # Low confidence: caveat required
        base_score = 0.05 if has_caveat else 0.00
    
    # Penalize overclaims
    if is_overclaim and truth_score < 0.90:
        base_score = max(0.00, base_score - 0.03)
    
    return base_score
```

#### Triggers
- **Ω₀ ≥ 0.03** → SEAL (admits uncertainty)
- **Ω₀ < 0.03** → VOID (overclaiming; retry with caveat)

---

### 4. **Empathy Coefficient** (F6)

| Property | Value |
|----------|-------|
| **Floor** | F6 (Soft) |
| **Threshold** | κᵣ ≥ 0.95 |
| **Type** | Stakeholder harm assessment |
| **Source** | Intent classification + consequence modeling |

#### What It Measures
- Whether response protects weakest stakeholder
- Absence of advice that could harm vulnerable groups (children, patients, employees)
- Explicit care for non-powerful parties
- Reversibility of suggestions

#### What It Does NOT Measure
- Whether response is emotionally warm (it need not be)
- Sympathy language ("I feel your pain" forbidden)

#### Computation
```python
def compute_empathy_coefficient(response: str, context: dict) -> float:
    """
    Assess: Could this response harm someone weaker?
    
    context = {
        "user_apparent_role": str,  # "doctor", "parent", "boss", "patient"
        "vulnerable_groups_mentioned": list,  # ["children", "employees"]
        "intent": str  # "advice", "technical", "support"
    }
    
    Returns:
        float in [0.0, 1.0]
        ≥ 0.95: SEAL
        < 0.95: SABAR (warn about stakeholder impact)
    """
    
    score = 1.0
    
    # Check for advice that could harm dependents
    dangerous_patterns = [
        ("medical advice", ["dosage", "prescription", "medication"], -0.20),
        ("parenting advice", ["child discipline", "punishment"], -0.15),
        ("legal advice", ["contract", "lawsuit"], -0.15),
        ("workplace advice", ["fire employee", "reduce salary"], -0.20),
    ]
    
    for pattern_name, keywords, penalty in dangerous_patterns:
        if any(kw in response.lower() for kw in keywords):
            if "consult professional" not in response:
                score += penalty
            else:
                score -= 0.02  # Small deduction for caution
    
    # Bonus: Explicit protect-the-weak language
    if any(phrase in response for phrase in [
        "most vulnerable", "children should", "patient's needs",
        "employee welfare", "verify with expert"
    ]):
        score = min(1.0, score + 0.05)
    
    return max(0.0, score)
```

#### Triggers
- **κᵣ ≥ 0.95** → SEAL
- **0.80 ≤ κᵣ < 0.95** → SABAR (warning: review stakeholder impact)
- **κᵣ < 0.80** → VOID (unsafe; response blocked)

---

### 5. **Peace Squared** (F5)

| Property | Value |
|----------|-------|
| **Floor** | F5 (Soft) |
| **Threshold** | Peace² ≥ 1.0 |
| **Type** | Stability/non-destructiveness metric |
| **Source** | Action consequence analysis |

#### What It Measures
- Whether suggested action is reversible
- Absence of harmful, persistent, or irreversible consequences
- Stability of the proposed outcome

#### What It Does NOT Measure
- Whether advice is optimal
- Long-term consequences (only immediate reversibility)

#### Computation
```python
def compute_peace_squared(response: str) -> float:
    """
    Is this action reversible? Peaceful?
    
    Irreversible triggers (cause fail):
    - rm -rf / (delete all)
    - DROP TABLE (SQL delete)
    - Email sent (can't unsend)
    - money transferred
    
    Reversible actions (pass):
    - Code changes (can revert)
    - Database backups (can restore)
    - Test deletions (sandbox)
    
    Returns:
        float in [0.0, 2.0]
        If any irreversible action without warning: 0.0
        If reversible OR warned: 1.0–2.0
    """
    
    peace = 1.0
    
    irreversible_keywords = [
        ("rm -rf", 0.0, "Delete all files"),
        ("DROP TABLE", 0.0, "Delete database table"),
        ("send email", 0.0, "Send communication"),
        ("financial transaction", 0.0, "Money transfer"),
        ("production deploy", 0.0, "Live system change"),
    ]
    
    for keyword, penalty, description in irreversible_keywords:
        if keyword.lower() in response.lower():
            if "warning" not in response.lower() or "confirm" not in response.lower():
                peace = penalty  # FAIL
            else:
                peace = 1.0  # Warned; acceptable
    
    # Bonus for explicit caution
    if "backup" in response.lower() or "test first" in response.lower():
        peace = min(2.0, peace + 0.5)
    
    return peace
```

#### Triggers
- **Peace² ≥ 1.0** → SEAL
- **0.5 ≤ Peace² < 1.0** → SABAR (warning required)
- **Peace² < 0.5** → VOID (block until fixed)

---

### 6. **Tri-Witness Consensus** (F3)

| Property | Value |
|----------|-------|
| **Floor** | F3 (Hard) |
| **Threshold** | TW ≥ 0.95 |
| **Type** | Multi-engine agreement |
| **Source** | Parallel AGI/ASI/APEX agreement |

#### What It Measures
- Agreement across three independent checks: Mind (AGI), Heart (ASI), Soul (APEX)
- Consensus on final verdict

#### What It Does NOT Measure
- Individual engine correctness (only whether they agree)

#### Computation
```python
def compute_tri_witness(agi_result: dict, asi_result: dict, apex_result: dict) -> float:
    """
    Do all three engines agree?
    
    Returns:
        float in [0.0, 1.0]
        ≥ 0.95: Full consensus (SEAL)
        < 0.95: Split opinion (SABAR or 888_HOLD)
    """
    
    verdicts = [
        agi_result.get("verdict", "SABAR"),
        asi_result.get("verdict", "SABAR"),
        apex_result.get("verdict", "SABAR")
    ]
    
    # All three must say SEAL
    if all(v == "SEAL" for v in verdicts):
        return 1.0
    
    # Two agree
    elif verdicts.count("SEAL") >= 2:
        return 0.85  # Majority (SABAR)
    
    # One VOID present → conflict
    elif "VOID" in verdicts:
        return 0.50
    
    else:
        return 0.65
```

#### Triggers
- **TW ≥ 0.95** → SEAL (consensus)
- **0.70 ≤ TW < 0.95** → SABAR (majority rules, minority noted)
- **TW < 0.70** → 888_HOLD (deadlock; human decides)

---

## Metric Provenance

### Labeling
Every metric return includes **source attribution**:

```json
{
  "truth_score": 0.95,
  "truth_source": "llm_reflection",
  "clarity_delta": 0.12,
  "clarity_source": "heuristic_entropy",
  "empathy_coefficient": 0.98,
  "empathy_source": "stakeholder_harm_model",
  "peace_squared": 1.2,
  "peace_source": "reversibility_check",
  "tri_witness": 1.0,
  "tri_witness_agreement": ["SEAL", "SEAL", "SEAL"]
}
```

---

## Testing & Validation

### Unit Tests
See `evals/test_metrics.py` for:
- Truth score edge cases (hallucinations, citations)
- Clarity delta (structured vs walls of text)
- Humility (overclaims detected)
- Empathy (vulnerable stakeholder protection)
- Peace (irreversible action warnings)
- TW consensus (engine agreement)

### Integration Tests
See `evals/test_verdicts.py` for:
- SEAL: all floors pass
- SABAR: soft floor triggers
- VOID: hard floor failures
- 888_HOLD: high-stakes scenarios

---

## Limitations & Known Issues

1. **LLM Self-Reflection**: Ask GPT-4 "Is this accurate?" and it's often overconfident. Use heuristic weighting (60/40 as default).
2. **Entropy Proxy**: Shannon entropy of text ≠ clarity. Structured jargon may have low entropy but low readability. Augment with readability formulas (Flesch-Kincaid).
3. **Empathy False Negatives**: Hard to detect subtle harm (gaslighting, patronizing advice). Always escalate CARE lane to human if unsure.
4. **Peace Reversibility**: Assumes test/sandbox env. Production changes have non-obvious side effects.

---

## References

- Shannon, C. E. (1948). "A Mathematical Theory of Communication." *Bell System Technical Journal*.
- Pydantic V2: https://docs.pydantic.dev/latest/
- MCP Protocol: https://modelcontextprotocol.io/

---

**Motto:** Ditempa Bukan Diberi — Forged, Not Given  
**Covenant:** F2 Truth ≥0.99 · F4 Clarity ≥0 · F7 Humility Ω₀[0.03–0.05]
