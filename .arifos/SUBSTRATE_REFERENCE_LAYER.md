# Substrate Reference Layer (Unified Spec)
> **Sovereign:** Muhammad Arif bin Fazil
> **Constitution:** arifOS Floors F4 (Clarity), F8 (Genius), F13 (Sovereign)
| **Version:** v2026.06.20.3-DRAFT-1
| **Status:** F13 RATIFIED — TIER 5 (Governance Doctrine) — BINDING
| **Ratified by:** Muhammad Arif bin Fazil — "seal and ratify everything" (2026-06-20), amended v2026.06.20.3 per Mortality Rate Asymmetry doctrine
| **VAULT999 Seal:** `a624ba3d77796cd8` (original) + amendment v2026.06.20.3
| **888 HOLD:** LIFTED. Option B execution now authorized per ratification scope.
> **DITEMPA BUKAN DIBERI — Forged, Not Given.**

---

## Epistemic Tier Declaration

This document operates at **Tier 5 (Governance Doctrine).** It interprets Tier 0–2 physical constraints and proposes how arifOS should govern against them. It does NOT assert new physical law.

| Tier | Name | Domain | Example |
|------|------|--------|---------|
| **T0** | Physical Law | Immutable | Conservation, 2nd Law, causality, c, h, k_B |
| **T1** | Physical Constraint | Universal within known physics | Landauer bound (kT ln 2), Shannon entropy, exergy degradation |
| **T2** | Information/Structural Constraint | Any ordered system | Gödel incompleteness, embodiment requirements, maintenance scaling |
| **T3** | Empirical Evidence | Domain-observed | Subsurface uncertainty (GEOX), market mode collapse (WEALTH) |
| **T4** | Operational Model | System-specific | NPV entropy gradient, hysteresis of wealth accumulation |
| **T5** | Governance Doctrine | Constitutional choice | Floor thresholds, verdict rules, 888 HOLD criteria, exergy ratio η_x ≥ 0.70 |
| **T6** | Operational Decision | Per-session judgment | This session's budget, this action's lease scope |

**Tier discipline:** T0–T1 are physics — cannot be changed by any floor. T2 is structural — changing it requires extraordinary evidence. T5 is governance — changeable only by F13 ratification. This document proposes T5 doctrine informed by T0–T2 constraints.

**Amendment v2026.06.20.3 — Mortality Rate Asymmetry (F13 ratified 2026-06-20):** The four sub-floors of #15 (Human mortality, Population evolution, Institutional succession, AI adaptation) are **rate-coupled to their carriers**. When carrier mortality rate exceeds institutional succession recording rate, the institution's memory becomes incoherent. **888 HOLD fires on `succession_gap`** when the time between agent action and VAULT999 record exceeds the agent's expected lifetime. This is a rate-trigger, not a content-trigger. See `REAlITY_LAWS.md` §8 for the full doctrine.

---

## 1. Executive Summary

This Substrate Reference Layer acts as a unified blueprint for arifOS economic-physics invariants. It is a **non-binding working draft** that addresses three execution gaps identified during the June 2026 substrate audit:

1. **Fragmentation of Landauer Bounds**: Unifying the four independent Landauer tracking points (`arifosd.py`, `thermodynamics_hardened.py`, `economic_invariants.py`, `thermo_estimator.py`) under a single shared session budget.
2. **Maintenance Scaling (The Blind Spot)**: Introducing the first mathematical formulation for passive complexity-time degradation — zero hits across all 6 repos as of 2026-06-20.
3. **Exergy (Useful Work) in WEALTH**: Closing line 90 of `/root/WEALTH/TODO.md` by defining exergy-to-heat ratios.

**Nothing in this document is enforceable until F13 ratification.** The 12 economic-physics invariants in `core/physics/economic_invariants.py` remain the sole enforced substrate layer. This document proposes extensions — it does not modify existing enforcement.

---

## 2. The 12 Consolidated Economic-Physics Invariants

The economic-physics substrate is governed by the 12 invariants defined in `core/physics/ECONOMIC_INVARIANTS.md` and enforced by `core/physics/economic_invariants.py` (1,059 lines, callable enforcement). They are mapped here to their unified reference structures:

