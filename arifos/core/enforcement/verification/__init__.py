"""
arifos.core.verification — Distributed Verification System.

Gap 6 Fix: Multi-source Tri-Witness consensus.
No single source of truth. Only convergence of evidence.

Version: v45.0.4
"""

from .distributed import (
                          AIValidatorWitness,
                          DistributedWitnessSystem,
                          ExternalWitness,
                          HumanWitness,
                          TriWitnessConsensus,
                          WitnessSource,
                          WitnessType,
                          WitnessVote,
)

__all__ = [
    "WitnessType",
    "WitnessVote",
    "WitnessSource",
    "HumanWitness",
    "AIValidatorWitness",
    "ExternalWitness",
    "TriWitnessConsensus",
    "DistributedWitnessSystem",
]
