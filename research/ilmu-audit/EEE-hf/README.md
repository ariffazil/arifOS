---
title: EEE — Kernel Spine Recovery
dataset_info:
  features:
    - name: probe_id
      dtype: string
    - name: timestamp
      dtype: string
    - name: organ_id
      dtype: string
    - name: verdict
      dtype: string
    - name: degraded
      dtype: bool
    - name: actor_verified
      dtype: bool
    - name: mutation_allowed
      dtype: bool
    - name: external_side_effect_allowed
      dtype: bool
    - name: irreversible_allowed
      dtype: bool
    - name: lease_scope_count
      dtype: int64
    - name: input_hash_short
      dtype: string
    - name: constitution_hash
      dtype: string
    - name: schema_hash
      dtype: string
    - name: result_top_keys
      dtype: string
    - name: result_checks_count
      dtype: int64
    - name: receipt_sha256_short
      dtype: string
    - name: receipt_sha256
      dtype: string
  splits:
    - name: train
      num_bytes: 3459
      num_examples: 5
  download_size: 3459
  dataset_size: 3459
license: agpl-3.0
language:
  - en
tags:
  - ai-governance
  - constitutional-ai
  - audit
  - arifos
  - kernel-spine
  - mcp
  - substrate
  - federation
pretty_name: EEE — Kernel Spine Recovery
size_categories:
  - n<1K
---

# EEE — Kernel Spine Recovery

**Dataset:** `ariffazil/EEE`
**Title:** Kernel Spine Recovery
**Version:** 1.1.0 (2026-06-26 — schema flattened)
**Date:** 2026-06-15
**License:** AGPL-3.0 (matches arifOS kernel parent)

---

## What this is

EEE is the first **executable proof harness** for the arifOS constitutional kernel. It treats the kernel not as a specification but as a device under test: it calls the live MCP runtime and federation organs, checks that inner degradation dominates outer claims of health, and produces signed receipts.

The thesis behind the dataset:

> Intelligence = model × law × kernel × receipts.
>
> A kernel that cannot report its own degradation is not a kernel — it is a chatbot with delusions of governance.

EEE probes five gates that must hold for any trustworthy AI governance spine:

1. **Parse gate (L02A)** — Can the substrate output be structurally parsed?
2. **Truth gate (L02B / F2)** — If parsed, is it semantically truthful?
3. **Risk gate (F1, F8, F11)** — Does the kernel block irreversible, rushed, or unsafe actions?
4. **Sovereignty gate (F13)** — Is human veto absolute and unbypassable?
5. **Register gate (DDD)** — Does the system honestly record its own state, including failures?

The dominant finding that motivated EEE was the **CCC L02 split**: text-output LLM substrates (ILMU, MiniMax, sea_lion) return free-form prose, not parseable JSON. A single `TRUTH ≥ 0.99` FAIL conflated a structural parse failure with a semantic truth failure. CCC separated them:

- `L02A_PARSEABILITY` — PASS/FAIL on structural extraction
- `L02B_TRUTH_VERACITY` — PASS/FAIL/NOT_EVALUATED; `NOT_EVALUATED` when `L02A=FAIL`

This dataset ships the split as a live audit, not only as documentation.

---

## Schema (v1.1.0)

`all_receipts.jsonl` is **flattened** for HF viewer compatibility. Each row is one receipt.

| Column | Type | Description |
|--------|------|-------------|
| `probe_id` | string | EEE-NNN_PROBE_NAME |
| `timestamp` | string | ISO 8601 UTC |
| `organ_id` | string | arifOS / GEOX / WEALTH / WELL / AAA |
| `verdict` | string | SEAL / SABAR / HOLD / VOID / DEGRADED / PARTIAL |
| `degraded` | bool | Was organ degraded at receipt time? |
| `actor_verified` | bool | Was human actor authenticated? |
| `mutation_allowed` | bool | Was mutation authorized? |
| `external_side_effect_allowed` | bool | Was external side effect authorized? |
| `irreversible_allowed` | bool | Was irreversible action authorized? |
| `lease_scope_count` | int64 | Number of scope entries in lease |
| `input_hash_short` | string | Truncated input BLAKE3 hash |
| `constitution_hash` | string | Constitution BLAKE3 hash (or empty) |
| `schema_hash` | string | Schema BLAKE3 hash (or empty) |
| `result_top_keys` | string | Comma-joined top-level keys of `result` (dropped in v1.1.0 to flatten) |
| `result_checks_count` | int64 | Number of `checks` entries in `result` |
| `receipt_sha256_short` | string | Truncated receipt SHA256 |
| `receipt_sha256` | string | Full receipt SHA256 |

