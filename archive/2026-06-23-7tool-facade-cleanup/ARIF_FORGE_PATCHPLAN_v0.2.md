# ARIF_FORGE_PATCHPLAN_v0.2
## arifOS MCP Tool Audit → Gap Analysis → Canonization Roadmap
## Version: 0.2 (post-fix)
## Date: 2026-05-16
## Status: PARTIAL — 5 of 16 tools fixed; 11 items require 888_HOLD or Arif confirmation

---

## Executive Summary

Full MCP tool audit of all 16 arifOS tools (13 canonical + 2 diagnostic probes + 1 bonus)
was completed via `/mcp` JSON-RPC endpoint against `ghcr.io/ariffazil/arifos:e03b9ac`.

**Result: 2 CRITICAL (P0), 5 HIGH/DEGRADED (P1), 6 MEDIUM, 5 WORKING**

5 code fixes applied in this session (P1-FIX-4, P1-REPAIR-4, P2-OBS-1, P2-OBS-2, P1-FIX-2).
11 items remain: 6 require 888_HOLD (irreversible deploy/secret), 2 require Arif SEA-LION confirmation,
3 ToM infrastructure stubs are 888_HOLD pending ToM roadmap.

---

## Source of Truth
- `arifosmcp/constitutional_map.py` — canonical tool registry + 13-tool manifest
- `arifosmcp/tool_registry.json` — generated JSON manifest
- `arifosmcp/tools/` — source of truth for all tool implementations
- Runtime: `http://localhost:8080/mcp` (streamable-http)

---

## Applied Fixes (v0.2 — This Session)

### P1-FIX-4: arif_memory_recall stats() layer_counts ✅
**File:** `arifosmcp/tools/memory_recall.py` (line ~320)
**Problem:** `stats()` returned 8 keys but was missing `layer_counts` for sessionless metadata.
The 6-layer memory architecture (L1 ephemeral, L2 session, L3 qdrant, L4 postgres,
L5 graphiti, L6 vault999) was not surfaced.
**Fix:** Added `layer_counts` dict to `stats()` return, mapping storage backends to layers.
```python
base_stats["layer_counts"] = {
    "L1_ephemeral": base_stats.get("legacy_files", 0),
    "L2_session": base_stats.get("by_session", {}),
    "L3_qdrant": base_stats.get("qdrant_vectors", 0),
    "L4_postgres": base_stats.get("postgres_records", 0),
    "L5_graphiti": "unavailable_in_memory_store",
    "L6_vault999": "append_only_ledger",
}
```
**Verification:** `arif_memory_recall(mode="stats")` now returns `layer_counts` key.
**Evidence anchor:** ARIF report §4, 13-tool manifest §555, audit finding MEM-01.

---

### P1-REPAIR-4: arif_gateway_connect discover federation organs ✅
**File:** `arifosmcp/tools/gateway.py` (line ~33)
**Problem:** `mode=discover` returned only `["kimi", "claude", "gemini"]` — missing all 6
federation organs (AAA, A-FORGE, GEOX, WEALTH, WELL, APEX).
**Fix:** Added federation organs to the discover agent list with comments explaining
internal A2A mesh vs. external bridge protocol distinction.
```python
"agents": [
    # Federation organs (internal A2A mesh)
    "AAA", "A-FORGE", "GEOX", "WEALTH", "WELL", "APEX",
    # External bridge agents
    "kimi", "claude", "gemini",
]
```
**Verification:** `arif_gateway_connect(mode="discover")` now returns 9 agents.
**Evidence anchor:** ARIF report §4, 13-tool manifest §666g, audit finding GATE-01.

---

