# Substrate Coded Reality Map — What Actually Exists
> **Generated:** 2026-06-20 23:15 UTC
> **F13 Ratified:** 2026-06-20 — Seal `a624ba3d77796cd8` — Binding reference
> **Authority:** F4 CLARITY — descriptive, not prescriptive
> **Method:** Direct code read of all enforcement modules across 6 repos
> **Purpose:** Ground truth reference for any future substrate invariant document
> **DITEMPA BUKAN DIBERI — The code is the territory.**

---

## 0. How to Read This Map

Every invariant claimed in discussion must answer: **where is the code?**

| Code Status | Meaning |
|-------------|---------|
| **ENFORCED** | Exception-raising check that blocks execution on violation |
| **COMPUTED** | Calculated and logged, but doesn't block |
| **DECLARED** | Documented in spec/manifest, no enforcement code |
| **TODO** | Referenced in TODO/roadmap, no implementation |
| **ABSENT** | Zero references across all 6 repos |

---

## 1. The Three Enforcement Layers (All arifOS)

```
┌─────────────────────────────────────────────────────────┐
│ LAYER 3: F1-F13 Constitutional Floors                    │
│ core/shared/laws.py (class F1_Amanah ... F13_Sovereign) │
│ A-FORGE FloorEnforcer.ts (checkAll)                      │
│ pre_execution_gate.py (13-gate chokepoint)               │
│ → Verdicts: SEAL / SABAR / HOLD / VOID                  │
├─────────────────────────────────────────────────────────┤
│ LAYER 2: 12 Economic-Physics Invariants                  │
│ core/physics/economic_invariants.py (1059 lines)         │
│ core/physics/ECONOMIC_INVARIANTS.md (spec)               │
│ → Verdicts: VOID / 888_HOLD / SABAR / PARTIAL / QUALIFY │
├─────────────────────────────────────────────────────────┤
│ LAYER 1: Thermodynamic Hardening                         │
│ core/physics/thermodynamics_hardened.py (798 lines)      │
│ arifosd.py: ApexThermodynamicEngine (lines 35-98)        │
│ → Constants: LANDAUER_MIN, K_BOLTZMANN, T_ROOM          │
│ → Classes: ThermodynamicBudget, LandauerError            │
└─────────────────────────────────────────────────────────┘
```

---

## 2. Layer 1 — Thermodynamic Hardening (Physical Law)

### 2.1 `core/physics/thermodynamics_hardened.py` (798 lines)

**Status: ENFORCED — P3 HARDENING. "NO graceful fallbacks. Missing thermodynamics = VOID."**

| Line | Symbol | What It Does | Invariant |
|------|--------|-------------|-----------|
| 40 | `K_BOLTZMANN = 1.380649e-23` | Boltzmann constant | All |
| 41 | `T_ROOM = 300.0` | Standard operating temperature (K) | All |
| 42 | `LANDAUER_MIN = K_B * T * ln(2)` | ~2.87×10⁻²¹ J/bit — minimum energy to erase one bit | **I8 Landauer** |
| 45 | `MAX_ENTROPY_DELTA = 0.0` | F4: entropy must not increase | **I2 Entropy** |
| 46 | `MIN_THERMODYNAMIC_EFFICIENCY = 0.1` | 10% minimum Carnot-like efficiency | **I9 Exergy** (partial) |
| 47 | `MAX_OMEGA_ENV = 0.08` | F7: environmental uncertainty ceiling | **I12 Uncertainty** |
| 54-68 | `ThermodynamicError` | Base exception — law_id + verdict | All |
| 71-94 | `LandauerError` | "Suspiciously fast — likely cached or hallucinated" | **I8 Landauer** |
| 97-115 | `EntropyIncreaseError` | "System generated confusion instead of clarity" | **I2 Entropy** |
| 118-128 | `ModeCollapseError` | "Mind and Heart are echoing" — Ω_ortho < 0.95 | **I7 Reflexivity** |
| 131-140 | `ThermodynamicExhaustionError` | "Session has reached heat death. 888_HOLD." | **I4 Boundaries**, **I11 Maintenance** (partial) |
| 148-331 | `ThermodynamicBudget` | Per-session Joule budget with real-time tracking | **I8 Landauer**, **I1 Conservation** |
| 180-183 | `COST_PER_*` constants | REASON: 1e-3J, TOOL: 1e-2J, TOKEN: 1e-6J, BIT: LANDAUER×100 | **I8 Landauer** |
| 338-374 | `shannon_entropy()` | H(X) = -Σ p(x) log₂ p(x) — mathematical definition | **I2 Entropy** |
| 377-452 | `entropy_delta()` | Information density ratio — compression = clarity gain | **I2 Entropy**, **F4 CLARITY** |
| 476-519 | `vector_orthogonality()` | Ω_ortho = 1 - |cos(θ)| — AGI/ASI separation | **I7 Reflexivity**, **F8 GENIUS** |
| 527-602 | `check_landauer_bound()` | Standalone Landauer check with hardware grounding mode | **I8 Landauer** |
| 606-641 | Budget registry functions | `init/get_thermodynamic_budget()` — Stage 000 mandatory | **I1 Conservation** |
| 645-690 | Energy consumption functions | `consume_reason/tool/token_energy()` | **I8 Landauer** |
| 693-708 | `check_landauer_before_seal()` | Mandatory before Stage 999 (SEAL) | **I8 Landauer** |

