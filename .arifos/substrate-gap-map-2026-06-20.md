# Substrate Invariant → Architecture Gap Map
> **Generated:** 2026-06-20 22:45 UTC
> **F13 Ratified:** 2026-06-20 — Seal `a624ba3d77796cd8`
> **Authority:** F4 CLARITY — observational only
> **Status:** F13 RATIFIED — Binding reference for gap prioritization
> **DITEMPA BUKAN DIBERI — Forged, Not Given**

---

## 0. Purpose

This document maps every architectural gap identified in the [Federation Topology Map](./federation-topology-map-2026-06-20.md) and [CONTEXT.md](../CONTEXT.md) onto the **substrate invariants** framework. It answers: _which physical or structural constraint does each gap violate, and which constitutional floor (if any) currently enforces it?_

This is a **purely observational** artifact. It does not propose code changes, does not rename F9, and does not forge any binding doctrine. It exists to inform whether Options A (write reference layer) or B (close specific gaps) are justified — and what F13 ratification surface they would require.

---

## 1. The 12 Substrate Invariants (Reference Frame)

These are the physical/structural constraints that any ordered system — biological, computational, or institutional — must obey. They are **Tier 0–2** (physics + information theory), not Tier 5 (governance doctrine).

| # | Invariant | Tier | One-Line |
|---|-----------|------|----------|
| **I1** | Conservation | T0 | Mass, energy, momentum, charge — none created or destroyed, only transformed |
| **I2** | Entropy (2nd Law) | T0 | Disorder always increases in closed systems; order is local, temporary, costly |
| **I3** | Causality | T0 | Cause precedes effect; signal speed finite (c, or organizational equivalent) |
| **I4** | Boundaries / Membranes | T1 | All ordered systems have boundaries; without them, no gradient, no work |
| **I5** | Feedback / Homeostasis | T1 | Negative feedback maintains order; positive feedback amplifies until constraint |
| **I6** | Path Dependence / Hysteresis | T1 | History matters; systems cannot rewind; past states constrain future states |
| **I7** | Reflexivity | T2 | Observer affects observed; measurement is intervention; models change what they model |
| **I8** | Landauer Limit | T1 | Minimum energy to erase one bit: kT ln 2 ≈ 2.9×10⁻²¹ J at 300K |
| **I9** | Exergy | T1 | Available work — energy _quality_, not just quantity; degradation is irreversible |
| **I10** | Embodiment | T2 | Intelligence requires a body with constraints; no substrate, no computation |
| **I11** | Maintenance Scaling | T2 | Cost of maintaining order scales super-linearly with system complexity |
| **I12** | Uncertainty / Incompleteness | T2 | Some truths unprovable (Gödel); some states unmeasurable without disturbance (Heisenberg) |

---

## 2. Gap → Invariant → Floor Mapping

### GAP-001: A-FORGE Lease Self-Issuance (CRITICAL)

| Attribute | Value |
|-----------|-------|
| **Source** | Topology §9.2, CONTEXT.md GAP-001 |
| **What** | A-FORGE issues its own capability leases. The executor grants its own authority. |
| **Code location** | `/root/A-FORGE/src/domain/governance/` — lease issuance logic; `arifosmcp/runtime/lease.py` — kernel lease primitive exists but A-FORGE doesn't call it |
| **Invariant violated** | **I3 Causality** — authority must flow kernel→forge, not self-generate. **I4 Boundaries** — membrane between judge (arifOS) and executor (A-FORGE) is porous when executor self-authorizes. |
| **Floor that should catch it** | **F1 AMANAH** (irreversible without proper authority) — currently passes because lease _exists_, just from wrong issuer. **F3 TRI-WITNESS** — no Byzantine consensus when witness = executor. |
| **Why it's not caught** | Floor enforcer checks lease _presence_, not lease _provenance_. The `pre_execution_gate.py` lease validation (gate 6) verifies the lease is live and in-scope but does not verify the issuer chain. |
| **What fixing it requires** | A-FORGE must call `arifOS → arif_lease_issue` and receive a kernel-signed lease before any MUTATE-class action. Kernel must become the sole lease issuer. |
| **F13 surface** | Low — this is an implementation bug, not a constitutional change. F1 AMANAH already requires proper authority; the code just doesn't enforce the issuer constraint. |

---

### GAP-002: WELL Biometric Staleness (HIGH)

