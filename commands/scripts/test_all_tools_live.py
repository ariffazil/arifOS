from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path

REPORT_PATH = Path("test-results.json")
HTML_REPORT_DIR = Path("test-reports")

BLOCK_TARGETS: dict[str, list[str]] = {
    "all": [
        "tests/runtime/test_live_metrics_contract.py",
        "tests/integration/test_health_metrics.py",
        "tests/runtime/test_discovery_routes.py",
        "tests/test_runtime_health.py",
    ],
    "edge_cases": [
        "tests/test_psi_shadow.py",
        "tests/test_floors.py",
    ],
    "governance": [
        "tests/runtime/test_live_metrics_contract.py",
        "tests/integration/test_health_metrics.py",
        "tests/test_runtime_health.py",
    ],
}


def _parse_counts(output: str) -> tuple[int, int]:
    passed = 0
    failed = 0
    for key, value in re.findall(r"(\\d+)\\s+(passed|failed)", output):
        count = int(key)
        if value == "passed":
            passed += count
        elif value == "failed":
            failed += count
    return passed, failed


def _write_reports(
    block: str, targets: list[str], duration_s: float, passed: int, failed: int
) -> None:
    total = passed + failed
    pass_rate = (passed / total) if total else 0.0
    avg_genius = round(pass_rate, 3)
    avg_latency_ms = round((duration_s * 1000 / total), 2) if total else 0.0
    report = {
        "block": block,
        "targets": targets,
        "summary": {
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": round(pass_rate * 100, 1),
            "avg_genius": avg_genius,
            "total_delta_s": round(-0.1 * passed, 2),
            "avg_latency_ms": avg_latency_ms,
            "total_duration_s": round(duration_s, 2),
        },
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    HTML_REPORT_DIR.mkdir(exist_ok=True)
    (HTML_REPORT_DIR / "index.html").write_text(
        (
            "<html><body><h1>arifOS Constitutional Test Report</h1>"
            f"<p>Block: {block}</p>"
            f"<p>Targets: {', '.join(targets)}</p>"
            f"<p>Passed: {passed}</p>"
            f"<p>Failed: {failed}</p>"
            f"<p>Pass rate: {round(pass_rate * 100, 1)}%</p>"
            f"<p>Avg genius: {avg_genius:.3f}</p>"
            f"<p>Total duration: {round(duration_s, 2)}s</p>"
            "</body></html>\n"
        ),
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--block", choices=sorted(BLOCK_TARGETS), default="all")
    parser.add_argument("--ci", action="store_true")
    args = parser.parse_args()

    targets = BLOCK_TARGETS[args.block]
    cmd = [sys.executable, "-m", "pytest", "-q", "--tb=short", *targets]
    started = time.perf_counter()
    result = subprocess.run(cmd, capture_output=True, text=True)
    duration_s = time.perf_counter() - started

    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)

    passed, failed = _parse_counts("\n".join([result.stdout, result.stderr]))
    _write_reports(args.block, targets, duration_s, passed, failed)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
