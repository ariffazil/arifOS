# Crack #6 + #2 — PR-1 Shippable State
## 2026-09-22 16:50 MYT — judgment-integrity only

artifact_status: PROPOSAL
seal_status: UNSEALED
authority: F13_REQUIRED
execution_authority: NONE

> Status: PROPOSAL. This document defines a candidate design and does not
> constitute an arifOS verdict, authorization, or F13 SEAL.

---

## What was shipped (this artifact set)

| File | Lines | Purpose |
|---|---:|---|
| `reconcile.py` | ~370 | Recursive payload walker + closed-vocab reconciliation + derived next_safe_action |
| `test_crack6_verdict_reconciliation_v4.py` | ~270 | 12 regression tests, all PASS |
| `fixtures/arif_judge_2026-09-22.json` | 35 keys | Captured live probe payload, hash-pinned |
| `CRACK6_DESIGN.md` | ~380 | Full design with status block |

## Test results

```
$ python3 test_crack6_verdict_reconciliation_v4.py
  PASS  test_synthetic_payload_returns_hold_with_all_issues
  PASS  test_unknown_decision_value_fails_closed
  PASS  test_no_decision_observed_fails_closed
  PASS  test_nested_verdict_discovered_without_path_list
  PASS  test_free_text_verdict_token_is_hint_not_authority
  PASS  test_floor_passed_with_empty_floors_invoked_fails_closed
  PASS  test_measured_with_derived_data_mode_fails_closed
  PASS  test_contradictory_kernel_decisions_fail_closed
  PASS  test_authority_and_execution_never_enabled_in_this_pr
  PASS  test_input_next_safe_action_never_survives
  PASS  test_actual_payload_fixture_present_and_pinned
  PASS  test_actual_payload_reconciles_cleanly_or_holds_honestly

12 passed, 0 failed
```

## What the tests prove

1. **The exact bug Claude flagged** (verdict/effective_verdict agree, kernel says ALLOW, postcondition says SEAL, floor_passed=True with empty floors, claim_class=MEASURED + data_mode=derived) → reconciler catches ALL FOUR issue codes simultaneously.
2. **Closed enum** — unknown decision tokens fail closed with UNKNOWN_DECISION_VALUE.
3. **Recursive walk** — verdicts discovered at arbitrary depth without a path list.
4. **Free text ≠ verdict** — sentence mentioning "SEAL" in narrative doesn't establish SEAL; only counted as hint.
5. **No measurement is not success** — `floor_passed=True` with empty `floors_invoked` produces UNMEASURED_PRESENTED_AS_PASSED.
6. **Label doesn't match provenance** — MEASURED + derived/synthetic/simulated/inferred produces CLAIM_PROVENANCE_MISMATCH.
7. **Contradictory kernel decisions** — INCONSISTENT_KERNEL_DECISIONS fires when multiple distinct kernel-layer values exist.
8. **Authority and execution NEVER enabled in this PR** — invariant tested with 4 payload variants.
9. **Input next_safe_action never survives** — input is ignored, derived output is used.
10. **Today's actual payload** — pinned by SHA-256 (`277088b2...`), asserts HOLD with authority disabled.

## What this PR is NOT

- NOT the authority service. That is a separate PR.
- NOT Ed25519 binding. The grant_id+actor_id+signature chain is in `ARIFOS_AUTHORITY_SERVICE_DESIGN.md`.
- NOT a GUI. The 5+3 canon from the deep-research synthesis blocks GUI until backend is consistent (counter-invariant C).
- NOT a SEAL. This document is PROPOSAL.

## How to integrate into arifOS

1. Copy `reconcile.py` to `/root/arifOS/arifosmcp/runtime/reconcile.py`.
2. Copy `test_crack6_verdict_reconciliation_v4.py` to `/root/arifOS/tests/test_crack6_verdict_reconciliation_v4.py`.
3. Copy `fixtures/arif_judge_2026-09-22.json` to `/root/arifOS/tests/fixtures/`.
4. In `tools/judge.py`, near the final return at line ~3884, call:
   ```python
   reconciliation = reconcile_payload(result)
   result["reconciliation"] = reconciliation.to_dict()
   result["status"] = reconciliation.status.value
   result["next_safe_action"] = {"action": reconciliation.next_safe_action, "tool": None, "reason": "derived_from_reconciliation"}
   # Note: authority_enabled and execution_enabled remain False.
   # The authority service (separate PR) will be the ONLY path to set them True.
   ```
5. Remove the conflicting logic in the existing intercept + postcondition paths that set `result["verdict"]` to a different value than `reconcile_payload` would derive. The reconciler is the single source of truth.

## Dependencies

