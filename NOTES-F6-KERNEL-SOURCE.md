# NOTES-F6-KERNEL-SOURCE.md — F6 floor source→build→deploy path & Kernel Implementation (2026-10-23)

Verified 2026-10-23. Purpose: record where the F6 floor logic lives in the
`arifOS` kernel and what `feat/f6-maruah-v0-20261023` implements in source
without deploying to production.

## 1. Baseline Findings

1. **F6 floor logic lives in the arifOS kernel source**: `/root/arifOS/arifosmcp/runtime/`
   - `rest_routes/rest_routes.py` — `_FLOOR_DEFAULTS` (line ~318, from
     `_canonical_floor_defaults()`), previously mapped `"F6": ("kappa_r",)` in
     `canonical_floor_aliases` (line 1145), and `_floor_status_with_provenance`
     (line 959) renders `unmeasured_default*` provenance as `unmeasured`, never
     pass/fail.
   - `health_truth.py` — single producer `floor_truth()` (line 208);
     `classify_provenance` maps `unmeasured*` → `UNMEASURED` (line 61-62), which
     can never render `PASS` (lines 240-248).
2. **Live deploy** at `/opt/arifos/current/venv/.../arifosmcp` remains untouched
   (`NOT DEPLOYED`).
3. **A-FORGE side**: `/root/A-FORGE/src/infrastructure/governance/actIngress.ts`
   writes `/var/lib/arifos/act_decision_events/act_decisions_YYYY-MM-DD.jsonl`
   (schema `act_decision_event.v1`). Live probe verified 78 daily files (73,292
   total rows; 117 rows on 2026-10-22 [75/79 at earlier snapshot], 44 rows on
   2026-10-23), **100% `OBSERVE`/`ALLOW` (`0` `MUTATE` rows)**.

## 2. What `feat/f6-maruah-v0-20261023` Implements in `/root/arifOS-wt-f6`

1. **`arifosmcp/runtime/f6/` package**:
   - `authority_binding.py`: Execution-time authority check (`check_binding`) and
     last-mile tool wrapper (`execute_bound`), recursive delegation-chain narrowing
     check (`_verify_delegation_chain`), required constrained parameter and
     `approved_params` snapshot enforcement, nonce replay guard, expiry check,
     SQLite + `lease_registry` revocation check, and `state_guard`.
   - `correction_effect.py`: Meter 5 canonical producer (`record_correction`,
     `apply_correction`, `verify_effect`, `propagate_correction_across_layers`
     across `L1_memory`..`L4_tool_payload`, `resolve_dissent_at_decision_gate`,
     append-only `challenge_record` and `supersede`).
   - `consent_scope.py`: Meter 6 canonical evaluator (`check_consent` separating
     `access`, `use`, `disclose`, enforcing delegation narrowing, expiry, and
     revocation, and rejecting `ConsentSource.INFERENCE` / `model_confidence`).
   - `meters.py`: Canonical M1–M6 evaluators (`evaluate_meter_1..6`,
     `evaluate_all`, `verify_claim_receipt_relevance`,
     `evaluate_comprehension_ceremony`, `evaluate_manipulation_detector`) with
     4 non-collapsed axes (`measurement`, `result`, `witness`, `authority`) and
     mandatory `pass_does_not_imply`.
   - `privacy_and_redress.py`: L1 human-scoring prohibition
     (`validate_no_human_scoring`), analytics-vs-authority separation
     (`verify_analytics_authority_separation`), `0o600` file mode enforcement,
     and technical-vs-external rollback classification
     (`classify_rollback_outcome`).
   - `pending_policies.py`: Keeps `third_party_dignity` (`PENDING`),
     `collective_witness` (`HOLD`), and `external_peer_witness` (`UNASSIGNED`)
     inactive (`PolicyNotActive` on `enforce()`).
2. **`arifosmcp/runtime/floor_producers.py`**:
   - Registers `_f6_maruah` under `_PRODUCERS["F6"]`.
   - Disqualifies (`FAIL`) on any L1 human-scoring/identity key.
   - Rejects `kappa_r` proxy (`unmeasured_default:kappa_r_proxy_rejected`).
   - Returns `UNMEASURED` (`unmeasured_default:f6_partially_measured`) whenever
     any meter is `UNKNOWN` or witness is not `REVIEWED` — never laundering
     partial or unwitnessed state into `PASS`.
3. **`arifosmcp/runtime/rest_routes/rest_routes.py`**:
   - Severs `"F6": ("kappa_r",)` in `canonical_floor_aliases` (`"F6": ()`) per
     Spec Amendment 05 (C.11).
   - Attaches `measurement_basis["f6_maruah"]` in `_build_governance_status_payload()`
     with `evaluate_all()` + `collect_floor_producer_signal("F6", sources=...)`.