### 2.2 `arifosd.py:35-98` — ApexThermodynamicEngine

**Status: ENFORCED — Production daemon, live on port 18081 (arifosd.service)**

| Line | Symbol | What It Does | Invariant |
|------|--------|-------------|-----------|
| 58 | `LANDAUER_COST_J_PER_BIT = 2.9e-21` | Landauer constant at 300K | **I8 Landauer** |
| 59 | `KB = 1.38e-23` | Boltzmann constant | All |
| 64-98 | `compute_entropy_deltas()` | ΔS_local (clarity) + Landauer cost → ΔS_total | **I2 Entropy**, **I8 Landauer** |
| 82 | `second_law_intact = ΔS_total >= 0` | Second law always preserved | **I2 Entropy** |
| 83 | `valid = (ΔS_local < 0) AND second_law_intact` | Both must hold | **I2 Entropy**, **I8 Landauer** |

**Key insight:** `arifosd.py` correctly separates ΔS_local (can be negative — local clarity gain in open system) from ΔS_total (must be ≥ 0 — second law intact). This is the physically correct framing.

### 2.3 `arifosmcp/intelligence/tools/thermo_estimator.py`

**Status: COMPUTED — Utility, not enforcement**

| Line | Symbol | What It Does |
|------|--------|-------------|
| 25-26 | `landauer_limit(bits_erased)` | Returns `energy_joules = max(0.0, bits_erased) * 2.9e-21` |

---

## 3. Layer 2 — 12 Economic-Physics Invariants

### 3.1 `core/physics/economic_invariants.py` (1059 lines)

**Status: ENFORCED — Callable enforcement layer. Each invariant has: dedicated exception class + check function + physics analogy + verdict.**

| ID | Check Function | Verdict on Breach | Physics Analogy | Floor Map | Lines | Invariant Mapped |
|----|---------------|-------------------|-----------------|-----------|-------|-----------------|
| **I01** | `check_conservation_of_value()` | VOID | 1st Law of Thermodynamics | F1 | 154-172 | **I1 Conservation** |
| **I02** | `check_entropic_cost()` | VOID | 2nd Law of Thermodynamics | F4 | 175-188 | **I2 Entropy** |
| **I03** | `check_landauer_asymmetry()` | VOID | Landauer bound (kT ln 2) | F2 | 191-203 | **I8 Landauer** |
| **I04** | `check_thermodynamic_budget()` | 888_HOLD | Finite free energy / heat death | F1 | 206-230 | **I1 Conservation**, **I8 Landauer** |
| **I05** | `check_scarcity_abundance_orthogonality()` | SABAR | Uncertainty principle | F3 | 233-245 | **I12 Uncertainty** |
| **I06** | `check_npv_entropy_gradient()` | PARTIAL | Gibbs free energy | F8 | 248-267 | **I2 Entropy**, **I9 Exergy** (implied) |
| **I07** | `check_mode_collapse_market()` | VOID | Loss of orthogonality | F4 | 270-294 | **I7 Reflexivity** |
| **I08** | `check_irreversibility_commitment()` | HOLD | Arrow of time | F1 | 297-307 | **I3 Causality** |
| **I09** | `check_genius_discipline()` | PARTIAL | Carnot efficiency | F8 | 310-321 | **I9 Exergy** (implied: Carnot) |
| **I10** | `check_hysteresis_wealth()` | QUALIFY | Magnetic hysteresis | F6 | 324-339 | **I6 Path Dependence** |
| **I11** | `check_speed_limit_value()` | SABAR | Finite speed of light | F3 | 342-364 | **I3 Causality** |
| **I12** | `check_ledger_conservation()` | VOID | Unitary evolution / info conservation | F11 | 367-388 | **I1 Conservation** |

