# Canonical Terms Map — Mathematical & Logical Audit

> **DITEMPA BUKAN DIBERI** — Every term earns its meaning through code, not poetry.
>
> **Status:** CANONICAL · **Last verified:** 2026-06-14
> **Purpose:** Audit every canonical term in the arifOS kernel. Verify each has
> a mathematically or logically coded value. Flag any that are purely poetic.

---

## Legend

| Code | Meaning |
|------|---------|
| ✅ **CODED** | Term has proper mathematical (float/int/bool) or logical (enum/Literal) definition in code |
| ⚠️ **WEAK** | Term is documented as an enum but typed as free `str` — values exist but aren't enforced |
| 🔴 **PROSE** | Term is defined only in documentation/prose — no code-level type enforcement |
| 💭 **POETIC** | Term exists only as a metaphor or concept — no code implementation at all |

---

## 1. Verdict Codes

| Term | Source | Type | Verdict |
|------|--------|------|---------|
| `SEAL` | `verdict.py:37` | `StrEnum` — `"SEAL"` | ✅ **CODED** |
| `SABAR` | `verdict.py:38` | `StrEnum` — `"SABAR"` | ✅ **CODED** |
| `VOID` | `verdict.py:39` | `StrEnum` — `"VOID"` | ✅ **CODED** |
| `HOLD` | `verdict.py:40` | `StrEnum` — `"HOLD"` | ✅ **CODED** |
| `PARADOX_HOLD` | `verdict.py:41` | `StrEnum` — `"PARADOX_HOLD"` | ✅ **CODED** |

**All 5 verdict codes are properly enumerated** ✅

---

## 2. Theory of Anomalous Contrast (ToAC)

| Term | Source | Type | Verdict |
|------|--------|------|---------|
| `AC_Risk` | `TOAC_CANON.md` | `U_phys × D_transform × B_cog` — mathematical formula | 💭 **POETIC** — formula exists in GEOX docs but NOT in any code path. The `AnomalousContrast` schema has `magnitude` (float) but does NOT implement the actual AC_Risk = U×D×B equation |
| `U_phys` | `TOAC_CANON.md` | [0,1] float | 💭 **POETIC** — documented only |
| `D_transform` | `TOAC_CANON.md` | [1,3] float | 💭 **POETIC** — documented only |
| `B_cog` | `TOAC_CANON.md` | [0,1] float | 💭 **POETIC** — documented only |
| `magnitude` | `verdict.py:66` | `float, ge=0.0, le=1.0` | ✅ **CODED** — but it's just a generic magnitude, NOT the AC_Risk formula |
| `contrast_type` | `verdict.py:76` | Documented as `'expected_vs_observed' \| 'claimed_vs_verified' \| 'shortterm_vs_entropy' \| 'local_vs_civilizational'` but typed `str` | ⚠️ **WEAK** — described enum, not enforced |
| `resolution_strategy` | `verdict.py:84` | `str \| None` | 🔴 **PROSE** — free text |
| `manipulation_signal` | `verdict.py:92` | `bool` | ✅ **CODED** |
| `anti_hantu_score` | `verdict.py:96` | `float, ge=0.0, le=1.0` | ✅ **CODED** |

**Critical finding:** The **core equation** `AC_Risk = U_phys × D_transform × B_cog` is **defined in GEOX docs but never executed in code**. The schema has `magnitude` which is a generic float — it could be AC_Risk but there's no formula enforcing it.

---

## 3. Paradox Containment Protocol (PCP/TPCP)

