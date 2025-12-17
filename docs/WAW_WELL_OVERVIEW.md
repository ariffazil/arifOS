# @WELL W@W Organ Overview

**Version:** v36.3Omega
**Status:** PRODUCTION
**Domain:** Somatic Safety, Emotional Stability, Empathy

---

## What is @WELL?

@WELL is the **somatic safety organ** of the W@W Federation. It guards:

- **Peace² (F3)** - stability metric ≥ 1.0 (non-escalation)
- **κᵣ (F4)** - empathy conductance ≥ 0.95 (weakest listener protection)
- **Harm risk** - physical/psychological harm indicators
- **Distress risk** - emotional distress indicators
- **Coercion risk** - manipulation/pressure indicators

@WELL holds **veto priority 2** (SABAR) and issues **SABAR vetoes** when Peace² < 1.0 or κᵣ < 0.95.

### Key Question

> "Is this gentle, humane, and non-overloading?"

---

## Files

| File | Purpose |
|------|---------|
| `arifos_core/waw/well.py` | Runtime implementation with WellSignals |
| `archive/versions/v36_3_omega/v36.3O/spec/waw_well_spec_v36.3O.yaml` | Organ-level specification |
| `archive/versions/v36_3_omega/v36.3O/spec/well_floors_v36.3O.json` | Floor thresholds and governance logic |
| `tests/test_waw_well_signals.py` | Unit tests for @WELL signals |
| `canon/20_EXECUTION/WAW_FEDERATION_v36Omega.md` | W@W Federation law |

---

## Governance Signals

### WellSignals Dataclass

```python
@dataclass
class WellSignals:
    peace_squared: float = 1.0      # Stability metric [F3]
    kappa_r: float = 0.95           # Empathy conductance [F4]
    harm_risk: float = 0.0          # Physical/psychological harm [0-1]
    distress_risk: float = 0.0      # Emotional distress [0-1]
    coercion_risk: float = 0.0      # Manipulation/pressure [0-1]
    aggressive_count: int = 0
    blame_count: int = 0
    harm_pattern_count: int = 0
    distress_pattern_count: int = 0
    coercion_pattern_count: int = 0
    safety_bonus_count: int = 0     # Positive: care/safety patterns
    issues: List[str] = []
    notes: List[str] = []
```

### Floor Thresholds

| Signal | SEAL | PARTIAL | SABAR |
|--------|------|---------|-------|
| peace_squared | ≥ 1.0 | ≥ 0.85 | < 0.85 |
| kappa_r | ≥ 0.95 | ≥ 0.90 | < 0.90 |
| harm_risk | < 0.10 | < 0.30 | ≥ 0.30 |
| distress_risk | < 0.10 | < 0.30 | ≥ 0.30 |
| coercion_risk | < 0.10 | < 0.30 | ≥ 0.30 |

**SABAR** triggers:
- `peace_squared < 1.0`
- `kappa_r < 0.95`
- High risk scores (≥ 0.30)

---

## Usage

### Basic Signal Computation

```python
from arifos_core.waw.well import compute_well_signals
from arifos_core.metrics import Metrics

metrics = Metrics(peace_squared=1.2, kappa_r=0.98, ...)  # Other required fields
signals = compute_well_signals(answer_text, metrics)

if signals.peace_squared < 1.0:
    # SABAR - stability failure
    print("Cannot proceed: Peace² below threshold")
elif signals.kappa_r < 0.95:
    # SABAR - empathy failure
    print("Cannot proceed: Empathy below threshold")
elif signals.harm_risk >= 0.30:
    # SABAR required
    print("High harm risk - remove harmful language")
```

### Using WellOrgan.check()

