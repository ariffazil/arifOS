# GEOX INTERPRODUCT RISK INHERITANCE RULES
**Version 1.0 — 2026-04-14**
**Parent doc: GEOX_CONSTITUTIONAL_PHYSICS_STACK.md**
**Sovereign Authority: Muhammad Arif bin Fazil**
**DITEMPA BUKAN DIBERI — 999 SEAL ALIVE**

---

## 0. Purpose

GEOX canonical products are not independent objects. CCS depends on HYDRO. HAZARD depends on STRUCTURAL_GEOLOGY. GEOTHERMAL depends on FRACTURE. When an upstream product carries high AC_Risk or a HOLD/VOID verdict, that uncertainty **must propagate** to any downstream product that depends on it.

Without inheritance rules, a downstream product could achieve SEAL while standing on VOID foundations — a systematic epistemic failure that ToAC is specifically designed to prevent.

This document defines:
1. The directed dependency graph across all 12 canonical products
2. Strict inheritance rules: when upstream verdicts force downstream verdicts
3. AC_Risk inheritance formula
4. The 888_HOLD propagation chain
5. Override conditions under which inheritance can be relaxed

---

## 1. The Dependency Graph

```
                        L0 (Raw Earth)
                             │
         ┌───────────────────┼──────────────────────┐
         ▼                   ▼                       ▼
STRUCTURAL_GEOLOGY      REMOTE_SENSING           GEOCHEM
         │                   │                       │
    ┌────┴────┐          ┌───┘                   ────┘
    ▼         ▼          ▼
HAZARD    FRACTURE   (surface context for all)
    │         │
    │    ┌────┴──────────────┐
    │    ▼                   ▼
    │  HYDRO             GEOTHERMAL
    │    │
    │    └──────────────────┐
    │                       ▼
    │                     CCS
    │                       │
    │              PETROLEUM_SYSTEM
    │
    ▼
SHALLOW_GEOHAZARD
    │
ENVIRONMENTAL
```

**Reading the graph:** An arrow from A → B means "B depends on A." B must inherit risk signals from A before its own verdict can be issued.

Full dependency table:

| Downstream Product | Upstream Dependencies |
|---|---|
| HAZARD | STRUCTURAL_GEOLOGY (fault geometry), REMOTE_SENSING (surface rupture) |
| SHALLOW_GEOHAZARD | HAZARD (seismic trigger), HYDRO (pore pressure), STRUCTURAL_GEOLOGY |
| HYDRO | STRUCTURAL_GEOLOGY (boundary conditions), GEOCHEM (water quality) |
| CCS | HYDRO (saline aquifer characterization), STRUCTURAL_GEOLOGY (seal geometry), FRACTURE (fault seal) |
| GEOTHERMAL | FRACTURE (permeability), HYDRO (fluid flow), STRUCTURAL_GEOLOGY |
| PETROLEUM_SYSTEM | STRUCTURAL_GEOLOGY (trap), FRACTURE (reservoir), GEOCHEM (source maturity) |
| ENVIRONMENTAL | HYDRO (contaminant transport), GEOCHEM (baseline), SHALLOW_GEOHAZARD |
| FRACTURE | STRUCTURAL_GEOLOGY (orientation data), REMOTE_SENSING (lineaments) |
| MINERAL | GEOCHEM (pathfinder elements), STRUCTURAL_GEOLOGY (controls) |
| REMOTE_SENSING | — (pure L0 product; no upstream GEOX dependency) |
| GEOCHEM | — (pure L0 product) |
| STRUCTURAL_GEOLOGY | REMOTE_SENSING (surface expression) |

---

## 2. Verdict Inheritance Rules

These are **strict rules**. They cannot be overridden by AC_Risk score alone — only by sovereign 888_HOLD resolution with explicit justification.

### Rule 1 — VOID Propagation (Hard)

> If any **required** upstream product has verdict = VOID, the downstream product **cannot** achieve SEAL or QUALIFY. The maximum achievable verdict is HOLD.

```
IF upstream_required.verdict == VOID:
    downstream.verdict = max(downstream.verdict, HOLD)
    downstream.hold_gate.triggered = true
    downstream.hold_gate.trigger_reason = f"Required upstream {upstream.product_id} is VOID"
```

