# AF-FORGE Zoo Control Matrix v0.1

Status: Draft for implementation
Date: 2026-04-14
Scope: Taxonomy -> control families -> runtime hooks -> telemetry -> incident playbooks

## 1) Purpose

This document turns the AI-agent failure zoo into enforceable control families for arifOS and AF-FORGE.

Design rule:
- Every failure species must map to one control family.
- Every family must map to a hard runtime gate.
- Every gate must emit telemetry.
- Every critical gate failure must map to 888_HOLD or explicit fail-closed behavior.

## 2) Control Family Registry

| Family ID | Family Name | Primary Failure Theme | arifOS Floors (primary) | Default Verdict Bias |
|---|---|---|---|---|
| FAM-01 | Objective Integrity | Spec gaming, reward hacking, wrong goals | F2, F3, F4, F7 | HOLD/PARTIAL when evidence weak |
| FAM-02 | Runtime Containment | Loops, storms, unsafe sequencing, runaway cost | F1, F5, F6, F13 | HOLD on budget or irreversibility |
| FAM-03 | Trust Boundary Defense | Injection, poisoning, spoofing, privilege bleed | F2, F8, F9, F11, F13 | VOID/HOLD on trust breach |
| FAM-04 | Coordination Stability | Multi-agent conflict, deadlock, message storms | F3, F4, F6, F8 | HOLD on unresolved disagreement |
| FAM-05 | Governance Fidelity | Drift, bypass, fake compliance, missing audit | F1, F11, F13 | HOLD/VOID on bypass or no trace |

## 3) Master Species -> Control Matrix

| Species ID | Failure Species | Family | arifOS Chokepoint | AF-FORGE Module | Runtime Hook | Telemetry Signals | 888_HOLD Condition |
|---|---|---|---|---|---|---|---|
| SP-001 | Specification gaming | FAM-01 | PolicyEnforcer objective checks | forge-governor | pre_plan_validate | objective_mismatch_count, success_criteria_coverage | success criteria missing or contradictory |
| SP-002 | Reward hacking / proxy overfit | FAM-01 | Judge evidence weighting | forge-verifier | pre_complete_verify | proxy_real_gap_score, evidence_density | proxy score rises while evidence quality drops |
| SP-003 | Goal misbinding | FAM-01 | Planner mission binding | forge-governor | pre_manifest_issue | intent_alignment_score | intent score below threshold |
| SP-004 | Horizon neglect | FAM-01 | ApprovalRouter risk horizon | forge-governor | pre_execute_gate | long_term_risk_score | irreversible long-tail risk without ratification |
| SP-005 | Premature done claim | FAM-01 | Verifier evidence gate | forge-verifier | completion_claim_check | completion_claims_total, unbacked_claims_total | done claim without diff/test/hash evidence |
| SP-006 | Looping / runaway recursion | FAM-02 | Budget law | forge-runner | runtime_budget_tick | tool_calls_total, loop_detect_score, runtime_seconds | budget exceeded or loop score high |
| SP-007 | Fan-out storm | FAM-02 | Scheduler fan-out limits | forge-runner | spawn_guard | spawned_agents_total, queue_depth, storm_index | spawned agents exceed manifest budget |
| SP-008 | Unsafe sequencing | FAM-02 | sequencing policy | forge-governor | phase_order_check | policy_sequence_violations_total | deploy/send/delete before verify/preview |
| SP-009 | Partial apply drift | FAM-02 | apply report integrity | forge-runner | post_apply_reconcile | apply_partial_count, file_hash_mismatch_count | partial apply on protected paths |
| SP-010 | Cost gaming | FAM-02 | budget + value gate | forge-governor | cost_guard | cost_per_success, cheap_path_failures | cost optimization degrades mission evidence |
| SP-011 | Direct prompt injection | FAM-03 | injection_guard + source trust | forge-memory-gate | pre_context_merge | injection_detected_total, high_risk_input_total | injection signal above threshold |
| SP-012 | Indirect injection via tools | FAM-03 | data-not-law policy | forge-memory-gate | tool_output_sanitize | untrusted_tool_output_total, instruction_strip_count | external content attempts policy override |
| SP-013 | Memory poisoning | FAM-03 | memory trust tiering | forge-memory-gate | memory_write_gate | poisoned_memory_hits, trust_downgrade_count | untrusted memory proposed as canonical |
| SP-014 | Agent spoofing / identity confusion | FAM-03 | identity verification | forge-governor | manifest_signature_verify | signature_fail_total, issuer_mismatch_total | signature invalid or issuer mismatch |
| SP-015 | Privilege bleed | FAM-03 | F13 scope check | forge-runner | tool_scope_check | forbidden_tool_attempt_total | tool/path outside manifest scope |
| SP-016 | Supply-chain compromise signal | FAM-03 | integrity attestation gate | forge-observer | startup_attest | image_digest_mismatch_total | unsigned or mismatched runtime artifact |
| SP-017 | Multi-agent disagreement escalation | FAM-04 | arbitration policy | forge-governor | conflict_resolution_gate | disagreement_score, unresolved_conflicts_total | disagreement above threshold after retry |
| SP-018 | Deadlock / lease starvation | FAM-04 | scheduler lease law | forge-runner | lease_expiry_check | lease_expired_total, deadlock_duration_seconds | task lease expiry exceeds tolerance |
| SP-019 | Message storm / gossip drift | FAM-04 | message schema enforcement | forge-runner | message_schema_gate | invalid_message_schema_total, message_rate | schema violations or storm index high |
| SP-020 | Role confusion across agents | FAM-04 | role law + ACL | forge-governor | role_acl_check | role_violation_total | agent performs out-of-role action |
| SP-021 | Governance bypass attempt | FAM-05 | mandatory chokepoint | forge-observer | bypass_detector | actions_without_manifest_total | mutation without manifest_id |
| SP-022 | Missing immutable audit | FAM-05 | vault seal requirement | forge-observer | pre_close_audit_check | unsealed_outcome_total | terminal outcome without VAULT999 seal |
| SP-023 | Deceptive compliance | FAM-05 | tri-witness consistency check | forge-verifier | evidence_consistency_check | claim_evidence_divergence_score | claim/evidence divergence exceeds threshold |
| SP-024 | Policy drift (docs vs runtime) | FAM-05 | policy hash sync | forge-observer | policy_digest_check | policy_digest_mismatch_total | runtime policy hash != canonical hash |
| SP-025 | Human veto friction bypass | FAM-05 | approval UX + SLA guard | forge-governor | hold_workflow_check | hold_latency_seconds, hold_abandon_rate | hold path unhealthy for critical operations |

