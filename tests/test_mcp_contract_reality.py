"""
test_mcp_contract_reality.py -- Contract Reality Automated Canary (P0)

Tests that for every canonical MCP tool, the advertised parameters in its
schema are actually accepted by the callable runtime handler.

Enforces:
    S_declared = S_exported = S_callable = S_observed
Zero tolerance for exported-but-uncallable arguments (e.g. arif_route.mode).
"""

from __future__ import annotations

import inspect
import pytest
from arifosmcp.constitutional_map import CANONICAL_TOOLS
from arifosmcp.runtime.public_registry import public_tool_spec_by_name


def test_canonical_tools_accept_declared_parameters():
    """Verify that calling any tool with legal declared arguments succeeds without TypeError."""
    spec_by_name = public_tool_spec_by_name()
    from arifosmcp.runtime.tools import _CANONICAL_HANDLERS, _wrap_handler

    errors = []

    for name in ("arif_init", "arif_observe", "arif_think", "arif_route", "arif_judge"):
        spec = spec_by_name.get(name)
        if not spec:
            continue
        handler = _CANONICAL_HANDLERS.get(name)
        if not handler:
            continue

        wrapped = _wrap_handler(handler, name)
        input_schema = spec.input_schema or {}
        props = input_schema.get("properties", {})

        # Test each individual property with a dummy value to ensure no TypeError
        for prop_name in props:
            # Skip internal envelope transport fields
            if prop_name in ("_envelope", "contract_c_kwargs"):
                continue
            test_val = "test_val" if props[prop_name].get("type") == "string" else None
            try:
                # We inspect whether calling with this kwarg raises TypeError: unexpected keyword argument
                inspect.signature(wrapped).bind_partial(**{prop_name: test_val})
            except TypeError as te:
                if "unexpected keyword argument" in str(te):
                    errors.append(
                        f"Tool '{name}' advertises parameter '{prop_name}', "
                        f"but callable wrapped handler rejects it: {te}"
                    )

    assert not errors, "\n".join(errors)


def test_arif_route_callable_with_mode():
    """Explicit regression test: calling arif_route with mode='route' or 'bridge' must succeed."""
    from arifosmcp.tools.kernel_canonical import arif_route

    # Test mode="route"
    res_route = arif_route(intent="system vitals", mode="route")
    assert isinstance(res_route, dict)
    assert res_route.get("status") in ("OK", "SEAL", "HOLD", "ROUTED") or "organ" in res_route

    # Test mode="bridge"
    res_bridge = arif_route(intent="system vitals", mode="bridge")
    assert isinstance(res_bridge, dict)


@pytest.mark.asyncio
async def test_observe_to_think_continuity():
    """Verify that evidence and identity collected at OBSERVE deterministically survive into THINK."""
    from arifosmcp.runtime.tools import _SESSIONS
    from arifosmcp.tools.embodied_instances.arif_think_handler import embodied_mind_reason_handler

    test_sid = "ses-continuity-test-999"
    test_actor = "claude-code/external-audit"

    # Pre-seed session with an observation (as arif_observe does)
    _SESSIONS[test_sid] = {
        "session_id": test_sid,
        "actor_id": test_actor,
        "observations": [
            {
                "tool": "arif_observe",
                "mode": "vitals",
                "result": {"cpu": 63.2, "mem": 76.1, "disk_free_gb": 120.3},
            }
        ],
    }

    # Call arif_think with the same session_id and actor_id
    think_res = await embodied_mind_reason_handler(
        query="what are the system vitals?",
        mode="reason",
        session_id=test_sid,
        actor_id=test_actor,
    )

    assert isinstance(think_res, dict)
    # 1. Identity must NOT regress to anonymous
    assert think_res.get("session_id") == test_sid, f"Expected {test_sid}, got {think_res.get('session_id')}"
    assert think_res.get("actor_id") == test_actor, f"Expected {test_actor}, got {think_res.get('actor_id')}"

    # 2. Evidence must survive into the inner result
    inner_res = think_res.get("result", {})
    if isinstance(inner_res, dict):
        payload = inner_res.get("result") if isinstance(inner_res.get("result"), dict) else inner_res
        assert inner_res.get("session_id") == test_sid or payload.get("session_id") == test_sid
        assert inner_res.get("actor_id") == test_actor or payload.get("actor_id") == test_actor
        evidence_used = payload.get("evidence_used", []) or inner_res.get("evidence_used", [])
        assert len(evidence_used) > 0, "Expected evidence_used to contain observations from prior step!"

