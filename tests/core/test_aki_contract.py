from __future__ import annotations

import pytest

from core.enforcement.aki_contract import AKIContract, L0KernelGatekeeper, SovereignGate
from core.governance_kernel import AuthorityLevel, GovernanceKernel, GovernanceState


def test_aki_blocks_when_uncertainty_exceeds_threshold() -> None:
    kernel = GovernanceKernel(session_id="aki-omega")
    kernel.update_uncertainty(
        safety_omega=kernel.UNCERTAINTY_THRESHOLD + 0.01,
        display_omega=0.05,
        components={"source_conflict": 0.4},
    )

    approved = AKIContract(kernel).validate_material_action("write_file", {"path": "tmp.txt"})

    assert approved is False
    assert kernel.governance_state == GovernanceState.AWAITING_888


def test_aki_blocks_irreversible_action_without_human_approval() -> None:
    kernel = GovernanceKernel(session_id="aki-hold")
    kernel.update_irreversibility(impact_scope=1.0, recovery_cost=1.0, time_to_reverse=1.0)
    kernel.human_approval_status = "pending"

    approved = AKIContract(kernel).validate_material_action("deploy_prod", {"action": "deploy"})

    assert approved is False
    assert kernel.irreversibility_index > kernel.IRREVERSIBILITY_THRESHOLD


def test_aki_allows_irreversible_action_after_human_approval() -> None:
    kernel = GovernanceKernel(session_id="aki-approved")
    kernel.update_irreversibility(impact_scope=1.0, recovery_cost=1.0, time_to_reverse=1.0)
    kernel.human_approval_status = "approved"

    approved = AKIContract(kernel).validate_material_action("deploy_prod", {"action": "deploy"})

    assert approved is True


def test_aki_blocks_all_actions_while_quarantined() -> None:
    kernel = GovernanceKernel(session_id="aki-quarantine")
    kernel.phoenix_recovery(mode="quarantine")

    approved = AKIContract(kernel).validate_material_action("read_file", {"path": "safe.txt"})

    assert approved is False
    assert kernel.governance_state == GovernanceState.QUARANTINED


def test_aki_degraded_mode_allows_read_and_search_only() -> None:
    kernel = GovernanceKernel(session_id="aki-degraded")
    kernel.phoenix_recovery(mode="degrade")
    aki = AKIContract(kernel)

    assert aki.validate_material_action("read_file", {"path": "safe.txt"}) is True
    assert aki.validate_material_action("get_config", {}) is True
    assert aki.validate_material_action("list_dir", {}) is True
    assert aki.validate_material_action("search_docs", {"query": "vault"}) is True
    assert aki.validate_material_action("audit_rules", {}) is True
    assert aki.validate_material_action("check_vital", {}) is True
    assert aki.validate_material_action("write_file", {"path": "unsafe.txt"}) is False


def test_aki_blocks_when_authority_is_unsafe() -> None:
    kernel = GovernanceKernel(session_id="aki-unsafe")
    kernel.authority_level = AuthorityLevel.UNSAFE_TO_AUTOMATE

    approved = AKIContract(kernel).validate_material_action("any_tool", {})

    assert approved is False


def test_aki_blocks_when_system_heat_high() -> None:
    kernel = GovernanceKernel(session_id="aki-heat")
    # Low reversibility + low energy = high heat
    kernel.update_irreversibility(impact_scope=1.0, recovery_cost=1.0, time_to_reverse=1.0)
    kernel.current_energy = 0.2

    approved = AKIContract(kernel).validate_material_action("any_tool", {})

    assert approved is False


@pytest.mark.asyncio
async def test_sovereign_gate_holds_irreversible_actions() -> None:
    gate = SovereignGate(action_type="delete", resource_path="VAULT999/vault999.jsonl")

    result = await gate.check_approval(context={"actor": "ai"})

    assert result["verdict"] == "888_HOLD"
    assert result["stage"] == "888_HOLD"
    assert result["output"]["authority"] == "888_JUDGE"
    assert result["output"]["ratification_token_required"] is True
    assert "nonce" in result["output"]


@pytest.mark.asyncio
async def test_sovereign_gate_allows_reversible_actions() -> None:
    gate = SovereignGate(action_type="read", resource_path="docs/report.md")

    result = await gate.check_approval(context={"actor": "ai"}, proposed_verdict="SEAL")

    assert result["verdict"] == "SEAL"
    assert result["stage"] == "pre-flight"
    assert result["output"]["approved"] is True


def test_sovereign_gate_signature_check_is_explicit() -> None:
    gate = SovereignGate(action_type="deploy", resource_path="prod")

    assert gate.verify_signature("SEAL") is True
    assert gate.verify_signature("SEAL", nonce="abc") is True
    assert gate.verify_signature("hold") is False


def test_l0_gatekeeper_blocks_protected_paths() -> None:
    assert L0KernelGatekeeper.check_modification_permission("core/shared/floors.py") is False
    assert L0KernelGatekeeper.check_modification_permission("000_THEORY/000_LAW.md") is False
    assert L0KernelGatekeeper.check_modification_permission("pyproject.toml") is False
    assert L0KernelGatekeeper.check_modification_permission("core/kernel/orchestrator.py") is False
    assert L0KernelGatekeeper.check_modification_permission("arifosmcp/runtime/bridge.py") is False
    assert L0KernelGatekeeper.check_modification_permission("core\\kernel\\test.py") is False


def test_l0_gatekeeper_allows_non_protected_paths() -> None:
    assert (
        L0KernelGatekeeper.check_modification_permission("tests/core/test_aki_contract.py") is True
    )


def test_l0_gatekeeper_raises_for_protected_paths() -> None:
    with pytest.raises(PermissionError):
        L0KernelGatekeeper.assert_modification_allowed("core/shared/floors.py")
