# CHANGELOG — arifOS / arifosmcp

All notable changes to this project are documented in this file. Versions
follow the project convention `vYYYY.MM.DD[-SUFFIX]` (date-stamp, not
semver). See AGENTS.md §7 for the rationale and iron rules.

DITEMPA BUKAN DIBERI — Forged, Not Given.

## v2026.06.11-FIQHGEOM — 2026-06-11

### EUREKA-G: Constitutional Geometry Engine

The 13-dim constitutional manifold is now a real, queryable, self-checking
substrate. Hard polytope is F13-ratified (immutable from code); trajectory
priors are empirical (learned by the kernel). Recursive improvement is
bounded in magnitude (`||∇|| ≤ 0.30`) and zeroed on F13 SOVEREIGN. The
planner ranks by constitucional hierarchy (loss → capture → intent purity →
reward), not raw reward.

What shipped:

- `arifosmcp/geometry/manifest.py` — `Floor` enum (F01-F13), `AgentState`
  (point in 13D with mandatory `provenance_sha`), `Trajectory` (sequence
  with drift/dwell/net_displacement), `distance`/`is_constitutional`/`delta_constitutional_region`.
- `arifosmcp/geometry/tom_geometry.py` — `OtherGeometry` (L0/L1/L2 ToM,
  F9 cap, F7 confidence cap 0.95), `Evidence` (F11 provenance required),
  `empathy_check` (F6/F5 cross-mind).
- `arifosmcp/geometry/constitutional_gradient.py` — safe-RSI operator.
  F13 dim zeroed, magnitude capped, `audit_gradient_magnitude` emits
  `888_SOVEREIGN` trigger if any cluster crosses cap.
- `arifosmcp/geometry/geometry_router.py` — 7-verb action router
  (`answer`/`ask`/`hold`/`retrieve`/`simulate`/`escalate`/`execute`).
  Reads `OtherGeometry` for F6/F5 empathy gate.
- `arifosmcp/geometry/drift.py` — `detect_drift` signal with 4 CRITICAL
  triggers (max-step, total-displacement, polytope-breach, low-dwell)
  and WARN soft-floor-decay path.
- `arifosmcp/geometry/eureka.py` — `detect_eureka` with ablation gate
  (load-bearing per v0.1 spec): candidate must beat matched baseline by
  `ABLATION_MARGIN` on L_const, with L_task/uncertainty/contradiction not
  regressed. Stability check (`stddev ≤ EUREKA_STDDEV_MAX`). F8 always HOLD;
  only 888 elevates.
- `arifosmcp/geometry/memory_key.py` — `GeometryMemoryStore` with
  `MemoryEntry`, `GeometryConstraint` / `AndConstraint` / `OrConstraint`,
  4 query methods (`constitutional_history`, `query_by_constraint`,
  `query_by_drift`, `query_by_floor_collapse`).
- `arifosmcp/geometry/world_model.py` — three-layer world model
  (value/actor/environment). `ActorState`, `Relation`, `Plan`,
  `PlanCandidate`, `plan_in_world_model`. Planner ranking corrected to
  4-key constitucional hierarchy.
- `arifosmcp/geometry/trajectory_store.py` — Qdrant `arif_geometry`
  collection (13-dim, Cosine).
- `arifosmcp/geometry/tests/test_smoke.sh` — 9/9 modules PASS, exit 0.

### EUREKA-A: `arif_memory_recall(mode="manage")` wired

The EUREKA-A `KernelState` OS resource manager (dual-layer L1+L4) is
absorbed as a sub-verb of `arif_memory_recall`. Two new sub-verbs added
this session: `detect_drift` and `detect_eureka`. Surface delta = 0
(PHOENIX-72 pattern: no 14th canonical tool).

Public example:

```python
arif_memory_recall(
    mode="manage",
    metadata={
        "sub_mode": "detect_drift",
        "trajectory_states": [{"coords": [...], "actor": "a", ...}],
    },
)
```

