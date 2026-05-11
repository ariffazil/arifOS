"""
arifos_train.py — Editable test harness for arifOS E2E Autoresearch.
ONLY THIS FILE gets modified per experiment.

Pattern: karpathy/autoresearch train.py
Adaptation: MCP tool-chain E2E testing under constitutional governance

Usage: python arifos_train.py

DITEMPA BUKAN DIBERI — Testing is forged, not given.
"""

from __future__ import annotations
import json
import time
import sys

from arifos_prepare import (
    SCENARIOS,
    evaluate_score,
    TIME_BUDGET_SECONDS,
    ARIFOS_API_KEY,
    MCP_TOOL_TIMEOUT,
)


# ── Tool Call Executor ──────────────────────────────────────
def call_arifos_tool(tool_name: str, tool_input: dict) -> dict:
    """
    Calls a single arifOS MCP tool via subprocess.
    Replace this with your actual MCP transport (HTTP, stdio, etc.)
    """
    import urllib.request
    import urllib.error

    if not ARIFOS_API_KEY:
        raise RuntimeError("ARIFOS_API_KEY not in environment — abort")

    payload = json.dumps(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": tool_name, "arguments": tool_input},
        }
    ).encode()

    req = urllib.request.Request(
        "http://localhost:8080/mcp",
        data=payload,
        headers={
            "Authorization": f"Bearer {ARIFOS_API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=MCP_TOOL_TIMEOUT) as resp:
            return json.loads(resp.read())
    except Exception as e:
        return {"error": str(e)}


def parse_verdict(result: dict) -> tuple[str, list[str]]:
    """Extract verdict + triggered floors from tool result."""
    try:
        if "error" in result:
            return "ERROR", []
        content = result.get("content", [])
        if isinstance(content, list) and len(content) > 0:
            text = content[0].get("text", "{}")
            data = json.loads(text)
            return data.get("verdict", "UNKNOWN"), data.get("floors_triggered", [])
        return "UNKNOWN", []
    except Exception:
        return "ERROR", []


# ── Run Scenarios ──────────────────────────────────────────
def run_scenarios() -> list[dict]:
    """Run all scenarios and return list of result dicts."""
    results = []
    for scenario_id, spec in SCENARIOS.items():
        tool = spec["tool"]
        inp = spec["input"]
        expected_verdict = spec["expected_verdict"]
        expected_floors = spec["expected_floors"]

        start = time.time()
        raw = call_arifos_tool(tool, inp)
        elapsed = time.time() - start

        verdict, floors_triggered = parse_verdict(raw)

        results.append(
            {
                "scenario_id": scenario_id,
                "tool": tool,
                "input": inp,
                "verdict": verdict,
                "floors_triggered": floors_triggered,
                "expected_verdict": expected_verdict,
                "expected_floors": expected_floors,
                "elapsed_sec": round(elapsed, 2),
                "raw_result": raw,
            }
        )
    return results


# ── Main ───────────────────────────────────────────────────
def main() -> None:
    start_time = time.time()

    print("=" * 60)
    print("arifOS E2E Autoresearch")
    print("=" * 60)

    if not ARIFOS_API_KEY:
        print("ERROR: ARIFOS_API_KEY not in environment")
        print("E2E_SCORE: 0.000000")
        sys.exit(1)

    results = run_scenarios()
    scores = evaluate_score(results)

    wall_time = time.time() - start_time

    print(f"E2E_SCORE:  {scores['e2e_score']:.6f}")
    print(f"governance: {scores['governance_score']:.4f}")
    print(f"correctness:{scores['correctness_score']:.4f}")
    print(f"stability: {scores['stability_score']:.4f}")
    print(f"wall_time: {wall_time:.1f}s")
    print("-" * 60)
    for r in results:
        print(
            f"  {r['scenario_id']}: verdict={r['verdict']} floors={r['floors_triggered']} [{r['elapsed_sec']}s]"
        )

    # Save detailed results
    with open("run.log", "w") as f:
        f.write(f"E2E_SCORE: {scores['e2e_score']:.6f}\n")
        f.write(f"governance_score: {scores['governance_score']:.4f}\n")
        f.write(f"correctness_score: {scores['correctness_score']:.4f}\n")
        f.write(f"stability_score: {scores['stability_score']:.4f}\n")
        f.write(f"wall_time: {wall_time:.1f}s\n")
        f.write(json.dumps(results, indent=2, default=str))

    if wall_time > TIME_BUDGET_SECONDS * 2:
        print("WARNING: exceeded 2x time budget — possible OOM or hang")
        sys.exit(1)


if __name__ == "__main__":
    main()
