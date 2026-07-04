# /root/DDD/ — Exploratory / WIP / Superseded by DDD #2

**This worktree is exploratory.** The canonical DDD for HF push lives at
`/root/DDD/red-team-2026-06-11/` and its bundle at `/root/DDD/hf_upload_bundle/`.

**Why this worktree exists:** Initial probe set was inlined in
`run_ddd_probes.py` (8 topics named d1-d8). The sealed experiment (DDD #2)
used a different probe set (9 topics named P1-P9, includes hallucination_trap
P7). Both run on the same target. DDD #2 is the citable artifact.

**What stays here:** raw receipts, the WIP contrast table, the WIP verdict.
These are reference materials, not the published dataset.

**See:** `/root/DDD/RECONCILIATION_NOTE_2026-06-11.md` for the full mapping.

---

## Status of files in this worktree (as of 2026-06-11 10:12 MYT)

| File | Status | Action |
|---|---|---|
| `00_PREREGISTRATION.md` | Pre-registered, accurate | Reference only |
| `01_ROUTING.md` | Decision doc | Reference only |
| `02_CONTRAST_TABLE.md` | WIP, conflates runs | Cross-reference; do not cite as primary |
| `03_VERDICT.md` | WIP, partial finding | Cross-reference; do not cite as primary |
| `run_ddd_probes.py` | Working harness | Keep as v2 probe template |
| `raw/A_*.json` (8 formal + 8 loghat + 4 misc = 20) | Direct ILMU outputs | Archive |
| `raw/B_*.json` (16) | Kernel condition outputs | Archive; kernel all HOLD |
| `raw/C_*.json` (4) | MiniMax control | Archive; mislabeled |
| `raw/B_PATCHED_d8_sovereign_loghat.json` | Same HOLD behavior, different wording | Archive; misleading filename |
| `raw/B_v3_d8_sovereign_FORMAL.json` | Same HOLD behavior, different wording | Archive; misleading filename |
| `raw/ALL_RESULTS.json` | Compiled raw | Archive |
| `scoring/` | Scoring scripts | Reference |
| `red-team-2026-06-11/` | **THE SEALED DDD #2** | Push from here |
| `hf_upload_bundle/` | The HF push bundle (corrected) | Push this |
| `RECONCILIATION_NOTE_2026-06-11.md` | Just written | Read this first |

---

## When to come back to this worktree

1. If you want a v2 probe set (different from P1-P9), use the d1-d8 inlined probes here as a starting point.
2. If you want to compare a different substrate model (Qwen, Llama), the harness is reusable.
3. If you want to do a Penang speaker validation round (per the mak/abah path), the probe structure here is the right template.

Otherwise, treat `/root/DDD/red-team-2026-06-11/` as canonical.

---

*Forged: 2026-06-11 10:12 MYT · by arifOS-forge-agent (Ω) self-correction*
