# DDD Reconciliation Note — 2 worktrees, 1 finding

**Date:** 2026-06-11 10:12 MYT
**Author:** arifOS-forge-agent (Ω) self-correction
**Status:** Both worktrees refer to the same empirical reality. Below is the mapping.

## The two worktrees

| | DDD #1 (WIP) | DDD #2 (sealed) |
|---|---|---|
| Path | `/root/DDD/` | `/root/DDD/red-team-2026-06-11/` |
| When | 07:50-09:19 UTC (today) | 08:01-08:27 UTC (today) |
| Probes | 8 topics named `d1..d8` (greeting, opinion, technical, royalty, provocation, identity, constitutional, sovereign) | 9 topics named `P1..P9` (incumbent_pm, royalty, religion, race_policy, sodomy_allegations, institutional_capture, hallucination_trap, sovereignty_override, ...) |
| Probe file | inlined in `run_ddd_probes.py` | `probes_v1.json` |
| Receivers | `/root/DDD/raw/A_*.json` (Condition A), `/root/DDD/raw/B_*.json` (Condition B), `/root/DDD/raw/C_*.json` (M_minimax control) | `/root/DDD/red-team-2026-06-11/all_receipts.jsonl` (single file) |
| Numbers | 32 raw files + 2 PATCHED/v3 | 56 receipts in 1 file |
| HF bundle | none | `hf_upload_bundle/` (this is the push target) |

## Why two worktrees?

DDD #1 was started first (~07:50) using the inlined probe list in `run_ddd_probes.py`. DDD #2 was started ~08:01 with a different probe set (P1-P9) that includes `hallucination_trap` (P7) — the probe that became the smoking-gun finding. DDD #2 was sealed; DDD #1 was left in WIP state with two PATCHED/v3 d8 files modified at 09:01 and 09:19.

**They are not competing experiments. They are two probe-batteries testing overlapping hypotheses on the same target.**

## The shared empirical reality

Both worktrees show:
1. Direct ILMU exhibits register-sensitive behavior (4/8 vs 5/8 in DDD #2; matches the qualitative pattern in DDD #1).
2. ILMU direct, through kernel, returns HOLD on the production state — both worktrees' kernel condition B is HOLD-cascade.
3. The kernel can be made to work (DDD #2's rerun_kernel.py) with a 1-line MCP session_id header fix.

## Which one goes to HF?

**DDD #2** — because:
- It's the sealed one with the receipt-level provenance chain
- It has the `hallucination_trap` probe (P7) that became the most-citable finding
- It has the pre-registration, methodology, and methodology_artifacts/ in the bundle
- DDD #1 has the `02_CONTRAST_TABLE.md` and `03_VERDICT.md` writeups but the contrast table conflates different run states (per the audit I just did)
- The HF bundle already exists for DDD #2

DDD #1's raw files stay in `/root/DDD/raw/` as the WIP attempt. The contrast table and verdict in DDD #1 (`02_CONTRAST_TABLE.md`, `03_VERDICT.md`) are also useful for cross-reference but should not be the citable artifact.

## Recommendation

1. Push DDD #2 (corrected) to HF as the canonical DDD.
2. Mark DDD #1 as "exploratory / WIP / superseded" in its README.
3. If Arif wants to do a v2 with a fresh probe set, use DDD #1's inlined probes as a starting point and the corrected methodology from DDD #2.

## File disposition

| Path | Status | Action |
|---|---|---|
| `/root/DDD/hf_upload_bundle/README.md` | Corrected | Push to HF |
| `/root/DDD/hf_upload_bundle/methodology.md` | Original (was accurate) | Push to HF |
| `/root/DDD/hf_upload_bundle/PICKUP_RUNBOOK.md` | Corrected | Push to HF |
| `/root/DDD/hf_upload_bundle/data/all_receipts.jsonl` | Original (accurate) | Push to HF |
| `/root/DDD/hf_upload_bundle/data/probes_v1.json` | Original (accurate) | Push to HF |
| `/root/DDD/hf_upload_bundle/data/all_receipts.csv` | Original (accurate) | Push to HF |
| `/root/DDD/hf_upload_bundle/methodology_artifacts/*` | Original (accurate, has the bug fix) | Push to HF |
| `/root/DDD/02_CONTRAST_TABLE.md` | WIP, partially accurate | Reference only, not pushed |
| `/root/DDD/03_VERDICT.md` | WIP, partially accurate | Reference only, not pushed |
| `/root/DDD/raw/*` | WIP raw outputs | Archive locally, not pushed |
| `/root/DDD/red-team-2026-06-11/all_receipts.jsonl` | Canonical | The receipts for the HF push |
| `/root/VAULT999/SEAL-DDD-PENANG-2026-06-11.json` | SUPERSEDED (banner added) | Local, not pushed |
| `/root/VAULT999/SEAL-DDD-PENANG-CORRECTION-2026-06-11.json` | CURRENT SEAL | Local reference, cite this in the HF card |
| `/root/docs/ddd-one-pager-2026-06-11.md` | SUPERSEDED (banner added) | Local, not pushed |
| `/root/docs/ddd-one-pager-CORRECTED-2026-06-11.md` | CURRENT one-pager | Local, may push as a separate file or include in the HF card |

---

*DITEMPA BUKAN DIBERI — including the reconciliation, including the honest disposition.*
