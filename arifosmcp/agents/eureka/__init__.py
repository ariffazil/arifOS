"""
Engineering Eureka Agent — substrate-aware engineering forge agent.

Doctrine: DITEMPA BUKAN DIBERI — Engineering intelligence is forged through substrate discipline, not granted by LLM eloquence.

The Eureka Agent is the substrate-aware execution arm of the arifOS federation.
It combines:
- substrate intelligence (Pydantic, OTel, OPA, Sigstore, Graphiti, NetworkX)
- engineering eureka detection (cross-domain pattern recognition)
- AGI-level reasoning (typed contracts, evidence chain, fail-closed)

Constitutional binding:
- F1 AMANAH: every action is reversible or explicitly approved
- F2 TRUTH: every claim carries epistemic label
- F4 CLARITY: reduce entropy, never amplify it
- F7 HUMILITY: confidence cap 0.90
- F8 LAW: respect system boundaries
- F9 ANTI-HANTU: this is a tool, not a being
- F11 AUDIT: every consequential action leaves a trace
- F13 SOVEREIGN: Arif holds final veto
"""

from .agent import EngineeringEurekaAgent, EurekaResult, EurekaSignal
from .signals import EngineeringSignal, SignalDetector
from .substrate import SubstrateCapability, SubstrateIndex
from .validator import EngineeringClaim, EngineeringClaimValidator, ValidationVerdict

__all__ = [
    "EngineeringEurekaAgent",
    "EurekaSignal",
    "EurekaResult",
    "SubstrateIndex",
    "SubstrateCapability",
    "SignalDetector",
    "EngineeringSignal",
    "EngineeringClaimValidator",
    "EngineeringClaim",
    "ValidationVerdict",
]
