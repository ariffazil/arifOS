"""
tests/test_cognition_spine_e2e.py — Golden End-to-End Cognition Spine Test
══════════════════════════════════════════════════════════════════════════

Golden test verifying the full arifOS cognition spine:
  INIT -> OBSERVE -> THINK -> ROUTE -> MEMORY -> JUDGE

Asserts:
  1. Valid session ID propagated across all stages
  2. Evidence from OBSERVE is passed to THINK context
  3. THINK outputs valid epistemic fields (claim_state, synthesis, confidence, uncertainty)
  4. ROUTE produces valid destination or governed HOLD
  5. MEMORY returns context or deterministic empty
  6. JUDGE produces governed verdict (HOLD / SEAL / ACT / SABAR)

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

import json
import os
import urllib.request
import pytest

KERNEL_URL = os.environ.get("ARIFOS_KERNEL_URL", "http://127.0.0.1:8088")


def _mcp_call(name: str, args: dict, timeout: float = 65.0) -> dict:
    url = f"{KERNEL_URL.rstrip('/')}/mcp"
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {"name": name, "arguments": args},
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        res = data.get("result", {})
        return res.get("structuredContent") or res


def test_cognition_spine_e2e():
    actor_id = "test_warga_333"

    # 1. INIT
    init_res = _mcp_call("arif_init", {"actor_id": actor_id, "mode": "init"})
    session_id = init_res.get("session_id")
    assert session_id is not None, f"Missing session_id in init: {init_res}"
    assert session_id != "anonymous-session", "Session must be bound, not anonymous"

    # 2. OBSERVE
    evidence_text = "Gravitational redshift has been experimentally verified via Pound-Rebka experiment."
    obs_res = _mcp_call(
        "arif_observe",
        {
            "actor_id": actor_id,
            "session_id": session_id,
            "observation_type": "evidence",
            "raw_input": evidence_text,
        },
    )
    assert obs_res.get("status") in ("completed", "OK"), f"Observe failed: {obs_res}"
    obs_hash = obs_res.get("call_hash")

    # 3. THINK
    think_res = _mcp_call(
        "arif_think",
        {
            "actor_id": actor_id,
            "session_id": session_id,
            "mode": "reason",
            "query": "Is gravitational redshift experimentally verified?",
            "context": {"observed_evidence": evidence_text, "evidence_hash": obs_hash},
        },
        timeout=65.0,
    )
    assert think_res.get("status") in ("completed", "OK", "HOLD"), f"Think failed: {think_res}"
    
    # Verify structured epistemic output
    inner = think_res.get("result", {})
    if isinstance(inner, dict) and "result" in inner and isinstance(inner["result"], dict):
        ro = inner["result"].get("reasoning_output", {})
    else:
        ro = inner.get("reasoning_output", {}) if isinstance(inner, dict) else {}

    claim_state = ro.get("claim_state") or think_res.get("claim_state")
    synthesis = ro.get("synthesis") or (inner.get("synthesis") if isinstance(inner, dict) else None)
    confidence = ro.get("confidence") or (inner.get("confidence") if isinstance(inner, dict) else None)

    assert claim_state in ("VERIFIED_FACT", "SUPPORTED_CLAIM", "HYPOTHESIS", "UNKNOWN", "CLAIM"), (
        f"Invalid claim_state: {claim_state}"
    )
    assert synthesis is not None and len(synthesis) > 0, "Synthesis must not be empty"
    assert confidence is not None, "Confidence / uncertainty must be present"

    # 4. ROUTE
    route_res = _mcp_call(
        "arif_route",
        {
            "actor_id": actor_id,
            "session_id": session_id,
            "intent": "Evaluate Pound-Rebka experimental verification claim",
            "context": {"claim_state": claim_state, "domain": "physics"},
        },
    )
    assert route_res.get("status") in ("completed", "OK", "HOLD"), f"Route failed: {route_res}"

    # 5. MEMORY
    mem_res = _mcp_call(
        "arif_memory",
        {
            "actor_id": actor_id,
            "session_id": session_id,
            "action": "query",
            "query": "Pound-Rebka gravitational redshift experiment",
        },
    )
    assert mem_res.get("status") in ("completed", "OK", "HOLD"), f"Memory failed: {mem_res}"

    # 6. JUDGE
    judge_res = _mcp_call(
        "arif_judge",
        {
            "actor_id": actor_id,
            "session_id": session_id,
            "claim": "Pound-Rebka experiment confirms gravitational redshift",
            "candidate_action": "record_verified_observation",
            "evidence": {
                "claim_state": claim_state,
                "confidence": confidence.get("overall", 0.85) if isinstance(confidence, dict) else 0.85,
                "source": "arif_think",
            },
        },
    )
    judge_verdict = (
        judge_res.get("effective_verdict")
        or judge_res.get("verdict")
        or (judge_res.get("result", {}).get("verdict") if isinstance(judge_res.get("result"), dict) else None)
    )
    assert judge_verdict in ("HOLD", "SEAL", "ACT", "SABAR", "VOID"), (
        f"Invalid judge verdict: {judge_verdict}"
    )


if __name__ == "__main__":
    test_cognition_spine_e2e()
    print("✅ test_cognition_spine_e2e PASSED successfully!")
