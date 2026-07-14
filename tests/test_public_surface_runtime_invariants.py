"""Runtime visibility is selected by semantic profile, never by model vendor."""

from __future__ import annotations

import pytest

from arifosmcp.runtime.public_surface import (
    DIAGNOSTIC_TOOLS,
    KERNEL_ABI_8,
    PUBLIC_AGENT_6,
    public_tool_names_for_mode,
)


def test_kernel_abi_has_exactly_eight_provider_bindings() -> None:
    assert KERNEL_ABI_8 == (
        "arif_init",
        "arif_observe",
        "arif_think",
        "arif_route",
        "arif_memory",
        "arif_judge",
        "arif_forge",
        "arif_seal",
    )


@pytest.mark.parametrize("mode", [None, "public", "public_agent", "chatgpt", "agnostic_public", "canonical13"])
def test_public_host_aliases_resolve_to_platform_neutral_public_agent(mode: str | None) -> None:
    assert public_tool_names_for_mode(mode) == PUBLIC_AGENT_6


def test_profiles_expand_authority_without_changing_semantics() -> None:
    public = set(public_tool_names_for_mode("public_agent"))
    executor = set(public_tool_names_for_mode("executor"))
    sovereign = set(public_tool_names_for_mode("sovereign"))

    assert public < executor < sovereign
    assert sovereign == set(KERNEL_ABI_8)
    assert executor - public == {"arif_forge"}
    assert sovereign - executor == {"arif_seal"}


def test_operator_diagnostics_require_explicit_gate(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ARIFOS_MCP_EXPOSE_DEV_TOOLS", raising=False)
    assert public_tool_names_for_mode("operator") == PUBLIC_AGENT_6

    monkeypatch.setenv("ARIFOS_MCP_EXPOSE_DEV_TOOLS", "true")
    expanded = set(public_tool_names_for_mode("operator"))
    assert set(KERNEL_ABI_8).issubset(expanded)
    assert set(DIAGNOSTIC_TOOLS).issubset(expanded)


def test_compatibility_aliases_never_appear_in_discovery() -> None:
    exposed = set(public_tool_names_for_mode("sovereign"))
    assert not exposed & {
        "arif_session_init",
        "arif_sense_observe",
        "arif_fetch",
        "arif_critique",
        "arif_bridge_connect",
        "arif_memory_recall",
        "arif_judge_deliberate",
        "arif_forge_execute",
        "arif_vault_seal",
    }