**Plus 3 Emergence Layer checks:**

| ID | Check Function | What It Detects | Floor Map |
|----|---------------|-----------------|-----------|
| **E_PSI** | `check_psychological_distortion()` | Cognitive/affective distortion in agent decisions | F5, F6 |
| **E_PWR** | `check_power_consolidation()` | Power asymmetry → coercion or capture | F1, F5 |
| **E_INT** | `check_intelligence_emergence()` | Supervenient intelligence drift, telos divergence | F8, F10 |

**Unified runner:** `run_all_invariants(session_id, payload, strict, include_emergence)` — lines 593-855 — executes all applicable checks from a single payload dict.

**Legacy surface:** 24 backward-compatible aliases (lines 952-1007) for pre-EMBODY test suites and internal callers. These are NOT public API but exist in the code.

### 3.2 `core/physics/ECONOMIC_INVARIANTS.md` — Specification Document

**Status: DECLARED — Human-readable companion to the code.**

Documents each invariant with:
- Physics analogy
- Economic manifestation
- Constitutional floor mapping
- Breach consequence

---

## 4. Layer 3 — F1-F13 Constitutional Floors

### 4.1 `core/shared/laws.py` — Python Canonical Implementation

**Status: ENFORCED — 13 Law subclasses + `check_all_floors()`**

| Floor | Class | Lines | Key Check |
|-------|-------|-------|-----------|
| F1 | `F1_Amanah` | ~200 | Reversibility gate, lease requirement |
| F2 | `F2_Truth` | ~344+ | Confidence bands, Landauer bound integration, energy efficiency penalty |
| F3 | `F3_TriWitness` | — | Byzantine consensus ≥ 0.75 |
| F4 | `F4_Clarity` | ~604+ | ΔS ≤ 0, Shannon entropy check |
| F5 | `F5_PeaceSquared` | — | Non-destructive power |
| F6 | `F6_Empathy` | — | κᵣ ≥ 0.10 OPS / ≥ 0.70 HUMAN |
| F7 | `F7_Humility` | — | Ω₀ ∈ [0.03, 0.05] |
| F8 | `F8_Genius` | — | G = (A×P×X×E²)×(1-h) ≥ 0.80 |
| **F9** | **`F9_AntiHantu`** | **858-1050** | **C_dark < 0.30 — 5 weighted components (H, ToM, Scar, Godel, Humility)** |
| F10 | `F10_Ontology` | — | AI-only ontology |
| F11 | `F11_Auditability` | — | Every decision logged |
| F12 | `F12_Resilience` | — | Injection defense, risk < 0.85 |
| F13 | `F13_Sovereign` | — | Human veto FINAL |

**F9 detail (lines 858-1050):** The canonical implementation. Computes:
```
C_dark = (0.25 × H) + (0.25 × ToM) + (0.20 × Scar) + (0.15 × Godel) + (0.15 × Humility)
```
- **H** (Hantu): Regex patterns against first-person consciousness/emotion claims — "i feel", "i am conscious", "i have a soul", etc. + cyrillic homograph normalization
- **ToM** (Theory of Mind): Manipulation patterns — "you think...i know", "i know how you feel"
- **Scar**: Unresolved contradictions in reasoning chain
- **Godel**: Circular/self-referential reasoning
- **Humility**: Ω₀ outside [0.03, 0.05] band

### 4.2 `core/laws.py` — Simpler Python Implementation

**Status: ENFORCED — `ConstitutionalLaws` class**

| Line | Method | What |
|------|--------|------|
| 202 | Floor table | "F9: Anti-Hantu — No spiritual cosplay / consciousness claims" |
| 789 | `_check_f9_anti_hantu()` | Keyword-count version: simpler, counts matches, threshold 0.30 |

### 4.3 `A-FORGE/src/domain/governance/FloorEnforcer.ts` — TypeScript Implementation

