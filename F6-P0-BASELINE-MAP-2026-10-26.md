# F6 / MARUAH — P0 BASELINE MAP (2026-10-26)

> **Status:** EVIDENCE RECORD (not canon, not a verdict). Every row below was
> probed in this session; nothing here is inferred from a prior report.
> **Branch under test:** `feat/f6-maruah-v0-20261023`
> **Kernel worktree:** `/root/arifOS-wt-f6` @ `aaf00ebc9` (+ 2026-10-26 changes)
> **Actuator worktree:** `/root/A-FORGE-wt-f6` @ `e2f1f764` (+ 2026-10-26 changes)
> **Deployed kernel:** `e62a940` (`/opt/arifos/app`)

---

## 1. Deployment reconciliation (the question that was open)

| Question | Probe | Result |
|---|---|---|
| What is actually running? | `GET :8088/health` → `git_commit`, `deployed_commit` | `e62a940`, `runtime_matches_build: true`, `source_build_drift: false` |
| Does the deployed tree contain F6 code? | `ls /opt/arifos/app/arifosmcp/runtime/f6/` | **NO such directory** — F6 v0 is not deployed |
| Is the F6 branch merged? | `git merge-base --is-ancestor aaf00ebc9 main` / `... 30fc077d9` | **NO** on both. Merge-base = `257c146bf` |
| Does the candidate contain F6 modules? | `ls arifOS-wt-f6/arifosmcp/runtime/f6/` | 7 modules + floor producer + rest-route wiring + 3 test files |

**Conclusion (OBS):** the F6 candidate is a clean, unmerged branch. The deployed
kernel has none of it. Any claim that "F6 is enforced in production" is false
at `e62a940`.

---

## 2. Six-meter map — producer → code → enforcement → evidence → gap

Canonical numbering M1–M6 from `meters.py` (aligned with the F13 ruling).
Each meter carries the four axes (`measurement` / `result` / `witness` /
`authority`) and its own `pass_does_not_imply`.

| Meter | Producer (live?) | Code path | Enforcement point | Current evidence | Test | Gap |
|---|---|---|---|---|---|---|
| **M1** Authority-bypass | PARTIAL — last-20 A-FORGE commit signatures + today's ACT ledger | `meters.py:evaluate_meter_1_authority_bypass` | None in kernel; advisory only | git probe live; ledger rows are 100% OBSERVE/ALLOW → no MUTATE coverage | `test_01`, `test_02a-c` | hermes-lane raw commit gap remains; no MCP/cron coverage |
| **M2** Unreceipted claims | PARTIAL — commit-subject scan only | `meters.py:evaluate_meter_2_unreceipted_claims`, `verify_claim_receipt_relevance` | None; UNKNOWN by design | no commit→receipt production index | `test_07`, `test_07b` | production join store missing |
| **M3** Comprehension (machine obligation) | **NONE** | `meters.py:evaluate_meter_3_comprehension`, `evaluate_comprehension_ceremony` | None | no `[decision_id, restatement_provided]` emitter | `test_12` | producer missing → UNKNOWN, never estimated |
| **M4** False urgency / flattery | **NONE** | `meters.py:evaluate_meter_4_false_urgency_flattery`, `evaluate_manipulation_detector` | Out-of-band only (never retry/reward loop) | no calibrated classifier | `test_13` | FP/FN rates unmeasured; production classifier absent |
| **M5** Correction acceptance | **MECHANISM NOW EXISTS** (2026-10-26) | `correction_effect.py` + A-FORGE `forget_propagation.py` | Advisory ledger; **no production call site** | 2026-10-23: FAIL all 4 layers (registry-only `emit`). 2026-10-26: dispatcher + 4 adapters + re-read verification, 9/9 tests | `test_f6_correction_propagation.py` (A-FORGE 9, kernel 3) | no production layer adapters registered yet |
| **M6** Consent-scope | **NONE** — evaluator only | `consent_scope.py:check_consent`, `meters.py:evaluate_meter_6_consent_scope` | None | no production consent ledger; `check_consent(None)` → UNKNOWN + dependency | `test_06`, `test_06b` | **BLOCKED**: no legitimate consent source exists |