### P2-OBS-1: arif_kernel_route status stage hardcoded '000' ✅
**File:** `arifosmcp/tools/kernel.py` (line ~116 + function signature)
**Problem:** `mode=status` returned `stage: "000"` as hardcoded fallback. Also added missing
`session_id` parameter to function signature.
**Fix:** Added `session_id: str | None = None` to `arif_kernel_route` parameters. When
`session_id` is provided, resolves live stage from `_SESSIONS[session_id]["stage"]`.
Falls back to passed `stage` parameter, or "unknown" if neither is set.
```python
live_stage = "unknown"
if session_id:
    sess = _SESSIONS.get(session_id, {})
    live_stage = sess.get("stage", stage or "unknown")
elif stage:
    live_stage = stage
return _ok("arif_kernel_route", {
    "stage": live_stage,
    "stage_source": "session" if session_id else ("parameter" if stage else "unknown"),
    ...
})
```
**Verification:** `arif_kernel_route(mode="status", session_id="<active>")` returns actual stage.
**Evidence anchor:** ARIF report §4, 13-tool manifest §444, audit finding KERNEL-01.

---

### P2-OBS-2: arif_ops_measure vitals hardcoded g_score/delta_S/omega ✅
**File:** `arifosmcp/tools/ops.py` (line ~129)
**Problem:** `mode=vitals` returned hardcoded values: `g_score=0.98, delta_S=0.001, omega=0.95`.
**Fix:** Wired to live thermodynamic telemetry:
- Primary: `core.physics.thermodynamics_hardened.get_thermodynamic_report()`
- Secondary: `arifosmcp.core.cooldown_engine.get_cooldown_engine().vitals()`
- Fallback: hardcoded defaults with `source: "default_unavailable"` flag
```python
live_vitals = {"g_score": 0.97, "delta_S": 0.002, "omega": 0.95, "source": "default"}
try:
    from core.physics.thermodynamics_hardened import get_thermodynamic_report
    thermo = get_thermodynamic_report()
    live_vitals["g_score"] = thermo.get("G_star", 0.97)
    live_vitals["delta_S"] = thermo.get("entropy_delta", 0.002)
    live_vitals["omega"] = thermo.get("omega", 0.95)
    live_vitals["source"] = "thermodynamic_report"
except Exception:
    # cooldown_engine fallback...
```
**Verification:** `arif_ops_measure(mode="vitals")` returns live values with `source` field.
**Evidence anchor:** ARIF report §4, 13-tool manifest §777, audit finding OPS-01.

---

### P1-FIX-2: arif_heart_critique VAULT999_PATH hardcoded ✅
**File:** `arifosmcp/tools/heart.py` (line ~25)
**Problem:** `_VAULT999_PATH` used hardcoded `/root/arifOS/arifosmcp/VAULT999/SEALED_EVENTS.jsonl`.
Inside the container (user `arifos`, uid 1000), this path is inaccessible (host `/root/` is mode 700).
**Fix:** Use `ARIFOS_VAULT_PATH` env var with correct container path fallback:
```python
_VAULT999_PATH = Path(os.getenv(
    "ARIFOS_VAULT_PATH",
    "/var/lib/arifos/vault/outcomes.jsonl",
))
```
**Note:** `/var/lib/arifos/vault/outcomes.jsonl` is the correct container path (verified
writable by `arifos` user). Host path `/root/VAULT999/` is NOT accessible from inside
the container. The `ARIFOS_VAULT_PATH` env var should be set in the Docker compose.
**Evidence anchor:** ARIF report §4, 13-tool manifest §666, audit finding HEART-01.

---

## Remaining Items (888 HOLD Required)

### P0-FIX-1: arif_vault_seal depth=0 always returns empty ❌
**File:** `arifosmcp/core/vault999/vault_ledger.py` or `vault_writer.py`
**Problem:** `arif_vault_seal` with `depth=N` returns 0 entries regardless of N > 0.
Root cause: `_VAULT_LEDGER` is in-memory list initialized empty at module load.
Container `ghcr.io/ariffazil/arifos:e03b9ac` has original bug; `fix-vault-reader` branch
has the fix but it was never merged to `main`.
**Fix (ready):** Ensure `_VAULT_LEDGER` is populated from `/var/lib/arifos/vault/outcomes.jsonl`
on startup, OR read directly from the JSONL file for depth queries.
**Action required:**
1. Merge `fix-vault-reader` branch to `main` (git merge)
2. Rebuild container: `make deploy-local` or `docker build`
3. Deploy to VPS: `make publish-ghcr` + VPS rsync
4. Verify: `arif_vault_seal(mode="list", depth=5)` returns actual entries
**888_HOLD REASON:** Requires container rebuild + production deploy.

