# APEX Semantics — Epistemic Interoperability Contract

**Status:** BINDING companion to `apex.schema.json` + `apex-ontology.json`  
**Date:** 2026-07-12  
**Verdict context:** Files ≠ contracts ≠ federation coherent ≠ system proven  

---

## One law

```
schema compatibility  ≠  epistemic compatibility
local correctness     +  interface mismatch  =  system failure
```

A verified governed transition (the unit of completion) requires:

1. intent bound  
2. evidence typed  
3. uncertainty preserved  
4. authority valid  
5. contradictions exposed  
6. action scoped  
7. execution bounded  
8. outcome independently verified  
9. failure recoverable  
10. chain replayable  

---

## Confidence is a struct, not a float

```json
{
  "value": 0.78,
  "kind": "bayesian_posterior | frequentist_rate | model_output | expert_judgment | calibration_score | heuristic | unknown",
  "target": "what the number is about",
  "method": "how produced",
  "calibration_model": "id or null",
  "validation_window": "optional",
  "sample_size": null,
  "expires_at": "RFC3339 or null"
}
```

**Illegal:** combining GEOX posterior with LLM verbal certainty as if same type.

---

## Five coherences (must all pass for “federation coherent”)

| Coherence | Question |
|-----------|----------|
| **Structural** | Same outer envelope shape? |
| **Semantic** | Fields mean the same object? |
| **Temporal** | Fresh enough to combine? |
| **Authority** | Evidence ≠ recommendation ≠ approval ≠ execution? |
| **Contradiction** | Unresolved disagreement retained without false consensus? |

Example of coherent multi-verdict (not one global light):

| Claim / action | Verdict |
|----------------|---------|
| Technical feasibility study | SEAL |
| Further analysis | SEAL |
| Capital commitment | HOLD |
| Immediate irreversible execution | HOLD |

---

## Supremacy (precedence)

```
Constitution (F1–F13, APEX admissibility)
  > federation policy
  > domain policy
  > workflow configuration
  > agent prompt
```

When README language conflicts with this contract + ontology + schemas → **canonical wins**.

---

## Canonical owners

| Layer | Owner |
|-------|--------|
| Human purpose / F13 | Arif |
| APEX math + epistemic definitions | APEX / arifOS contracts |
| Verdict semantics SEAL/HOLD/VOID | arifOS |
| Federation state | AAA |
| Domain evidence meaning | GEOX / WELL / WEALTH |
| Execution / rollback | A-FORGE |
| Provenance | VAULT999 |
| Cross-organ envelope | Joint, versioned under arifOS contracts |

---

## Proof required (not docs)

| Artefact | Proves |
|----------|--------|
| `apex.schema.json` | Syntax |
| `apex-ontology.json` | Shared meaning catalogue |
| **this file** | Semantic rules |
| `federation_conformance.py` scenarios A–J | Integration under stress |
| Adversarial autonomy (unauth blocked + auth verify) | Bounded action |

---

See also: `apex-ontology.json`, `organ_evidence.schema.json`,  
`AAA/docs/REPOSITORY_AUTHORITY_MAP.md`,  
`A-FORGE/forge_work/2026-07-12/EPISTEMIC-SEMANTICS.md` (organ tables).
