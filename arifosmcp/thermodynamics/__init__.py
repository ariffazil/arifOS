"""
arifOS Thermodynamics — Entropy Investment Engine

BIJAKSANA v37Ω-E: Governed entropy pricing for constitutional adjudication.

Every proposed action has an entropy pathway.
Every actor has an entropy-pricing capacity (B).
Every system has an entropy buffer (Φ).

DITEMPA BUKAN DIBERI — Forged, Not Given. 2026-08-01.
"""

from arifosmcp.thermodynamics.engine import (
    BufferStatus,
    EntropyPathway,
    EntropyReceipt,
    ThermodynamicVerdict,
    backpropagate_entropy_gradient,
    classify_actor_buffer,
    compute_entropy_pathway,
    compute_governance_loss,
    compute_phi_delta,
    forward_propagate_phi,
    render_entropy_receipt,
    thermodynamic_judge,
)

__all__ = [
    "EntropyPathway",
    "EntropyReceipt",
    "ThermodynamicVerdict",
    "BufferStatus",
    "compute_entropy_pathway",
    "classify_actor_buffer",
    "thermodynamic_judge",
    "render_entropy_receipt",
    "compute_phi_delta",
    "forward_propagate_phi",
    "backpropagate_entropy_gradient",
    "compute_governance_loss",
]
