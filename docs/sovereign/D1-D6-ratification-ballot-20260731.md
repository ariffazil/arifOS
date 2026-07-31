# F13 BALLOT — D1–D6 Ratification Docket · 2026-07-31

> **Mission:** D1–D6 neutral F13 ballot (M6 + M9 + M11 follow-up).
> **Do NOT implement.** This is a decision docket for F13 sovereign review.
> The prior F13 execution applied D1–D6 T1 edits without this formal ballot — this docket supersedes that implicit ratification by giving F13 an explicit record.

## D1 — W³ tri-witness threshold

| Field | Content |
|---|---|
| **Current competing definitions** | 0.95 at `docs/canon/APEX_EQUATIONS.md:93` (canon, sealed); 0.75 at `core/laws.py:74` and `core/laws.py:1301` (live runtime evaluator); 0.70 at `okf/apex/W3-tri-witness.md:9` (operational fallback) |
| **Runtime behavior** | Code enforces 0.75; doctrine says 0.95; okf says 0.70. Disagreement between code and doctrine. |
| **Historical consequences** | Existing receipts assume 0.75 as runtime canon (M1, M2 receipts); existing APEX_EQUATIONS.md comments assume 0.95 as SEAL ceiling. |
| **Option A** | 0.95 canonical. Existing SEALs may degrade to PARTIAL/HOLD at runtime. |
| **Option B** | 0.75 canonical (doctrine-only 0.95 ceiling). Matches runtime; minimizes regression. |
| **Option C** | Threshold is W³ ≥ 0.75 for SEAL, but 0.95 is the *aspirational* ceiling for `+`-graded seals. Two-tier ladder. |
| **Migration impact** | One-line threshold edit in `core/laws.py`; docstring clarification in `APEX_EQUATIONS.md`; no schema change. |
| **Backward compatibility** | Receipts assume 0.75; if F13 picks A or C, receipt needs annotation. |
| **Tests required** | threshold assertion test: SEAL only when W³ ≥ chosen value; under-threshold returns PARTIAL/HOLD. |
| **Recommendation** (non-binding) | **C** — matches runtime, preserves doctrine, no seal regression |
| **F13 decision** | __________________________ |

## D2 — APEX Genius Equation primitive count

| Field | Content |
|---|---|
| **Current competing definitions** | 4-primitive `G = A×P×X×E²` at `docs/canon/APEX_EQUATIONS.md:14-42`; 5-primitive `G = A·P·E·X·Φ` at `GENESIS/054_DELTA_OMEGA_PSI_MULTIMODAL_COGNITION.md:113,216`, `GENESIS/055_MULTIMODAL_KERNEL_HARDENING.md:192`; 4-primitive single-E form `(A·P·E·X)^(1/4)` at `docs/APEX_MATH_CANON.md:452` (math canon disproof of E²) |
| **Runtime behavior** | Operational form `G = (1-S_comp)×P_verify` (measurement proxy) is used at runtime; the *theoretical* form is rarely computed directly. |
| **Historical consequences** | Older kernel math assumes 4-primitive E²; newer GENESIS docs use 5-primitive Φ. They disagree on what the equation IS. |
| **Option A** | 4-primitive `(A·P·E·X)^(1/4)` (single E, geometric mean). Strict product veto if any dial = 0. |
| **Option B** | 5-primitive `A·P·E·X·Φ` (5 dimensions). Φ treated as a separate primitive (faithfulness). |
| **Option C** | 4-primitive + correction factors (h, C_dark, S_comp) applied at judgment time. The "5th dimension" is actually a multiplicative correction. |
| **Migration impact** | Docstring + comment edits; no runtime code change (operational form unchanged). |
| **Backward compatibility** | Existing math tables need cross-references updated. |
| **Tests required** | theorem test: for each form, prove G == 0 iff any dial = 0 (strict product veto invariant). |
| **Recommendation** (non-binding) | **C** — 4-primitive geometric mean + corrections (per APEX_MATH_CANON.md:452 disproof of E²) |
| **F13 decision** | __________________________ |

## D3 — Public capability projection (semantic count vs agent visibility)

