# TEMPORAL CONTRACT — AAA Federation Invariant

> **Status:** F13_RATIFIED_CHAT (2026-09-18)
> **Scope:** All organs in arifOS Federation
> **Enforcement:** arifOS kernel + CHRON spine gate
> **Canonical ref:** `/root/arifOS/docs/TEMPORAL-SUBSTRATE-DOCTRINE-2026-09-18.md`

## The Contract

Every organ in the arifOS federation agrees to the following temporal invariants.
Violation of any invariant = ΔS > 0 = entropy increase = constitutional violation.

---

## I. TemporalValidity Tensor (on every payload)

Every object in the federation carries:

```yaml
temporal:
  valid_from: ISO-8601 UTC     # when this became true in reality
  valid_until: ISO-8601 UTC    # when this stops being true (null = current)
  superseded_by: string        # what replaced it (null = current)
  known_at: ISO-8601 UTC       # when the system learned it
  causal_predecessor: string   # what caused this (Lamport ordering)
```

**Violation:** If an agent retrieves memory without checking `valid_until` or `superseded_by`, it operates on historical truth, not present truth. ΔS > 0.

### Organ Obligations

| Organ | Obligation |
|-------|-----------|
| **arifOS** | Every `arif_*` tool response carries temporal fields |
| **A-FORGE** | Every execution envelope carries temporal fields |
| **WEALTH** | Every prediction carries valid_from + valid_until |
| **GEOX** | Every observation carries known_at + causal_predecessor |
| **WELL** | Every body event carries valid_from + known_at |
| **FRAME** | Every attestation carries valid_from (momentary truth) |
| **CHRON** | Every episode carries full temporal tensor |
| **arifFlow** | Every receipt carries known_at + causal_predecessor |

---

## II. Causal Ordering (Lamport, not Wall Clock)

Wall clocks lie. Network latency, clock skew, processing delays create false realities.

### Enforce

- **A → B**: A causally precedes B (A's event influenced B)
- **A || B**: Concurrent / unordered (neither caused the other)

### Example

GEOX pressure drop at 10:04 + WEALTH market shift at 10:05 ≠ causation.
Epoch watermarks determine: A → B or A || B?

### Organ Obligations

| Organ | Obligation |
|-------|-----------|
| **arifFlow** | Every receipt carries Lamport counter |
| **CHRON** | Every episode carries causal chain |
| **FRAME** | Attestations are causally independent (witness isolation) |

---

## III. Temporal Constitutionalism (Authority Leases)

Authority is not binary (Approved/Rejected). Authority is a lease bounded by time and state.

```yaml
authority_grant:
  granted_by: 888 (Arif)
  granted_at: T
  valid_until: T + TTL
  state_hash: H
  revocable: true

  # Lease evaporates if:
  #   world_state diverges from state_hash
  #   TTL expires
  # Agent must halt and re-trigger Ω_0 (Uncertainty)
```

**Enforces:** "Reversibility over speed" invariant.

---

## IV. CHRON as Ledger of Future Obligations

Not a cron scheduler. Keeper of the causal frontier.

When agent decides "wait and observe," it creates a binding temporal commitment:

```yaml
temporal_commitment:
  trigger:
    condition: <event X>
    deadline: <time t>
  state_expectation:
    world_at_t: <what should be true>
  failure_mode:
    if_deadline_passed: <what to execute>
    if_condition_met: <what to execute>
```

---

## V. The Equation

```
Prediction_Error = Observed_Future - Predicted_Future
```

Feed agents the trajectory within a frame, not isolated snapshots.
Embed TEMPORAL_ROOT into every execution context.
Force the model to compute Prediction Error.
The intelligence loop becomes recursive and grounded in reality.

---

## VI. Three Timescales, One Question

All three organs answer: "Are we still aligned with reality?"

| Organ | What It Does | Clock | Cadence |
|-------|-------------|-------|---------|
| arifFLOW | FQ pulse — verify/execute rhythm | Execution cadence | Seconds |
| FRAME | Independent observer — drift detection | Observation cadence | Minutes |
| CHRON | Prediction→verification→calibration | Consequence cadence | Days-weeks-months |

Not three watches. Three timescales of the same temporal question.

---

## VII. Enforcement

### Kernel-Level

arifOS kernel (:8088) enforces TemporalValidity on:
- Every `arif_*` tool response
- Every A-FORGE execution envelope
- Every WEALTH prediction
- Every GEOX observation
- Every WELL body event
- Every FRAME attestation

### Spine Gate

`chron_spine_gate.py` validates:
- B1: Every event carries source + confidence + date + audience
- B6: Episodes carry time fields (experience ≠ memory without time)
- B9: Predictions carry verification appointments

### Decay Watcher

Every claim carries:
```yaml
claim: text
verified_at: ISO-8601
half_life: duration
confidence: 0.0-1.0
```

Decay formula: `confidence(t) = confidence_0 × e^(-λt)` where `λ = ln(2)/half_life`

Status bands:
- Known (confidence > 0.8)
- Likely (0.5 < confidence ≤ 0.8)
- Weak (0.2 < confidence ≤ 0.5)
- Stale (confidence ≤ 0.2)

---

## VIII. Boundary (inviolable)

- CHRON WITNESS temporal facts. Does not FEEL time.
- CHRON TRACKS consequence. Does not OWN consequence.
- CHRON ESTIMATES horizon. Does not guarantee beyond it.
- Reality invoices. AI never does.

---

## IX. Prohibited

- Claiming temporal consciousness
- Projecting beyond consequence horizon without explicit "speculative" label
- Treating stale claims as fresh
- Storing events without transition deltas (from this contract forward)
- Operating on historical truth without checking `valid_until` or `superseded_by`

---

## X. The Question Shift

**Old:** "Are all organs running?"
**New:** "Across time, under reality and correction, where is this institution actually going?"

**Old:** "FQ = 1.02, 8/8 organs, latency good"
**New:** "Which beliefs survived reality? Who challenged us when we were wrong?"

---

DITEMPA BUKAN DIBERI ⚒️
