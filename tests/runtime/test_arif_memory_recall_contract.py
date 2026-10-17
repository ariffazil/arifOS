"""
tests/runtime/test_arif_memory_recall_contract.py — recall must never be
silent and never answer a tier it did not search.

Regression (2026-10-16, live :8088 probes):
  1. recall returning zero hits carried NO hits list, NO reason — an agent
     could not distinguish "not found" from "blocked" (verbosity minimal
     projection dropped the RuntimeEnvelope payload; echo_canonical_session
     then filled result with the standing blob).
  2. tier=L4 / tier=L6 requests were silently answered from the L3 cascade.
  3. arifos://memory documented arif_memory_recall + tier=L4 recall and did
     not document the write modes (doc-only; asserted here as a canary).

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

import os

os.environ["ARIFOS_DEV_MODE"] = "1"

from arifosmcp.runtime.megaTools.tool_13_arif_memory import (  # noqa: E402
    RECALL_TIERS_NOT_SEARCHED,
    _recall_empty_payload,
    annotate_recall_contract,
)
from arifosmcp.runtime.model import RuntimeEnvelope  # noqa: E402
from arifosmcp.runtime.verbosity import trim_for_verbosity  # noqa: E402


def test_annotate_empty_hits_carries_reason_and_tiers():
    env = RuntimeEnvelope(
        ok=True,
        tool="engineering_memory",
        session_id="s1",
        stage="555m_MEMORY",
        payload={"results": [], "count": 0, "query": "q", "found": False, "backend": "qdrant"},
    )
    out = annotate_recall_contract(env, {"query": "q", "tier_hint": "L3"})
    body = out.payload
    assert body["hits"] == []
    assert body["tiers_requested"] == ["L3"]
    assert body["tiers_searched"] == ["L3"]
    assert body["tier_honored"] is True
    assert body["reason"], "empty recall must carry a reason"


def test_annotate_reports_unhonored_tier():
    env = RuntimeEnvelope(
        ok=True,
        tool="engineering_memory",
        session_id="s1",
        stage="555m_MEMORY",
        payload={"results": [{"id": "m1"}], "backend": "qdrant", "found": True},
    )
    out = annotate_recall_contract(env, {"query": "q", "tier_hint": "L7"})
    body = out.payload
    assert body["hits"] == [{"id": "m1"}]
    assert body["tiers_requested"] == ["L7"]
    assert body["tiers_searched"] == ["L3"]
    assert body["tier_honored"] is False, "L7 was not searched — must not read as honored"


def test_unsearchable_tiers_declared():
    for tier in ("L4", "L6"):
        assert tier in RECALL_TIERS_NOT_SEARCHED
        payload = _recall_empty_payload("q", tier, [], RECALL_TIERS_NOT_SEARCHED[tier])
        assert payload["hits"] == []
        assert payload["tiers_searched"] == []
        assert payload["tier_honored"] is False
        assert payload["reason"] == RECALL_TIERS_NOT_SEARCHED[tier]
    # L6 single-path invariant: the reason names arif_seal as the only writer
    assert "arif_seal" in RECALL_TIERS_NOT_SEARCHED["L6"]


def test_minimal_trim_projects_envelope_payload_not_standing():
    """The exact regression: minimal verbosity dropped the RuntimeEnvelope
    payload and echo filled result with the standing blob."""
    env = RuntimeEnvelope(
        ok=True,
        tool="engineering_memory",
        session_id="s1",
        stage="555m_MEMORY",
        payload={"hits": [{"id": "m1"}], "count": 1, "found": True, "tiers_searched": ["L3"]},
    )
    response = {"status": "OK", "tool": "arif_memory", "result": env, "session_id": "s1"}
    minimal = trim_for_verbosity(response, "minimal")
    assert isinstance(minimal["result"], dict)
    assert minimal["result"].get("hits") == [{"id": "m1"}], "memory payload must survive trim"
    assert minimal["result"].get("count") == 1
