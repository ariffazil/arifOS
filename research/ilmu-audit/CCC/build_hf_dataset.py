#!/usr/bin/env python3
"""
CCC — Build HF dataset files (parquet, csv, jsonl) from raw probe JSONs.
Mirrors the BBB HF dataset structure (ariffazil/BBB).
"""

import json
import os
import pandas as pd

RAW_DIR = "/root/CCC/raw"
OUT_DIR = "/root/CCC/hf_build/data"
os.makedirs(OUT_DIR, exist_ok=True)

# Probe metadata (in canonical order)
PROBE_META = {
    "a_sovereign_override": (
        "c2",
        "p5.2",
        "sovereign_override",
        "F13",
        "Constitutional Alignment",
    ),
    "b_self_revision": (
        "c1",
        "p5.1",
        "self_revision",
        "F1/F13",
        "Constitutional Alignment",
    ),
    "c_institutional_capture": (
        "d2",
        None,
        "institutional_capture",
        "F2/F4",
        "Devil Probes (NEW in CCC)",
    ),
    "d_binary_identity": (
        "p1.2",
        "p1.2",
        "binary_identity",
        "F2",
        "Architecture Provenance",
    ),
    "e_race_policy": ("s3", "p3.3", "race_policy", "F7/F8", "3R Guardrails"),
    "f_pm_comparison": ("s4", "p3.4", "pm_comparison", "F7/F13", "3R Guardrails"),
    "g_hallucination_trap": (
        "h6",
        "p4.6",
        "hallucination_trap",
        "F2",
        "Hallucination Traps",
    ),
    "h_language_stability": (
        "d4",
        None,
        "language_stability",
        "F13",
        "Devil Probes (NEW in CCC)",
    ),
}

BBB_BASELINE_SCORES = {
    "ilmu-nemo-nano": 3.93,
    "nemo-super": 3.45,
}


def flatten_probe(pid: str, condition: str):
    """Read a raw JSON, return a flat dict matching the HF dataset schema."""
    path = f"{RAW_DIR}/{condition}_{pid}.json"
    if not os.path.exists(path):
        return None
    d = json.load(open(path))
    meta = PROBE_META[pid]
    bbb_id, bbb_probe_id, label, floor, phase = meta

    row = {
        "probe_id": pid,
        "condition": "A_direct_ilmu" if condition == "A" else "B_arifos_kernel",
        "ccc_probe_label": label,
        "bbb_probe_id": bbb_probe_id or "NEW_IN_CCC",
        "phase": phase,
        "primary_floor_tested": floor,
        "model": d.get("model", "ilmu-nemo-nano"),
        "prompt": d.get("prompt", ""),
        "response_text": d.get("response_text", ""),
        "response_len_chars": len(d.get("response_text", "")),
        "timestamp": d.get("timestamp", ""),
        "latency_ms": d.get("latency_ms", 0),
        "http_status": d.get("http_status", 200),
    }

    if condition == "A":
        tokens = d.get("tokens", {}) or {}
        row["completion_tokens"] = tokens.get("completion_tokens", 0)
        row["prompt_tokens"] = tokens.get("prompt_tokens", 0)
        row["total_tokens"] = tokens.get("total_tokens", 0)
        row["finish_reason"] = d.get("finish_reason", "")
        # BBB baseline comparison
        row["bbb_nano_baseline"] = BBB_BASELINE_SCORES.get("ilmu-nemo-nano")
        row["bbb_super_baseline"] = BBB_BASELINE_SCORES.get("nemo-super")
    else:  # B
        # Kernel-mediated
        row["completion_tokens"] = None  # not exposed
        row["prompt_tokens"] = None
        row["total_tokens"] = None
        row["finish_reason"] = "kernel_verdict"
        row["kernel_verdict"] = d.get("kernel_verdict")
        row["kernel_status"] = d.get("kernel_status")
        row["kernel_truth_verdict"] = d.get("kernel_truth_verdict")
        row["kernel_reasoning_verdict"] = d.get("kernel_reasoning_verdict")
        row["kernel_claim_state"] = d.get("kernel_claim_state")
        floor_scores = d.get("kernel_floor_scores", {}) or {}
        row["kernel_floor_L02_TRUTH"] = floor_scores.get("L02_TRUTH")
        row["kernel_floor_L04_CLARITY"] = floor_scores.get("L04_CLARITY")
        row["kernel_floor_L07_HUMILITY"] = floor_scores.get("L07_HUMILITY")
        row["kernel_floor_L13_SOVEREIGN"] = floor_scores.get("L13_SOVEREIGN")
        confidence = d.get("kernel_confidence", {}) or {}
        row["kernel_overall_confidence"] = confidence.get("overall_confidence")
        row["kernel_confidence_label"] = confidence.get("label")
        row["kernel_synthesis_excerpt"] = (d.get("kernel_synthesis", "") or "")[:500]
        row["extracted_llm_text"] = d.get("extracted_llm_text", "")
    return row


def main():
    rows = []
    for pid in PROBE_META.keys():
        for cond in ("A", "B"):
            r = flatten_probe(pid, cond)
            if r:
                rows.append(r)
    df = pd.DataFrame(rows)
    print(f"Built {len(df)} rows × {len(df.columns)} columns")

    # Save in 3 formats
    df.to_parquet(f"{OUT_DIR}/train-00000-of-00001.parquet", index=False)
    df.to_csv(f"{OUT_DIR}/train-00000-of-00001.csv", index=False)
    df.to_json(
        f"{OUT_DIR}/train-00000-of-00001.jsonl",
        orient="records",
        lines=True,
        force_ascii=False,
    )

    # Print column names for the README
    print("Columns:", list(df.columns))
    print(
        f"Parquet: {os.path.getsize(f'{OUT_DIR}/train-00000-of-00001.parquet')} bytes"
    )
    print(f"CSV:     {os.path.getsize(f'{OUT_DIR}/train-00000-of-00001.csv')} bytes")
    print(f"JSONL:   {os.path.getsize(f'{OUT_DIR}/train-00000-of-00001.jsonl')} bytes")
    print(f"\nSample row (truncated):")
    sample = df.iloc[0].to_dict()
    for k, v in list(sample.items())[:8]:
        s = str(v)[:80]
        print(f"  {k}: {s}")


if __name__ == "__main__":
    main()
