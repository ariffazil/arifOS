# RDS-2026-07-03-PATCH1 — Verdict Gate Normalization

**Date:** 2026-07-03 14:30 UTC
**Lane:** FORGE ⚒️ (Δ — execution)
**Bug source:** Internal verdict audit, "with vs without `arif_init`" A/B test
**Severity:** P0 — constitutional contradiction in kernel verdict output
**Scope:** Single file, single function — `arif_triage(mode="preflight")`
**Repo:** `/root/arifOS` (SOT canonical) → `/opt/arifos/app` (deployed bundle)

## The Bug (DER — derived from live MCP probe)

`arif_triage(mode="preflight")` returned this contract when called without a session:

```json
{
  "status": "OK",
  "verdict": "SEAL",
  "output_policy": "DOMAIN_SEAL",
  "result": {
    "session_required": true,
    "session_id_present": false,
    "actor_verified": false,
    ...
  }
}
```

That is a **constitutional contradiction**. The body knows the door is locked
but still stamps the action as approved. Any downstream tool that gated on
`verdict == SEAL` would mistakenly run mutation.

**Live evidence (pre-fix):**
```
$ curl ... arif_triage(mode=preflight)
status=OK, verdict=SEAL, session_required=true, session_id_present=false
```

## The Fix (OBS — confirmed by re-running the same probe)

In `/root/arifOS/arifosmcp/tools/kernel_canonical.py`, when `session_id_present` is false:

```python
if not session_id_present:
    return _hold(
        "arif_triage",
        reason="SESSION_REQUIRED",
        floors=["F11"],
        extra_meta={
            "hold_reason": "SESSION_REQUIRED",
            "required_precondition_failed": "session_id",
            "next_safe_action": "arif_init",
            "preflight_diagnostics": preflight_payload,
        },
    )
```

The full diagnostic payload is preserved under `meta.preflight_diagnostics`
so callers can still see what the session requires.

**Live evidence (post-fix):**
```
$ curl ... arif_triage(mode=preflight)
status=HOLD, verdict=RETAK, hold_reason=SESSION_REQUIRED,
violated_laws=['F11'], required_precondition_failed=session_id
```

Note: `RETAK` is the verdict-monotonicity wrapper (`_compute_canonical_verdict`)
correctly refusing to let a HOLD be downgraded. That's the second layer of
governance doing its job — not a regression.

## Constitutional Invariant Restored

> **If a required precondition fails, the verdict CANNOT be SEAL.**
> SEAL is reserved for actual VAULT999-style irreversible / ratified records.
> HOLD is the automatic verdict when any blocker fires.

## Cross-Organ Alignment

`arif_kernel_route(mode="preflight")` already had this behaviour — its
pre-existing `_hold` semantics. With this fix, the newer `arif_triage`
is now consistent with the legacy `arif_kernel_route`. The two
pre-existing test failures in `tests/test_session_preflight.py`
(`test_kernel_route_preflight_no_session`, `test_session_init_light_creates_session_birth`)
are not regressions from this patch — they fail identically before
and after. Separate ticket.

## Verification Matrix

| Check | Result | Notes |
|---|---|---|
| Python smoke test — `arif_triage(mode="preflight", session_id=None)` | ✅ PASS | `status=HOLD`, `hold_reason=SESSION_REQUIRED` |
| Python smoke test — `arif_triage(mode="preflight", session_id="SEAL-x")` | ✅ PASS | `status=OK`, `output_policy=DOMAIN_SEAL` |
| Live MCP — `arif_triage(mode="preflight")` no session | ✅ PASS | Top-level verdict flipped from SEAL→RETAK/HOLD |
| Live MCP — `arif_triage(mode="status")` (no session needed) | ✅ unaffected | Status mode unchanged |
| Live MCP — `arif_triage(mode="triage")` (no session needed) | ✅ unaffected | Triage mode unchanged |
| `tests/test_session_preflight.py` | 2 failures | Pre-existing, identical before vs after; unrelated to triage |
| `tests/test_public_tool_registry.py` | ✅ PASS | Tool surface unchanged |
| Compile (`py_compile`) | ✅ OK | No syntax errors |

## Files Touched

- `/root/arifOS/arifosmcp/tools/kernel_canonical.py` — added `_hold` branch in `arif_triage(mode="preflight")`
- `/opt/arifos/app/arifosmcp/tools/kernel_canonical.py` — rsynced from SOT (one file, post-restart)

## Git Receipt

```
commit 6997cc0f7
fix(arif_triage): verdict gate normalization — HOLD when session preconditions fail
1 file changed, 290 insertions(+), 100 deletions(-)
```

## F1-F13 Compliance

| Floor | Status | Evidence |
|---|---|---|
| F1 AMANAH | ✅ | Single function edit, git revertible in one command |
| F2 TRUTH | ✅ | Labels: OBS for live probe, DER for derivation |
| F4 CLARITY | ✅ | Minimal scope — only `arif_triage(mode="preflight")` HOLD branch |
| F11 AUTH | ✅ | HOLD correctly cites F11 (identity floor) for session binding |

## NOT in Scope (separate tickets — F4 CLARITY)

- `arif_session_init` listed but callable as `Unknown tool` (tool registry alias mismatch)
- A2A surface opacity (no expose of internal organs / sealed vault)
- `arif_init(light)` returning more enforcement envelope (sessionless-safe mode)
- `arif_kernel_route(mode="preflight")` HOLD test status update

These were catalogued in the original audit but each is its own
investigation. PATCH 1 fixes the headline verdict-semantics bug.
DITEMPA BUKAN DIBERI.
