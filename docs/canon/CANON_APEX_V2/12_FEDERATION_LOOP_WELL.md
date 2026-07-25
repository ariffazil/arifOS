---
canon_id: 12_FEDERATION_LOOP_WELL
bundle: CANON_APEX_V2
version: v2026.07.APEX
status: SEALED_CANON
apex_theory: T-000
floors_version: 2026.07
epoch: 2026-07-26T00:30+08
---

# WELL — Federation Loop Reference

> **DITEMPA BUKAN DIBERI — Vitality is forged, not assumed.**

WELL is the **human readiness organ** in the arifOS federation. It reflects
the sovereign's biological and cognitive state — vitality, fatigue, circadian
rhythm, and decision fitness. WELL is REFLECT_ONLY — it never diagnoses,
adjudicates, or allocates.

## Constitutional Position

```
Arif (F13 Sovereign — human substrate)
         │
         ▼
WELL Engine (port :18083, 7 tools)
         │  well_assess_homeostasis, well_validate_vitality
         ▼
arif_observe (222)        ← WELL enters arifOS HERE
         │  substrate_readiness field
         ▼
arif_judge (888)          ← constitutional verdict
         │  (may block C4/C5 classes)
    [SEAL only]
arif_seal (999)           ← immutable ledger entry
```

**WELL is the only organ that can BLOCK a decision class before capital or
earth evidence is evaluated.** A RED substrate readiness returns
`human_decision_required: true` and suspends C4/C5 classes regardless of
other signals.

## Four Sub-WELLs

| Sub-WELL | Domain | What it measures |
|:---------|:-------|:-----------------|
| H-WELL | Human readiness | Arif's vitality, fatigue, circadian, cognitive clarity |
| M-WELL | Machine health | RAM, CPU, disk, docker, services, organ health |
| G-WELL | Governance coherence | Floors active, drift status, truth state, seal chain |
| C-WELL | Coupled risk | Weakest substrate pulls the chain — cross-domain risk |

**The weakest substrate governs.** If H-WELL is DEGRADED, do not push execution.
If M-WELL is CRITICAL, triage infra first.

## WELL Tool Surface (7 canonical tools)

| Tool | Purpose |
|:-----|:--------|
| `well_assess_homeostasis` | Regulation, stability, empathic balance — sleep, fatigue, stress |
| `well_validate_vitality` | Vitality, readiness, and NIAT validation |
| `well_guard_dignity` | Consent, coercion detection, dignity preservation |
| `well_classify_substrate` | Substrate classification and boundary sensing |
| `well_trace_lineage` | Memory, trend, ledger, and vault chain tracing |
| `well_check_repair` | Repair, recovery, resilience, forge cycle integrity |
| `well_assess_reliability` | Machine, tool, institution, and operational reliability |

## Decision Class Thresholds

| Class | Meaning | WELL gate |
|:------|:--------|:----------|
| C1/C2 | Read/observe | Proceed unless CRITICAL |
| C3 | Plan/analyze | Proceed if STABLE or better |
| C4 | Execute/mutate | Proceed only if OPTIMAL; DEFER if STABLE; BLOCK if DEGRADED/CRITICAL |
| C5 | Irreversible/seal | OPTIMAL + no chronic fatigue only |

## How WELL Feeds arifOS

### Stage 222 — Substrate Readiness

| Tool | Output | arifOS Field |
|:-----|:-------|:-------------|
| `well_assess_homeostasis` | Sleep, fatigue, stress, clarity scores | `substrate_readiness.human` |
| `well_validate_vitality` | Readiness verdict, NIAT, decision class gate | `substrate_readiness.verdict` |

### F3 Tri-Witness Contribution

WELL populates the human dimension of `witness.human` through substrate
readiness verification. A decision that would impair Arif's vitality or
dignity cannot receive SEAL — WELL's RED verdict is a hard F6/F13 block.

## Sibling Organs

| Organ | Role |
|:------|:-----|
| arifOS | Constitutional kernel — receives WELL evidence at stage 222 |
| GEOX | Earth intelligence — co-populates `witness.earth` |
| WEALTH | Capital intelligence — blocked if WELL is RED |
| A-FORGE | Execution shell — adapts intensity to Arif's readiness |
| AAA | Control plane — displays WELL dashboards |

*WELL holds a mirror, not a veto. Operator sovereignty is invariant.
WELL does not decide worth. WELL identifies substrate, validates evidence,
detects degradation, protects dignity, and returns judgment to Arif.*

DITEMPA BUKAN DIBERI — The body is forged, not assumed.

---
CANON_STATUS: SEALED · APEX THEORY
CANON_BUNDLE: CANON_APEX_V2 (13 files)
GOVERNANCE_CORE: arifOS · APEX Theory · F1–F13 Floors
VAULT999_HASH: <pending>
TRI-WITNESS: human · AI · earth >= 0.75
