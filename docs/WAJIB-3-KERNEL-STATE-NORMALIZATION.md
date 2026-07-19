# WAJIB 3 — Kernel State Normalization Spec

> **Forged:** 2026-07-19 | **Source:** Reality Verdict 58/100
> **Problem:** `LIMITED_MUTATE` vs `OBSERVE_ONLY` vs `actor_bound` vs
> `actor_verified` vs `mutation_allowed` vs `can_mutate` — multiple
> authority fields at different response levels report contradictory states.

## Root Cause

`session.py:554-568` documents the bug:
> "Prior bug: actor_verified alone → authority_mode=SOVEREIGN / verdict=FULL
> while top-level authority stayed LIMITED_MUTATE/OBSERVE_ONLY (dual source)."

The fix at line 558-568 attempted to mirror the authority band into
`session_birth` but did not eliminate the dual-source problem. The response
still emits authority at:
1. `session_birth.authority_mode` (line 562)
2. `session_birth.verdict` (line 565)
3. `session_birth.mutation_allowed` (line 566)
4. `clarity_contract.authority_band` (line 599)
5. `actor.authority_state.runtime_grant.level`
6. `actor.effective_action_authority`
7. `effective_verdict` (top-level)
8. `status` (top-level — "pending" vs "OK")

## Fix: Single Canonical effective_state

```json
{
  "effective_state": {
    "actor_verified": false,
    "authority_band": "OBSERVE_ONLY",
    "mutation_allowed": false,
    "seal_allowed": false,
    "verdict": "HOLD",
    "reason": "ACTOR_NOT_VERIFIED",
    "derived_from": "session_capability_token_v1",
    "computed_at": "2026-07-19T22:00:00Z"
  }
}
```

## Conformance Rule

**No field, UI, API, or MCP response may describe stronger authority
than the canonical effective_state.** All other authority-bearing fields
must derive from this single source or be removed.

## Implementation Plan

1. [ ] Extract authority computation into a single `compute_effective_state()` function
2. [ ] Remove `session_birth.authority_mode`, `session_birth.verdict` as separate fields
3. [ ] `session_birth.mutation_allowed` → derive from `effective_state.mutation_allowed`
4. [ ] `clarity_contract.authority_band` → derive from `effective_state.authority_band`
5. [ ] `actor.authority_state` → emit only as debug/internal, not public surface
6. [ ] `effective_verdict` → derive from `effective_state.verdict`
7. [ ] Add conformance test: `test_kernel_state_not_self_contradictory` in conformance/kernel/test_authority.py
8. [ ] Verify: all existing tests still pass after refactor

## Affected Files

- `/root/arifOS/arifosmcp/tools/session.py` — primary (lines 540-600)
- `/root/arifOS/arifosmcp/tools/kernel_canonical.py` — bridge authority propagation
- `/root/arifOS/arifosmcp/schemas/kernel_envelope.py` — envelope types
- `/root/arifOS/conformance/kernel/test_authority.py` — conformance test

**DITEMPA BUKAN DIBERI.**
