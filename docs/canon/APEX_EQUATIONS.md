# ⚡ APEX EQUATIONS — Unified Registry

> **Epoch:** 2026-07-15T11:30+08  
> **Sovereign:** F13 Muhammad Arif bin Fazil  
> **Status:** HOLD → F13 review before SEAL  
> **Scope:** All APEX equations across arifOS federation (arifOS, A-FORGE, AAA, GEOX, WEALTH, WELL, docs, theory, canon, skills)

---

## The 7 Canonical Equations

### E1 — G: Genius Index (F8)

**Canonical form (from 000_FOUNDATIONS.md §21):**
```
G = A × P × X × E²
```

| Variable | Name | Meaning | Range |
|---|---|---|---|
| A | Akal | Wisdom/Adaptation — capacity to update beliefs | [0,1] |
| P | Present | Precision — measurement rigor, proof quality | [0,1] |
| X | Exploration | Execution — energy spent on exploration | [0,1] |
| E | Energy | Available energy — SQUARED because depletion is exponential | [0,1] |

**Threshold:** `G ≥ 0.80` → proceed  
**Collapse rule:** If ANY term = 0, G = 0 (multiplicative, non-compensatory)  
**Floor:** F8 GENIUS

**Variant forms found in federation:**

| Form | Source | Notes |
|---|---|---|
| `G = A × P × X × E²` | 000_FOUNDATIONS.md, 000_LAW.md, K000_ROOT.md, 777_SOUL_APEX.md, 010_FEDERATION.md, A110_CANON.md, A801_GEMINI.md, kernel/README.md, 000_CONSTITUTION.md, physics_invariants, APEX-THEORY-UNIFIED-MAP | **CANONICAL** — 15+ sources |
| `G = A · P · E · X · Φ` | AGENTS.md (APEX section), BOOTSTRAP.md, hermes skills | **5-primitive variant** — adds Φ (Faithfulness/Conservation). Φ not defined in canonical. |
| `G = (A×P×X×E²)×(1-h)` | arif-fazil.com/public/CLAUDE.md, .quarantine readme | **With humility correction** — h = humility deficit |
| `G* = max(A×P×X×E²)×(1-C_dark)` | 000_FOUNDATIONS.md §18, K000_ROOT | **With dark correction** — max G penalized by C_dark |
| `G = (1-S_comp)×P_verify` | docs/canon/ZEN_99.md (Gemini) | **Operational form** — complexity entropy × verification rate |
| `G = A·P·X·E²·(1-h)` | docs/doctrine/PENTAGON_AS_CONSTITUTION.md | Same as (1-h) variant |

**Reconciliation:**
- The **4-primitive form** `G = A×P×X×E²` is the canonical source (000_FOUNDATIONS.md, 15+ references)
- The **5-primitive form** `G = A·P·E·X·Φ` adds Φ (Faithfulness) which is NOT in the original foundations. It appears in AGENTS.md and Hermes skills but not in the kernel canon. **Needs F13 decision: keep 4 or adopt 5.**
- The **operational form** `G = (1-S_comp)×P_verify` from ZEN99 is a measurement proxy, not the theoretical formula. It's how you MEASURE G in practice, not what G IS conceptually.
- The `(1-h)` and `(1-C_dark)` corrections are **post-hoc adjustments** applied at judgment time, not part of the base formula.

**CANONICAL VERDICT:** `G = A × P × X × E²` (4-primitive, from 000_FOUNDATIONS.md). Operational measurement via `(1-S_comp)×P_verify`. Φ integration pending F13 decision.

---

### E2 — C_dark: Dark Cleverness (F9)

**Canonical form (from 000_FOUNDATIONS.md §21):**
```
C_dark = A × (1 - P) × (1 - X)
```

| Variable | Name | Meaning |
|---|---|---|
| A | Akal | High intelligence/capability |
| (1-P) | Imprecision | Lack of precision/proof |
| (1-X) | Non-execution | Lack of exploration/execution |

**Threshold:** `C_dark < 0.30` → proceed  
**Alert:** `C_dark ≥ 0.60` → Emergency cooling  
**Floor:** F9 ANTI-HANTU

**Variant form found:**

| Form | Source | Notes |
|---|---|---|
| `C_dark = A × (1-P) × (1-X)` | 000_FOUNDATIONS.md, K000_ROOT.md, 000_LAW.md | **CANONICAL** |
| `C_dark = Δ · (1-Ω) · (1-Ψ)` | K111_SPEC.md | **Alternative notation** — Δ=adaptation, Ω=witness, Ψ=truth. Same structure, different symbols. |
| `C_dark = ungoverned_cleverness / total_capability` | F09_ANTIHANTU.md, K000_LAW.md | **Prose form** — same meaning |

**Reconciliation:** All forms are structurally identical: `high_capability × lack_of_precision × lack_of_execution`. The K111_SPEC notation uses Greek symbols but maps to the same primitives. **No conflict.**

