# FORGE EVIDENCE: LeaseGuard Hard-Block (Phase 1)

**Forge ID:** lease-hard-block-v1  
**Date:** 2026-06-14 01:41 UTC  
**Forger:** FORGE (000Ω) / OPENCLAW  
**Judge:** arif_judge_deliberate  
**Sovereign:** Arif (F13)  
**Verdict:** SEAL (forge complete, awaiting deploy)  

## Summary

Changed the P2-7 Lease Gate in `_arif_forge_execute` from **warn-and-proceed** to **hard-block** for all mutation-class forge modes.

Before: mutation without lease → LEASE_AWARENESS (informational), execution proceeds  
After: mutation without lease → HOLD (hard block), execution stopped  

This is the constitutional circuit breaker. No mutation without bounded, witnessed, time-limited authority.

## Files Changed

| File | Change | Lines |
|------|--------|-------|
| `arifosmcp/runtime/tools.py` | Lease Gate hard-block | 12641-12721 |
| `arifosmcp/runtime/lease.py` | Status comment updated | 4-7 |
| `tests/runtime/test_h2_h3_ratification.py` | Updated + 3 new tests | 246-330 |

## What Changed (Behavior)

| Scenario | Before | After |
|----------|--------|-------|
| Mutation mode, no lease, `ack_irreversible=True` | HOLD | HOLD (unchanged) |
| Mutation mode, no lease, `ack_irreversible=False` | LEASE_AWARENESS → proceed | **HOLD** ← CHANGED |
| Mutation mode, valid lease | Proceed | Proceed + consume invocation |
| Lease subsystem crash | LEASE_SUBSYSTEM_ERROR → proceed | **HOLD** ← CHANGED |
| Read-only modes (query, recall) | No lease needed | No lease needed (unchanged) |

## Test Evidence

```
92 passed, 8 deselected (epoch hang — pre-existing), 0 failed
```

Test files covered:
- `tests/runtime/test_lease.py`: 20 passed
- `tests/runtime/test_h2_h3_ratification.py`: 16 passed (including 3 new)
- `tests/test_agi_kernel_grade.py`: 6 lease tests passed

New tests added:
1. `test_lease_hard_block_commit_without_lease` — commit without lease → HOLD, plan stays approved
2. `test_lease_hard_block_write_without_lease` — write without lease → HOLD  
3. `test_lease_success_with_valid_lease` — valid lease → proceeds to execution

## Rollback

To reverse this change:
1. Comment out the Lease Gate block (lines 12652-12721 in `runtime/tools.py`)
2. Restore the old warn-and-proceed path
3. Redeploy

Or simpler: `git revert` the commit.

## Next Phases (NOT INCLUDED — for future forge)

2. Witness alarm (last_human_witness_at, autonomous_elapsed_seconds)
3. Dehumanization gate (action pre-check, not person-labeling)
4. Arendt banality prechecks (bureaucratic harm, passive approval, diffused responsibility)
5. Moral creep accumulator (exception → habit → identity → institution)

## Constitutional Alignment

- F1 AMANAH: Reversible — comment out and redeploy to undo
- F11 AUTH: Authority now requires lease for mutation
- F13 SOVEREIGN: Awaiting Arif's deploy approval (888_HOLD)

DITEMPA BUKAN DIBERI — Forged, Not Given.
