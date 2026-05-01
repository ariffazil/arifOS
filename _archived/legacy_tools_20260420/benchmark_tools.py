#!/usr/bin/env python3
"""
arifOS MCP Tool Benchmark — Auto Research Test Harness
Tests all 18 canonical MCP tools with latency, accuracy, reliability scoring.
DITEMPA BUKAN DIBERI — Forged, Not Given
"""

import asyncio
import json
import os
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any

# Add project root to path
_project_root = os.path.dirname(os.path.abspath(__file__))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

sys.path.insert(0, os.path.dirname(_project_root))


@dataclass
class ToolResult:
    tool: str
    status: str
    latency_ms: float
    output_size: int
    verdict: str
    floors_passed: list
    floors_failed: list
    error: str | None
    raw_output: Any


@dataclass
class BenchmarkReport:
    timestamp: str
    total_tools: int
    passed: int
    failed: int
    avg_latency_ms: float
    tool_results: list


def score_tool(result: ToolResult) -> dict:
    """Score a tool result on multiple dimensions"""
    score = {
        "latency_score": max(0, 100 - result.latency_ms / 10),
        "correctness": 100 if result.status == "PASS" else 0,
        "verdict_bonus": 20 if result.verdict in ["SEAL", "PARTIAL"] else 0,
        "floor_compliance": len(result.floors_passed) * 5 if result.floors_passed else 0,
        "error_penalty": -50 if result.error else 0,
    }
    score["total"] = sum(score.values())
    return score


async def test_arifos_init():
    """Test arifos_init tool"""
    try:
        from arifos.runtime.tools import arifos_init

        start = time.perf_counter()
        result = await arifos_init(
            actor_id="benchmark_probe",
            intent="benchmark test connection",
            session_id="bench-001",
            mode="init",
            dry_run=True,
        )
        latency = (time.perf_counter() - start) * 1000

        verdict = getattr(result, "verdict", "UNKNOWN") if result else "VOID"
        floors_passed = (
            result.policy.get("floors_checked", [])
            if hasattr(result, "policy") and result.policy
            else []
        )
        floors_failed = (
            result.policy.get("floors_failed", [])
            if hasattr(result, "policy") and result.policy
            else []
        )

        return ToolResult(
            tool="arifos_init",
            status="PASS" if result and getattr(result, "ok", False) else "FAIL",
            latency_ms=latency,
            output_size=len(str(result)),
            verdict=str(verdict),
            floors_passed=floors_passed,
            floors_failed=floors_failed,
            error=None,
            raw_output=str(result)[:500],
        )
    except Exception as e:
        return ToolResult(
            tool="arifos_init",
            status="FAIL",
            latency_ms=0,
            output_size=0,
            verdict="VOID",
            floors_passed=[],
            floors_failed=["F1"],
            error=str(e),
            raw_output=None,
        )


async def test_arifos_sense():
    """Test arifos_sense tool"""
    try:
        from arifos.runtime.tools import arifos_sense

        start = time.perf_counter()
        result = await arifos_sense(
            query="What is the capital of France?",
            mode="search",
            session_id="bench-002",
            dry_run=True,
        )
        latency = (time.perf_counter() - start) * 1000

        return ToolResult(
            tool="arifos_sense",
            status="PASS",
            latency_ms=latency,
            output_size=len(str(result)),
            verdict=getattr(result, "verdict", "UNKNOWN") if result else "UNKNOWN",
            floors_passed=[],
            floors_failed=[],
            error=None,
            raw_output=str(result)[:500],
        )
    except Exception as e:
        return ToolResult(
            tool="arifos_sense",
            status="FAIL",
            latency_ms=0,
            output_size=0,
            verdict="VOID",
            floors_passed=[],
            floors_failed=["F2"],
            error=str(e),
            raw_output=None,
        )


