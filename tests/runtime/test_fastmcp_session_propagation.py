import pytest

from fastmcp import FastMCP

from arifosmcp.apps.metabolic_monitor import _live_floor_status, _live_metabolics
from arifosmcp.runtime.sessions import clear_session_identity
from arifosmcp.runtime.tools import (
    _arifos_kernel_public,
    _arifos_ops_public,
    _arifos_init_public,
    register_v2_tools,
)


@pytest.mark.asyncio
async def test_init_propagates_verified_identity_to_kernel_and_ops():
    session_id = "sess-fastmcp-prop-001"
    clear_session_identity(session_id)

    init_env = await _arifos_init_public(
        actor_id="ARIF",
        intent="test",
        session_id=session_id,
        mode="init",
        platform="unknown",
    )
    assert init_env.verdict.value == "SEAL"
    assert init_env.payload["result"]["actor"] == "ARIF"
    assert init_env.payload["result"]["verified"] is True

    kernel_env = await _arifos_kernel_public(
        query="status",
        mode="status",
        session_id=session_id,
    )
    assert kernel_env.verdict.value in {"SEAL", "PARTIAL"}
    assert kernel_env.payload["result"]["actor"] == "ARIF"
    assert kernel_env.payload["result"]["verified"] is True

    ops_env = await _arifos_ops_public(
        query="health",
        mode="health",
        session_id=session_id,
    )
    assert ops_env.payload["result"]["actor"] == "ARIF"
    assert ops_env.payload["result"]["risk"] in {"medium", "high", "critical"}


@pytest.mark.asyncio
async def test_kernel_status_degrades_instead_of_void_without_session():
    env = await _arifos_kernel_public(query="status", mode="status", session_id="missing-session")

    assert env.verdict.value == "PARTIAL"
    assert env.payload["result"]["status"] == "degraded"
    assert env.caller_state == "anonymous"


def test_register_v2_tools_exposes_all_11_canonical_tools():
    mcp = FastMCP("fastmcp-regression")
    registered = register_v2_tools(mcp)

    expected = {
        "arifos_init",
        "arifos_sense",
        "arifos_mind",
        "arifos_kernel",
        "arifos_heart",
        "arifos_ops",
        "arifos_judge",
        "arifos_memory",
        "arifos_vault",
        "arifos_forge",
        "arifos_gateway",
    }
    assert set(registered) == expected


@pytest.mark.asyncio
async def test_metabolic_monitor_reads_live_session_state():
    session_id = "sess-fastmcp-monitor-001"
    clear_session_identity(session_id)

    await _arifos_init_public(
        actor_id="ARIF",
        intent="test monitor",
        session_id=session_id,
        mode="init",
        platform="mcp",
    )
    await _arifos_kernel_public(query="status", mode="status", session_id=session_id)
    await _arifos_ops_public(query="health", mode="health", session_id=session_id)

    metrics = _live_metabolics(session_id)
    floors = _live_floor_status(session_id)

    assert metrics["status"] == "LIVE"
    assert metrics["delta_s"] > 0
    assert any(floor["status"] in {"PASS", "FAIL", "STRAIN"} for floor in floors)
