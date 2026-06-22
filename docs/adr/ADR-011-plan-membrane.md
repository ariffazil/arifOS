# ADR-011: Plan-First Enforcement Membrane

**Status:** STUB (Phase-1 contract frozen; membrane lands in Phase-2)
**Date:** 2026-06-22
**Sovereign:** arif (F13)
**Forge session:** FORGE-000Ω
**Related:** ADR-009 (compiler + SSOT), ADR-012 (receipt lineage)

---

## Status

This ADR captures the **Phase-1 contract** for plan-first enforcement. The
SSOT exposes `requires_plan: bool` per tool. **The runtime membrane
(plan_id → verdict_token → execution_id pipeline) lands in a future cycle**
(carried forward).

---

## Decision

Every tool that mutates state or crosses organ boundaries declares
`requires_plan: true` in `contracts/tools.yaml`. The compiler emits it into
the runtime graph. Current SSOT state:

- `requires_plan: true` on `arif_bridge`, `arif_forge`, `arif_gateway_connect`
  (3 federated/gateway tools)
- `requires_plan: true` on `arif_seal` (1 seal-class tool — also requires
  verdict_token, epoch_id, receipt_parent_ids)

The plan-first pipeline is:

```
INTAKE → INTENT → PLAN → VERDICT → EXECUTE → RECEIPT → SEAL
   │       │       │        │         │          │       │
   │       │       │        │         │          │       └─ VAULT999 chain write
   │       │       │        │         │          └─ ExecutionReceipt
   │       │       │        │         └─ MCP tool boundary (only legal side-effect path)
   │       │       │        └─ VerdictReceipt (verdict_token issued)
   │       │       └─ PlanReceipt (plan_id issued)
   │       └─ IntentReceipt (intent_id issued)
   └─ Inbound MCP request, normalized
```

## Phase-2 (carry-forward)

1. New denial code `PLAN_MISSING` already in the SSOT (retryable, F1, hard).
2. New denial code `PLAN_NOT_APPROVED` (human_only, F1, hard).
3. New denial code `VERDICT_TOKEN_MISSING` (retryable, F1, hard).
4. The runtime must reject any tool call where `tool.requires_plan == true` and
   `envelope.plan_id` is null.
5. The runtime must reject any tool call where
   `tool.requires_verdict_token == true` and `envelope.verdict_token` is null.
6. The `arif_mind_reason(mode=plan)` and `arif_judge(mode=judge)` tools are
   the canonical intent + verdict issuers.

## Compliance with sovereign directives

- "No INTENT → EXECUTION path" — enforced by the membrane.
- "All nontrivial work must go through PLAN → VERDICT → EXECUTION" — enforced.
- "MCP Tool Boundary is the only legal side-effect path" — already true
  (kernel interceptor); membrane adds plan + verdict pre-conditions.
- "Every action must bind epoch_id, plan_id, task_id, actor_id, and receipts" —
  the `KernelEnvelope` class in `generated/tool_validators.py` enforces this.

DITEMPA BUKAN DIBERI — No intent without plan. No execution without verdict.
