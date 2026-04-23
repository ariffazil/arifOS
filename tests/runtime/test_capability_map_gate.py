from __future__ import annotations

import pytest

from arifosmcp.capability_map import (
    CAPABILITY_MAP,
    LEGACY_TOOLS,
    MEGA_TOOLS,
    MEGA_TOOL_MODES,
    iter_invalid_megatool_targets,
    iter_invalid_modes,
    iter_unmapped_legacy_tools,
    iter_unknown_tools_in_map,
)


def test_megatools_are_exactly_11():
    assert len(MEGA_TOOLS) == 11, f"Expected 11 mega-tools, got {len(MEGA_TOOLS)}"
    assert len(set(MEGA_TOOLS)) == 11, "Duplicate mega-tool names found"


def test_legacy_surface_coverage_is_100_percent():
    unmapped = iter_unmapped_legacy_tools()
    assert not unmapped, (
        "❌ CAPABILITY_MAP coverage is incomplete. Unmapped legacy tool(s):\n"
        + "\n".join(f"- {t}" for t in unmapped)
    )


def test_no_typos_or_phantom_entries_in_map():
    unknown = iter_unknown_tools_in_map()
    assert not unknown, (
        "❌ CAPABILITY_MAP contains tool(s) not in LEGACY_TOOLS. Typos or dead entries:\n"
        + "\n".join(f"- {t}" for t in unknown)
    )


def test_all_targets_are_canonical_megatools():
    bad = iter_invalid_megatool_targets()
    assert not bad, "❌ CAPABILITY_MAP points to non-canonical mega-tools:\n" + "\n".join(f"- {x}" for x in bad)


def test_all_modes_are_valid_for_their_megatool():
    bad = iter_invalid_modes()
    assert not bad, "❌ CAPABILITY_MAP contains invalid mode mappings:\n" + "\n".join(f"- {x}" for x in bad)


def test_every_megatool_has_modes_declared():
    missing = [t for t in MEGA_TOOLS if t not in MEGA_TOOL_MODES]
    assert not missing, "❌ Some mega-tools have no declared mode set:\n" + "\n".join(f"- {t}" for t in missing)


@pytest.mark.parametrize("megatool", list(MEGA_TOOL_MODES.keys()))
def test_modes_are_nonempty_strings(megatool: str):
    modes = MEGA_TOOL_MODES[megatool]
    assert modes, f"{megatool} must have at least one mode"
    assert all(isinstance(m, str) and m.strip() for m in modes), f"{megatool} has invalid mode(s): {modes}"