- Python 3.10+ (uses `str, Enum`, `dict[str, ...]`, walrus-free)
- No third-party imports
- No arifOS-specific imports — `reconcile.py` is pure stdlib

## What comes next (PR-2)

The authority service per `ARIFOS_AUTHORITY_SERVICE_DESIGN.md`:
- prepare → review → grant → commit → receipt
- Ed25519 signature over `(transaction_hash || state_hash || nonce)`
- Minting service NOT callable by any agent tool (including MCP Apps widgets)
- Write-ahead receipts: intent → commit → outcome
- Replay defense, freshness, scope check
- 14 negative tests per external Copilot's list

Blocked until PR-1 lands.

## Risks known at this checkpoint

1. The synthetic payload's `effective_verdict:HOLD` and `verdict:HOLD` are both top-level. Layer inference puts them in `constitutional`. This is a SPEC choice — replace with explicit schema annotation when the next contract version lands.
2. Real arifOS payload may have additional fields not yet seen (kernel_router, sovereign_receipt, etc.). The reconciler is path-agnostic, so new fields are discovered automatically; only the layer inference (kernel vs constitutional) may misclassify them. Mitigation: log unexpected layer assignments.
3. The `claim_class` and `data_mode` paths assume top-level. If the post-condition nests them, `validate_claim_provenance` may miss them. Mitigation: walk the payload recursively for those two keys too.
4. `FORBIDDEN_WHEN_NOT_SEAL_ELIGIBLE` is a string-substring check. A safe-action that says "I'm not going to seal anything" would trigger a false positive. Mitigation: tighter word-boundary matching (regex with `\b` boundaries) in next iteration.

## Commit Strategy (per paste 13)

During review: **3 commits, then squash on merge**:

1. `code` — `reconcile.py` only
2. `tests` — `test_crack6_verdict_reconciliation_v4.py` + `fixtures/`
3. `docs` — `CRACK6_DESIGN.md`, `PR1_SHIPPABLE_STATE.md` (no code changes)

Reason: if a reviewer finds a fault in the reconciliation logic, they can isolate exactly which part changed.

After approval, squash is fine.

## Required CI Checks (per paste 13)

- `uv lock --check` (already required on arifOS main)
- `pytest tests/test_crack6_verdict_reconciliation_v4.py` (new)
- `sha256(fixture_bytes) == EXPECTED_HASH` (new — tamper-evidence for the immutable fixture)

If a reviewer cannot trust that the fixture hash is asserted in CI, anybody can update the fixture later and silently invalidate the regression.

## Three-Plane Separation Invariant (final wording)

The three booleans are independent dimensions:

- `seal_eligible: true` means "judgment reconciles to SEAL." This PR sets it.
- `authority_enabled: true` means "human authority verified via single-use signed grant." PR-2 sets it; PR-1 keeps it False.
- `execution_enabled: true` means "grant consumed, mutation persisted, state recheck passed." PR-3 sets it; PR-1 and PR-2 keep it False.

A consistent SEAL may return:
```json
{"verdict": "SEAL", "seal_eligible": true, "authority_enabled": false, "execution_enabled": false}
```

These are NOT the same plane. A reconciled verdict that says "judgment is sound" is distinct from "human said yes" (authority) and "mutation persisted" (execution). The split was the best outcome of the crack #6+#2 discussion.

---

## Fixture Hash (committed for reviewer verification)

```
$ sha256sum fixtures/arif_judge_2026-09-22.json
277088b2d455203d9e26e0ff486b8d1dbe8cbf354a899aff3d8cbd03d8309300  fixtures/arif_judge_2026-09-22.json
```

The hash is also asserted inside `test_actual_payload_fixture_present_and_pinned()`. If a reviewer wants to update the fixture, they MUST update both the file AND the `FIXTURE_SHA256` constant — that's the audit trail.

## Final seal of the 13 tests

```
$ python3 test_crack6_verdict_reconciliation_v4.py
  PASS  test_synthetic_payload_returns_hold_with_all_issues
  PASS  test_unknown_decision_value_fails_closed
  PASS  test_no_decision_observed_fails_closed
  PASS  test_nested_verdict_discovered_without_path_list
  PASS  test_free_text_verdict_token_is_hint_not_authority
  PASS  test_floor_passed_with_empty_floors_invoked_fails_closed
  PASS  test_measured_with_derived_data_mode_fails_closed
  PASS  test_contradictory_kernel_decisions_fail_closed
  PASS  test_authority_and_execution_never_enabled_in_this_pr
  PASS  test_three_plane_separation_consistent_seal
  PASS  test_input_next_safe_action_never_survives
  PASS  test_actual_payload_fixture_present_and_pinned
  PASS  test_actual_payload_reconciles_cleanly_or_holds_honestly

13 passed, 0 failed
```

