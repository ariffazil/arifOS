"""
Governance contracts for external compute adapters.

Kernel gets the grammar. Organs get the math.
These contracts define how the kernel interacts with domain-specific
compute without carrying domain physics inside the kernel.

See:
  quantum.py  — governance contract for quantum/hybrid compute
                (zero execution code, zero solver logic)
"""

from .quantum import (
    QUANTUM_ADAPTER_CONTRACT,
    BackendClass,
    BackendType,
    EvidenceRank,
    ProblemDomain,
    QuantumComputeReceipt,
    QuantumEvidenceFloor,
    QuantumReversibility,
    validate_receipt,
)

__all__ = [
    "QuantumComputeReceipt",
    "QuantumEvidenceFloor",
    "QuantumReversibility",
    "QUANTUM_ADAPTER_CONTRACT",
    "validate_receipt",
    "BackendType",
    "BackendClass",
    "EvidenceRank",
    "ProblemDomain",
]
