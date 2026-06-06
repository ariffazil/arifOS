# AAA-Supabase Record Doctrine
**Authority:** 888 (Muhammad Arif bin Fazil, F13 SOVEREIGN)
**Version:** 1.0
**Date:** 2026-06-02
**Status:** RATIFIED
**doctrine_id:** AAA-SUPABASE-RECORD-DOCTRINE
**ratified_at:** 2026-06-02
**authority:** Muhammad Arif bin Fazil (F13 SOVEREIGN)

---

## Preamble

AAA is the constitution. Supabase is the court record. VAULT999 is the national archive.

Without this doctrine, Supabase is just tables. With it, Supabase becomes constitutional receipts — proof that the system obeyed the law.

This doctrine answers:

> **Which record receives which event, under which floor, with what evidence, and when does it become permanent?**

---

## The Six-Question Filter

Before any event is written to any layer, the doctrine asks:

| # | Question | If Yes → | If No → |
|---|----------|----------|---------|
| 1 | Is this an action or observation? | Record to tool_calls | Skip |
| 2 | Does a floor require human approval? | Create approval_ticket | Proceed |
| 3 | Is the verdict SEAL? | Promote to vault_sealed_events | Keep in tool_calls |
| 4 | Is this session final? | Promote to sessions (closed) | Keep sessions (open) |
| 5 | Is this record a constitutional artifact? | Promote to canon_records | Keep in domain table |
| 6 | Is this the second seal of a duplicate event? | Skip duplicate | Write to vault |

---

## Record Type Jurisdiction

Each record type has a specific constitutional job:

### `arifosmcp_tool_calls` — The Daily Log

**Jurisdiction:** Every MCP tool execution that alters state.

**AAA floors that trigger recording:**
- F01 (AMANAH): If `risk_tier >= 3`, requires `ack_irreversible`
- F02 (TRUTH): Must include `evidence_refs` if claims made
- F11 (AUDIT): Every action logged with reasoning trace
- F13 (SOVEREIGN): If `requires_888 = true`, ticket must be open

**Required fields per record:**
```
tool_name, session_id, organ, verdict, risk_tier
floor_triggered[], evidence_refs[], approval_ticket_id?
input_hash, duration_ms, epoch, result_code, error_msg?
```

**Verdict mapping:**
| arifOS verdict | result_code | seal_status |
|---|---|---|
| SEAL | SUCCESS | eligible |
| HOLD | BLOCKED | pending |
| VOID | ERROR | rejected |
| SABAR | PARTIAL | conditional |
| REFUSE | ERROR | rejected |

**Seal eligibility:** Only records with `verdict = SEAL` and `risk_tier >= 2` may be promoted to `vault_sealed_events`.

---

### `vault_sealed_events` — The Sealed Archive

**Jurisdiction:** Final, irreversible outcomes that must never be silently changed.

**AAA floors that require sealing:**
- F01 (AMANAH): All irreversible actions (deletion, deployment, seal itself)
- F11 (AUDIT): Append-only, no UPDATE, no DELETE
- F13 (SOVEREIGN): `human_ratifier` must be present

**Required fields per record:**
```
event_type, session_id?, actor_id, stage, verdict
risk_tier, payload (jsonb), source_ledger
prev_leaf, merkle_leaf, signature, signed_by, sealed_at
```

**Event type taxonomy:**
| event_type | Description | Example |
|---|---|---|
| `ARIFOS_JUDGE_SEAL` | arifOS judge approved | arif_judge_deliberate → SEAL |
| `ARIFOS_VAULT_SEAL` | Vault final seal | arif_vault_seal |
| `ARIFOS_HEART_CRITIQUE` | Heart critique completed | arif_heart_critique |
| `MCP_TOOL_SEAL` | High-risk tool executed | arif_forge_execute |
| `FLOOR_CROSSING` | Floor triggered | F01, F09, F13 crossings |
| `A-FORGE_SEAL` | A-FORGE execution seal | forge execution |
| `AAA_APPROVAL_GRANTED` | Human approved | 888_HOLD cleared |
| `AAA_APPROVAL_DENIED` | Human denied | veto |