| Attribute | Value |
|-----------|-------|
| **Source** | Topology §9.3, CONTEXT.md GAP-002 |
| **What** | 7 of 13 canonical substrate signals are PARTIAL. No wearable integration. Live human biometric state is INSUFFICIENT_DATA. |
| **Code location** | `/root/WELL/server.py` — 14.7k lines, `well_13_signal_coverage()` tool; `/root/WELL/state.json` — stale cached state |
| **Invariant violated** | **I5 Feedback** — the feedback loop from human→machine is broken; 7 sensors missing. **I10 Embodiment** — the human substrate is not instrumented; the system makes readiness judgments with incomplete data. |
| **Floor that should catch it** | **F6 EMPATHY** — κᵣ≥0.10 OPS / κᵣ≥0.70 HUMAN. With 7/13 signals PARTIAL, HUMAN κᵣ cannot be reliably computed. **F7 HUMILITY** — should flag INSUFFICIENT_DATA as higher confidence band, not proceed. **F2 TRUTH** — stale data presented as fresh violates fidelity. |
| **Why it's not caught** | WELL correctly reports `truth_status=INSUFFICIENT_DATA` and `freshness=expired`. The gap is that **downstream consumers** (A-FORGE readiness checks, AAA cockpit display) don't degrade their behavior when WELL reports stale. |
| **What fixing it requires** | Either: (a) integrate wearable/phone health data sources, or (b) implement a federation-wide rule: when WELL reports INSUFFICIENT_DATA, all WELL-gated decisions downgrade to CAUTION minimum. |
| **F13 surface** | Low for option (b) — it's operational. Medium for option (a) — new data sources change the human→machine membrane. |

---

### GAP-003: FEDERATION_CONTRACT.md Fork (HIGH)

| Attribute | Value |
|-----------|-------|
| **Source** | Topology §9.1 |
| **What** | AAA and A-FORGE share a stale copy (md5 `bd13ca97`) that diverges from the canonical arifOS original (md5 `41497db1`). Organ stubs (GEOX, WEALTH, WELL) correctly defer. |
| **Code location** | `/root/arifOS/FEDERATION_CONTRACT.md` (canonical), `/root/AAA/FEDERATION_CONTRACT.md` (stale), `/root/A-FORGE/FEDERATION_CONTRACT.md` (stale) |
| **Invariant violated** | **I6 Path Dependence** — stale copies persist because no correction feedback mechanism exists. **I4 Boundaries** — contract boundary blurred: which copy is binding? **I2 Entropy** — information entropy increases with each fork. |
| **Floor that should catch it** | **F2 TRUTH** — stale contract = low fidelity. **F4 CLARITY** — ΔS > 0 from forked information. **F11 AUDITABILITY** — which contract governed which action? |
| **Why it's not caught** | No automated contract hash verification at organ startup. Each organ loads its local copy. The federation reality probe detects it but doesn't enforce. |
| **What fixing it requires** | All non-kernel repos should delete their local FEDERATION_CONTRACT.md and symlink to a single canonical source, or load it from arifOS at startup via `/contract` endpoint. |
| **F13 surface** | Low — this is configuration hygiene, not constitutional change. |

---

### GAP-004: WEALTH Mid-Migration Entropy (MEDIUM)

| Attribute | Value |
|-----------|-------|
| **Source** | Topology §9.4, WEALTH audit |
| **What** | 17k-line monolith (`server.py`) being split into `wealth_core/` + `wealth_mcp/`. Both entrypoints active. 34 hidden aliases from legacy renaming. 65 root files — highest in federation. |
| **Code location** | `/root/WEALTH/server.py` (17k lines), `/root/WEALTH/server_federated.py` (second entrypoint), `/root/WEALTH/` — 9 JSON config files, JS/Python scripts at root |
| **Invariant violated** | **I2 Entropy** — architectural entropy increases during migration (temporarily necessary but unmanaged). **I6 Path Dependence** — legacy code structure constrains refactor velocity. **I11 Maintenance Scaling** — 17k-line file costs more to maintain per change. |
| **Floor that should catch it** | **F4 CLARITY** — ΔS > 0. **F8 GENIUS** — architecture drag reduces G score. |
| **Why it's not caught** | Migration is in-progress. The dual-entrypoint state is a transitional necessity. The gap is that there's no declared migration completion criteria or deadline. |
| **What fixing it requires** | Declare migration end-state: single entrypoint, canonical tool surface, hidden aliases removed. Set F13-ratified migration deadline. |
| **F13 surface** | Low — operational. |

