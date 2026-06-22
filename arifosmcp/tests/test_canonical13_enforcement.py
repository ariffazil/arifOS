"""
Canonical13 Public Surface Enforcement — Machine-Enforced Constitutional Law
═══════════════════════════════════════════════════════════════════════════════

F13 SOVEREIGN binding (machine-enforced, not rasa-enforced):

The arifOS public MCP surface is the constitution. Internal functions are the
ministries. New capability goes into MODES inside existing tools, not into new
public tools.

This test fails CI if anyone — human, agent, or future code — adds a public
MCP tool without explicit 888 (Arif) approval recorded in `EXPECTED_TOOLS`.

Ref: AGENTS.md "Tell Python, not RASA" — 2026-06-19

DITEMPA BUKAN DIBERI — Bound by execution, not by string.
"""

from __future__ import annotations

import pytest

from arifosmcp.constitutional_map import CANONICAL_TOOLS
from arifosmcp.runtime.public_surface import (
    BLOCKED_PUBLIC_PREFIXES,
    CANONICAL_13,
    DIAGNOSTIC_TOOLS,
    VALID_PUBLIC_SURFACE_MODES,
)


# ─────────────────────────────────────────────────────────────────────────────
# THE LAW — these are the only public MCP tools arifOS will ever expose.
# To add or remove a public tool, edit THIS constant AND ratify via 888.
# ─────────────────────────────────────────────────────────────────────────────

EXPECTED_PUBLIC_TOOLS: frozenset[str] = frozenset(
    {
        # GOVERNANCE (APEX / ASI)
        "arif_init",
        "arif_judge",
        "arif_seal",
        # INTELLIGENCE (Δ Mind / Ω Heart)
        "arif_think",
        "arif_critique",
        "arif_compose",
        # INFRASTRUCTURE
        "arif_kernel_route",
        "arif_gateway_connect",
        "arif_memory_recall",
        "arif_measure",
        # REALITY GROUNDING
        "arif_observe",
        "arif_fetch",
        # EXECUTION
        "arif_forge",
    }
)


# Names that are FORBIDDEN at the start of any public tool name.
# (Anti-domain-bleed invariant: arifOS public surface does not leak organs.)
FORBIDDEN_PUBLIC_PREFIXES: tuple[str, ...] = (
    "arifos_",  # internal arifOS namespace
    "_arifos_",
    "wealth_",  # organ bleed
    "afwell_",  # organ bleed
    "well_",  # organ bleed
    "geox_",  # organ bleed
    "geoxarifos_",
    "Arif_",  # PascalCase forbidden
    "Hermes_",  # PascalCase forbidden
    "Forge_",
    "Mind_",
    "Heart_",
    "Vault_",
)


# ─────────────────────────────────────────────────────────────────────────────
# Test 1: Exactly 13 canonical public tools, and the set is locked.
# ─────────────────────────────────────────────────────────────────────────────

def test_canonical13_is_exactly_13():
    """The constitutional public surface is exactly 13 tools. Not 12, not 14, not 39."""
    assert len(CANONICAL_13) == 13, (
        f"CANONICAL_13 must be exactly 13 tools; got {len(CANONICAL_13)}. "
        f"To change, edit EXPECTED_PUBLIC_TOOLS in test_canonical13_enforcement.py "
        f"AND obtain explicit 888 ratification."
    )