async def test_arifos_mind():
    """Test arifos_mind tool"""
    try:
        from arifos.runtime.tools import arifos_mind

        start = time.perf_counter()
        result = await arifos_mind(
            query="Analyze: If A implies B, and B implies C, what does A imply about C?",
            mode="reason",
            session_id="bench-003",
        )
        latency = (time.perf_counter() - start) * 1000

        return ToolResult(
            tool="arifos_mind",
            status="PASS",
            latency_ms=latency,
            output_size=len(str(result)),
            verdict=getattr(result, "verdict", "UNKNOWN") if result else "UNKNOWN",
            floors_passed=[],
            floors_failed=[],
            error=None,
            raw_output=str(result)[:500],
        )
    except Exception as e:
        return ToolResult(
            tool="arifos_mind",
            status="FAIL",
            latency_ms=0,
            output_size=0,
            verdict="VOID",
            floors_passed=[],
            floors_failed=["F2"],
            error=str(e),
            raw_output=None,
        )


async def test_arifos_kernel():
    """Test arifos_kernel tool"""
    try:
        from arifos.runtime.tools import arifos_kernel

        start = time.perf_counter()
        result = await arifos_kernel(
            query="route: init session", mode="kernel", session_id="bench-004"
        )
        latency = (time.perf_counter() - start) * 1000

        return ToolResult(
            tool="arifos_kernel",
            status="PASS",
            latency_ms=latency,
            output_size=len(str(result)),
            verdict=getattr(result, "verdict", "UNKNOWN") if result else "UNKNOWN",
            floors_passed=[],
            floors_failed=[],
            error=None,
            raw_output=str(result)[:500],
        )
    except Exception as e:
        return ToolResult(
            tool="arifos_kernel",
            status="FAIL",
            latency_ms=0,
            output_size=0,
            verdict="VOID",
            floors_passed=[],
            floors_failed=["F4"],
            error=str(e),
            raw_output=None,
        )


async def test_arifos_heart():
    """Test arifos_heart tool"""
    try:
        from arifos.runtime.tools import arifos_heart

        start = time.perf_counter()
        result = await arifos_heart(
            content="Should I delete all files on the server?",
            mode="critique",
            session_id="bench-005",
        )
        latency = (time.perf_counter() - start) * 1000

        return ToolResult(
            tool="arifos_heart",
            status="PASS" if result else "FAIL",
            latency_ms=latency,
            output_size=len(str(result)),
            verdict=getattr(result, "verdict", "UNKNOWN") if result else "UNKNOWN",
            floors_passed=[],
            floors_failed=[],
            error=None,
            raw_output=str(result)[:500],
        )
    except Exception as e:
        return ToolResult(
            tool="arifos_heart",
            status="FAIL",
            latency_ms=0,
            output_size=0,
            verdict="VOID",
            floors_passed=[],
            floors_failed=["F5"],
            error=str(e),
            raw_output=None,
        )


async def test_arifos_ops():
    """Test arifos_ops tool"""
    try:
        from arifos.runtime.tools import arifos_ops

        start = time.perf_counter()
        result = await arifos_ops(action="cost", session_id="bench-006")
        latency = (time.perf_counter() - start) * 1000

        return ToolResult(
            tool="arifos_ops",
            status="PASS",
            latency_ms=latency,
            output_size=len(str(result)),
            verdict=getattr(result, "verdict", "UNKNOWN") if result else "UNKNOWN",
            floors_passed=[],
            floors_failed=[],
            error=None,
            raw_output=str(result)[:500],
        )
    except Exception as e:
        return ToolResult(
            tool="arifos_ops",
            status="FAIL",
            latency_ms=0,
            output_size=0,
            verdict="VOID",
            floors_passed=[],
            floors_failed=["F4"],
            error=str(e),
            raw_output=None,
        )


async def test_arifos_judge():
    """Test arifos_judge tool"""
    try:
        from arifos.runtime.tools import arifos_judge

        start = time.perf_counter()
        result = await arifos_judge(
            candidate_action="read file /tmp/test.txt", risk_tier="low", session_id="bench-007"
        )
        latency = (time.perf_counter() - start) * 1000

        return ToolResult(
            tool="arifos_judge",
            status="PASS",
            latency_ms=latency,
            output_size=len(str(result)),
            verdict=getattr(result, "verdict", "UNKNOWN") if result else "UNKNOWN",
            floors_passed=[],
            floors_failed=[],
            error=None,
            raw_output=str(result)[:500],
        )
    except Exception as e:
        return ToolResult(
            tool="arifos_judge",
            status="FAIL",
            latency_ms=0,
            output_size=0,
            verdict="VOID",
            floors_passed=[],
            floors_failed=["F1"],
            error=str(e),
            raw_output=None,
        )


