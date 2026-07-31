# RECEIPT — M3 tools_sot.yaml Codegen · 2026-07-31

> **M3 of Kernel Hardening Sprint** — T1, regenerate tools_sot.yaml from constitutional_map.py canon.

## WHAT WAS BROKEN

`tools_sot.yaml` (10,110 bytes) had:
- `stage: '888'` present (line 176) — conflicts with constitutional_map.py
  canon header that says `arif_judge (666)`
- 8 different stage codes scattered (000, 111, 333, 444, 555, 666, 777, 888)
  with no clear source of truth
- Mixed mode aliases — same tool appearing as multiple entries with
  slightly different stage/mode combinations (e.g., `arif_init` repeated
  at lines 19 and 149)
- Hand-edited, no codegen — drift inevitable

## THE FIX

Created `scripts/gen_tools_sot.py` that:
1. Imports `CORE_NINE` (ordered list of 8 public tools) and
   `CORE_NINE_STAGE_MAP` (stage→tool mapping) from
   `arifosmcp/constitutional_map.py` (the spine)
2. Inverts the stage map to tool→stage, **skipping stage 888**
   (legacy "compose absorbed into forge" alias per
   CORE_NINE_STAGE_MAP comment)
3. Reads each tool's full spec from `CANONICAL_TOOLS` (description,
   floors, risk_tier, modes)
4. Emits a clean YAML with **one stage per tool** sourced from the spine

Emitted file: 3,886 bytes (was 10,110 — 60% reduction). Header banner:
`GENERATED — DO NOT HAND-EDIT. Regenerate via: python3 scripts/gen_tools_sot.py > tools_sot.yaml`

## ACCEPTANCE — measured at fix time

| Gate | Before | After |
|---|---|---|
| Tools emitted | 23+ entries (mode aliases) | **8 tools** |
| `grep "stage: '888'" tools_sot.yaml` | 1 (line 176) | **0** |
| `grep "stage: '666'" tools_sot.yaml` | 1 | **1** (arif_judge canon) |
| `grep "stage: '777'" tools_sot.yaml` | 2 (duplicates) | **1** (arif_forge canon) |
| Unique stage codes | 8 scattered | **8 canonical** (000, 111, 333, 444, 555, 666, 777, 999) |
| Runtime arifOS initialize | kanon-2026.07.31+0b03b5b | unchanged |
| Runtime tools/list | 8 | 8 (same names) |

## FINDING LOGGED FOR F13 (D5 — Stage canon ratification)

The codegen treats `arif_judge = 666` as canon (per
`CORE_NINE_STAGE_MAP` and the constitutional_map.py header comment).

HOWEVER, `ToolStage.JUDGE = '888'` in the same file (line 78). This is
an enum-level inconsistency between the doctrinally-declared canon and
the runtime enum. The codegen reads the doctrinally-correct source
(CORE_NINE_STAGE_MAP), NOT the enum.

Per the brief's hard constraints (no constitutional_map.py edits, no
sovereign decisions without F13), this is logged in M6 as D5 (Stage
canon: 666 vs 888 JUDGE). Sovereign ratification required to reconcile.

DITEMPA BUKAN DIBERI.