**Promotion rule from tool_calls:**
```
tool_calls.verdict = 'SEAL'
AND tool_calls.risk_tier >= 2
AND tool_calls.result_code = 'SUCCESS'
→ promote to vault_sealed_events with event_type = 'MCP_TOOL_SEAL'
```

---

### `arifosmcp_sessions` — Session Lifecycle

**Jurisdiction:** Each governed session from init to seal.

**AAA floors:**
- F11 (AUDIT): Every session logged
- F13 (SOVEREIGN): Opened with sovereign identity
- F04 (CLARITY): `declared_intent` must be present

**State machine:**
```
open (session_id, agent_id, declared_intent)
  → running (first tool call)
  → closed (final_verdict issued)
```

**Seal eligibility:** Session is sealed when `final_verdict` is set. Promotes session summary to `vault_sealed_events` with `event_type = 'SESSION_SEAL'`.

---

### `arifosmcp_approval_tickets` — The Hold Queue

**Jurisdiction:** Actions paused for human (888) review.

**AAA floors:**
- F01 (AMANAH): Human must approve before irreversible action
- F13 (SOVEREIGN): Only Arif can clear a HOLD

**Ticket states:**
```
open → approved (Arif grants)
open → denied (Arif denies)
open → expired (timeout)
open → voided (tool cancelled)
```

**Fields that must be present:**
```
ticket_id, session_id, status, risk_level
intent_model, domain?, data, created_at
```

**Escalation:** Tickets open > 24h without resolution trigger `L13_ESCALATION` event in `vault_sealed_events`.

---

### `arifosmcp_canon_records` — Constitutional Artifacts

**Jurisdiction:** ADRs, doctrine changes, floor rule changes.

**AAA floors:**
- F01 (AMANAH): Immutable after creation
- F10 (ONTOLOGY): Consistent naming, no structural conflicts
- F11 (AUDIT): Full reasoning trace

**ADR states:**
```
draft → proposed → ratified → deprecated
```

**Seal eligibility:** `status = ratified` → `vault_sealed_events` with `event_type = 'CANON_RATIFIED'`.

---

### `arifosmcp_transactions` — Financial Records

**Jurisdiction:** Capital movements, allocations, commitments.

**AAA floors:**
- F01 (AMANAH): No deletion, no reversal
- F05 (PEACE): `destruction_score` must be computed
- F11 (AUDIT): Full audit trail

**Seal eligibility:** Transactions with `amount >= 10000 MYR` → `vault_sealed_events` with `event_type = 'FINANCIAL_SEAL'`.

---

### `arifosmcp_portfolio_snapshots` — Wealth State

**Jurisdiction:** Periodic wealth state for WEALTH organ.

**AAA floors:**
- F05 (PEACE): `peace2` component of dignity impact
- F11 (AUDIT): Immutable snapshots

**Frequency:** Daily snapshot minimum. Promoted to `vault_sealed_events` weekly.

---

### `arifosmcp_well_states` — Human Vitality State

**Jurisdiction:** Sovereign's biometric and readiness state.

**AAA floors:**
- F05 (PEACE): Human dignity and vitality
- F06 (EMPATHY): Weakest stakeholder — Arif himself
- F13 (SOVEREIGN): Only Arif controls his own state

**Seal eligibility:** Weekly `well_state` → `vault_sealed_events` with `event_type = 'WELL_STATE_SEAL'`. Daily states stay in `arifosmcp_well_states`.

---

## Memory Layer Routing