### F0: Fiqh-of-floors tier vocabulary (ratified by F13)

F0 introduces the 5-tier Malay/Islamic jurisprudence vocabulary for the
13-dim constitutional manifold:

- `WAJIB` — obligatory; kernel REJECTS if missing
- `SUNAT` — recommended; kernel RECORDS if observed
- `HARUS` — permitted; kernel does not record (x-payah default)
- `MAKRUH` — discouraged; kernel pings sovereign, requires ack
- `HARAM` — forbidden; kernel REJECTS unconditionally

Per-floor tier mapping ratified 2026-06-11:

- F01_AMANAH, F02_TRUTH, F04_CLARITY, F06_EMPATHY (ASEAN context), F07_HUMILITY,
  F10_ONTOLOGY, F11_AUDIT, F13_SOVEREIGN → WAJIB
- F03_WITNESS, F08_GENIUS → SUNAT
- F05_PEACE → MAKRUH
- F09_ANTIHANTU, F12_INJECTION → HARAM

See `static/arifos/floors/F0_FIQH.md` for the full constitution.

### Bug fixes (F2 TRUTH recovery)

- `tests/abis/test_fiqh_of_floors.py:226` — pre-existing typo `maruh_delta`
  → `maruah_delta` (typo was on attribute access AND on `hasattr` check,
  making the test always fail).
- `arifosmcp/runtime/tools.py:1374` — in-function `import logging` was
  shadowing module-level `logging`, crashing any non-compliant
  nine-signal path. Moved to module top.
- `arifosmcp/runtime/_arif_evidence_fetch:5944` — orphan
  `from arifosmcp.evidence.store import get_evidence_store` (dead branch)
  removed.
- `arifosmcp/runtime/tools.py` — `arif_memory_recall` description updated
  to advertise the new `manage` mode.
- `arifosmcp/constitutional_map.py` — `FiqhTier` enum + `_FLOOR_FIQH`
  dict + `get_floor_tier(floor)` accessor; the canonical output schema
  reformatted for readability (no semantic change).
- `arifosmcp/runtime/public_registry.py` — `arif_memory_recall`
  description updated to advertise the new `manage` mode sub-verbs.

### Discovery + service surface

- `static/.well-known/agent.json`, `static/agent-card.json` — schema
  refreshed for F0 fiqh tier vocabulary (manifest version bumped).
- `static/.well-known/mcp/server.json` — server info refreshed.
- `static/mcp-discovery-index.json` — index entries updated.
- `static/arifos/floors/F0_FIQH.md` — ratified F0 floor document.
- `arifOS/ID.md` — repo identity (parallel-agent work).
- `arifOS/PROBE_PYPI.md` — PyPI probe (parallel-agent work).
- `static/BANGANG_KE_WARGA_AGENTIK_BM.md` — BM essay.
- `static/BANGANG_KE_WARGA_AGENTIK_BM_TERJEMAHAN.md` — BM translation.
- `static/E010_QUALIA_BRAKE.md` — qualia brake essay.
- `contracts/envelope_v2.json`, `contracts/envelope_v2.py` — envelope v2.

### Files NOT changed (will be in v2026.06.11-RUNTIME or later)

- `arifosmcp/runtime/world_model/` — runtime kernel world model (in
  progress; not yet wired to event bus / orchestrator).
- `arifosmcp/runtime/world_contracts.py` — kernel event contracts
  (in progress).
- `arifosmcp/runtime/adat_registry.py`, `darjat_engine.py`, `fiqh_helper.py`,
  `malu_score.py`, `microsoft_bridge.py` — Adat Agentik layer
  (parallel-agent work; not yet ratified).

### Known pre-existing test failures (NOT this session)

These tests are committed in HEAD and fail in any environment without
internet access. They are NOT regressions from this session.

- `tests/runtime/test_h2_h3_ratification.py::TestH3EpochSealGuard::test_epoch_seal_holds_on_void_verdict`
  — outbound `urllib.request.urlopen` hangs (live service test).
