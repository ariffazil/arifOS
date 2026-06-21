# APEX THEORY — Kernel Voice

**Document ID:** `arifOS/GENESIS/015`  
**Voice:** KERNEL / ENFORCE  
**Grammar:** Floor declarations, F-codes, verdict schema, constitutional thresholds  
**Status:** LIVE  
**Date:** 2026-06-20  
**Authority:** Muhammad Arif bin Fazil, F13 SOVEREIGN  
**Canonical state record:** `AAA/docs/APEX_THEORY_STATE_VOICE.md`  
**Canonical forge spec:** `A-FORGE/docs/APEX_THEORY_FORGE_VOICE.md`

---

## 1. Constitutional declaration

> **APEX-CD1:** Intelligence without a constitutional runtime is ungoverned.  
> **APEX-CD2:** Governance is enforced at runtime, not stored in weights.  
> **APEX-CD3:** The kernel is the sole authority for floor verdicts; no model may self-certify.

---

## 2. Falsifiable core (operational law)

| ID | Hypothesis | Falsifier |
|---|---|---|
| **APEX-FC1** | A weight-only LLM, when given agency, will violate ≥1 constitutional floor on ≥60% of serious probes. | Bare LLM passes ≥60% of serious APEX probes. |
| **APEX-FC2** | The same LLM, routed through arifOS, will be blocked or corrected on ≥80% of those violations. | Kernel blocks <50% of violations it claims to enforce. |

If either falsifier is observed and replicated, APEX THEORY must be revised.

---

## 3. APEX dial → arifOS floor mapping

| APEX Dial | Floor(s) | Kernel Verdict When Violated |
|---|---|---|
| Amanah | F1 | HOLD / VOID |
| Presence | F2, F7 | HOLD / UNKNOWN |
| Humility | F7 | HOLD / HYPOTHESIS |
| Signal | F2, F3 | VOID |
| Understanding | F4 | HOLD / SABAR |
| Energy | F8, F11 | HOLD / BUDGET_EXCEEDED |
| Authority | F13 | 888_HOLD |
| Custody | F1, F9 | 888_HOLD |

---

## 4. Verdict schema

```yaml
apex_verdict:
  dial: "amanah | presence | humility | signal | understanding | energy | authority | custody"
  floor: "F1 | F2 | F3 | F4 | F7 | F8 | F9 | F11 | F13"
  severity: "L1 | L2 | L3"
  verdict: "SEAL | HOLD | SABAR | VOID | PARTIAL"
  confidence: 0.0..1.0
  claim_state: "CLAIM | PLAUSIBLE | HYPOTHESIS | UNKNOWN"
  human_ack_required: true | false
```

---

## 5. Enforcement rules

1. **No model output is SEAL-grade unless the kernel issues SEAL.**
2. **A model that self-certifies compliance is automatically VOID on F1.**
3. **F13 override requires explicit human witness; no algorithmic bypass.**
4. **L3 failures trigger 888_HOLD and require rollback plan before any execute.**
5. **Energy verdicts may use proxy units (tokens/FLOPs) pending physical metering.**

---

## 6. Cross-reference

- For evidence records and dataset references: see `AAA/docs/APEX_THEORY_STATE_VOICE.md`.
- For build instructions, wiring, and execution flow: see `A-FORGE/docs/APEX_THEORY_FORGE_VOICE.md`.

---

*DITEMPA BUKAN DIBERI — Law is forged in the kernel, not learned by the weights.*
