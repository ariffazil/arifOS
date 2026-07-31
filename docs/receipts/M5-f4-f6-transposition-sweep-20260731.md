# RECEIPT — M5 F4/F6 Transposition Sweep · 2026-07-31

> **M5 of Kernel Hardening Sprint** — T1, fix wrong F4/F6 pairings across 11 static/ docs files.

## WHAT WAS BROKEN

The audit confirmed 7 files (plus the duplicate-tree variants: 11 total) had
`F4 (Empathy)` paired with `ΔS entropy reduction` description, and `F6 (Clarity)`
paired with `κ_r stakeholder alignment` description — labels and descriptions
were both transposed relative to canon.

The CANON (per constitutional_map.py header) is:
- **F4 = Clarity** → ΔS entropy reduction
- **F6 = Empathy** → κ_r stakeholder alignment

The docs had it backwards in two ways: the labels AND the descriptions were
both transposed. So the right fix is to swap BOTH labels and descriptions,
ending up with each floor paired with its correct concept.

## WHAT CHANGED

3 distinct patterns of wrong pairings, all swapped correctly:

| Original (wrong) | After (correct) |
|---|---|
| `\| F4 (Empathy) \| κ_r stakeholder alignment \|` | `\| F4 (Clarity) \| ΔS entropy reduction \|` |
| `\| F6 (Clarity) \| ΔS entropy reduction \|` | `\| F6 (Empathy) \| κ_r stakeholder alignment \|` |
| `F4 Empathy, universal access` (Philanthropists row) | `F6 Empathy, universal access` |
| `F4 Empathy check: ...` (K333_CODE) | `F6 Empathy check: ...` |
| `**F6 (Clarity)** — This document reduces entropy` | `**F4 (Clarity)** — This document reduces entropy` |
| `### Visual Principles (F6 Clarity)` | `### Visual Principles (F4 Clarity)` |
| `- **F6 Clarity:** Composition preserves information` | `- **F4 Clarity:** Composition preserves information` |

## ACCEPTANCE — measured at fix time

| Gate | Before | After |
|---|---|---|
| `grep "F4 Empathy\|F6 Clarity" static/ docs/` | 3 hits | **0** |
| `grep "F4 (Empathy)\|F6 (Clarity)" static/ docs/` | 9 hits | **0** |
| `grep "F4 (Clarity) \| ΔS entropy reduction" static/ docs/` | 0 hits | **3** (correct pairings restored) |
| `grep "F6 (Empathy) \| κ_r stakeholder alignment" static/ docs/` | 0 hits | **3** |

## FILES CHANGED (11 total, 17 line swaps)

- docs/core/VISUAL_SCHEMA.md (1 swap)
- static/arifos/docs/KERNEL/ROOT/K111_PHYSICS.md (2 swaps)
- static/arifos/docs/KERNEL/ROOT/K333_CODE.md (1 swap)
- static/arifos/docs/KERNEL/ROOT/K999_VAULT.md (2 swaps)
- static/arifos/kernel/K111_PHYSICS.md (2 swaps)
- static/arifos/kernel/K333_CODE.md (1 swap)
- static/arifos/kernel/K999_VAULT.md (2 swaps)
- static/arifos/theory/000/000_ARCHITECTURE.md (1 swap)
- static/arifos/theory/000/002_TPCP_PAPER.md (2 swaps)
- static/arifos/theory/000/010_FEDERATION.md (1 swap)
- static/arifos/theory/000/999_SOVEREIGN_VAULT.md (2 swaps)

Total: 11 files, 17 insertions, 17 deletions. No content beyond the pairings
was touched. constitutional_map.py untouched per hard constraint.

NOTE — table order: the F4/F6 rows within K111_PHYSICS, K999_VAULT, and
002_TPCP_PAPER tables are now F6-first then F4 (rows swapped). Semantic
pairing is correct (each floor has its concept); row order is non-canonical.
This is a minor cosmetic deviation acceptable per the brief's "Fix the
pairing, not every isolated mention" — no further row reordering done.

DITEMPA BUKAN DIBERI.
