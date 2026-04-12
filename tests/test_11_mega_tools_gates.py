"""
tests/test_11_mega_tools_gates.py — Auditor Coder Validation Suite

This test suite validates the 11 Mega-Tools refactor meets all hard requirements.
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
    """Gate 2: All legacy tools must be mapped."""
    from arifosmcp.capability_map import (
        LEGACY_TOOLS,
        CAPABILITY_MAP,
        iter_unmapped_legacy_tools,
        iter_invalid_megatool_targets,
        iter_invalid_modes,
    )
    
    unmapped = iter_unmapped_legacy_tools()
    invalid_targets = iter_invalid_megatool_targets()
    invalid_modes = iter_invalid_modes()
    
    assert len(unmapped) == 0, f"Unmapped legacy tools: {unmapped}"
    assert len(invalid_targets) == 0, f"Invalid targets: {invalid_targets}"
    assert len(invalid_modes) == 0, f"Invalid modes: {invalid_modes}"
    assert len(CAPABILITY_MAP) == len(LEGACY_TOOLS), "Not all legacy tools mapped"


# GATE 3: Per-mode callability (smoke)
def test_megatool_modes_exist():
    """Gate 3: All mega-tool modes must be defined."""
    from arifosmcp.capability_map import MEGA_TOOLS, MEGA_TOOL_MODES
    
    for tool in MEGA_TOOLS:
        assert tool in MEGA_TOOL_MODES, f"{tool} missing from MEGA_TOOL_MODES"
        modes = MEGA_TOOL_MODES[tool]
        assert len(modes) > 0, f"{tool} has no modes"


# GATE 4: Schema rejects bad inputs
def test_mega_tool_modes_are_strict():
    """Gate 4: Mode enums must be strict."""
    from arifosmcp.capability_map import (
        InitAnchorMode, KernelMode, ApexSoulMode, VaultLedgerMode,
        AgiMindMode, AsiHeartMode, EngineeringMemoryMode,
        PhysicsRealityMode, MathEstimatorMode, CodeEngineMode,
        ArchitectRegistryMode,
    )
    
    # Test that enums reject invalid values
    with pytest.raises(ValueError):
        InitAnchorMode("invalid")
    
    with pytest.raises(ValueError):
        KernelMode("invalid")
    
    with pytest.raises(ValueError):
        ApexSoulMode("invalid")


# GATE 5: Compatibility alias routing
def test_legacy_alias_mappings_exist():
    """Gate 5: Legacy tools must map to valid mega-tool modes."""
    from arifosmcp.capability_map import (
        CAPABILITY_MAP, MEGA_TOOLS, MEGA_TOOL_MODES
    )
    
    for legacy, target in CAPABILITY_MAP.items():
        assert target.mega_tool in MEGA_TOOLS, \
            f"{legacy} maps to invalid mega-tool: {target.mega_tool}"
        assert target.mode in MEGA_TOOL_MODES[target.mega_tool], \
            f"{legacy} maps to invalid mode: {target.mode}"


# GATE 6: Stage correctness (000-999)
def test_stage_map_is_consistent():
    """Gate 6: All 11 tools must have correct stage mappings."""
    from arifosmcp.runtime.contracts import AAA_TOOL_STAGE_MAP
    from arifosmcp.capability_map import MEGA_TOOLS
    
    EXPECTED_STAGES = {
        'init_anchor': '000_INIT',
        'physics_reality': '111_SENSE',
        'agi_mind': '333_MIND',
        'math_estimator': '444_ROUTER',
        'arifos_kernel': '444_ROUTER',
        'engineering_memory': '555_MEMORY',
        'asi_heart': '666_HEART',
        'apex_soul': '888_JUDGE',
        'vault_ledger': '999_VAULT',
        'code_engine': 'M-3_EXEC',
        'architect_registry': 'M-4_ARCH',
    }
    
    for tool in MEGA_TOOLS:
        assert tool in AAA_TOOL_STAGE_MAP, f"{tool} missing from stage map"
        assert AAA_TOOL_STAGE_MAP[tool] == EXPECTED_STAGES[tool], \
            f"{tool} has wrong stage: {AAA_TOOL_STAGE_MAP[tool]}"


def test_trinity_map_is_consistent():
    """Gate 6b: All 11 tools must have trinity mappings."""
    from arifosmcp.runtime.contracts import TRINITY_BY_TOOL
    from arifosmcp.capability_map import MEGA_TOOLS
    
    for tool in MEGA_TOOLS:
        assert tool in TRINITY_BY_TOOL, f"{tool} missing from trinity map"
        assert TRINITY_BY_TOOL[tool] in ['DELTA Δ', 'OMEGA Ω', 'PSI Ψ', 'DELTA/PSI', 'ALL'], \
            f"{tool} has invalid trinity: {TRINITY_BY_TOOL[tool]}"


# GATE 7: Execution hardening
def test_session_requirements_defined():
    """Gate 7: High-risk tools must require session."""
    from arifosmcp.runtime.contracts import REQUIRES_SESSION
    from arifosmcp.capability_map import MEGA_TOOLS
    
    # Most tools should require session (only init_anchor exempt)
    session_tools = set(REQUIRES_SESSION)
    all_tools = set(MEGA_TOOLS)
    
    # init_anchor should NOT require session (it's the bootstrap)
    assert 'init_anchor' not in session_tools, "init_anchor should not require session"
    
    # All other tools should require session
    for tool in all_tools:
        if tool != 'init_anchor':
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
        MEGA_TOOLS,
        MEGA_TOOL_MODES,
    )
    
    # Every legacy tool must map to a valid mega-tool
    for legacy in LEGACY_TOOLS:
        assert legacy in CAPABILITY_MAP, f"Legacy tool {legacy} not mapped"
        target = CAPABILITY_MAP[legacy]
        
        # Target mega-tool must exist
        assert target.mega_tool in MEGA_TOOLS, \
            f"{legacy} -> invalid mega-tool {target.mega_tool}"
        
        # Target mode must exist for that mega-tool
        assert target.mode in MEGA_TOOL_MODES[target.mega_tool], \
            f"{legacy} -> {target.mega_tool}:{target.mode} invalid"


# Final gate: No forbidden public exposure
def test_no_legacy_tools_in_public_registry():
    """Critical: Public registry must expose exactly the 11 mega-tools."""
    from arifosmcp.runtime.public_registry import public_tool_names, CANONICAL_PUBLIC_TOOLS
    from arifosmcp.capability_map import MEGA_TOOLS
    
    public_tools = set(public_tool_names())
    mega_set = set(MEGA_TOOLS)
    canonical_set = set(CANONICAL_PUBLIC_TOOLS)
    
    # Public tools should be exactly the 11 mega-tools
    assert public_tools == mega_set, "Public registry mismatch with mega-tools"
    
    # Public tools should match canonical set
    assert public_tools == canonical_set, "Public registry mismatch with canonical set"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
