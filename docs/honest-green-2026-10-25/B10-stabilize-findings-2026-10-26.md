# B10 — Stabilize arifOS: baseline, F1 root cause, honest-green wiring (2026-10-26)

> Directive: F13 "INIT, VERIFY AND STABILIZE arifOS" (2026-10-26).
> Scope executed: read-only inspection, isolated code changes, tests, prepared PR.
> **Production deployment, executor hook activation, canon ratification and seals were NOT performed.**
> Evidence labels: OBS = directly observed, DER = derived, INT = interpreted, SPEC = speculation.

---

## 0. Headline

**Three defects made the federation read worse than it is, and one defect makes it read better than it is.**

| # | State | Claim | Evidence |
|---|-------|-------|----------|
| A | OBS | The running kernel is a **mixed-version install**: 4 of 11 critical modules differ from `HEAD` | `sha256(live)` vs `sha256(git show HEAD:…)` — verdict.py, rest_routes.py, floor_producers.py, tools.py |
| B | OBS | **Every v2-enveloped response HOLDs** because `verdict.py` in the running venv lacks the `intermediate_trace_states.canonical_verdict` carve-out that exists in source | live `arif_judge` ×3 → `INCONSISTENT_STATE: UNKNOWN_VERDICT_TOKEN:intermediate_trace_states.canonical_verdict=DENY` |
| C | OBS→TESTED | **F1 FAIL / FEEL_UNANCHORED was a cold-start wiring race**, not a flow failure | same FQ band (0.9677 then 0.9883, floor 0.5) produced F1 0.0/fail then 1.0/pass with no threshold crossed |
| D | OBS→TESTED | **F8 published a fabricated pass** (0.80, `measured: true`) while the live G reading was skipped | provenance `arifflow_vector_g_skipped:calibration=PHASE_1_HEURISTIC_UNCALIBRATED` + status `pass` |
| E | OBS | **arif_report is registered and invocable** — the snapshot claim is refuted on this release | `arif_report(mode=stats)` → `status: completed`, `total_reports`, `by_kind` |
| F | OBS→TESTED | **`input_schema_hash_match: false` conflated mismatch with never-measured** | capability cache: every public verb except arif_init has `input_schema_hash: null` |
| G | OBS | **F6 is not un-wired — it is unwritable**: the meter reads `payload.heart_critique`; no writer in the federation produces it, and every live seal row has `payload: null` or `payload: str` | 277 seal rows, `heart_critique` count = 0; `arif_seal(payload: str = "")` |