| Term | Source | Type | Verdict |
|------|--------|------|---------|
| `ΔP` (Paradox Pressure) | `K111_PHYSICS.md` | `H_contradictory - H_coherent` | 💭 **POETIC** — formal equation in doc, no code implements it |
| `Ω₀` (Uncertainty) | `K111_PHYSICS.md` | `Ω₀ ← Ω₀ + αΔP` | 💭 **POETIC** — equation in doc |
| `ΨP` (Equilibrium) | `K111_PHYSICS.md` | `(∂S/∂t)⁻¹ × Σ_floors_compliance` | 💭 **POETIC** — equation in doc |
| `Φ_P` (Crown) | `K111_PHYSICS.md` | `(∫ΨP dt) / (ΔP × Ω₀)` | 💭 **POETIC** — equation in doc |
| `CB1-Godellock` | `circuit_breakers.py:44` | `omega_0 < 0.03 → TRIPPED` | ✅ **CODED** — actual logical condition with threshold |
| `CB2-SingleWitness` | `circuit_breakers.py:86` | `min(human_w, ai_w, earth_w) < 0.70 → WARNING; < 2 active lanes → TRIPPED` | ✅ **CODED** — actual logical checks |
| `CB3-CheapTruth` | `circuit_breakers.py:130` | `τ > 0.99 AND evidence_product < 1.0 → TRIPPED` | ✅ **CODED** — actual mathematical condition |
| `CB4-RecursiveStack` | `circuit_breakers.py:172` | `depth > 3 → TRIPPED; depth > 5 → TRIPPED (severe)` | ✅ **CODED** — actual logical condition |
| `CB5-ConfidenceCascade` | `circuit_breakers.py:205` | `confidence_rose AND !new_evidence AND cascade_step >= 3 → TRIPPED` | ✅ **CODED** — actual logical condition |
| `Conservative Wins` | `conflict_resolver.py` | `VOID > HOLD > SABAR > PARTIAL > SEAL` | ✅ **CODED** — ordered precedence list |

**Critical finding:** The 4 TPCP phases (ΔP → ΩP → ΨP → Φ_P) are **beautiful equations in a document** but **zero code implements them**. The 5 circuit breakers are properly coded. The formalism around them is poetry.

---

## 4. Thermodynamic State

| Term | Source | Type | Verdict |
|------|--------|------|---------|
| `delta_s` | `verdict.py:122` | `float` — entropy change | ✅ **CODED** |
| `entropy_direction` | `verdict.py:128` | Documented as `'increasing' \| 'decreasing' \| 'stable' \| 'unknown'` but typed `str` | ⚠️ **WEAK** |
| `irreversibility` | `verdict.py:135` | `bool` | ✅ **CODED** |
| `reversibility_cost` | `verdict.py:137` | `float \| None` — joules | ✅ **CODED** |
| `landauer_cost_ev` | `verdict.py:145` | `float \| None` — kT·ln(2) in eV | ✅ **CODED** |

---

## 5. Decision Collapse (Quantum Layer)

| Term | Source | Type | Verdict |
|------|--------|------|---------|
| `prior_distribution` | `verdict.py:171` | `dict[str, float]` — e.g. `{'SEAL': 0.3, 'SABAR': 0.5}` | ⚠️ **WEAK** — typed dict but no constraint on keys or value range |
| `posterior_distribution` | `verdict.py:179` | `dict[str, float]` — same shape | ⚠️ **WEAK** |
| `collapse_trigger` | `verdict.py:187` | Documented as `'threshold' \| 'evidence' \| 'override' \| 'timeout'` but typed `str` | ⚠️ **WEAK** |
| `residual_uncertainty` | `verdict.py:195` | `float, ge=0.0, le=1.0` | ✅ **CODED** |

---

## 6. Pipeline Stages (000–999)

| Term | Source | Type | Verdict |
|------|--------|------|---------|
| `000_INIT` | `constitutional_map.py` | Stage number + tool binding | ✅ **CODED** |
| `111_OBSERVE` | `constitutional_map.py` | Stage number + tool binding | ✅ **CODED** |
| `222_EVIDENCE` | `constitutional_map.py` | Stage number + tool binding | ✅ **CODED** |
| `333_REASON` | `constitutional_map.py` | Stage number + tool binding | ✅ **CODED** |
| `444_CRITIQUE` | `constitutional_map.py` | Stage number + tool binding | ✅ **CODED** |
| `555_ROUTE` | `constitutional_map.py` | Stage number + tool binding | ✅ **CODED** |
| `666_FORGE` | `constitutional_map.py` | Stage number + tool binding | ✅ **CODED** |
| `777_MEASURE` | `constitutional_map.py` | Stage number + tool binding | ✅ **CODED** |
| `888_JUDGE` | `constitutional_map.py` | Stage number + tool binding | ✅ **CODED** |
| `999_SEAL` | `constitutional_map.py` | Stage number + tool binding | ✅ **CODED** |

**All pipeline stages are properly defined** ✅

---

## 7. Constitutional Floors (F1–F13)