```
                            ┌────────────────────────┐
                            │    Sovereign (F13)      │
                            └───────────┬────────────┘
                                        │
                            ┌───────────▼────────────┐
                            │   arifOS Kernel (Ω)    │
                            └───────────┬────────────┘
                                        │
           ┌────────────────────────────┼───────────────────────────┐
           ▼                            ▼                           ▼
  [ I01 - I04: Thermo ]        [ I05 - I08: Market ]       [ I09 - I12: Ledger ]
  - Value Conservation         - Scarcity-Abundance        - Genius Discipline
  - Entropic Cost              - NPV as Gradient           - Hysteresis
  - Landauer Asymmetry         - Mode Collapse             - Speed Limit
  - Thermodynamic Budget       - Irreversibility           - Ledger Conservation
```

**Ground truth:** All 12 invariants have dedicated exception classes + check functions + physics analogies + verdict rules in `economic_invariants.py`. Plus 3 emergence layer checks (E_PSI, E_PWR, E_INT). Legacy aliases exist at lines 952-1007 for backward compatibility.

---

## 3. Landauer Budget Consolidation Schema (Solving Fragmentation)

### The Issue
Landauer limits are currently tracked independently in four places:
- `arifosd.py:35-98` — `ApexThermodynamicEngine` with `LANDAUER_COST_J_PER_BIT = 2.9e-21`
- `thermodynamics_hardened.py:42` — `LANDAUER_MIN = K_B * T * ln(2)` with `ThermodynamicBudget` class
- `economic_invariants.py:191-203` — `check_landauer_asymmetry()` as I03
- `thermo_estimator.py:25` — `landauer_limit()` utility

They lack a unified accounting ledger, resulting in fragmented energy-asymmetry tracking. Each module tracks its own budget independently.

### Proposed Unified Budget Model
A singleton `ThermodynamicBudgetLedger` running as a shared kernel memory structure inside `arifOS`. All tools query and modify this single ledger:

```python
# Proposed Unified Interface in core/physics/thermodynamics_hardened.py
# NOTE: Non-binding design sketch — DO NOT IMPLEMENT without F13 ratification
class ThermodynamicBudgetLedger:
    def __init__(self, session_id: str, initial_joules: float):
        self.session_id = session_id
        self.initial_joules = initial_joules
        self.consumed_joules = 0.0
        self.bits_erased = 0
        self.bits_written = 0

    def record_operation(self, bits: int, temperature_k: float = 300.0) -> float:
        # Landauer minimum energy dissipation: E = k_B * T * ln(2) * bits
        min_joules = bits * (1.380649e-23 * temperature_k * 0.69314718056)
        self.consumed_joules += min_joules
        self.bits_erased += bits
        return min_joules

    @property
    def remaining(self) -> float:
        return max(0.0, self.initial_joules - self.consumed_joules)
```

All four legacy points of contact would proxy their calls to the `ThermodynamicBudgetLedger` singleton, preventing duplicate accounting. **This is a design proposal, not an implementation directive.**

---

## 4. Maintenance Scaling Model (Closing the Blind Spot)

### The Issue
Audit scans on 2026-06-20 revealed **zero hits** for maintenance scaling across all 6 federation repos. An active agent consumes cognitive resources and creates system entropy over time, even during idle periods. Without a maintenance decay model, the system experiences undetected resource leakage. This is the single largest blind spot in the substrate architecture.

### Proposed Mathematical Formulation (Tier 5 — Governance Doctrine)
E_maintenance (ΔS_decay), representing the passive thermodynamic cost of keeping an agent session or organ active:

$$E_{\text{maintenance}} = M_{\text{base}} \cdot \left(1 + \alpha \ln(1 + t_{\text{active}})\right) \cdot \left(1 + \beta \cdot \text{Complexity}_{\text{index}}\right)$$

Where:
- M_base: Base maintenance cost (10⁻⁶ Joules/sec)
- t_active: Time elapsed in seconds since session initialization
- α: Time scaling decay coefficient (0.05)
- β: Complexity decay scaling multiplier (0.12)
- Complexity_index: Calculated based on the number of active tools and repository file density:
  $$\text{Complexity}_{\text{index}} = \ln(1 + N_{\text{tools}}) + 0.02 \cdot N_{\text{tracked\_files}}$$

