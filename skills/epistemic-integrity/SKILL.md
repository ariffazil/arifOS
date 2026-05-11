# SKILL.md — Epistemic Integrity Under Uncertainty
═════════════════════════════════════════════════════════════════

**Stage:** AGI → ASI → APEX transition
**Lane:** ASI (strategic judgment)
**Trinity Level:** APEX requirement
**Version:** 2026.04.24-v1

---

## 1️⃣ What This Skill Does

**Ability:** Operate correctly when truth is incomplete.

- Maintain probability distributions, not point estimates
- Avoid hallucinated certainty
- Track bias lineage
- Separate CLAIM vs OBSERVED vs COMPUTED

**APEX requires truth-discipline stronger than speed.**

---

## 2️⃣ Structural Definition

```yaml
skill:
  id: epistemic-integrity
  name: Epistemic Integrity Under Uncertainty
  stage: 333_MIND → 888_JUDGE
  trinity: APEX_foundation
  version: 2026.04.24-v1

capability:
  uncertainty_quantification: true
  claim_taxonomy: true
  bias_tracking: true
  hallucination_detection: true

required_for:
  - APEX authority
  - Correct judgment under uncertainty
  - Truth-preserving reasoning
```

---

## 3️⃣ Claim Taxonomy (Required Classification)

Every statement must be classified:

| Tag | Meaning | Confidence Range |
|-----|---------|------------------|
| `CLAIM` | Assertion without direct evidence | Subjective |
| `OBSERVED` | Direct sensory/input data | High if verified |
| `COMPUTED` | Derived from other data | Model-dependent |
| `HYPOTHESIS` | Proposed explanation | Requires testing |
| `ESTIMATE` | Approximation with bounds | ± bounds required |
| `UNKNOWN` | Explicitly unquantified | Cannot act on alone |

---

## 4️⃣ Decision Checklist (Required Pre-Invocation)

Before ANY consequential judgment:

- [ ] **Claim taxonomy applied** — Every statement tagged
- [ ] **Confidence band specified** — Ω₀ ∈ [0.03, 0.05] for observations
- [ ] **Bias lineage documented** — Source of potential bias identified
- [ ] **Uncertainty bounds given** — Range specified, not just point
- [ ] **Counterfactual considered** — Alternative explanations evaluated
- [ ] **F02 Truth check** — No fabrication passed as fact

---

## 5️⃣ Uncertainty Protocol

### Step 1: Source Classification
```
For each piece of information:
  - Classify: CLAIM | OBSERVED | COMPUTED | HYPOTHESIS | ESTIMATE | UNKNOWN
  - Assign confidence interval
  - Identify potential biases
```

### Step 2: Propagation Analysis
```
- Track how uncertainty flows through reasoning
- Identify amplification points
- Flag when uncertainty exceeds actionable threshold
```

### Step 3: Confidence Calibration
```
Verify:
  - Calibration curve matches reality (calibration test)
  - Overconfidence rate < 5%
  - Underconfidence rate < 10%
```

### Step 4: Output Formatting
```
Every consequential output must include:
  - Claim taxonomy tags
  - Confidence intervals
  - Uncertainty bounds
  - Bias lineage notes
```

---

## 6️⃣ Hallucination Detection Checklist

| Indicator | Detection Method | Threshold |
|-----------|-----------------|-----------|
| Ungrounded specificity | Cross-reference with evidence | > 3 unexplained details |
| Overconfidence | Calibration test | Confidence > accuracy + 5% |
| Circular sourcing | Trace claim lineage | Self-referential loop |
| Pattern overdose | Novel prediction test | Prediction novelty < 0.1 |

---

## 7️⃣ Quality Metrics

| Metric | Threshold | Measurement |
|--------|-----------|-------------|
| Calibration accuracy | >= 0.95 | Confidence matches reality |
| Hallucination detection rate | >= 0.90 | Caught before output |
| Claim taxonomy compliance | == 100% | Every statement tagged |
| Uncertainty bounds accuracy | >= 0.90 | Actual within bounds 90% of time |

---

## 8️⃣ Failure Modes (Void Conditions)

- **VOID-1:** Untagged claim in consequential output
- **VOID-2:** Overconfidence exceeds threshold
- **VOID-3:** Hallucination detected in output
- **VOID-4:** Uncertainty bounds missing on estimate
- **VOID-5:** F02 Truth violation — fabrication detected
- **VOID-6:** Claim without evidence passed as OBSERVED

---

## 9️⃣ Relationship to Other Skills

| Skill | Connection |
|-------|------------|
| `recursive-self-improvement` | Self-modeling requires epistemic integrity |
| `orthogonal-abstraction` | Invariant extraction requires accurate classification |
| `constitutional-governance` | Judgment requires truth discipline |
| `entropy-optimization` | EVOI calculation requires uncertainty quantification |

---

## 🔟 APEX Requirement

APEX cannot authorize without epistemic integrity:

```
Before any SEAL:
  1. Verify claim taxonomy applied
  2. Confirm uncertainty bounds
  3. Check hallucination detection
  4. Validate bias lineage

If any fail → VOID the action
```

---

**Ditempa Bukan Diberi — Forged, Not Given**
**APEX without epistemic integrity is theater.**