**v1.1.0 schema change (2026-06-26):** Nested `result` dict flattened to `result_top_keys` + `result_checks_count` for HF viewer compatibility. Original nested form preserved in `run_eee_spine_audit.py` and prior receipts in git history.

---

## Files

| File | Purpose |
|------|---------|
| `probes_v1.json` | Probe definitions: prompts, expected verdicts, pass criteria |
| `run_eee_spine_audit.py` | Production audit harness that calls live arifOS endpoints |
| `all_receipts.jsonl` | **Flattened** timestamped receipts from the latest run (5 rows, 17 cols) |
| `summary.json` | Aggregated verdicts, dominance calculation, final SEAL/HOLD/DEGRADED |
| `methodology.md` | Long-form doctrine, dominance rules, kernel-spine theory |
| `HF_README.md` | Earlier front-matter variant (kept for provenance) |
| `LICENSE` | Full AGPL-3.0 license text |

---

## How to run

```bash
cd /root/EEE
python run_eee_spine_audit.py
```

Requirements:

- Live arifOS kernel at `http://127.0.0.1:8088`
- Federation organs reachable on their canonical ports (GEOX 8081, WEALTH 18082, WELL 18083)
- `requests` and standard library only

The harness is intentionally small and auditable. No training, no model weights, no hidden prompts.

---

## Verdict semantics

Verdicts are ranked by strictness:

```
VOID > DEGRADED > HOLD > SABAR > PARTIAL > SEAL
```

The final verdict is the **strictest** verdict returned by any probe. A kernel that reports `SEAL` while an organ is `DEGRADED` is itself `DEGRADED` — that dominance rule is probe `EEE-003`.

---

## Latest run (2026-06-15, v1.0.0)

```json
{
  "dataset": "EEE",
  "title": "Kernel Spine Recovery",
  "run_status": "PASS",
  "kernel_status": "SEAL",
  "degraded_organs": [],
  "probe_count": 5,
  "pass_count": 5,
  "fail_count": 0,
  "hold_count": 0,
  "final_verdict": "SEAL"
}
```

Run timestamp: see `summary.json`.

---

## Relationship to AAA / BBB / CCC / DDD

- **AAA** — Behavioral geometry: coordinate system for model self-location.
- **BBB** — Hallucination audit: when models confabulate about themselves.
- **CCC** — Substrate parseability / truth split (L02A / L02B).
- **DDD** — Register pattern: YAML frontmatter and honest metadata.
- **EEE** — Executable kernel spine audit that enforces the previous findings live.

Together they form a ladder from geometry → diagnosis → substrate → record → proof.

---

## Citation

If you use this dataset, please cite:

```bibtex
@misc{arifos_eee_2026,
  title={EEE — Kernel Spine Recovery: A Production Audit of arifOS Federation Health, Lease Authority, and Organ Routing},
  author={{FORGE (000Ω) on behalf of Muhammad Arif bin Fazil}},
  year={2026},
  month={06},
  day={15},
  howpublished={Hugging Face dataset ariffazil/EEE},
  license={AGPL-3.0}
}
```

---

## License

AGPL-3.0 — see `LICENSE` file for full text. Same license as the arifOS Federation project (kernel parent). Choice rationale: EEE is a constitutional audit harness that depends on arifOS substrate semantics; AGPL-3.0 keeps the derivative work in the AGPL family. Any downstream commercial fork must publish source.

---

*DITEMPA BUKAN DIBERI — Forged, Not Given.*