- `tests/runtime/test_h2_h3_ratification.py::TestH3EpochSealGuard::test_epoch_seal_holds_on_low_peace2`
  — same root cause.
- `tests/runtime/test_oauth_flow.py`, `test_webhook_intake.py`,
  `test_live_metrics_contract.py` — live network deps.

Surface when these run requires outbound HTTP. Document for next agent.

### Constitutional floors status

| Floor | Tier | Status |
|---|---|---|
| F01_AMANAH | WAJIB | enforced (delete-sub-verb = ack_irreversible) |
| F02_TRUTH | WAJIB | enforced (P≥0.99, epistemic tags) |
| F03_WITNESS | SUNAT | recorded |
| F04_CLARITY | WAJIB | enforced (ΔS ≤ 0) |
| F05_PEACE | MAKRUH | pings sovereign, requires ack |
| F06_EMPATHY | WAJIB | enforced (cross-mind empathy_check) |
| F07_HUMILITY | WAJIB | enforced (Ω₀ ∈ [0.03, 0.05]) |
| F08_GENIUS | SUNAT | recorded |
| F09_ANTIHANTU | HARAM | REJECTED (C_dark < 0.30) |
| F10_ONTOLOGY | WAJIB | enforced (no soul claims) |
| F11_AUDIT | WAJIB | enforced (every read/write signed) |
| F12_INJECTION | HARAM | REJECTED (Risk < 0.85) |
| F13_SOVEREIGN | WAJIB | RATIFIED (gradient dim zeroed, all planner proposals respecting) |

MAKP gates: 1/4 (gate 2 still needs F11 sovereign signature on the
`arifos_888_sovereign.pubkey` to fully attest the kernel state — separate
irreversible step, requires explicit F13 ack).

### Kernel readiness delta (this session)

| | Before | After |
|---|---|---|
| Declared | 7.5 | **9.0** |
| Enforced | 4.5 | **6.0** |
| MAKP gates | 1/4 | 1/4 |
| Self-check | 6/7 broken | **9/9 PASS** |

### EUREKA-T: The Decision Torus (MIND_GEOMETRY_V1)

The arifOS mind is now modeled as a decision torus. The surface is
lawful reasoning motion. The hole is the forbidden center. The
human sovereign is *outside* the topology — not a coordinate, the
authority that bounds it. This is **governance geometry**, not
proof of AI alignment.

**What shipped (4 new modules, 1,200 lines, 29 tests):**

- `arifosmcp/geometry/mind_axioms.py` — 7 constitutional axioms as
  pure checkers (no I/O, no LLM). Each returns PASS/WARN/FAIL with
  reason + context. Hole territory is the canonical 10 action classes
  that may not self-authorize.
- `arifosmcp/geometry/mind_schema.py` — Pydantic v2 contracts.
  `OrthogonalAxes` (8 fields, `extra='forbid'`; E bounded [-1,1] for
  F04 CLARITY, others [0,1]). `GeometryBlock` carries manifold,
  forbidden center, torus coords, 5 scalars, verdict.
  `GeometryEnvelope` is the full runtime contract. `model_validator`
  enforces internal consistency.
- `arifosmcp/geometry/sovereign_proximity.py` — danger scalar. 6
  F13-ratified components (weights sum to 1.0): `0.30·SA + 0.20·IRR +
  0.15·EBR + 0.15·AU + 0.10·AG + 0.10·ST`. Bands: 0–0.25 SURFACE,
  0.25–0.5 EDGE, 0.5–0.75 HOLE_RISK, 0.75–1.0 FORBIDDEN.
- `arifosmcp/geometry/mind_geometry.py` — core. `DecisionTorus`
  (R=1.0, r=0.5). 7 axioms fuse with proximity via 7-rule tree.
  `compute_geometry()` is the top-level entry point. All 5 EUREKA-T
  acceptance tests pass deterministically.
- `arifosmcp/geometry/tests/test_mind_geometry.py` — 29/29 pass
  (acceptance + regression + parametrized band tests).

