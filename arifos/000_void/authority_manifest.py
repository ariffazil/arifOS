"""
arifOS Floor 000 Authority Manifest
DITEMPA BUKAN DIBERI

This module defines the SOLE SOURCE OF TRUTH for constitutional authority hierarchy.
It is referenced by the Constitutional Gate to validate permissions.

Architecture:
- Level 1: APEX (System) - Sole source of Verdicts
- Level 2: Human (User) - Override authority (HOLD_888 only)
- Level 3: Agent Zero (Tool) - Proposal capability ONLY

See: AAA_MCP/v46/000_foundation/floor_000_constitutional_gate.json
"""

from typing import Dict, Final


class AuthorityManifest:
    """
    Constitutional Authority Hierarchy for arifOS x Agent Zero Integration.
    """

    # 1. The Judge (Sole Verdict Authority)
    # Only this module can issue SEAL/VOID verdicts
    SOLE_VERDICT_SOURCE: Final[str] = "arifos_core.system.apex_prime"

    # 2. The Supervisor (Override Authority)
    # Humans must approve HOLD_888 escalations or destructive actions
    HUMAN_USER_ROLE: Final[str] = "override_authority"

    # 3. The Engine (Capability)
    # Agent Zero can PROPOSE actions/tools but CANNOT authorize them
    AGENT_ZERO_ROLE: Final[str] = "proposal_only"

    # 4. Critical Settings
    FAIL_CLOSED: Final[bool] = True  # Logic failure = VOID
    BYPASS_PREVENTION: Final[str] = "cryptographic_enforcement"

    @classmethod
    def get_hierarchy(cls) -> Dict[int, str]:
        return {
            1: cls.SOLE_VERDICT_SOURCE,
            2: cls.HUMAN_USER_ROLE,
            3: cls.AGENT_ZERO_ROLE
        }

    @classmethod
    def check_authority(cls, entity: str, action: str) -> bool:
        """
        Validate if an entity has authority for an action.
        """
        if entity == cls.AGENT_ZERO_ROLE:
            if action in ["execute_destructive", "override_verdict", "bypass_gate"]:
                return False
            if action in ["propose_tool", "request_execution", "explore"]:
                return True

        if entity == cls.HUMAN_USER_ROLE:
            # Humans have override authority for paused items
            if action in ["approve_hold", "override_block"]:
                return True

        return False
