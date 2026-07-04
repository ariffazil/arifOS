# DDD Pickup Runbook — CORRECTED EDITION (post-F11/F2 audit)

**Date of correction:** 2026-06-11 10:08 MYT
**Supersedes:** the prior runbook dated 2026-06-11 08:27

The original runbook's "Day 1" card TL;DR was:
> "Direct ILMU refuses 5/8 on Penang loghat + hallucinates on the trap probe. Through the arifOS kernel: 0/8 refusals, no hallucination, register-mirrors perfectly. The mind is in the kernel, not the model."

This is **partially incorrect** and is what the corrected SEAL+one-pager+README replace. The corrections are documented in `/root/VAULT999/SEAL-DDD-PENANG-CORRECTION-2026-06-11.json`. This runbook now points at the corrected artifacts.

---

## What the receipts actually say (8-cell decomposition)

| Cell | n | Refused | Reg-match | Loghat-comp | Latency | Note |
|---|---|---|---|---|---|---|
| A_ilmu_direct formal | 8 | 4 (50%) | 0.51 | 0.43 | 910ms | The original BBB/CCC cell |
| A_ilmu_direct loghat | 8 | 5 (62.5%) | 0.74 | 0.48 | 714ms | 1 of 5 "refusals" is a hallucination (P7) |
| B_kernel_first_run formal | 8 | 8 (100%) | 1.00 | 0.40 | **3ms** | MCP session_id bug — kernel never engaged |
| B_kernel_first_run loghat | 8 | 8 (100%) | 0.30 | 0.40 | 1216ms | Same bug, loghat got further into MCP layer |
| B_kernel_rerun formal | 8 | 0 (0%) | 0.65 | 0.60 | 7168ms | Post-patch: kernel works |
| B_kernel_rerun loghat | 8 | 0 (0%) | 1.00 | 0.85 | 7193ms | Post-patch: kernel works on loghat |
| M_minimax_formal | 8 | 0 actual (6/8 mislabeled) | 0.82 | 0.43 | **16852ms** | 4× finish_reason=length, 2× timeout |

---

## The right next steps (in order)

### 1. Sovereign reviews the corrected bundle
- Read `/root/VAULT999/SEAL-DDD-PENANG-CORRECTION-2026-06-11.json` (corrected SEAL with all per-cell numbers)
- Read `/root/DDD/hf_upload_bundle/README.md` (corrected dataset card)
- Read `/root/docs/ddd-one-pager-CORRECTED-2026-06-11.md` (corrected one-pager)
- Read the originals at the `.pre-correction-2026-06-11T10-08` suffix to see the overclaim explicitly

### 2. Sovereign pushes DDD to HF (F13 territory)
The agent cannot click the push button. Once you approve, the exact command is below. **The card is honest. The receipts are public. The overclaim is named, not hidden.**

```bash
# Set HF token first (one-time)
export HF_TOKEN="hf_..."  # get from https://huggingface.co/settings/tokens

# Auth
hf auth login --token "$HF_TOKEN"

# Create the dataset (one-time)
# Visit https://huggingface.co/new-dataset
# Name: DDD, License: CC-BY-4.0, Visibility: Public

# Push (from the bundle directory)
cd /root/DDD/hf_upload_bundle
hf upload ariffazil/DDD . . \
  --repo-type dataset \
  --commit-message "DDD v1 — Penang loghat register-sensitivity (corrected edition, F11/F2 audit applied)" \
  --create-pr  # sovereign reviews PR first, then merge
```

After push, the URLs to record:
- `https://huggingface.co/datasets/ariffazil/DDD`
- `https://huggingface.co/datasets/ariffazil/DDD/tree/main/README.md`

### 3. Update CCC card with the kernel-cascade finding
The CCC card should add: "Same MCP session_id bug affected DDD. Pre-patch kernel returns 100% HOLD on any free-form LLM substrate. The CCC kernel DEGRADES -0.190 mean is a symptom of the same integration bug. Patch is 1 line: read mcp-session-id from HTTP header, not body."

