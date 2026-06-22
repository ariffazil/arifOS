"""
tests/test_contract_conformance.py — SSOT-Derived Conformance Tests
═══════════════════════════════════════════════════════════════════

These tests verify that the runtime matches the compiled SSOT contract.
Source of truth: contracts/tools.yaml → compiler.py → generated/validators_runtime.py

Run: python -m pytest tests/test_contract_conformance.py -v

DITEMPA BUKAN DIBERI — Tested, not assumed.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest


# ═══════════════════════════════════════════════════════════════════════════════
# TEST: Contract Registry Completeness (SSOT is authority, not CANONICAL_TOOLS)
# ═══════════════════════════════════════════════════════════════════════════════


def test_contract_registry_has_all_ssot_tools():
    """CONTRACT_REGISTRY must have exactly 22 tools (the SSOT universe)."""
    from contracts.generated.validators_runtime import CONTRACT_REGISTRY

    # SSOT: 13 canonical + 1 diagnostic + 7 federated + 1 sanctioned = 22
    assert len(CONTRACT_REGISTRY) == 22, (
        f"CONTRACT_REGISTRY has {len(CONTRACT_REGISTRY)} tools, expected 22"
    )


def test_all_contracts_have_required_fields():
    """Every contract must have the SSOT-derived required fields."""
    from contracts.generated.validators_runtime import CONTRACT_REGISTRY

    required_fields = [
        "canonical_name", "role", "axis", "pipeline_stage",
        "contract_class", "mutation_class", "modes",
        "reversibility", "blast_radius", "authority_required",
        "channel", "hold_conditions", "denial_codes", "audit_events",
        "witness_requirements", "contract_version",
    ]
    for name, contract in CONTRACT_REGISTRY.items():
        for field in required_fields:
            assert hasattr(contract, field), (
                f"Contract '{name}' missing required field '{field}'"
            )


# ═══════════════════════════════════════════════════════════════════════════════
# TEST: Governance Invariants
# ═══════════════════════════════════════════════════════════════════════════════


def test_irreversible_tools_require_sovereign_authority():
    """Irreversible tools must require sovereign authority OR have hold conditions."""
    from contracts.generated.validators_runtime import CONTRACT_REGISTRY, Authority

    for name, contract in CONTRACT_REGISTRY.items():
        if contract.irreversible:
            # Must have hold conditions or require sovereign authority
            has_hold = len(contract.hold_conditions) > 0
            is_sovereign = contract.authority_required == Authority.SOVEREIGN
            assert has_hold or is_sovereign, (
                f"Irreversible tool '{name}' must have hold_conditions "
                f"or require sovereign authority"
            )


def test_seal_class_tools_have_hold_conditions():
    """SEAL-class tools must have hold conditions (verdict_token, epoch_id, etc.)."""
    from contracts.generated.validators_runtime import CONTRACT_REGISTRY

    for name, contract in CONTRACT_REGISTRY.items():
        if contract.contract_class == "seal":
            assert len(contract.hold_conditions) > 0, (
                f"SEAL-class tool '{name}' has no hold conditions"
            )


def test_gateway_class_tools_require_plan():
    """Gateway-class tools must have requires_plan=True."""
    from contracts.generated.validators_runtime import CONTRACT_REGISTRY

    for name, contract in CONTRACT_REGISTRY.items():
        if contract.contract_class == "gateway":
            assert contract.requires_plan, (
                f"Gateway-class tool '{name}' must have requires_plan=True"
            )


def test_all_tools_have_audit_events():
    """Every tool must have at least one audit event."""
    from contracts.generated.validators_runtime import CONTRACT_REGISTRY

    for name, contract in CONTRACT_REGISTRY.items():
        assert len(contract.audit_events) > 0, (
            f"Tool '{name}' has no audit events"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# TEST: Validation Logic
# ═══════════════════════════════════════════════════════════════════════════════


def test_validate_tool_call_accepts_valid_call():
    """Valid tool call with all requirements met should pass."""
    from contracts.generated.validators_runtime import validate_tool_call

    result = validate_tool_call(
        tool_name="arif_observe",
        mode="search",
        actor_authority="public",
        has_envelope=True,
    )
    assert result.valid is True
    assert result.denial_code is None


def test_validate_tool_call_rejects_unknown_tool():
    """Unknown tool should be rejected with CONTRACT_DRIFT."""
    from contracts.generated.validators_runtime import validate_tool_call, DenialCode

    result = validate_tool_call(
        tool_name="nonexistent_tool",
        mode="run",
        has_envelope=True,
    )
    assert result.valid is False
    assert result.denial_code == DenialCode.CONTRACT_DRIFT


def test_validate_tool_call_rejects_bad_mode():
    """Invalid mode should be rejected."""
    from contracts.generated.validators_runtime import validate_tool_call, DenialCode

    result = validate_tool_call(
        tool_name="arif_observe",
        mode="nonexistent_mode",
        has_envelope=True,
    )
    assert result.valid is False
    assert result.denial_code == DenialCode.SCHEMA_VALIDATION_FAILED


def test_validate_tool_call_rejects_missing_envelope():
    """Missing envelope should be rejected."""
    from contracts.generated.validators_runtime import validate_tool_call, DenialCode

    result = validate_tool_call(
        tool_name="arif_observe",
        mode="search",
        has_envelope=False,
    )
    assert result.valid is False
    assert result.denial_code == DenialCode.ENVELOPE_MISSING


def test_validate_tool_call_rejects_insufficient_authority():
    """Public actor on sovereign tool should be rejected."""
    from contracts.generated.validators_runtime import validate_tool_call, DenialCode

    result = validate_tool_call(
        tool_name="arif_judge",
        mode="judge",
        actor_authority="public",
        has_envelope=True,
    )
    assert result.valid is False
    assert result.denial_code == DenialCode.AUTHORITY_INSUFFICIENT


def test_validate_tool_call_rejects_missing_plan_for_gateway():
    """Gateway tool without plan should be rejected."""
    from contracts.generated.validators_runtime import validate_tool_call, DenialCode, CONTRACT_REGISTRY

    # Find a gateway-class tool
    gateway_tools = [
        name for name, c in CONTRACT_REGISTRY.items()
        if c.contract_class == "gateway"
    ]
    if gateway_tools:
        gw = gateway_tools[0]
        result = validate_tool_call(
            tool_name=gw,
            mode=CONTRACT_REGISTRY[gw].modes[0],
            actor_authority="operator",
            has_envelope=True,
            has_plan=False,
        )
        assert result.valid is False
        assert result.denial_code == DenialCode.PLAN_MISSING


# ═══════════════════════════════════════════════════════════════════════════════
# TEST: Drift Detection
# ═══════════════════════════════════════════════════════════════════════════════


def test_find_orphan_tools():
    """Orphan detector should find tools not in contracts."""
    from contracts.generated.validators_runtime import find_orphan_tools

    orphans = find_orphan_tools(["arif_observe", "unknown_tool_1", "unknown_tool_2"])
    assert "unknown_tool_1" in orphans
    assert "unknown_tool_2" in orphans
    assert "arif_observe" not in orphans


def test_find_contract_drift():
    """Drift detector should find missing runtime tools."""
    from contracts.generated.validators_runtime import find_contract_drift

    drift = find_contract_drift(["arif_observe"])
    # arif_observe should NOT be in drift (it's registered)
    assert "arif_observe" not in drift
    # Other tools should be in drift
    assert len(drift) > 0


# ═══════════════════════════════════════════════════════════════════════════════
# TEST: Axis Coverage (replaces floor coverage — SSOT uses axes, not floors)
# ═══════════════════════════════════════════════════════════════════════════════


def test_all_axes_covered_by_at_least_one_tool():
    """Every governance axis must be covered by at least one tool."""
    from contracts.generated.validators_runtime import CONTRACT_REGISTRY

    all_axes = {contract.axis for contract in CONTRACT_REGISTRY.values()}
    # Critical axes that must be covered
    critical_axes = {"000_KERNEL", "111_SENSE", "333_THINK", "888_JUDGE", "999_SEAL"}
    covered = critical_axes.intersection(all_axes)
    assert covered == critical_axes, (
        f"Critical axes not covered: {critical_axes - covered}"
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