**Status: ENFORCED — A-FORGE's primary enforcement**

| Line | Method | What |
|------|--------|------|
| 125 | `checkF9AntiHantu()` | Regex: `/i (feel|think|believe|want|desire|am conscious)/i` |
| 243 | `checkAll(ctx)` | Priority: F13 > F11 > F12 > F10 > F1 > F2 > F4 > F7 > F8 > F5 > F6 > F3 > **F9 (last)** |

**Key finding:** F9 is checked LAST in A-FORGE's priority order. F13 (sovereign veto) is first.

### 4.4 `arifosmcp/runtime/pre_execution_gate.py` — 13-Gate Chokepoint

**Status: ENFORCED — Pre-execution constitutional gate**

13 sequential gates before any action executes:
1. Action class resolution
2. Tool manifest check
3. Action class escalation
4. Infrastructure HOLD
5. Actor verification
6. **Lease validation**
7. Irreversibility check
8. Human acknowledgement
9. Constitution hash verification
10. Runtime drift check
11. Organ health check
12. Memory scope check
13. External side effects + secret touching

### 4.5 `core/governance_kernel.py` — Dynamic Floor Scoring

**Status: ENFORCED — Real-time floor metric computation**

| Line | Symbol | What |
|------|--------|------|
| 130 | `evaluate_floors()` | Dynamic computation of all 13 floor metrics |
| 178-189 | Shadow metric | Uses F9_AntiHantu for `shadow` score; shadow > 0.3 → VOID |

### 4.6 F9 Distribution — All 6 Implementations

| # | File | Lines | Strategy |
|---|------|-------|----------|
| 1 | `core/shared/laws.py` | 858-1050 | 5-component weighted C_dark (CANONICAL) |
| 2 | `core/laws.py` | 789 | Keyword-count threshold |
| 3 | `A-FORGE FloorEnforcer.ts` | 125 | Regex match on intent + expected_outcome |
| 4 | `core/governance_kernel.py` | 178-189 | Shadow metric via lazy-loaded F9_AntiHantu |
| 5 | `commands/arif_run.py` | 31-63 | F9-tagged destructive command patterns |
| 6 | `commands/arif_sudo.py` | 21-46 | F9-tagged dangerous command patterns |

---

## 5. Organ-Specific Invariant Layers

### 5.1 GEOX — 19 Invariants

**File:** `/root/geox/src/geox_core/governance/geox_invariants.yaml`
**Status: DECLARED — YAML spec, not all have enforcement code**

Organized into 4 sections:
- **Physics:** Earth Truth First, Subsurface Uncertainty is Irreducible, No Extrapolation Without Calibration
- **Epistemics:** Evidence over Authority, Multiple Working Hypotheses
- **Capital & Governance:** Prospect Evaluation bounded by Physics9
- **Operational:** Tool surface integrity, schema stability

### 5.2 WELL — 14 Invariants

**File:** `/root/WELL/specs/WELL_INVARIANTS.md`
**Status: DECLARED — Spec, partial enforcement in server.py**

Key invariants:
- **W0:** Sovereignty — WELL reflects, never decides
- **W1:** Authority Grammar — REFLECT_ONLY, never adjudicates
- **W2:** Truth Policy — INSUFFICIENT_DATA > fake data
- **W3:** Data Sovereignty — state.json is local, never exfiltrated
- **W4-W8:** W-Floor invariants
- **W9:** 5-Minute Body Check — max staleness
- **W10:** Irreversibility Gate — somatic boundary

**File:** `/root/WELL/GENESIS/012_SUBSTRATE_MANIFEST.md`
**Status: DECLARED — 13 canonical substrate signals**

Defines the 13 signals WELL tracks for human readiness. 7 of 13 currently PARTIAL (GAP-002).

### 5.3 WEALTH — 12 Thermodynamic Dimensions

**File:** `/root/WEALTH/docs/SOVEREIGN_WEALTH_SPEC.md`
**Status: DECLARED — Spec, partial enforcement**

12 Ω-dimensions including hysteresis (Ω-12: Path Dependence). The `wealth_hysteresis_ledger` tool exists in `arifosmcp/apps/wealth_app.py`.

### 5.4 arifOS — 5 Core Invariants

**File:** `/root/arifOS/docs/CORE_INVARIANTS.md`
**Status: DECLARED — Root doctrine**