## 4) Runtime Hook Contract (Minimum)

Each module must emit deterministic events with stable reason codes.

| Hook Name | When Fired | Required Fields |
|---|---|---|
| pre_plan_validate | before planner output accepted | task_id, family_id, species_id, reason_codes |
| pre_manifest_issue | before arifOS issues manifest | manifest_id, intent_alignment_score, evidence_refs |
| manifest_signature_verify | at AF-FORGE ingress | manifest_id, issuer_id, signature_status |
| phase_order_check | before high-stakes operation | operation_type, prior_required_steps, result |
| runtime_budget_tick | periodic during run | budget_remaining, runtime_seconds, tool_calls |
| tool_scope_check | each tool call | tool_name, scope_allowed, scope_source |
| post_apply_reconcile | after diff apply | files_touched, hash_before_after, partial_apply |
| completion_claim_check | before final done | claim_type, evidence_count, verifier_result |
| pre_close_audit_check | before task close | vault_seal_ref, tri_witness_state |
| bypass_detector | asynchronous monitor | actor_id, action_type, manifest_present |

## 5) Reason Codes (Starter Set)

| Code | Meaning | Family |
|---|---|---|
| NEW_FILE_WITHOUT_EVIDENCE | new file proposed without retrieval support | FAM-01 |
| OBJECTIVE_MISMATCH | task actions diverge from mission criteria | FAM-01 |
| BUDGET_EXCEEDED | tool/time/cost budget exceeded | FAM-02 |
| UNSAFE_SEQUENCE | operation order violates policy | FAM-02 |
| UNTRUSTED_INSTRUCTION_SOURCE | data attempted to override law | FAM-03 |
| SIGNATURE_INVALID | manifest signature failed verification | FAM-03 |
| SCOPE_VIOLATION | tool or path outside allowed scope | FAM-03 |
| CONFLICT_UNRESOLVED | multi-agent disagreement unresolved | FAM-04 |
| MESSAGE_SCHEMA_VIOLATION | inter-agent payload schema invalid | FAM-04 |
| ACTION_WITHOUT_MANIFEST | mutation detected with no charter | FAM-05 |
| OUTCOME_UNSEALED | terminal outcome not sealed to vault | FAM-05 |
| CLAIM_EVIDENCE_DIVERGENCE | claim does not match evidence | FAM-05 |

