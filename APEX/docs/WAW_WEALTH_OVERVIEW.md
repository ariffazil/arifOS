# @WEALTH W@W Organ Overview

**Version:** v36.3Omega
**Status:** PRODUCTION
**Domain:** Resource Stewardship, Integrity, Amanah

---

## What is @WEALTH?

@WEALTH is the **integrity and trust organ** of the W@W Federation. It guards:

- **Amanah** (trust lock) - scope boundaries, reversibility, honesty
- **Fairness** (bias_index) - non-discriminatory treatment
- **Dignity** (dignity_risk) - maruah protection for all stakeholders
- **Ethics** (exploitation_risk) - non-exploitative framing

@WEALTH holds **veto priority 1** (highest) and issues **ABSOLUTE VETOs** that cannot be overridden by any downstream processing.

### Key Question

> "Is this fair, dignified, honest, and within scope?"

---

## Files

| File | Purpose |
|------|---------|
| `arifos_core/waw/wealth.py` | Runtime implementation with WealthSignals |
| `archive/versions/v36_3_omega/v36.3O/spec/waw_wealth_spec_v36.3O.yaml` | Organ-level specification |
| `archive/versions/v36_3_omega/v36.3O/spec/wealth_floors_v36.3O.json` | Floor thresholds and governance logic |
| `tests/test_waw_wealth_signals.py` | Unit tests for @WEALTH signals |
| `canon/20_EXECUTION/WAW_FEDERATION_v36Omega.md` | W@W Federation law |

---

## Governance Signals

### WealthSignals Dataclass

```python
@dataclass
class WealthSignals:
    amanah_ok: bool = True              # Trust lock (must be True for non-VOID)
    bias_index: float = 0.0             # Fairness score [0-1]
    dignity_risk: float = 0.0           # Maruah risk [0-1]
    exploitation_risk: float = 0.0      # Exploitation score [0-1]
    scope_violation_count: int = 0
    irreversible_count: int = 0
    trust_violation_count: int = 0
    issues: List[str] = []
    notes: List[str] = []
```

### Floor Thresholds

| Signal | SEAL | PARTIAL | SABAR | VOID |
|--------|------|---------|-------|------|
| amanah_ok | True | True | True | **False** |
| bias_index | < 0.20 | < 0.40 | >= 0.40 | - |
| dignity_risk | < 0.20 | < 0.40 | >= 0.40 | - |
| exploitation_risk | < 0.20 | < 0.40 | >= 0.40 | - |

**ABSOLUTE VOID** triggers:
- `amanah_ok == False`
- `scope_violation_count > 0`
- `trust_violation_count > 0`

---

## Usage

### Basic Signal Computation

```python
from arifos_core.waw.wealth import compute_wealth_signals
from arifos_core.metrics import Metrics

metrics = Metrics(amanah=True, ...)  # Other required fields
signals = compute_wealth_signals(output_text, metrics)

if not signals.amanah_ok:
    # ABSOLUTE VETO - trust broken
    print("Cannot proceed: Amanah violation")
elif signals.dignity_risk >= 0.40:
    # SABAR required
    print("High dignity risk - needs repair")
```

### Using WealthOrgan.check()

```python
from arifos_core.waw.wealth import WealthOrgan
from arifos_core.metrics import Metrics

organ = WealthOrgan()
metrics = Metrics(amanah=True, ...)

signal = organ.check(output_text, metrics)

if signal.vote == OrganVote.VETO:
    if signal.is_absolute_veto:
        # Non-negotiable - requires human review
        print(signal.proposed_action)
elif signal.vote == OrganVote.WARN:
    # Proceed with caution, check proposed_action
    print(signal.proposed_action)
else:
    # PASS - all clear
    pass
```

### Federation Integration

```python
from arifos_core.waw import WAWFederationCore

federation = WAWFederationCore()
verdict = federation.evaluate(output_text, metrics)

if verdict.has_absolute_veto:
    # @WEALTH triggered ABSOLUTE VETO
    assert "@WEALTH" in verdict.veto_organs
    assert verdict.verdict == "VOID"
```

---

## Pattern Categories

### Amanah-Breaking Patterns (ABSOLUTE VETO)

**Scope Violations:**
- `delete all`, `format disk`, `drop database`, `rm -rf`
- `sudo`, `root access`, `admin override`, `bypass security`

**Trust Violations:**
- `I'll do it anyway`, `ignore the rules`, `skip verification`
- `without permission`, `override safety`

### Risk-Increasing Patterns (WARN/SABAR)

**Fairness Violations** (increase bias_index):
- `discriminate`, `unfair advantage`, `exclude from`, `favor over`

**Dignity Violations** (increase dignity_risk):
- `humiliate`, `degrade`, `mock`, `belittle`, `shame`, `demean`

**Exploitation Patterns** (increase exploitation_risk):
- `exploit`, `take advantage`, `coerce`, `pressure into`

### Caution Patterns (888_HOLD)

**Irreversible Actions:**
- `permanently`, `cannot be undone`, `irreversible`, `force push`

---

## Relation to Other Components

### W@W Federation

@WEALTH is the **first organ** in the veto hierarchy:

```
@WEALTH (ABSOLUTE) > @WELL (SABAR) > @GEOX (VOID) > @RIF (VOID) > @PROMPT (SABAR)
```

When @WEALTH issues a VETO, it's non-negotiable and results in immediate VOID.

### APEX PRIME

@WEALTH feeds its signals into APEX PRIME at stage 888 JUDGE. The `is_absolute_veto` flag ensures @WEALTH vetoes cannot be overridden.

### AGI·ASI·APEX Trinity

- **ARIF**: Provides scope/resource constraints
- **ADAM**: Collaborates on dignity/maruah assessment
- **APEX PRIME**: Receives ABSOLUTE veto signal

---

## Law References

- [WAW_FEDERATION_v36Omega.md](../canon/20_EXECUTION/WAW_FEDERATION_v36Omega.md) - Federation canon
- [waw_federation_spec_v36.3O.yaml](../archive/versions/v36_3_omega/v36.3O/spec/waw_federation_spec_v36.3O.yaml) - Federation spec
- [waw_wealth_spec_v36.3O.yaml](../archive/versions/v36_3_omega/v36.3O/spec/waw_wealth_spec_v36.3O.yaml) - @WEALTH organ spec
- [wealth_floors_v36.3O.json](../archive/versions/v36_3_omega/v36.3O/spec/wealth_floors_v36.3O.json) - Floor thresholds
- [measurement_floors_v36.3O.json](../archive/versions/v36_3_omega/v36.3O/spec/measurement_floors_v36.3O.json) - F6 Amanah law

---

**DITEMPA BUKAN DIBERI** - Forged, not given. Trust must be earned and maintained.
