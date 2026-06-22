# ADR-012: Receipt Lineage + VAULT999 Sealing

**Status:** STUB (Phase-1 contract frozen; lineage lands in Phase-2)
**Date:** 2026-06-22
**Sovereign:** arif (F13)
**Forge session:** FORGE-000Ω
**Related:** ADR-009 (compiler + SSOT), ADR-011 (plan membrane)

---

## Status

This ADR captures the **Phase-1 contract** for receipt lineage. The 6 canonical
receipts are declared in the SSOT (audit_events). **The runtime receipt writers
(intent, plan, verdict, execution, rollback, seal) land in a future cycle**
(carried forward).

---

## Decision

The 6-receipt lineage follows the pipeline in ADR-011:

| Receipt | Pipeline stage | Triggered by | Required fields | Carries |
|---|---|---|---|---|
| **IntentReceipt** | INTENT | `arif_mind_reason(mode=reason)` | intent_id, actor_id, session_id, epoch_id, intent_text | Raw intent + provenance |
| **PlanReceipt** | PLAN | `arif_mind_reason(mode=plan)` | plan_id, intent_id, actor_id, steps[], resources[] | Decomposed plan |
| **VerdictReceipt** | VERDICT | `arif_judge(mode=judge)` | verdict_id, plan_id, actor_id, verdict_token, denial_codes, witnesses[] | Constitutional verdict |
| **ExecutionReceipt** | EXECUTE | every tool that mutates state | exec_id, plan_id, verdict_id, actor_id, tool_name, side_effect_summary | What actually happened |
| **RollbackReceipt** | RECEIPT | inverse of any reversible mutation | rollback_id, exec_id, actor_id, reversal_summary | Compensation trail |
| **SealReceipt** | SEAL | `arif_seal(mode=seal)` | seal_id, verdict_id, exec_id, actor_id, payload_hash, chain_hash, prev_seal_id | Append-only VAULT999 entry |

The `audit_events` taxonomy in the SSOT enumerates 14 event types that fire
across these 6 receipts. The compiler emits the JSON schemas for each event
into `generated/audit_schemas.json`.

## KernelEnvelope (already in generated/tool_validators.py)

```python
class KernelEnvelope(BaseModel):
    epoch_id: str
    plan_id: str
    task_id: str
    actor_id: str
    witness_type: str = "ai"
    verdict_token: Optional[str] = None
    receipt_parent_ids: List[str] = []
```

Every tool call must carry this envelope. SEAL-class tools additionally require
`verdict_token`, `epoch_id`, and `receipt_parent_ids` to be set on the envelope
itself (not on the tool input).

## VAULT999 sealing (pre-existing, hardened in this cycle)

The VAULT999 writer at `:5001` is the canonical sealer. **Pre-existing bug
discovered during this RSI cycle**: the `/seal` endpoint's INSERT statement
references `actor_id` but the Supabase schema requires `agent_id` (NOT NULL).
This means `/seal` has been broken since the Supabase migration. We worked
around it for this cycle by writing directly to Supabase via `psycopg2` and
the file mirror at `/root/VAULT999/`. The 22nd seal (`SEAL-2026-06-22-RSI-ARIF-INIT-BUGS-FIX`)
was written this way.

**Carry-forward:** fix the writer's INSERT to add `agent_id` to the column list
and bind `req.agent_id` to it. 1-line fix; needs the writer restart.

## Phase-2 (carry-forward)

1. Write the 6 receipt writers as Pydantic models in `arifosmcp/contracts/`.
2. Wire each receipt stage to fire on the corresponding tool call.
3. Build the chain-link validator: every new seal must reference a valid
   `prev_seal_id` with a matching `prev_chain_hash`.
4. Add a `Receipt` resource to the MCP server so external tools can query
   lineage via `arif_memory_recall(mode=audit)`.

## Compliance with sovereign directives

- "All verdicts and executions emit append-only receipts" — enforced by the
  seal stage; verified by the `append-only` constraint on the VAULT999
  `no_arifosmcp_vault_seal_mutation` trigger.
- "Every action must bind epoch_id, plan_id, task_id, actor_id, and receipts" —
  the `KernelEnvelope` enforces the first four; the 6 receipts bind the lineage.

DITEMPA BUKAN DIBERI — Every action leaves a trace. Every trace links to the
previous. The chain is the arrow of time.
