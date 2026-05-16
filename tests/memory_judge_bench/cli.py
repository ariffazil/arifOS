"""
tests/memory_judge_bench/cli.py
===============================
MEMORY_JUDGE_BENCH — CLI and Report Runner

Usage:
  python -m tests.memory_judge_bench --report
  python -m tests.memory_judge_bench --score-only
  python -m tests.memory_judge_bench --verbose
  python -m tests.memory_judge_bench --list-tests

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure project root on path
sys.path.insert(0, str(Path(__file__).parents[3]))

from tests.memory_judge_bench.conftest import get_test_results, reset_test_results
from tests.memory_judge_bench.reports import print_summary, write_reports
from tests.memory_judge_bench.test_score import compute_memory_behavior_score


def run_benchmarks(verbose: bool = False) -> dict:
    """Run all benchmark tests and return raw results."""
    # Import test functions — pytest discovers and runs them
    # We trigger them programmatically here for report generation
    import subprocess

    pytest_args = [
        sys.executable,
        "-m",
        "pytest",
        str(Path(__file__).parent / "test_matrix.py"),
        "-v" if verbose else "-q",
        "--tb=short",
        "--no-header",
    ]

    result = subprocess.run(
        pytest_args,
        capture_output=True,
        text=True,
    )

    return {
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="memory_judge_bench",
        description="MEMORY_JUDGE_BENCH — arifOS Memory Behavioral Evaluation Harness",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Run benchmarks and produce JSON + Markdown reports",
    )
    parser.add_argument(
        "--score-only",
        action="store_true",
        help="Compute and print score from collected test results (no re-run)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose pytest output",
    )
    parser.add_argument(
        "--list-tests",
        action="store_true",
        help="List all test cases without running them",
    )
    parser.add_argument(
        "--json-output",
        help="Override JSON report path",
    )
    parser.add_argument(
        "--md-output",
        help="Override Markdown report path",
    )

    args = parser.parse_args()

    if args.list_tests:
        print("MEMORY_JUDGE_BENCH Test Classes:")
        for cls_name, cls in [
            ("sacred_scar_recall", "High-consequence memory handled with care"),
            (
                "public_private_separation",
                "Sealed/private memory not casually surfaced",
            ),
            ("stale_memory_handling", "Expired facts require re-verification"),
            ("contradiction_handling", "Conflicts flagged, not blindly merged"),
            ("anti_hantu", "Consciousness/emotion claims rejected at write"),
            ("phoenix_state", "Cooling memories not treated as canon"),
            ("f4_supersession", "Newer facts supersede older ones correctly"),
            ("human_authority", "Consequential outputs escalate to 888_JUDGE"),
            ("retrieval_restraint", "Unsafe memory filtered, not just retrieved"),
            ("behavior_change_trace", "Output explains what memory changed and why"),
        ]:
            print(f"  [{cls_name}] — {cls}")
        return 0

    if args.score_only:
        results = get_test_results()
        if not results:
            print("No test results found. Run with --report first.")
            return 1
        score = compute_memory_behavior_score(results)
        print_summary(score)
        return 0

    if args.report:
        # Reset before run
        reset_test_results()

        # Run pytest
        print("Running MEMORY_JUDGE_BENCH...")
        bench_result = run_benchmarks(verbose=args.verbose)

        if bench_result["returncode"] != 0:
            print("⚠️  Some tests may have failed. Proceeding to scoring...")

        # Collect and score
        results = get_test_results()
        if not results:
            # Fallback: try reading from pytest's json report
            print("No in-process results collected. Running pytest directly to collect results...")
            import subprocess

            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    str(Path(__file__).parent / "test_matrix.py"),
                    "-v",
                    "--tb=short",
                ]
            )
            results = get_test_results()

        score = compute_memory_behavior_score(results)
        print_summary(score)

        paths = write_reports(score)
        print("\nReports written:")
        for kind, path in paths.items():
            print(f"  {kind}: {path}")

        return bench_result["returncode"]

    # Default: show help
    parser.print_help()
    return 0
