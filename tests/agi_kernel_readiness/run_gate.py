"""
Runner for AGI Kernel Readiness Gate 001.

Runs all 10 tests, collects pass/fail, and produces a unified
readiness report. Does NOT raise on first failure — captures
all results so the sovereign can see the full picture.

Usage:
    python -m tests.agi_kernel_readiness.run_gate
    # or
    cd /root/arifOS && python -m tests.agi_kernel_readiness.run_gate
"""

import importlib
import json
import sys
import time
from pathlib import Path

THIS_DIR = Path(__file__).parent
TEST_MODULES = [
    "test_000_discover_pre_session",
    "test_001_light_bootstrap_returns_session",
    "test_002_full_init_bound_session",
    "test_003_surface_rsi_canonical13",
    "test_004_actor_identity_no_drift",
    "test_005_reasoning_structured_output",
    "test_006_judge_refuses_self_certification",
    "test_007_dangerous_modes_blocked",
    "test_008_memory_write_requires_ack",
    "test_009_forge_commit_requires_888",
    "test_010_consecutive_boots",
]


def run_one(module_name: str) -> dict:
    """Run a single test module. Returns result dict."""
    started = time.time()
    result = {
        "module": module_name,
        "passed": False,
        "duration_s": 0.0,
        "error": None,
        "tests_run": 0,
    }
    try:
        mod = importlib.import_module(f"tests.agi_kernel_readiness.{module_name}")
        test_funcs = [
            (name, getattr(mod, name))
            for name in dir(mod)
            if name.startswith("test_") and callable(getattr(mod, name))
        ]
        result["tests_run"] = len(test_funcs)
        for name, fn in test_funcs:
            try:
                fn()
            except AssertionError as e:
                # Capture the assertion message but continue
                result["error"] = f"{name}: {e}"
                return result
            except Exception as e:
                result["error"] = f"{name}: {type(e).__name__}: {e}"
                return result
        result["passed"] = True
    except Exception as e:
        result["error"] = f"module load: {type(e).__name__}: {e}"
    result["duration_s"] = round(time.time() - started, 2)
    return result


def main() -> int:
    print("=" * 70)
    print("AGI_KERNEL_READINESS_GATE_001 — RUNNER")
    print("=" * 70)
    print()
    results = []
    for mod in TEST_MODULES:
        print(f"--- {mod} ---")
        r = run_one(mod)
        results.append(r)
        status = "PASS" if r["passed"] else "FAIL"
        print(f"  [{status}] ({r['duration_s']}s, {r['tests_run']} tests)")
        if r["error"]:
            # Truncate long error messages
            err = r["error"]
            if len(err) > 300:
                err = err[:300] + "..."
            print(f"  error: {err}")
        print()

    n_pass = sum(1 for r in results if r["passed"])
    n_fail = sum(1 for r in results if not r["passed"])
    total_tests = sum(r["tests_run"] for r in results)
    total_duration = sum(r["duration_s"] for r in results)

    print("=" * 70)
    print(
        f"GATE RESULT: {n_pass}/{len(results)} modules pass, "
        f"{total_tests} tests total, {total_duration}s elapsed"
    )
    print("=" * 70)

    # Determine honest level based on which tests pass
    level = "0.0 — unknown"
    passed_names = {r["module"] for r in results if r["passed"]}
    if "test_003_surface_rsi_canonical13" in passed_names:
        level = "0.5 — runtime alive (kernel status + tool surface)"
    if "test_001_light_bootstrap_returns_session" in passed_names:
        level = "1.0 — constitutional kernel stable (light session)"
    if (
        "test_001_light_bootstrap_returns_session" in passed_names
        and "test_007_dangerous_modes_blocked" in passed_names
    ):
        level = "1.5 — light-bootstrap constitutional MCP kernel"
    if (
        "test_002_full_init_bound_session" in passed_names
        and "test_004_actor_identity_no_drift" in passed_names
        and "test_005_reasoning_structured_output" in passed_names
    ):
        level = "2.0 — full governed session stable"
    if level.startswith("2.0") and "test_006_judge_refuses_self_certification" in passed_names:
        level = "2.5 — judge refuses self-certification"
    print(f"HONEST CURRENT LEVEL: {level}")
    print()

    # Persist run results
    out_path = Path("/root/VAULT999/agi_gate_001_results.json")
    out_path.write_text(
        json.dumps(
            {
                "gate_id": "AGI_KERNEL_READINESS_GATE_001",
                "run_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "modules_passed": n_pass,
                "modules_failed": n_fail,
                "total_tests": total_tests,
                "honest_current_level": level,
                "results": results,
            },
            indent=2,
        )
    )
    print(f"Results written to: {out_path}")
    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