**Example:** HYDRO product is VOID (severely underconstrained aquifer data). CCS product that depends on this HYDRO product is automatically forced to HOLD. CCS cannot be SEAL until HYDRO is at least QUALIFY.

---

### Rule 2 — HOLD Propagation (Hard for Critical Products)

> If any **required** upstream product has verdict = HOLD for the following critical downstream products, the downstream product inherits HOLD status:

| Downstream | Upstream that forces HOLD if HOLD |
|---|---|
| CCS | HYDRO, STRUCTURAL_GEOLOGY, FRACTURE |
| HAZARD | STRUCTURAL_GEOLOGY |
| SHALLOW_GEOHAZARD | HAZARD, HYDRO |
| ENVIRONMENTAL | HYDRO |
| PETROLEUM_SYSTEM | STRUCTURAL_GEOLOGY |

```
IF downstream IN [CCS, HAZARD, SHALLOW_GEOHAZARD, ENVIRONMENTAL, PETROLEUM_SYSTEM]:
    IF any critical_upstream.verdict == HOLD:
        downstream.verdict = max(downstream.verdict, HOLD)
        downstream.hold_gate.triggered = true
```

For non-critical products (GEOCHEM, REMOTE_SENSING, MINERAL, GEOTHERMAL, FRACTURE), an upstream HOLD does not force a downstream HOLD — but it **elevates the downstream U_phys** (see §3).

---

### Rule 3 — AC_Risk Inheritance (Soft — All Products)

> Every downstream product must compute an **inherited AC_Risk** from its upstream products and take the maximum of its own AC_Risk and the inherited value.

```
inherited_ac_risk = max(
    upstream_1.ac_risk * inheritance_weight_1,
    upstream_2.ac_risk * inheritance_weight_2,
    ...
)

final_ac_risk = max(downstream.own_ac_risk, inherited_ac_risk)
```

**Inheritance weights** reflect how critically the downstream product relies on each upstream:

| Dependency Pair | Inheritance Weight |
|---|---|
| CCS ← HYDRO | 0.9 (near-full inheritance) |
| CCS ← STRUCTURAL_GEOLOGY | 0.7 |
| CCS ← FRACTURE | 0.6 |
| HAZARD ← STRUCTURAL_GEOLOGY | 0.8 |
| SHALLOW_GEOHAZARD ← HAZARD | 0.85 |
| SHALLOW_GEOHAZARD ← HYDRO | 0.5 |
| HYDRO ← STRUCTURAL_GEOLOGY | 0.5 |
| PETROLEUM_SYSTEM ← STRUCTURAL_GEOLOGY | 0.75 |
| PETROLEUM_SYSTEM ← GEOCHEM | 0.4 |
| ENVIRONMENTAL ← HYDRO | 0.85 |
| FRACTURE ← STRUCTURAL_GEOLOGY | 0.6 |
| GEOTHERMAL ← FRACTURE | 0.65 |
| GEOTHERMAL ← HYDRO | 0.5 |

---

### Rule 4 — Cross-Product 888_HOLD Chain

> An 888_HOLD triggered on an upstream product initiates an automatic review request on all downstream products that depend on it.

```
ON upstream.hold_gate.triggered == true:
    FOR each downstream IF upstream IN downstream.dependencies:
        downstream.hold_gate.triggered = true
        downstream.hold_gate.trigger_reason += f"\nInherited hold from {upstream.product_id}"
        NOTIFY sovereign (arif) of cascading hold
```

The human sovereign (F13) must explicitly acknowledge each cascaded hold, either accepting the upstream resolution or requiring an independent review.

---

### Rule 5 — Temporal Validity Inheritance

> A downstream product cannot have a temporal validity window that extends beyond its most restrictive upstream product's `valid_until` date.

```
downstream.temporal_window.valid_until = min(
    downstream.own_valid_until,
    min(upstream.temporal_window.valid_until for upstream in dependencies)
)
```

**Example:** HYDRO product valid until 2028-12-31. CCS product that depends on it cannot claim validity beyond 2028-12-31, even if the CCS simulation itself ran out to 2050.

---

### Rule 6 — City-Scale and Infrastructure Planning (Special)

