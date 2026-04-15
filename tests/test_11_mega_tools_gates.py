"""
tests/test_11_mega_tools_gates.py — Auditor Coder Validation Suite (Flat 11-Tool Registry)

This test suite validates the 11 canonical public tools meet all hard requirements.
CI stops on failure.
"""

import pytest
from typing import Any

# GATE 1: Public surface is exactly 11
def test_public_registry_exposes_only_11():
    """Gate 1: /tools must return exactly 11 tools."""
    from arifosmcp.runtime.public_registry import (
        public_tool_names,
        CANONICAL_PUBLIC_TOOLS,
        EXPECTED_TOOL_COUNT,
        verify_no_drift,
    )

    names = public_tool_names()
    drift = verify_no_drift()

    assert len(names) == EXPECTED_TOOL_COUNT, f"Expected {EXPECTED_TOOL_COUNT}, got {len(names)}"
    assert set(names) == CANONICAL_PUBLIC_TOOLS, f"Names don't match canonical set"
    assert drift["ok"], f"Drift detected: {drift}"


# GATE 2: Legacy coverage is 100%
def test_capability_map_100_percent_coverage():
    """Gate 2: All legacy tools must be mapped to canonical handlers."""
    from arifosmcp.capability_map import (
        LEGACY_TOOLS,
        CAPABILITY_MAP,
        CANONICAL_TOOL_HANDLERS,
        iter_unmapped_legacy_tools,
        iter_invalid_megatool_targets,
        iter_invalid_modes,
    )
    from arifosmcp.runtime.tools import CANONICAL_TOOL_HANDLERS as ALL_TOOL_HANDLERS

    unmapped = iter_unmapped_legacy_tools()
    invalid_targets = iter_invalid_megatool_targets()
    invalid_modes = iter_invalid_modes()

    assert len(unmapped) == 0, f"Unmapped legacy tools: {unmapped}"
    assert len(invalid_targets) == 0, f"Invalid targets: {invalid_targets}"
    assert len(invalid_modes) == 0, f"Invalid modes: {invalid_modes}"
    assert len(CAPABILITY_MAP) >= len(LEGACY_TOOLS), "Not all legacy tools mapped"

    # Every legacy tool must map to a valid handler (public or internal)
    for legacy, target in LEGACY_TOOLS.items():
        assert target in ALL_TOOL_HANDLERS, f"{legacy} maps to invalid target: {target}"


# GATE 3: Per-mode callability (smoke)
def test_canonical_tool_modes_exist():
    """Gate 3: All canonical tools must have modes defined."""
    from arifosmcp.runtime.contracts import TOOL_MODES
    from arifosmcp.capability_map import CANONICAL_TOOL_HANDLERS

    for tool in CANONICAL_TOOL_HANDLERS:
        assert tool in TOOL_MODES, f"{tool} missing from TOOL_MODES"
        modes = TOOL_MODES[tool]
        assert len(modes) > 0, f"{tool} has no modes"


# GATE 4: Schema rejects bad inputs
def test_tool_modes_are_strict():
    """Gate 4: Mode sets must be strict non-empty sets."""
    from arifosmcp.runtime.contracts import TOOL_MODES
    from arifosmcp.capability_map import CANONICAL_TOOL_HANDLERS

    for tool in CANONICAL_TOOL_HANDLERS:
        modes = TOOL_MODES[tool]
        assert isinstance(modes, set), f"{tool} modes must be a set"
        assert len(modes) > 0, f"{tool} must have at least one mode"
        # All modes should be strings
        for mode in modes:
            assert isinstance(mode, str), f"{tool} mode {mode!r} is not a string"


# GATE 5: Compatibility alias routing
def test_legacy_alias_mappings_exist():
    """Gate 5: Legacy tools must map to valid canonical tool names."""
    from arifosmcp.capability_map import CAPABILITY_MAP
    from arifosmcp.runtime.tools import CANONICAL_TOOL_HANDLERS as ALL_TOOL_HANDLERS

    for legacy, target in CAPABILITY_MAP.items():
        assert isinstance(target, str), f"{legacy} maps to non-string target: {target}"
        assert target in ALL_TOOL_HANDLERS, \
            f"{legacy} maps to invalid canonical tool: {target}"