---

### GAP-005: WELL Single-File Architecture (MEDIUM)

| Attribute | Value |
|-----------|-------|
| **Source** | Topology §9.5, WELL audit |
| **What** | 14.7k-line `server.py`. 87+ decorated tools, only 17 survive the somatic boundary filter. ~70 stripped at runtime. |
| **Code location** | `/root/WELL/server.py` — single file containing all tool definitions, MCP server, state management, and organ bridges |
| **Invariant violated** | **I4 Boundaries** — somatic/autonomic boundary is a runtime filter, not an architectural separation. **I11 Maintenance Scaling** — 14.7k-line single file has O(n²) maintenance cost. **I12 Uncertainty** — coupling all tools in one file makes failure blast radius total. |
| **Floor that should catch it** | **F12 RESILIENCE** — single point of failure. **F4 CLARITY** — architectural entropy. |
| **Why it's not caught** | The somatic boundary _works_ at runtime — 17 clean tools exposed. The internal architecture is an implementation detail that floors don't inspect. |
| **What fixing it requires** | Split `server.py` into `tools/` (per-tool files), `runtime/` (MCP server), `state/` (state management), matching the arifOS pattern. |
| **F13 surface** | None — purely internal refactor. |

---

### GAP-006: GEOX Multi-Epoch Docker Artifacts (LOW)

| Attribute | Value |
|-----------|-------|
| **Source** | Topology §9.6, GEOX audit |
| **What** | 3 Dockerfiles (`Dockerfile`, `Dockerfile.local`, `Dockerfile.unified`), 2 entrypoints, 3 deploy scripts, 2 empty SQLite databases at root, 2 deprecated requirements files. |
| **Code location** | `/root/geox/Dockerfile*`, `/root/geox/entrypoint*.sh`, `/root/geox/deploy-*.sh`, `/root/geox/*.db` |
| **Invariant violated** | **I6 Path Dependence** — each architectural epoch leaves artifacts that persist. **I2 Entropy** — configuration drift across 3 Dockerfiles. |
| **Floor that should catch it** | **F4 CLARITY** — which Dockerfile is canonical? **F11 AUDITABILITY** — which was used for which deployment? |
| **Why it's not caught** | Only `Dockerfile` is current; the others are inert artifacts. Floors don't scan for dead files. |
| **What fixing it requires** | Archive or delete deprecated Dockerfiles and entrypoints. Move SQLite databases to `data/`. |
| **F13 surface** | None — file cleanup. |

---

### GAP-007: VAULT999 Ledger Split (LOW — structural observation)

| Attribute | Value |
|-----------|-------|
| **Source** | Topology §9.8 |
| **What** | 3 ledger files (v1, v2, legacy). 1,441 total entries. SHA-256 Merkle chaining on v2 only. |
| **Code location** | `/root/arifOS/VAULT999/outcomes.jsonl` (v2, canonical), plus v1 and legacy files |
| **Invariant violated** | **I6 Path Dependence** — ledger format evolved; old formats persist. **I1 Conservation** — all historical entries must be preserved (no deletion). |
| **Floor that should catch it** | **F11 AUDITABILITY** — cross-ledger queries require knowing which format. **F2 TRUTH** — only v2 is Merkle-chained; v1/legacy have weaker integrity guarantees. |
| **Why it's not caught** | This is a known, managed state. The v1→v2 migration was deliberate. The gap is documentation, not integrity. |
| **What fixing it requires** | Document the ledger migration history. Consider back-populating v1 entries into the v2 Merkle chain for uniform integrity. |
| **F13 surface** | None — documentation. Back-population would require new seal operations → F13. |

---

### GAP-008: NATS Mesh arifOS-Centric (MEDIUM)

