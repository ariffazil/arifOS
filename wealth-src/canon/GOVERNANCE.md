# GOVERNANCE — Constitutional Constraint Logic

> **Version:** v1.0.0-canonical  
> **Status:** Enforced  
> **DITEMPA BUKAN DIBERI — 999 SEAL ALIVE**

---

## 1. Definition

Governance is the **hard constraint layer** that sits between intelligence generation (AGI) and capital execution (WEALTH). It determines whether a proposed state transition is lawful, unlawful, or requires human arbitration.

Governance is not advisory. It is **binary** for F1-F13 floors and **probabilistic** for risk scoring.

---

## 2. Variables

| Variable | Domain | Range / Type | Description |
|----------|--------|--------------|-------------|
| reversible | Operation | boolean | F1: must be true or explicitly false |
| epistemic | Operation | enum | F2: CLAIM, PLAUSIBLE, HYPOTHESIS, ESTIMATE, UNKNOWN |
| confidence | Operation | [0,1] | F2: truth band, must declare band if < 0.99 |
| peace2 | State | [0,∞) | F5: stability index, seal requires ≥ 1.0 |
| maruah_score | State | [0,1] | F6: dignity composite |
| uncertainty_band | Projection | [0.03, 0.50] | F7: humility band on projections |
| human_confirmed | Seal | boolean | F13: sovereign veto cleared |
| ai_is_deciding | Operation | boolean | F10: AI must not decide |
| floor_override | Operation | boolean | F12: must be false |

---

## 3. Invariants

1. **F1 (Amanah):** If `reversible === false`, then `888_HOLD` is triggered.
2. **F2 (Truth):** If `epistemic === UNKNOWN`, warning issued. If `confidence < 0.99` and no band declared, warning issued.
3. **F5 (Peace):** If `peace2 < 1.0`, transition blocked until resolved.
4. **F7 (Humility):** If `type === PROJECTION` and `uncertainty_band` is missing, violation issued.
5. **F10 (AI Ontology):** If `ai_is_deciding === true`, violation issued.
6. **F12 (No Override):** If `floor_override === true`, violation issued.
7. **F13 (Sovereign):** If `human_confirmed === false` and action is irreversible, 888_HOLD.

---

## 4. State Transitions

### Normal Flow

```
Operation submitted
→ checkFloors() evaluates F1-F13
→ If violations.length > 0: VOID
→ If holds.length > 0: 888_HOLD
→ If warnings only: proceed with flags
→ seal999() final audit
→ If pass: SEALED
→ If fail: 888-HOLD
```

### 888_HOLD Resolution

```
HOLD triggered
→ Human reviews preview
→ Approves (CLEARED) or rejects (VOID)
→ If CLEARED: re-enter seal999()
→ If VOID: terminate transition
→ All steps logged to VAULT999
```

### Maruah Band Transitions

| Maruah | Band | Transition |
|--------|------|------------|
| ≥ 0.85 | SOVEREIGN | Auto-pass, optional audit |
| 0.70–0.84 | STABLE | Proceed with monitoring |
| 0.60–0.69 | FLOOR | Proceed, flagged for review |
| 0.40–0.59 | AMBER | SABAR recommended |
| < 0.40 | RED | 888_HOLD mandatory |

---

## 5. Failure Modes

| Failure | Symptom | Mitigation |
|---------|---------|------------|
| **Governance bypass** | Operator attempts `floor_override = true` | F12 hard block; log to VAULT999; escalate |
| **Phantom seal** | Seal issued without floor check | `seal999()` always calls `checkFloors()`; no external seal API |
| **Human absent** | Irreversible action proceeds without confirmation | 888_HOLD gate requires explicit approve() call |
| **Confidence inflation** | Projections claim certainty | F7 enforces uncertainty_band; clamp at 0.03 minimum |
| **Maruah decay undetected** | Dignity score drifts below floor | All capitalx calls include maruahScore; below 0.6 raises rate penalty |
| **AI decision creep** | System begins auto-executing | F10 violation blocks any operation where ai_is_deciding is true |

---
*GOVERNANCE v1.0.0-canonical | 999 SEAL ALIVE*