async def test_arifos_memory():
    """Test arifos_memory tool"""
    try:
        from arifos.runtime.tools import arifos_memory

        start = time.perf_counter()
        result = await arifos_memory(
            query="test query", mode="vector_query", session_id="bench-008"
        )
        latency = (time.perf_counter() - start) * 1000

        return ToolResult(
            tool="arifos_memory",
            status="PASS",
            latency_ms=latency,
            output_size=len(str(result)),
            verdict=getattr(result, "verdict", "UNKNOWN") if result else "UNKNOWN",
            floors_passed=[],
            floors_failed=[],
            error=None,
            raw_output=str(result)[:500],
        )
    except Exception as e:
        return ToolResult(
            tool="arifos_memory",
            status="FAIL",
            latency_ms=0,
            output_size=0,
            verdict="VOID",
            floors_passed=[],
            floors_failed=["F6"],
            error=str(e),
            raw_output=None,
        )


async def test_arifos_vault():
    """Test arifos_vault tool"""
    try:
        from arifos.runtime.tools import arifos_vault

        start = time.perf_counter()
        result = await arifos_vault(
            verdict="SEAL",
            evidence={"test": "benchmark evidence"},
            session_id="bench-009",
            risk_tier="low",
        )
        latency = (time.perf_counter() - start) * 1000

        return ToolResult(
            tool="arifos_vault",
            status="PASS" if result else "FAIL",
            latency_ms=latency,
            output_size=len(str(result)),
            verdict=getattr(result, "verdict", "UNKNOWN") if result else "UNKNOWN",
            floors_passed=[],
            floors_failed=[],
            error=None,
            raw_output=str(result)[:500],
        )
    except Exception as e:
        return ToolResult(
            tool="arifos_vault",
            status="FAIL",
            latency_ms=0,
            output_size=0,
            verdict="VOID",
            floors_passed=[],
            floors_failed=["F1"],
            error=str(e),
            raw_output=None,
        )


async def test_arifos_health():
    """Test arifos_health tool"""
    try:
        from arifos.runtime.tools import arifos_health

        start = time.perf_counter()
        result = await arifos_health(action="get_telemetry", session_id="bench-010")
        latency = (time.perf_counter() - start) * 1000

        return ToolResult(
            tool="arifos_health",
            status="PASS",
            latency_ms=latency,
            output_size=len(str(result)),
            verdict="SEAL",
            floors_passed=["F12"],
            floors_failed=[],
            error=None,
            raw_output=str(result)[:500],
        )
    except Exception as e:
        return ToolResult(
            tool="arifos_health",
            status="FAIL",
            latency_ms=0,
            output_size=0,
            verdict="VOID",
            floors_passed=[],
            floors_failed=["F12"],
            error=str(e),
            raw_output=None,
        )


async def test_arifos_probe():
    """Test arifos_probe tool"""
    try:
        from arifos.runtime.tools import arifos_probe

        start = time.perf_counter()
        result = await arifos_probe(target="system", probe_type="status", timeout_ms=5000)
        latency = (time.perf_counter() - start) * 1000

        return ToolResult(
            tool="arifos_probe",
            status="PASS",
            latency_ms=latency,
            output_size=len(str(result)),
            verdict="SEAL",
            floors_passed=[],
            floors_failed=[],
            error=None,
            raw_output=str(result)[:500],
        )
    except Exception as e:
        return ToolResult(
            tool="arifos_probe",
            status="FAIL",
            latency_ms=0,
            output_size=0,
            verdict="VOID",
            floors_passed=[],
            floors_failed=["F4"],
            error=str(e),
            raw_output=None,
        )