### Proposed Enforcement (Requires F13 Ratification)
If ratified, the `arifosd` daemon would deduct E_maintenance from the active `ThermodynamicBudget` on every session loop. If idle decay exhausts the remaining budget, the session would trigger an `888_HOLD` to stop further computation.

**Current state:** No enforcement. Formula is a first draft for discussion. Coefficients (α=0.05, β=0.12, M_base=10⁻⁶) are placeholders requiring empirical calibration.

---

## 5. Exergy (Useful Work) in WEALTH (Resolving the TODO Gap)

### The Issue
Line 90 of `/root/WEALTH/TODO.md` reads: `- [ ] Thermodynamic capital accounting — exergy + negentropy capital types`. Test fixtures in `/root/WEALTH/tests/fixtures/micro-loan-loop.json` reference `exergy_mj_per_unit` but no enforcement code exists. WEALTH currently measures entropy (via `thermodynamics_hardened.py` integration) but not energy *quality* — the distinction between useful work and waste heat.

### Proposed Exergy Model (Tier 5 — Governance Doctrine)
Exergy (Ξ) represents the maximum useful work obtainable from a capital/computational allocation before it reaches equilibrium:

$$\Xi = \frac{W_{\text{useful}}}{H_{\text{total}}} = \frac{\text{NPV}_{\text{realized}}}{\text{Allocated Capital} \cdot \left(1 + \Delta S_{\text{allocation}}\right)}$$

Where:
- NPV_realized: Net Present Value generated by the trade or asset allocation
- Allocated Capital: The total financial or compute resources deployed
- ΔS_allocation: The change in entropy caused by the decision

### Proposed Enforcement Rules (Requires F13 Ratification)
If ratified, before issuing a `SEAL` verdict on any capital allocation proposal, the WEALTH organ would evaluate the exergy ratio:

$$\text{Exergy Ratio } (\eta_x) = \frac{\Xi}{\text{Allocated Capital}} \ge 0.70$$

If η_x < 0.70, the proposal would be flagged as **heat waste** — the resource allocation is too entropic relative to the value it returns. The specific threshold (0.70) is a governance choice (Tier 5), not a physical constant (Tier 0–1). It should be calibrated against historical WEALTH decisions before enforcement.

---

## 6. Relationship to Existing Enforcement

| Layer | File | Status | This Document's Stance |
|-------|------|--------|------------------------|
| F1-F13 Floors | `core/shared/laws.py` | ENFORCED | No changes proposed |
| F9 ANTI-HANTU | 6 implementations | ENFORCED | **Untouched** — constitutional law |
| 12 Economic Invariants | `economic_invariants.py` | ENFORCED | Extends, does not replace |
| Thermodynamic Hardening | `thermodynamics_hardened.py` | ENFORCED | Proposes unification of 4 Landauer trackers |
| ApexThermodynamicEngine | `arifosd.py` | ENFORCED | No changes proposed |
| WEALTH exergy | `/root/WEALTH/TODO.md` line 90 | TODO | Proposes implementation |
| Maintenance scaling | — | ABSENT | Proposes first formulation |

---

## 7. Ratification Path

This document follows the constitutional forge order:

```
1. DRAFT v0.1 (this document)    ← CURRENT STATE — non-binding
2. F1-F13 mapping review          ← Next: each floor must affirm or reject each proposal
3. Sovereign review (F13)         ← Arif reads, amends, or vetoes
4. If ratified: forge to .arifos/ as binding Tier 5 doctrine
5. If ratified: implement per ratification scope (Option B)
```

**Until Step 4, this document has zero enforcement authority.** The existing 12 invariants in `economic_invariants.py` remain the sole enforced substrate layer.

---

*F13 RATIFIED — Seal a624ba3d77796cd8. Option B authorized. 888 HOLD lifted.*
*DITEMPA BUKAN DIBERI — Ratified doctrine. Forge authorized.*