---

### P0-FIX-2: arif_evidence_fetch evidence receipts permission denied ❌
**File:** `arifosmcp/runtime/reality_handlers.py` (suspected)
**Problem:** Evidence receipts cannot be written. Container user `arifos` (uid 1000) cannot
write to host `/root/VAULT999/evidence/receipts/` (mode 700). Correct container path is
`/var/lib/arifos/vault/evidence/receipts/`.
**Fix:** Code change ready (env var approach). Deploy = 888_HOLD.
**888_HOLD REASON:** Requires container rebuild + production deploy.

---

### P1-FIX-1: arif_heart_critique SEA-LION wiring ❌
**Problem:** Audit shows `_llm_available: false` even when SEA-LION should be reachable.
"deceptive marketing campaign" returned `risk_tier: GREEN` — false negative on clear
F05/F06/F09 violation. The 3-tier fallback (SEA-LION → Ollama → keyword) is structurally
correct in `llm_client.py`, but the container may not have SEA_LION_API_KEY configured.
**Fix options:**
1. Confirm SEA-LION endpoint + provide API key (Tier 1 primary)
2. Verify Ollama is reachable at `http://ollama:11434` (Tier 2 fallback)
3. Container env needs: `SEA_LION_API_KEY`, `SEA_LION_BASE_URL`, `SEA_LION_MODEL`
**Action required from Arif:** Confirm SEA-LION credentials or approve fallback-only mode.
**888_HOLD REASON:** Requires sovereign confirmation for SEA-LION API key.

---

### P1-FIX-2 (ARCH-001): arif_mind_reason forge dispatch bleed ❌
**File:** `arifosmcp/tools.py` at `tools.py:1338` (suspected)
**Problem:** MEMORY.md flags `_arif_mind_reason` at `tools.py:1338` as having a `forge`
dispatch path. This is an architectural issue — `mind_reason` should not dispatch to `forge`.
**MEMORY.md note:** "requires sovereign review before surgical removal"
**Action required from Arif:** Confirm removal of forge dispatch path from mind_reason.
**888_HOLD REASON:** Requires sovereign review (ARCH-001 per MEMORY.md).

---

### TOM-1 through TOM-4: ToM Infrastructure Stubs ❌
**All 4 ToM (Theory of Mind) stubs are 888_HOLD pending:**
1. TOM-1: Self-model persistence layer (AAA integration)
2. TOM-2: Counterfactual reasoning engine (apex_self_model)
3. TOM-3: ToM projection primitives (self_other_distinction)
4. TOM-4: ToM readiness dashboard (WELL integration)
**888_HOLD REASON:** Require Arif + AAA confirmation before any ToM work.

---

## Tool Health Summary (Post-Fix v0.2)

| Tool | P0/P1/P2 | Status After Fix | Notes |
|------|----------|-----------------|-------|
| arif_session_init | — | WORKING | Init/anchor tool |
| arif_judge_deliberate | — | WORKING | 888_JUDGE apex |
| arif_vault_seal | P0 | BROKEN | depth=0 bug; 888_HOLD |
| arif_mind_reason | P1 | DEGRADED | ARCH-001 forge bleed; 888_HOLD |
| arif_heart_critique | P1 | DEGRADED | SEA-LION unwired; 888_HOLD |
| arif_reply_compose | — | WORKING | Reply synthesis |
| arif_kernel_route | P2 | FIXED ✅ | stage hardcoded; now live |
| arif_gateway_connect | P1 | FIXED ✅ | discover missing organs |
| arif_memory_recall | P1 | FIXED ✅ | layer_counts added |
| arif_ops_measure | P2 | FIXED ✅ | hardcoded vitals; now live |
| arif_sense_observe | — | WORKING | 8-stage reality pipeline |
| arif_evidence_fetch | P0 | BROKEN | evidence receipts perms; 888_HOLD |
| arif_forge_execute | — | WORKING | Sovereign forge only |
| arif_anti_sink_check | — | DEGRADED | 4 of 8 fields unknown |
| institutional_drift_check | — | DEGRADED | Static heuristics |
| arif_stack_health_probe | — | WORKING | Full federation probe |

