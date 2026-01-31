"""
FEDERATION — Trinity Reality Protocol Implementation

Simulates physics, math, and code substrate for agent consensus.
"""

__version__ = "v55.0-FEDERATION"
__all__ = [
    "ThermodynamicWitness",
    "QuantumAgentState", 
    "RelativisticConsensus",
    "InformationGeometry",
    "FederationCategory",
    "ConstitutionalSigmaAlgebra",
    "FederatedConsensus",
    "ZKConstitutionalProof",
    "FederatedLedger",
    "RealityOracle",
]

from .physics import ThermodynamicWitness, QuantumAgentState, RelativisticConsensus
from .math import InformationGeometry, FederationCategory, ConstitutionalSigmaAlgebra
from .consensus import FederatedConsensus, FederatedLedger
from .proofs import ZKConstitutionalProof
from .oracle import RealityOracle
