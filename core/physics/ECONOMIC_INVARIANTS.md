# 12 Economic-Physics Invariants

**Canonical Source:** `core/physics/ECONOMIC_INVARIANTS.md`  
**Version:** 2026.05.11-EMBODY  
**Governance Floor:** F4 (Clarity), F8 (Genius), F1 (Amanah)  
**Organ Binding:** WEALTH (`_5_wealth.py`), APEX (`_3_apex.py`), PHYSICS (`thermodynamics_hardened.py`)

> **THERMODYNAMIC LAWS ARE NOT OPTIONAL.**  
> Economic systems are physical systems with accounting layers.  
> These invariants are enforced, not suggested.

---

## Invariant 1 — Conservation of Allocated Value
**Law:** Value is neither created nor destroyed in a closed economic loop; it is only transformed across states (liquidity, risk, time, information).

**Physics Analogy:** First Law of Thermodynamics (conservation of energy).  
**Economic Expression:** `ΣV_in + ΣV_generated = ΣV_out + ΣV_dissipated + ΣV_locked`  
**Enforcement:** Any NPV calculation that claims ex-nihilo value creation without corresponding risk/entropy transfer receives `VOID`.

---

## Invariant 2 — Entropic Cost of Transaction
**Law:** Every economic exchange increases total systemic entropy. Frictionless markets are a mathematical impossibility.

**Physics Analogy:** Second Law of Thermodynamics.  
**Economic Expression:** `ΔS_transaction ≥ k_B · ln(2)` per bit of price information resolved.  
**Enforcement:** WEALTH organ tags transactions with `entropy_deltas`. Proposals claiming zero transaction cost trigger F4 Clarity breach.

---

## Invariant 3 — Landauer Limit on Information Asymmetry
**Law:** Reducing information asymmetry (price discovery, due diligence, audit) has a minimum thermodynamic cost per bit. "Free" alpha is physically suspect.

**Physics Analogy:** Landauer bound (`E ≥ n·k_B·T·ln(2)`).  
**Economic Expression:** `C_discovery ≥ LANDAUER_MIN · I_bits_resolved`  
**Enforcement:** Stages 222 (EVIDENCE) and 777 (MEASURE) validate that discovery costs are grounded. Suspiciously cheap due diligence → `LandauerError` → `VOID`.

---

## Invariant 4 — Thermodynamic Budget Constraint
**Law:** Every economic agent (sovereign, firm, agent) possesses a finite decision-energy budget. Exhaustion forces `888_HOLD`.

**Physics Analogy:** Heat death / finite free energy in a control volume.  
**Economic Expression:** `ΣE_decisions + ΣE_commitments ≤ Β_session`  
**Enforcement:** `ThermodynamicBudget` in `thermodynamics_hardened.py` tracks consumption. Depletion ratio > 1.0 raises `ThermodynamicExhaustionError`.

---

## Invariant 5 — Scarcity-Abundance Orthogonality
**Law:** Genuine abundance in one economic dimension necessitates scarcity in another. There are no free lunches across the full state-space.

**Physics Analogy:** Uncertainty principle / conjugate variables.  
**Economic Expression:** `Ω_abundance · Ω_scarcity ≥ ℏ_eff` (effective economic uncertainty constant).  
**Enforcement:** APEX Forge Stage 777 tests `scarcity_abundance` pressure. Proposals claiming universal abundance fail `telos_drift` checks.

---

## Invariant 6 — NPV as Entropy Gradient
**Law:** Positive Net Present Value corresponds to negative entropy production (clarity gain) in resource allocation. Negative NPV is heat waste.

**Physics Analogy:** Gibbs free energy (`ΔG = ΔH - TΔS`; profitable when `ΔG < 0`).  
**Economic Expression:** `NPV ∝ -ΔS_allocation` for constant risk-adjusted capital.  
**Enforcement:** WEALTH organ `wealth_npv_reward` binds NPV to `delta_s` in `EconomicEnvelope`. NPV > 0 requires `delta_s < 0`.

---

## Invariant 7 — Mode Collapse in Market Concentration
**Law:** When market participant vectors become parallel (cosine similarity → 1), the system suffers mode collapse—monopoly, cartel, or ideological echo chamber.

**Physics Analogy:** Loss of orthogonality in vector spaces.  
**Economic Expression:** `Ω_ortho = 1 - |cos(θ_market)| < 0.95 → collapse risk`.  
**Enforcement:** APEX checks `vector_orthogonality`. Market structures with `Ω_ortho < 0.95` raise `ModeCollapseError`.

---

## Invariant 8 — Irreversibility of Capital Commitment
**Law:** Sunk costs are thermodynamically irreversible. Once committed, capital cannot be un-burned.