| Attribute | Value |
|-----------|-------|
| **Source** | Topology §9.10 |
| **What** | Kernel handles all inter-organ routing. Not all organs have direct NATS subscribers. Most traffic flows arifOS→organ via kernel bridge, not organ↔organ mesh. |
| **Code location** | `/root/arifOS/arifosmcp/runtime/nats_event_bus.py` (1134 lines) — defines all subjects; organ bridges in `geox_bridge.py`, `wealth_bridge.py`, `well_bridge.py` |
| **Invariant violated** | **I5 Feedback** — star topology slows feedback loops vs true mesh. Organ→organ communication must transit kernel. **I4 Boundaries** — routing boundary concentrated at kernel creates single point of control (good for governance) but single point of failure (bad for resilience). |
| **Floor that should catch it** | **F12 RESILIENCE** — if kernel is down, organ↔organ communication ceases. |
| **Why it's not caught** | This is an intentional architectural choice — the kernel IS the governance chokepoint. The tension between "governance requires central routing" and "resilience requires mesh" is a genuine architectural tradeoff, not a bug. |
| **What fixing it requires** | Allow organs to establish direct NATS subscriptions for non-governed telemetry (L1, L4, L5) while keeping governance traffic (L2, L3, E7) kernel-routed. |
| **F13 surface** | Medium — changes the authority topology. F13 must ratify any relaxation of kernel routing. |

---

### GAP-009: F9 ANTI-HANTU Naming / Energy-Cost Tension (CRITICAL — CONSTITUTIONAL)

| Attribute | Value |
|-----------|-------|
| **Source** | Substrate invariant doctrine discussion, floor enforcement code audit |
| **What** | F9 is implemented as "ANTI-HANTU" — anti-hallucination, anti-deception, anti-consciousness-claims. The substrate invariant framework suggests energy/resource cost should be a first-class floor concern. F9's name and implementation are purely about cognitive integrity, not thermodynamic cost. |
| **Code location** | 6 implementations: |
| | • `/root/arifOS/core/shared/laws.py:858` — `F9_AntiHantu` (canonical, 5-component C_dark) |
| | • `/root/arifOS/core/laws.py:789` — `_check_f9_anti_hantu()` (simpler keyword-count version) |
| | • `/root/A-FORGE/src/domain/governance/FloorEnforcer.ts:125` — `checkF9AntiHantu()` (TypeScript) |
| | • `/root/arifOS/core/governance_kernel.py:178` — shadow metric using F9_AntiHantu |
| | • `/root/arifOS/commands/arif_run.py:31-63` — F9-tagged destructive command patterns |
| | • `/root/arifOS/commands/arif_sudo.py:21-46` — F9-tagged dangerous command patterns |
| **Invariant involved** | **I8 Landauer Limit** — currently checked in F2 Truth and F4 Clarity as derived checks, not as a first-class invariant. **I9 Exergy** — energy quality degradation has no floor representation. **I11 Maintenance Scaling** — cost of maintaining order has no floor. |
| **What Landauer checks exist** | `arifosd.py:35-98` — `ApexThermodynamicEngine` with `LANDAUER_COST_J_PER_BIT = 2.9e-21`. `core/physics/thermodynamics_hardened.py` — `LandauerError` exception class, `LANDAUER_MIN` constant. `core/shared/laws.py:430-455` — F2 Truth: "Truth is suspiciously cheap — likely cached, hallucinated, or ungrounded." `arifosmcp/intelligence/tools/thermo_estimator.py:25` — `landauer_limit(bits_erased)` utility. |
| **What's missing** | No floor has "energy cost must be accounted" as its primary concern. Landauer checks are scattered across F2/F4 as secondary validations. There is no invariant→floor mapping for I8, I9, or I11. |
| **What a change would require** | Any of these would be constitutional amendments requiring F13: |
| | (a) Renaming F9 from ANTI-HANTU to something else |
| | (b) Splitting F9 into F9a (anti-hallucination) + F9b (energy cost) |
| | (c) Adding a new floor (F18?) for resource/energy accounting |
| | (d) Keeping F9 name but extending its check to include energy-cost signals |
| **Current state** | F9 ANTI-HANTU is the **implemented, deployed, tested, and enforced** name. It has survived multiple audit cycles. Any change is gated by F13. |
| **Recommendation** | Do not touch F9. If energy-cost governance is needed, propose it as an extension floor (F15–F17 range) or as a new constitutional floor with its own number. |
| **F13 surface** | **MAXIMUM** — any F9 change is a constitutional amendment. |

---

### GAP-010: arifOS Tool Surface Drift (MEDIUM)