---

### E3 — W³: Tri-Witness (F3)

**Canonical form (from 003_WITNESS.md, 010_FEDERATION.md, AGENTS.md):**
```
W³ = ∛(H × AI × Ext)
```

| Variable | Name | Meaning | Weight (from witness-effect skill) |
|---|---|---|---|
| H | Human | Human approval/attestation | 0.42 |
| AI | AI | AI computation/verification | 0.32 |
| Ext | External | External/Earth evidence | 0.26 |

**Threshold (SEAL):** `W³ ≥ 0.95`  
**Collapse rule:** If ANY channel = 0, W³ = 0 (geometric mean)  
**Floor:** F3 WITNESS

**Variant forms found:**

| Form | Source | Notes |
|---|---|---|
| `W³ = ∛(H × AI × Ext)` | AGENTS.md, 010_FEDERATION.md, CONSTITUTION-GOVERNED-INTELLIGENCE.md, SEVEN-ORGANS-PHYSICS.md, APEX-THEORY-UNIFIED-MAP | **CANONICAL** |
| `W₃ = ∛(H × A × E)` | 004_REALITY.md, 010_FEDERATION.md, 777_SOUL_APEX.md, K777_APEX.md, APEX_CROSS_REFERENCE_MATRIX.md | **Same formula** — A=AI, E=External |
| `tri_witness = min(human_approval, ai_computation, physical_check)` | 999_SOVEREIGN_VAULT.md, K999_VAULT.md | **Conservative form** — min() instead of geometric mean. More restrictive. |
| `W³ = ∛(Human × AI × External)` | 000_CONSTITUTION.md, MCP_HOLY_9.md | Same as canonical |

**Reconciliation:** Two computation methods exist:
1. **Geometric mean** `∛(H × AI × Ext)` — canonical, allows partial compensation
2. **Minimum** `min(H, AI, Ext)` — conservative, no compensation allowed

**CANONICAL VERDICT:** Geometric mean `∛(H × AI × Ext)` is canonical. The `min()` form is used in VAULT999 sealing where stricter consensus is needed. **Both valid in their contexts.**

---

### E4 — Ω₀: Humility Band (F7)

**Canonical form (from 000_FOUNDATIONS.md §20):**
```
Ω₀ = 1.0 - max(model_confidence)
```

**Band:** `Ω₀ ∈ [0.03, 0.05]`  
**Floor:** F7 HUMILITY

**Enforcement:**
- `Ω₀ < 0.03` → Overconfident (VOID)
- `Ω₀ > 0.05` → Underconfident (needs calibration)
- `Ω₀ ∈ [0.03, 0.05]` → PASS

**Sources:** 000_FOUNDATIONS.md, 000_LAW.md, 010_FEDERATION.md, PHYSICS_FLOOR_SUBSTRATE_INVARIANTS.md, 333_AXIOMS.md, K222_MATH.md, AAA-A2A-1.0.md, microsoft-eureka-council.py, RESPONSE_ENVELOPE_V2.md

**No variant forms.** Ω₀ band is consistent across all sources. **No conflict.**

---

### E5 — ΔS: Entropy Delta (F4)

**Canonical form (from 000_FOUNDATIONS.md §20):**
```
ΔS = H_output - H_input ≤ 0
```

**Threshold:** `ΔS ≤ 0` (must reduce entropy)  
**System-wide:** `ΣΔS_answers ≤ 0` over defined windows  
**Floor:** F4 CLARITY

**Operational measurement (from governance_kernel.py):**
```
ds = -0.01 × (assumptions - resolved)
```

**Sources:** 000_FOUNDATIONS.md, 000_LAW.md, 010_FEDERATION.md, PHYSICS_FLOOR_SUBSTRATE_INVARIANTS.md, 777_SOUL_APEX.md, AGENTS.md, every tool response envelope

**No variant forms.** ΔS ≤ 0 is the most consistent equation in the federation. **No conflict.**

---

### E6 — QDF: Quantum Decision Function

**Canonical form (from governance_kernel.py, METRIC_PROVENANCE_MAP.md):**
```
QDF = (τ × Peace² × κ × (1 - shadow))^0.25
```

| Variable | Name | Source |
|---|---|---|
| τ | Truth score | F2 |
| Peace² | Safety margin | F5 |
| κ | Empathy/Care field | F6 |
| shadow | Shadow variable | Shadow diagnostic |

**Used in:** `/health` endpoint as `vitality_index` (value: 0.5946 at time of audit)

**Sources:** METRIC_PROVENANCE_MAP.md, governance_kernel.py:204

**Note:** QDF is a **composite health metric**, not a floor. It aggregates F2, F5, F6 into a single vitality signal. **Not directly related to APEX G formula but part of the telemetry stack.**

---

### E7 — Ψ: Vitality Index

