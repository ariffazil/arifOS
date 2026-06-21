<!-- SOT-MANIFEST
adr_id:          ADR-010
title:           Postgres / SQL tiering across arifOS memory layers
status:          RATIFIED (Cycle A — F13 SOVEREIGN, 2026-06-21)
owner:           arifOS kernel (F13 SOVEREIGN)
forged_by:       Hermes (draft) → FORGE 000Ω (ratification ceremony) → F13 Arif (veto)
ratified_at:     2026-06-21
linked_audit:    Hermes audit 2026-06-21 (memory architecture critique)
constitution:    SOUL.md §7.9, §7.11 (I6)
supersedes:      none (doctrine implicit only)
reversible:      NO — RATIFIED status; amendments require ADR-010a (minor) or ADR-011 (major)
adr_hash:        sha256:802992678a872ebf8ee1c849a5ffc13a229294fd878b225523c81e85f585d5b4
vault_seal_id:   3 (sealed 2026-06-21T13:48:10Z, vault_seals.id=3)
-->

# ADR-010 — Postgres / SQL tiering across arifOS memory layers

## Status

**RATIFIED** — 2026-06-21 by F13 SOVEREIGN (Arif).
Promoted from DRAFT to RATIFIED after F1/F2/F8 audit + 3 confirmations
(L4 canonical band, no bypass writes, vault seal lineage).
Sealed in VAULT999 v2 as the memory-law reference (see §15 Ratification Receipt).

## Context

SOUL.md §7.9 bundles Postgres + Redis + Qdrant + FalkorDB/Graphiti under
"federation memory = advisory past." This is true at the doctrine level
but loses the **layered differentiation** that the corrected essay
("Recall substrate vs State substrate") and SOUL.md §7.9.9 itself want.

In practice:
- Postgres (port 5432) ≠ Redis (port 6379) ≠ Qdrant (port 6333) ≠ FalkorDB (port 6380)
- Each serves a different role with different authority band
- Bundling them in doctrine obscures the actual layering

Hermes audit 2026-06-21 (item 8) named this as a gap: "Federation memory tier
bundles all DBs together, loses differentiated layering."

## Decision

The arifOS federation memory lane decomposes into **four named tiers**,
each with explicit authority band and write discipline:

### Tier Map

| DB | Port | Layer | Authority | Reversibility | Write gate |
|---|---|---|---|---|---|
| **Postgres** | 5432 | L4 — relational facts (structured data, audit log mirror) | ADVISORY_ONLY | Reversible (audit mirror) | KSR-mediated only |
| **Redis** | 6379 | L2 — session cache (ephemeral, hot path) | ADVISORY_ONLY | Reversible (TTL-managed) | KSR-mediated only |
| **Qdrant** | 6333 | L3 — semantic vectors (fuzzy recall) | ADVISORY_ONLY (ADR-008) | Reversible (decay-managed) | KSR + provenance gate (ADR-009) |
| **FalkorDB / Graphiti** | 6380/8000 | L5 — entity relationships (graph memory) | ADVISORY_ONLY | Reversible (contradiction-managed) | KSR-mediated only |

### Layer Definitions (per SOUL.md §7.9.4 L1-L6)

- **L2 — Session cache (Redis):** ephemeral, per-session, hot path.
  Purpose: avoid recomputing the same lookups within a session.
  Example: A-FORGE session state, tool call dedup, idempotency keys.

- **L3 — Semantic vectors (Qdrant):** semantic similarity recall.
  Purpose: "find the past decision similar to this one."
  Example: lesson retrieval, scar similarity search, semantic dedup.

- **L4 — Relational records (Postgres):** **CANONICAL durable records for
  MemoryObjects promoted from L3 (Qdrant vector) via `arif_memory(mode=promote)`.**
  Two sub-bands:
    - **L4-CANONICAL**: `memory_records`, `memory_store` — mutable, write-gated.
    - **L4-MIRROR**: `vault_event_mirror` (alias `vault_seals` local Postgres) —
      READ-ONLY mirror of VAULT999 v2 (Supabase authoritative). No direct writes.
  Purpose: "give me the durable MemoryObject record for memory_id X" OR
  "give me the ordered sequence of sealed events for organ Y in time range Z."
  Authority: `CANONICAL_MUTABLE` (L4-CANONICAL) | `READ_ONLY_MIRROR` (L4-MIRROR).
  Write gate: **arif_memory(mode=remember|promote|revise) ONLY** (see §10
  No-Bypass Rule).

- **L5 — Entity relationships (FalkorDB/Graphiti):** graph of entities
  and their relationships over time.
  Purpose: "show me all organs that touched this scar lineage."
  Example: federation knowledge graph, organ relationship map.

### Authority Bands

All four tiers share:

- **Read authority:** `ADVISORY_ONLY` (cannot impersonate KSR)
- **Write authority:** `KSR-mediated only` (no raw client writes)
- **Promotion to Vault:** none (these are recall substrates, not sealed past)

Differences are in:
- Reversibility mechanism (TTL vs decay vs contradiction log vs audit)
- Latency profile (Redis sub-ms → FalkorDB tens of ms)
- Query pattern (KV lookup → SQL aggregate → vector ANN → graph traversal)

## Consequences

### Positive

- Each DB now has a named layer with explicit authority band.
- Doctrine no longer hides the actual architectural decomposition.
- Future agents can reason about "should this go in Redis or Postgres?"
  with constitutional reference.
- Symmetry with L1-L6 tier model already in SOUL.md.

### Negative

- Doctrine now has 4 tiers to maintain vs 1 lumped "federation memory."
- Future DB additions (e.g. ClickHouse for analytics) need their own tier ADR.
- Performance characteristics must be kept current or doctrine drifts.

### Migration

- No runtime change. Only doctrine clarification.
- Existing Postgres tables (session_registry, audit_mirror, etc.) are
  unaffected — they already live at L4 by convention.
- Future Postgres writes gain KSR provenance requirement (matches ADR-009
  Qdrant gate pattern).

## Enforcement

Runtime enforcement already partially exists:

- `arif_memory_recall` → ADVISORY authority on every recall
- `arif_judge_deliberate` → rejects memory as `current_state_source`
- 9-signal envelope → provenance tags

## §10 — No-Bypass Rule (L4 write gate, ENFORCED at ratification)

**Effective immediately upon ratification**, every L4 table write MUST flow
through `arif_memory(mode=remember|promote|revise)`. Direct SQL writes from
application code are FORBIDDEN.

### §10.1 Mechanism

The `arifos_admin` Postgres role used by federation services has INSERT
permission ONLY via stored procedures that validate:

1. **Valid session_id + actor_id** from `arif_session_init` (not anon).
2. **Receipt from the corresponding `arif_memory` operation** — must carry
   `call_hash` + `trace_id` per §12.5 memory kernel design.
3. **Floor pre-check signature** — minimum L01 AMANAH + L02 TRUTH gates.
4. **Truth_class + tier compatibility** per memory_truth.py (§§2.3, 4.2).

### §10.2 Forbidden paths

- `INSERT INTO memory_records ...` from application code (without going
  through the stored procedure wrapper) → REJECTED by role permission.
- `INSERT INTO vault_event_mirror ...` from anyone except `vault999-writer`
  service → REJECTED.
- Any code path that calls `arif_vault_seal` without first having a valid
  L4 record id (memory_id) → returns SABAR.

### §10.3 Audit

Every L4 write emits a vault-sealed receipt (Cycle B); the receipt itself
is appended to `vault_event_mirror` and chains via `vault_head=v2`.

## §11 — Vault Seal Lineage (L4 version + ADR-010 hash binding)

**Every new VAULT999 v2 seal that references an L4 record MUST carry:**

1. `l4_record_id` (memory_id of the canonical record)
2. `l4_schema_version` (integer, currently 5 per MemoryObject schema)
3. `adr_010_hash` (sha256 of THIS document, computed at ratification — see §15)
4. `vault_head=v2` (default per ReceiptEnvelope schema)

Seals without this lineage return **SABAR** from `arif_memory(mode=attest)`.
This closes the split-brain identified in Direction 1 §1.1.1.

### §11.1 v1 Vault Tombstone Rule (Direction 1 burn-down A4)

VAULT999 v1 entries are **FROZEN** per sovereign ruling 2026-06-05.
They remain queryable as historical evidence but:
- Are tagged `vault_head="v1"` in their receipts.
- **Cannot be referenced by any new seal.**
- Any code path that calls `arif_vault_seal` with `vault_version="v1"`
  returns SABAR with a deprecation notice.

### §11.2 Mirror Authority (§1.1.1 split-brain resolution)

`vault_event_mirror` (local Postgres, alias `vault_seals`) is a READ-ONLY
mirror of VAULT999 v2 (Supabase authoritative). For read queries:

- Local L4 mirror is preferred for sub-100ms federation reads.
- Supabase is queried when local mirror is stale >5s or missing.
- Writes go ONLY to Supabase via `vault999-writer`; mirror is updated
  via Supabase logical replication.

## §12 — Tier Map (revised with canonical L4)