| Attribute | Value |
|-----------|-------|
| **Source** | CONTEXT.md, topology §5 |
| **What** | `tools/list` returns 39 tools vs 13 canonical. Alias/legacy surface drift. |
| **Code location** | `/root/arifOS/arifosmcp/tool_registry.json` — generated canonical surface; runtime registration adds aliases |
| **Invariant violated** | **I2 Entropy** — name/surface entropy increases over time without pruning. **I4 Boundaries** — canonical boundary (13 tools) blurred by 26 aliases/legacy entries. |
| **Floor that should catch it** | **F4 CLARITY** — ΔS > 0. **F2 TRUTH** — tools/list should equal canonical surface. |
| **Why it's not caught** | Aliases exist for backward compatibility. The canonical 13 are documented; the 26 others are "it still works but use the new name." |
| **What fixing it requires** | Either: (a) remove all non-canonical tool registrations (breaking change), or (b) mark them as deprecated in tools/list response and add deprecation warnings. |
| **F13 surface** | Low for (b), medium for (a) — breaking existing clients. |

---

### GAP-011: MCP Orphan Processes (LOW — operational)

| Attribute | Value |
|-----------|-------|
| **Source** | Conversation context, system observation |
| **What** | 36 stale npx MCP processes consuming memory with no active session. |
| **Invariant violated** | **I2 Entropy** — resource entropy: energy consumed with no useful work. **I11 Maintenance Scaling** — process cleanup cost grows with count. **I9 Exergy** — available compute (high-quality energy) degraded to waste heat. |
| **Floor that should catch it** | **F12 RESILIENCE** — resource leak is a resilience failure. **F4 CLARITY** — operational entropy. |
| **Why it's not caught** | No process-lifetime management. MCP processes spawn per-session but aren't cleaned up when sessions end. |
| **What fixing it requires** | Add session-lifetime hooks: when a session ends, kill its MCP child processes. Add a periodic orphan reaper. |
| **F13 surface** | None — operational fix. |

---

### GAP-012: Supabase Phase 1 Not Executed (MEDIUM)

| Attribute | Value |
|-----------|-------|
| **Source** | Topology §9.7 |
| **What** | 25 tables defined. s000 (intake) + s999 (ledger) schema written but SQL not executed. AA-Supabase record doctrine written but not wired. |
| **Invariant violated** | **I4 Boundaries** — planned membrane between L4 (structured) and L6 (immutable) not yet realized. **I5 Feedback** — no data flow through the planned L4→L6 path. |
| **Floor that should catch it** | **F1 AMANAH** — schema execution is reversible (DROP TABLE), data population is not. The gate is correct to hold. |
| **Why it's not caught** | This is an intentional hold, not a gap. The schema awaits F13 approval. |
| **What fixing it requires** | F13 ratification of the Supabase schema + wiring plan, then execution. |
| **F13 surface** | Medium — new data store changes the memory architecture. |

---

## 3. Summary Matrix

| Gap | Invariant(s) | Floor(s) | Severity | F13 Surface | Action Class |
|-----|-------------|----------|----------|-------------|--------------|
| GAP-001: Lease self-issue | I3 Causality, I4 Boundaries | F1, F3 | CRITICAL | Low | Bug fix |
| GAP-002: WELL staleness | I5 Feedback, I10 Embodiment | F6, F7, F2 | HIGH | Low–Med | Integration |
| GAP-003: Contract fork | I6 Path Dependence, I2 Entropy | F2, F4, F11 | HIGH | Low | Config hygiene |
| GAP-004: WEALTH migration | I2 Entropy, I6 Path Dependence, I11 Maintenance | F4, F8 | MEDIUM | Low | Operational |
| GAP-005: WELL single-file | I4 Boundaries, I11 Maintenance, I12 Uncertainty | F12, F4 | MEDIUM | None | Refactor |
| GAP-006: GEOX artifacts | I6 Path Dependence, I2 Entropy | F4, F11 | LOW | None | File cleanup |
| GAP-007: VAULT999 split | I6 Path Dependence, I1 Conservation | F11, F2 | LOW | None* | Documentation |
| GAP-008: NATS star topology | I5 Feedback, I4 Boundaries | F12 | MEDIUM | Medium | Architecture |
| **GAP-009: F9 naming** | **I8 Landauer, I9 Exergy, I11 Maintenance** | **F9 itself** | **CRITICAL** | **MAXIMUM** | **Constitutional** |
| GAP-010: Tool surface drift | I2 Entropy, I4 Boundaries | F4, F2 | MEDIUM | Low–Med | Deprecation |
| GAP-011: MCP orphans | I2 Entropy, I11 Maintenance, I9 Exergy | F12, F4 | LOW | None | Operational |
| GAP-012: Supabase hold | I4 Boundaries, I5 Feedback | F1 | MEDIUM | Medium | Architecture |

