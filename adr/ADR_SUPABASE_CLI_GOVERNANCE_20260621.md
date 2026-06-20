# ADR: Supabase CLI Governance — Irreversible Mutation Discipline

**Status:** RATIFIED
**Date:** 2026-06-21
**Architect:** Arif Fazil
**Decision Driver:** FED-SUPABASE-ALIGN-20260621-001 Phase 4

## Context

Supabase CLI (`supabase db push`, `db pull`, migrations, secrets management) can mutate the production database schema, apply RLS changes, rotate secrets, and alter connected project configuration. These operations affect all federation organs that depend on Supabase for persistence.

Before this ADR, CLI invocation had no formal lease requirement. Any agent or operator with CLI access could push schema changes without constitutional gate.

## Decision

**All Supabase CLI destructive mutations require an active 888_HOLD lease + F13 approval before execution.**

### The Rule

| Operation | Classification | Gate Required |
|-----------|---------------|---------------|
| `supabase db push` | IRREVERSIBLE STRUCTURAL | 888_HOLD + F13 approval |
| `supabase db diff --apply` | IRREVERSIBLE STRUCTURAL | 888_HOLD + F13 approval |
| `supabase secrets set` | DESTRUCTIVE (secret rotation) | 888_HOLD + F13 approval |
| `supabase secrets delete` | DESTRUCTIVE | 888_HOLD + F13 approval |
| `supabase projects create` | DESTRUCTIVE (billing) | 888_HOLD + F13 approval |
| `supabase projects delete` | IRREVERSIBLE (data loss) | 888_HOLD + F13 approval |
| `supabase db pull` | READ-ONLY (local diff only) | None (exempt) |
| `supabase db diff` (no apply) | READ-ONLY | None (exempt) |
| `supabase db dump` | READ-ONLY | None (exempt) |
| `supabase db query` (SELECT only) | READ-ONLY | None (exempt) |

### Lease Protocol

1. Operator opens 888_HOLD with: `intent`, `table_names`, `sql_hash` (SHA-256 of commands)
2. 888_JUDGE reviews against F1–F13
3. F13 (Arif) explicitly approves or rejects
4. Lease issued — operator executes
5. Post-execution **PAIReceipt** emitted (see `arifos/arifosmcp/schemas/pai_receipt.py` — canonical federation envelope, ratified 2026-06-06): `evidence.input_hash`, `evidence.payload_hash`, `verdict`, `producer.identity`, `authority.tier`
6. PAIReceipt sealed to VAULT999 + mirrored to Supabase `receipts` table
7. Lease closed

### What Constitutes a Violation

- CLI mutation executed without active 888_HOLD lease
- CLI mutation by non-F13 actor without explicit delegation
- PAIReceipt not emitted within 5 minutes of completion
- SQL applied without prior review (SQL must be shown to F13 before `db push`)

## Consequences

### Positive
- No accidental schema drift
- Clear audit trail for every Supabase schema change
- RLS policy changes are gated (constitutional integrity)
- Secret rotation events are traceable

### Negative
- Adds latency to schema changes (waiting for F13 review)
- Requires F13 availability for urgent production fixes
- F13 is the bottleneck — but that's the point

## Exceptions

- Emergency production fix requiring immediate `db push` can be executed with verbal F13 approval, but receipt must be filed within 1 hour
- `supabase db pull` is always free (read-only, creates local SQL diff)

---

*DITEMPA BUKAN DIBERI — 999 SEAL ALIVE*
