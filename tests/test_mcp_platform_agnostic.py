"""Tests for MCP platform & model agnostic invariants and fixes.

Covers:
1. arif_init(mode="canary") works without session / actor_id and returns alive status
2. arif_seal schema correctly scopes payload requirement to write modes only
3. arif_route documentation and contract clarity
4. build attestation reports clean zero drift when build stamps align
"""

from __future__ import annotations

import pytest
from arifosmcp.runtime.public_registry import _runtime_contracts, _TOOL_DESCRIPTIONS
from arifosmcp.runtime.build import get_runtime_attestation
from arifosmcp.tools.session import arif_init


def test_arif_init_canary_mode():
    """Canary probe must succeed without session_id or actor_id."""
    res = arif_init(mode="canary")
    assert getattr(res, "status", None) in ("completed", "OK")
    inner = getattr(res, "result", None)
    if isinstance(inner, dict):
        assert inner.get("kernel") == "alive"
        assert inner.get("observe_only") is True
    else:
        assert getattr(inner, "kernel", None) == "alive"
        assert getattr(inner, "observe_only", None) is True


def test_arif_seal_schema_payload_conditional():
    """arif_seal must not globally require payload on read modes (verify, ledger, etc)."""
    contracts = _runtime_contracts()
    assert "arif_seal" in contracts
    schema = contracts["arif_seal"].get("input_schema", {})
    # Top-level required must not contain payload
    assert "payload" not in schema.get("required", [])

    # allOf must contain conditional requirement for seal / session_close
    all_of = schema.get("allOf", [])
    assert len(all_of) >= 1
    rule = all_of[0]
    then_block = rule.get("then", {})
    assert "payload" in then_block.get("required", [])
    assert "seal_purpose" in then_block.get("required", [])


def test_arif_route_description_clarity():
    """arif_route description clarifies routing envelope vs actual execution."""
    desc = _TOOL_DESCRIPTIONS.get("arif_route", "")
    assert "dispatch envelope" in desc
    assert "Calling the organ tool itself is a separate" in desc


def test_runtime_attestation_zero_drift():
    """Software release build stamps must report zero drift."""
    att = get_runtime_attestation()
    assert isinstance(att, dict)
    assert att.get("drift") is False
    assert att.get("source_commit") == att.get("built_commit") == att.get("deployed_commit")