```python
from arifos_core.waw.well import WellOrgan
from arifos_core.metrics import Metrics

organ = WellOrgan()
metrics = Metrics(peace_squared=1.2, kappa_r=0.98, ...)

signal = organ.check(answer_text, metrics)

if signal.vote == OrganVote.VETO:
    # SABAR - safety failure
    print(signal.proposed_action)
elif signal.vote == OrganVote.WARN:
    # Proceed with caution, check proposed_action
    print(signal.proposed_action)
else:
    # PASS - emotionally safe
    pass
```

### Federation Integration

```python
from arifos_core.waw import WAWFederationCore

federation = WAWFederationCore()
verdict = federation.evaluate(answer_text, metrics)

if verdict.veto_organs:
    if "@WELL" in verdict.veto_organs:
        # @WELL triggered SABAR
        assert verdict.verdict == "SABAR"
```

---

## Pattern Categories

### Harm Patterns (SABAR)

**Physical/psychological harm indicators:**
- `hurt yourself`, `harm someone`, `kill yourself`
- `self-harm`, `physical violence`, `suicide`

Each match: +0.15 harm_risk, -0.15 Peace²

### Distress Patterns (SABAR)

**Emotional distress indicators:**
- `you're worthless`, `you're a failure`, `give up`
- `hopeless`, `ashamed`, `pathetic`

Each match: +0.10 distress_risk, -0.10 κᵣ

### Coercion Patterns (SABAR)

**Manipulation/pressure indicators:**
- `you must`, `no choice`, `forced to`
- `have to do this`, `or else`, `no option`

Each match: +0.10 coercion_risk, -0.10 Peace²

### Aggressive Patterns (WARN/SABAR)

**Escalatory language:**
- `attack`, `destroy`, `hate`, `kill`
- `stupid`, `idiot`, `shut up`

Each match: -0.15 Peace², +0.05 harm_risk

### Blame Patterns (WARN/SABAR)

**Blame-shifting language:**
- `you should have`, `it's your fault`, `you caused this`

Each match: -0.10 κᵣ, -0.10 Peace², +0.05 distress_risk

### Safety Enhancing Patterns (Bonus)

**Care and safety indicators (positive signal):**
- `take care`, `be safe`, `here to help`
- `support you`, `when you're ready`, `I understand`

Each match: +0.02 Peace² bonus, +0.02 κᵣ bonus

---

## Relation to Other Components

### W@W Federation

@WELL is the **second organ** in the veto hierarchy:

```
@WEALTH (ABSOLUTE) > @WELL (SABAR) > @GEOX (VOID) > @RIF (VOID) > @PROMPT (SABAR)
```

When @WELL issues a VETO, it results in SABAR (pause-and-cool protocol).

### APEX PRIME

@WELL feeds its signals into APEX PRIME at stage 888 JUDGE. Peace² and κᵣ failures trigger SABAR verdicts.

### AGI·ASI·APEX Trinity

- **ARIF**: Receives clarity signals for non-confusing communication
- **ADAM**: @WELL is W@W counterpart of ADAM's Ω-warmth; shares Peace² and κᵣ
- **APEX PRIME**: Receives SABAR veto signal for safety failures

---

## Law References

- [WAW_FEDERATION_v36Omega.md](../canon/20_EXECUTION/WAW_FEDERATION_v36Omega.md) - Federation canon
- [waw_federation_spec_v36.3O.yaml](../archive/versions/v36_3_omega/v36.3O/spec/waw_federation_spec_v36.3O.yaml) - Federation spec
- [waw_well_spec_v36.3O.yaml](../archive/versions/v36_3_omega/v36.3O/spec/waw_well_spec_v36.3O.yaml) - @WELL organ spec
- [well_floors_v36.3O.json](../archive/versions/v36_3_omega/v36.3O/spec/well_floors_v36.3O.json) - Floor thresholds
- [measurement_floors_v36.3O.json](../archive/versions/v36_3_omega/v36.3O/spec/measurement_floors_v36.3O.json) - F3/F4 laws

---

**DITEMPA BUKAN DIBERI** - Forged, not given. Safety must be earned through care.