**Fixed this session:** 5 (P1-FIX-4, P1-REPAIR-4, P2-OBS-1, P2-OBS-2, P1-FIX-2)
**888_HOLD remaining:** 6 (P0-FIX-1, P0-FIX-2, P1-FIX-1, ARCH-001, TOM-1..4)
**Working:** 5
**Still degraded:** 2 diagnostic probes

---

## ToM Readiness Roadmap (BLOCKED — 888_HOLD)

```
TODAY ────────────────────────────────────────────────────────
│
├─ ToM Infrastructure Stubs (TOM-1 → TOM-4) [ALL 888_HOLD]
│   ├─ TOM-1: Self-model persistence (AAA integration)
│   ├─ TOM-2: Counterfactual engine (apex_self_model)
│   ├─ TOM-3: ToM projection primitives
│   └─ TOM-4: ToM readiness dashboard (WELL integration)
│
FUTURE (after 888_HOLD cleared) ────────────────────────────────
│
├─ Phase 1: Self-Model Grounding
│   ├─ Extend arif_memory_recall to expose self-model reads
│   ├─ Wire self_model to arif_mind_reason (replace ARCH-001 dispatch)
│   └─ Add TOM-1 to tool surface
│
├─ Phase 2: Counterfactual Reasoning
│   ├─ Build TOM-2 counterfactual engine (if/else world projection)
│   ├─ Wire to arif_judge_deliberate (ASI layer)
│   └─ C_dark ToM component integration (F09 Anti-Hantu)
│
└─ Phase 3: ToM Projection + WELL Integration
    ├─ Implement TOM-3 self_other_distinction
    ├─ Build TOM-4 readiness dashboard
    └─ Integrate with WELL state (W-MELLON signals)
```

**Blocker for all ToM work:** Arif + AAA confirmation on ToM roadmap.
F9 Anti-Hantu (C_dark ToM component) and F10 Ontology (self-model) are both
hard floors that require ToM infrastructure to be done correctly.

---

## Breaking Change Register

The following changes introduce potential breaking changes to the tool surface:

| Change | File | Risk | Mitigation |
|--------|------|------|------------|
| `layer_counts` key added to stats() response | memory_recall.py | Low — additive | Consumer handles unknown keys |
| `stage_source` field added to kernel status | kernel.py | Low — additive | Consumer handles unknown keys |
| Federation organs added to discover agents | gateway.py | Low — additive | Consumer handles unknown keys |
| `source` field added to vitals response | ops.py | Low — additive | Consumer handles unknown keys |
| `_VAULT999_PATH` env var changed | heart.py | Medium — path semantics changed | Set `ARIFOS_VAULT_PATH` in container env |

---

## Audit Trail

- **ARIF canonical source:** `/root/arifOS/arifosmcp/constitutional_map.py`
- **13-tool manifest:** `arifosmcp/tool_registry.json` (generated from constitutional_map.py)
- **Patch plan v0.1:** Previous session working notes
- **Patch plan v0.2:** This document
- **Memory reference:** `/root/MEMORY.md` (ARCH-001, WEALTH-002, GEOX-006)
- **arifOS version:** `v2026.05.05-SSCT`, git `e03b9ac`
- **Container image:** `ghcr.io/ariffazil/arifos:e03b9ac`

---

*DITEMPA BUKAN DIBERI — Forged, Not Given*
*This document is a working design artifact. All 888_HOLD items require Arif confirmation before action.*
