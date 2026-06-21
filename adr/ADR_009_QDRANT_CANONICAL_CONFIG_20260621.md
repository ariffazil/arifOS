<!-- SOT-MANIFEST
adr_id:          ADR-009
title:           Qdrant canonical configuration for arifOS collection
status:          DRAFT (Cycle A — pre-F13 ratification)
owner:           arifOS kernel (F13 SOVEREIGN)
forged_by:       Hermes, 2026-06-21
linked_audit:    Hermes audit 2026-06-21 (memory architecture critique)
constitution:    SOUL.md §7.9, §7.11 (I6, I11)
supersedes:      none
reversible:      yes (draft status — no canonical mutation yet)
-->

# ADR-009 — Qdrant canonical configuration for arifOS collection

## Status

**DRAFT** — Cycle A of Remediation Plan 2026-06-21-002.
Requires **888_JUDGE review + F13 ratification** before promotion to RATIFIED.

## Context

Qdrant collection `arifos_memory` is operational but its canonical configuration
(collection name, dimensions, distance metric, retention policy, governance band)
is not sealed anywhere in doctrine. A new agent spinning up Qdrant from
constitution-only sources has no reference.

Hermes audit 2026-06-21 (item 12) named this as a gap: "Vector store is operational,
not constitutional."

## Decision

The canonical Qdrant configuration for arifOS is:

| Parameter | Value | Rationale |
|---|---|---|
| **Host** | `127.0.0.1:6333` | ADR-001 localhost-is-password doctrine |
| **Collection** | `arifos_memory` | Stable, matches runtime |
| **Vector dim** | `1024` | bge-m3 default embedding dimension |
| **Distance** | `Cosine` | Standard for semantic recall |
| **Write authority** | `KSR` (kernel-mediated only) | SOUL.md §7.9, §7.11 I2 |
| **Recall authority** | `ADVISORY_ONLY` | ADR-008 |
| **Retention** | Append-only, decay-managed | Federation memory lane |
| **TTL** | none (decay by contradiction log + revocation manager) | See `arifosmcp/memory/revocation_manager.py` |
| **Provenance tag (write)** | REQUIRED — `authority_source: KSR` | Closes write-side membrane gap (audit item 13) |
| **Provenance tag (read)** | REQUIRED — `memory_context_source: memory_recall` | Already enforced |

## Write Discipline (NEW)

Every write to `arifos_memory` collection MUST carry:

```json
{
  "authority_source": "KSR",
  "current_state_source": "kernel_attest | fresh_KSR | verified_state_resume",
  "checkpoint_type": "KSR_SNAPSHOT",
  "actor_signature": "<ed25519>",
  "issued_at": "<RFC3339>",
  "provenance_anchor": "<event_hash from Vault>"
}
```

Writes lacking any of these fields are rejected at the kernel layer.

This closes the **write-side membrane gap** named in Hermes audit item 13
("Read-side gated, write-side not gated").

## Recall Discipline

Every recall MUST:

1. Return `authority_claim: ADVISORY_ONLY`
2. Return no verdict-shaped objects (no `active_verdict`, no `holds`, no
   `mutation_allowed` flag)
3. Carry `memory_context_source: memory_recall` provenance tag

This is already runtime-enforced. ADR-009 only canonicalizes the requirement.

## Consequences

### Positive

- Canonical config prevents drift across re-deployments.
- Write-side gate closes the asymmetry between read enforcement and write enforcement.
- Provenance tags enable Vault ↔ Qdrant traceability.

### Negative

- New write-side gate adds latency (kernel must sign before Qdrant write).
- Performance: ~2-5ms overhead per write (negligible for advisory storage).
- Operational burden: every Qdrant client must be updated to send provenance.

### Migration

- Existing 1,754 SEALED_EVENTS_v2 entries in Vault → batched T1 promotion
  (see Cycle B — outcomes.jsonl promotion artifact).
- Existing Qdrant entries (count unknown, requires live probe) → if they
  lack provenance tags, classify as `judgment_class: batch_legacy_888_ratified`
  retroactively per SOUL.md §7.9.9 grandfather rule.

## Enforcement

- Runtime: `arifosmcp/memory/vector_memory_qdrant.py` gains write-gate function
  (to be added in Cycle B)
- Test: `tests/abis/test_qdrant_write_gate.py` — verify rejected writes
  lack required fields
- Test: `tests/abis/test_cross_organ_probe.py` — already passing, no change

## Constitutional Anchors

- **F2 (TRUTH):** Configuration matches live state.
- **F11 (AUTH):** Provenance tag required on every write.
- **§7.9 invariant 6:** Read-side advisory contract.
- **§7.11 I6:** Federation memory is advisory only.
- **§7.11 I8:** ZKPC level must be declared honestly (applies if Qdrant
  is later promoted to ZKPC evidence layer).

## Ratification Path

1. ✅ Draft (this document) — Cycle A
2. ⏳ 888_JUDGE review
3. ⏳ F13 SOVEREIGN ratification
4. ⏳ Promote to RATIFIED
5. ⏳ Implement write-gate in `vector_memory_qdrant.py` (Cycle B)
6. ⏳ Add `tests/abis/test_qdrant_write_gate.py` (Cycle B)

## Links

- Hermes memory architecture critique, 2026-06-21, item 12 + 13
- ADR-008 — Qdrant advisory-only role
- SOUL.md §7.9 — Federation memory lane
- `arifosmcp/memory/vector_memory_qdrant.py` — runtime implementation
- `arifosmcp/memory/revocation_manager.py` — decay discipline
- ADR-001 — Localhost-as-authentication doctrine

---

**DITEMPA BUKAN DIBERI — Configuration forged, not improvised.**