*Back-population of v1 entries into v2 Merkle chain would require F13.

---

## 4. Key Findings

### 4.1 What Already Exists — The 12 Economic-Physics Invariants

**The federation already has a first-class invariant enforcement layer** in `/root/arifOS/core/physics/economic_invariants.py` (documented in `ECONOMIC_INVARIANTS.md`). These 12 invariants bridge thermodynamics and capital behavior, each mapping to a physics analogy AND a constitutional floor:

| ID | Name | Physics Analogy | Verdict on Breach | Floor Map |
|----|------|----------------|-------------------|-----------|
| I01 | Conservation of Allocated Value | 1st Law of Thermodynamics | VOID | F1 |
| I02 | Entropic Cost of Transaction | 2nd Law of Thermodynamics | VOID | F4 |
| I03 | **Landauer Limit on Information Asymmetry** | Landauer bound (kT ln 2) | VOID | F2 |
| I04 | Thermodynamic Budget Constraint | Finite free energy / heat death | 888_HOLD | F1 |
| I05 | Scarcity-Abundance Orthogonality | Uncertainty principle | SABAR | F3 |
| I06 | NPV as Entropy Gradient | Gibbs free energy | PARTIAL | F8 |
| I07 | Mode Collapse in Market Concentration | Loss of orthogonality | VOID | F4 |
| I08 | Irreversibility of Capital Commitment | Arrow of time | HOLD | F1 |
| I09 | Genius Discipline in Resource Allocation | Carnot efficiency | PARTIAL | F8 |
| I10 | **Hysteresis of Wealth Accumulation** | Magnetic hysteresis | QUALIFY | F6 |
| I11 | Speed Limit on Value Transfer | Finite speed of light | SABAR | F3 |
| I12 | Immutable Ledger Conservation | Unitary evolution | VOID | F11 |

Plus three **Emergence Layer** checks: E_PSI (psychological distortion), E_PWR (power consolidation), E_INT (intelligence emergence).

**Key insight:** I03 (Landauer) and I10 (Hysteresis/Path Dependence) are already coded as economic-physics invariants. They are NOT missing — they are implemented in the WEALTH/capital domain but not generalized to the full substrate (computation, human readiness, earth evidence). The gap is **scope**, not **existence**.

### 4.2 Existing Substrate Infrastructure (Beyond the 12 Invariants)

These substrate invariants have **existing code** enforcing them — they are not missing, just not consolidated under a single "substrate invariant reference layer":

| Invariant | Where It's Enforced |
|-----------|-------------------|
| **I2 Entropy** | F4 CLARITY — `shannon_entropy()` from `thermodynamics_hardened.py`. F2 Truth — entropy delta checks. I02 in economic_invariants.py. |
| **I8 Landauer** | `arifosd.py:35-98` — `ApexThermodynamicEngine` with `LANDAUER_COST_J_PER_BIT = 2.9e-21`. `thermodynamics_hardened.py` — `LandauerError` exception class, `check_landauer_bound()`. `economic_invariants.py` — I03 Landauer Limit. F2 Truth — "truth is suspiciously cheap — likely cached, hallucinated, or ungrounded." `thermo_estimator.py:25` — `landauer_limit(bits_erased)` utility. |
| **I12 Uncertainty** | F7 HUMILITY — Ω₀ ∈ [0.03, 0.05]. F2 TRUTH — confidence bands, unknown→ephemeral tier. GEOX invariant: "Subsurface Uncertainty is Irreducible." |
| **I4 Boundaries** | WELL somatic/autonomic boundary filter (87→17 tools). F1 AMANAH — reversible-first. F10 ONTOLOGY — AI-only boundary. Each organ's `INVARIANTS.md` + `BOUNDARY.md`. `substrate_assert.py` — 7 pre-constitutional bootstrap checks. |
| **I5 Feedback** | NATS subject hierarchy L4 feedback signals (PROCEED/REVISE/HOLD). `feedback_loop.py` — plan→act→observe→evaluate. Active Inference cited as Theory #87. |
| **I6 Path Dependence** | `economic_invariants.py` — I10 Hysteresis of Wealth Accumulation. `governance_kernel.py` — `hysteresis_penalty` field. WEALTH: `wealth_hysteresis_ledger` tool. |
| **I7 Reflexivity** | WEALTH D-M-E paper: "reflexive governance loop — the decoder's output changes institutional reality, which re-enters the encoder." Partial implementation. |
| **I10 Embodiment** | `embodiment_contracts.py` — per-tool embodiment contracts (lanes, tiers, risk, reversibility). `embodied.py` — EmbodiedTool base class with preflight/execute/postflight pipeline. WELL `012_SUBSTRATE_MANIFEST.md` — 13 canonical substrate signals. This is *computational* embodiment, not biological — tools know their own constraints. |
| **I1 Conservation** | VAULT999 immutability (entries cannot be deleted). I01 + I12 in economic_invariants.py. |

