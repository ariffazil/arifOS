#!/usr/bin/env python3
"""
arifOS Latency Benchmark — p50/p95 for all 7 canonical tools.
Blind Spot #8 seal: operational reality > impressive documentation.
Run: python3 benchmarks/latency_benchmark.py
"""
import time
import json
import statistics
import urllib.request
from typing import Any

BASE_URL = "http://localhost:8088/mcp"
RUNS = 10


def mcp_call(method: str, params: dict[str, Any]) -> tuple[dict, float]:
    """Make MCP JSON-RPC call and return (result, elapsed_ms)."""
    opener = urllib.request.build_opener(urllib.request.HTTPRedirectHandler())
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(
        BASE_URL,
        data=payload,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    t0 = time.perf_counter()
    resp = opener.open(req, timeout=30)
    result = json.loads(resp.read())
    elapsed_ms = (time.perf_counter() - t0) * 1000
    return result, elapsed_ms


def bench(name: str, method: str, params: dict, runs: int = RUNS) -> dict:
    """Run N iterations and return p50/p95/min/max."""
    times = []
    errors = 0
    for _ in range(runs):
        try:
            _, ms = mcp_call(method, params)
            times.append(ms)
        except Exception:
            errors += 1
    if not times:
        return {"tool": name, "error": "all calls failed", "error_count": errors}
    times.sort()
    p50 = statistics.median(times)
    p95 = times[int(len(times) * 0.95)] if len(times) >= 20 else times[-1]
    return {
        "tool": name,
        "runs": runs,
        "errors": errors,
        "p50_ms": round(p50, 1),
        "p95_ms": round(p95, 1),
        "min_ms": round(times[0], 1),
        "max_ms": round(times[-1], 1),
    }


def main():
    print("arifOS Latency Benchmark")
    print("=" * 50)

    # 1. Get a session_id first
    print("\n[0] Bootstrapping session...")
    try:
        result, ms = mcp_call("tools/call", {
            "name": "arif_init",
            "arguments": {"actor_id": "benchmark_runner", "mode": "light"}
        })
        content = result.get("result", {}).get("content", [{}])
        session_id = None
        if content and isinstance(content[0], dict):
            text = content[0].get("text", "{}")
            try:
                data = json.loads(text)
                session_id = data.get("result", {}).get("session_id") or data.get("session_id")
            except Exception:
                pass
        print(f"  Init: {ms:.0f}ms | session_id: {session_id}")
    except Exception as e:
        print(f"  Init failed: {e}")
        session_id = None

    results = []

    # 2. Benchmark each canonical tool
    benchmarks = [
        ("arif_init (light)", "tools/call", {
            "name": "arif_init",
            "arguments": {"actor_id": "benchmark_runner", "mode": "light"}
        }),
        ("arif_route", "tools/call", {
            "name": "arif_route",
            "arguments": {
                "intent": "analyze portfolio risk",
                "session_id": session_id or "",
            }
        }),
        ("arif_observe", "tools/call", {
            "name": "arif_observe",
            "arguments": {
                "mode": "ping",
                "session_id": session_id or "",
            }
        }),
        ("arif_think", "tools/call", {
            "name": "arif_think",
            "arguments": {
                "question": "What is 2+2?",
                "mode": "fast",
                "session_id": session_id or "",
            }
        }),
        ("arif_judge", "tools/call", {
            "name": "arif_judge",
            "arguments": {
                "actor": "benchmark_runner",
                "intent": "read file",
                "requested_capability": "read",
                "mode": "intercept",
                "session_id": session_id or "",
            }
        }),
        ("arif_seal (dry_run)", "tools/call", {
            "name": "arif_seal",
            "arguments": {
                "mode": "dry_run",
                "payload": "benchmark test",
                "session_id": session_id or "",
            }
        }),
        ("arif_canary (ping)", "tools/call", {
            "name": "arif_canary",
            "arguments": {"mode": "ping"}
        }),
    ]

    for label, method, params in benchmarks:
        print(f"\n[bench] {label} ({RUNS} runs)...")
        r = bench(label, method, params)
        results.append(r)
        if "error" in r:
            print(f"  ERROR: {r['error']}")
        else:
            print(f"  p50={r['p50_ms']}ms  p95={r['p95_ms']}ms  min={r['min_ms']}ms  max={r['max_ms']}ms  errors={r['errors']}")

    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"{'Tool':<30} {'p50':>8} {'p95':>8} {'errors':>8}")
    for r in results:
        if "error" not in r:
            print(f"{r['tool']:<30} {r['p50_ms']:>7}ms {r['p95_ms']:>7}ms {r['errors']:>8}")

    # Write results
    output_path = "benchmarks/latency_results.json"
    with open(output_path, "w") as f:
        json.dump({
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "base_url": BASE_URL,
            "runs_per_tool": RUNS,
            "results": results,
        }, f, indent=2)
    print(f"\nResults written to {output_path}")


if __name__ == "__main__":
    main()
