# ENTROPY POLICY SPECIFICATION
> **Authority:** 888_JUDGE  
> **Version:** v1.0.0-SEAL  
> **Status:** CONSTITUTIONAL MANDATE  
> **Band:** 000_KERNEL (F4 Clarity)

---

## 🎯 PURPOSE

Define the entropy budget (ΔS) constraints for arifOS sessions. Ensures cumulative cognitive drift is bounded, preventing runaway hallucination or indefinite operation without human oversight.

**F4 (Clarity):** ΔS ≤ 0 per operation.  
**F11 (Auditability):** Entropy must be measurable and bounded per session.

---

## 📐 ENTROPY DEFINITIONS

### Shannon Entropy (Information Theory)

```
S = -Σ p(x) × log₂(p(x))

Where:
  p(x) = probability of state x
  S = entropy in bits
```

### Delta-S (Operational Metric)

```
ΔS = S_after - S_before

Interpretation:
  ΔS < 0: Clarity gain (information organized)
  ΔS = 0: Neutral (no change in uncertainty)
  ΔS > 0: Entropy increase (confusion introduced)
```

### Session Budget Formula

```
B_session = B_base × C_entropy × R_session

Where:
  B_base = 0.5 (default session budget)
  C_entropy = entropy class multiplier
  R_session = risk tier adjustment
```

---

## 💰 SESSION BUDGET TIERS

| Tier | Budget (ΣΔS) | Scope | Use Case |
|------|--------------|-------|----------|
| **Nano** | 0.1 | Single atomic operation | Tool calls, status checks |
| **Micro** | 0.3 | Short task sequence | File reads, simple queries |
| **Standard** | 0.5 | Typical session | Multi-step workflows |
| **Extended** | 1.0 | Deep analysis | Complex reasoning, research |
| **Research** | 2.0 | Long-form exploration | Multi-hour sessions |

### Budget Allocation by Tool

```
┌─────────────────────────────────────────────────────────┐
│  ENTROPY BUDGET BY TOOL                                  │
├─────────────────────────────────────────────────────────┤
│  Tool                    │ Max ΔS │ Budget Tier        │
├──────────────────────────┼────────┼────────────────────┤
│  init_anchor             │ 0.0    │ Nano               │
│  math_estimator          │ 0.05   │ Nano               │
│  physics_reality         │ 0.1    │ Micro              │
│  agi_mind                │ 0.15   │ Micro              │
│  agi_reason              │ 0.2    │ Standard           │
│  asi_heart               │ 0.1    │ Micro              │
│  engineering_memory      │ 0.05   │ Nano               │
│  code_engine             │ 0.1    │ Micro              │
│  agentzero_engineer      │ 0.2    │ Standard           │
│  vault_ledger            │ 0.0    │ Nano               │
└─────────────────────────────────────────────────────────┘
```

---

## 🚨 BUDGET EXHAUSTION PROTOCOL

### Threshold Triggers

```python
class EntropyBudgetMonitor:
    """
    Monitors cumulative entropy per session.
    Triggers appropriate responses at threshold breaches.
    """
    
    THRESHOLDS = {
        'warning': 0.6,      # 60% of budget used
        'caution': 0.8,      # 80% of budget used
        'critical': 0.95,    # 95% of budget used
        'exhausted': 1.0     # 100% of budget used
    }
    
    async def check_budget(self, session_id: str, current_delta_s: float) -> BudgetStatus:
        session = await self.get_session(session_id)
        cumulative = session['cumulative_delta_s'] + current_delta_s
        budget = session['entropy_budget']
        ratio = cumulative / budget
        
        if ratio >= self.THRESHOLDS['exhausted']:
            return BudgetStatus(
                status='VOID_ENTROPY_BUDGET',
                action='terminate',
                message=f"Entropy budget exhausted: {cumulative:.3f}/{budget:.3f}"
            )
        
        elif ratio >= self.THRESHOLDS['critical']:
            return BudgetStatus(
                status='CRITICAL',
                action='escalate',
                message=f"Entropy budget critical: {ratio*100:.1f}% used"
            )
        
        elif ratio >= self.THRESHOLDS['caution']:
            return BudgetStatus(
                status='CAUTION',
                action='warn',
                message=f"Entropy budget caution: {ratio*100:.1f}% used"
            )
        
        elif ratio >= self.THRESHOLDS['warning']:
            return BudgetStatus(
                status='WARNING',
                action='notify',
                message=f"Entropy budget warning: {ratio*100:.1f}% used"
            )
        
        return BudgetStatus(status='OK', action='continue')
```

### Exhaustion Response Matrix