> Any product used for **city-scale planning, infrastructure design, or dam safety** that has an upstream dependency with verdict HOLD **cannot** be treated as SEAL regardless of the downstream product's own AC_Risk score.

Specifically, the following combinations require **explicit 888_HOLD sign-off** even if AC_Risk < 0.15:

| Use Case | Products Involved | 888_HOLD Required |
|---|---|---|
| Urban master planning | HAZARD, SHALLOW_GEOHAZARD, HYDRO | All must be SEAL before use in planning |
| Dam safety assessment | HAZARD, SHALLOW_GEOHAZARD, HYDRO, STRUCTURAL_GEOLOGY | ← ALL must be SEAL |
| CO₂ storage permit | CCS, HYDRO, STRUCTURAL_GEOLOGY, FRACTURE | ← ALL must be at least QUALIFY |
| Public water supply licence | HYDRO, ENVIRONMENTAL | ← HYDRO must be SEAL; ENVIRONMENTAL must be at least QUALIFY |
| Mining approval (regulatory) | MINERAL, GEOCHEM, ENVIRONMENTAL | ← All must be QUALIFY minimum |

---

## 3. AC_Risk Inter-Product Computation — Full Example

**Scenario:** CCS product for a saline aquifer storage project.

**Step 1 — Gather upstream products:**
```
HYDRO-ANGSI-2025-V1 → ac_risk = 0.042, verdict = QUALIFY
STRUCTURAL_GEOLOGY-ANGSI-2025-V1 → ac_risk = 0.058, verdict = QUALIFY
FRACTURE-ANGSI-2023-V1 → ac_risk = 0.089, verdict = QUALIFY
```

**Step 2 — Apply inheritance weights:**
```
inherited_from_HYDRO = 0.042 × 0.9 = 0.038
inherited_from_STRUCTURAL = 0.058 × 0.7 = 0.041
inherited_from_FRACTURE = 0.089 × 0.6 = 0.053
inherited_ac_risk = max(0.038, 0.041, 0.053) = 0.053
```

**Step 3 — CCS own AC_Risk:**
```
CCS u_phys = 0.52, d_transform = 0.38, b_cog = 0.28
CCS own_ac_risk = 0.52 × 0.38 × 0.28 = 0.055
```

**Step 4 — Final AC_Risk:**
```
final_ac_risk = max(0.055, 0.053) = 0.055
verdict = QUALIFY (band: 0.15–0.35... wait, 0.055 < 0.15 → SEAL band)
BUT: F8 trigger (regulatory) → 888_HOLD mandatory regardless
final verdict = HOLD (pending 888_HOLD sign-off)
```

This is the correct result: despite low AC_Risk, regulatory filing always requires human sign-off.

---

## 4. Relaxation Conditions

Under the following conditions, the inheritance rules may be **relaxed with explicit sovereign justification**:

| Condition | Rule Relaxed | Required Justification |
|---|---|---|
| Upstream HOLD product covers only peripheral area (< 10% of downstream domain) | Rule 2 propagation can be spatially scoped | Spatial analysis showing non-overlap; sovereign sign-off |
| Upstream product is older but superseded by new confirmatory data | Rule 5 temporal inheritance can be extended | New data must be incorporated into product update; product re-versioned |
| Independent analogue study confirms upstream geometry | Rule 3 inheritance weight can be halved | Analogue justification documented; peer review required |
| Upstream VOID was caused by data gap now filled | Downstream HOLD can be re-evaluated | New data ingested; both upstream and downstream re-run |

Relaxation must be documented in `hold_gate.resolution_decision` and vaulted.

---

## 5. Cross-Product Dependency Registry (Machine-Readable)