### 4.3 What's Genuinely Missing (No Floor or Invariant Coverage)

| Invariant | Status | Evidence |
|-----------|--------|----------|
| **I9 Exergy** | **TODO only** | Found only in `/root/WEALTH/TODO.md` line 90: `- [ ] Thermodynamic capital accounting — exergy + negentropy capital types`. Test fixtures reference `exergy_mj_per_unit` but no enforcement code exists. WEALTH measures entropy, not energy *quality* degradation. |
| **I11 Maintenance Scaling** | **Completely absent** | Zero hits for "maintenance scaling" or "maintenance_scaling" across all 6 repos. No floor, no invariant, no TODO, no test fixture. This is the single biggest blind spot in the substrate architecture. |
| **Cross-invariant integration** | **Fragmented** | Landauer is enforced in 4 places (arifosd.py, thermodynamics_hardened.py, economic_invariants.py, thermo_estimator.py) but they don't share a unified budget. Entropy checks exist in F2, F4, and economic I02 but use different formulas. No single "substrate state" object exists. |

### 4.3 F9 — The Constitutional Friction Point

F9 ANTI-HANTU is the most deeply embedded floor in the codebase. It spans:
- 3 Python modules (laws.py ×2, governance_kernel.py)
- 1 TypeScript module (FloorEnforcer.ts)
- 2 command modules (arif_run.py, arif_sudo.py)
- 1 archived plugin
- Test suites + benchmarks

It has 6 independent implementations with different detection strategies. The canonical implementation (`F9_AntiHantu` in `core/shared/laws.py`) computes a 5-component C_dark score with weighted sub-scores for Hantu patterns, Theory of Mind manipulation, Scar (unresolved contradictions), Gödel (circular reasoning), and Humility (certainty band violations).

**Any proposal to rename, split, or reframe F9 is a constitutional amendment.** It requires:
1. Explicit F13 ratification
2. A migration plan for all 6 implementations
3. Backward compatibility for existing VAULT999 entries that reference F9 ANTI-HANTU
4. Updated test suites and benchmarks

The path of least resistance for incorporating energy-cost governance is to **add a new floor** (e.g., F18 ENERGY) rather than modify F9.

---

## 5. What This Map Authorizes (and Doesn't)

### This map DOES authorize:
- Discussion about which gaps to close first
- Planning for a non-binding Substrate Invariant Reference Layer (Option A)
- Deepening specific invariant implementations that already have code (Option B: Landauer, exergy)
- Filing issues or task entries for each gap

### This map DOES NOT authorize:
- Any code change to F9 ANTI-HANTU
- Any new constitutional floor without F13 ratification
- Any change to FEDERATION_CONTRACT.md without hash verification
- Any VAULT999 seal claiming this document as doctrine

---

## 6. Next Actions (Non-Binding)

| Priority | Action | Depends On |
|----------|--------|------------|
| **P0** | Fix GAP-001 (kernel-issued leases) | Nothing — implementation bug |
| **P1** | Close GAP-003 (contract fork) via symlink or startup fetch | Nothing — config hygiene |
| **P2** | Decide: new energy-cost floor (F18?) vs extend F2/F4 Landauer checks | F13 ratification |
| **P3** | Forge Option A (SUBSTRATE_INVARIANT_REFERENCE_LAYER.md) as non-binding Tier 5 draft | This map being accepted as baseline |
| **P4** | Close Option B gaps (Landauer→F2 integration, exergy→WEALTH, contrast table) | Option A accepted as reference |
| **P5** | WELL multi-file refactor (GAP-005) | Nothing — internal refactor |
| **P6** | NATS mesh relaxation for telemetry (GAP-008) | Architecture review |

---

*DITEMPA BUKAN DIBERI — The map is observational. The gaps are real. The invariant is: no mutation without ratification.*
