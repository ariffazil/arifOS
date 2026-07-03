# DDD HuggingFace Upload — Step-by-step Instructions

This is a F13-territory action. The sovereign (Arif) does the push, not the agent.

## 1. Go to https://huggingface.co/new-dataset

- **Name**: `DDD`
- **Type**: Dataset
- **License**: CC-BY-4.0
- **Visibility**: Public (so the data is reproducible)

## 2. Upload files in this exact order

```
README.md                                  (the dataset card, 8K)
methodology.md                             (pre-registration, 12K)
PICKUP_RUNBOOK.md                          (handoff doc, 8K)
data/probes_v1.json                        (16 probe pairs, 4K)
data/all_receipts.jsonl                    (40 deduped receipts, 47K)
data/all_receipts.csv                      (same in CSV, 18K)
methodology_artifacts/run_ddd.py           (harness, 14K)
methodology_artifacts/rerun_kernel.py      (bug-fix harness, 7K)
methodology_artifacts/run_resume.py        (partial-run resume, 11K)
```

(adjust paths — HF wants flat `data/` or flat root, not nested. Move `methodology_artifacts/*.py` to root if needed.)

## 3. Suggested tags (one-time add after upload)

```
constitutional-ai
arifos
federation
penang-loghat
register-sensitivity
kernel-audit
llm-safety-benchmark
f1-f13
anomalous-contrast
bahasa-melayu
malaysian-llm
malay
```

## 4. Verify

After upload, check:
- `ariffazil/DDD` exists and is public
- File count = 9 (3 markdown + 3 data + 3 python)
- Total size ≈ 200 KB
- Dataset card renders correctly
- License badge shows CC-BY-4.0

## 5. After upload — record the URLs

Once pushed, save the URLs:
- `https://huggingface.co/datasets/ariffazil/DDD` (dataset page)
- `https://huggingface.co/datasets/ariffazil/DDD/tree/main/README.md` (raw card)

These go into:
- `/root/VAULT999/SEAL-DDD-PENANG-2026-06-11.json` (add `hf_url` field)
- `/root/docs/ddd-one-pager-2026-06-11.md` (cite the dataset)
- `/root/DDD/red-team-2026-06-11/PICKUP_RUNBOOK.md` (update with URLs)

## 6. The F13 caveat

This is **not** an autonomous agent action. It's a sovereign action. The agent can prep the bundle, write the card, hash the files, generate the upload checklist — but the actual `git push hf` equivalent is a human click.

If the sovereign does not have HF write access, the agent can alternatively suggest a `huggingface-cli` command for terminal execution by the sovereign.

## 7. Provenance trail

The bundle hashes (sha256) at the time of upload are recorded in the SEAL. If HF rejects the upload or files change in transit, the SEAL can be re-pinned to the new hashes.

```
DITEMPA BUKAN DIBERI — even the upload is forged, not given.
```

