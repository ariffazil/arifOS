from __future__ import annotations

import pytest

from arifosmcp.runtime.public_surface import (
    KERNEL_ABI_8,
    PUBLIC_AGENT_6,
    VALID_PUBLIC_SURFACE_MODES,
    normalize_public_surface_mode,
    public_boundary_allows,
    public_tool_names_for_mode,
)


def test_numeric_legacy_constants_no_longer_define_semantics() -> None:
    from arifosmcp.runtime.public_surface import CANONICAL_7, CANONICAL_9, CANONICAL_12, CANONICAL_13

    assert CANONICAL_7 == CANONICAL_9 == CANONICAL_12 == CANONICAL_13 == KERNEL_ABI_8


def test_default_is_public_agent() -> None:
    assert normalize_public_surface_mode(None) == "public_agent"
    assert public_tool_names_for_mode(None) == PUBLIC_AGENT_6


def test_platform_aliases_have_no_special_authority() -> None:
    assert public_tool_names_for_mode("chatgpt") == PUBLIC_AGENT_6
    assert public_tool_names_for_mode("agnostic_public") == PUBLIC_AGENT_6


def test_profiles_are_semantic_not_numeric() -> None:
    assert set(VALID_PUBLIC_SURFACE_MODES) == {
        "public_agent",
        "trusted_agent",
        "executor",
        "sovereign",
        "operator",
        "legacy",
    }


def test_public_boundary_tracks_selected_profile() -> None:
    assert public_boundary_allows("arif_observe", "public_agent")
    assert not public_boundary_allows("arif_forge", "public_agent")
    assert public_boundary_allows("arif_forge", "executor")
    assert not public_boundary_allows("arif_seal", "executor")
    assert public_boundary_allows("arif_seal", "sovereign")


def test_operator_diagnostics_are_explicitly_gated(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ARIFOS_MCP_EXPOSE_DEV_TOOLS", raising=False)
    assert public_tool_names_for_mode("operator") == PUBLIC_AGENT_6
    monkeypatch.setenv("ARIFOS_MCP_EXPOSE_DEV_TOOLS", "true")
    assert len(public_tool_names_for_mode("operator")) > len(KERNEL_ABI_8)