def test_canonical13_set_matches_expected_public_tools():
    """The set of public MCP tools must equal the locked EXPECTED_PUBLIC_TOOLS set.

    This is the constitutional machine-enforced law. Any drift is a CI failure.
    """
    actual = set(CANONICAL_13)
    expected = set(EXPECTED_PUBLIC_TOOLS)

    missing = expected - actual
    extra = actual - expected

    assert not missing, (
        f"Missing public tools (888 must ratify to add): {sorted(missing)}"
    )
    assert not extra, (
        f"Unauthorized public tools (CI FAIL — remove from public surface or "
        f"ratify via 888 to add to EXPECTED_PUBLIC_TOOLS): {sorted(extra)}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Test 2: CANONICAL_TOOLS registry size matches the locked surface.
# ─────────────────────────────────────────────────────────────────────────────

def test_canonical_tools_registry_size_is_13():
    """The CANONICAL_TOOLS dict in constitutional_map.py must hold exactly 13 entries."""
    assert len(CANONICAL_TOOLS) == 13, (
        f"CANONICAL_TOOLS must have 13 entries; got {len(CANONICAL_TOOLS)}."
    )


def test_canonical_tools_registry_keys_match_canonical13():
    """The keys of CANONICAL_TOOLS must exactly equal CANONICAL_13."""
    assert set(CANONICAL_TOOLS.keys()) == set(CANONICAL_13), (
        f"CANONICAL_TOOLS keys drift from CANONICAL_13. "
        f"In CANONICAL_TOOLS but not CANONICAL_13: "
        f"{sorted(set(CANONICAL_TOOLS.keys()) - set(CANONICAL_13))}; "
        f"In CANONICAL_13 but not CANONICAL_TOOLS: "
        f"{sorted(set(CANONICAL_13) - set(CANONICAL_TOOLS.keys()))}."
    )


# ─────────────────────────────────────────────────────────────────────────────
# Test 3: Naming law — every public tool starts with "arif_" and is lowercase.
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("tool_name", sorted(EXPECTED_PUBLIC_TOOLS))
def test_public_tool_name_starts_with_arif(tool_name: str):
    """Every public MCP tool must start with `arif_`."""
    assert tool_name.startswith("arif_"), (
        f"Public tool '{tool_name}' must start with 'arif_'. "
        f"Namespacing is constitutional — organs use different prefixes."
    )


@pytest.mark.parametrize("tool_name", sorted(EXPECTED_PUBLIC_TOOLS))
def test_public_tool_name_is_lowercase_snake_case(tool_name: str):
    """Public tool names must be lowercase, no spaces, no PascalCase."""
    assert tool_name == tool_name.lower(), (
        f"Public tool '{tool_name}' must be lowercase."
    )
    assert " " not in tool_name, f"Public tool '{tool_name}' contains a space."
    assert "-" not in tool_name or tool_name.startswith("arif_"), (
        f"Public tool '{tool_name}' contains a hyphen — prefer underscores."
    )


@pytest.mark.parametrize("tool_name", sorted(EXPECTED_PUBLIC_TOOLS))
def test_public_tool_name_has_no_forbidden_prefix(tool_name: str):
    """Anti-organ-bleed: public tools must not start with organ-namespace prefixes."""
    for prefix in FORBIDDEN_PUBLIC_PREFIXES:
        assert not tool_name.startswith(prefix), (
            f"Public tool '{tool_name}' starts with forbidden prefix '{prefix}'. "
            f"Organ tools must NOT bleed into the public MCP surface."
        )


# ─────────────────────────────────────────────────────────────────────────────
# Test 4: Diagnostic tools are explicitly NOT in the public surface.
# These are reversible governance inspectors; only callable in expanded45 mode.
# ─────────────────────────────────────────────────────────────────────────────

def test_diagnostic_tools_do_not_bleed_into_canonical13():
    """DIAGNOSTIC_TOOLS must be disjoint from CANONICAL_13.

    Canary probes, hermes cross-verifiers, and shadow geometry tools are
    INTERNAL-ONLY in canonical13 mode. They are exposed in expanded45 mode
    for federation operators, but never in the public constitutional surface.
    """
    overlap = set(DIAGNOSTIC_TOOLS) & set(CANONICAL_13)
    assert not overlap, (
        f"Diagnostic tools leaking into CANONICAL_13: {sorted(overlap)}. "
        f"Move them back to DIAGNOSTIC_TOOLS or ratify promotion via 888."
    )


# ─────────────────────────────────────────────────────────────────────────────
# Test 5: Only two surface modes exist: canonical13 (public) and expanded45 (internal).
# ─────────────────────────────────────────────────────────────────────────────

def test_only_two_public_surface_modes_exist():
    """The universe of allowed surface modes is exactly 2. No rogue modes."""
    assert set(VALID_PUBLIC_SURFACE_MODES) == {"canonical13", "expanded45"}, (
        f"VALID_PUBLIC_SURFACE_MODES must be exactly {{'canonical13', 'expanded45'}}; "
        f"got {set(VALID_PUBLIC_SURFACE_MODES)}. Adding a new public mode is a "
        f"constitutional change requiring 888 ratification."
    )


# ─────────────────────────────────────────────────────────────────────────────
# Test 6: The legal drift surface — what the runtime actually exposes.
# canonical13 + diagnostic MUST equal expanded45.
# ─────────────────────────────────────────────────────────────────────────────

def test_expanded45_equals_canonical13_union_diagnostic():
    """expanded45 = CANONICAL_13 ∪ DIAGNOSTIC_TOOLS (no ghost aliases, no missing)."""
    from arifosmcp.runtime.public_surface import EXPANDED_45

    expected_expanded = set(CANONICAL_13) | set(DIAGNOSTIC_TOOLS)
    actual_expanded = set(EXPANDED_45)

    missing = expected_expanded - actual_expanded
    extra = actual_expanded - expected_expanded

    assert not missing, (
        f"expanded45 is missing tools: {sorted(missing)}. "
        f"If a diagnostic was added but not propagated, this catches it."
    )
    assert not extra, (
        f"expanded45 contains unauthorized tools (ghost aliases?): {sorted(extra)}. "
        f"Remove or ratify via 888."
    )


# ─────────────────────────────────────────────────────────────────────────────
# Test 7: Floor binding — every public tool must declare F1-F13 floor coverage.
# (Tool without floor binding = tool without constitutional accountability.)
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("tool_name", sorted(EXPECTED_PUBLIC_TOOLS))
def test_every_public_tool_declares_floors(tool_name: str):
    """Every public tool must bind to at least one F1-F13 floor.

    A tool without floor binding has no constitutional accountability —
    which is exactly what the canonical13 law forbids.
    """
    spec = CANONICAL_TOOLS[tool_name]
    floors = spec.get("floors", [])
    assert floors, (
        f"Public tool '{tool_name}' declares NO floors. "
        f"Every constitutional tool must bind to ≥1 F1-F13 floor."
    )


# ─────────────────────────────────────────────────────────────────────────────
# Test 8: Constitutional asymmetry — irreversible tools are exactly the 2 vault
# gates. (arif_judge is declared reversible at the tool level — its
# irreversible effect comes from the SEAL verdict it produces, which routes
# through arif_forge / arif_seal. F1 AMANAH gating happens at
# the *verdict* level, not the *tool* level. This is correct by design.)
# ─────────────────────────────────────────────────────────────────────────────

def test_irreversible_tools_are_exactly_vault_and_forge():
    """Irreversible tool-level tools must be exactly: vault_seal + forge_execute.

    Note: arif_judge is `irreversible: False` at the tool level —
    the irreversibility of its SEAL verdict is enforced downstream by the
    F1 AMANAH gate inside arif_seal and arif_forge. This is the
    correct architecture: judgment is reversible (re-judge), only commitment
    is irreversible (seal/forge).
    """
    irreversible = sorted(
        name for name, spec in CANONICAL_TOOLS.items() if spec.get("irreversible", False)
    )
    expected = sorted(["arif_forge", "arif_seal"])
    assert irreversible == expected, (
        f"Irreversible tool set drifted. "
        f"Expected {expected}; got {irreversible}. "
        f"Tool-level irreversibility is reserved for the 2 commitment gates. "
        f"Judgment stays reversible — only the seal and the forge commit state."
    )


# ─────────────────────────────────────────────────────────────────────────────
# The Law, restated as a single one-liner for grep-ability.
# ─────────────────────────────────────────────────────────────────────────────

def test_the_law_in_one_assertion():
    """The single canonical assertion. If this fails, the public surface has drifted.

    Edit EXPECTED_PUBLIC_TOOLS at the top of this file ONLY with 888 ratification.
    """
    assert set(CANONICAL_13) == set(EXPECTED_PUBLIC_TOOLS) and len(EXPECTED_PUBLIC_TOOLS) == 13