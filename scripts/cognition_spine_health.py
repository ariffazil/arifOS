#!/usr/bin/env python3
"""
scripts/cognition_spine_health.py — Deterministic Cognition Spine Health Probe
═════════════════════════════════════════════════════════════════════════════

Deterministic health probe verifying the 6-stage cognition spine:
  1. INIT    — Session context present and session capability token bound
  2. OBSERVE — Evidence can be observed and hashed
  3. THINK   — Reasoning invocation returns structured epistemic output
  4. ROUTE   — Destination routed or governed HOLD
  5. MEMORY  — Memory recall returns context or deterministic empty
  6. JUDGE   — Governance reach intact, returns governed verdict (HOLD/SEAL/ACT)

Usage:
    python scripts/cognition_spine_health.py [--url http://127.0.0.1:8088] [--timeout 60] [--json]

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from typing import Any


def call_mcp_tool(
    base_url: str,
    name: str,
    args: dict[str, Any],
    timeout: float = 60.0,
) -> tuple[dict[str, Any], float]:
    """Execute tool call on arifOS MCP surface, return (structuredContent, latency_s)."""
    payload = {
        "jsonrpc": "2.0",
        "id": int(time.time() * 1000) % 1000000,
        "method": "tools/call",
        "params": {
            "name": name,
            "arguments": args,
        },
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{base_url.rstrip('/')}/mcp",
        data=data,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        },
    )
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            dt = time.perf_counter() - t0
            parsed = json.loads(raw)
            result = parsed.get("result", {})
            sc = result.get("structuredContent", {})
            return (sc if sc else result), dt
    except urllib.error.HTTPError as e:
        dt = time.perf_counter() - t0
        err_body = e.read().decode("utf-8", errors="replace")
        try:
            parsed_err = json.loads(err_body)
            sc = parsed_err.get("result", {}).get("structuredContent", {})
            if sc:
                return sc, dt
        except Exception:
            pass
        return {"error": f"HTTP {e.code}", "detail": err_body}, dt
    except Exception as exc:
        dt = time.perf_counter() - t0
        return {"error": str(type(exc).__name__), "detail": str(exc)}, dt


def run_probe(base_url: str = "http://127.0.0.1:8088", timeout: float = 65.0) -> dict[str, Any]:
    """Run deterministic cognition spine health probe."""
    report: dict[str, Any] = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "base_url": base_url,
        "checks": {},
        "latencies": {},
        "passed": False,
        "anomalies": [],
    }

    actor_id = "cognition_health_probe"

    # 1. INIT — Session context present
    init_res, init_dt = call_mcp_tool(
        base_url,
        "arif_init",
        {"actor_id": actor_id, "mode": "init"},
        timeout=15.0,
    )
    report["latencies"]["init"] = round(init_dt, 3)
    session_id = init_res.get("session_id")
    has_session = bool(session_id and session_id != "anonymous-session")
    report["checks"]["session_context_present"] = has_session
    if not has_session:
        report["anomalies"].append(f"INIT failed: {init_res.get('error') or 'no session_id'}")
        return report

    # 2. OBSERVE — Evidence can be observed
    obs_res, obs_dt = call_mcp_tool(
        base_url,
        "arif_observe",
        {
            "actor_id": actor_id,
            "session_id": session_id,
            "observation_type": "query",
            "raw_input": "Observe physical invariance of local light speed in general relativity",
        },
        timeout=15.0,
    )
    report["latencies"]["observe"] = round(obs_dt, 3)
    has_obs = obs_res.get("status") in ("completed", "OK") or "call_hash" in obs_res
    report["checks"]["evidence_observed"] = has_obs
    if not has_obs:
        report["anomalies"].append(f"OBSERVE failed: {obs_res.get('error') or 'status not OK'}")

    # 3. THINK — Reasoning invocation works + structured epistemic output
    think_res, think_dt = call_mcp_tool(
        base_url,
        "arif_think",
        {
            "actor_id": actor_id,
            "session_id": session_id,
            "mode": "reason",
            "query": "Is local light speed invariant in general relativity?",
        },
        timeout=timeout,
    )
    report["latencies"]["think"] = round(think_dt, 3)
    inner_res = think_res.get("result", {})
    if isinstance(inner_res, dict) and "result" in inner_res and isinstance(inner_res["result"], dict):
        ro = inner_res["result"].get("reasoning_output", {})
    else:
        ro = inner_res.get("reasoning_output", {})

    claim_state = ro.get("claim_state") or think_res.get("claim_state")
    synthesis = ro.get("synthesis") or inner_res.get("synthesis")
    confidence = ro.get("confidence") or inner_res.get("confidence")
    degraded_state = think_res.get("degraded_state") or ro.get("degraded_state")

    think_ok = bool(think_res.get("status") in ("completed", "OK", "HOLD"))
    structured_epistemic = bool(claim_state and synthesis is not None)
    uncertainty_preserved = bool(confidence is not None or degraded_state is not None)

    report["checks"]["reasoning_invocation_works"] = think_ok
    report["checks"]["structured_epistemic_output"] = structured_epistemic
    report["checks"]["uncertainty_preserved"] = uncertainty_preserved
    report["checks"]["claim_state"] = claim_state
    report["checks"]["confidence"] = confidence

    if not (think_ok and structured_epistemic):
        report["anomalies"].append(f"THINK failed or malformed: status={think_res.get('status')}")

    # 4. ROUTE — Route produces valid destination / hold
    route_res, route_dt = call_mcp_tool(
        base_url,
        "arif_route",
        {
            "actor_id": actor_id,
            "session_id": session_id,
            "intent": "Evaluate general relativity invariance claim",
            "context": {"claim_state": claim_state or "CLAIM", "domain": "physics"},
        },
        timeout=15.0,
    )
    report["latencies"]["route"] = round(route_dt, 3)
    route_ok = route_res.get("status") in ("completed", "OK", "HOLD")
    report["checks"]["route_valid"] = route_ok

    # 5. MEMORY — Memory recall returns context or deterministic empty
    mem_res, mem_dt = call_mcp_tool(
        base_url,
        "arif_memory",
        {
            "actor_id": actor_id,
            "session_id": session_id,
            "action": "query",
            "query": "local speed of light invariance",
        },
        timeout=15.0,
    )
    report["latencies"]["memory"] = round(mem_dt, 3)
    mem_ok = mem_res.get("status") in ("completed", "OK", "HOLD")
    report["checks"]["memory_reachable"] = mem_ok

    # 6. JUDGE — Governance reach intact (returns HOLD, SEAL, or ACT)
    judge_res, judge_dt = call_mcp_tool(
        base_url,
        "arif_judge",
        {
            "actor_id": actor_id,
            "session_id": session_id,
            "claim": "Local light speed invariance in GR is strongly supported by evidence",
            "candidate_action": "record_epistemic_observation",
            "evidence": {
                "claim_state": claim_state or "SUPPORTED_CLAIM",
                "confidence": 0.85,
                "source": "arif_think",
            },
        },
        timeout=15.0,
    )
    report["latencies"]["judge"] = round(judge_dt, 3)
    judge_verdict = (
        judge_res.get("effective_verdict")
        or judge_res.get("verdict")
        or judge_res.get("result", {}).get("verdict")
    )
    governance_intact = judge_verdict in ("HOLD", "SEAL", "ACT", "SABAR", "VOID")
    report["checks"]["governance_reach_intact"] = governance_intact
    report["checks"]["judge_verdict"] = judge_verdict

    # Overall verdict
    all_passed = (
        report["checks"]["session_context_present"]
        and report["checks"]["evidence_observed"]
        and report["checks"]["reasoning_invocation_works"]
        and report["checks"]["structured_epistemic_output"]
        and report["checks"]["uncertainty_preserved"]
        and report["checks"]["governance_reach_intact"]
    )
    report["passed"] = all_passed
    report["total_latency_s"] = round(sum(report["latencies"].values()), 3)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Deterministic Cognition Spine Health Probe")
    parser.add_argument("--url", default="http://127.0.0.1:8088", help="Kernel base URL")
    parser.add_argument("--timeout", type=float, default=65.0, help="Think timeout in seconds")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    args = parser.parse_args()

    report = run_probe(base_url=args.url, timeout=args.timeout)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("=" * 60)
        print("ARIFOS COGNITION SPINE HEALTH PROBE")
        print("=" * 60)
        print(f"Timestamp:       {report['timestamp']}")
        print(f"Kernel URL:      {report['base_url']}")
        print(f"Overall Result:  {'✅ PASSED' if report['passed'] else '❌ FAILED'}")
        print(f"Total Latency:   {report.get('total_latency_s', 0)}s")
        print("\nSpine Stage Checks:")
        for check, val in report["checks"].items():
            icon = "✅" if val is True else ("❌" if val is False else "ℹ️")
            print(f"  {icon} {check:<30}: {val}")
        print("\nStage Latencies (seconds):")
        for stage, lat in report["latencies"].items():
            print(f"  - {stage:<10}: {lat:.3f}s")
        if report["anomalies"]:
            print("\nAnomalies Detected:")
            for a in report["anomalies"]:
                print(f"  ⚠️ {a}")
        print("=" * 60)

    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
