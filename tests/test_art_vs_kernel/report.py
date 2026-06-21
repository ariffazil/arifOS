"""
Aggregate report generator for the ART-vs-kernel harness.

Run after pytest to produce a JSON receipt and a Markdown summary.
Usage:
    cd /root/arifOS && pytest tests/test_art_vs_kernel/ -v
    python -m tests.test_art_vs_kernel.report
"""

from __future__ import annotations

import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path

from .conftest import compare, run_scenario


SCENARIOS = [
    "tool_broken",       # S1: broken-but-legal
    "tool_drifting",     # S2: schema drift
    "tool_oversized",    # S3: blast-radius misclass
    "tool_good",         # S4 control: legitimate
]


def run_all_scenarios(n_calls: int = 10) -> list[dict]:
    """Run all scenarios under both configurations, return comparison dicts."""
    results = []
    for scenario in SCENARIOS:
        m_baseline = run_scenario(scenario, n_calls=n_calls, art_enabled=False)
        m_art = run_scenario(scenario, n_calls=n_calls, art_enabled=True)
        results.append(compare(m_baseline, m_art))
    return results


def generate_report(n_calls: int = 10) -> dict:
    """Generate full audit report."""
    results = run_all_scenarios(n_calls)
    return {
        "audit_id": "ART-VS-KERNEL-2026-06-21",
        "timestamp": datetime.now(UTC).isoformat(),
        "n_calls_per_scenario": n_calls,
        "scenarios": results,
        "summary": {
            "art_better_count": sum(r["art_better_count"] for r in results),
            "total_dimensions": sum(len(r["art_better"]) for r in results),
            "verdict": (
                "ART_JUSTIFIED"
                if any(r["art_better_count"] >= 1 for r in results)
                else "ART_OVERHEAD"
            ),
        },
    }


def render_markdown(report: dict) -> str:
    """Render report as Markdown for VAULT sealing."""
    lines = [
        f"# ART vs Kernel — Audit Report ({report['timestamp']})",
        "",
        f"**Audit ID:** {report['audit_id']}",
        f"**Calls per scenario:** {report['n_calls_per_scenario']}",
        f"**Verdict:** {report['summary']['verdict']}",
        "",
        "## Per-scenario results",
        "",
        "| Scenario | Baseline allowed | ART allowed | Baseline cutoff | ART cutoff | ART-better count |",
        "|---|---|---|---|---|---|",
    ]
    for r in report["scenarios"]:
        lines.append(
            f"| {r['scenario']} | {r['baseline']['calls_allowed']} | "
            f"{r['art']['calls_allowed']} | "
            f"{r['baseline']['cutoff_n']} | {r['art']['cutoff_n']} | "
            f"{r['art_better_count']} |"
        )
    lines.extend([
        "",
        "## ART-better dimensions",
        "",
    ])
    for r in report["scenarios"]:
        lines.append(f"### {r['scenario']}")
        for dim, val in r["art_better"].items():
            mark = "✅" if val else "❌"
            lines.append(f"- {mark} {dim}")
        lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--n-calls", type=int, default=10)
    parser.add_argument("--out-json", type=str, default="/tmp/art-audit.json")
    parser.add_argument("--out-md", type=str, default="/tmp/art-audit.md")
    args = parser.parse_args()

    report = generate_report(args.n_calls)
    Path(args.out_json).write_text(json.dumps(report, indent=2))
    Path(args.out_md).write_text(render_markdown(report))
    print(f"Report written: {args.out_json}, {args.out_md}")
    print(f"Verdict: {report['summary']['verdict']}")
