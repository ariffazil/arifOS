"""
router.py - The Sovereign Intelligence Router (v46 Kernel)

PHILOSOPHY:
    "The Router is the Switchboard. It directs Intent to the appropriate Intelligence
     based on Thermodynamic Constraints (Privacy, Entropy, Latency)."

    It serves as the 'Air Gap' between the User's Intent and the Model's Execution.

AUTHORITY:
    L1_THEORY/canon/00_MASTER_INDEX_v45.md (Sovereign Pivot)

USAGE:
    from arifos.integration.router import IntelligenceRouter, RoutingProfile, Intent

    router = IntelligenceRouter()
    backend, reason = router.route(
        intent=Intent.REASON,
        profile=RoutingProfile.PRIVACY_FIRST
    )
    # Returns: ("local-sealion", "Privacy constraint prevents cloud export")
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Dict, Optional, Tuple


class Intent(Enum):
    """The High-Level Objective of the request."""
    REASON = auto()      # Deep thinking, logic (needs high IQ)
    ACT = auto()         # Desktop automation, tool use (needs precision)
    AUDIT = auto()       # Scanning logs, verifying truth (needs high context/speed)
    CHAT = auto()        # Casual interaction (low stakes)

class RoutingProfile(Enum):
    """The Constraint Configuration for the request."""
    PRIVACY_FIRST = auto()     # ABSOLUTE sovereign privacy (Local only)
    BALANCED = auto()          # Privacy preferred, but can burst to cloud for difficult tasks if sanitized
    CAPABILITY_FIRST = auto()  # Maximum intelligence required (Cloud permitted)
    SPEED_FIRST = auto()       # Latency critical (Local/Cached)

@dataclass
class RouteDecision:
    """The verdict of the Router."""
    provider_id: str       # e.g., 'sealion-27b-local', 'gpt-4o-cloud'
    routing_reason: str    # Why this route was chosen (for audit trail)
    constraints_met: bool  # Whether the request satisfied the laws

class IntelligenceRouter:
    """
    The Central Switchboard for arifOS v46.
    Decouples 'Intent' from 'Model'.
    """

    def __init__(self) -> None:
        # In the future, this will load from ARIFOS_GLOBAL_CONFIG.json
        self._provider_registry: Dict[str, Any] = {
            "sealion": {"type": "local", "privacy": "sovereign", "iq": "medium"},
            "mamba":   {"type": "local", "privacy": "sovereign", "iq": "specialized"},
            "cloud_gpt": {"type": "cloud", "privacy": "public", "iq": "high"},
        }

    def route(self, intent: Intent, profile: RoutingProfile) -> RouteDecision:
        """
        Determines the optimal backend for the given Intent + Profile constraint.

        Logic:
        1. IF profile == PRIVACY_FIRST -> MUST use Local (SEA-LION / Mamba)
           ELSE VOID.
        2. IF intent == AUDIT -> Prefer Mamba (O(N) context).
        3. IF intent == ACT -> Prefer Cloud (until Local LAMs mature).
        """

        # 1. Sovereign Constraint (Privacy)
        if profile == RoutingProfile.PRIVACY_FIRST:
            return RouteDecision(
                provider_id="sealion-27b-local",
                routing_reason="Privacy Constraint: Sovereign traffic only.",
                constraints_met=True
            )

        # 2. Audit Constraint (Thermodynamics)
        if intent == Intent.AUDIT:
            return RouteDecision(
                provider_id="mamba-ssm-local",
                routing_reason="Thermodynamic Constraint: 0(N) auditing required.",
                constraints_met=True
            )

        # 3. Action Constraint (Capability)
        if intent == Intent.ACT:
            if profile == RoutingProfile.PRIVACY_FIRST:
                 # Paradox: Needs smarts but user blocked cloud
                 return RouteDecision(
                     provider_id="sealion-27b-local",
                     routing_reason="Conflict: Local used due to privacy, but capability may be low.",
                     constraints_met=False
                 )
            return RouteDecision(
                provider_id="cloud_gpt",
                routing_reason="Capability Request: Action requires high-fidelity reasoning.",
                constraints_met=True
            )

        # Default fallback
        return RouteDecision(
            provider_id="sealion-27b-local",
            routing_reason="Default: Routing to Sovereign Baseline.",
            constraints_met=True
        )

# Constitutional Interface (Singleton)
router = IntelligenceRouter()
