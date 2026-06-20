# Substrate Reference Layer (Unified Spec)

**Sovereign:** Muhammad Arif bin Fazil  
**Constitution:** arifOS Floors F4 (Clarity), F8 (Genius), F13 (Sovereign)  
**Version:** v2026.06.20-CONSOLIDATED  
**Status:** DRAFT — NOT RATIFIED — TIER 5 (Governance Doctrine) — 888 HOLD ACTIVE

---

## 0. Important Caveat

This document is **Tier 5 governance doctrine — DRAFT and NOT RATIFIED**. It
must not be treated as binding constitutional law. All code artifacts generated
from it carry the same `DRAFT — TIER 5 — 888 HOLD ACTIVE` watermark. F13
ratification is required before any of these mechanisms may block a SEAL.

---

## 1. Executive Summary

This Substrate Reference Layer maps the **existing** economic-physics
infrastructure inside arifOS and WEALTH, and closes three identified gaps:

1. **Landauer budget fragmentation** — The 12 invariants already exist in
   `core/physics/economic_invariants.py`. Landauer enforcement already exists in
   `core/physics/thermodynamics_hardened.py`, `arifosd.py`, and other modules.
   The gap is a **unified ledger**, not missing physics.

2. **Maintenance scaling blind spot** — No code, TODO, or fixture referenced
   passive complexity-time degradation before this draft. This is the single
   largest gap.

3. **Exergy in WEALTH** — `WEALTH/TODO.md` line 90 mandates thermodynamic
   capital accounting. Test fixtures reference `exergy_mj_per_unit` but no
   enforcement code existed.

---

## 2. Existing 12 Economic-Physics Invariants

Canonical location: `core/physics/economic_invariants.py` (~1,058 lines).

| ID | Name | Canonical check | Verdict on breach |
|----|------|-----------------|-------------------|
| I01 | Conservation of Allocated Value | `check_conservation_of_value` | VOID |
| I02 | Entropic Cost of Transaction | `check_entropic_cost` | VOID |
| I03 | Landauer Limit on Information Asymmetry | `check_landauer_asymmetry` | VOID |
| I04 | Thermodynamic Budget Constraint | `check_thermodynamic_budget` | 888_HOLD |
| I05 | Scarcity-Abundance Orthogonality | `check_scarcity_abundance_orthogonality` | SABAR |
| I06 | NPV as Entropy Gradient | `check_npv_entropy_gradient` | PARTIAL |
| I07 | Mode Collapse in Market Concentration | `check_mode_collapse_market` | VOID |
| I08 | Irreversibility of Capital Commitment | `check_irreversibility_commitment` | HOLD |
| I09 | Genius Discipline in Resource Allocation | `check_genius_discipline` | PARTIAL |
| I10 | Hysteresis of Wealth Accumulation | `check_hysteresis_wealth` | QUALIFY |
| I11 | Speed Limit on Value Transfer | `check_speed_limit_value` | SABAR |
| I12 | Immutable Ledger Conservation | `check_ledger_conservation` | VOID |

---

## 3. Landauer Budget Consolidation

### The Issue

Landauer limits are tracked independently in at least four places:
- `core/physics/thermodynamics_hardened.py` (`LANDAUER_MIN`)
- `arifosd.py` (`ApexThermodynamicEngine.LANDAUER_COST_J_PER_BIT`)
- `core/physics/economic_invariants.py` (`check_landauer_asymmetry`)
- Legacy estimators elsewhere

They lacked a unified accounting ledger.

### The Fix (DRAFT)

`core/physics/thermodynamics_hardened.py` now exports:
- `ThermodynamicBudgetLedger` — singleton-per-session ledger
- `init_budget_ledger(session_id, initial_joules)`
- `record_budget_operation(session_id, bits, ...)`
- `get_consolidated_budget_report(session_id)`
- `cleanup_budget_ledger(session_id)`

`arifosd.py` initializes the ledger per metabolize call and records the
Landauer cost of the APEX thermodynamic engine.

---

## 4. Maintenance Scaling (The Blind Spot)

### The Issue

Zero hits across all 6 repos before this draft.

### The Formulation (DRAFT)

```
E_maintenance = M_base * (1 + alpha * ln(1 + t_active)) * (1 + beta * Complexity_index)

Complexity_index = ln(1 + N_tools) + 0.02 * N_tracked_files
```

Constants:
- `M_base = 1e-6 J/s`
- `alpha = 0.05`
- `beta = 0.12`

### The Fix (DRAFT)

`core/physics/thermodynamics_hardened.py` now exports:
- `MaintenanceScaling` class
- `compute_maintenance_cost(...)`
- `apply_maintenance_decay(session_id, t_active_seconds, n_tools, n_tracked_files)`

`core/physics/economic_invariants.py` adds an opt-in check:
- `check_maintenance_scaling(...)` (I13_DRAFT)
- `run_all_invariants(..., include_maintenance_scaling=True)`

---

## 5. Exergy in WEALTH

### The Issue

`WEALTH/TODO.md` line 90: "Thermodynamic capital accounting — exergy +
negentropy capital types." No enforcement code existed.

### The Formulation (DRAFT)

```
Ξ = NPV_realized / (Allocated_Capital * (1 + ΔS_allocation))
η_x = Ξ / Allocated_Capital

Gate: η_x >= 0.70
```

If `η_x < 0.70`, the proposal is classified as **heat waste** (`VOID`).

### The Fix (DRAFT)

New module: `WEALTH/internal/engines/exergy.py`
- `calculate_exergy(...)`
- `exergy_gate(...)`
- `downgrade_verdict_by_exergy(...)`

Integration: `WEALTH/internal/engines/five_seals.py` now attaches an
`exergy_gate` field to the Five Seals output when `npv_realized` and
`allocated_capital` are present, and downgrades `VALUE_SEAL` to `HEAT_WASTE`
when the gate fails.

---

## 6. F9 ANTI-HANTU Boundary

F9 spans 6 implementations across the federation. This draft **does not**
rename, split, or reframe F9. The new energy/substrate constraints are
introduced as separate draft artifacts (I13_DRAFT, exergy gate), not as
modifications to F9.

---

## 7. Implementation Checklist

- [x] Acknowledge existing 12 invariants in `economic_invariants.py`
- [x] Map Landauer enforcement to real code locations
- [x] Add `ThermodynamicBudgetLedger` and registry helpers
- [x] Add `MaintenanceScaling` and decay helpers
- [x] Add I13_DRAFT maintenance check (opt-in)
- [x] Hook unified ledger into `arifosd.py` metabolize envelope
- [x] Implement `calculate_exergy()` in WEALTH
- [x] Integrate exergy gate into Five Seals
- [x] Add tests: `tests/test_substrate_reference_draft.py`,
      `WEALTH/tests/test_exergy_gate.py`
- [ ] F13 ratification before any draft gate may block SEAL

---

*DITEMPA BUKAN DIBERI — Intelligence is forged, not given.*
