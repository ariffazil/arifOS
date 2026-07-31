# RECEIPT — M2 Fail-Closed Totality · 2026-07-31

> **M2 of Kernel Hardening Sprint** — T1, fail-closed totality in floor evaluation.

## WHAT WAS BROKEN

`arifosmcp/core/law_evaluator.py` had 11 bare `except Exception:` blocks
(10 inside the per-floor check loop + 1 inside `_lazy_floor`). Both patterns
were fail-open: a raising floor was silently treated as PASSED, not failed.

This violated F1 AMANAH + F9 ANTIHANTU — silence on error is the exact
"do not tell the truth when truth-telling is hard" failure mode the
constitution exists to prevent.

## THE FIX

1. **New `_check_floor` helper** — a total function that wraps the
   instantiate+check pipeline. Any exception (instantiation OR check) is
   recorded as failed with the exception class+message fingerprint in the
   trace. Replaces the 10 repeated fail-open blocks with one explicit
   error-handling path.

2. **`_lazy_floor` no longer swallows instantiation errors** — the
   pre-existing `try/except: return None` is replaced with a clean
   propagation. The cache uses None as a "not loaded" sentinel, with
   `cache.get(key) is None` as the trigger condition (was buggy: was
   `key not in cache`, but callers pre-seeded with None, so instantiation
   was being skipped).

3. **New regression test** `tests/test_m2_fail_closed_totality.py`:
   - injecting a raising-on-instantiation floor → VOID + fingerprint
   - injecting a raising-on-check floor → VOID + fingerprint
   - literal grep gate: 0 `except Exception: pass` in source
   - healthy-floor regression check (no breakage of the happy path)

## ACCEPTANCE — measured at fix time

| Gate | Before | After |
|---|---|---|
| `grep -c "except Exception: pass" core/law_evaluator.py` | **11** | **0** |
| `pytest tests/test_m2_fail_closed_totality.py` | n/a | **4 passed** |
| Runtime `arifOS` initialize | kanon-2026.07.31+0b03b5b | unchanged |
| Runtime `tools/list` | 8 tools | 8 tools |
| Live `arif_judge` smoke call | healthy | healthy |

## CONSTRAINT CHECK

- ✅ Did NOT touch `server.py`, `runtime/tools.py`, `constitutional_map.py`.
- ✅ Did NOT change canon (W³ threshold, verdict lattice, capability count, stage code untouched).
- ✅ One commit per mission.
- ✅ Live verified after restart (post-restart kanon- handshake + 8 tools).

## BEHAVIORAL SEMANTICS

Before M2: a raising floor = "this floor was silently skipped".
After M2: a raising floor = "this floor is VOID with fingerprint X in trace".

The verdict string (SEAL/HOLD/VOID) still derives from
`FloorEvaluator.is_void` (L13_VIOLATION, CRITICAL irreversibility, or
injection category). M2 changes WHICH floors appear in `violated_laws`,
not how the verdict string is derived. This is the correct scoping:
M2 fixes the input, not the verdict policy.

DITEMPA BUKAN DIBEI.