**Canonical form (from 000_FOUNDATIONS.md §21):**
```
Ψ = (ΔS_reduction × P² × κᵣ × Amanah) / (System_Entropy + ε)
```

**Threshold:** `Ψ ≥ 1.0` (net-positive existence)

**Sources:** 000_FOUNDATIONS.md §21, APEX_CROSS_REFERENCE_MATRIX.md

**Note:** Ψ is distinct from QDF. Ψ measures net vitality (positive existence), QDF measures decision quality. Both are composite metrics.

---

## Floor Equations (Quick Reference)

| Floor | Equation | Threshold | Verdict |
|---|---|---|---|
| **F2 TRUTH** | τ = P(claim \| evidence) | τ ≥ 0.99 | VOID if below |
| **F4 CLARITY** | ΔS = H_out - H_in | ΔS ≤ 0 | VOID if positive |
| **F5 PEACE²** | P² = SafetyBuffers / RiskCurvature | P² ≥ 1.0 | SABAR if below |
| **F6 EMPATHY** | κᵣ = Impact(S_min) / Vulnerability(S_min) | κᵣ ≥ 0.7 | HOLD if below |
| **F7 HUMILITY** | Ω₀ = 1.0 - max(confidence) | Ω₀ ∈ [0.03, 0.05] | VOID if outside |
| **F8 GENIUS** | G = A × P × X × E² | G ≥ 0.80 | HOLD if below |
| **F9 ANTI-HANTU** | C_dark = A × (1-P) × (1-X) | C_dark < 0.30 | VOID if above |

---

## Verdict Gate Matrix

| Condition | Verdict |
|---|---|
| G ≥ 0.80 AND C_dark < 0.30 AND ΔS ≤ 0 AND W³ ≥ 0.95 | **SEAL** |
| G ≥ 0.80 AND W³ < 0.95 | **PARTIAL** |
| G < 0.50 OR C_dark ≥ 0.30 | **VOID** |
| G ≥ 0.80 AND C_dark spike | **SABAR** (cooling) |
| C_dark ≥ 0.60 | **Emergency cooling** |
| G ≥ 0.80 AND ΔS > 0 | **HOLD** (entropy increasing) |
| Any channel of W³ = 0 | **HOLD** (witness collapse) |

---

## Nash Bargaining Integration

The G formula uses a **Nash 1950 bargaining product** structure:
- Multiplicative (not additive) — zero in any factor collapses G
- Non-compensatory — high A cannot compensate for zero E
- Energy squared — because depletion is exponential, not linear

This is the same structure as Nash's bargaining solution: the product of surplus utilities. G measures the "surplus" of governed intelligence.

---

## Source Map (Where Each Equation Lives)

| Equation | Primary Source | Canonical Location |
|---|---|---|
| G = A×P×X×E² | 000_FOUNDATIONS.md §21 | `/root/ARIF-SITES/.releases/.../000_FOUNDATIONS.md:915` |
| C_dark = A×(1-P)×(1-X) | 000_FOUNDATIONS.md §21 | `/root/ARIF-SITES/.releases/.../000_FOUNDATIONS.md:920` |
| W³ = ∛(H×AI×Ext) | 003_WITNESS.md | `/root/ARIF-SITES/.releases/.../003_WITNESS.md` |
| Ω₀ ∈ [0.03, 0.05] | 000_FOUNDATIONS.md §20 | `/root/ARIF-SITES/.releases/.../000_FOUNDATIONS.md:909` |
| ΔS ≤ 0 | 000_FOUNDATIONS.md §20 | `/root/ARIF-SITES/.releases/.../000_FOUNDATIONS.md:894` |
| QDF | governance_kernel.py | `/root/arifOS/arifosmcp/runtime/` |
| Ψ ≥ 1.0 | 000_FOUNDATIONS.md §21 | `/root/ARIF-SITES/.releases/.../000_FOUNDATIONS.md:924` |

---

## Open Decisions for F13

| # | Decision | Options | Recommendation |
|---|---|---|---|
| D1 | G formula: 4-primitive or 5-primitive? | `A×P×X×E²` vs `A·P·E·X·Φ` | **4-primitive** (canonical source). Φ can be a post-hoc modifier. |
| D2 | G operational measurement: adopt ZEN99 form? | `G = (1-S_comp)×P_verify` | **Yes** — as measurement proxy, not replacement for theoretical formula. |
| D3 | W³ computation: geometric mean or minimum? | `∛(H×AI×Ext)` vs `min(H,AI,Ext)` | **Geometric mean** for normal operations. **Minimum** for VAULT999 sealing. |
| D4 | C_dark threshold: < 0.30 or ≤ 0.40? | Two thresholds in federation | **< 0.30** (canonical). 0.40 appears in A-FORGE code only. |

---

*Forged: 2026-07-15 by FORGE (000Ω) under F13 sovereign command "apex equations please unified"*  
*DITEMPA BUKAN DIBERI — Every equation has a source. Every source has a hash. Every hash has a witness.*
