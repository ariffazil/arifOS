---
canon_id: 10_FEDERATION_LOOP_GEOX
bundle: CANON_APEX_V2
version: v2026.07.APEX
status: SEALED_CANON
apex_theory: T-000
floors_version: 2026.07
epoch: 2026-07-26T00:30+08
source: GEOX/docs/archive/entropy-2026-07-15/FEDERATION_LOOP_GEOX_SPACE.md (v2026.05.02, updated)
---

# GEOX — Federation Loop Reference

> **DITEMPA BUKAN DIBERI — Physics before narrative. Maruah before convenience.**

GEOX is the **earth intelligence Ψ-node** in the arifOS federation. It governs
wells, seismic, maps, time, and prospects — the physical substrate of capital
decisions that involve natural resources, planetary boundaries, or subsurface
reality.

## Constitutional Position

GEOX is the **only organ** with a direct gateway to `arif_judge` (888_JUDGE).
All other organs feed evidence at stage 222; GEOX can invoke the judge directly
via `geox_prospect` when a prospect evaluation is ready for constitutional
ratification.

```
Subsurface Signal (LAS / SEG-Y / CSV / Parquet)
         │
         ▼
GEOX Kernel (port :8081, 32 canonical tools)
         │
    ┌────┴────────────────────────────────────┐
    │  Standard path (stage 222):             │
    │  geox_evidence · geox_prospect          │
    │          │                              │
    │          ▼                              │
    │  arif_observe (222)                     │
    │          │  earth_evidence field        │
    │          ▼                              │
    │  arif_judge (888)                       │
    └────────────────────────────────────────┘
         │
    ┌────┴────────────────────────────────────┐
    │  Direct judge path (prospect-ready):    │
    │  geox_prospect (mode=evaluate)          │
    │          │  SEAL / HOLD / SABAR / VOID  │
    │          ▼                              │
    │  arif_judge (888)                       │
    └────────────────────────────────────────┘
```

## How GEOX Feeds arifOS

### Stage 222 — Standard Evidence Path

| Tool | Output | arifOS Field |
|:-----|:-------|:-------------|
| `geox_evidence` | Causal synthesis — well + seismic + map + time | `earth_evidence.synthesis` |
| `geox_prospect` | Probabilistic volumetrics (GRV/NTG/Recov), POS score | `earth_evidence.prospect` |

### Stage 888 — Direct Judge Gateway

`geox_prospect` (evaluate mode) is the constitutional boundary tool.
Heavily auth-gated — F11 mandatory before invocation.

| Verdict | Meaning |
|:--------|:--------|
| SEAL | Prospect constitutionally cleared for capital commitment |
| HOLD | Human confirmation required before proceeding |
| SABAR | Wait — timing constraint; conditions not yet met |
| VOID | Hard floor violation — prospect blocked |

### F3 Tri-Witness Contribution

GEOX populates the earth dimension of `witness.earth` in the F3 Tri-Witness
gate. A subsurface capital decision missing GEOX earth evidence cannot receive
a full `SEAL` from `arif_judge`.

## GEOX Tool Surface (32 canonical tools)

| Category | Tools | Purpose |
|:---------|:------|:--------|
| Ingest | `geox_well_ingest`, `geox_seismic_ingest` | LAS, SEG-Y, CSV, Parquet loading |
| QC | `geox_well_qc` | Header/unit/CRS/anomaly/missingness verification |
| Compute | `geox_petrophysics`, `geox_seismic_compute`, `geox_geomechanics` | Vsh, porosity, Sw, AI, synthetic, inversion |
| Interpret | `geox_seismic_interpret` | Horizon tracking, fault sticks, structure validation |
| Basin | `geox_basin` | Profile, macrostrat, backstrip, thermal maturity |
| Map | `geox_map_*` (4 tools) | Layer listing, scene planning, render, export |
| Claim | `geox_claim`, `geox_falsify`, `geox_contradiction_scan` | Evidence lifecycle, K001-K007 falsification |
| Prospect | `geox_prospect` | Volumetrics, POS, EVOI, risk assessment |
| Bridge | `geox_to_wealth_bridge` | Prospect economics → WEALTH score_kernel |

**Fail-closed:** GEOX_SECRET_TOKEN missing → F1_HALT before port bind.

## Sibling Organs

| Organ | Role |
|:------|:-----|
| arifOS | Constitutional kernel — receives GEOX evidence at stage 222 |
| WEALTH | Capital intelligence — receives GEOX prospect economics via bridge |
| WELL | Human substrate — gates decision classes before capital evaluation |
| A-FORGE | Execution shell — executes post-SEAL capital allocation |
| AAA | Identity gateway — A2A routing |

DITEMPA BUKAN DIBERI — Earth evidence is forged, not given.

---
CANON_STATUS: SEALED · APEX THEORY
CANON_BUNDLE: CANON_APEX_V2 (13 files)
GOVERNANCE_CORE: arifOS · APEX Theory · F1–F13 Floors
VAULT999_HASH: <pending>
TRI-WITNESS: human · AI · earth >= 0.75
