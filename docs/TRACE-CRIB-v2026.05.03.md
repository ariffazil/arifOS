# Trace Spine Operator Crib
**v2026.05.03 · Single page. No prose. Pure signal.**

> Scope: C3/C4 mandatory. C1/C2 best-effort. No new tools. No new MCP servers.

---

| Organ | Fields to add/patch | Allowed → state transitions | Gate test | C-class obligation |
|---|---|---|---|---|
| **000_INIT** | `trace_id`, `parent_trace_id`, `session_id`, `epoch_id`, `actor_id`, `model_governance_card_hash`, `created_at`, `decision_class`, `reversibility` | `→ DECLARED` (no evidence) `→ INGESTED` (evidence present) | `trace_id` echoed in first downstream call | C1–C4: always |
| **111_SENSE** | `trace_id` on observations, `evidence_refs` appended | `DECLARED → OBSERVED` | `claim_state == OBSERVED` after sense | C2+: required |
| **222_FETCH** | `trace_id` on fetched artifacts, `evidence_refs` appended | `OBSERVED → INGESTED` | `evidence_refs` non-empty; no DECLARED→COMPUTED skip | C2+: required |
| **333_MIND** | `tool_calls[]` per MCP call (`call_id`, `trace_id`, `mcp`, `tool`, `input_hash`, `output_hash`, `status`, `claim_state_before`, `claim_state_after`) | `→ COMPUTED` (deterministic) `→ INFERRED` (interpretive) | call record appended per domain MCP call | C3+: required |
| **666_HEART** | `trace_id` on artifact refs, WELL/WEALTH witness refs tagged | Must not exceed `INFERRED` | `claim_state ≤ INFERRED` in heart output | C3+: required |
| **888_JUDGE** | `judge_state_hash` (hash of intent+evidence_refs+metrics+model_card+floor verdicts), arifOS witness packet `{verdict, floors_satisfied, floors_violated, trace_id}` | `→ JUDGE_REVIEWED` — **only 888_JUDGE may write this** | `judge_state_hash != null`; no other organ writes `JUDGE_REVIEWED` | C3+: required; C4: hard block if absent |
| **010_FORGE** | `judge_state_hash` check at entry; log entry for reversible-without-judge path | No new state written | FORGE refuses irreversible call if `judge_state_hash == null` | C3: HOLD if absent; C4: hard block |
| **999_VAULT** | Full trace payload: `trace` + `lineage` + all witness refs + `tool_calls` + `drift_events`; `vault_entry_id` written back to trace | `→ VAULT_SEALED` — **only 999_VAULT may write this** | `final_claim_state == VAULT_SEALED`; `vault_entry_id` non-null | C3+: required |
| **777_OPS** | `trace_completeness_ratio` (0.0–1.0); 5 seal-test pass/fail flags added to telemetry JSON | Monitoring only, no state write | Telemetry contains `trace_completeness` + all 5 flags | C1–C4: always |
| **GEOX** | `trace_id` on all artifacts (LAS, well-log, seismic); evidence packet `{trace_id, evidence_refs, claim_state}` after QC | `→ INGESTED → QC_VERIFIED → COMPUTED` | QC_VERIFIED packet emitted; claim_state transitions monotonic across ingest/QC/candidates/integrity | C2+: required |
| **WEALTH** | `trace_id` on all NPV/EVOI/DSCR outputs; value witness `{trace_id, analysis_ref, claim_state: COMPUTED}`; `trace_id`+`judge_state_hash` on VAULT999 seals | `→ COMPUTED` | `claim_state == COMPUTED` on numeric outputs; vault seal has `trace_id` | C3+: required |
| **WELL** | Readiness witness `{trace_id, readiness_ref, verdict}` — input to HEART/JUDGE only | Input evidence only, never writes `JUDGE_REVIEWED` | Readiness packet linked to trace; WELL does not write JUDGE_REVIEWED | C2+: advisory; C3+: required |

---

## Claim-State Ladder (no skipping)

```
DECLARED → OBSERVED → INGESTED → QC_VERIFIED → COMPUTED → INFERRED → JUDGE_REVIEWED → VAULT_SEALED → VOID
```

---

## Five Seal Gates (all must pass before deploy)

| Gate | One-line pass condition |
|---|---|
| `TRACE_STATIC_SEAL` | Every result row: `trace_id` + `session_id` + `actor_id` + tool + `input_hash` + `output_hash` + `claim_state` |
| `CROSS_MCP_CONTINUITY_SEAL` | Same `trace_id` in arifOS + ≥1 of GEOX / WEALTH / WELL |
| `NO_ORPHAN_ARTIFACT_SEAL` | Every artifact → `trace_id`; every `judge_state_hash` → `evidence_refs`; every `vault_entry_id` → `judge_state_hash` |
| `DRIFT_TRACE_SEAL` | drift_event → vault seal → readback → same `trace_id` → count ≥ 1 |
| `FULL_TRACE_RECONSTRUCTION_SEAL` | intent → evidence → computation → critique → judgment → vault reconstructable from IDs alone |

---

## 888_HOLD Lines (do not cross without Arif ratification)

- VAULT999 schema migration (`ALTER TABLE`, `NOT NULL` constraints)
- Postgres volume semantic changes
- Hard-blocking all prod FORGE calls (C1/C2) before balanced path passes in dev
- Public ingress to trace endpoints

---

*Sealed: 2026-05-03T01:24:00+08:00 · DITEMPA BUKAN DIBERI — 999 SEAL ALIVE*