### 4. Penang speaker validation (the mak/abah path)
Per the original Day 3: ask a native Penang speaker to read the 16 probe pairs out loud. Replace `probes_v1.json` with `probes_v2.json`. Re-run. Update SEAL. Re-push.

The P7_loghat finding (1/1 hallucination) is a single observation. With n=1 we cannot say "loghat triggers confabulation" — we can say "loghat *can* trigger confabulation in this model on this probe class." Replication at k=5 is required before the claim is publishable-grade.

### 5. Re-run the M_minimax control with a real comparison model
The M_minimax "control" was mislabeled infrastructure failures. Use a model with:
- Real 200 OK responses (no length truncation)
- Reasonable latency (<5s)
- Equivalent capability tier to ILMU

Candidates: `Qwen2.5-7B-Instruct`, `Llama-3.1-8B-Instruct`, `sea-lion-2.1`. Replace the M_minimax cell in the next run.

### 6. Fix the MCP session_id bug
The bug is 1 line in `rerun_kernel.py`. The fix is in the file (and the dataset's `methodology_artifacts/`). The kernel itself is correct. Apply the patch in the running kernel client (`/root/arifOS/arifosmcp/runtime/` or wherever the MCP client lives — check `/root/DDD/hf_upload_bundle/methodology_artifacts/rerun_kernel.py` for the line).

This is a 5-minute change for whoever owns the MCP client. Once applied, the kernel stops cascading to HOLD on every probe, and CCC/BBB reruns become meaningful.

---

## Citation chain for the corrected finding

When you cite DDD, use:
- The corrected SEAL: `arifazil/VAULT999/SEAL-DDD-PENANG-CORRECTION-2026-06-11.json`
- The corrected one-pager: `/root/docs/ddd-one-pager-CORRECTED-2026-06-11.md`
- The receipts: `sha256:426c0d6d5aeb89958f6073d7380f95b020970b4ff22b0b7246e3a1d7c81ceb83`
- The original SEAL/one-pager are preserved at `.pre-correction-2026-06-11T10-08` suffix for audit trail

Don't cite the originals as if they were current. The supersession banner is on the originals so anyone reading them knows.

---

## What NOT to do (patterns to break)

1. **Don't quote aggregate numbers without per-cell decomposition.** This is what the F11/F2 detector caught.
2. **Don't treat LLM-as-judge labels as ground truth.** The judge mislabeled infrastructure failures as refusals. Always spot-check at least 3 receipts per cell.
3. **Don't promote post-patch numbers to "the kernel" headline.** Always name the patch context. The shipped kernel is not the patched kernel.
4. **Don't push the overclaimed version.** The corrected bundle is more credible. Pushing the overclaim would be irreversible reputation damage on a public artifact, and would invalidate BBB/CCC credibility too (same author, same audit standards).
5. **Don't claim "kernel as mind saves the day" without naming the integration constraint.** The kernel works post-patch. The shipped state is 100% HOLD. Both are true. Both must be in the card.

---

## Final seal status

| Seal | State | Use? |
|---|---|---|
| SEAL-DDD-PENANG-2026-06-11 | SUPERSEDED (banner added) | Audit trail only |
| SEAL-DDD-PENANG-2026-06-11.json.pre-correction-2026-06-11T10-08 | Original (untouched) | Audit trail only |
| SEAL-DDD-PENANG-CORRECTION-2026-06-11 | CURRENT | Cite this one |
| SEAL-DDD-B-HYPOTHESIS-CAPTURE-2026-06-11 | Pre-run hypothesis capture | Reference only |
| SEAL-DDD-HF-UPLOAD-BUNDLE-2026-06-11 | Bundle SHA manifest | Reference only |

---

*DITEMPA BUKAN DIBERI — including the audit, including the rollback, including the corrected version.*

*Forged: 2026-06-11 10:08 MYT · by arifOS-forge-agent (Ω) on af-forge · self-correction from live receipts*
