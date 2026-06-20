# ADR: WELL Persistence — Local-Only Model

**Status:** RATIFIED
**Date:** 2026-06-21
**Architect:** Arif Fazil
**Decision Driver:** FED-SUPABASE-ALIGN-20260621-001 Phase 1

## Context

WELL (Ω) is the human readiness organ of the arifOS federation. It tracks biometric signals — sleep, fatigue, metabolic flux, dignity preservation, sovereign entropy. Currently it persists to two local files:
- `/root/WELL/state.json` — current sovereign state
- `/root/WELL/events.jsonl` — append-only event log

The Supabase alignment review (FED-SUPABASE-ALIGN-20260621-001) identified WELL as having no `supabase-py` dependency. This ADR decides whether to add one.

## Decision

**WELL remains local-only. No `supabase-py` dependency. No cloud persistence.**

### Rationale

1. **Biometric sensitivity (F6 MARUAH):** Sleep, fatigue, and metabolic flux data are personal. Storing them in a cloud-managed Postgres (even Supabase) introduces an unnecessary attack surface. Local disk, chmod 600, is the minimum viable boundary.

2. **Isolation boundary (REFLECT_ONLY):** WELL is constitutionally `REFLECT_ONLY` — it observes and signals, never decides. Adding a network dependency for persistence pushes it toward cross-machine state, which blurs its constitutional isolation. Local files enforce the boundary.

3. **Ephemerality by design:** Biometric states older than 30 days are compressible to trends, not retained as point-in-time records. Local file rotation (logrotate or simple cron) keeps this natural. A cloud DB incentivizes hoarding — exactly what F4 CLARITY forbids.

4. **Simplicity:** 2 files, no connection pool, no migration, no vector index, no secrets management for a cloud endpoint. If migration is ever needed, it's `cp` + `scp`, not a schema migration with rollback plan.

### What We Lose

- Cross-machine WELL state (e.g., querying WELL data from AAA cockpit via Supabase directly)
- Agent persistence through VPS reboot (state.json survives local disk anyway)

Neither is worth the constitutional trade-off.

### What This Means for Federation

- WELL remains the only organ without `supabase-py` — documented, intentional, not a gap
- AAA cockpit that wants WELL data must go through WELL's MCP surface (port 18083), not Supabase directly
- VAULT999 seals from WELL events are still mirrored if `vault_mirror` table is created (via MCP call, not direct DB)

## Consequences

### Positive
- No cloud vector for biometric data
- Clear constitutional boundary preserved
- Zero migration debt
- No connection pool to manage
- Easy backup (single directory)

### Negative
- WELL state is not queryable from Supabase dashboard
- Cross-agent WELL queries require MCP round-trip (acceptable — this is the governed path)

## Implementation

- [x] Decision made (this ADR)
- [ ] Document in WELL AGENTS.md: "WELL persists to local files only — no Supabase"
- [ ] No code changes required (current implementation is already correct)

---

*DITEMPA BUKAN DIBERI — 999 SEAL ALIVE*
