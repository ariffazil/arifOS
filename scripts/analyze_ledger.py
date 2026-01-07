#!/usr/bin/env python3
"""
analyze_ledger.py — Cooling Ledger Floor Analysis Tool (v45Ω)

Analyzes the Cooling Ledger to identify floor violations, pass rates,
and "hot zones" (frequent failure patterns).

Usage:
    python scripts/analyze_ledger.py --last 50
    python scripts/analyze_ledger.py --violations-only
    python scripts/analyze_ledger.py --floor F1

DITEMPA BUKAN DIBERI — Forged, not given; truth must cool before it rules.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional

# Default ledger path
DEFAULT_LEDGER_PATH = Path(__file__).parent.parent / "cooling_ledger" / "L1_cooling_ledger.jsonl"


def load_ledger_entries(
    ledger_path: Path,
    last_n: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Load entries from the JSONL ledger.

    Args:
        ledger_path: Path to the JSONL ledger file
        last_n: Optional limit to last N entries

    Returns:
        List of parsed JSON entries
    """
    entries = []
    if not ledger_path.exists():
        print(f"ERROR: Ledger file not found: {ledger_path}")
        return entries

    with open(ledger_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError as e:
                    print(f"WARN: Skipping malformed line: {e}")

    if last_n:
        entries = entries[-last_n:]

    return entries


def extract_floor_failures(entry: Dict[str, Any]) -> List[str]:
    """
    Extract floor failures from a ledger entry.

    Handles various entry formats (zkpc_receipt, ledger_entry, incident).
    """
    failures = []

    # Direct floor_failures field
    if "floor_failures" in entry:
        failures.extend(entry["floor_failures"])

    # Metrics-based failure detection
    if "metrics" in entry:
        metrics = entry["metrics"]
        # F1: Amanah
        if metrics.get("amanah") is False:
            failures.append("F1: Amanah")
        # F2: Truth
        if metrics.get("truth", 1.0) < 0.99:
            failures.append("F2: Truth")
        # F3: Peace²
        if metrics.get("peace_squared", 1.0) < 1.0:
            failures.append("F3: Peace²")
        # F4: DeltaS
        if metrics.get("delta_s", 0) < 0.0:
            failures.append("F4: DeltaS")
        # F5: Tri-Witness
        if metrics.get("tri_witness", 1.0) < 0.95:
            failures.append("F5: Tri-Witness")
        # F6: kappa_r
        if metrics.get("kappa_r", 1.0) < 0.95:
            failures.append("F6: Kr")
        # F7: omega_0
        omega = metrics.get("omega_0", 0.04)
        if omega < 0.03 or omega > 0.05:
            failures.append("F7: Omega₀")

    # Receipt-based failure detection
    if "receipt" in entry:
        receipt = entry["receipt"]
        if "metrics" in receipt:
            rm = receipt["metrics"]
            if rm.get("amanah") == "VOID" or rm.get("amanah") is False:
                failures.append("F1: Amanah")

    return failures


def analyze_entries(entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze ledger entries for floor pass rates and hot zones.

    Returns:
        Analysis dict with stats, floor_pass_rates, hot_zones, verdicts
    """
    total = len(entries)
    if total == 0:
        return {"error": "No entries to analyze"}

    verdict_counts: Counter = Counter()
    floor_failures: Counter = Counter()
    floor_checks: Counter = Counter()
    risk_levels: Counter = Counter()
    entry_types: Counter = Counter()

    for entry in entries:
        # Count entry types
        entry_type = entry.get("type", "unknown")
        entry_types[entry_type] += 1

        # Count verdicts
        verdict = entry.get("verdict") or entry.get("receipt", {}).get("verdict")
        if verdict:
            verdict_counts[verdict] += 1

        # Count risk levels from genius_law
        genius = entry.get("genius_law", {})
        risk = genius.get("risk_level")
        if risk:
            risk_levels[risk] += 1

        # Extract and count floor failures
        failures = extract_floor_failures(entry)
        for failure in failures:
            floor_failures[failure] += 1

        # Track which floors were checked (for pass rate calculation)
        for i in range(1, 10):
            floor_checks[f"F{i}"] += 1

    # Calculate pass rates
    floor_pass_rates = {}
    for floor, checks in floor_checks.items():
        failures = floor_failures.get(f"{floor}: {_floor_name(floor)}", 0)
        # Also check alternate naming
        for key in floor_failures:
            if key.startswith(floor):
                failures = floor_failures[key]
                break
        floor_pass_rates[floor] = {
            "checked": checks,
            "failed": failures,
            "pass_rate": 1.0 - (failures / checks) if checks > 0 else 1.0,
        }

    # Hot zones (top 5 failures)
    hot_zones = floor_failures.most_common(5)

    return {
        "total_entries": total,
        "entry_types": dict(entry_types),
        "verdicts": dict(verdict_counts),
        "risk_levels": dict(risk_levels),
        "floor_pass_rates": floor_pass_rates,
        "hot_zones": hot_zones,
    }


def _floor_name(floor_id: str) -> str:
    """Map floor ID to name."""
    names = {
        "F1": "Amanah",
        "F2": "Truth",
        "F3": "Tri-Witness",
        "F4": "DeltaS",
        "F5": "Peace²",
        "F6": "Kr",
        "F7": "Omega₀",
        "F8": "G",
        "F9": "C_dark",
    }
    return names.get(floor_id, "Unknown")


def print_report(analysis: Dict[str, Any], violations_only: bool = False) -> None:
    """Print formatted analysis report."""
    print("\n" + "=" * 60)
    print("  COOLING LEDGER FLOOR ANALYSIS")
    print("=" * 60)

    print(f"\nTotal Entries Analyzed: {analysis['total_entries']}")

    # Entry types
    print("\n📊 Entry Types:")
    for etype, count in analysis.get("entry_types", {}).items():
        print(f"   {etype}: {count}")

    # Verdicts
    print("\n⚖️ Verdicts:")
    for verdict, count in sorted(analysis.get("verdicts", {}).items()):
        pct = count / analysis['total_entries'] * 100
        print(f"   {verdict}: {count} ({pct:.1f}%)")

    # Risk levels
    if analysis.get("risk_levels"):
        print("\n⚠️ Risk Levels:")
        for risk, count in sorted(analysis.get("risk_levels", {}).items()):
            print(f"   {risk}: {count}")

    # Floor pass rates
    print("\n🏛️ Floor Pass Rates:")
    for floor, stats in sorted(analysis.get("floor_pass_rates", {}).items()):
        pct = stats["pass_rate"] * 100
        bar = "█" * int(pct / 10) + "░" * (10 - int(pct / 10))
        status = "✅" if pct == 100 else "⚠️" if pct >= 95 else "❌"
        print(f"   {floor} ({_floor_name(floor)}): {bar} {pct:.1f}% {status}")

    # Hot zones
    if analysis.get("hot_zones"):
        print("\n🔥 Hot Zones (Frequent Failures):")
        for failure, count in analysis["hot_zones"]:
            print(f"   [{count}x] {failure}")

    print("\n" + "=" * 60)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze Cooling Ledger for floor violations and trends."
    )
    parser.add_argument(
        "--ledger",
        type=Path,
        default=DEFAULT_LEDGER_PATH,
        help="Path to JSONL ledger file",
    )
    parser.add_argument(
        "--last",
        type=int,
        default=None,
        help="Analyze only the last N entries",
    )
    parser.add_argument(
        "--violations-only",
        action="store_true",
        help="Only show entries with violations",
    )
    parser.add_argument(
        "--floor",
        type=str,
        default=None,
        help="Filter by specific floor (e.g., F1, F2)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON instead of formatted report",
    )

    args = parser.parse_args()

    # Load entries
    entries = load_ledger_entries(args.ledger, args.last)
    if not entries:
        print("No entries to analyze.")
        return

    # Filter by violations if requested
    if args.violations_only:
        entries = [e for e in entries if extract_floor_failures(e)]

    # Filter by floor if requested
    if args.floor:
        floor_filter = args.floor.upper()
        entries = [
            e for e in entries
            if any(floor_filter in f for f in extract_floor_failures(e))
        ]

    # Analyze
    analysis = analyze_entries(entries)

    if "error" in analysis:
        print(f"ERROR: {analysis['error']}")
        return

    # Output
    if args.json:
        print(json.dumps(analysis, indent=2))
    else:
        print_report(analysis, args.violations_only)


if __name__ == "__main__":
    main()
