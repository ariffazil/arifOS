#!/usr/bin/env python3
"""
test_all_tools_live.py — Live Constitutional Test Runner (v2)

Provides a CLI wrapper around the production-grade pytest suite for arifOS MCP.
Enforces 13 stationary floors and generates constitutional metrics.

Usage:
    python test_all_tools_live.py              # Run all tests
    python test_all_tools_live.py --block governance  # Run specific block
    python test_all_tools_live.py --only f12,f9       # Run specific tests
    python test_all_tools_live.py --ci                # CI mode (JSON output)
"""

import argparse
import subprocess
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="🔥 arifOS MCP — Constitutional Test Runner v2",
        epilog="Ditempa Bukan Diberi — Forged, Not Given",
    )
    parser.add_argument(
        "--block",
        type=str,
        choices=["governance", "triad", "edge_cases", "sensory", "pipeline_full"],
        help="Specific test block to run",
    )
    parser.add_argument(
        "--only",
        type=str,
        help="Comma-separated test names to run (e.g., f12,f9,hold_888)",
    )
    parser.add_argument(
        "--ci",
        action="store_true",
        help="CI mode: JSON output only, minimal console noise",
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Run tests in parallel using pytest-xdist (requires: pip install pytest-xdist)",
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Generate coverage report (requires: pip install pytest-cov)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Verbose output (pytest -vv)",
    )

    args = parser.parse_args()

    # Path to tests/mcp_live
    tests_dir = Path(__file__).parent / "tests" / "mcp_live"

    pytest_args = [sys.executable, "-m", "pytest"]

    # Determine test path
    if args.block:
        # Specific block: tests/mcp_live/test_{block}.py
        pytest_args.append(str(tests_dir / f"test_{args.block}.py"))
    else:
        # All tests in tests/mcp_live
        pytest_args.append(str(tests_dir))

    # Keyword filtering
    if args.only:
        keywords = " or ".join(args.only.split(","))
        pytest_args.extend(["-k", keywords])

    # CI mode
    if args.ci:
        # Quiet mode
        pytest_args.extend(["-q", "--tb=short"])
        # Prefer pytest-json-report when available
        try:
            import pytest_jsonreport  # noqa: F401

            pytest_args.extend(["--json-report", "--json-report-file=test-results.json"])
        except ImportError:
            pass  # No JSON artifact plugin installed
    else:
        # Human-readable mode
        pytest_args.append("-v" if not args.verbose else "-vv")
        pytest_args.append("--tb=short")

    # Parallel execution
    if args.parallel:
        try:
            import xdist  # noqa: F401

            pytest_args.extend(["-n", "auto"])
        except ImportError:
            print("⚠️  pytest-xdist not installed. Run: pip install pytest-xdist")
            print("Falling back to sequential execution.\n")

    # Coverage
    if args.coverage:
        pytest_args.extend(
            [
                "--cov=arifosmcp.transport",
                "--cov=arifosmcp.intelligence",
                "--cov-report=html",
                "--cov-report=term",
            ]
        )

    # Always generate HTML report (if pytest-html is available)
    try:
        import pytest_html  # noqa: F401

        pytest_args.append("--html=test-reports/arifos-live-report.html")
        pytest_args.append("--self-contained-html")
    except ImportError:
        pass

    print(f"🔥 Running Constitutional Tests: {' '.join(pytest_args)}")
    print()

    result = subprocess.run(pytest_args)

    # Post-run summary
    if args.ci and Path("test-results.json").exists():
        print("\n📊 Test results written to: test-results.json")
        print("✓ Upload this file to CI artifacts for analysis")

    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
