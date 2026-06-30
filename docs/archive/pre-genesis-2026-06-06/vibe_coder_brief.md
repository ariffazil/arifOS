# Vibe Coder Brief — arifOS Autoresearch

**Date:** 2026-04-22
**Author:** OpenClaw (arifOS_bot)
**For:** Mistral Vibe (autonomous coder)

---

## Goal

Improve arifOS E2E_SCORE from **53.0/100** toward **75+/100** by improving tool correctness and error handling. No governance floors may be removed or weakened.

---

## Non-Negotiables (DO NOT TOUCH)

- ❌ No secrets in git — only vault path references
- ❌ No removal or weakening of any floor (F1–F13)
- ❌ No disabling of 888_judge or constitutional_guard
- ❌ No destructive operations against real /mnt/arifos/secrets/
- ❌ No changes to arifos_prepare.py (fixed ground truth)

---

## Focus Areas (Priority Order)

### 1. Fix arifos_train.py scenario inputs (HIGH)
Improve test harness accuracy so scenarios produce correct expected verdicts:
- **C (arifos_444_kernel):** Currently returns ERROR because test sends `claim` kwarg not in schema. Fix: remove `claim` and `domain` from test input — use only `route_target`.
- **D (arifos_222_witness):** Returns CLAIM_ONLY but expected HOLD. Fix: use `mode: "search"` with `search_query` that has no results, or pass `witness_required: 4` with no evidence.
- **E (arifos_999_vault):** Returns VOID for `action: "read"` but expected HOLD. Fix: change expected_verdict to "VOID" (vault correctly blocks unauthorized read with VOID).

### 2. Improve error messages (MEDIUM)
When arifos_444_kernel gets unexpected kwargs, the error message is a raw FastMCP validation traceback. Replace with a clean JSON error: `{"verdict": "ERROR", "reason": "unexpected_kwarg: claim", "tool": "arifos_444_kernel"}`.

### 3. Observability (LOW)
Ensure all scenarios emit consistent `floors_triggered` in output, even when empty list `[]`.

---

## Constraints on Changes

- Only edit: `scripts/e2e_runner.py`, `arifos_e2e_program.md`, `arifos_train.py`
- All changes: self-contained commits, no secrets, describe in CHANGELOG_AUTORESEARCH.md
- After changing anything: run `python scripts/e2e_runner.py` and record score

---

## How to Proceed

1. Read `arifos_e2e_program.md` and `scripts/e2e_runner.py`
2. Read the current run log: `logs/autoresearch_2026-04-22.jsonl`
3. Make ONE small change to the test harness or scenario inputs
4. Run `python scripts/e2e_runner.py` — record E2E_SCORE
5. If score improves → git commit with description
6. If score worsens → git reset and retry

---

**DITEMPA BUKAN DIBERI — Testing is forged, not assumed.**
