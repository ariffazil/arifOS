# TEST_DISPUTE — Phase 0c premise is stale

**Author:** 333-AGI · AUDITOR lane
**Date:** 2026-10-28T00:40Z (08:40 MYT)
**Live build tested:** `843f3f0fe` (`/health.version = 2026.10.26-843f3f0`, `deployment_drift_status = aligned`)
**Rule invoked:** GLOBAL RULE 2 — "If a test is wrong → TEST_DISPUTE.md and stop."

## 1. The disputed claim

Phase 0c says: *"fixtures A and B as above, same unverified actor. Assert they differ… Must FAIL on current HEAD."*

This presumes that fixture B currently returns `unwitnessed_evidence: []`.

**That premise is false on the live build.** With the canonical fixture shape
(`[{"fact": "...", "source": "none", "tag": "UNKNOWN"}]`) the live kernel returns:

```
B judge_postcondition.unwitnessed_evidence =
  [{"index": 0, "field": "tag", "item": "CVSS 9.2 per advisory text pasted by the operator"}]
A judge_postcondition.unwitnessed_evidence = []
```

A and B are already distinguishable on the canonical shape. A literal implementation of
Phase 0c would therefore **pass** on HEAD, and Gate 0 ("both tests fail for the stated reason")
could not be satisfied by an honest test.

## 2. What is actually broken (measured, not inferred)

The detector is **transport-shape-blind and key-blind**. Three named defects, each
reproduced at the pure-function level (`check_judge_postcondition`) and through the live
MCP surface on `:8088`:

| # | Defect | Trigger | Observed | Blast radius |
|---|--------|---------|----------|--------------|
| D1 | `STRING_EVIDENCE_INVISIBLE` | `evidence` sent as a JSON string | `unwitnessed_evidence: []`, digest identical to an unparsed blob | Schema-legal transport (`{} \| Array \| string`). Any non-MCP caller. |
| D2 | `KEY_ALIAS_BLIND` | UNKNOWN declared under `epistemic` or nested `meta.tag` | `[]` | Any caller not using the five hard-coded key names. |
| D3 | `INTERCEPT_ADVISORY_SKIP` | `mode=intercept` | key absent entirely (early return in `_ADVISORY_MODES`) | The pre-flight gate — the exact path a caller uses to decide whether to proceed. `mode=validate` attaches no postcondition at all. |

## 3. Why this explains the 23:30 observation

The 23:30 external test reported `unwitnessed_evidence: []` **and** `applied: false`
on the same build that catches the canonical shape. `[]` + `applied:false` means the
postcondition *ran* and *found nothing*, not that it was skipped. D1 or D2 is the
mechanism that produces exactly that signature.

**UNKNOWN:** the exact payload the 23:30 caller sent. It is not recoverable from kernel
records — see §4. A string-encoded or alias-keyed evidence item is the consistent
hypothesis; it is not proven.

## 4. Independent finding — the call itself is not in telemetry

`/var/lib/arifos/metrics/tool_invocations.jsonl` (66,367 rows) contains **zero**
`arif_judge` invocations between `2026-10-27T14:00Z` and `2026-10-27T16:25Z` — the window
containing the 23:30 MYT (15:30Z) test. The last recorded row is
`2026-10-27T16:25:44Z organ=arifFlow`.

`/var/lib/arifos/act_decision_events/act_decisions_2026-10-27.jsonl` contains **zero**
occurrences of `CVSS`.

Consequence: a result reported as "live-verified" left no invocation record. Any claim
about that run is un-witnessable from inside the kernel. This is a second, separate
observability defect, and it is the reason §3 must stay UNKNOWN rather than DER.

## 5. What was written instead

`tests/acceptance/test_discrimination.py` and `tests/acceptance/test_unwitnessed_regression.py`
encode the *danger the premise was pointing at* — discrimination must hold across every
transport shape and every judge mode a schema-legal caller can use.

Baseline on `843f3f0fe`: **6 failed, 3 passed.**

Controls (must keep passing): canonical list shape, `{facts:[…]}` envelope, and the
canonical-shape half of the discrimination test.

Failures (real, each named):
- `test_discrimination[json_string]` — D1
- `test_discrimination[intercept]` — D3
- `test_unwitnessed_regression::test_json_string_transport_is_detected` — D1
- `test_unwitnessed_regression::test_unknown_tag_under_alias_keys_is_detected[epistemic_alias]` — D2
- `test_unwitnessed_regression::test_unknown_tag_under_alias_keys_is_detected[nested_meta_tag]` — D2
- `test_unwitnessed_regression::test_intercept_mode_reports_unwitnessed_evidence` — D3

No test was weakened, skipped, or xfailed. The controls are the guard against
"fix by making everything awake".

## 6. Ownership note

These are AUDITOR artefacts. The fix belongs to the BUILDER lane (Lane 1). This branch
contains the tests alone (`audit/phase0-unwitnessed-baseline`), per "Commit the test alone".
`b0e5f5a85` is already an ancestor of `HEAD` — the merge-coordination precondition in
Phase 2 is satisfied.
