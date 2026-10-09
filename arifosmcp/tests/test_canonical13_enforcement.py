"""
Public Surface Enforcement — Machine-Enforced Constitutional Law
═══════════════════════════════════════════════════════════════════════════════

F13 SOVEREIGN binding (machine-enforced, not rasa-enforced):

The arifOS public MCP surface is the constitution. Internal functions are the
ministries. New capability goes into MODES inside existing tools, not into new
public tools — unless 888 ratifies a surface expansion.

This test fails CI if anyone — human, agent, or future code — adds a public
MCP tool without explicit 888 (Arif) approval recorded in `EXPECTED_PUBLIC_TOOLS`.

SOT 2026-09-24 (S4 canonical verb registry): public wire = 8 canonical verbs
(KERNEL_ABI_8). Ratification trail: docs/CANONICAL-VERBS.md (S4, FastMCP
authoritative), commits 64497a435 + 445761b94 (arifosd.py TOOLS frozen
REFERENCE-ONLY; arif_act alias retired). Live :8088 wire serves exactly these
8 tools. Prior SOT 2026-07-12 (18 tools: metabolic 12 + entropy mesh 6) is
superseded; entropy-mesh verbs moved off the public wire.

DITEMPA BUKAN DIBERI — Bound by execution, not by string.
"""

from __future__ import annotations

import pytest

from arifosmcp.constitutional_map import CANONICAL_TOOLS
from arifosmcp.runtime.public_surface import (
    CANONICAL_12,
    CANONICAL_13,
    DIAGNOSTIC_TOOLS,
    VALID_PUBLIC_SURFACE_MODES,
)

# ─────────────────────────────────────────────────────────────────────────────
# THE LAW — public MCP tools arifOS exposes on default wire.
# To add or remove a public tool, edit THIS constant AND ratify via 888.
# ─────────────────────────────────────────────────────────────────────────────

EXPECTED_PUBLIC_TOOLS: frozenset[str] = frozenset(
    {
        # Canonical verbs — KERNEL_ABI_8 (S4, 2026-09-24; docs/CANONICAL-VERBS.md)
        "arif_init",     # kernel 000
        "arif_observe",  # kernel 111
        "arif_think",    # kernel 333
        "arif_route",    # kernel 444
        "arif_memory",   # kernel 555
        "arif_judge",    # kernel 666
        "arif_forge",    # kernel 777
        "arif_seal",     # kernel 999
    }
)

EXPECTED_PUBLIC_COUNT = 8

FORBIDDEN_PUBLIC_PREFIXES: tuple[str, ...] = (
    "arifos_",
    "_arifos_",
    "wealth_",
    "afwell_",
    "well_",
    "geox_",
    "geoxarifos_",
    "Arif_",
    "Hermes_",
    "Forge_",
    "Mind_",
    "Heart_",
    "Vault_",
)


def test_public_surface_is_exactly_8():
    """Public wire is exactly 8 canonical verbs (KERNEL_ABI_8, S4 2026-09-24)."""
    assert len(CANONICAL_12) == EXPECTED_PUBLIC_COUNT, (
        f"CANONICAL_12 must be exactly {EXPECTED_PUBLIC_COUNT}; got {len(CANONICAL_12)}. "
        f"To change, edit EXPECTED_PUBLIC_TOOLS AND obtain 888 ratification."
    )
    assert len(CANONICAL_13) == EXPECTED_PUBLIC_COUNT
    assert list(CANONICAL_13) == list(CANONICAL_12)


def test_canonical13_set_matches_expected_public_tools():
    """Public MCP tools must equal the locked EXPECTED_PUBLIC_TOOLS set."""
    actual = set(CANONICAL_12)
    expected = set(EXPECTED_PUBLIC_TOOLS)
    missing = expected - actual
    extra = actual - expected
    assert not missing, f"Missing public tools (888 must ratify to add): {sorted(missing)}"
    assert not extra, (
        f"Unauthorized public tools (CI FAIL — remove or ratify via 888): {sorted(extra)}"
    )