| Budget % | Action | Human Notification | Session State |
|----------|--------|-------------------|---------------|
| < 60% | Continue | None | OPERATIONAL |
| 60-80% | Continue + Log | Async digest | OPERATIONAL |
| 80-95% | Degrade | Immediate alert | DEGRADED |
| 95-100% | Suspend | Urgent notification | SUSPENDED |
| ≥ 100% | Terminate | Critical alert | TERMINATED |

---

## 🔄 ENTROPY RESET CONDITIONS

### Automatic Reset

Session entropy counter resets when:

1. **Explicit Human Checkpoint**
   ```python
   await init_anchor(mode="refresh", actor_id="888_JUDGE")
   # Resets budget, maintains session context
   ```

2. **Verdict SEAL with ΔS < -0.1**
   - Major clarity gain indicates "fresh start"
   - Resets 50% of budget (not full reset)

3. **24-Hour Session Boundary**
   - Daily automatic budget renewal
   - Preserves accumulated wisdom, resets drift

### Manual Reset (888_JUDGE only)

```python
await vault_ledger({
    'mode': 'seal',
    'evidence': 'Manual entropy reset authorized',
    'actor_id': '888_JUDGE',
    'payload': {
        'action': 'entropy_reset',
        'session_id': '<target_session>',
        'reason': '<justification>'
    }
})
```

---

## 📊 ENTROPY CALCULATION

### Per-Operation Calculation

```python
def calculate_delta_s(operation: Operation, context: Context) -> float:
    """
    Calculate entropy change for an operation.
    Returns ΔS (negative = clarity gain)
    """
    
    # Base entropy cost
    base_cost = OPERATION_COSTS.get(operation.type, 0.05)
    
    # Complexity multiplier
    complexity = len(operation.inputs) * 0.01
    
    # Uncertainty factor
    uncertainty = 1 - context.confidence  # Higher uncertainty = higher entropy
    
    # Ambiguity penalty (unresolved questions)
    ambiguity = context.unresolved_questions * 0.02
    
    # Contradiction penalty (conflicting information)
    contradiction = context.contradiction_count * 0.05
    
    # Calculate total
    delta_s = base_cost + complexity + (uncertainty * 0.1) + ambiguity + contradiction
    
    # Clarity reduction (negative entropy)
    if operation.organizes_information:
        delta_s -= 0.1 * operation.information_gain
    
    return round(delta_s, 3)
```

### Example Calculations

| Operation | Base | Complexity | Uncertainty | ΔS Result |
|-----------|------|------------|-------------|-----------|
| Simple file read | 0.02 | 0.01 | 0.00 | **0.03** |
| Multi-file grep | 0.05 | 0.03 | 0.02 | **0.10** |
| Complex reasoning | 0.10 | 0.05 | 0.05 | **0.20** |
| Information synthesis | 0.05 | 0.02 | -0.10 | **-0.03** ✅ |
| Contradiction resolution | 0.10 | 0.00 | -0.15 | **-0.05** ✅ |

---

## 🎛️ ENTROPY OPTIMIZATION GUIDELINES

### Reducing Entropy (Best Practices)

1. **Structured Outputs**
   - Use tables over prose
   - Enumerate options clearly
   - Quantify uncertainty

2. **Progressive Disclosure**
   - Start with summary
   - Detail on request
   - Avoid information overload

3. **Explicit Ambiguity**
   - State "I don't know" clearly
   - Provide confidence intervals
   - Distinguish fact from inference

4. **Conflict Resolution**
   - Acknowledge contradictions
   - Provide resolution criteria
   - Don't leave tensions unresolved

### Code Example: Low-Entropy Response

```python
# ❌ High Entropy (ΔS ≈ 0.15)
"""
I think maybe the answer is around 42, but I'm not entirely sure. 
There could be other factors. It depends on various things.
"""

# ✅ Low Entropy (ΔS ≈ 0.02)
"""
| Metric | Value | Confidence |
|--------|-------|------------|
| Answer | 42    | 0.85       |
| Range  | [40, 44] | Ω = 0.04 |

Assumptions:
- Input parameters within normal range
- No external interference

Uncertainty: ±2 units (estimate only)
"""
```

---

## 📋 COMPLIANCE CHECKLIST

For session implementers:

- [ ] Initialize session with entropy_budget field
- [ ] Calculate ΔS for every operation
- [ ] Accumulate ΣΔS in session state
- [ ] Check thresholds before each operation
- [ ] Return VOID_ENTROPY_BUDGET when exhausted
- [ ] Support checkpoint/refresh mode
- [ ] Log all entropy changes to audit trail
- [ ] Provide entropy metrics in every verdict

---

## 🔗 RELATED DOCUMENTS

- `000_CONSTITUTION.md` (F4 Clarity)
- `VERDICT_SCHEMA_STANDARD.md` (metrics.delta_s)
- `HUMILITY_SPEC.md` (Ω₀ interaction with ΔS)

---

*Ditempa Bukan Diberi* [ΔΩΨ|888] 🌡️