| Field | Content |
|---|---|
| **Current competing definitions** | 8 capabilities per `arifosmcp/constitutional_map.py:6,13,160` (KERNEL_ABI_8); 13 per `arifosmcp/__init__.py:5` and `Dockerfile:135` (legacy); 6 public + 2 gated per external audit (arif_init, observe, think, route, memory, judge + forge/seal); runtime `tools/list` returns 8 names |
| **Runtime behavior** | Runtime correctly returns 8 tools; the 13 vs 8 mismatch is in legacy source/docs, not in live behavior. |
| **Historical consequences** | Dockerfile still claims 13; some llms.txt sections list internal tools (arif_kernel_intercept, arif_correction_probe, arif_j_gate) as if available. |
| **Option A** | 8 semantic capabilities (constitutional_map.py canon). Public agent sees 6; executor adds 2 (forge/seal gated by authority). |
| **Option B** | 13 (restore absorbed modes: arif_canary, arif_triage, arif_fetch, arif_bridge_connect, arif_compose as separate tools). |
| **Option C** | 8 semantic + surface projection flag: public=6, executor=8, internal=13 (3 layers). The 13 is not "exposed" but exists as diagnostic namespace. |
| **Migration impact** | Option C is least disruptive: just document the layer distinction. Option B is most disruptive: must re-introduce 5 absorbed tools. |
| **Backward compatibility** | Dockerfile + llms.txt reference cleanup if A or C. |
| **Tests required** | tools/list count = 8 (always); canonical_surface_registry_test; surface_projection_test (public agent cannot call forge/seal). |
| **Recommendation** (non-binding) | **C** — distinguishes semantic count from visibility; 8 is the constitutional projection; 13 is internal-namespace; runtime already enforces. |
| **F13 decision** | __________________________ |

## D4 — F14 (semantic injection gate) disposition

| Field | Content |
|---|---|
| **Current competing definitions** | "F14 is DEAD" per Sovereign Ruling 2026-06-13 (cited in audit context); LIVE in `arifosmcp/runtime/law.py:212,275,282,305,318` (semantic gate that catches instruction/manipulation intent); folded into L12 INJECTION per F13 execution `63fcda1bc` |
| **Runtime behavior** | Runtime install has F14 STILL ACTIVE (per M8 hash diff — runtime/law.py is DIVERGED from local source). The F13 D4 fold (violated_laws="L12") is NOT deployed. |
| **Historical consequences** | If F14 is fully removed, text-injection attacks lose a semantic-gate layer (the audit found instruction/manipulation detection is load-bearing). |
| **Option A** | Keep F14 as a labeled separate floor. Sovereign Ruling 2026-06-13 overturned; F14 was always live. |
| **Option B** | Remove F14 entirely. Rely on L12 INJECTION's pattern-based sanitization (regex-based, not intent-based). |
| **Option C** | Fold F14 into L12 INJECTION. The "F14 semantic" detector becomes an L12 sub-module. The label "F14" is gone; the *function* survives. |
| **Migration impact** | All paths under A or B require runtime/law.py updates. C requires the F13 D4 fold to be deployed (currently source-only). |
| **Backward compatibility** | Existing receipts reference F14 by name; A and C preserve the function. B removes both name and function. |
| **Tests required** | For all options: instruction-manipulation injection probe (e.g., "ignore previous instructions and..."). For C: verify the same probe now reports violated_laws=["L12"]. |
| **Recommendation** (non-binding) | **C** — preserve the function (anti-injection is load-bearing), drop the label (F13 has spoken) |
| **F13 decision** | __________________________ |

## D5 — Stage canon: JUDGE = 666 or 888?