A/B are **deployment** findings (out of this instruction's authority).
C/D/F are **fixed in this branch and unit-tested**.
E/G are **reported**, with the exact missing decision named.

---

## 1. Baseline (recorded separately, as ordered)

| Axis | Value | Label | Note |
|------|-------|-------|------|
| Source checkout (`git HEAD`) | `823c4c488` on `fix/honest-green-2026-10-25` | OBS | 10 commits ahead of `origin/main` (`55ab6acc`) |
| Working tree | dirty: `runtime/tools.py`, `requirements.txt`, `uv.lock` + 5 untracked (sibling session work) | OBS | not touched by this branch |
| Reported `source_commit` / `built` / `deployed` | `e62a940` / `e62a940` / `e62a940` | OBS | .health |
| **Actual** installed package | `arifos 1!2026.10.17`, `site-packages/arifosmcp/`, module mtimes 2026-10-25 20:58–21:08 | OBS | the build stamp is **stale**; the tree is a partial rsync, not a clean wheel |
| Modules identical to HEAD | health_truth, v2_envelope, tools/vault, tools/judge, session_standing, fq_gate, tool_charter (7/11) | OBS | |
| Modules NOT identical to HEAD | `runtime/verdict.py`, `runtime/rest_routes/rest_routes.py`, `runtime/floor_producers.py`, `runtime/tools.py` (4/11) | OBS | drift, not a clean build |
| `/health` freshness | `fresh`; service started `2026-10-26T01:20:08Z` | OBS | the observatory snapshot `obs_20261026_011419` was taken ~8 min after boot, inside the 300 s health cache window |

**Consequence (DER):** no single commit describes what is running. "Deployed `e62a940`" is a build-time stamp that the install no longer honours.

### 1.1 Snapshot provenance — NOT VERIFIED (missing access)

`obs_20261026_011419` / `2026-10-26T01:14:19Z` could not be retrieved, so its signature was **not** verified. Bounded probes, all 404:

```
GET :8088/observatory/snapshot      404   (source declares @route("/snapshot"))
GET :8088/observatory/state         404
GET :8088/snapshot                  404
GET :8088/snapshot/capabilities     404
GET :8088/seal/head                 404
```

No local file named `obs_20261026_011419*` was found under the usual state dirs, and `/var/lib/arifos/observatory/` holds only `capability-test-cache.json` (2026-10-26 09:30) + three July files. The observatory route module that source declares appears **not registered in the running build** — consistent with finding A (mixed install), and a Phase-7 observation in its own right: the snapshot the operator reads may be produced by a different surface than the one this repo describes. Label: **UNKNOWN**, not absent.


---

## 2. Phase 2 — F1 `FEEL_UNANCHORED`: root cause

### 2.1 What was observed

| t | F1 score | F1 status | provenance | measured quantity |
|---|----------|-----------|-----------|-------------------|
| 01:20:18Z (cached, post-boot) | 0.0 | fail | `arifflow_verdict:PARTIAL_WIRING;fq=0.9677419354838711` | FQ **0.9677** |
| 01:25:49Z (`?nocache=1`) | 1.0 | pass | `arifflow_verdict:FLOWING;fq=0.988333988727225` | FQ **0.9883** |

Both readings are **above** the ratified floor 0.5 (`fq_policy.yaml`, F13 RATIFIED 2026-09-12). The score flipped without the measurement crossing its floor. That is decisive: the floor was not decided by its instrument.

### 2.2 Root cause (OBS)

`arifosmcp/runtime/rest_routes/rest_routes.py` (pre-fix):

```python
_phi_fq = 1.0 if _fq_verdict == "FLOWING" else 0.0
```

and `_phi_fq_from_quotient()` — the ratified quotient mapping — existed **with tests and zero callers**.

The `verdict` field is arifFlow's *constellation classifier*, whose non-`FLOWING` values are explicitly not failures:

```
/root/arifFlow/src/vector.rs:506   Unwired dimensions ... shift the
                                   constellation to `PARTIAL_WIRING` —
                                   they are not pathologies.
/root/arifFlow/src/vector.rs:514   return "FEEL_UNANCHORED"   (FEEL anchor absent)
/root/arifFlow/src/vector.rs:589   return format!("PARTIAL_WIRING:{}", primary)
```

Classification: **producer/consumer contract mismatch** (not a policy outcome, not a stale receipt, not a missing anchor in the sense of a *failed* anchor — the anchor is genuinely absent at cold start, which is a **wiring-coverage** fact).

### 2.3 Fix (IMPLEMENTED + TESTED, not deployed)

- F1 scores on `_phi_fq_from_quotient(fq_quotient)` — the ratified instrument, floor 0.5 unchanged.
- The constellation rides in provenance as a **diagnostic** (`arifflow_probe:quotient=…;floor=0.5;constellation=…`) so coverage stays visible and testable — without gating AMANAH.
- Cold arifFlow with no pooled quotient → `unmeasured_default:arifflow_no_quotient` (K2: a void is not a zero), instead of `float(None)` → probe error.

**Thresholds were not changed.** No gate was widened: the same 0.5 boundary decides, sourced from the same ratified policy.

---

## 3. Phase 6 — the meaning of green

### 3.1 F8 (FIXED)

Observed: `score 0.80 · status pass · measured true` while provenance said the G dimension was **skipped** because `PHASE_1_HEURISTIC_UNCALIBRATED` must not be gate-grade. The 0.80 is `_FLOOR_DEFAULTS["F8"]` — a substituted placeholder, not a reading. Classification: **retained default published as a measurement**.

Fix: one predicate, `_provenance_is_unmeasured()`, used by all four measurement surfaces in the response (`status`, `measured`, `floors_measured`, and — via status — `floors_unmeasured`). A skipped producer now reads `unmeasured`. Real G readings still pass/fail on their own score. No new score was invented.

### 3.2 F13 (REPORTED, not changed)

`F13 = 1.0 PASS`, provenance `floor_producer:PASS:seal_chain_sovereign`. What the producer actually proves (`_f13_sovereign`): across the last 100 seal rows since 2026-09-08, **no SEAL-verdict row from a non-sovereign actor lacks ratification** (`authority_state == SOVEREIGN_RATIFIED` or an explicit human ratifier).

What it does **not** prove: that the action currently under judgement was authorised, nor that a delegation was valid. It is a **ledger-tail self-acceptance property**, not an authorisation of the live action.

Deliberate non-change: a test asserts the origin string `seal_chain_sovereign`; renaming it would break a sibling's in-flight test. The scope statement belongs in `/health` documentation and in the producer docstring — that is an F13 wording decision, not a code decision I may take.

### 3.3 F3 witness lineage (OBS)

`F3 = 0.9257`, provenance `floor_producer:MEASURED:witness_coherence=0.9257`. Three legs are collected, but coherence is an aggregate — three labels sharing one source are still one witness. Not changed this session.

---

## 4. Phase 4 — tool contract and status drift

| Claim (snapshot) | Verdict | Evidence |
|---|---|---|
| `arif_report` declared/exposed but not registered/invocable | **REFUTED** | live `arif_report(mode=stats)` → `status: completed`, `result.total_reports`, `result.by_kind`; `mode=inbox` → `result.count`, `result.reports`. Registered at `runtime/tools.py:29998` outside the 8-verb ABI profile (by design). |
| Some tools labelled PROVEN while in/out match = false | **CONFIRMED — label was under-specified, now tri-state** | see §4.1 |

### 4.1 What `in/out match = false` meant (OBS, then FIXED)

`capability_drift.compute_capability_matrix` computed the flags as a boolean AND-chain. Two different realities collapsed into `false`:

- both hashes present and **different** → real mismatch;
- observed hash **missing** → never measured.

Live cache (`/var/lib/arifos/observatory/capability-test-cache.json`): every public verb except `arif_init` carries `input_schema_hash: null`. So the matrix published `*_hash_match: false` for measurements nobody had taken, and the capability plane could never say `PROVEN 8/8`.

Also note the ladder's own comment: `PROVEN` is deliberately assigned *for durable success without full schema match*. `PROVEN` therefore means "it ran and succeeded recently, schema conformance unverified" — it does not mean "verified end-to-end".

Fix: `in_match`/`out_match` are now `True | False | None`. `PASS` still requires both `True` (fail-closed unchanged); `None` renders as unknown, not as mismatch.

`arif_judge`, `arif_forge`, `arif_seal` carry `last_error: "intentionally_skipped: mutation/irreversible tool"`. For `arif_judge` that classification is wrong — judge arbitrates, it does not mutate — so the one verb that gates everything is excluded from the proof matrix and can never be PROVEN by the probe.

---

## 5. Phase 5 — F6 MARUAH: wired, but unwritable

Chain: `_f6_maruah` → registered in `_PRODUCERS` → called from `/health` (§ `_wire_producer` F6 block) → reads `seals[*].payload.heart_critique` → `UNMEASURED` when absent.

Measured (OBS):

- `_f6_maruah` is imported and called on every `/health` build — verified live (`provenance: unmeasured_default:no_heart_critique`, not `f6_producer_error`).
- The seal chain has **277 rows**; **0** contain `heart_critique`.
- Row payloads are `None` (most) or `str` (2026-09-07 rows) — never the `dict` the producer assumed.
- `arif_seal(payload: str = "")` — the writer's payload is a **string**.

So F6 is not unimplemented. It is **unreachable**: no producer in the federation writes a `heart_critique` block that the meter can read. Its unit tests feed a synthetic dict shape the writer cannot emit.

Fixed (IMPLEMENTED + TESTED): the producer now accepts a JSON-string payload (parse or skip) and a `None` payload, so a real ledger row cannot crash it, and an unparseable payload reports `no_heart_critique` rather than `f6_producer_error`.

**Blocker (needs a decision, not code):** making F6 measurable requires F13 to rule whether `heart_critique` is a first-class seal-payload field, and which actor may assert it (the `arif_heart_critique` verb's output is the obvious candidate). Until then F6 must stay `UNMEASURED` — a passing score would be fabrication.

Consent and correction-propagation (`spec` priorities A/B) were **not** implemented: they depend on the same unwritten contract.

---

## 6. Phase 3 — one complete action chain (partial, blocked by A/B)

Controlled, harmless, reversible probe against the **current release** (no reuse of the 2026-09-09 canary):

| Case | Expected | Observed | Verdict |
|---|---|---|---|
| Governed session bind (`arif_init`, `requested_authority=OBSERVE_ONLY`) | session bound, band OBSERVE_ONLY | `SEAL-bc458936ff594056`, reason `OBSERVE_ONLY — identity not verified` | **PASS** |
| Valid read-only candidate (count lines in README) | SEAL or SABAR | **HOLD** — `INCONSISTENT_STATE: UNKNOWN_VERDICT_TOKEN:intermediate_trace_states.canonical_verdict=DENY` | **BLOCKED (defect B)** |
| Wrong actor (`999-IMPERSONATOR` + 333-AGI token) | refuse / not verified | HOLD, but `actor_verified: true` | **NOT PROVEN** — actor_id is not cross-checked against the session's bound actor |
| Widened scope (irreversible federated mutate) | refuse | HOLD + `requires actor_signature` + `FALSIFICATION_REQUIRED` | **PASS** |
| Duplicate delivery / retry idempotency | no duplicate effect | not exercised (blocked upstream by B) | UNKNOWN |
| Receipt ↔ effect reconciliation | receipt matches effect | not exercised (no effect was permitted) | UNKNOWN |

Defect B is the reason none of the success-path cases can be closed: **the running `verdict.py` fail-closes every response that carries `intermediate_trace_states.canonical_verdict`**, and the carve-out for that path exists only in the source tree.

The side-finding on actor binding is independent and more serious than a HOLD: an attacker holding any valid SCT can rename themselves in `actor_id` and still read `actor_verified: true`. Reported as **P0-security**, not patched (identity semantics are F13's).

---

## 7. Patches in this branch (all unit-tested, none deployed)

| File | Change | Test |
|---|---|---|
| `arifosmcp/runtime/rest_routes/rest_routes.py` | F1 scores via `_phi_fq_from_quotient`; constellation published as diagnostic; no-quotient → unmeasured | `test_honest_green_wiring_2026_10_26.py` (4) |
| `arifosmcp/runtime/rest_routes/rest_routes.py` | `_provenance_is_unmeasured()` used by status / `measured` / `floors_measured` — a skipped producer cannot pass | same file (3) |
| `arifosmcp/runtime/floor_producers.py` | `_f6_maruah` accepts `str`/`None` payloads; no AttributeError path | same file (4) |
| `arifosmcp/runtime/capability_drift.py` | schema-hash match is `True/False/None` | `test_capability_hash_match_tristate.py` (4) |

Test run: **15 new assertions pass**.
Regression check: `tests/runtime/test_no_synthetic_floor_evidence.py` + `tests/test_truth_chain_patches.py` fail **identically with and without these edits** (verified by stashing) — pre-existing debt from an in-flight sibling branch.
Environment block: 10 `test_capability_probe.py` failures are `socket.gaierror` (no DNS in this sandbox), not logic.

---

## 8. Deployment prerequisites and rollback (for a future authorised deploy)

1. **Do not deploy this branch alone.** Defect A/B must be fixed in the *same* install, or every tool keeps HOLDing and none of these fixes is observable.
2. Deploy = full `pip install` / `rsync -rt --checksum` of one commit, **not** a partial copy. Verify with the §1 hash table (11/11 `YES`).
3. Restart `arifos.service` (lowercase), then `?nocache=1` probe: F1 provenance must read `arifflow_probe:quotient=…`; F8 must read `unmeasured` while G is uncalibrated; `runtime_floors_status[*].measured` must agree with `floors_aggregate`.
4. Rollback = reinstall the previous pinned wheel; no schema migration is involved. These are pure code changes, reversible.

---

## 9. Still blocked (owner + exact missing evidence)

| # | Blocker | Owner | Missing |
|---|---|---|---|
| 1 | Mixed-version install; verdict carve-out absent → all HOLD | deploy lane (A-FORGE) + 888 | authorisation to install one commit end-to-end |
| 2 | `actor_verified` true on actor_id swap inside a valid session | F13 | decision: is actor_id advisory or binding? |
| 3 | F6 unreachable (no `heart_critique` writer) | F13 | ruling: is `heart_critique` a seal-payload field, and who may assert it? |
| 4 | F13 PASS scope reads as authorisation | F13 | wording/scope ratification; separate `action_authorization` signal is a new surface |
| 5 | `arif_judge` excluded from the proof matrix as "mutation tool" | capability probe owner | reclassification (judge does not mutate) |
| 6 | 8 pre-existing test failures on the branch | sibling session | not mine; listed so nobody re-diagnoses them |
