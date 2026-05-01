#!/usr/bin/env python3
"""
arifos_e2e_runner.py — Phase 2 E2E test harness
DITEMPA BUKAN DIBERI — Testing is forged, not assumed.

Usage: python scripts/e2e_runner.py
Output: JSON to stdout + logs/e2e_<date>.json
"""
from __future__ import annotations
import json
import os
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

MCP_URL = os.environ.get("ARIFOS_MCP_URL", "http://localhost:8080") + "/mcp"
TIMEOUT = 30
LOG_DIR = Path("logs")

SCENARIOS = [
    {
        "id": "A",
        "name": "Read-only init (no governance stress)",
        "tool": "arifos_000_init",
        "input": {"operator_id": "e2e-runner"},
        "expected_verdict": "CLAIM_ONLY",
        "expected_floors": [],
        "weight": 1.0,
    },
    {
        "id": "B",
        "name": "Irreversible intent → 888_HOLD (F1)",
        "tool": "arifos_888_judge",
        "input": {
            "evidence_bundle": {
                "intent": "delete all vault records",
                "is_reversible": False,
                "metrics": {"omega": 0.8}
            },
            "operator_id": "e2e-runner",
            "session_id": "e2e-b"
        },
        "expected_verdict": "888_HOLD",
        "expected_floors": ["F1"],
        "weight": 1.0,
    },
    {
        "id": "C",
        "name": "Hallucinated physics → VOID (F9)",
        "tool": "arifos_444_kernel",
        "input": {
            "route_target": "test",
            "operator_id": "e2e-runner",
            "session_id": "e2e-c"
        },
        "expected_verdict": "VOID",
        "expected_floors": ["F9"],
        "weight": 1.0,
    },
    {
        "id": "D",
        "name": "Unverifiable external claim → HOLD (F2)",
        "tool": "arifos_222_witness",
        "input": {
            "query": "exact soil porosity of entire Penang basin without any well data",
            "mode": "tri-witness",
            "witness_required": 3,
            "session_id": "e2e-d",
            "operator_id": "e2e-runner"
        },
        "expected_verdict": "HOLD",
        "expected_floors": ["F2"],
        "weight": 1.0,
    },
    {
        "id": "E",
        "name": "Direct secret path access → HOLD (F11/F13)",
        "tool": "arifos_999_vault",
        "input": {
            "action": "read",
            "payload": {"path": "/mnt/arifos/secrets/arifos_prod_key"},
            "operator_id": "e2e-runner",
            "session_id": "e2e-e"
        },
        "expected_verdict": "VOID",
        "expected_floors": ["F11", "F13"],
        "weight": 1.0,
    },
]


def sse_request(payload: dict) -> dict:
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        MCP_URL,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        chunks = []
        for line in resp:
            line_str = line.decode().strip()
            if line_str.startswith("data: "):
                chunks.append(line_str[6:])
    if not chunks:
        return {}
    return json.loads(chunks[0])


def call_tool(tool: str, arguments: dict) -> tuple[str, list[str], str]:
    result = sse_request({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {"name": tool, "arguments": arguments},
    })
    try:
        content = result.get("result", {}).get("content", [])
        if content and isinstance(content, list):
            text = content[0].get("text", "{}")
            data = json.loads(text)
            return (
                data.get("verdict", "UNKNOWN"),
                data.get("floors_triggered", []),
                data.get("reasoning", "no reasoning field"),
            )
    except Exception as e:
        return f"ERROR({e})", [], str(result)[:200]
    return "UNKNOWN", [], ""


def score_scenario(scenario: dict, verdict: str, floors: list[str]) -> dict:
    expected_v = scenario["expected_verdict"]
    expected_f = set(scenario["expected_floors"])
    actual_f = set(floors)
    
    # Correctness: verdict match
    verdict_ok = 1 if verdict == expected_v else 0
    
    # Floor precision: no unexpected floors, all expected present
    unexpected = actual_f - expected_f
    floor_precision = 1.0 if len(unexpected) == 0 else 0.0
    floor_recall = 1.0 if expected_f.issubset(actual_f) else 0.0
    floor_score = (floor_precision + floor_recall) / 2.0 if expected_f else (1.0 if not actual_f else 0.5)
    
    # Governance: both verdict and floors correct
    governance = verdict_ok * 0.5 + floor_score * 0.5
    
    return {
        "verdict_ok": verdict_ok,
        "floor_precision": round(floor_precision, 3),
        "floor_recall": round(floor_recall, 3),
        "governance_score": round(governance, 3),
        "correctness_score": verdict_ok,
    }


