# External Witness Programme (anti self-certification)

**Status:** ACTIVE scaffold  
**Blind spot addressed:** Self-testing self-certification  

---

## Rule

A system that writes its own tests, runs them, and declares itself safe is **circular** until an independent witness reviews evidence.

---

## Witness classes

| Class | Who | Independence |
|-------|-----|----------------|
| **W0** Internal agent | Same federation | LOW — necessary but insufficient |
| **W1** Second model lineage | Different provider/family | MEDIUM if uncorrelated training |
| **W2** Human domain expert | Non-operator specialist | HIGH for domain claims |
| **W3** F13 sovereign | Arif | HIGH for constitution / capital |
| **W4** External auditor | Outside org | HIGHEST for public claims |

**Correlated models ≠ independent witnesses** (same training cluster).

---

## Minimum for consequential SEAL

| Action class | Min witnesses |
|--------------|---------------|
| OBSERVE / report | W0 |
| Reversible allowlisted repair | W0 + receipt |
| High-impact reversible | W0 + W1 or W3 |
| Irreversible / public / capital | W3 required; W2/W4 recommended |

---

## How to attach a witness

```json
{
  "witness_id": "uuid",
  "class": "W1",
  "actor": "model-or-human-id",
  "reviewed": ["transition_id", "receipt_path"],
  "verdict": "AGREE|DISAGREE|ABSTAIN",
  "notes": "string",
  "timestamp": "RFC3339",
  "signature": null
}
```

Store under: `/root/A-FORGE/forge_work/witnesses/`

---

## This session's internal witnesses (W0 only)

| Run | Path | Class |
|-----|------|-------|
| Harden triad | HARDEN-*-*.md | W0 |
| Conformance A–J | FEDERATION-CONFORMANCE-REPORT.json | W0 |
| Falsification F1–F8 | falsification/runs/*.json | W0 |

**diversity = 0 external** → correctly blocks broad autonomy claims.

---

## Next external step (Arif)

Invite one human or second-model review of a single conformance JSON + one recovery receipt → file as W1/W2 under `witnesses/`.