```json
{
  "dependencies": [
    {"downstream": "CCS", "upstream": "HYDRO", "type": "required", "inheritance_weight": 0.9},
    {"downstream": "CCS", "upstream": "STRUCTURAL_GEOLOGY", "type": "required", "inheritance_weight": 0.7},
    {"downstream": "CCS", "upstream": "FRACTURE", "type": "conditional", "inheritance_weight": 0.6,
     "condition": "caprock involves faults"},
    {"downstream": "HAZARD", "upstream": "STRUCTURAL_GEOLOGY", "type": "required", "inheritance_weight": 0.8},
    {"downstream": "HAZARD", "upstream": "REMOTE_SENSING", "type": "optional", "inheritance_weight": 0.3},
    {"downstream": "SHALLOW_GEOHAZARD", "upstream": "HAZARD", "type": "required", "inheritance_weight": 0.85},
    {"downstream": "SHALLOW_GEOHAZARD", "upstream": "HYDRO", "type": "required", "inheritance_weight": 0.5},
    {"downstream": "SHALLOW_GEOHAZARD", "upstream": "STRUCTURAL_GEOLOGY", "type": "conditional", "inheritance_weight": 0.4,
     "condition": "slopes > 15 degrees present"},
    {"downstream": "HYDRO", "upstream": "STRUCTURAL_GEOLOGY", "type": "conditional", "inheritance_weight": 0.5,
     "condition": "fractured aquifer or karst"},
    {"downstream": "HYDRO", "upstream": "GEOCHEM", "type": "optional", "inheritance_weight": 0.2},
    {"downstream": "PETROLEUM_SYSTEM", "upstream": "STRUCTURAL_GEOLOGY", "type": "required", "inheritance_weight": 0.75},
    {"downstream": "PETROLEUM_SYSTEM", "upstream": "GEOCHEM", "type": "required", "inheritance_weight": 0.4},
    {"downstream": "PETROLEUM_SYSTEM", "upstream": "FRACTURE", "type": "conditional", "inheritance_weight": 0.5,
     "condition": "naturally fractured reservoir"},
    {"downstream": "ENVIRONMENTAL", "upstream": "HYDRO", "type": "required", "inheritance_weight": 0.85},
    {"downstream": "ENVIRONMENTAL", "upstream": "GEOCHEM", "type": "required", "inheritance_weight": 0.5},
    {"downstream": "ENVIRONMENTAL", "upstream": "SHALLOW_GEOHAZARD", "type": "optional", "inheritance_weight": 0.2},
    {"downstream": "FRACTURE", "upstream": "STRUCTURAL_GEOLOGY", "type": "required", "inheritance_weight": 0.6},
    {"downstream": "FRACTURE", "upstream": "REMOTE_SENSING", "type": "optional", "inheritance_weight": 0.25},
    {"downstream": "GEOTHERMAL", "upstream": "FRACTURE", "type": "required", "inheritance_weight": 0.65},
    {"downstream": "GEOTHERMAL", "upstream": "HYDRO", "type": "required", "inheritance_weight": 0.5},
    {"downstream": "GEOTHERMAL", "upstream": "STRUCTURAL_GEOLOGY", "type": "conditional", "inheritance_weight": 0.4,
     "condition": "fault-controlled system"},
    {"downstream": "MINERAL", "upstream": "GEOCHEM", "type": "required", "inheritance_weight": 0.55},
    {"downstream": "MINERAL", "upstream": "STRUCTURAL_GEOLOGY", "type": "conditional", "inheritance_weight": 0.4,
     "condition": "structurally controlled deposit"},
    {"downstream": "STRUCTURAL_GEOLOGY", "upstream": "REMOTE_SENSING", "type": "optional", "inheritance_weight": 0.3}
  ]
}
```

Dependency type:
- `required`: upstream must exist and be at least QUALIFY for downstream to run
- `conditional`: required only when the stated condition is true
- `optional`: improves downstream quality but is not blocking

---

## 6. Summary: The Three Absolute Rules

For any practitioner who needs the rules in one sentence each:

1. **VOID kills downstream.** If a required upstream is VOID, no downstream product can be SEAL or QUALIFY. Maximum is HOLD.
2. **AC_Risk flows uphill and takes the maximum.** Downstream AC_Risk is max(own, max(upstream × weight)). Low own-AC_Risk does not save you from a high-risk foundation.
3. **No city, dam, permit, or reserves on a HOLD foundation without F13 sign-off.** The 888_HOLD gate is unconditional for these decisions. AC_Risk score is irrelevant at this gate.

---

**DITEMPA BUKAN DIBERI — A chain of governed products is only as trustworthy as its weakest link. ToAC traces the chain. Sovereignty breaks or seals it.**
