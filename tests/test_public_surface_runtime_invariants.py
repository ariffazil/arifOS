"""
Runtime public surface invariants for the arifOS MCP facade.

These tests bind the resolver used by runtime code, not only the static
canonical constants. The goal is to catch connector/tool-list drift before
agents expose internal machinery to public clients.
"""

from __future__ import annotations

import pytest

from arifosmcp.runtime.public_surface import (
    CANONICAL_7,
    public_tool_names_for_mode,
)

EXPECTED_PUBLIC_TOOLS = frozenset(
    {
        "arif_init",
        "arif_observe",
        "arif_think",
        "arif_route",
        "arif_judge",
        "arif_act",
        "arif_seal",
    }
)

FORBIDDEN_DEFAULT_PUBLIC_TOOLS = frozenset(
    {
        "arif_bridge_connect",
        "arif_gateway_connect",
        "arif_forge",
        "arif_forge_execute",
        "arif_memory",
        "arif_memory_recall",
        "arif_vault_seal",
        "hermes_vault_query",
        "arif_canary",
        "arif_conformance_report",
    }
)


@pytest.mark.parametrize("mode", [None, "canonical13", "public", "chatgpt", "agnostic_public"])
def test_runtime_public_surface_resolves_to_canonical7(mode: str | None):
    """Default/public runtime modes must resolve to exactly the 7-tool facade."""
    resolved = set(public_tool_names_for_mode(mode))

    assert resolved == set(CANONICAL_7) == set(EXPECTED_PUBLIC_TOOLS)
    assert len(resolved) == 7


def test_default_runtime_surface_excludes_internal_and_diagnostic_tools():
    """Default tools/list must not leak aliases, diagnostics, bridge, forge, memory, or vault."""
    resolved = set(public_tool_names_for_mode(None))
    leaked = resolved & FORBIDDEN_DEFAULT_PUBLIC_TOOLS

    assert not leaked, f"Forbidden tools leaked into default public surface: {sorted(leaked)}"


def test_canonical13_surface_excludes_internal_and_diagnostic_tools():
    """Explicit canonical13 mode must remain public-safe."""
    resolved = set(public_tool_names_for_mode("canonical13"))
    leaked = resolved & FORBIDDEN_DEFAULT_PUBLIC_TOOLS

    assert not leaked, f"Forbidden tools leaked into canonical13 surface: {sorted(leaked)}"


def test_expanded45_mode_is_not_default_public_surface(monkeypatch: pytest.MonkeyPatch):
    """Expanded/operator mode must never activate from the default resolver by accident."""
    monkeypatch.delenv("ARIFOS_PUBLIC_SURFACE_MODE", raising=False)
    monkeypatch.delenv("ARIFOS_PUBLIC_TOOL_PROFILE", raising=False)
    monkeypatch.delenv("ARIFOS_MCP_EXPOSE_DEV_TOOLS", raising=False)

    resolved = set(public_tool_names_for_mode(None))

    assert resolved == set(EXPECTED_PUBLIC_TOOLS)
    assert "arif_conformance_report" not in resolved
    assert "arif_canary" not in resolved


def test_expanded45_requires_explicit_dev_gate(monkeypatch: pytest.MonkeyPatch):
    """
    Expanded45 is an operator/dev surface and must not be reachable merely by
    passing mode='expanded45' unless the explicit dev-tools gate is enabled.

    This test intentionally encodes the safety invariant needed after the
    connector exposed an expanded surface to ChatGPT.
    """
    monkeypatch.delenv("ARIFOS_MCP_EXPOSE_DEV_TOOLS", raising=False)

    resolved = set(public_tool_names_for_mode("expanded45"))

    assert resolved == set(EXPECTED_PUBLIC_TOOLS)
    assert not (resolved & FORBIDDEN_DEFAULT_PUBLIC_TOOLS)