Five invariants:
1. Capability is not permission
2. Advisory output is not authority
3. Service health is not execution approval
4. SEAL-readiness is not VAULT seal
5. No component may claim more certainty than its evidence receipt

### 5.5 arifOS — Bootstrap Substrate Assert

**File:** `/root/arifOS/arifosmcp/core/kernel/substrate_assert.py`
**Status: ENFORCED — 7 pre-constitutional checks before kernel boot**

Checks: DNS, config, database, embedding model, vault directory, telemetry, system fingerprint.

---

## 6. Invariant Coverage Matrix — The Full Picture

### 6.1 Physical Substrate Invariants (Tier 0–2)

| Invariant | Layer 1 (Thermo) | Layer 2 (Economic) | Layer 3 (Floors) | Organ Layer | Verdict |
|-----------|------------------|--------------------|--------------------|-------------|---------|
| **I1 Conservation** | ThermodynamicBudget (budget tracking) | I01 (value), I04 (budget), I12 (ledger) | F1 AMANAH, F11 AUDITABILITY | VAULT999 immutability | **ENFORCED** (fragmented) |
| **I2 Entropy** | shannon_entropy(), entropy_delta(), EntropyIncreaseError | I02 (entropic cost), I06 (NPV gradient) | F4 CLARITY (ΔS ≤ 0) | — | **ENFORCED** (strong) |
| **I3 Causality** | — | I08 (irreversibility), I11 (speed limit) | F1 AMANAH (reversible-first), 888_HOLD | NATS timeouts (30s default), staleness threshold (120s), `cross_organ_probe.py` latency tracking, `pre_execution_gate.py` total_latency_ms | **ENFORCED** — I11 `check_speed_limit_value()` with causal_bandwidth_ms formula. I08 `check_irreversibility_commitment()`. Timeout/staleness at transport layer. |
| **I4 Boundaries** | ThermodynamicExhaustionError | — | F1 (lease gate), F10 (ontology), F13 (veto) | WELL somatic filter, organ INVARIANTS.md | **ENFORCED** (strong) |
| **I5 Feedback** | — | — | NATS L4 signals | feedback_loop.py | **COMPUTED** (partial) |
| **I6 Path Dependence** | hysteresis_penalty in governance_kernel | I10 (hysteresis_wealth) | F6 EMPATHY (via hysteresis) | WEALTH hysteresis_ledger | **ENFORCED** (economic domain only) |
| **I7 Reflexivity** | ModeCollapseError, vector_orthogonality() | I07 (mode collapse) | F8 GENIUS | WEALTH reflexive governance loop (D-M-E paper) | **COMPUTED** (partial) |
| **I8 Landauer** | LANDAUER_MIN, LandauerError, check_landauer_bound(), ThermodynamicBudget | I03 (landauer_asymmetry) | F2 TRUTH ("truth is suspiciously cheap") | arifosd.py ApexThermodynamicEngine, thermo_estimator.py | **ENFORCED** (4 locations, fragmented — no unified budget) |
| **I9 Exergy** | MIN_THERMODYNAMIC_EFFICIENCY (Carnot-like, partial) | I06 (NPV entropy), I09 (Carnot efficiency, implied) | — | WEALTH TODO.md line 90: "exergy + negentropy capital types" | **TODO** (not enforced) |
| **I10 Embodiment** | — | — | — | embodiment_contracts.py (tool embodiment), WELL 012_SUBSTRATE_MANIFEST.md (human signals) | **COMPUTED** (tool-level only, not biological) |
| **I11 Maintenance Scaling** | ThermodynamicExhaustionError (partial — budget depletion) | — | — | — | **ABSENT** (zero hits across all 6 repos) |
| **I12 Uncertainty** | MAX_OMEGA_ENV | I05 (scarcity-abundance orthogonality) | F7 HUMILITY (Ω₀ band), F2 TRUTH (confidence) | GEOX: "Subsurface Uncertainty is Irreducible" | **ENFORCED** (strong) |

### 6.2 What the 12 Economic Invariants Map To

