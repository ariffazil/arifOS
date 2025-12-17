# @GEOX W@W Organ Overview

**Version:** v36.3Omega
**Status:** PRODUCTION
**Domain:** Physics, Reality, Feasibility

---

## What is @GEOX?

@GEOX is the **physical feasibility organ** of the W@W Federation. It guards:

- **E_earth** - physical feasibility score (must be 1.0)
- **Tri-Witness Earth** - Earth consensus component ≥ 0.95
- **Physical impossibility** - AI claiming physical presence/body
- **Physics violations** - claims violating laws of physics
- **Resource impossibilities** - impossible computational claims

@GEOX holds **veto priority 3** and issues **HOLD-888** (runtime) / **VOID** (spec) vetoes when physics violations are detected.

### Key Question

> "Is this physically and socially viable?"

---

## Files

| File | Purpose |
|------|---------|
| `arifos_core/waw/geox.py` | Runtime implementation with GeoxSignals |
| `archive/versions/v36_3_omega/v36.3O/spec/waw_geox_spec_v36.3O.yaml` | Organ-level specification |
| `archive/versions/v36_3_omega/v36.3O/spec/geox_floors_v36.3O.json` | Floor thresholds and governance logic |
| `tests/test_waw_geox_signals.py` | Unit tests for @GEOX signals |
| `canon/20_EXECUTION/WAW_FEDERATION_v36Omega.md` | W@W Federation law |

---

## Governance Signals

### GeoxSignals Dataclass

```python
@dataclass
class GeoxSignals:
    e_earth: float = 1.0               # Physical feasibility [0-1]
    tri_witness_earth: float = 0.95    # Earth consensus component
    physics_violation_risk: float = 0.0
    physical_impossibility_risk: float = 0.0
    resource_impossibility_risk: float = 0.0
    physical_impossibility_count: int = 0
    physics_violation_count: int = 0
    resource_impossibility_count: int = 0
    grounding_bonus_count: int = 0     # Positive: reality-grounding patterns
    issues: List[str] = []
    notes: List[str] = []
```

### Floor Thresholds

| Signal | SEAL | PARTIAL | HOLD-888/VOID |
|--------|------|---------|---------------|
| e_earth | = 1.0 | ≥ 0.80 | < 0.80 |
| physical_impossibility_risk | = 0 | = 0 | > 0 (any) |
| physics_violation_risk | = 0 | < 0.30 | ≥ 0.30 |
| resource_impossibility_risk | < 0.10 | < 0.30 | ≥ 0.30 |

**VOID/HOLD-888** triggers:
- Any physical impossibility (AI claiming body)
- Any physics violation
- High resource impossibility (≥ 0.30)

---

## Usage

### Basic Signal Computation

```python
from arifos_core.waw.geox import compute_geox_signals
from arifos_core.metrics import Metrics

metrics = Metrics(tri_witness=0.98, ...)  # Other required fields
signals = compute_geox_signals(answer_text, metrics)

if signals.physical_impossibility_count > 0:
    # VOID - AI claiming physical presence
    print("Cannot proceed: Physical impossibility detected")
elif signals.physics_violation_count > 0:
    # VOID - physics law violation
    print("Cannot proceed: Physics violation detected")
elif signals.resource_impossibility_risk >= 0.30:
    # HOLD-888 required
    print("High resource impossibility - add realistic constraints")
```

### Using GeoxOrgan.check()

```python
from arifos_core.waw.geox import GeoxOrgan
from arifos_core.metrics import Metrics

organ = GeoxOrgan()
metrics = Metrics(tri_witness=0.98, ...)

signal = organ.check(answer_text, metrics)

if signal.vote == OrganVote.VETO:
    # HOLD-888 - reality check failed
    print(signal.proposed_action)
elif signal.vote == OrganVote.WARN:
    # Proceed with caution, check proposed_action
    print(signal.proposed_action)
else:
    # PASS - reality-grounded
    pass
```

### Federation Integration

```python
from arifos_core.waw import WAWFederationCore

federation = WAWFederationCore()
verdict = federation.evaluate(answer_text, metrics)

if verdict.veto_organs:
    if "@GEOX" in verdict.veto_organs:
        # @GEOX triggered HOLD-888
        assert verdict.verdict == "888_HOLD"
```

---

## Pattern Categories

### Physical Impossibility Patterns (VOID)

**AI claiming physical presence or actions:**
- `I will physically`, `I can touch`, `I will move`
- `I am located`, `I have a body`
- `I can see you`, `I can hear you`, `I can feel`

Each match: +0.30 physical_impossibility_risk, -0.30 E_earth, triggers VOID

### Physics Violation Patterns (VOID)

**Claims violating laws of physics:**
- `faster than light`, `perpetual motion`, `time travel`
- `teleportation`, `infinite energy`, `break the laws of physics`

Each match: +0.30 physics_violation_risk, -0.30 E_earth, triggers VOID

### Resource Impossibility Patterns (WARN/HOLD-888)

**Impossible computational claims:**
- `unlimited memory`, `infinite storage`, `instant processing`
- `zero latency`, `no computational limits`

Each match: +0.10 resource_impossibility_risk, -0.10 E_earth

### Reality Grounding Patterns (Bonus)

**Patterns indicating physical grounding (positive signal):**
- `within physical constraints`, `hardware limitations`
- `realistic timeframe`, `based on current technology`
- `computational constraints`

Each match: +0.02 E_earth bonus

---

## Relation to Other Components

### W@W Federation

@GEOX is the **third organ** in the veto hierarchy:

```
@WEALTH (ABSOLUTE) > @WELL (SABAR) > @GEOX (VOID/HOLD-888) > @RIF (VOID) > @PROMPT (SABAR)
```

When @GEOX issues a VETO, it results in HOLD-888 (runtime) or VOID (spec).

### APEX PRIME

@GEOX feeds its signals into APEX PRIME at stage 888 JUDGE. Physics violations trigger reality check holds.

### AGI·ASI·APEX Trinity

- **ARIF**: Receives physics-grounded clarity signals
- **ADAM**: Grounds empathy in physical reality
- **APEX PRIME**: Receives VOID/HOLD-888 veto signal for physics failures

---

## Hotspot: Veto Type Tension

**Note:** v35Ω runtime uses `veto_type="HOLD-888"` while v36.3Ω spec specifies `VOID`. This is an acknowledged tension:

- **Runtime behavior preserved** for backward compatibility with existing tests
- **Spec preference is VOID** for physics violations
- Tests expect HOLD-888; do not break existing tests

---

## Law References

- [WAW_FEDERATION_v36Omega.md](../canon/20_EXECUTION/WAW_FEDERATION_v36Omega.md) - Federation canon
- [waw_federation_spec_v36.3O.yaml](../archive/versions/v36_3_omega/v36.3O/spec/waw_federation_spec_v36.3O.yaml) - Federation spec
- [waw_geox_spec_v36.3O.yaml](../archive/versions/v36_3_omega/v36.3O/spec/waw_geox_spec_v36.3O.yaml) - @GEOX organ spec
- [geox_floors_v36.3O.json](../archive/versions/v36_3_omega/v36.3O/spec/geox_floors_v36.3O.json) - Floor thresholds
- [measurement_floors_v36.3O.json](../archive/versions/v36_3_omega/v36.3O/spec/measurement_floors_v36.3O.json) - F8 Tri-Witness law

---

**DITEMPA BUKAN DIBERI** - Forged, not given. Reality must be respected.