# GATE 6: Stage correctness (000-999)
def test_stage_map_is_consistent():
    """Gate 6: All 11 canonical tools must have correct stage mappings."""
    from arifosmcp.runtime.contracts import AAA_TOOL_STAGE_MAP
    from arifosmcp.capability_map import CANONICAL_TOOL_HANDLERS

    EXPECTED_STAGES = {
        "arifos_init": "000_INIT",
        "arifos_sense": "111_SENSE",
        "arifos_mind": "333_MIND",
        "arifos_kernel": "444_ROUTER",
        "arifos_heart": "666_HEART",
        "arifos_ops": "777_OPS",
        "arifos_judge": "888_JUDGE",
        "arifos_memory": "555_MEMORY",
        "arifos_vault": "999_VAULT",
        "arifos_forge": "010_FORGE",
        "arifos_gateway": "888_OMEGA",
    }

    for tool in CANONICAL_TOOL_HANDLERS:
        assert tool in AAA_TOOL_STAGE_MAP, f"{tool} missing from stage map"
        assert AAA_TOOL_STAGE_MAP[tool] == EXPECTED_STAGES[tool], \
            f"{tool} has wrong stage: {AAA_TOOL_STAGE_MAP[tool]}"


def test_trinity_map_is_consistent():
    """Gate 6b: All 11 canonical tools must have trinity mappings."""
    from arifosmcp.runtime.contracts import TRINITY_BY_TOOL
    from arifosmcp.capability_map import CANONICAL_TOOL_HANDLERS

    for tool in CANONICAL_TOOL_HANDLERS:
        assert tool in TRINITY_BY_TOOL, f"{tool} missing from trinity map"
        assert TRINITY_BY_TOOL[tool] in ["DELTA Δ", "OMEGA Ω", "PSI Ψ", "DELTA/PSI", "ALL"], \
            f"{tool} has invalid trinity: {TRINITY_BY_TOOL[tool]}"


# GATE 7: Execution hardening
def test_session_requirements_defined():
    """Gate 7: High-risk tools must require session."""
    from arifosmcp.runtime.contracts import REQUIRES_SESSION
    from arifosmcp.capability_map import CANONICAL_TOOL_HANDLERS

    session_tools = set(REQUIRES_SESSION)
    all_tools = set(CANONICAL_TOOL_HANDLERS.keys())

    # arifos_init should NOT require session (it's the bootstrap)
    assert "arifos_init" not in session_tools, "arifos_init should not require session"

    # All other canonical tools should require session
    for tool in all_tools:
        if tool != "arifos_init":
            assert tool in session_tools, f"{tool} should require session"


def test_contracts_verify_passes():
    """Gate 7b: Contract verification must pass."""
    from arifosmcp.runtime.contracts import verify_contract

    result = verify_contract()
    assert result["ok"], f"Contract verification failed: {result}"
    assert all(result["checks"].values()), f"Some checks failed: {result['checks']}"


# Integration test: Full capability map validation
def test_full_capability_map_integration():
    """Integration: Validate entire capability map end-to-end."""
    from arifosmcp.capability_map import (
        LEGACY_TOOLS,
        CAPABILITY_MAP,
        CANONICAL_TOOL_HANDLERS,
    )
    from arifosmcp.runtime.tools import CANONICAL_TOOL_HANDLERS as ALL_TOOL_HANDLERS
    from arifosmcp.runtime.contracts import TOOL_MODES

    # Every legacy tool must map to a valid handler
    for legacy in LEGACY_TOOLS:
        assert legacy in CAPABILITY_MAP, f"Legacy tool {legacy} not mapped"
        target = CAPABILITY_MAP[legacy]

        # Target must be a string in canonical handlers
        assert isinstance(target, str), f"{legacy} -> non-string target {target!r}"
        assert target in ALL_TOOL_HANDLERS, \
            f"{legacy} -> invalid canonical tool {target}"

        # Target must have at least one mode defined
        assert target in TOOL_MODES, f"{legacy} -> {target} missing from TOOL_MODES"
        assert len(TOOL_MODES[target]) > 0, f"{legacy} -> {target} has no modes"


# Final gate: No forbidden public exposure
def test_no_legacy_tools_in_public_registry():
    """Critical: Public registry must expose exactly the 11 canonical tools."""
    from arifosmcp.runtime.public_registry import public_tool_names, CANONICAL_PUBLIC_TOOLS
    from arifosmcp.capability_map import CANONICAL_TOOL_HANDLERS

    public_tools = set(public_tool_names())
    canonical_set = set(CANONICAL_TOOL_HANDLERS.keys())
    expected_set = set(CANONICAL_PUBLIC_TOOLS)

    # Public tools should be exactly the 11 canonical tools
    assert public_tools == canonical_set, "Public registry mismatch with canonical handlers"

    # Public tools should match canonical set
    assert public_tools == expected_set, "Public registry mismatch with canonical set"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