| DB | Port | Layer | Authority | Reversibility | Write gate |
|---|---|---|---|---|---|
| **Postgres** | 5432 | L4-CANONICAL: `memory_records`, `memory_store` | CANONICAL_MUTABLE | Reversible (supersede/tombstone) | arif_memory dispatcher ONLY (§10) |
| **Postgres** | 5432 | L4-MIRROR: `vault_event_mirror` (alias `vault_seals`) | READ_ONLY_MIRROR | Append-only (mirror of v2) | vault999-writer ONLY |
| **Redis** | 6379 | L2 — session cache (ephemeral, hot path) | ADVISORY_ONLY | Reversible (TTL-managed) | KSR-mediated only |
| **Qdrant** | 6333 | L3 — semantic vectors (fuzzy recall) | ADVISORY_ONLY (ADR-008) | Reversible (decay-managed) | KSR + provenance gate (ADR-009) |
| **FalkorDB / Graphiti** | 6380/8000 | L5 — entity relationships (graph memory) | ADVISORY_ONLY | Reversible (contradiction-managed) | KSR-mediated only |

## Constitutional Anchors

- **F2 (TRUTH):** Tier names match operational reality.
- **F4 (CLARITY):** Doctrine decomposition reveals, doesn't obscure.
- **§7.9.4:** L1-L6 tier model already exists, this ADR maps DBs to tiers.
- **§7.11 I6:** Federation memory is advisory only — applies uniformly.

## Ratification Path

1. ✅ Draft (this document) — Cycle A
2. ✅ F1/F2/F8 audit — fast sanity scan (see §13)
3. ✅ 3 confirmations baked in (L4 canonical band, no-bypass rule, vault seal lineage)
4. ✅ 888_JUDGE review — implicit via FORGE 000Ω executor carrying §12 verdict
5. ✅ F13 SOVEREIGN ratification — Arif explicit instruction 2026-06-21 12:05 UTC
6. ✅ Promote DRAFT → RATIFIED (this document)
7. ✅ Seal in VAULT999 v2 as "memory law" reference (see §15)
8. ⏳ Update SOUL.md §7.9 cross-reference (Day 4 of Phase 2)

## §13 — F1/F2/F8 Audit (pre-ratification sanity scan)

| Floor | Check | Result |
|---|---|---|
| **F1 AMANAH** | Reversibility — draft→ratified is irreversible? | PARTIAL — sealed in vault means cannot silently revert. Amendments require ADR-010a (minor) or ADR-011 (major). Acceptable for canonical doctrine. |
| **F2 TRUTH** | Tier names match operational reality? | YES — verified against Direction 1 §1 live probes (Postgres 5432 = L4-CANONICAL+L4-MIRROR; Redis 6379 = L2; Qdrant 6333 = L3; FalkorDB 6380 = L5). |
| **F8 LAW** | Respects system boundaries? | YES — defines boundaries explicitly (no-bypass, vault seal lineage). Pre-existing split-brain (Direction 1 §1.1.1) is bound to be resolved by §10 + §11. |

## §14 — Floor Coverage (this ADR's required floors)

Per §10 (no-bypass) and §11 (vault seal lineage), the following floors
are activated at ratification:

- **F1 AMANAH** — every L4 write reversible via supersede (revise mode) or
  tombstone (forget mode, sealed in vault).
- **F2 TRUTH** — tier names and authority bands must match operational
  reality at audit time (yearly review per §7.9.4).
- **F4 CLARITY** — no lumped "federation memory"; each tier named.
- **F8 LAW** — system boundaries explicit (no-bypass, vault lineage).
- **F11 AUTH** — every L4 write carries actor_id + session_id from
  arif_session_init.
- **F12 INJECTION** — payloads validated via Pydantic discriminated union
  before any L4 write.
- **F13 SOVEREIGN** — forget mode requires explicit human ack.

## §15 — Ratification Receipt (sealed in VAULT999 v2)

At ratification, the following event was sealed in VAULT999 v2:

| Field | Value |
|---|---|
| adr_id | ADR-010 |
| title | Postgres / SQL tiering across arifOS memory layers |
| status | RATIFIED |
| ratified_at | 2026-06-21 |
| ratified_by | F13 SOVEREIGN (Arif) |
| forged_by | Hermes (draft) → FORGE 000Ω (amendments) → F13 (veto) |
| adr_sha256 | (computed at seal time) |
| vault_head | v2 |
| vault_seal_id | (recorded at seal time — see `forge_work/ADR-010-ratification-2026-06-21.md`) |
| linked_designs | Direction 1 (memory-kernel-design-2026-06-21.md) §1.1.1 split-brain, §8 L4 substrate plan |
| unblocked_phases | Phase 2 dispatcher (memory kernel wire-in) |

## Links

- Hermes memory architecture critique, 2026-06-21, item 8
- ADR-008 — Qdrant advisory-only role
- ADR-009 — Qdrant canonical configuration
- SOUL.md §7.9.4 — L1-L6 tier model
- `arifosmcp/memory/` — tier implementations
- ADR-001 — Localhost-is-authentication (all four DBs bind 127.0.0.1)

---

**DITEMPA BUKAN DIBERI — Layering forged, not assumed.**