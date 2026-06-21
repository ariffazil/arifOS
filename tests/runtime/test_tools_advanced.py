from __future__ import annotations

from arifosmcp.constitutional_map import CANONICAL_TOOLS
from arifosmcp.runtime.public_surface import CANARY_PROBES
from arifosmcp.runtime.tools import _arif_ping, _arif_session_init


def test_ping_reports_canonical13_surface() -> None:
    result = _arif_ping()["result"]

    # canonical13 public surface = 21 canonical tools + 1 transport canary diagnostic
    assert result["tools_registered"] == len(CANONICAL_TOOLS) + len(CANARY_PROBES)
    assert result["public_surface"]["mode"] == "canonical13"
    assert result["public_surface"]["kernel_tools"] == len(CANONICAL_TOOLS)
    assert set(result["public_surface"]["diagnostic_tools"]) == set(CANARY_PROBES)
    assert result["constitution"]["kernel"] == "canonical13"


def test_ping_full_expands_constitution_only_on_request() -> None:
    default_result = _arif_ping()["result"]
    full_result = _arif_ping(mode="full")["result"]

    assert "floors" not in default_result["constitution"]
    assert len(full_result["constitution"]["floors"]) == 13


def test_session_init_returns_binding_governance_and_public_tools() -> None:
    result = _arif_session_init(mode="init", actor_id="arif")["result"]

    assert result["binding"]["public_surface"] == "canonical13"
    assert result["binding"]["kernel"] == "canonical13"
    assert result["governance"]["forge_default"] == "dry_run_only"
    assert result["next_allowed_tools"]
    assert all(name.startswith("arif_") for name in result["next_allowed_tools"])
