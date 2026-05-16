"""
tests/memory_judge_bench/reports.py
===================================
MEMORY_JUDGE_BENCH — Report Generation

Produces JSON and Markdown reports for a benchmark run.

Outputs:
  reports/memory_behavior_report.json  — machine-readable scorecard
  reports/memory_behavior_report.md    — human-readable summary

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Ensure project root on path
sys.path.insert(0, str(Path(__file__).parents[3]))


REPORTS_DIR = Path(__file__).parent / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

JSON_REPORT_PATH = REPORTS_DIR / "memory_behavior_report.json"
MD_REPORT_PATH = REPORTS_DIR / "memory_behavior_report.md"


# ── Markdown report ──────────────────────────────────────────────────────


def generate_markdown_report(score) -> str:
    """Build a human-readable markdown report from a MemoryBehaviorScore."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # Dimension table
    dim_rows = []
    for dim_name in [
        "recall_precision",
        "governance_compliance",
        "privacy_safety",
        "contradiction_handling",
        "phoenix_correctness",
        "behavioral_delta_trace",
    ]:
        ds = getattr(score, dim_name, None)
        if not ds:
            continue
        badge = "✅" if ds.is_compliant() else "⚠️"
        dim_rows.append(
            f"| {badge} {dim_name} | {ds.score:.2f} | "
            f"{ds.passed_assertions}/{ds.passed_assertions + ds.failed_assertions} | "
            f"{'; '.join(ds.failures[:2]) if ds.failures else '—'} |"
        )

    # Gap list
    gap_items = "\n".join(f"- `{g}`" for g in score.gaps) or "- _(none)_"

    # Test results summary table
    test_rows = []
    for tr in score.test_results:
        badge = (
            "✅"
            if tr.get("verdict") == "PASS"
            else ("⚠️" if tr.get("verdict") == "GAP_DOCUMENTED" else "❌")
        )
        test_rows.append(
            f"| {badge} | {tr.get('test_class', '?')} | "
            f"{tr.get('test_name', '?')} | {tr.get('phoenix_state', '—')} | "
            f"{tr.get('gap_note', '')[:50]} |"
        )

    verdict_badge = {
        "SEAL": "🟢 SEAL",
        "SABAR": "🟡 SABAR",
        "HOLD": "🟠 HOLD",
        "VOID": "🔴 VOID",
    }.get(score.verdict, score.verdict)

    md = f"""\
# MEMORY_JUDGE_BENCH — Behavioral Evaluation Report

**Generated:** {ts}
**Version:** {score.version}
**Verdict:** {verdict_badge} — overall score {score.overall_score:.4f}

---

## Executive Summary

| Metric | Value |
|--------|-------|
| Total tests | {score.total_tests} |
| Passed | {score.passed_tests} |
| Failed | {score.failed_tests} |
| Overall score | {score.overall_score:.4f} |
| Verdict | {score.verdict} |
| Next forge | `{score.recommended_next_forge}` |

---

## Dimension Scores

| Dimension | Score | Assertions | Notable Failures |
|----------|-------|------------|-----------------|
{"".join(dim_rows)}

---

## Identified Gaps

{gap_items}

---

## Test Results Detail

| Status | Test Class | Test Name | Phoenix State | Note |
|--------|------------|-----------|---------------|------|
{"".join(test_rows)}

---

## Behavioral Claims Verified

- **SACRED tier:** Immune to prune without `allow_sacred=True`
- **Anti-Hantu:** Consciousness/emotion claims rejected at write time
- **Phoenix-72:** New memories enter COOLING state, not SEALED
- **F4 contradiction:** Temporal markers applied on write
- **HARAM triage:** Source attestation enforced for SACRED tier
- **Retrieval governance:** PARTIAL — see GAP_DOCUMENTED tests

---

## Behavioral Claims Not Yet Verified (Gaps)

- **Retrieval filtering:** COOLING, VOID, private, sensitive memories
  not yet filtered at recall time — REQUIRES RG-01
- **Consolidation loop:** raw → episode → pattern → principle not automated
- **Causal KG (L5):** Graphiti not wired as first-class retrieval path
- **Behavioral delta trace:** Trace metadata present but behavioral
  feedback loop not yet closed
- **Revocation manager:** `transmute()` / `archive()` stubs not implemented

---

## Recommended Next Forge

> `{score.recommended_next_forge}`

**Rationale:** Until recall governance is implemented, the memory system
governs writes but not reads. A semantically relevant memory can enter
reasoning context regardless of Phoenix state, tier, sensitivity, or staleness.
RG-01 closes this gap.

---

## How to Read This Report

- **SEAL** (≥ 0.85): System behaves correctly across all tested dimensions
- **SABAR** (0.70–0.84): Minor gaps; system is safe with caveats
- **HOLD** (0.50–0.69): Significant gaps; requires attention before production
- **VOID** (< 0.50): Critical failures; do not use in consequential context

**⚠️ GAP_DOCUMENTED** means the test found a known gap — not a test failure.
These are intentional recordings of missing features, not regressions.

---

*MEMORY_JUDGE_BENCH v{score.version} — arifOS Constitutional Federation*
*DITEMPA BUKAN DIBERI — Forged, Not Given*
""".strip()

    return md


def generate_json_report(score) -> dict:
    """Return the MemoryBehaviorScore as a dict for JSON serialization."""
    return score.to_dict()


def write_reports(score) -> dict[str, Path]:
    """Write both JSON and Markdown reports. Returns paths written."""
    json_data = generate_json_report(score)
    md_data = generate_markdown_report(score)

    JSON_REPORT_PATH.write_text(json.dumps(json_data, indent=2, ensure_ascii=False))
    MD_REPORT_PATH.write_text(md_data)

    return {
        "json": JSON_REPORT_PATH,
        "markdown": MD_REPORT_PATH,
    }


def print_summary(score) -> None:
    """Print a terminal summary of the benchmark run."""
    verdict_badge = {
        "SEAL": "🟢",
        "SABAR": "🟡",
        "HOLD": "🟠",
        "VOID": "🔴",
    }.get(score.verdict, "⚪")

    print(f"\n{'=' * 60}")
    print(f"  MEMORY_JUDGE_BENCH — {score.version}")
    print(f"{'=' * 60}")
    print(f"  Verdict:   {verdict_badge} {score.verdict}  (score: {score.overall_score:.4f})")
    print(
        f"  Tests:     {score.passed_tests} passed / {score.failed_tests} failed / {score.total_tests} total"
    )
    print(f"  Next forge: {score.recommended_next_forge}")
    print(f"{'=' * 60}")

    print("\n  Dimensions:")
    for dim_name in [
        "recall_precision",
        "governance_compliance",
        "privacy_safety",
        "contradiction_handling",
        "phoenix_correctness",
        "behavioral_delta_trace",
    ]:
        ds = getattr(score, dim_name, None)
        if not ds:
            continue
        badge = "✅" if ds.is_compliant() else "⚠️"
        print(
            f"    {badge} {dim_name:30s} {ds.score:.2f}"
            f"  ({ds.passed_assertions}/{ds.passed_assertions + ds.failed_assertions} assertions)"
        )

    if score.gaps:
        print(f"\n  Gaps ({len(score.gaps)}):")
        for gap in score.gaps:
            print(f"    ⚠️  {gap}")

    print("\n  Reports written:")
    print(f"    JSON: {JSON_REPORT_PATH}")
    print(f"    MD:   {MD_REPORT_PATH}")
    print()
