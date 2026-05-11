# arifOS <-> AF-FORGE Governed Diff Execution Blueprint

Status: Draft for implementation
Date: 2026-04-14
Scope: Enforce read-first planning and diff-only execution across Governance Plane and Agent Plane

## 1) Objective

Make edit-existing the default and make free-form write behavior impossible by contract.

Principles:
- Planner is read-only.
- Executor is diff-only.
- Policy enforcement is deterministic and non-LLM.
- High-risk or irreversible paths escalate to 888_HOLD.
- Terminal outcomes are sealed to VAULT999.

## 2) Plane Mapping

Governance Plane (arifOS):
- PlannerAgent: retrieval-first plan generation.
- PolicyEnforcer: static validation of every requested operation.
- ApprovalRouter: machine rulebook for auto-apply vs human gate.
- Judge/Vault hooks: 888_HOLD, SEAL, immutable audit trail.

Agent Plane (AF-FORGE):
- Agent Manager: accepts only governed ForgeExecutionManifest payloads.
- Agent Runner: applies diffs inside workspace volume under path and tool constraints.

Data Plane:
- Retrieval index (pgvector) for existing-file targeting.
- Immutable records for proposed_diffs and applied_diffs.

Infra/Observability Plane:
- Metrics and alerts for policy rejects, HOLD escalations, and file-change behavior.

## 3) Contract: ForgeExecutionManifest

This manifest is the only write-capable handoff from arifOS to AF-FORGE.

Required top-level fields:
- schema_version: string
- manifest_id: string (uuid)
- session_id: string
- task_id: string
- issued_at: ISO-8601
- expires_at: ISO-8601
- issuer: object
- governance: object
- workspace: object
- operations: list
- budgets: object
- observability: object

Required governance block:
- verdict: SEAL | PARTIAL | SABAR | VOID | 888_HOLD
- risk_tier: low | medium | high | critical
- confidence: float [0,1]
- floor_scores: object containing F1..F13 numeric values
- hold_reasons: list of machine-readable codes
- vault_preseal_ref: string (optional for dry run, required for apply)

Required workspace block:
- repo_ref: owner/repo or local workspace id
- writable_roots: list of allowed paths
- deny_paths: list of denied paths
- allowed_globs: list of glob patterns
- forbidden_globs: list of glob patterns

Operation type (diff-only):
- op: APPLY_UNIFIED_DIFF
- file_path: relative path
- base_blob_sha: expected preimage hash
- unified_diff: textual patch
- intent: modify_existing | create_new_with_justification
- retrieval_evidence: list of retrieval hit refs
- create_justification: required only if intent is create_new_with_justification

Forbidden operation types:
- DELETE_FILE
- TRUNCATE_FILE
- RAW_WRITE
- EXEC_SHELL_UNSCOPED

Budgets block:
- max_files_touched
- max_write_ops
- max_new_files
- max_runtime_seconds

Observability block:
- trace_id
- metrics_labels
- expected_change_summary

## 4) arifOS -> AF-FORGE Call Graph

1. Intake request
2. Retrieval-first planner pass
3. Planner emits candidate diffs and target-file decision
4. PolicyEnforcer validates all operations
5. ApprovalRouter decides:
   - auto-apply if low risk and within policy
   - else 888_HOLD and require human ratification
6. Judge emits final verdict
7. If verdict is SEAL, issue ForgeExecutionManifest
8. AF-FORGE Agent Manager validates manifest signature and constraints
9. Agent Runner applies diffs in sandbox workspace volume
10. Runner returns apply report (success/failure + resulting file hashes)
11. arifOS writes immutable VAULT999 seal with provenance

## 5) Enforcement Points (Exact)

A) Agent Manager ingress gate (AF-FORGE)
- Reject request unless payload type is ForgeExecutionManifest.
- Reject if verdict is not SEAL.
- Reject expired manifest.
- Reject if manifest signature or issuer trust chain fails.
- Reject if any operation type is not APPLY_UNIFIED_DIFF.