| Layer | What it holds | What triggers it | Governance |
|-------|--------------|-----------------|------------|
| **Redis (L1)** | Current session, in-progress approvals, live queue | Every event | F11 partial |
| **Supabase** | Official records, tool calls, sessions, tickets, transactions | F11 requires all logged | F11 full |
| **Qdrant (L3)** | Semantic similarity of past doctrine, claims, evidence | Claims, interpretations | F02 (TRUTH) |
| **Graphiti (L5)** | Relationships: tool → agent → evidence → verdict | High-risk executions | F03 (WITNESS) |
| **VAULT999 (L6)** | Final, sealed, permanent records | `verdict = SEAL` + `risk_tier >= 2` | F01 + F11 + F13 |

---

## Floor → Record Type Mapping

| Floor | Primary Record Type | Trigger Condition |
|-------|--------------------|--------------------|
| F01 AMANAH | `approval_tickets` | `risk_tier >= 3` OR `ack_irreversible = true` |
| F02 TRUTH | `arifosmcp_tool_calls` | `evidence_refs` must be non-empty |
| F03 WITNESS | `vault_sealed_events` | `W3 >= 0.95` achieved |
| F04 CLARITY | `arifosmcp_sessions` | `declared_intent` present |
| F05 PEACE | `arifosmcp_well_states`, `transactions` | `destruction_score` computed |
| F06 EMPATHY | `arifosmcp_well_states` | Stakeholder impact assessed |
| F07 HUMILITY | `arifosmcp_tool_calls` | `omega_0` in [0.03, 0.05] |
| F08 GENIUS | `arifosmcp_tool_calls` | `G >= 0.80` achieved |
| F09 ANTIHANTU | `arifosmcp_tool_calls` | `C_dark < 0.30` verified |
| F10 ONTOLOGY | `arifosmcp_canon_records` | Naming consistency verified |
| F11 AUDIT | ALL record types | Every event |
| F12 INJECTION | `arifosmcp_tool_calls` | Input sanitization verified |
| F13 SOVEREIGN | `vault_sealed_events`, `approval_tickets` | `human_ratifier` present |

---

## Evidence Requirements

| Record Type | Evidence Required | Form |
|-------------|-----------------|------|
| `tool_calls` | If `risk_tier >= 2` | `evidence_refs[]` — URLs, artifact IDs |
| `vault_sealed_events` | Always | `merkle_leaf` (hash chain) + `signature` |
| `approval_tickets` | Always | `intent_model` + `risk_level` |
| `canon_records` | Always | `payload` with full reasoning |
| `transactions` | If `amount >= 10000 MYR` | `metadata` with authorization |

---

## The Seal Promotion Rule

```
FROM    arifosmcp_tool_calls
WHERE   verdict = 'SEAL'
AND     risk_tier >= 2
AND     result_code = 'SUCCESS'
AND     floor_triggered IS NOT NULL
SELECT  event_type    = 'MCP_TOOL_SEAL'
        session_id
        actor_id     = organ
        stage        = tool_name
        verdict
        risk_tier
        payload      = { tool_name, tool_args, result_summary }
        source_ledger = 'arifOS:kernel:ingress'
        merkle_leaf  = input_hash
        signature    = seal_id (generated)
        signed_by    = organ
        sealed_at    = NOW()
INSERT INTO vault_sealed_events
```

**VAULT999 promotion** (L6 from Supabase):
```
FROM    vault_sealed_events
WHERE   event_type IN ('ARIFOS_JUDGE_SEAL', 'ARIFOS_VAULT_SEAL', 'FINANCIAL_SEAL', 'WELL_STATE_SEAL')
AND     risk_tier >= 3
SELECT  (same record)
INSERT INTO VAULT999/outcomes.jsonl + Supabase merkle_leaf chain
```

---

## What Stays Temporary

These records are **Supabase only** — they do NOT promote to VAULT999:

- `tool_calls` with `risk_tier = 1` and `verdict = SEAL`
- `sessions` that are still `open`
- `approval_tickets` that are still `open`
- `arifosmcp_transactions` with `amount < 10000 MYR`
- `arifosmcp_portfolio_snapshots` (daily, not weekly)
- Redis ephemeral state (L1)

---

## What Requires Human Approval (F01 + F13)

These events **must** have an open `approval_ticket` before proceeding:

| Event | Risk Level | Ticket Required |
|-------|-----------|-----------------|
| `arif_forge_execute` | TIER_3 | YES |
| `arif_vault_seal` | TIER_3 | YES |
| `arif_judge_deliberate` with HOLD | TIER_2 | YES |
| `DROP TABLE` or equivalent | TIER_3 | YES |
| Secret rotation | TIER_3 | YES |
| Cross-repo architecture change | TIER_3 | YES |
| Constitutional floor change (F1-F13) | TIER_3 | YES (Arif only) |

---

## What Triggers VAULT999 Sealing

Only these event types are sealed into VAULT999:

| Event Type | Seal Criteria | Human Ratifier Required |
|------------|--------------|------------------------|
| `ARIFOS_JUDGE_SEAL` | Always | Yes |
| `ARIFOS_VAULT_SEAL` | Always | Yes |
| `MCP_TOOL_SEAL` | `risk_tier >= 3` | Yes |
| `FINANCIAL_SEAL` | `amount >= 10000 MYR` | Yes |
| `WELL_STATE_SEAL` | Weekly | Yes |
| `SESSION_SEAL` | Session closed | Yes |
| `CANON_RATIFIED` | ADR ratified | Yes |

---

## Failure Modes

| Failure | System Response |
|---------|-----------------|
| Supabase write fails | Log to local file, retry async, never block tool |
| VAULT999 seal fails | Keep in `vault_sealed_events`, retry on next cycle |
| Approval ticket never cleared | After 24h: emit `L13_ESCALATION` event |
| Evidence ref is empty for `risk_tier >= 2` | Set `verdict = HOLD`, do not execute |
| Duplicate seal attempt | Skip write, increment `duplicate_count` in metadata |

---

## Enforcement

This doctrine is enforced by:
- **arifOS kernel hook** (F01, F11): Every tool call receipt checked
- **AAA cockpit** (F13): Shows all pending tickets, recent seals, floor crossings
- **Supabase adapter** (F11): Fail-soft writes, retry logic, never block
- **VAULT999 bridge** (F01, F13): Merkle chain integrity, human ratifier verification

---

**SEAL: RATIFIED**

> AAA gives law. arifOS gives judgment. MCP gives action. Supabase gives record. VAULT999 gives finality. AAA cockpit gives visibility. Arif remains the final judge.

---

## Addendum: AAA Namespace Receipt Fields (v1.2 — 2026-06-02)

Following the ratification of the [AAA Namespace Doctrine](AAA_NAMESPACE_DOCTRINE.md), every Supabase record now carries explicit namespace context. The bare field name `aaa_version` is banned from new schemas.

### New Fields (all tables)

| Field | Type | Default | Purpose |
|-------|------|---------|---------|
| `aaa_surface` | `TEXT` | `'AAA-HF'` | Which AAA surface governed this record |
| `aaa_doctrine_version` | `TEXT` | `NULL` | Version of the AAA-HF corpus in effect |
| `aaa_canon_refs` | `TEXT[]` | `NULL` | Canonical references from the HF corpus |
| `floor_refs` | `TEXT[]` | `NULL` | All floors triggered (multi-floor replacement for `floor_triggered`) |
| `record_class` | `TEXT` | `'constitutional_receipt'` | Semantic class of this record |

### Canonical Receipt Shape

```json
{
  "aaa_surface": "AAA-HF",
  "aaa_doctrine_version": "v1.2",
  "aaa_canon_refs": ["aaa-0000"],
  "floor_refs": ["F1", "F3", "F12"],
  "verdict": "888_HOLD",
  "record_class": "constitutional_receipt"
}
```

### Migration

Applied via: `supabase/migrations/20260602000000_aaa_namespace_receipt_fields.sql`

Full schema reference: `docs/architecture/CONSTITUTIONAL_RECEIPT_SCHEMA.md`

---

*DITEMPA BUKAN DIBERI — Intelligence is forged, not given.*
