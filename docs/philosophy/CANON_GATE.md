# CANON_GATE — arifOS Federation | Semantic Garbage Collection & Term Admission

To prevent **semantic overgrowth** and **abstraction bloat** (where arifOS becomes too good at naming things instead of changing reality), all canonical vocabulary must pass the `CANON_GATE` admission process and is subject to `CANON_GARBAGE_COLLECTION`.

---

## 1. The Term Admission Gate (CANON_GATE)

No new arifOS term enters the canonical vocabulary unless it passes all 5 of the following tests:

1. **Real Operational Distinction**: It names a distinction that physically or systemically exists in reality.
2. **Behavior or Routing Impact**: It changes routing, execution, or agent behavior.
3. **Non-redundancy**: It cannot be replaced or represented by an existing canonical term.
4. **Declared Failure Mode**: The term must have a clear failure state (what happens when this condition is degraded or breached?).
5. **Anti-mix Boundary**: It must have explicit boundaries defining what it is NOT (e.g. `RETAK` is not `BANGANG`).

### Required Declaration Form

Every proposed canonical term must declare:

```yaml
term: <NAME>
layer: SUBSTRATE | CONSTITUTION | COGNITION
meaning: <prose definition>
owner: <agent/organ/role responsible>
behavior_impact: <exact routing, execution, or judgment change>
anti_mix_boundary: <what this term must never be mixed with>
review_date: <expiry or scheduled pruning review date>
```

---

## 2. Canonical Garbage Collection (CANON_GARBAGE_COLLECTION)

To keep the kernel like a bonsai (disciplined, cut often, rooted in reality), a routine garbage collection scan is enforced:

* **Rule**: Any term that does not actively route a call, boundary an action, diagnose a failure, gate an execution, or index an audit log is **demoted to metaphor**.
* **Pruning Invariant**: *A kernel should have fewer sacred words than tools. A verdict should be rarer than a log.*

---

## 3. The Core Admissibility Map

| Term | Status | Operational/Behavioral Impact |
| --- | --- | --- |
| **BANGANG** | `CANON` | Diagnoses cognition failure; halts execution if confidence is ungrounded. |
| **BIJAK** | `CANON` | Marks useful-but-not-governed intelligence; prevents auto-SEAL. |
| **BIJAKSANA** | `CANON` | Marks governed wisdom; required for sovereign execution path. |
| **RETAK** | `CANON` | Diagnoses degraded substrate/machine state; triggers fail-closed recovery. |
| **Quantum/Cautious Eureka** | `METAPHOR` | Demoted. Does not affect routing or execution parameters. |
