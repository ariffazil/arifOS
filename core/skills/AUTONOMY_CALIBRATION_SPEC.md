# SKILL: Autonomy Calibration
> **Target Organ:** arifOS — `core/skills/autonomy_calibration.py`
> **Class:** OBSERVE + PROPOSE (never execute)
> **Forged:** 2026-06-14 by FORGE (000Ω)
> **Status:** SPEC

---

## PURPOSE

Periodically re-evaluate tool risk bands and autonomy ceilings (E7) based on observed false positives / false negatives. Proposes changes — never applies them.

---

## DATA MODEL

```python
class ToolRiskMetrics(BaseModel):
    tool_name: str
    action_class: str  # OBSERVE | DERIVE | MUTATE | ATOMIC
    current_band: str  # FULL_AUTO | APPROVE_ONLY | PROPOSE_ONLY | HUMAN_ONLY
    total_invocations: int
    hold_count: int
    override_count: int
    false_positive_count: int  # HOLD that was overridden and successful
    false_negative_count: int  # went through without HOLD but caused issues
    hold_rate: float           # holds / total
    override_rate: float       # overrides / holds
    fp_rate: float             # false_positives / holds
    fn_rate: float             # false_negatives / total_negative_events
    last_evaluated: datetime

class CalibrationProposal(BaseModel):
    tool_name: str
    current_band: str
    proposed_band: str
    direction: str  # TIGHTEN | LOOSEN | MAINTAIN
    evidence: str
    confidence: float
    recommended_action: str  # IMPLEMENT | REVIEW | DEFER
```

---

## CALIBRATION RULES

```python
CALIBRATION_RULES = {
    # If HOLD rate > 30% AND override rate > 20%: policy too strict → LOOSEN
    ("HOLD_RATE", ">", 0.30): lambda m: CalibrationProposal(
        direction="LOOSEN",
        proposed_band=loosen_band(m.current_band),
        evidence=f"HOLD rate {m.hold_rate:.1%} with {m.override_rate:.1%} override"
    ),
    
    # If false_negative_rate > 5%: policy too loose → TIGHTEN
    ("FN_RATE", ">", 0.05): lambda m: CalibrationProposal(
        direction="TIGHTEN",
        proposed_band=tighten_band(m.current_band),
        evidence=f"False negative rate {m.fn_rate:.1%} — dangerous calls slipping through"
    ),
    
    # If tool has NEVER been held in 100+ invocations: consider FULL_AUTO
    ("HOLD_RATE", "==", 0.0): lambda m: CalibrationProposal(
        direction="LOOSEN" if m.total_invocations > 100 else "MAINTAIN",
        proposed_band=loosen_band(m.current_band) if m.total_invocations > 100 else m.current_band,
        evidence=f"Zero HOLDs in {m.total_invocations} calls"
    ),
}

def tighten_band(current: str) -> str:
    BANDS = ["FULL_AUTO", "APPROVE_ONLY", "PROPOSE_ONLY", "HUMAN_ONLY"]
    idx = BANDS.index(current)
    return BANDS[min(idx + 1, len(BANDS) - 1)]

def loosen_band(current: str) -> str:
    BANDS = ["FULL_AUTO", "APPROVE_ONLY", "PROPOSE_ONLY", "HUMAN_ONLY"]
    idx = BANDS.index(current)
    return BANDS[max(idx - 1, 0)]
```

---

## INVOCATION

Weekly or on significant governance event volume:
```
1. Query VAULT999 + NATS for last 30 days of tool metrics
2. Compute ToolRiskMetrics per tool
3. Apply calibration rules
4. Generate CalibrationReport → route to Kernel Scribe or Arif
```

---

*SPEC forged: 2026-06-14. Implementation target: `/root/arifOS/core/skills/autonomy_calibration.py`*
