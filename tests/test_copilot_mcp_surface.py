"""tests/test_copilot_mcp_surface.py — Acceptance tests for Copilot MCP surface optimizations.

Tests:
1. Output trimming: minimal verbosity strips _affordance and pipes irfan_review / sesat_event.
2. Resource tools bridge: search_resources and read_resource.
3. Copilot facade: arif_research, arif_recall, arif_delegate.
"""

from __future__ import annotations

import json
import os
import pytest

from arifosmcp.runtime.verbosity import trim_for_verbosity
from arifosmcp.tools.resource_bridge import read_resource, search_resources
from arifosmcp.tools.copilot_facade import arif_research, arif_recall, arif_delegate


def test_output_trimming_strips_internal_bloat():
    heavy_response = {
        "status": "OK",
        "tool": "arif_observe",
        "verdict": "SEAL",
        "session_id": "SEAL-test",
        "actor_id": "arif",
        "actor_verified": True,
        "call_hash": "sha256:123",
        "trace_id": "trc-123",
        "result": {
            "cpu": 25.0,
            "mem": 50.0,
            "_affordance": {"huge": "schema" * 500},
            "_wrapper_degradation": ["degraded"],
            "_wrapper_note": "note",
            "act_claims": {"claims": 123},
            "apex_scalars": {"G": 0.58},
        },
        "meta": {
            "reason": "telemetry ok",
            "irfan_review": {"recommendation": "CLEAR", "tests": ["test1" * 100]},
            "sesat_event": {"id": "sesat-999", "failure_code": "JALAN_BENAR", "payload": "large" * 100},
            "session_notice": {"notice": "notice"},
        },
    }

    trimmed = trim_for_verbosity(heavy_response, "minimal")
    res = trimmed.get("result", {})
    meta = trimmed.get("meta", {})

    # Internal bloat keys stripped from result
    assert "_affordance" not in res
    assert "_wrapper_degradation" not in res
    assert "_wrapper_note" not in res
    assert "act_claims" not in res
    assert "apex_scalars" not in res
    assert res.get("cpu") == 25.0

    # Diagnostics condensed in meta
    assert "irfan_review" not in meta
    assert meta.get("irfan_recommendation") == "CLEAR"
    assert "sesat_event" not in meta
    assert meta.get("sesat_id") == "sesat-999"
    assert meta.get("sesat_code") == "JALAN_BENAR"
    assert "session_notice" not in meta

    # Witness ledger contains the piped entries
    ledger_path = "/var/lib/arifos/witness/governance_telemetry.jsonl"
    assert os.path.exists(ledger_path)
    with open(ledger_path, "r", encoding="utf-8") as f:
        lines = [json.loads(l) for l in f if l.strip()]
    kinds = [entry.get("kind") for entry in lines]
    assert "irfan_review" in kinds
    assert "sesat_event" in kinds


@pytest.mark.asyncio
async def test_resource_tools_bridge():
    # 1. search_resources
    search_res = await search_resources(query="vitals")
    assert search_res["status"] == "ok"
    assert search_res["count"] >= 1
    uris = [r["uri"] for r in search_res["resources"]]
    assert any("vitals" in u for u in uris)

    # 2. read_resource
    read_res = await read_resource("arifos://vitals")
    assert read_res["status"] == "ok"
    assert "telemetry" in read_res["content"] or "vitals" in read_res["content"]

    # 3. read non-existent resource fails gracefully
    err_res = await read_resource("arifos://non-existent-resource-uri-xyz")
    assert err_res["status"] == "error"
    assert "error" in err_res


@pytest.mark.asyncio
async def test_copilot_facade_tools():
    # 1. arif_research
    research_res = await arif_research(query="system vitals test")
    assert research_res["status"] == "ok"
    assert "query" in research_res
    assert isinstance(research_res.get("facts"), list)
    assert "synthesis" in research_res

    # 2. arif_recall
    recall_res = await arif_recall(query="anti-bangang")
    assert recall_res["status"] == "ok"
    assert "entries" in recall_res

    # 3. arif_delegate
    delegate_res = await arif_delegate(query="calculate seismic velocity for fault zone", organ="GEOX")
    assert delegate_res["status"] == "ok"
    assert "target_organ" in delegate_res
