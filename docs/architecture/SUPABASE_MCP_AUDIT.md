# Supabase–MCP Integration Audit
**Date:** 2026-06-02
**Auditor:** Ω-FORGE (Kim)
**Scope:** arifOS, GEOX, WEALTH, WELL, A-FORGE, AAA

---

## Arif's Rule (Source of Truth)

> Supabase is a **recorder, registry, artifact shelf, and prompt/resource index**.
> It does NOT route MCPs, control MCPs, or replace arifOS.

**Pattern A (arifOS writes for everyone):**
Approvals, judge verdicts, final seals, high-risk tool calls, floor crossings.

**Pattern B (each organ writes its own domain):**
GEOX → evidence/artifacts
WEALTH → transactions/portfolio snapshots
WELL → well_states/agent_telemetry
A-FORGE → build artifacts/execution receipts
AAA → reads only

---

## 1. What Exists vs What's Needed

| Organ | Adapter Exists? | Called from MCP? | Schema Correct? | Status |
|-------|----------------|------------------|-----------------|--------|
| **arifOS** | ✅ `supabase_adapter.py` | ❌ NO | ✅ Mostly | Kernel hook missing |
| **GEOX** | ❌ NO | ❌ NO | N/A | No integration |
| **WEALTH** | ❌ NO | ❌ NO | N/A | No integration |
| **WELL** | ❌ NO | ❌ NO | N/A | No integration |
| **A-FORGE** | ⚠️ Partial | ❓ Unknown | ❌ NO | Wrong tables/columns |
| **AAA** | ✅ Views | ✅ YES | ✅ | Cockpit working |

---

## 2. Live Schema Map

### Production Tables (public.*)

| Table | Rows | Key Fields |
|-------|------|-----------|
| `arifosmcp_tool_calls` | **0** | `id` (bigserial), `organ`, `session_id`, `tool_name`, `agent_id`, `input_hash`, `verdict`, `floor_triggered`, `duration_ms`, `epoch`, `result_code`, `peace2`, `error_msg` |
| `vault_sealed_events` | **1337** | `id`, `event_id` (UUID), `event_type`, `session_id`, `actor_id`, `stage`, `verdict`, `risk_tier`, `payload`, `source_ledger`, `prev_leaf`, `merkle_leaf`, `signature`, `signed_by`, `sealed_at` |
| `arifosmcp_sessions` | **0** | `id`, `session_id`, `actor_id`, `status`, `risk_tier`, `verdict`, `telemetry`, `opened_at`, `closed_at`, `anchor_seal_id`, `close_seal_id`, `state_snapshot` |
| `arifosmcp_approval_tickets` | **0** | `id`, `ticket_id`, `action_plan` (jsonb), `human_verdict`, `requested_at`, `resolved_at` |
| `arifosmcp_canon_records` | **0** | `id`, `record_type`, `reference_id`, `body` (jsonb), `verdict`, `witness` (jsonb), `sealed_by`, `epoch` |
| `arifosmcp_floor_rules` | **6** | `id`, `floor_code`, `rule_name`, `constraint_definition` (jsonb), `is_active`, `updated_at` |
| `arifosmcp_transactions` | **0** | `id`, `tx_type`, `asset`, `amount`, `currency`, `metadata` (jsonb), `epoch` |
| `arifosmcp_portfolio_snapshots` | **0** | `id`, `snapshot_ts`, `holdings` (jsonb), `total_value`, `currency` |
| `arifosmcp_well_states` | **1** | `id`, `agent_id`, `state_key`, `state_value` (jsonb), `updated_at`, `created_at` |
| `arifosmcp_vault_seals` | **❌ TABLE DOES NOT EXIST** | — |

### Phase 1 Design Tables (s000/s999)

| Table | Rows | Notes |
|-------|------|-------|
| `s000.tool_calls` | 14 | UUID primary key, rich schema with `arguments`/`result` jsonb |
| `s000.approvals` | 7 | FK to `tool_call_id` (UUID) |
| `s000.evidence_items` | 10 | Geo/domain evidence |
| `s000.artifacts` | 10 | Artifact metadata |
| `s000.judge_verdicts` | 6 | Constitutional verdicts |
| `s000.constitutional_floors` | 13 | F1–F13 design |
| `s000.mcp_servers` | 5 | Server registry |
| `s000.mcp_manifest_snapshots` | 1 | Tool surface snapshot |
| `s999.vault999_ledger` | 10 | Phase 1 v2 ledger |

---

## 3. A-FORGE Client — Schema Violations

A-FORGE's `supabase_client.ts` writes to **wrong tables and wrong columns**:

### `arifosmcp_vault_seals` — TABLE DOES NOT EXIST
A-FORGE calls `sb.from("arifosmcp_vault_seals").insert(...)` but this table **does not exist**.
The canonical vault table is `vault_sealed_events` (1,337 rows).
**Fix:** Route to `vault_sealed_events` with correct columns.

### `arifosmcp_tool_calls` — Wrong Column Names
A-FORGE inserts: `organ`, `tool_args`, `tool_result`, `floor_triggered`, `verdict`
Production schema has: `organ` ✅, `floor_triggered` ✅, `verdict` ✅
But `tool_args` → `arguments` (jsonb), `tool_result` → `result` (jsonb), `run_id` → not in schema

