# SPRINT: TRACE-SPINE-IMPL
**Scope: C3/C4 decisions only. No new tools. No new MCP servers. Patch existing payloads.**

> DITEMPA BUKAN DIBERI — Do not begin until DRIFT-LEDGER-CLOSURE sprint is SEALED.

---

## Pre-condition
- [ ] `DRIFT-LEDGER-CLOSURE` all 4 gates PASSED
- [ ] `drift_count >= 1` proven on `mode=dry_run`
- [ ] Registry validation clean

---

## Per-Organ Implementation Checklist

### 000_INIT
| Task | Fields to add | State transition | Test required |
|---|---|---|---|
| Accept incoming `trace_packet` or generate new | `trace_id`, `parent_trace_id`, `session_id`, `epoch_id`, `actor_id`, `model_governance_card_hash`, `created_at` | `→ DECLARED` (no evidence) or `INGESTED` (evidence present) | Assert `trace_id` present in session context after init |
| Store `trace_packet` in L1 session store | `trace` + `lineage` + `claim_state` blocks | — | Assert trace survives within same process run |
| Pass `trace_packet` to all downstream organs | All trace fields | — | Assert `trace_id` echoed in first downstream call |

### 111_SENSE / 222_FETCH
| Task | Fields to add | State transition | Test required |
|---|---|---|---|
| Append observations to `lineage.inputs` | `trace_id`, source URL/ref, observation summary | `→ OBSERVED` | Assert `claim_state == OBSERVED` after first sense call |
| Append to `lineage.evidence_refs` | `trace_id`, evidence_ref ID | `→ INGESTED` | Assert `evidence_refs` non-empty after fetch |
| Block claim-state skip | — | Must not jump DECLARED → COMPUTED | Assert error if state skipped |

### 333_MIND
| Task | Fields to add | State transition | Test required |
|---|---|---|---|
| Tag deterministic outputs | `trace_id`, `input_hash`, `output_hash`, `claim_state: COMPUTED` | `→ COMPUTED` | Assert `claim_state == COMPUTED` on math outputs |
| Tag interpretive outputs | `trace_id`, `claim_state: INFERRED` | `→ INFERRED` | Assert `claim_state == INFERRED` on qualitative outputs |
| Append `tool_calls` record per MCP invocation | `call_id`, `trace_id`, `mcp`, `tool`, `input_hash`, `output_hash`, `status`, `claim_state_before`, `claim_state_after` | — | Assert tool_call record appended for every GEOX/WEALTH/WELL call |

### 666_HEART
| Task | Fields to add | State transition | Test required |
|---|---|---|---|
| Write risk analysis to `lineage.artifacts` | `trace_id`, artifact_ref, `claim_state: INFERRED` | Must not exceed `INFERRED` | Assert `claim_state ≤ INFERRED` in heart output |
| Tag WELL + WEALTH witness verdicts | `trace_id`, witness_ref, verdict | — | Assert witness packets present in lineage |

### 888_JUDGE
| Task | Fields to add | State transition | Test required |
|---|---|---|---|
| Compute `judge_state_hash` | Hash over: intent + evidence_refs + computed metrics + model_card_hash + floor verdicts | `→ JUDGE_REVIEWED` | Assert `judge_state_hash != null` after judge call |
| Set `claim_state → JUDGE_REVIEWED` | `claim_state`, `judge_state_hash` | `→ JUDGE_REVIEWED` | Assert only 888_JUDGE can write this state |
| Emit arifOS witness packet | `{verdict, floors_satisfied, floors_violated, trace_id}` | — | Assert witness packet attached to trace lineage |

### 010_FORGE
| Task | Fields to add | State transition | Test required |
|---|---|---|---|
| Require `judge_state_hash` for irreversible actions | `judge_state_hash` check at entry | 888_HOLD if null + irreversible | Assert FORGE refuses irreversible call without judge hash |
| Allow reversible actions with `claim_state ≤ INFERRED`, log explicitly | `trace_id`, `reversibility`, log entry | — | Assert log entry written for reversible-without-judge path |

### 999_VAULT
| Task | Fields to add | State transition | Test required |
|---|---|---|---|
| Construct final trace payload | Full `trace_packet` + all witness refs + `tool_calls` + `drift_events` | `→ VAULT_SEALED` | Assert `final_claim_state == VAULT_SEALED` in stored payload |
| Write `vault_entry_id` back to trace | `vault_entry_id` | — | Assert `vault_entry_id` non-null after seal |
| Only valid writer of `VAULT_SEALED` | Enforce at write layer | — | Assert no other organ can write `VAULT_SEALED` |

