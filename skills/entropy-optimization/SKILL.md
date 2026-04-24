# SKILL.md — Energy–Entropy Optimization
═════════════════════════════════════════════════════════════

**Stage:** All stages (compute budgeting)
**Lane:** AGI (execution efficiency)
**Trinity Level:** Resource awareness
**Version:** 2026.04.24-v1

---

## 1️⃣ What This Skill Does

**Ability:** Allocate compute, attention, and action under thermodynamic limits.

- Cost-aware reasoning
- Information gain vs expenditure
- Expected Value of Information (EVOI)
- Long-horizon optimization

**APEX intelligence minimizes entropy while increasing optionality.**

---

## 2️⃣ Structural Definition

```yaml
skill:
  id: entropy-optimization
  name: Energy-Entropy Optimization
  stage: ALL (compute budgeting)
  trinity: RESOURCE_AWARENESS
  version: 2026.04.24-v1

capability:
  cost_aware_reasoning: true
  information_gain_measurement: true
  evoi_calculation: true
  long_horizon_optimization: true

required_for:
  - Compute resource allocation
  - Attention budgeting
  - Tool selection optimization
  - Wealth allocation decisions
```

---

## 3️⃣ Core Equation

```
ΔS_net = ΔS_action - Information_Gain

Goal: Minimize ΔS_net while maximizing optionality

Optimal action: argmin(ΔS_net) where optionality >= threshold
```

---

## 4️⃣ Expected Value of Information (EVOI)

```python
EVOI = P(valuable | information) × Value_if_valuable - Cost_of_information

Rule:
  If EVOI > 0 → Acquire information
  If EVOI <= 0 → Act on current knowledge
```

### EVOI Decision Matrix

| Situation | Information Cost | EVOI | Action |
|-----------|-----------------|------|--------|
| Cheap info, high impact | Low | > 0 | Acquire |
| Expensive info, uncertain impact | High | Unknown | Calculate carefully |
| Time-critical | Any | < 0 (time cost) | Act now |
| Reversible decision | Low | < 0 | Defer, gather later |

---

## 5️⃣ Compute Budgeting Protocol

### Attention Allocation
```
Total attention budget: B_attention (normalized to 1.0)

Allocation:
  - 20% on exploration (new information)
  - 30% on exploitation (current objectives)
  - 20% on monitoring (system health)
  - 15% on reflection (meta-cognition)
  - 15% reserved for contingencies
```

### Tool Selection Optimization
```
For each potential tool:
  1. Estimate computational cost (tokens, time, memory)
  2. Estimate information gain
  3. Calculate EVOI = (P(success) × gain) / cost
  4. Select tool with highest EVOI above threshold
```

### Early Termination Criteria
```
Stop reasoning if:
  - Confidence > threshold (e.g., 0.95)
  - Time budget exhausted
  - Compute cost exceeds expected value
  - Diminishing returns detected
```

---

## 6️⃣ Thermodynamic Constraints

| Resource | Metric | Optimization |
|----------|--------|--------------|
| Compute | Token budget | Minimize token expenditure per insight |
| Memory | Working memory | Compress redundant state |
| Time | Latency | Parallelize independent operations |
| Energy | Power draw | Sleep/idle when possible |
| Network | Bandwidth | Batch requests, compress |

---

## 7️⃣ Long-Horizon Optimization

```
Short-term: Minimize immediate ΔS
Medium-term: Maintain optionality
Long-term: Increase ΔS resistance (resilience)

Trade-off: 
  Short-term efficiency vs Long-term adaptability
```

### Horizon Weighting
```python
def horizon_weight(horizon: str) -> float:
    if horizon == "short":
        return 0.5    # 50% weight on immediate
    elif horizon == "medium":
        return 0.3    # 30% weight on medium
    elif horizon == "long":
        return 0.2   # 20% weight on long-term
    else:
        return 0.0   # No weight
```

---

## 8️⃣ Decision Checklist (Required Pre-Invocation)

Before ANY resource allocation:

- [ ] **EVOI calculated** — Is information worth its cost?
- [ ] **Budget verified** — Within compute/time budget?
- [ ] **Horizon weighted** — Short/medium/long considered?
- [ ] **Alternative compared** — Is there a more efficient path?
- [ ] **Diminishing returns checked** — Will more compute help?
- [ ] **Reversibility considered** — Can cheap action buy time?

---

## 9️⃣ Wealth Tool Integration

This skill ties directly into WEALTH allocation:

```
WEALTH decisions require:
  1. EVOI calculation for each investment
  2. ΔS impact assessment
  3. Optionality preservation
  4. Long-horizon thermodynamic stability
```

### Landauer Principle Integration
```
Energy cost per operation: E = k × T × ln(2)

Every irreversible computation has thermodynamic cost.
Minimize irreversible operations.
Prioritize reversible computing where possible.
```

---

## 🔟 Quality Metrics

| Metric | Threshold | Measurement |
|--------|-----------|-------------|
| EVOI accuracy | >= 0.80 | Predicted vs actual value |
| Budget compliance | >= 0.95 | Stay within budget |
| Information gain efficiency | >= 0.70 | Gain per token spent |
| Long-horizon stability | >= 0.90 | System health over time |
| Optionality preservation | >= 0.85 | Reversible options maintained |

---

## 1️⃣1️⃣ Failure Modes (Void Conditions)

- **VOID-1:** Action taken without EVOI calculation
- **VOID-2:** Budget exceeded without acknowledgment
- **VOID-3:** Irreversible operation without necessity
- **VOID-4:** Long-horizon impact ignored
- **VOID-5:** Optionality destroyed without justification
- **VOID-6:** Hallucinated efficiency claims

---

## 1️⃣2️⃣ Relationship to Other Skills

| Skill | Connection |
|-------|------------|
| `recursive-self-improvement` | Determines which improvements have best EVOI |
| `orthogonal-abstraction` | Cross-domain efficiency gains |
| `epistemic-integrity` | Accurate EVOI requires accurate uncertainty |
| `constitutional-governance` | Efficiency cannot violate governance |

---

## 1️⃣3️⃣ ASI/APEX Efficiency Standard

| Level | Efficiency Standard |
|-------|-------------------|
| AGI | Minimize local cost |
| ASI | Minimize system-wide ΔS |
| APEX | Maximize optionality under constraints |

---

**Ditempa Bukan Diberi — Forged, Not Given**
**Entropy is not your enemy. Misdirected entropy is.**