### `arifosmcp_sessions` — Wrong Column Names
A-FORGE inserts: `session_id`, `agent_id`, `risk_tier`, `declared_intent`
Production schema has: `session_id` ✅, `agent_id` ✅, `risk_tier` ✅
But `declared_intent` → `status`? Schema doesn't have `declared_intent`.

### `logToolCall()` — Writes to `arifosmcp_tool_calls` which is empty (0 rows)
Even if column names matched, the table has 0 rows — nothing is being recorded.

---

## 4. arifOS Kernel Hook — Missing

**Status: NOT WIRED**

The `supabase_adapter.py` exists and works (7/7 PASS in design mode). But the arifOS MCP server (`/root/arifOS/arifosmcp/server.py`) does NOT call any adapter function after tool execution.

Every MCP tool invocation should produce a receipt:

```
MCP tool executes
  ↓
arifOS MCP server receives result
  ↓
supabase_adapter.record_tool_call() ← NOT BEING CALLED
  ↓
Supabase records tool call
```

This is the single biggest gap. Without this, Supabase has no canonical record of what arifOS actually did.

---

## 5. GEOX / WEALTH / WELL — No Integration

| Organ | Supabase Integration |
|-------|----------------------|
| GEOX | Zero. No adapter, no receipts, no artifact metadata writing. |
| WEALTH | Zero. TypeScript tools have no Supabase client. |
| WELL | Zero. `arifosmcp_well_states` has 1 stale row, not being updated. |

Per Arif's spec, each organ should write Pattern B records via its own lightweight adapter.

---

## 6. What Works

- ✅ `scripts/aaa_cockpit.py` — reads unified views, works correctly
- ✅ `scripts/aaa_unified_views.sql` — 10 views reading both namespaces
- ✅ `supabase_adapter.py` — correctly structured, 7 functions, multi-mode
- ✅ Production `vault_sealed_events` — 1,337 sealed events canonical
- ✅ Append-only triggers on s999.vault999_ledger

---

## 7. Priority Fix Order

### P0 — CRITICAL (breaks existing data flow)

1. **arifOS kernel hook** — Wire `record_tool_call()` into arifOS MCP server. This is the constitutional kernel. Every tool call needs a receipt.

2. **A-FORGE vault writes** — Fix `supabase_client.ts` to write to `vault_sealed_events` (not `arifosmcp_vault_seals`). Use correct column names.

### P1 — HIGH (enables domain receipts)

3. **GEOX adapter** — Lightweight Python adapter for `evidence_items` and `artifacts`. GEOX tools call it after producing domain output.

4. **WEALTH adapter** — TypeScript adapter for `transactions` and `portfolio_snapshots`.

5. **WELL adapter** — Python adapter for `well_states`.

### P2 — MEDIUM (completes the picture)

6. **A-FORGE tool call receipts** — Fix column names, write to `arifosmcp_tool_calls`.

7. **AAA cockpit enhancement** — Show tool call receipts, domain evidence, artifact index.

8. **MCP manifest snapshots** — Periodic tool surface snapshots from each organ.

---

## 8. Concrete Fixes Needed

### A-FORGE `supabase_client.ts`

```typescript
// WRONG (table doesn't exist):
sb.from("arifosmcp_vault_seals").insert(...)

// RIGHT (table exists, 1337 rows):
sb.from("vault_sealed_events").insert({
  event_id: record.sealId,
  event_type: "verdict",
  session_id: record.sessionId,
  actor_id: profileName,
  verdict: record.verdict,
  risk_tier: "high",
  payload: { task, finalText, turnCount, floors_triggered, escalation },
  prev_leaf: record.prevHash,
  merkle_leaf: record.hashofinput,
  signature: null,
  signed_by: "arifOS-A-FORGE",
  sealed_at: record.timestamp,
})
```

### arifOS MCP server.py

After each tool execution, call:
```python
await record_tool_call(
    session_ref=session_id,
    tool_name=tool_name,
    organ_code="arifos",
    arguments=tool_args,
    result=tool_result,
    risk_tier=risk_tier,
    verdict=verdict,
    latency_ms=duration_ms,
)
```

---

## 9. What NOT To Do

- ❌ Do NOT connect Supabase as an MCP router
- ❌ Do NOT make Supabase the session brain
- ❌ Do NOT add blocking writes — all must be fail-soft
- ❌ Do NOT route GEOX/WEALTH/WELL through arifOS for domain records
- ❌ Do NOT write `arifosmcp_vault_seals` (doesn't exist)
- ❌ Do NOT touch VAULT999 ledger writes (only arifOS/VAULT999 service)

---

## 10. Summary for Arif

The architecture Arif described is correct and clean. Here's the reality:

| What Arif Described | What Exists | Gap |
|---------------------|-------------|-----|
| arifOS writes governance receipts | `supabase_adapter.py` exists, not called | **Kernel hook missing** |
| GEOX writes evidence/artifacts | Nothing | **No adapter** |
| WEALTH writes financial records | Nothing | **No adapter** |
| WELL writes substrate state | Nothing | **No adapter** |
| A-FORGE writes execution receipts | Client exists, wrong schema | **Table/column mismatch** |
| AAA reads unified views | Cockpit works ✅ | Working correctly |

**Biggest single gap:** The arifOS MCP kernel doesn't call the adapter. Every tool invocation is invisible to Supabase.

**Recommended next step:** P0 (1) — arifOS kernel hook. This is the constitutional core and the most impactful fix.