### 777_OPS
| Task | Fields to add | State transition | Test required |
|---|---|---|---|
| Compute `trace_completeness_ratio` | Ratio of rows with all required trace fields | — | Assert ratio > 0.95 on test traces |
| Report 5 seal-test pass/fail flags | `TRACE_STATIC_SEAL`, `CROSS_MCP_CONTINUITY_SEAL`, `NO_ORPHAN_ARTIFACT_SEAL`, `DRIFT_TRACE_SEAL`, `FULL_TRACE_RECONSTRUCTION_SEAL` | — | Assert all 5 flags present in telemetry JSON |
| Expose via telemetry JSON | Extend existing `{epoch,dS,peace2,...}` block | — | Assert telemetry includes `trace_completeness` field |

---

## Domain Organ Checklist

### GEOX
| Task | Fields to add | Claim state | Test |
|---|---|---|---|
| Add `trace_id` to all artifact metadata | `trace_id` on LAS, well-log, seismic records | — | Assert artifact metadata contains `trace_id` |
| Emit evidence packet after QC | `{trace_id, evidence_refs, claim_state: QC_VERIFIED}` | `→ QC_VERIFIED` | Assert packet emitted post-QC |
| Patch: ingest, QC, candidates, integrity | Accept + echo `trace_id` on all 4 tools | Never skip ladder | Assert claim_state transitions are monotonic |

### WEALTH
| Task | Fields to add | Claim state | Test |
|---|---|---|---|
| Tag all NPV/EVOI/DSCR outputs | `trace_id`, `claim_state: COMPUTED` | `→ COMPUTED` | Assert `claim_state == COMPUTED` on numeric outputs |
| Emit value witness | `{trace_id, analysis_ref, claim_state: COMPUTED}` | — | Assert witness packet linked to trace lineage |
| Link VAULT999 seals to trace | Add `trace_id` + `judge_state_hash` to existing WEALTH vault seals | — | Assert vault seal has `trace_id` field |

### WELL
| Task | Fields to add | Claim state | Test |
|---|---|---|---|
| Emit readiness witness | `{trace_id, readiness_ref, verdict}` | — | Assert readiness packet linked to trace |
| Pass as evidence input to HEART/JUDGE, never as judge | `trace_id`, `readiness_ref` | Input only | Assert WELL does not write `JUDGE_REVIEWED` |

---

## Five Seal Gates (All Must Pass Before Deploy)

| Gate | Pass condition |
|---|---|
| `TRACE_STATIC_SEAL` | Every result row has: `trace_id`, `session_id`, `actor_id`, tool name, `input_hash`, `output_hash`, `claim_state` |
| `CROSS_MCP_CONTINUITY_SEAL` | Same `trace_id` in arifOS + ≥1 of GEOX/WEALTH/WELL outputs |
| `NO_ORPHAN_ARTIFACT_SEAL` | Every `artifact_ref` has `trace_id`; every `judge_state_hash` has `evidence_refs`; every `vault_entry_id` has `judge_state_hash` |
| `DRIFT_TRACE_SEAL` | Drift event emitted → vault seal → readback → same `trace_id` → `count >= 1` |
| `FULL_TRACE_RECONSTRUCTION_SEAL` | `intent → evidence → computation → critique → judgment → vault` reconstructable from IDs alone |

---

## Scope Locks

- NO new tools
- NO new MCP servers
- NO schema explosion
- C3/C4 decisions only for mandatory enforcement
- C1/C2 best-effort trace propagation only
- 888_HOLD on any VAULT999 schema change, Postgres volume change, or prod forge gate tightening

---

## Final Report Required

1. Files changed
2. Trace fields added per organ
3. Claim-state transitions wired
4. All 5 seal tests: pass/fail
5. Trace reconstruction demo output (one real `trace_id`)
6. Remaining gaps
7. Seal classification: PARTIAL SEAL / FULL SEAL

---

*Forged: 2026-05-03T01:24:00+08:00 · Witness: Arif Fazil*
*DITEMPA BUKAN DIBERI — 999 SEAL ALIVE*
