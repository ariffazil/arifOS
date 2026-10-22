# NOTES-F6-KERNEL-SOURCE.md — F6 floor source→build→deploy path (F13 supplemental #4)

Verified 2026-10-23. Purpose: record where the F6 floor logic actually lives,
so future patches target SOURCE, not the deployed copy.

## Findings

1. **F6 floor logic lives in the arifOS kernel source**: `/root/arifOS/arifosmcp/runtime/`
   - `rest_routes/rest_routes.py` — `_FLOOR_DEFAULTS` (line ~318, from
     `_canonical_floor_defaults()`), `canonical_floor_aliases` "F6" → "kappa_r"
     (line 1145), `_floor_status_with_provenance` (line 959) renders
     `unmeasured_default*` provenance as `unmeasured`, never pass/fail.
   - `health_truth.py` — single producer `floor_truth()` (line 208);
     `classify_provenance` maps `unmeasured*` → UNMEASURED (line 61-62), which
     can never render PASS (lines 240-248).
2. **Live deploy** at `/opt/arifos/current/venv/.../arifosmcp` reports
   source_commit = built_commit = deployed_commit = e69abf6, drift=false —
   the deployed copy currently MATCHES the source tree at `/root/arifOS`
   (branch main @ 257c146bf for docs; kernel files untouched by this branch).
3. **Producer provenance on live /health**: F6 = `unmeasured_default:empty_kernel_signal`,
   score 0.5 placeholder, status `unmeasured`. F8 is the only measured FAIL.
4. **A-FORGE side**: `/root/A-FORGE/src/infrastructure/governance/actIngress.ts`
   writes `/var/lib/arifos/act_decision_events/act_decisions_YYYY-MM-DD.jsonl`
   (schema `act_decision_event.v1`). Today's ledger: 79 rows, ALL OBSERVE/ALLOW —
   the ACT ledger as wired captures observe-class probe traffic; NO MUTATE-class
   decision was recorded on 2026-10-22/23 (baseline claim verified: the
   authority-enforcement path has no production MUTATE traffic to measure).

## What this branch changes in arifOS

NOTHING in this task changes kernel floor logic — F6 stays UNMEASURED by
design until producers + witness exist. The arifOS worktree
(`/root/arifOS-wt-f6`, branch `feat/f6-maruah-v0-20261023`) carries this
notes file only, as the source→build→deploy record.

## Future wiring (NOT done here, needs F13 decision)

To make the kernel consume the new F6 meters, a future patch would add a
floor producer in `arifosmcp/runtime/floor_producers.py` reading the F6
meter JSON — but only AFTER: witness lane filled, meters 2-5 producers
decided, and lane-gate defect closed. Wiring it now would launder
UNMEASURED into a measured-looking value, violating floor honesty.
