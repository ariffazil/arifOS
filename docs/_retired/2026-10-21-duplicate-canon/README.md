# RETIRED 2026-10-21 — duplicate canon mirror (DO NOT RESURRECT)

## What was here
Three trees inside `static/arifos/` that were byte-identical duplicates of canon
that already lives at the canonical path:

| Retired path | Canonical path (kept, live) |
|---|---|
| `static/arifos/docs/KERNEL/FLOORS/*` | `static/arifos/theory/000/*` |
| `static/arifos/kernel/K*.md` | `static/arifos/theory/000/*` |
| `static/arifos/floors/F*.md` | `static/arifos/theory/000/*` |

64 files, 720 KB.

## Why retired
Only `static/arifos/theory/000/` is read by live code:
`arifosmcp/runtime/organ_attestation.py:139-144` loads
`static/arifos/theory/000/000_CONSTITUTION.md` at runtime.
`scripts/reachability_analysis.py:259` pins `.../theory/000/CANONICAL_SPEC.yaml`.

The other three had **zero** consumers: no Python import, no CI workflow, no
script, no HTML reference. The only references anywhere in the repo were inside
`.ua/intermediate/batches.json` (a tool cache, not a consumer).

## Why this was a real defect, not just clutter
Three byte-identical copies of constitutional canon is three places to edit.
An agent updating floor text would update one copy, the other two would go
stale, and nothing would fail loudly — the live reader only reads the fourth
path. That is a silent divergence trap.

## If you need this content
Read `static/arifos/theory/000/`. Do not copy it back out.