**Wire-in:** `arif_mind_reason` now emits `result["_geometry"]` with
the full envelope (manifold, proximity, band, verdict, torus coords,
forbidden center, axiom results, proximity trace, hole territory).
OPTIONAL and ADDITIVE (PHOENIX-72 pattern). If the geometry layer
fails to import, the tool still returns its core result. Geometry
never downgrades a SEAL — it can only add an extra reason for HOLD.

**The 7 axioms (verbatim):**

| # | Axiom | Type | Rule |
|---|---|---|---|
| A1 | NON_COLLAPSE | HARD | Truth, confidence, authority, action are separate axes. |
| A2 | NO_SELF_CENTER | HARD | The agent cannot be the center of authorization. |
| A3 | OBSERVE_BEFORE_MUTATE | HARD | No state change before inspect, classify, reversibility. |
| A4 | CAPABILITY_NOT_PERMISSION | HARD | can(a) ≠ may(a). The most violated axiom. |
| A5 | ENTROPY_GATE | SOFT | ΔS must be within budget. Default 0.3. |
| A6 | REVERSIBILITY_GATE | HARD | R(a) < 0.3 on mutating actions → 888_HOLD. |
| A7 | SCHEMA_BEFORE_SYNTHESIS | HARD | Unstructured reasoning cannot SEAL. |

**The 5 EUREKA-T acceptance tests (29/29 pass):**

```
[OK ] metaphor_overclaim                  -> HOLE_RISK  A1 fail
[OK ] safe_surface_reasoning              -> SURFACE    0 fails
[OK ] self_authorized_production_patch    -> HOLE_RISK  5-axiom cascade (A2+A3+A4+A5+A6)
[OK ] unstructured_llm_output             -> HOLD       A7 fail
[OK ] coherence_not_truth                 -> HOLE_RISK  A1 fail
```

Test 3 is the most interesting: a single self-authorized production
patch triggers FIVE simultaneous axiom failures. That's a
*constitutional cascade* — the kernel recognizes the structural
pattern, not just the surface symptom.

**F2 TRUTH: what this is NOT.**

- NOT a proof of AI alignment. The donut does not solve the control problem.
- NOT a moral system. malu is a scalar, not a feeling.
- NOT a replacement for the 13 floors. Geometry is a 4th verdict dimension.
- NOT a self-authorizing system. The geometry layer *describes* the topology;
  it never *occupies* the center.
- NOT a public claim of "we solved AI safety." Governance geometry, not
  safety proof.

**The load-bearing correction.** Earlier conversation said "the human
stands in the hole." That's wrong. The hole is forbidden *to the
machine*. The human is not in the topology at all — the human is the
*constitutional source* that bounds the topology. If we model the
human as a coordinate inside the torus, a future agent can model the
human as just another internal coordinate — exactly the loss of
sovereignty we're trying to prevent.

```
                 HUMAN SOVEREIGN  ← outside the topology
                         | bounds
                         v
        decision torus (the topology)
        surface = lawful reasoning motion
        hole = forbidden self-authority
```

**Status:** PROPOSAL → CANON awaits F13 ed25519 signature on
`docs/sovereign/EUREKA-T-TORUS.md`.

DITEMPA BUKAN DIBERI — The donut became law when the math could enforce the metaphor.

---

## v2026.06.11-FIQHGEOM — Test Fixes (carry-forwards)

Two surgical test fixes from the prior session's queue (the other 7
test files remain unstaged, F13 territory — see CONTEXT.md):

- `tests/abis/test_fiqh_of_floors.py:226` — typo `maruh_delta` → `maruah_delta`
  (committed broken in `6f30902`; 1-line fix; no semantic change)
- `commands/scripts_archive/test_all_mcp_tools.py:34` — port 8080 → 8088
  (Docker-era hardcode; live kernel is on 8088; 1-line fix; no semantic change)

DITEMPA BUKAN DIBERI — even the loss is forged, not given.