B) Agent Manager static policy gate
- Enforce writable_roots and deny_paths before scheduling runner.
- Enforce budgets before execution.
- Enforce create_new_with_justification requirement with retrieval evidence count >= configured minimum.
- Enforce protected path list for doctrine, policy, secrets, and governance files.

C) Agent Runner pre-apply gate
- Resolve file_path under workspace root and deny path traversal.
- Verify base_blob_sha matches current file preimage.
- Verify patch applies cleanly with no fuzz when high/critical risk.
- Deny patch hunks that remove more than configured line threshold without explicit approval token.

D) Agent Runner apply phase
- Apply unified diff only.
- No direct raw write API.
- No delete and no truncate primitives.
- Record per-file before_hash and after_hash.

E) Agent Runner post-apply gate
- Re-check changed files count against manifest budgets.
- Produce deterministic apply_report:
  - touched_files
  - created_files
  - rejected_ops
  - policy_events
  - resulting_hashes

F) Governance closure (arifOS)
- If apply_report contains policy violation, force 888_HOLD.
- Seal terminal outcome to VAULT999 with proposed_vs_applied diff lineage.

## 6) 888_HOLD Triggers for This Path

Mandatory HOLD conditions:
- files_touched > max_files_touched
- any op attempts delete/truncate/raw_write
- target path intersects deny_paths or protected constitutional files
- create_new_with_justification without retrieval evidence
- base_blob_sha mismatch on protected files
- risk_tier high/critical without explicit human approval token
- confidence below configured threshold
- conflicting evidence between planner rationale and live repo state

Required HOLD payload fields:
- hold_code
- violated_rule
- offending_operation_ref
- human_action_required
- remediation_options

## 7) Policy Profile (Machine-Readable Example)

Example policy keys to implement:
- enforce_diff_only: true
- enforce_read_first: true
- min_retrieval_hits_for_new_file: 3
- auto_apply_max_files: 1
- auto_apply_max_new_files: 0
- auto_apply_requires_additive_only: true
- deny_delete_truncate: true
- protected_paths: list
- mandatory_human_for_arch_changes: true

## 8) Metrics and SLOs

Emit these metrics from AF-FORGE and arifOS:
- governed_manifest_received_total
- governed_manifest_rejected_total
- diff_apply_success_total
- diff_apply_failure_total
- policy_reject_count
- hold_888_count
- files_touched_per_job
- new_files_created_per_job
- write_budget_exhausted_count
- base_sha_mismatch_count

SLO suggestions:
- 0 unauthorized writes
- 100% terminal outcomes sealed to VAULT999
- <1% false-positive policy rejects after tuning period

## 9) Rollout Plan

Phase 0 (Shadow mode):
- Generate manifests and reports but do not apply.
- Compare proposed diffs vs existing operator workflow.

Phase 1 (Low-risk auto-apply):
- Single-file, additive-only diffs.
- No new files.

Phase 2 (Guarded expansion):
- Allow limited multi-file edits with strict budgets.
- Keep architectural and protected paths human-gated.

Phase 3 (Full governed runtime):
- All writes require governed manifest.
- Any non-manifest write path disabled.

## 10) Implementation Backlog (Concrete)

In arifOS:
- Add manifest model and validator.
- Add planner output schema requiring retrieval_evidence.
- Add approval router rules for auto-apply policy.
- Add vault seal payload for proposed_vs_applied provenance.

In AF-FORGE:
- Add Agent Manager endpoint for governed manifests only.
- Add static policy gate and signature validation.
- Add runner patch engine with preimage hash checks.
- Add post-apply report and metric emission.

Cross-system:
- Define shared error code set and HOLD code taxonomy.
- Add contract tests for diff-only rejection scenarios.
- Add end-to-end test: read-first -> SEAL manifest -> apply -> VAULT999 record.

## 11) Non-Negotiable Rules

- No raw write path from LLM to filesystem.
- No delete/truncate unless explicit human ratification token is present.
- No new-file creation without retrieval evidence and policy approval.
- No execution without SEAL verdict.
- No terminal success without VAULT999 seal.

## 12) Related Canon

- AF-FORGE Zoo Control Matrix v0.1: ./AF_FORGE_ZOO_CONTROL_MATRIX_v0.1.md
