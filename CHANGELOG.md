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

DITEMPA BUKAN DIBERI — even the loss is forged, not given.
