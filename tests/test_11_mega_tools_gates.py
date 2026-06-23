from __future__ import annotations

from arifosmcp.constitutional_map import CANONICAL_TOOLS
from arifosmcp.runtime.public_registry import (
    CANONICAL_PUBLIC_TOOLS,
    EXPECTED_TOOL_COUNT,
    public_tool_names,
)
from arifosmcp.runtime.public_surface import current_public_surface_mode
from arifosmcp.runtime.tools import _arif_ping, _arif_selftest, _arif_session_init


def test_public_registry_exposes_only_canonical7() -> None:
    names = set(public_tool_names())

    assert len(names) == EXPECTED_TOOL_COUNT
    assert names == CANONICAL_PUBLIC_TOOLS


def test_ping_and_init_share_constitution_identity() -> None:
    ping = _arif_ping(include_constitution=True)
    init = _arif_session_init(mode="init", actor_id="arif")

    constitution = ping["result"]["constitution"]
    init_constitution = init["constitution"]
    init_result = init["result"]

    assert constitution["constitution_id"] == init_constitution["id"]
    assert init_constitution["id"] == init_result["constitution_hash"]
    assert constitution["kernel"] == "canonical13"
    assert current_public_surface_mode() == "canonical13"


def test_unknown_init_mode_holds_with_allowed_modes() -> None:
    result = _arif_session_init(mode="probe", actor_id="arif")

    assert result["status"] == "HOLD"
    assert "Unknown mode" in result["meta"]["reason"]
    assert result["meta"]["allowed_modes"] == [
        "init",
        "light",
        "resume",
        "validate",
        "epoch_open",
        "epoch_seal",
        "opt_out",
        "opt_out_profiling",
    ]


def test_selftest_passes_and_keeps_forge_dry_run() -> None:
    result = _arif_selftest()

    assert result["verdict"] == "PASS"
    assert result["checks"]["mind_check"]["verdict"] == "PASS"
    assert result["checks"]["heart_check"]["verdict"] == "PASS"
    assert result["checks"]["registry_check"]["tools_count"] == len(CANONICAL_TOOLS)
    assert result["checks"]["forge_dry_run_check"]["permanent_change"] is False