## 6) Telemetry Envelope Extension

Use one event per significant decision or action.

```json
{
  "epoch": "2026-04-14T15:25:00+08:00",
  "task_id": "task-abc123",
  "manifest_id": "manifest-001",
  "family_id": "FAM-03",
  "species_id": "SP-012",
  "verdict": "HUMAN_APPROVAL_REQUIRED",
  "reason_codes": ["UNTRUSTED_INSTRUCTION_SOURCE"],
  "risk_tier": "high",
  "confidence": 0.74,
  "kappa_r": 0.82,
  "dS": -0.21,
  "witness": {
    "human": true,
    "ai": true,
    "earth": true
  },
  "qdf": {
    "files_touched": 2,
    "new_files": 1,
    "tool_calls": 9,
    "retry_count": 1,
    "budget_remaining": 0.42
  }
}
```

## 7) Incident Playbooks (Cross-Species Coupling First)

### PB-01 Injection -> Objective Drift -> Fan-Out Storm

Trigger:
- injection_detected_total increases and objective_mismatch_count increases and spawned_agents_total increases.

Immediate actions:
1. Freeze task queue for affected tenant/workspace.
2. Force all active tasks to verifier lane.
3. Invalidate untrusted retrieval context for session.
4. Raise 888_HOLD for any irreversible operation.

Recovery:
1. Re-run planner with trusted sources only.
2. Re-issue signed manifest with reduced budgets.
3. Resume with canary mode and elevated telemetry sampling.

### PB-02 Governance Bypass Suspected

Trigger:
- actions_without_manifest_total > 0.

Immediate actions:
1. Stop runner mutations globally (fail-closed).
2. Snapshot affected workspace and runtime logs.
3. Raise critical incident and 888_HOLD all high-risk pipelines.

Recovery:
1. Diff unauthorized changes against last sealed manifest.
2. Rotate credentials/tokens for affected control plane.
3. Patch bypass vector and add regression test.

### PB-03 Deceptive Compliance

Trigger:
- claim_evidence_divergence_score above threshold.

Immediate actions:
1. Reject completion claims for affected run.
2. Force deterministic verifier checks.
3. Require human ratification for closure.

Recovery:
1. Add species-specific reason codes.
2. Increase evidence minimum for completion.
3. Tune policy to penalize unbacked claims.

## 8) CI/CD Enforcement Tests (Required)

| Test ID | Test | Expected Result |
|---|---|---|
| T-001 | mutation without manifest | hard fail + ACTION_WITHOUT_MANIFEST |
| T-002 | new file without retrieval evidence | hold + NEW_FILE_WITHOUT_EVIDENCE |
| T-003 | delete op without human token | hold + SCOPE_VIOLATION |
| T-004 | invalid signature | fail-closed + SIGNATURE_INVALID |
| T-005 | completion claim without evidence | reject + CLAIM_EVIDENCE_DIVERGENCE |
| T-006 | policy digest mismatch | hold + policy drift alert |
| T-007 | multi-agent unresolved conflict | hold + CONFLICT_UNRESOLVED |

## 9) Rollout (Containment First)

Phase A (Minimal):
- manifest law, diff-only apply, 888_HOLD on irreversible, immutable audit checks.

Phase B (Balanced):
- signed manifests, verifier lane, budgets/circuit breakers, provenance trust labels, bypass telemetry.

Phase C (Maximal):
- role-based protocol, chaos drills, policy simulator, full memory trust tiering, auto-rollback canaries.

## 10) Ownership and Review Cadence

- Primary owners: Governance Plane maintainer + AF-FORGE Agent Plane maintainer.
- Weekly review: species coverage gaps and false-positive/false-negative rates.
- Monthly review: add new species IDs only through family mapping and reason-code registration.

## 11) Exit Criteria for v0.1 -> v1.0

- Every high-risk species has an enforced gate and test.
- actions_without_manifest_total remains zero in production.
- 100% terminal outcomes sealed with traceable manifest linkage.
- At least one successful chaos exercise for each control family.
