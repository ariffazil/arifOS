"""
test_surface_lock.py — CI Surface Drift Gate
═══════════════════════════════════════════════

Verifies the canonical surface remains locked at startup.
Any drift = VOID. This prevents entropy back-leakage.

Ditempa Bukan Diberi — Forged, Not Given.
"""

from __future__ import annotations


def test_canonical_tool_count():
    """The semantic Kernel ABI remains exactly eight capabilities."""
    from arifosmcp.runtime.public_surface import KERNEL_ABI_8

    assert len(KERNEL_ABI_8) == len(set(KERNEL_ABI_8)) == 8


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
    assert not legacy, f"Legacy surface detected: {legacy}. arifos_ prefix is deprecated. VOID."


def test_canonical_prompts_count():
    """Prompt inventory is independent from the Kernel ABI and must remain unique."""
    from arifosmcp.prompts import CANONICAL_PROMPTS

    assert CANONICAL_PROMPTS
    assert len(CANONICAL_PROMPTS) == len(set(CANONICAL_PROMPTS))


def test_canonical_resources_count():
    """Resource inventory is independent from the Kernel ABI and must remain unique."""
    from arifosmcp.resources import CANONICAL_RESOURCES

    assert CANONICAL_RESOURCES
    assert len(CANONICAL_RESOURCES) == len(set(CANONICAL_RESOURCES))


def test_all_tools_have_floors():
    """Every constitutional tool must have at least one floor binding."""
    from arifosmcp.constitutional_map import CANONICAL_TOOLS, list_probe_tools

    probes = set(list_probe_tools())
    for name, spec in CANONICAL_TOOLS.items():
        if name in probes:
            continue
        floors = spec.get("floors", [])
        assert len(floors) >= 1, f"Tool {name} has no floor bindings. VOID."


def test_all_tools_have_stage():
    """Every tool must have a Trinity lane and stage."""
    from arifosmcp.constitutional_map import CANONICAL_TOOLS

    allowed_lanes = {"AGI", "ASI", "APEX", "SOVEREIGN"}
    for name, spec in CANONICAL_TOOLS.items():
        stage = spec.get("stage")
        lane = spec.get("lane")
        assert stage is not None, f"Tool {name} missing stage. VOID."
        assert lane is not None, f"Tool {name} missing lane. VOID."
        lane_val = getattr(lane, "value", lane)
        assert lane_val in allowed_lanes, f"Tool {name} has invalid lane {lane}. VOID."


def test_meta_skills_registered():
    """All 5 meta-skills must be available."""
    from arifosmcp.providers import get_meta_skills_provider

    provider = get_meta_skills_provider()
    skills = provider.list_skills()

    expected = {
        "RSI-recursive-improvement",
        "orthogonal-abstraction",
        "epistemic-integrity",
        "constitutional-governance",
        "entropy-optimization",
    }

    assert set(skills) == expected, (
        f"Meta-skill drift: expected {expected}, got {set(skills)}. VOID."
    )


def test_version_string():
    """Version must match the current sealed runtime release."""
    from arifosmcp import __version__

    assert __version__ == "2026.06.11-FIQHGEOM", (
        f"Version drift: expected 2026.06.11-FIQHGEOM, got {__version__}. VOID."
    )
