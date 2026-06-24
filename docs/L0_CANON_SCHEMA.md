# L0 Canon Schema — Bi-Temporal Memory Substrate

> **Scope:** `arifosmcp/data/memory/l0/`
> **Authority:** F13 SOVEREIGN
> **Epistemic class:** SOVEREIGN_TESTIMONY
> **Forged:** 2026-06-24

## Purpose

L0 Canon is the judge's bench of arifOS memory: policy, persona, sealed rules, and sovereign testimony. It is immutable except by F13 seal. Every L0 record carries bi-temporal metadata so the federation can answer:

> "What was true at time *t*?"

## Required fields (frontmatter or code-equivalent)

| Field | Type | Meaning |
|-------|------|---------|
| `id` | string | Stable identifier (e.g., `arif_human_substrate`, `F13-PRE-TRUST-2026-06-16`) |
| `type` | string | `canon` | `policy` | `persona` | `framework` | `scar` |
| `title` | string | Human-readable title |
| `description` | string | One-paragraph relevance hint (frontmatter-first principle) |
| `valid_from` | ISO-8601 | When this fact/version became canon |
| `superseded_at` | ISO-8601 \| null | When this version was replaced (not deleted) |
| `superseded_by` | string \| null | `id` of the version that replaced this one |
| `authority` | string | `F1` \| `F2` \| `F13` \| `AMANAH` |
| `scope.agent_id` | string | Owning identity (e.g., `arif_sovereign`) |
| `scope.visibility` | string | `federation` \| `organ` \| `private` |
| `created_at` | ISO-8601 | When this file/record was physically authored |
| `hash_prev` | string | SHA-256 of the previous version (chain attestation) |
| `tags` | list | Taxonomy tags |
| `links` | list | `[[wikilink]]` references to other L0 records |

## Operational rules

1. **Append-only versioning.** When a fact changes, do not edit the old record in place. Create a new record, set `valid_from` on the new one, and update the old record's `superseded_at` + `superseded_by`.
2. **No deletion.** Superseded records remain in L0 for temporal queries and audit.
3. **F13 gate.** Promotion to L0 requires `arif_judge` SEAL or F13 sovereign signature.
4. **Scope first.** Retrieval must filter by `scope.agent_id` and `scope.visibility` before LLM sees candidates.

## Current L0 records

| ID | File | valid_from | superseded_at |
|----|------|------------|---------------|
| `arif_human_substrate` | `arif_human_reality.md` | 2026-06-16T18:56:00+08:00 | null |
| `F13-PRE-TRUST-2026-06-16` | embedded in `substrate_loader.py` | 2026-06-16 | null |

## Migration note

The existing `arif_human_reality.md` predates this schema. Bi-temporal metadata is injected by `substrate_loader.py` at read time (`valid_from = SUBSTRATE_FORGED_AT`). Future L0 files should include YAML frontmatter directly and pass the pre-commit validator.

## `fact_at(entity, predicate, t)` primitive

```python
def fact_at(entity: str, predicate: str, t: datetime) -> dict | None:
    """Return the L0 record that was valid for (entity, predicate) at time t."""
    for record in L0_canon_records:
        if record["entity"] == entity and record["predicate"] == predicate:
            valid_from = parse_iso(record["valid_from"])
            superseded_at = parse_iso(record["superseded_at"]) if record["superseded_at"] else None
            if valid_from <= t and (superseded_at is None or superseded_at > t):
                return record
    return None
```

DITEMPA BUKAN DIBERI.
