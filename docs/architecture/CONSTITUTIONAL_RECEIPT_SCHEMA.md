# Constitutional Receipt Schema
**Authority:** AAA-HF v1.2, AAA_NAMESPACE_DOCTRINE.md  
**Version:** 1.0  
**Date:** 2026-06-02  
**Status:** RATIFIED  
**Migration:** `20260602000000_aaa_namespace_receipt_fields.sql`

---

## The Problem This Solves

Before this schema, a Supabase record said:
> "This happened, with verdict X."

After this schema, a Supabase record says:
> "This happened, under **version v1.2 of the AAA-HF doctrine**, citing floor F1 and F12, governed by the constitutional receipt class — not just a log row."

The key insight:

| Old field | Problem | Replacement |
|-----------|---------|-------------|
| `aaa_version` | Ambiguous — which AAA? App version? Dataset version? | `aaa_surface` + `aaa_doctrine_version` |
| `floor_triggered` | Single floor only | `floor_refs TEXT[]` (multi-floor) |
| *(none)* | No record type semantics | `record_class` |

---

## The 5 New Fields

These fields appear on `arifosmcp_tool_calls`, `arifosmcp_vault_seals`, `arifosmcp_approval_tickets`, and `arifosmcp_canon_records`.

### `aaa_surface TEXT DEFAULT 'AAA-HF'`

Which surface of AAA defined the law for this record.

| Value | Meaning | When to use |
|-------|---------|-------------|
| `AAA-HF` | HuggingFace doctrine corpus | Default — all constitutional records |
| `AAA-Cockpit` | GitHub AAA control plane | Records about cockpit state, A2A routing |
| `AAA-Doctrine` | Abstract constitutional meaning | Doctrine-level ADRs |
| `AAA-Interface` | Operator visibility surface | Cockpit UI interaction records |
| `AAA-Eval` | Benchmark/evaluation harness | Eval run results, gold record comparisons |

**Default is `AAA-HF`** because the doctrine corpus defines what a constitutional receipt is. This is almost always the right value.

### `aaa_doctrine_version TEXT`

Version of the AAA-HF corpus in effect when the record was written. Format: `vMAJOR.MINOR`.

```
aaa_doctrine_version = 'v1.2'
```

This is analogous to a law book edition. If the doctrine evolves (new floors, updated verdicts), records created before and after the change can be distinguished.

### `aaa_canon_refs TEXT[]`

Array of canonical references from the AAA-HF corpus that apply to this record.

```sql
aaa_canon_refs = ARRAY['aaa-0000', 'aaa-0042']
```

`aaa-0000` is the genesis record. Others reference specific floor definitions, verdict schemas, or evaluation records in the HF dataset.

### `floor_refs TEXT[]`

Array of constitutional floors that were triggered, checked, or relevant to this record.

```sql
floor_refs = ARRAY['F1', 'F3', 'F12']
```

Replaces the single `floor_triggered TEXT` column for records that touch multiple floors simultaneously. The `floor_triggered` column is retained for backward compatibility.

### `record_class TEXT DEFAULT 'constitutional_receipt'`

Semantic class of the record. Not a record type (table name tells you that). A semantic meaning.

| Value | Used on | Meaning |
|-------|---------|---------|
| `constitutional_receipt` | `tool_calls`, `vault_seals` | Governed MCP execution record |
| `approval_receipt` | `approval_tickets` | 888_HOLD queue entry |
| `canon_receipt` | `canon_records` | ADR, floor rule, doctrine change |
| `audit_trail` | `tool_calls` | Low-risk telemetry, not a constitutional event |
| `evidence_record` | `tool_calls` | Evidence fetch, sense/observe result |
| `telemetry` | `tool_calls` | Performance metric, health check |

---

## Canonical Receipt JSON Shape

The expected JSON payload for a fully-formed constitutional receipt:

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

Extended form (with all context):

```json
{
  "aaa_surface": "AAA-HF",
  "aaa_doctrine_version": "v1.2",
  "aaa_canon_refs": ["aaa-0000", "aaa-0042"],
  "floor_refs": ["F1", "F3", "F12"],
  "verdict": "888_HOLD",
  "record_class": "constitutional_receipt",

  "tool_name": "arif_forge_execute",
  "organ": "A-FORGE",
  "session_id": "sess-abc123",
  "agent_id": "hermes-asi",
  "risk_tier": 3,
  "duration_ms": 142,
  "evidence_refs": ["vault-event-abc"],
  "approval_ticket_id": "ticket-xyz",
  "epoch": "2026-06-02T12:00:00+08:00"
}
```

---

## Why Not `aaa_version`?

The bare field name `aaa_version` is now explicitly banned in new schemas. Reason: after the AAA Namespace Doctrine, "AAA" is polymorphic. A reader cannot tell if `aaa_version: "2.1.0"` means:

- The AAA-HF dataset version (doctrine corpus version)?
- The AAA-Cockpit app version (GitHub release)?
- The AAA-Eval harness version?

The correct replacement is always the pair:
```
aaa_surface = "AAA-HF"           -- which surface
aaa_doctrine_version = "v1.2"   -- which version of that surface
```

---

## Invariant Chain (from AAA_NAMESPACE_DOCTRINE.md)

```
AAA-HF defines doctrine (aaa_surface = 'AAA-HF', aaa_doctrine_version = 'v1.2')
  → arifOS applies doctrine (floor_refs = ['F1', 'F12'])
  → MCP tools execute
  → Supabase records (record_class = 'constitutional_receipt')
  → VAULT999 seals
  → AAA-Cockpit displays (aaa_surface = 'AAA-Cockpit' for display metadata)
  → Arif decides
```

---

## Validation Constraints

The `aaa_surface` column has a database-level CHECK constraint:

```sql
CHECK (aaa_surface IN ('AAA-HF', 'AAA-Cockpit', 'AAA-Doctrine', 'AAA-Interface', 'AAA-Eval'))
```

No other string values are permitted. This prevents ambiguous or invented surface names from entering the ledger.

---

## Related Files

| File | Role |
|------|------|
| `supabase/migrations/20260602000000_aaa_namespace_receipt_fields.sql` | Migration that adds the 5 new columns |
| `docs/architecture/AAA_NAMESPACE_DOCTRINE.md` | Master AAA surface definitions |
| `docs/architecture/AAA_SUPABASE_RECORD_DOCTRINE.md` | Full record type jurisdiction and floor → table mapping |
| `scripts/aaa_unified_views.sql` | Unified read views for AAA-Cockpit |

---

*DITEMPA BUKAN DIBERI — Intelligence is forged, not given.*