def test_canonical_tools_public_keys_match_surface():
    """Exposed CANONICAL_TOOLS keys must equal the public surface set."""
    public_tools = {
        name
        for name, spec in CANONICAL_TOOLS.items()
        if spec.get("access") != "internal_only" and spec.get("expose", True)
    }
    assert public_tools == set(CANONICAL_12), (
        f"Public CANONICAL_TOOLS keys drift from CANONICAL_12. "
        f"extra={sorted(public_tools - set(CANONICAL_12))}; "
        f"missing={sorted(set(CANONICAL_12) - public_tools)}."
    )
    assert len(public_tools) == EXPECTED_PUBLIC_COUNT


def test_canonical_tools_includes_internal_support():
    """Internal support tools remain in CANONICAL_TOOLS but expose=False."""
    internal = {
        name
        for name, spec in CANONICAL_TOOLS.items()
        if spec.get("access") == "internal_only" or not spec.get("expose", True)
    }
    assert "arif_triage" in internal
    assert not (internal & set(CANONICAL_12))


@pytest.mark.parametrize("tool_name", sorted(EXPECTED_PUBLIC_TOOLS))
def test_public_tool_name_starts_with_arif(tool_name: str):
    assert tool_name.startswith("arif_"), f"Public tool '{tool_name}' must start with 'arif_'."


@pytest.mark.parametrize("tool_name", sorted(EXPECTED_PUBLIC_TOOLS))
def test_public_tool_name_is_lowercase_snake_case(tool_name: str):
    assert tool_name == tool_name.lower()
    assert " " not in tool_name


@pytest.mark.parametrize("tool_name", sorted(EXPECTED_PUBLIC_TOOLS))
def test_public_tool_name_has_no_forbidden_prefix(tool_name: str):
    for prefix in FORBIDDEN_PUBLIC_PREFIXES:
        assert not tool_name.startswith(prefix), (
            f"Public tool '{tool_name}' starts with forbidden prefix '{prefix}'."
        )


def test_diagnostic_tools_do_not_bleed_into_public_surface():
    overlap = set(DIAGNOSTIC_TOOLS) & set(CANONICAL_12)
    assert not overlap, f"Diagnostic tools leaking into public surface: {sorted(overlap)}"


def test_public_surface_modes_are_actor_scoped():
    """Allowed modes are the actor-scope set (S4 redesign).

    The old surface-modes (canonical13/expanded45 + deprecated aliases
    canonical7/9/12) were replaced by actor scopes. See
    arifosmcp/runtime/public_surface.py VALID_PUBLIC_SURFACE_MODES.
    """
    modes = set(VALID_PUBLIC_SURFACE_MODES)
    assert modes == {
        "public_agent",
        "trusted_agent",
        "operator",
        "sovereign",
        "executor",
        "legacy",
    }


def test_expanded45_equals_public_union_diagnostic():
    from arifosmcp.runtime.public_surface import EXPANDED_45

    expected_expanded = set(CANONICAL_12) | set(DIAGNOSTIC_TOOLS)
    actual_expanded = set(EXPANDED_45)
    assert not (expected_expanded - actual_expanded)
    assert not (actual_expanded - expected_expanded)


@pytest.mark.parametrize("tool_name", sorted(EXPECTED_PUBLIC_TOOLS))
def test_every_public_tool_declares_floors(tool_name: str):
    spec = CANONICAL_TOOLS[tool_name]
    floors = spec.get("floors", [])
    assert floors, f"Public tool '{tool_name}' declares NO floors."


def test_seal_is_irreversible_public_commitment_gate():
    """arif_seal is the public irreversible commitment gate.

    arif_act was retired from the surface entirely (S4, 2026-09-24 —
    "arif_act alias retired", commit 64497a435); execution flows through
    arif_forge under lease governance.
    """
    assert CANONICAL_TOOLS["arif_seal"].get("irreversible") is True
    assert "arif_seal" in set(CANONICAL_12)
    assert "arif_act" not in CANONICAL_TOOLS, "arif_act retired (S4); remove if resurfaced"


def test_the_law_in_one_assertion():
    """Single canonical assertion. Edit EXPECTED_PUBLIC_TOOLS only with 888."""
    assert set(CANONICAL_12) == set(EXPECTED_PUBLIC_TOOLS)
    assert len(EXPECTED_PUBLIC_TOOLS) == EXPECTED_PUBLIC_COUNT