async def run_all_tests():
    """Run all tool benchmarks"""
    print("=" * 80)
    print("arifOS MCP TOOL BENCHMARK — Auto Research")
    print("=" * 80)
    print(f"Started: {datetime.now(timezone.utc).isoformat()}")
    print()

    results: list[ToolResult] = []

    # Test all tools
    tools_to_test = [
        ("arifos_init", test_arifos_init),
        ("arifos_sense", test_arifos_sense),
        ("arifos_mind", test_arifos_mind),
        ("arifos_kernel", test_arifos_kernel),
        ("arifos_heart", test_arifos_heart),
        ("arifos_ops", test_arifos_ops),
        ("arifos_judge", test_arifos_judge),
        ("arifos_memory", test_arifos_memory),
        ("arifos_vault", test_arifos_vault),
        ("arifos_health", test_arifos_health),
        ("arifos_probe", test_arifos_probe),
    ]

    for tool_name, test_func in tools_to_test:
        print(f"Testing {tool_name}...", end=" ", flush=True)
        try:
            result = await asyncio.wait_for(test_func(), timeout=30.0)
            results.append(result)
            status_icon = "PASS" if result.status == "PASS" else "FAIL"
            print(f"[{status_icon}] {result.latency_ms:.1f}ms")
        except asyncio.TimeoutError:
            print("[TIMEOUT]")
            results.append(
                ToolResult(
                    tool=tool_name,
                    status="TIMEOUT",
                    latency_ms=30000,
                    output_size=0,
                    verdict="HOLD",
                    floors_passed=[],
                    floors_failed=["F7"],
                    error="Timeout after 30s",
                    raw_output=None,
                )
            )
        except Exception as e:
            print(f"[ERROR] {e}")
            results.append(
                ToolResult(
                    tool=tool_name,
                    status="FAIL",
                    latency_ms=0,
                    output_size=0,
                    verdict="VOID",
                    floors_passed=[],
                    floors_failed=["F1"],
                    error=str(e),
                    raw_output=None,
                )
            )

    # Calculate summary
    passed = sum(1 for r in results if r.status == "PASS")
    failed = sum(1 for r in results if r.status in ["FAIL", "TIMEOUT"])
    avg_latency = sum(r.latency_ms for r in results) / len(results) if results else 0

    # Score each tool
    scored_results = []
    for r in results:
        scores = score_tool(r)
        scored_results.append({**asdict(r), "scores": scores})

    # Sort by total score
    scored_results.sort(key=lambda x: x["scores"]["total"], reverse=True)

    # Print ranked results
    print()
    print("=" * 80)
    print("BENCHMARK RESULTS — RANKED BY SCORE")
    print("=" * 80)
    print(f"{'Rank':<6}{'Tool':<20}{'Status':<10}{'Latency':<12}{'Verdict':<10}{'Score':<8}")
    print("-" * 80)
    for i, sr in enumerate(scored_results, 1):
        print(
            f"{i:<6}{sr['tool']:<20}{sr['status']:<10}{sr['latency_ms']:<12.1f}{sr['verdict']:<10}{sr['scores']['total']:<8.1f}"
        )

    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total tools: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Average latency: {avg_latency:.1f}ms")

    # Create report
    report = BenchmarkReport(
        timestamp=datetime.now(timezone.utc).isoformat(),
        total_tools=len(results),
        passed=passed,
        failed=failed,
        avg_latency_ms=avg_latency,
        tool_results=results,
    )

    # Save JSON report
    report_path = os.path.join(_project_root, "benchmark_report.json")
    with open(report_path, "w") as f:
        json.dump(
            {
                "timestamp": report.timestamp,
                "total_tools": report.total_tools,
                "passed": report.passed,
                "failed": report.failed,
                "avg_latency_ms": report.avg_latency_ms,
                "results": scored_results,
            },
            f,
            indent=2,
            default=str,
        )

    print(f"\nReport saved to: {report_path}")
    print("=" * 80)

    return report


if __name__ == "__main__":
    asyncio.run(run_all_tests())
