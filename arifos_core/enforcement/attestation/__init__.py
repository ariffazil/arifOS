"""
arifos_core.attestation — Agent Capability Attestation.

Gap 4 Fix: AAA-compliant agent attestation system.
Every agent must declare capabilities and constraints with proof.

Version: v45.0.4
"""

from .manifest import (
                       ARIF_AGI_ATTESTATION,
                       ARIF_APEX_ATTESTATION,
                       ARIF_ASI_ATTESTATION,
                       AgentAttestation,
                       AttestationRegistry,
                       CapabilityDeclaration,
                       ConstraintDeclaration,
)

__all__ = [
    "CapabilityDeclaration",
    "ConstraintDeclaration",
    "AgentAttestation",
    "AttestationRegistry",
    "ARIF_AGI_ATTESTATION",
    "ARIF_ASI_ATTESTATION",
    "ARIF_APEX_ATTESTATION",
]
