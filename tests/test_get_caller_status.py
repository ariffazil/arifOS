import pytest
from arifosmcp.runtime.tools import init_anchor
from arifosmcp.runtime.models import RuntimeStatus, Verdict, Stage, RuntimeEnvelope

@pytest.mark.asyncio
async def test_get_caller_status_decoration():
    """Verify get_caller_status returns proper bootstrap diagnostics."""
    envelope = await init_anchor(mode="status", session_id="global")
    
    assert envelope.status == RuntimeStatus.SUCCESS
    assert envelope.tool == "init_anchor"
    assert envelope.caller_state == "anonymous"
    
    # In V2, diagnostic fields are at the top level of the payload result
    res = envelope.payload["result"]
    assert "bootstrap_sequence" in res
    assert res["system_motto"] == "DITEMPA BUKAN DIBERI — Forged, Not Given"
    assert "check_vital" in envelope.allowed_next_tools

@pytest.mark.asyncio
async def test_get_caller_status_anchored_visibility():
    """Verify get_caller_status shows mind/heart tools when anchored."""
    session_id = "test-anchored-visibility"
    # Anchor first
    await init_anchor(
        mode="init",
        actor_id="arif",
        intent="test visibility",
        session_id=session_id
    )
    
    envelope = await init_anchor(mode="status", session_id=session_id)
    
    assert envelope.caller_state in {"anchored", "verified"}
    # Anchored sessions should see intelligence tools
    assert "arifos_kernel" in envelope.allowed_next_tools
    assert "agi_mind" in envelope.allowed_next_tools
    assert "physics_reality" in envelope.allowed_next_tools