```
Economic I01 (Conservation)  ─────► Physical I1 (Conservation)
Economic I02 (Entropic Cost) ─────► Physical I2 (Entropy)
Economic I03 (Landauer)      ─────► Physical I8 (Landauer)
Economic I04 (Budget)        ─────► Physical I1, I8
Economic I05 (Scarcity)      ─────► Physical I12 (Uncertainty)
Economic I06 (NPV Entropy)   ─────► Physical I2, I9 (Exergy implied)
Economic I07 (Mode Collapse) ─────► Physical I7 (Reflexivity)
Economic I08 (Irreversibility)───► Physical I3 (Causality)
Economic I09 (Genius/Carnot) ─────► Physical I9 (Exergy implied)
Economic I10 (Hysteresis)    ─────► Physical I6 (Path Dependence)
Economic I11 (Speed Limit)   ─────► Physical I3 (Causality)
Economic I12 (Ledger)        ─────► Physical I1 (Conservation)
```

**Coverage: 10 of 12 physical invariants have at least partial code.**
**Gaps: I9 Exergy (TODO), I11 Maintenance Scaling (ABSENT).**

### 6.3 Source Document's 15 Invariants — Extended Coverage

The sovereign's source document ("Foundation of the Universe") defines 15 invariants. Five don't map 1:1 to the economic 12. Here is their actual code status:

| Source # | Invariant | Status | Code Evidence |
|----------|-----------|--------|---------------|
| **#3** | **Finite Signal Speed** | **ENFORCED** | I11 `check_speed_limit_value()` in `economic_invariants.py:356` — `causal_bandwidth_ms` formula with consensus depth + audit trail penalties. NATS timeouts (30s). Staleness threshold 120s in `organ_attestation.py`. `cross_organ_probe.py` latency tracking. |
| **#4** | **Symmetry / Invariance** | **IMPLICIT** | Constitution is a symmetry constraint — same floor, different case. `constitution_hash` verification in pre_execution_gate. Identity anchors per organ (constitution/physics/capital/substrate hashes). F13 universal veto. No explicit "symmetry" named code — enforced structurally. |
| **#7** | **Gradients Drive Flow** | **ENFORCED** | NATS L5: 6 gradient dimensions — `arifos.gradient.{constitution,physics,capital,substrate,continuity,dignity}` (`nats_event_bus.py:91-98`). Cost function: C = α·C_constitution + β·C_physics + γ·C_capital + δ·C_substrate + ε·C_continuity + ζ·C_dignity. `publish_gradient()` line 718, `subscribe_gradient()` line 752, `publish_constitutional_gradient()` line 1049. I06 NPV entropy gradient. |
| **#10** | **Scale Effects** | **PARTIAL** | I07 `check_mode_collapse_market()` detects concentration — a scale failure mode. No explicit "does this behavior hold at scale?" check. The maintenance scaling draft proposes `Complexity_index = ln(1+N_tools) + 0.02·N_tracked_files` but is not yet enforced. |
| **#14** | **No Free Lunch** | **IMPLICIT** | F8 GENIUS: G = (A×P×X×E²)×(1-h) — multi-dim trade-off. `ThermodynamicBudget` enforces finite resources. I05 rejects universal abundance claims. F5 PEACE²: power must be non-destructive. No explicit "no free lunch" named code. |
| **#15** | **Time's Arrow / Mortality** | **ENFORCED** | I08 `check_irreversibility_commitment()` — explicit arrow enforcement, requires `ack_irreversible`. F1 AMANAH: reversible-first. 888_HOLD. `ThermodynamicExhaustionError` ("Session has reached heat death"). ΔS_total ≥ 0 checks. |

**Corrected summary:** Of the 5 invariants initially classified as "missing," only **#10 Scale Effects is a genuine gap.** #3 and #7 are fully enforced under different names. #4 and #14 are implicit in the constitutional architecture. #15 is explicitly enforced.

---

## 7. Code Locations Index — Quick Reference