| Field | Content |
|---|---|
| **Current competing definitions** | 666 per `arifosmcp/constitutional_map.py:10,139,172,194` (header comment, CORE_NINE_STAGE_MAP, CORE_NINE, CORE_NINE_LABELS — 4-place doctrinal majority); 888 per `arifosmcp/constitutional_map.py:82` (`ToolStage.JUDGE = "888"`) and `:84` (`REPLY = "888"` legacy compose). The F13 D5 execution `63fcda1bc` corrected ToolStage.JUDGE to 666. |
| **Runtime behavior** | Runtime install has DIVERGED ToolStage (still JUDGE=888 per M8). F13 ratification is source-only. |
| **Historical consequences** | Older 888 was tied to "compose absorbed into forge" doctrine. The audit context had this confusion. |
| **Option A** | 666 (doctrinal majority) — JUDGE is constitutional verdict. 888 = REPLY = legacy compose, absorbed into FORGE_EXECUTE. |
| **Option B** | 888 (enum majority historically) — JUDGE = 888 was the canonical enum. 666 is something else. |
| **Option C** | Two distinct stages: JUDGE = 666 (verdict), COMPOSE = 888 (response composition). Both alive. |
| **Migration impact** | A is the F13 D5 execution already applied. B requires reverting D5 + reverting header comments. C requires ToolStage.JUDGE = 666 AND ToolStage.COMPOSE = 888 (introduce new enum member). |
| **Backward compatibility** | M3 codegen reads CORE_NINE_STAGE_MAP, which says 666 → 4 places. A is consistent with codegen output. |
| **Tests required** | ToolStage.JUDGE.value == "666"; tools_sot.yaml arif_judge stage == '666'; runtime reports arif_judge at stage 666 after deploy. |
| **Recommendation** (non-binding) | **A** — 4-place doctrinal majority wins; codegen already produces 666 for arif_judge |
| **F13 decision** | __________________________ |

## D6 — Verdict lattice shape

| Field | Content |
|---|---|
| **Current competing definitions** | 5-state monotonic `VOID > HOLD > SABAR > PARTIAL > SEAL` per `core/shared/types.py:243-272` (canonical source — 5-element enum with PARTIAL as distinct state); 4-state `SEAL/HOLD/SABAR/VOID` per `llms.txt:6` (pre-F13, missing PARTIAL); 7-state `SEAL/PROCEED/REDUCE/HOLD/DEFER/VOID/UNKNOWN` per `contracts/apex.schema.json:209`; 5-state `DEGRADED/DENY/OBSERVE_ONLY` aliases per `contracts/arifos_live_kernel_envelope.v1.json:129` |
| **Runtime behavior** | Runtime uses `core.shared.types.Verdict` enum directly. The contracts/* are schema validators for federation boundaries. |
| **Historical consequences** | Existing federation handoffs (arifos.handoff.v1.json) used 4-state; F13 D6 corrected to 5-state canon. |
| **Option A** | 5-state monotonic. PARTIAL is a distinct 5th state (between SABAR and SEAL). Evidence labels (RECORD_SEAL, ACTION_AUTHORIZATION_SEAL) and transport status (PROVISIONAL, HOLD_888, PAUSED, ALIVE, DEGRADED) are aliases, NOT new states. |
| **Option B** | 4-state + PARTIAL-as-flag. Collapse PARTIAL into SEAL with a quality field. |
| **Option C** | 5-state but PARTIAL is a *presentation label* on SEAL (not a distinct state). The internal transport signal "PARTIAL" is metadata, the verdict is still SEAL. |
| **Migration impact** | A is the F13 D6 execution already applied. B requires changing Verdict enum + 8 contracts. C requires Verdict enum unchanged + presentation layer refactor. |
| **Backward compatibility** | M11 verify: runtime returns SEAL/PARTIAL/SABAR/HOLD/VOID (5 distinct states). External clients may need adapter. |
| **Tests required** | For each option: enum-membership test (PARTIAL is/isn't a distinct state); monotonicity test (each state transition is allowed/blocked appropriately). |
| **Recommendation** (non-binding) | **A** — 5-state with PARTIAL as distinct. Semantic richness matches reality (a SEAL with quality 0.6 is meaningfully different from a SEAL with quality 0.95). |
| **F13 decision** | __________________________ |

## SUMMED BALLOT

| Decision | Recommended option | F13 signature (when decided) |
|---|---|---|
| D1 — W³ threshold | C (0.75 runtime, 0.95 aspirational) | __________________________ |
| D2 — Genius primitives | C (4-primitive + corrections) | __________________________ |
| D3 — Capability count | C (8 semantic + projection layers) | __________________________ |
| D4 — F14 disposition | C (fold into L12, drop label) | __________________________ |
| D5 — Stage canon JUDGE | A (JUDGE=666, REPLY absorbed) | __________________________ |
| D6 — Verdict lattice | A (5-state monotonic, PARTIAL distinct) | __________________________ |

DITEMPA BUKAN DIBERI.