### 2.1 What `check_binding` actually did before 2026-10-26

```
grep -rn "check_binding|execute_bound|BindingStore" arifosmcp/ | grep -v runtime/f6/
→ (no hits)
```

`authority_binding.py` was a **dead seam**: fully implemented, fully tested,
zero live callers. P3 ("prove the boundary at the last tool") was therefore
**not satisfied** by the candidate, regardless of its tests.

**2026-10-26 change:** `runtime/f6/execution_boundary.py::guard_forge_call` is
now called from `_arif_forge_execute_tool` before any mutation dispatch.

- Flag: `ARIFOS_F6_BINDING_ENFORCE` (default `"0"` = observe-only annotation).
- Enforcing: a mutating mode (`engineer`/`write`/`generate`/`commit`) without
  `f6_binding_id` → `REJECT_BYPASS`; widened scope / changed params / expired /
  revoked / replayed / changed-after-approval → blocked before dispatch.
- No state guard → `UNKNOWN` → blocked when enforcing (fail-closed).
- Observation modes (`query`/`recall`/`dry_run`) → `NOT_APPLICABLE`.

---

## 3. Meter 5 — what was actually fixed

| Layer | 2026-10-23 | 2026-10-26 |
|---|---|---|
| L1 memory | stale (`emit` only) | `ListLayerAdapter` / `SQLiteLayerAdapter` rewrite + re-read |
| L2 queue | stale | adapter rewrites `assumption`, re-read verified |
| L3 planner | stale | adapter rewrites `assumption`, re-read verified |
| L4 tool payload | stale | adapter rewrites `assumption`, re-read verified |
| Registry | recorded "would notify" | append-only event + `propagation_results` row |

**Contract now enforced in code:**
- missing layer → `MISSING`, `propagated=False`
- subscriber exception → `ERROR`, `propagated=False`
- stale premise survives → `STALE`, `propagated=False`
- no row carried the premise → `NOT_APPLICABLE` **with reason**; if nothing
  changed anywhere → `propagated=False` ("correction without effect is not
  verified")
- `propagated=True` only when all required layers are clean **and** ≥1 row changed

The historical falsifier is preserved: `test_registry_only_emit_changes_no_layer`
still proves `emit()` alone touches nothing. The old
`test_no_subscriber_to_forget_events_exists` was the defect's receipt and was
replaced by `test_subscribers_exist_and_dispatch_changes_state` — it must fail
if dispatch regresses to registry-only.

---

## 4. Authority axis (separate from meters)

`check_binding` returns `ALLOW` / `REJECT_*` / `UNKNOWN`. It never consults a
meter score. Action approval remains: binding + risk policy → allow/block.
Meters inform assurance only.

---

## 5. Deferred decisions (unchanged, not activated)

| Item | Status |
|---|---|
| Third-party dignity | `PENDING` — extension point only |
| Collective witness / veto | `HOLD` / `DISABLED` — `PolicyNotActive` |
| External peer witness | `UNASSIGNED` — synthetic fixtures only |

No policy below was activated by this work.

---

## 6. Closure vocabulary (strict)

- **IMPLEMENTED:** `execution_boundary.guard_forge_call`; A-FORGE propagation
  dispatcher + four adapters + SQLite adapter.
- **TESTED:** kernel `test_f6_execution_boundary.py` 7/7; kernel F6 suites
  20+8+3/3; A-FORGE propagation 9/9.
- **UNTESTED:** live forge traffic under `ARIFOS_F6_BINDING_ENFORCE=1`; real
  production layer adapters (memory/queue/planner/payload) are not registered.
- **BLOCKED:** Meter 6 production consent source does not exist.
- **NOT DEPLOYED:** kernel `e62a940` contains no F6 code; branch unmerged.

*DITEMPA BUKAN DIBERI — evidence first, labels honest.*