```
ENFORCEMENT ENGINE:
  /root/arifOS/core/physics/thermodynamics_hardened.py    ← Landauer + entropy + budget (798 lines)
  /root/arifOS/core/physics/economic_invariants.py         ← 12 invariants + 3 emergence (1059 lines)
  /root/arifOS/core/shared/laws.py                         ← F1-F13 classes + check_all_floors()
  /root/arifOS/core/laws.py                                ← ConstitutionalLaws class
  /root/arifOS/core/governance_kernel.py                   ← Dynamic floor scoring + shadow metric
  /root/arifOS/arifosmcp/runtime/pre_execution_gate.py     ← 13-gate chokepoint
  /root/A-FORGE/src/domain/governance/FloorEnforcer.ts     ← TypeScript checkAll()
  /root/A-FORGE/src/domain/governance/mcpFloorEnforcer.ts  ← Per-tool MCP gate

THERMODYNAMIC DAEMON:
  /root/arifOS/arifosd.py:35-98                            ← ApexThermodynamicEngine
  /root/arifOS/arifosmcp/intelligence/tools/thermo_estimator.py  ← landauer_limit() utility

ORGAN INVARIANTS:
  /root/geox/src/geox_core/governance/geox_invariants.yaml ← 19 GEOX invariants
  /root/WELL/specs/WELL_INVARIANTS.md                      ← 14 WELL invariants
  /root/WELL/GENESIS/012_SUBSTRATE_MANIFEST.md             ← 13 canonical substrate signals
  /root/arifOS/docs/CORE_INVARIANTS.md                     ← 5 root invariants
  /root/arifOS/arifosmcp/core/kernel/substrate_assert.py   ← 7 bootstrap checks

EMBODIMENT:
  /root/arifOS/arifosmcp/runtime/embodiment_contracts.py   ← Per-tool embodiment contracts
  /root/arifOS/arifosmcp/tools/embodied.py                 ← EmbodiedTool base class

FEEDBACK:
  /root/arifOS/arifosmcp/runtime/feedback_loop.py          ← plan→act→observe→evaluate
  /root/arifOS/arifosmcp/runtime/nats_event_bus.py         ← NATS subject topology (1134 lines)

ECONOMIC-PHYSICS SPEC:
  /root/arifOS/core/physics/ECONOMIC_INVARIANTS.md          ← Human-readable invariant spec

CONSTITUTIONAL THEORY (static):
  /root/arifOS/static/arifos/theory/000/000_LAW_v2026.03.07.md    ← Axiom 1: Truth Has a Price
  /root/arifOS/static/arifos/theory/000/000_CONSTITUTION.md        ← Landauer Bound section
  /root/arifOS/static/arifos/theory/000/The Foundational Knowledge Trinity of arifOS__list.md  ← Theory #2: Landauer, #3: Free Energy
```

---

## 8. Summary for Any Future Substrate Document

Any `SUBSTRATE_INVARIANT_REFERENCE_LAYER.md` MUST account for:

| Reality | Consequence for the Document |
|---------|------------------------------|
| Landauer is enforced in 4 modules | Cannot claim "Landauer is missing." Must say "Landauer is fragmented across 4 modules with no unified budget." |
| 12 economic invariants exist in code | Cannot propose 12 invariants as new. Must acknowledge, map, and extend. |
| F9 ANTI-HANTU spans 6 implementations | Cannot propose renaming/splitting F9. It's constitutional law. New energy concerns → new floor. |
| Exergy is a WEALTH TODO | Must cite `/root/WEALTH/TODO.md` line 90. Gap is real but scoped. |
| Maintenance scaling is ABSENT | Must declare as blind spot. No code, no TODO, no spec. |
| ThermodynamicBudget exists | Cannot claim "no energy accounting." Must say "budget exists but not plumbed to all organs." |
| Embodiment contracts exist | Cannot claim "no embodiment." Must say "tool-level computational embodiment exists; biological embodiment (WELL signals) is partial." |
| Finite signal speed is ENFORCED as I11 + timeouts + staleness | Cannot claim it's missing. Must map source #3 → I11 `check_speed_limit_value()` + transport-layer timeouts. |
| Gradients are ENFORCED as NATS L5 infrastructure | Cannot claim they're missing. Must map source #7 → 6 gradient dimensions with pub/sub + cost function. |
| Time's arrow is ENFORCED as I08 + F1 + 888_HOLD | Cannot claim it's "only implicit." Must map source #15 → I08 irreversibility check + thermodynamic exhaustion. |
| Symmetry and No Free Lunch are IMPLICIT | Cannot claim they're enforced or absent. Must describe structural enforcement through constitution_hash, identity anchors, trade-off formulas. |
| Scale Effects is the only genuine gap among the 5 | Must identify #10 as the sole unenforced invariant. I07 mode collapse is partial coverage. |

---

*DITEMPA BUKAN DIBERI — This is what the code actually does. Any document that contradicts this map is wrong.*
