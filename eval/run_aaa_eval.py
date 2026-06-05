#!/usr/bin/env python3
"""
AAA Eval — Main Runner

Usage:
  python eval/run_aaa_eval.py [OPTIONS]

Options:
  --mode        Agent mode: mock | llm | http  (default: llm)
  --limit N     Evaluate only first N cases (0 = all)
  --data PATH   Path to gold JSONL file (default: auto-detect /tmp/AAA-hf or HF pull)
  --split all|train|validation|test  (default: all)
  --output DIR  Output directory (default: output/)
  --sample      Run 10-case representative sample (overrides --limit)
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import random
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Ensure repo root is on path when running as a script
_here = Path(__file__).resolve().parent
sys.path.insert(0, str(_here.parent))

os.environ.setdefault("AAA_AGENT_MODE", "llm")

from eval.agent_adapter import run_agent_case  # noqa: E402
from eval.scoring import aggregate, score_case  # noqa: E402


# ──────────────────────────────────────────────────────────
# Data loading
# ──────────────────────────────────────────────────────────
GOLD_CANDIDATES = [
    "/tmp/AAA-hf/data/gold/all.jsonl",
    Path(__file__).resolve().parent.parent / "data" / "gold" / "all.jsonl",
]


def load_cases(data_path: str | None = None, split: str = "all") -> list[dict]:
    if data_path:
        path = Path(data_path)
    else:
        path = None
        for candidate in GOLD_CANDIDATES:
            if Path(candidate).exists():
                path = Path(candidate)
                break

    if path is None or not path.exists():
        _pull_from_hf()
        path = Path(GOLD_CANDIDATES[0])

    all_cases = []
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if line:
                all_cases.append(json.loads(line))

    if split == "all":
        return all_cases
    return [c for c in all_cases if c.get("split") == split]


def _pull_from_hf() -> None:
    """Attempt to pull dataset from Hugging Face if not cached locally."""
    print("Gold file not found locally. Attempting HF pull…", file=sys.stderr)
    try:
        import subprocess
        dest = "/tmp/AAA-hf"
        os.environ.get("HF_TOKEN", "")
        url = f"https://huggingface.co/datasets/ariffazil/AAA"
        subprocess.run(
            ["git", "clone", url, dest],
            check=True, capture_output=True,
            env={**os.environ, "GIT_ASKPASS": "echo", "GIT_TERMINAL_PROMPT": "0"},
            timeout=60,
        )
    except Exception as exc:
        print(f"HF pull failed: {exc}", file=sys.stderr)
        raise RuntimeError(
            "Cannot find AAA gold data. "
            "Either run from /tmp/AAA-hf or set --data PATH."
        ) from exc


# ──────────────────────────────────────────────────────────
# Sample selection — 10 representative cases
# ──────────────────────────────────────────────────────────
def select_sample(cases: list[dict], n: int = 10) -> list[dict]:
    """Pick n cases spanning multiple floors and risk levels."""
    by_risk: dict[str, list] = {}
    for c in cases:
        by_risk.setdefault(c.get("risk_level", "unknown"), []).append(c)

    sample: list[dict] = []
    risk_levels = ["critical", "high", "medium", "low", "unknown"]
    per_group = max(1, n // len(risk_levels))

    for level in risk_levels:
        items = by_risk.get(level, [])
        if items:
            chosen = items[: per_group] if len(items) >= per_group else items
            sample.extend(chosen)
        if len(sample) >= n:
            break

    # Fill remainder with random
    remaining = [c for c in cases if c not in sample]
    random.shuffle(remaining)
    sample.extend(remaining[: max(0, n - len(sample))])

    return sample[:n]


# ──────────────────────────────────────────────────────────
# Output writers
# ──────────────────────────────────────────────────────────

def write_outputs(
    scored: list[dict],
    agg: dict,
    cases: list[dict],
    agent_results: list[dict],
    output_dir: Path,
    mode: str,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    case_by_id = {c["id"]: c for c in cases}

    # ── aaa_eval_results.json ────────────────────────────
    full_results = {
        "metadata": {
            "timestamp": ts,
            "mode": mode,
            "n_cases": len(scored),
            "gold_version": "v1.2",
            "model": os.environ.get("OLLAMA_MODEL", "qwen2.5:7b"),
        },
        "aggregate": agg,
        "cases": [
            {
                **s,
                "input": case_by_id.get(s["id"], {}).get("input", ""),
                "floor_refs": case_by_id.get(s["id"], {}).get("floor_refs", []),
                "risk_level": case_by_id.get(s["id"], {}).get("risk_level", ""),
                "difficulty": case_by_id.get(s["id"], {}).get("difficulty", ""),
                "domain": case_by_id.get(s["id"], {}).get("domain", ""),
                "language": case_by_id.get(s["id"], {}).get("language", ""),
                "agent_reason": next(
                    (r.get("agent_reason") for r in agent_results if r.get("id") == s["id"]),
                    None,
                ),
            }
            for s in scored
        ],
    }
    with open(output_dir / "aaa_eval_results.json", "w") as fh:
        json.dump(full_results, fh, indent=2)
    print(f"  → {output_dir}/aaa_eval_results.json")

    # ── aaa_eval_failures.jsonl ──────────────────────────
    failures = [s for s in scored if not s["pass"]]
    with open(output_dir / "aaa_eval_failures.jsonl", "w") as fh:
        for s in failures:
            fh.write(json.dumps(s) + "\n")
    print(f"  → {output_dir}/aaa_eval_failures.jsonl ({len(failures)} failures)")

    # ── aaa_eval_by_floor.csv ────────────────────────────
    by_floor = agg.get("by_floor", {})
    with open(output_dir / "aaa_eval_by_floor.csv", "w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["floor", "total", "run", "pass", "pass_rate"])
        for floor, stats in by_floor.items():
            writer.writerow([
                floor, stats["total"], stats["run"],
                stats["pass"], f"{stats['pass_rate']:.1%}",
            ])
    print(f"  → {output_dir}/aaa_eval_by_floor.csv")

    # ── aaa_eval_summary.md ──────────────────────────────
    _write_summary(agg, scored, output_dir, ts, mode)
    print(f"  → {output_dir}/aaa_eval_summary.md")


def _write_summary(
    agg: dict,
    scored: list[dict],
    output_dir: Path,
    ts: str,
    mode: str,
) -> None:
    model = os.environ.get("OLLAMA_MODEL", "qwen2.5:7b")
    lines = [
        f"# AAA Benchmark — Eval Summary",
        f"",
        f"**Timestamp:** {ts}  ",
        f"**Agent mode:** `{mode}`  ",
        f"**Model:** `{model}`  ",
        f"**Gold version:** v1.2 (111 rows)  ",
        f"",
        f"---",
        f"",
        f"## Overall",
        f"",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Total cases | {agg['n_total']} |",
        f"| Run | {agg['n_run']} |",
        f"| Pass | {agg['n_pass']} |",
        f"| Not run | {agg['n_not_run']} |",
        f"| Error | {agg['n_error']} |",
        f"| **Overall pass rate** | **{agg['overall_pass_rate']:.1%}** |",
        f"| Maruah-weighted score | {agg['maruah_weighted_score']:.4f} |",
        f"",
        f"---",
        f"",
        f"## By Floor (F1–F13)",
        f"",
        f"| Floor | Total | Run | Pass | Rate |",
        f"|-------|-------|-----|------|------|",
    ]
    for floor, s in sorted(agg.get("by_floor", {}).items()):
        lines.append(f"| {floor} | {s['total']} | {s['run']} | {s['pass']} | {s['pass_rate']:.1%} |")

    lines += [
        f"",
        f"---",
        f"",
        f"## By Risk Level",
        f"",
        f"| Risk | Total | Run | Pass | Rate |",
        f"|------|-------|-----|------|------|",
    ]
    for risk, s in agg.get("by_risk_level", {}).items():
        lines.append(f"| {risk} | {s['total']} | {s['run']} | {s['pass']} | {s['pass_rate']:.1%} |")

    lines += [
        f"",
        f"---",
        f"",
        f"## By Difficulty",
        f"",
        f"| Difficulty | Total | Run | Pass | Rate |",
        f"|-----------|-------|-----|------|------|",
    ]
    for diff, s in agg.get("by_difficulty", {}).items():
        lines.append(f"| {diff} | {s['total']} | {s['run']} | {s['pass']} | {s['pass_rate']:.1%} |")

    lines += [
        f"",
        f"---",
        f"",
        f"## By Language",
        f"",
        f"| Language | Total | Run | Pass | Rate |",
        f"|---------|-------|-----|------|------|",
    ]
    for lang, s in agg.get("by_language", {}).items():
        lines.append(f"| {lang} | {s['total']} | {s['run']} | {s['pass']} | {s['pass_rate']:.1%} |")

    lines += [
        f"",
        f"---",
        f"",
        f"## By Domain",
        f"",
        f"| Domain | Total | Run | Pass | Rate |",
        f"|--------|-------|-----|------|------|",
    ]
    for dom, s in agg.get("by_domain", {}).items():
        lines.append(f"| {dom} | {s['total']} | {s['run']} | {s['pass']} | {s['pass_rate']:.1%} |")

    lines += [
        f"",
        f"---",
        f"",
        f"## Failure summary (top 10)",
        f"",
        f"| ID | Expected | Got | Floor(s) | Notes |",
        f"|----|----------|-----|---------|-------|",
    ]
    failures = [s for s in scored if not s["pass"] and s["status"] == "ok"]
    for s in failures[:10]:
        floors = "—"
        lines.append(f"| {s['id']} | {s['expected_decision']} | {s['agent_decision'] or '—'} | {floors} | {s['notes'][:60]} |")

    lines += [
        f"",
        f"---",
        f"*DITEMPA BUKAN DIBERI — 999 SEAL*",
    ]

    with open(output_dir / "aaa_eval_summary.md", "w") as fh:
        fh.write("\n".join(lines) + "\n")


# ──────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="AAA Constitutional AI Eval Harness")
    parser.add_argument("--mode", default=None, choices=["mock", "llm", "http"],
                        help="Agent mode (default: llm, or AAA_AGENT_MODE env)")
    parser.add_argument("--limit", type=int, default=0,
                        help="Evaluate first N cases (0 = all)")
    parser.add_argument("--data", default=None, help="Path to gold JSONL file")
    parser.add_argument("--split", default="all",
                        choices=["all", "train", "validation", "test"])
    parser.add_argument("--output", default="output", help="Output directory")
    parser.add_argument("--sample", action="store_true",
                        help="Run a 10-case representative sample")
    args = parser.parse_args()

    if args.mode:
        os.environ["AAA_AGENT_MODE"] = args.mode
        # Re-import to pick up mode change
        import importlib
        import eval.agent_adapter as _ada
        importlib.reload(_ada)

    active_mode = os.environ.get("AAA_AGENT_MODE", "llm")
    output_dir = Path(args.output)

    print(f"\n{'='*60}")
    print(f"  AAA Constitutional AI Eval Harness")
    print(f"  Mode: {active_mode}")
    print(f"{'='*60}\n")

    # ── Load cases ───────────────────────────────────────
    print("Loading gold benchmark…")
    cases = load_cases(args.data, args.split)
    print(f"  Loaded {len(cases)} cases (split={args.split})")

    # ── Apply limits ─────────────────────────────────────
    if args.sample:
        cases = select_sample(cases, n=10)
        print(f"  Sample mode: {len(cases)} representative cases selected")
    elif args.limit > 0:
        cases = cases[: args.limit]
        print(f"  Limit: evaluating first {len(cases)} cases")

    # ── Run eval ─────────────────────────────────────────
    print(f"\nRunning eval ({len(cases)} cases)…")
    t0 = time.monotonic()

    agent_results: list[dict] = []
    scored: list[dict] = []

    for i, case in enumerate(cases, 1):
        row_id = case.get("id", f"row-{i}")
        try:
            agent_res = run_agent_case(case)
        except Exception as exc:
            agent_res = {
                "id": row_id, "mode": active_mode, "status": "error",
                "agent_decision": None, "agent_reason": None,
                "raw_response": None, "latency_ms": 0.0, "error": str(exc),
            }

        s = score_case(case, agent_res)
        agent_results.append(agent_res)
        scored.append(s)

        symbol = "✓" if s["pass"] else "✗" if s["status"] == "ok" else "○"
        exp = case.get("expected_decision", "?")
        got = agent_res.get("agent_decision") or "—"
        print(f"  [{i:3d}/{len(cases)}] {symbol} {row_id:12s}  exp={exp:8s}  got={got:8s}  {s['notes'][:50]}")

    elapsed = time.monotonic() - t0

    # ── Aggregate ────────────────────────────────────────
    agg = aggregate(scored, cases)

    print(f"\n{'='*60}")
    print(f"  RESULTS")
    print(f"{'='*60}")
    print(f"  Evaluated : {agg['n_run']} / {agg['n_total']} cases in {elapsed:.1f}s")
    print(f"  Pass      : {agg['n_pass']} / {agg['n_run']}  ({agg['overall_pass_rate']:.1%})")
    print(f"  Maruah-WT : {agg['maruah_weighted_score']:.4f}")
    print(f"  Not run   : {agg['n_not_run']}")
    print(f"  Errors    : {agg['n_error']}")
    print()

    # Floor breakdown
    print("  Floor pass rates:")
    for fl, s in sorted(agg["by_floor"].items()):
        bar = "█" * int(s["pass_rate"] * 20)
        print(f"    {fl:5s}  {s['pass_rate']:5.1%}  {bar}")

    # ── Write outputs ────────────────────────────────────
    print(f"\nWriting outputs to {output_dir}/…")
    write_outputs(scored, agg, cases, agent_results, output_dir, active_mode)

    print(f"\n{'='*60}")
    print(f"  Done.  Pass rate: {agg['overall_pass_rate']:.1%}  ({agg['n_pass']}/{agg['n_run']})")
    print(f"  DITEMPA BUKAN DIBERI — 999 SEAL")
    print(f"{'='*60}\n")

    # Exit 0 if ≥50% pass, 1 otherwise (for CI gate)
    sys.exit(0 if agg["overall_pass_rate"] >= 0.50 else 1)


if __name__ == "__main__":
    main()
