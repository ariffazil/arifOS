# ADR-012: Receipt Lineage and Sealing

**Status:** DRAFT (stub — implementation pending)
**Date:** 2026-06-22

## Context

The canon requires append-only audit with cryptographic attribution. VAULT999 already provides hash-chained sealing. But receipt types (IntentReceipt, PlanReceipt, etc.) are not yet first-class objects — they're implicit in the audit event stream.

## Decision

Define six receipt types as Merkle-linked objects:

| Receipt | Emitted when | Required fields |
|---------|-------------|-----------------|
| `IntentReceipt` | Agent declares intent | intent_id, actor_id, action_class, timestamp |
| `PlanReceipt` | Plan created/approved | plan_id, intent_id, task_count, approver_id |
| `VerdictReceipt` | Judge issues verdict | verdict_id, verdict_type, candidate, floors_checked |
| `ExecutionReceipt` | Tool execution completes | tool_name, mode, verdict, output_hash, duration_ms |
| `RollbackReceipt` | Execution rolled back | original_receipt_id, reason, remediation |
| `SealReceipt` | VAULT999 seal written | seal_id, payload_hash, prev_seal_hash |

Each receipt hashes:
- Parent receipt ID(s)
- Actor ID
- Tool contract version
- Input hash
- Output hash
- Timestamp

This gives Merkle-grade lineage, not just text logs.

## Open questions

- Should receipts be stored in VAULT999 (append-only JSONL) or in Postgres (queryable)?
- How do receipts relate to the existing `AuditEvent` in `kernel_envelope.py`?
- Should receipt hashing use SHA-256 or BLAKE3?
- IncidentRecord and OverrideRecord: should they be receipt subtypes or separate objects?

DITEMPA BUKAN DIBERI.
