"""
Organ Contract Matrix — defines what each organ can and cannot do.
═══════════════════════════════════════════════════════════════════════════════

IRON LAW 1 (SINGLE_SPINE): Every packet through arifOS.
No organ may act outside its contract.

Each organ has a contract defining:
  - allowed_stages: which metabolic stages it can execute
  - allowed_tools: which tool modes it can invoke
  - max_action_class: highest action class permitted
  - forbidden: what it must NEVER do
  - requires_lease: whether it needs a lease for mutation

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class OrganContract:
    """Contract defining an organ's capabilities and boundaries."""

    organ_id: str
    port: int
    role: str
    allowed_stages: list[str]
    allowed_tool_modes: list[str]
    max_action_class: str  # OBSERVE, DRAFT, MUTATE, EXTERNAL_SIDE_EFFECT, IRREVERSIBLE
    forbidden: list[str]
    requires_lease: bool = False
    can_seal: bool = False
    can_judge: bool = False
    description: str = ""


# ═══════════════════════════════════════════════════════════════════════════════
# ORGAN CONTRACTS
# ═══════════════════════════════════════════════════════════════════════════════

ARIFOS_CONTRACT = OrganContract(
    organ_id="arifOS",
    port=8088,
    role="Constitutional Kernel",
    allowed_stages=["000", "111", "333", "555", "666", "777", "999"],
    allowed_tool_modes=["init", "observe", "think", "route", "judge", "forge", "compose", "seal"],
    max_action_class="IRREVERSIBLE",
    forbidden=["bypass_floors", "self_authorize", "skip_judge"],
    requires_lease=False,
    can_seal=True,
    can_judge=True,
    description="Sovereign kernel — owns constitution, judgment, vault, seal",
)

AAA_CONTRACT = OrganContract(
    organ_id="AAA",
    port=3001,
    role="Control Plane",
    allowed_stages=["000", "111", "333"],
    allowed_tool_modes=["init", "observe", "think", "route", "compose"],
    max_action_class="DRAFT",
    forbidden=["judge", "seal", "mutate_files", "shell_exec"],
    requires_lease=False,
    can_seal=False,
    can_judge=False,
    description="Control plane — agent registry, A2A, cockpit",
)

AFORGE_CONTRACT = OrganContract(
    organ_id="A-FORGE",
    port=7071,
    role="Execution Shell",
    allowed_stages=["777"],
    allowed_tool_modes=["forge", "execute", "shell", "filesystem", "git", "docker"],
    max_action_class="EXTERNAL_SIDE_EFFECT",
    forbidden=["judge", "seal", "self_authorize"],
    requires_lease=True,
    can_seal=False,
    can_judge=False,
    description="Execution shell — build, deploy, execute under lease",
)

GEOX_CONTRACT = OrganContract(
    organ_id="GEOX",
    port=8081,
    role="Earth Intelligence",
    allowed_stages=["111", "333"],
    allowed_tool_modes=["observe", "think", "basin", "seismic", "petrophysics", "prospect"],
    max_action_class="OBSERVE",
    forbidden=["judge", "seal", "mutate_files", "shell_exec"],
    requires_lease=False,
    can_seal=False,
    can_judge=False,
    description="Earth intelligence — seismic, petrophysics, basin analysis",
)

WEALTH_CONTRACT = OrganContract(
    organ_id="WEALTH",
    port=18082,
    role="Capital Intelligence",
    allowed_stages=["111", "333"],
    allowed_tool_modes=["observe", "think", "conservation", "flow", "entropy", "wisdom"],
    max_action_class="OBSERVE",
    forbidden=["judge", "seal", "mutate_files", "shell_exec", "move_capital"],
    requires_lease=False,
    can_seal=False,
    can_judge=False,
    description="Capital intelligence — NPV, risk, conservation. EVIDENCE_ONLY.",
)

WELL_CONTRACT = OrganContract(
    organ_id="WELL",
    port=18083,
    role="Human Readiness",
    allowed_stages=["111", "333"],
    allowed_tool_modes=["observe", "think", "assess", "validate", "guard"],
    max_action_class="OBSERVE",
    forbidden=["judge", "seal", "mutate_files", "shell_exec", "diagnose"],
    requires_lease=False,
    can_seal=False,
    can_judge=False,
    description="Human readiness — vitality, fatigue, dignity. REFLECT_ONLY.",
)

# ═══════════════════════════════════════════════════════════════════════════════
# CONTRACT REGISTRY
# ═══════════════════════════════════════════════════════════════════════════════

ORGAN_CONTRACTS: dict[str, OrganContract] = {
    "arifOS": ARIFOS_CONTRACT,
    "AAA": AAA_CONTRACT,
    "A-FORGE": AFORGE_CONTRACT,
    "GEOX": GEOX_CONTRACT,
    "WEALTH": WEALTH_CONTRACT,
    "WELL": WELL_CONTRACT,
}


def get_organ_contract(organ_id: str) -> OrganContract | None:
    """Get the contract for an organ."""
    return ORGAN_CONTRACTS.get(organ_id)


def check_organ_permission(
    organ_id: str,
    stage: str,
    tool_mode: str,
    action_class: str,
) -> tuple[bool, str]:
    """
    Check if an organ is permitted to execute a given stage/tool/action.

    Returns (permitted, reason).
    """
    contract = ORGAN_CONTRACTS.get(organ_id)
    if contract is None:
        return False, f"Unknown organ: {organ_id}"

    if stage not in contract.allowed_stages:
        return False, f"{organ_id} not permitted at stage {stage}"

    if tool_mode not in contract.allowed_tool_modes:
        return False, f"{organ_id} not permitted to use tool mode {tool_mode}"

    # Check action class hierarchy
    class_order = [
        "OBSERVE",
        "ANALYZE",
        "DRAFT",
        "SIMULATE",
        "MUTATE",
        "EXTERNAL_SIDE_EFFECT",
        "IRREVERSIBLE",
    ]
    try:
        requested_idx = class_order.index(action_class)
        max_idx = class_order.index(contract.max_action_class)
        if requested_idx > max_idx:
            return (
                False,
                f"{organ_id} max action class is {contract.max_action_class}, requested {action_class}",
            )
    except ValueError:
        return False, f"Unknown action class: {action_class}"

    # Check forbidden list
    for forbidden_item in contract.forbidden:
        if forbidden_item in tool_mode or forbidden_item in action_class:
            return False, f"{organ_id} forbidden: {forbidden_item}"

    return True, "PERMITTED"


def list_all_contracts() -> dict[str, dict[str, Any]]:
    """List all organ contracts as dicts."""
    return {
        oid: {
            "port": c.port,
            "role": c.role,
            "max_action": c.max_action_class,
            "stages": c.allowed_stages,
        }
        for oid, c in ORGAN_CONTRACTS.items()
    }


__all__ = [
    "OrganContract",
    "ORGAN_CONTRACTS",
    "ARIFOS_CONTRACT",
    "AAA_CONTRACT",
    "AFORGE_CONTRACT",
    "GEOX_CONTRACT",
    "WEALTH_CONTRACT",
    "WELL_CONTRACT",
    "get_organ_contract",
    "check_organ_permission",
    "list_all_contracts",
]
