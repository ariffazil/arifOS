"""
test_surface_lock.py — CI Surface Drift Gate
═══════════════════════════════════════════════

Verifies the canonical surface remains locked at startup.
Any drift = VOID. This prevents entropy back-leakage.

Ditempa Bukan Diberi — Forged, Not Given.
"""
from __future__ import annotations

import pytest


def test_canonical_tool_count():
    """Surface must be exactly 13 tools."""
    from arifosmcp.constitutional_map import CANONICAL_TOOLS

    assert len(CANONICAL_TOOLS) == 13, (
        f"Surface drift: expected 13 tools, got {len(CANONICAL_TOOLS)}. VOID."
    )


def test_tool_naming_convention():
    """All tools must follow arif_<noun>_<verb> convention."""
    from arifosmcp.constitutional_map import CANONICAL_TOOLS

    for name in CANONICAL_TOOLS:
        assert name.startswith("arif_"), (
            f"Tool {name} does not follow arif_<noun>_<verb> convention. VOID."
        )


def test_no_legacy_surface():
    """arifos_ legacy prefix must not exist in canonical tools."""
    from arifosmcp.constitutional_map import CANONICAL_TOOLS

    legacy = [n for n in CANONICAL_TOOLS if n.startswith("arifos_")]
    assert not legacy, (
        f"Legacy surface detected: {legacy}. "
        "arifos_ prefix is deprecated. VOID."
    )


def test_canonical_prompts_count():
    """Exactly 8 canonical prompts required."""
    from arifosmcp.prompts import CANONICAL_PROMPTS

    assert len(CANONICAL_PROMPTS) == 8, (
        f"Prompt drift: expected 8, got {len(CANONICAL_PROMPTS)}. VOID."
    )


def test_canonical_resources_count():
    """Exactly 5 canonical resources required."""
    from arifosmcp.resources import CANONICAL_RESOURCES

    assert len(CANONICAL_RESOURCES) == 5, (
        f"Resource drift: expected 5, got {len(CANONICAL_RESOURCES)}. VOID."
    )


def test_all_tools_have_floors():
    """Every tool must have at least one floor binding."""
    from arifosmcp.constitutional_map import CANONICAL_TOOLS

    for name, spec in CANONICAL_TOOLS.items():
        floors = spec.get("floors", [])
        assert len(floors) >= 1, (
            f"Tool {name} has no floor bindings. VOID."
        )


def test_all_tools_have_stage():
    """Every tool must have a Trinity lane and stage."""
    from arifosmcp.constitutional_map import CANONICAL_TOOLS

    for name, spec in CANONICAL_TOOLS.items():
        stage = spec.get("stage")
        lane = spec.get("lane")
        assert stage is not None, f"Tool {name} missing stage. VOID."
        assert lane is not None, f"Tool {name} missing lane. VOID."
        assert lane in ("AGI", "ASI", "APEX"), (
            f"Tool {name} has invalid lane {lane}. VOID."
        )


def test_meta_skills_registered():
    """All 5 meta-skills must be available."""
    from arifosmcp.providers import get_meta_skills_provider

    provider = get_meta_skills_provider()
    skills = provider.list_skills()

    expected = {
        "recursive-self-improvement",
        "orthogonal-abstraction",
        "epistemic-integrity",
        "constitutional-governance",
        "entropy-optimization",
    }

    assert set(skills) == expected, (
        f"Meta-skill drift: expected {expected}, got {set(skills)}. VOID."
    )


def test_version_string():
    """Version must be 2026.04.24-KANON."""
    from arifosmcp import __version__

    assert __version__ == "2026.04.24-KANON", (
        f"Version drift: expected 2026.04.24-KANON, got {__version__}. VOID."
    )
