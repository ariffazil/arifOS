from __future__ import annotations

from arifosmcp.runtime.tools import _arif_ping, _arif_session_init


def test_ping_reports_canonical15_surface() -> None:
    result = _arif_ping()["result"]

    assert result["tools_registered"] == 15
    assert result["public_surface"]["mode"] == "canonical15"
    assert result["public_surface"]["kernel_tools"] == 13
    assert result["public_surface"]["diagnostic_tools"] == ["arif_ping", "arif_selftest"]
    assert result["constitution"]["kernel"] == "canonical13"


def test_ping_full_expands_constitution_only_on_request() -> None:
    default_result = _arif_ping()["result"]
    full_result = _arif_ping(mode="full")["result"]

    assert "floors" not in default_result["constitution"]
    assert len(full_result["constitution"]["floors"]) == 13


def test_session_init_returns_binding_governance_and_public_tools() -> None:
    result = _arif_session_init(mode="init", actor_id="arif")["result"]

    assert result["binding"]["public_surface"] == "canonical15"
    assert result["binding"]["kernel"] == "canonical13"
    assert result["governance"]["forge_default"] == "dry_run_only"
    assert result["next_allowed_tools"]
    assert all(name.startswith("arif_") for name in result["next_allowed_tools"])
