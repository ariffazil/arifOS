# 000–999 Canonical Mapping

**Scope:** constitutional lifecycle geometry  
**Authority:** F13 SOVEREIGN — Muhammad Arif bin Fazil  
**SEAL:** DITEMPA BUKAN DIBERI — Forged, Not Given  
**Related files:**
- `arifosmcp/kernel/metabolic_loop.py` — 5-stage metabolic execution pump
- `tests/e2e/test_000_to_999_flow.py` — full-pipeline integration test
- `docs/APEX_THEORY_v2026.05.26.md` — historical framing (see note below)

---

## 1. Two Valid Schemes, One Geometry

The arifOS Federation operates two explicitly-named views of the same constitutional physics:

1. **11-stage constitutional pipeline** — the full paradox-resolution lifecycle, used when every stage must be witnessed, deliberated, and sealed.
2. **5-stage metabolic loop** — the same lifecycle compressed into an execution pump that fits inside the arifOS kernel runtime (`arifosmcp/kernel/metabolic_loop.py`).

They are not competing taxonomies. The 5-stage loop is the 11-stage pipeline at coarser resolution, exactly as a protein fold is the same molecule viewed at a different scale. Code, tests, and documentation must remain aligned to this single canonical mapping.

> **Terminology note:** The sovereign has reframed the underlying theory as **constitutional physics**. Legacy references to "APEX THEORY" in older documents should be read as the same physical substrate; new writing should prefer "constitutional physics."

---

## 2. Canonical 11-Stage Constitutional Pipeline

| Stage | Name | Function | Paradox-Resolution Annotation |
|-------|------|----------|-------------------------------|
| **000** | **INIT** | Bind identity, geometry, scar, soul, and lineage. | Establishes the actor-substrate boundary before any cognition occurs. |
| **111** | **SENSE** | Observe reality through multiple contrast transforms (Theory of Aligned Contrast). | No observation without a contrast pair; prevents single-perspective hallucination. |
| **222** | **EVIDENCE** | Tri-witness evidence from GEOX, WEALTH, WELL, and external sources. | Requires at least three independent witnesses or an explicit gap declaration. |
| **333** | **REASON** | Generate hypotheses with epistemic tiering. | Every claim carries an evidence tier; no interpretation masquerades as observation. |
| **444** | **ROUTE** | Send the candidate action to the correct organ; no self-routing of irreversible action. | Irreversible actions must be routed by the kernel, never by the proposing agent. |
| **555** | **MEMORY** | Compare against lineage, scars, and VAULT999. | Detects rhymes with past failures and prevents institutional amnesia. |
| **666** | **GOVERN** | Apply the F1–F13 constitutional floors; detect drift, hallucination, and paradox. | The floor scan is a hard gate, not an advisory checklist. |
| **777** | **MEASURE** | Compute AC_Risk, entropy, fatigue, and reversibility. | Quantifies the cost of being wrong before the action is approved. |
| **888** | **JUDGE** | External verdict: SEAL, SABAR, HOLD, or VOID. | Judgment is performed by an external constitutional organ, never by the executor. |
| **889** | **PROOF** | Issue receipt, lease, scope, and expected outcome. | A binding contract that the execution layer must honor. |
| **999** | **SEAL** | Write to VAULT999; the action becomes memory. | Irreversible only at this stage; the chain is append-only and hash-linked. |

### 2.1 Stage Groupings by Cognitive Organ

- **Mind (orthogonal reasoning):** 111 SENSE → 222 EVIDENCE → 333 REASON  
- **Heart (fractal empathy / critique):** 555 MEMORY → 666 GOVERN  
- **Soul (toroidal closure):** 000 INIT, 444 ROUTE, 777 MEASURE, 888 JUDGE, 889 PROOF, 999 SEAL

### 2.2 Hard Invariants

- **No stage may be skipped.** A detected skip returns `HOLD`.
- **No stage may claim completion without evidence.**
- **888 JUDGE is external.** The proposing runtime cannot judge its own action.
- **999 SEAL is irreversible.** Everything before 999 is reversible; 999 is not.
- **Entropy must be non-increasing across the pipeline.** ΔS ≤ 0 at each transition.

---

## 3. Canonical 5-Stage Metabolic Loop

The metabolic loop in `arifosmcp/kernel/metabolic_loop.py` compresses the 11-stage pipeline into five execution stages that fit the kernel's stage-gate engine.

| Metabolic Stage | 11-Stage Equivalent | Runtime Meaning |
|-----------------|---------------------|-----------------|
| **000 PERCEIVE** | 000 INIT + 111 SENSE + 222 EVIDENCE | Bind the session and gather witnessed reality. |
| **444 PROPOSE** | 333 REASON + 444 ROUTE | Form the candidate action and route it to the correct organ. |
| **777 EVALUATE** | 555 MEMORY + 666 GOVERN + 777 MEASURE | Recall lineage, apply F1–F13 floors, and measure risk. |
| **888 SOVEREIGN** | 888 JUDGE + 889 PROOF | Obtain external verdict and issue execution proof. |
| **999 SEAL** | 999 SEAL | Commit the action to VAULT999. |

### 3.1 Why the Numbers Are Preserved

The metabolic stage numbers are not arbitrary labels. They are the **highest-numbered stage** contained within each compressed block, making the 5-stage loop a lossy but deterministic projection of the 11-stage pipeline:

```
000 PERCEIVE  ← {000, 111, 222}
444 PROPOSE   ← {333, 444}
777 EVALUATE  ← {555, 666, 777}
888 SOVEREIGN ← {888, 889}
999 SEAL      ← {999}
```

This preserves the invariant that stage order is monotonic and that each metabolic gate maps back to one or more constitutional gates.

---

## 4. Known Drift and Alignment Status

The E2E integration test `tests/e2e/test_000_to_999_flow.py` currently mixes the two schemes and assigns some stages incorrectly. Specifically:

- **333 was labeled MIND but is canonically REASON.** `mind_reason` is an acceptable implementation name; the stage label must be REASON.
- **444 was labeled HEART/CRITIQUE but is canonically ROUTE.** Critique belongs at **666 GOVERN**.
- **555 was conflated with ROUTE but is canonically MEMORY.** Routing is **444**.

These label and comment mismatches are being aligned in a separate E2E-test pass. The execution logic in the test remains valid; only the stage naming must converge to this canonical mapping.

---

## 5. How to Use This Document

- **When adding a tool:** Map it to the lowest constitutional stage it participates in.
- **When writing tests:** Name test classes and comments after the 11-stage pipeline.
- **When compressing for runtime:** Use the 5-stage metabolic mapping and document the 11-stage decomposition in comments.
- **When in doubt:** The 11-stage pipeline is the source of truth. The 5-stage loop follows from it.

---

## 6. Summary

> The 11-stage constitutional pipeline is the canonical lifecycle.  
> The 5-stage metabolic loop is the same lifecycle compressed for execution.  
> They are the same geometry at different resolutions.

Both are governed by the same constitutional physics: identity before observation, evidence before reason, routing before governance, measurement before judgment, and proof before seal.