**Physics Analogy:** Arrow of time; entropy increase is irreversible.  
**Economic Expression:** `C_sunk → S_generated ≥ 0` (permanent entropy increase).  
**Enforcement:** F1 Amanah. Any tool proposing irreversible capital destruction requires `ack_irreversible=True`. Without explicit sovereign acknowledgment → `HOLD`.

---

## Invariant 9 — Genius Discipline in Resource Allocation
**Law:** Capital deployment below a genius threshold (`G < 0.80`) is not permitted to receive `SEAL`. Elegance and correctness are mandatory, not decorative.

**Physics Analogy:** Carnot efficiency—no engine can exceed its theoretical maximum.  
**Economic Expression:** `G = G* · η ≥ 0.80` for SEAL eligibility.  
**Enforcement:** APEX Judge Stage 888 calculates `calculate_genius()`. `G < 0.80` downgrades verdict from `SEAL` to `PARTIAL`.

---

## Invariant 10 — Hysteresis of Wealth Accumulation
**Law:** Economic state depends on path history. Two systems with identical current parameters but different histories are not equivalent.

**Physics Analogy:** Magnetic hysteresis; work done along a path is path-dependent.  
**Economic Expression:** `W_path(A→B) ≠ W_path(B→A)`; `∮δW ≠ 0`.  
**Enforcement:** VAULT999 ledger enforces path-dependence. `calculate_genius()` accepts `hysteresis` parameter. Wealth evaluations without historical context receive `QUALIFY`.

---

## Invariant 11 — Speed Limit on Value Transfer
**Law:** No economic signal, arbitrage, or value flow can propagate faster than the system's causal bandwidth. Infinite velocity implies infinite dissipation.

**Physics Analogy:** Finite speed of light / finite thermal conductivity.  
**Economic Expression:** `v_value ≤ c_system = f(computation_ms, consensus_depth, audit_trail_length)`  
**Enforcement:** Stage 777 MEASURE checks `compute_ms` against claimed value resolution. Instantaneous cross-border settlement claims without audit depth → F2 Truth breach.

---

## Invariant 12 — Immutable Ledger Conservation
**Law:** Every economic state transition must leave an append-only, hash-chained trace. Information is never lost; it is only archived.

**Physics Analogy:** Unitary evolution in quantum mechanics; information conservation (black hole paradox resolution).  
**Economic Expression:** `H(VAULT_t) = Hash(VAULT_{t-1} || Payload_t)`; no `DELETE`, no `UPDATE`, only `APPEND`.  
**Enforcement:** VAULT999 organ. Any economic operation not sealed to the ledger within `τ_max` is considered uncommitted and may be rolled back.

---

## Enforcement Matrix

| Invariant | Primary Floor | Physics Module | Wealth Organ | Verdict on Breach |
|-----------|--------------|----------------|--------------|-------------------|
| 1. Conservation of Value | F4 | `thermodynamics_hardened.py` | `wealth_npv_reward` | `VOID` |
| 2. Entropic Cost | F4 | `thermodynamics_hardened.py` | `EconomicEnvelope.delta_s` | `VOID` |
| 3. Landauer Limit | F2/F4 | `check_landauer_bound()` | Due-diligence gate | `VOID` |
| 4. Thermodynamic Budget | F7 | `ThermodynamicBudget` | Session gate | `888_HOLD` |
| 5. Scarcity-Abundance | F8 | — | APEX pressure test | `SABAR` |
| 6. NPV ∝ -ΔS | F4 | `entropy_delta()` | `wealth_npv_reward` | `PARTIAL` |
| 7. Mode Collapse | F8 | `vector_orthogonality()` | Market structure audit | `VOID` |
| 8. Irreversibility | F1 | — | Capital commitment gate | `HOLD` |
| 9. Genius Discipline | F8 | `calculate_genius()` | Allocation SEAL gate | `PARTIAL` |
| 10. Hysteresis | F4 | — | VAULT999 path trace | `QUALIFY` |
| 11. Speed Limit | F2 | `check_landauer_bound()` | Settlement velocity | `SABAR` |
| 12. Ledger Conservation | F3 | VAULT999 | Seal latency gate | `VOID` |

---

## Integration Notes

- These invariants are **not philosophical ornaments**. They bind directly to existing enforcement code.
- WEALTH organ (`_5_wealth.py`) shall expose `economic_invariant_check(invariant_id, payload)` by v2026.05.15.
- APEX Forge environmental pressure classes (stability, adversarial, scarcity/abundance, telos drift) map to Invariants 5, 7, 9, and 10.
- Thermodynamic budget consumption rates in `ThermodynamicBudget` are calibrated against Invariant 4.

**DITEMPA BUKAN DIBERI — Forged, Not Given**