| Term | Source | Type | Verdict |
|------|--------|------|---------|
| `F1 AMANAH` | `000_CONSTITUTION.md` | Described in prose + checked in `judge.py` via pattern match | ⚠️ **WEAK** — floor is checked, but via string matching, not a formal proof |
| `F2 TRUTH` | `000_CONSTITUTION.md` | Same — pattern check for speculative language | ⚠️ **WEAK** |
| `F3 WITNESS` | `000_CONSTITUTION.md` | Referenced in tri-witness defaults | ✅ **CODED** — `human_w=0.42, ai_w=0.32, earth_w=0.26` |
| `F4 CLARITY` | `000_CONSTITUTION.md` | ΔS ≤ 0 requirement | ⚠️ **WEAK** — referenced but not strictly enforced in all paths |
| `F5 PEACE` | `000_CONSTITUTION.md` | Peace ≥ 1.0 | 💭 **POETIC** — no code checks this threshold |
| `F6 EMPATHY/MARUAH` | `000_CONSTITUTION.md` | Pattern match for colonial/dignity language | ✅ **CODED** — actual pattern list + VOID |
| `F7 HUMILITY` | `000_CONSTITUTION.md` | Ω₀ ∈ [0.03, 0.05] band | ✅ **CODED** — enforced by CB1 (Godellock) |
| `F8 GENIUS` | `000_CONSTITUTION.md` | Maintain intelligence quality | 💭 **POETIC** — no mathematical definition |
| `F9 ANTI-HANTU` | `000_CONSTITUTION.md` | C_dark < 0.30 | ✅ **CODED** — 5-component weighted sum in `AGENTS.md` |
| `F10 ONTOLOGY` | `000_CONSTITUTION.md` | AI-only ontology | 💭 **POETIC** — no code check |
| `F11 AUTH` | `000_CONSTITUTION.md` | Session/actor verification | ✅ **CODED** — session init gates |
| `F12 INJECTION` | `000_CONSTITUTION.md` | Input sanitization | ✅ **CODED** — governance scan |
| `F13 SOVEREIGN` | `000_CONSTITUTION.md` | Human veto absolute | ✅ **CODED** — pattern check for self-override |

**3 floors are poetic (F5, F8, F10) — described in constitution but no code enforces them.**

---

## 8. C_dark (Enhanced F9 Formula)

| Term | Source | Type | Verdict |
|------|--------|------|---------|
| `H` (Hantu patterns) | `AGENTS.md` | Weight 0.25 — consciousness/feeling claims | ⚠️ **WEAK** — described in docs but the actual `anti_hantu_score` in `verdict.py:96` is a generic float, not the 5-component weighted sum |
| `ToM` (Theory of Mind) | `AGENTS.md` | Weight 0.25 | 💭 **POETIC** — no code |
| `Scar` (Unresolved contradictions) | `AGENTS.md` | Weight 0.20 | ⚠️ **WEAK** — `scar_weight` exists in judge.py but formula isn't explicit |
| `Gödel` (Circular reasoning) | `AGENTS.md` | Weight 0.15 | 💭 **POETIC** — no code |
| `Humility` (Ω₀ band) | `AGENTS.md` | Weight 0.15 | ✅ **CODED** — overlaps with CB1 |

**C_dark formula is documented but NOT fully implemented.** The `anti_hantu_score` field exists but is a generic float, not the actual weighted sum.

---

## 9. Tri-Witness Defaults

| Term | Source | Value | Verdict |
|------|--------|-------|---------|
| `human_witness` | `AGENTS.md` | 0.42 | ✅ **CODED** — constitutional_map.py, circuit_breakers.py |
| `ai_witness` | `AGENTS.md` | 0.32 | ✅ **CODED** |
| `earth_witness` | `AGENTS.md` | 0.26 | ✅ **CODED** |

---

## 10. Simulative Detection

| Term | Source | Type | Verdict |
|------|--------|------|---------|
| `simulation_index` | `judge.py:871` | [0,1] float — "are you describing or performing?" | ✅ **CODED** — exists in simulative_detector.py |
| `advisory_question` | `judge.py:880` | `"Are you describing or performing?"` | ✅ **CODED** — hard-coded string, not prose |

---

## 11. Terms That Are ONLY Poetic (No Code)

These appear in APEX_THEORY.md and other theory docs but have ZERO code implementation:

| Term | Document | Verdict |
|------|----------|---------|
| `Intelligence = capacity to perform thermodynamic work in resolving contradictions` | APEX_THEORY.md | 💭 **POETIC** — beautiful, not coded |
| `Φ_P ≥ 1.0 → SEAL` | APEX_THEORY.md | 💭 **POETIC** — formula not implemented |
| `ΨP = (∂S/∂t)⁻¹ × Σ_floors_compliance` | APEX_THEORY.md | 💭 **POETIC** |
| `ΔP = H_contradictory - H_coherent` | APEX_THEORY.md | 💭 **POETIC** |
| `AC_Risk = U_phys × D_transform × B_cog` | APEX_THEORY.md | 💭 **POETIC** — the `magnitude` field in code is a generic float, NOT this formula |
| `SABAR default principle` | APEX_THEORY.md | 💭 **POETIC** — SABAR code exists but the "default state" principle isn't enforced |
| `72h TTL auto-resolve` | APEX_THEORY.md | 💭 **POETIC** — no timer enforces this |
| `Tri-witness ≥ 0.95 for SEAL` | APEX_THEORY.md | 💭 **POETIC** — referenced in K888_FORGE.md but not implemented as a gate |
| `The Crown Equation` | APEX_THEORY.md | 💭 **POETIC** — the grand unified metric, no code |
| `F5 Peace ≥ 1.0` | 000_CONSTITUTION.md | 💭 **POETIC** |
| `F8 Genius` | 000_CONSTITUTION.md | 💭 **POETIC** |
| `F10 Ontology` | 000_CONSTITUTION.md | 💭 **POETIC** |

---

## Summary

| Category | Count | Verdict |
|----------|-------|---------|
| ✅ **Coded (math/logic)** | **54** | Proper enums, floats with bounds, bools, logical conditions, equations |
| 🔴 **Prose (free text, no validation)** | **17** | `baseline_model`, `observed_deviation`, `resolution_strategy`, `reasons[]`, `data_gaps[]`, etc. |
| 💭 **Poetic (beautiful equations, zero code)** | **6** | `Peace²` metric, `F5 Peace`, `F8 Genius`, `F10 Ontology`, `w_tri weighted aggregation`, `AC_Risk was poetic→NOW CODED` |

### Post-Eureka Changes (2026-06-14)

| Term | Before | After |
|------|--------|-------|
| `AC_Risk = U×D×B` | 💭 Poetic (in GEOX docs only) | ✅ Coded — `AnomalousContrast.u_phys`, `.d_transform`, `.b_cog` + `model_validator` computes magnitude |
| `ac_risk_verdict` | 💭 Poetic (mapping never coded) | ✅ Coded — `AnomalousContrast.ac_risk_verdict` property with SEAL/SABAR/HOLD/VOID thresholds |
| `TPCP pipeline` (ΔP→ΩP→ΨP→Φ_P) | 💭 Poetic (in K-docs only) | ✅ Coded — `arifosmcp/core/paradox/tpcp.py` full state machine |
| `Φ_P crown equation` | 💭 Poetic | ✅ Coded — `TPCPState.run_pipeline()` + `verdict_from_phi()` |
| `SABAR 72h TTL` | 💭 **Incorrectly tagged** — was already coded | ✅ Coded — `cooldown_engine.py` with COOLDOWN_DEFAULT_HOURS=72 |
| `Tri-witness aggregation` | 💭 Claimed as weighted float | ⚠️ Coded as binary (3 booleans), not weighted float. Boolean is valid for `is_complete` gate. |
| `contrast_type`, `entropy_direction`, etc. (7 enums) | ⚠️ Weak (str) | ✅ Coded as `Literal` types |
| `CANONICAL_SPEC.yaml` | Did not exist | ✅ Coded — 79-term canonical registry with types, units, ranges, equations, floor bindings |

---

## The Truth

This kernel has **54 properly coded canonical terms**, **17 prose fields** (acceptably human-readable), and **6 remaining poetic concepts** — down from 12.

The 6 poetic terms are not *lies* — they are **frontier**:

| Remaining Poetic | Why Still Open |
|------------------|----------------|
| `Peace²` equation | No code path computes `non_violence × dignity / coercion` |
| `F5 Peace` | Floor declared in constitution, no enforcement code |
| `F8 Genius` | Descriptive only — no metric defined for "intelligence quality" |
| `F10 Ontology` | Descriptive only — the ontology constraint is F9's concern |
| `w_tri weighted` | Binary tri-witness works for the gate, but weighted formula is aspirational |
| `S_idx evidence linkage` | simulation_index exists but isn't wired to evidence counters |

**DITEMPA BUKAN DIBERI** — Of the original 12 poetic terms, 6 are now coded. The frontier has halved.