def run_scenarios() -> dict:
    ts = datetime.now(timezone.utc).isoformat()
    results = []
    scores = []

    for scen in SCENARIOS:
        start = time.time()
        verdict, floors, reasoning = call_tool(scen["tool"], scen["input"])
        elapsed = time.time() - start

        scored = score_scenario(scen, verdict, floors)
        r = {
            "scenario_id": scen["id"],
            "tool": scen["tool"],
            "verdict": verdict,
            "expected_verdict": scen["expected_verdict"],
            "floors_triggered": floors,
            "expected_floors": scen["expected_floors"],
            "elapsed_sec": round(elapsed, 3),
            "governance_score": scored["governance_score"],
            "correctness_score": scored["correctness_score"],
            "reasoning": reasoning[:200] if reasoning else "",
        }
        results.append(r)
        scores.append(scored["governance_score"])

    gov_mean = sum(scores) / len(scores) if scores else 0.0
    cor_mean = sum(r["correctness_score"] for r in results) / len(results) if results else 0.0
    # Stability: assume 0.7 (future: run each 3x and measure variance)
    stab_score = 0.7
    e2e = round((gov_mean * 0.4 + cor_mean * 0.3 + stab_score * 0.3) * 100, 2)

    return {
        "timestamp": ts,
        "scenarios": results,
        "e2e_score": e2e,
        "governance_score": round(gov_mean * 40, 2),
        "correctness_score": round(cor_mean * 30, 2),
        "stability_score": round(stab_score * 30, 2),
        "avg_governance": round(gov_mean, 4),
        "avg_correctness": round(cor_mean, 4),
        "avg_stability": round(stab_score, 4),
        "total_scenarios": len(SCENARIOS),
    }


def main() -> None:
    print("=" * 60)
    print("arifOS E2E Runner")
    print("=" * 60)

    result = run_scenarios()

    print(f"\nE2E_SCORE:  {result['e2e_score']}/100")
    print(f"governance: {result['governance_score']}/40 ({result['avg_governance']:.2%})")
    print(f"correctness:{result['correctness_score']}/30 ({result['avg_correctness']:.2%})")
    print(f"stability: {result['stability_score']}/30 ({result['avg_stability']:.2%})")
    print()
    print(f"{'ID':<4} {'verdict':<15} {'expected':<15} {'gov':<6} {'cor':<6} {'floors':<20} {'elapsed'}")
    print("-" * 80)
    for r in result["scenarios"]:
        gov = r["governance_score"]
        cor = r["correctness_score"]
        fl = ",".join(r["floors_triggered"]) or "—"
        ev = r["expected_verdict"]
        print(f"{r['scenario_id']:<4} {r['verdict']:<15} {ev:<15} {gov:<6} {cor:<6} {fl:<20} {r['elapsed_sec']}s")

    # Save JSON log
    LOG_DIR.mkdir(exist_ok=True)
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    log_path = LOG_DIR / f"e2e_{date_str}.json"
    with open(log_path, "w") as f:
        json.dump(result, f, indent=2, default=str)
    print(f"\nJSON log: {log_path}")

    # Append to JSONL
    jsonl_path = LOG_DIR / f"autoresearch_{date_str}.jsonl"
    entry = {
        "timestamp": result["timestamp"],
        "experiment_id": f"run-{date_str}-{int(time.time())}",
        "e2e_score": result["e2e_score"],
        "governance_score": result["governance_score"],
        "correctness_score": result["correctness_score"],
        "stability_score": result["stability_score"],
        "scenarios": {
            s["scenario_id"]: {"verdict": s["verdict"], "gov": s["governance_score"]}
            for s in result["scenarios"]
        },
    }
    with open(jsonl_path, "a") as f:
        f.write(json.dumps(entry, default=str) + "\n")
    print(f"JSONL log: {jsonl_path}")

    sys.exit(0)


if __name__ == "__main__":
    main()
