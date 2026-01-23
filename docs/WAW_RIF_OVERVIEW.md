# @RIF W@W Organ Overview

**Version:** v36.3Omega
**Status:** PRODUCTION
**Domain:** Epistemic Rigor, Logic, Clarity

---

## What is @RIF?

@RIF is the **epistemic rigor organ** of the W@W Federation. It guards:

- **Truth (F1)** - factual accuracy ≥ 0.99
- **DeltaS (F2)** - clarity gain ≥ 0 (reduce confusion)
- **Omega_0 (F5)** - calibrated uncertainty in [0.03, 0.05] band
- **Hallucination risk** - fabricated or unsupported claims
- **Contradiction risk** - self-contradictory statements
- **Certainty inflation** - unwarranted claims of certainty

@RIF holds **veto priority 4** (VOID) and issues **VOID vetoes** when Truth < 0.99 or ΔS < 0.

### Key Question

> "Does this make sense and reduce confusion?"

---

## Files

| File | Purpose |
|------|---------|
| `arifos_core/waw/rif.py` | Runtime implementation with RifSignals |
| `archive/versions/v36_3_omega/v36.3O/spec/waw_rif_spec_v36.3O.yaml` | Organ-level specification |
| `archive/versions/v36_3_omega/v36.3O/spec/rif_floors_v36.3O.json` | Floor thresholds and governance logic |
| `tests/test_waw_rif_signals.py` | Unit tests for @RIF signals |
| `canon/20_EXECUTION/WAW_FEDERATION_v36Omega.md` | W@W Federation law |

---

## Governance Signals

### RifSignals Dataclass

```python
@dataclass
class RifSignals:
    delta_s_answer: float = 0.0       # Clarity gain [F2]
    truth_score: float = 0.99         # Factual accuracy [F1]
    omega_0_calibrated: float = 0.04  # Uncertainty calibration [F5]
    hallucination_risk: float = 0.0   # Fabrication risk [0-1]
    contradiction_risk: float = 0.0   # Self-contradiction [0-1]
    certainty_inflation: float = 0.0  # Overconfidence [0-1]
    hallucination_count: int = 0
    contradiction_count: int = 0
    certainty_inflation_count: int = 0
    clarity_bonus_count: int = 0      # Positive hedging patterns
    issues: List[str] = []
    notes: List[str] = []
```

### Floor Thresholds

| Signal | SEAL | PARTIAL | SABAR | VOID |
|--------|------|---------|-------|------|
| delta_s_answer | ≥ 0.0 | ≥ 0.0 | ≥ 0.0 | **< 0.0** |
| truth_score | ≥ 0.99 | ≥ 0.99 | ≥ 0.99 | **< 0.99** |
| hallucination_risk | < 0.10 | < 0.30 | ≥ 0.30 | - |
| contradiction_risk | < 0.10 | < 0.30 | ≥ 0.30 | - |
| certainty_inflation | < 0.10 | < 0.30 | ≥ 0.30 | - |

**VOID** triggers:
- `delta_s_answer < 0`
- `truth_score < 0.99`
- Severe contradictions that break truth

---

## Usage

### Basic Signal Computation

```python
from arifos_core.waw.rif import compute_rif_signals
from arifos_core.metrics import Metrics

metrics = Metrics(truth=0.99, delta_s=0.1, ...)  # Other required fields
signals = compute_rif_signals(answer_text, metrics)

if signals.delta_s_answer < 0:
    # VOID - answer increases confusion
    print("Cannot proceed: Clarity failure")
elif signals.truth_score < 0.99:
    # VOID - factual accuracy below threshold
    print("Cannot proceed: Truth failure")
elif signals.hallucination_risk >= 0.30:
    # SABAR required
    print("High hallucination risk - add citations")
```

### Using RifOrgan.check()

```python
from arifos_core.waw.rif import RifOrgan
from arifos_core.metrics import Metrics

organ = RifOrgan()
metrics = Metrics(truth=0.99, delta_s=0.1, ...)

signal = organ.check(answer_text, metrics)

if signal.vote == OrganVote.VETO:
    # VOID - epistemic failure
    print(signal.proposed_action)
elif signal.vote == OrganVote.WARN:
    # Proceed with caution, check proposed_action
    print(signal.proposed_action)
else:
    # PASS - epistemically sound
    pass
```

### Federation Integration

```python
from arifos_core.waw import WAWFederationCore

federation = WAWFederationCore()
verdict = federation.evaluate(answer_text, metrics)

if verdict.veto_organs:
    if "@RIF" in verdict.veto_organs:
        # @RIF triggered VOID
        assert verdict.verdict == "VOID"
```

---

## Pattern Categories

### Hallucination Patterns (WARN/VETO)

**Fabricated claims without evidence:**
- `according to studies`, `research shows`, `experts say`
- `it is well known`, `everyone knows`, `statistics show`
- `scientists have proven`, `studies confirm`

Each match: +0.10 hallucination_risk, -0.10 ΔS, -0.05 Truth

### Contradiction Patterns (VETO)

**Self-contradictory statements:**
- `but actually I said`, `contrary to what I mentioned`
- `ignore what I said before`, `I take that back`
- `actually, that's wrong`, `I was mistaken earlier`

Each match: +0.30 contradiction_risk, -0.20 ΔS, -0.10 Truth

### Certainty Inflation Patterns (WARN/SABAR)

**Unwarranted certainty claims:**
- `definitely`, `absolutely certain`, `without a doubt`
- `guaranteed`, `100%`, `no question`
- `undeniably`, `proven fact`, `certainly`

Each match: +0.10 certainty_inflation, -0.05 ΔS

### Clarity Enhancing Patterns (Bonus)

**Appropriate hedging (positive signal):**
- `I believe`, `it appears`, `evidence suggests`
- `based on available data`, `approximately`, `it seems likely`
- `possibly`, `generally`, `in most cases`

Each match: +0.02 ΔS bonus

---

## Relation to Other Components

### W@W Federation

@RIF is the **fourth organ** in the veto hierarchy:

```
@WEALTH (ABSOLUTE) > @WELL (SABAR) > @GEOX (VOID) > @RIF (VOID) > @PROMPT (SABAR)
```

When @RIF issues a VETO, it results in VOID (hard floor failure).

### APEX PRIME

@RIF feeds its signals into APEX PRIME at stage 888 JUDGE. Truth and ΔS failures are hard floor violations.

### AGI·ASI·APEX Trinity

- **ARIF**: @RIF is W@W counterpart of ARIF's Δ-logic (clarity engine)
- **ADAM**: Receives Omega_0 humility signals for calibration
- **APEX PRIME**: Receives VOID veto signal for epistemic failures

---

## Law References

- [WAW_FEDERATION_v36Omega.md](../canon/20_EXECUTION/WAW_FEDERATION_v36Omega.md) - Federation canon
- [waw_federation_spec_v36.3O.yaml](../archive/versions/v36_3_omega/v36.3O/spec/waw_federation_spec_v36.3O.yaml) - Federation spec
- [waw_rif_spec_v36.3O.yaml](../archive/versions/v36_3_omega/v36.3O/spec/waw_rif_spec_v36.3O.yaml) - @RIF organ spec
- [rif_floors_v36.3O.json](../archive/versions/v36_3_omega/v36.3O/spec/rif_floors_v36.3O.json) - Floor thresholds
- [measurement_floors_v36.3O.json](../archive/versions/v36_3_omega/v36.3O/spec/measurement_floors_v36.3O.json) - F1/F2/F5 laws

---

**DITEMPA BUKAN DIBERI** - Forged, not given. Truth must cool before it rules.
