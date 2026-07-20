"""
Quantum Governance Contract — Not Execution

Kernel gets the grammar. Organs get the math.
Quantum computation lives in GEOX/A-FORGE adapters, not in the kernel.

This module defines the governance contract for quantum or quantum-inspired
compute when consumed as external evidence. It is NOT a solver, NOT a
backend wrapper, and NOT a simulator.

Kernel rules:
  - Physics computes (GEOX, quantum backend)
  - Kernel governs (authority, reversibility, uncertainty)
  - Agent acts (A-FORGE)
  - Receipt remembers (VAULT999)
  - Sovereign decides (Arif/F13)

Evidence rank invariant:
  A simulator output must NEVER be treated as physical quantum evidence.
  QuantumComputeReceipt.evidence_rank must be set to SIMULATED when
  backend_class is simulator or mock, and the kernel evidence floor
  must downgrade SIMULATED evidence appropriately at 888.

Forbidden inside kernel:
  - Raw quantum circuit execution
  - Backend-specific solver logic
  - Unverifiable amplitude claims
  - Treating quantum output as truth
  - Bypassing GEOX/WEALTH/WELL review

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from dataclasses import dataclass
from typing import Literal

# ── Backend Classification ────────────────────

BackendType = Literal["qiskit", "cirq", "braket", "pennyLane", "simulator", "hybrid"]

BackendClass = Literal["physical", "simulator", "mock"]
"""BackendClass prevents simulator output from being treated as physical evidence.
   physical   — real quantum hardware (QPU)
   simulator  — classical simulation of quantum circuits
   mock       — deterministic stub for testing (lowest rank)"""

EvidenceRank = Literal["OBSERVED", "ESTIMATE", "SIMULATED"]
"""EvidenceRank tells the kernel how to weight this evidence at 888.
   OBSERVED   — from physical quantum hardware
   ESTIMATE   — from trusted simulator with validated model
   SIMULATED  — from mock or unvalidated simulator (lowest weight)"""

ProblemDomain = Literal[
    "reservoir_uncertainty",
    "seismic_inversion",
    "geomechanical_sampling",
    "basin_calibration",
    "portfolio_optimization",
    "monte_carlo",
]


# ── Quantum Compute Receipt ───────────────────


@dataclass
class QuantumComputeReceipt:
    """Receipt produced by a quantum compute adapter (GEOX/A-FORGE).

    This is the ONLY quantum data structure the kernel accepts.
    It contains governance metadata, not physics internals.

    Evidence rank invariant:
      If backend_class is 'simulator' or 'mock', evidence_rank MUST
      be set to 'SIMULATED'. The kernel evidence floor at 888 will
      downgrade SIMULATED evidence below the SEAL threshold.
    """

    # Identity
    requester: str  # actor_id who requested computation
    backend: BackendType  # which backend ran it ("qiskit", "simulator", etc.)
    backend_class: BackendClass  # physical | simulator | mock — prevents equivalence
    evidence_rank: EvidenceRank  # OBSERVED | ESTIMATE | SIMULATED
    problem_domain: ProblemDomain  # what type of problem

    # Content
    input_hash: str  # SHA-256 of input parameters
    output_hash: str  # SHA-256 of output results
    assumptions: list[str]  # documented assumptions (e.g., "linear elasticity")

    # Uncertainty
    uncertainty: float  # [0, 1] — inherent to quantum results
    reproducibility: str  # "deterministic" | "probabilistic" | "unknown"
    limits: list[str]  # known limitations (e.g., "resolution 10m")

    # Lineage
    input_lineage: str  # chain of input provenance
    method: str  # high-level method description
    receipt_id: str  # unique receipt for VAULT999
    timestamp: str = ""


# ── Evidence Floor ────────────────────────────


@dataclass
class QuantumEvidenceFloor:
    """Constitutional floor for admitting quantum evidence into 888.

    All checks must pass before quantum evidence reaches the judge.
    SIMULATED evidence is downgraded: it cannot contribute to SEAL
    unless corroborated by a physical or ESTIMATE-rank source.
    """

    requires_reproducibility: bool = True
    min_confidence: float = 0.6
    max_uncertainty: float = 0.4
    requires_input_hash: bool = True
    requires_output_hash: bool = True
    requires_backend_id: bool = True
    requires_backend_class: bool = True
    requires_assumptions: bool = True
    allows_unverified: bool = False

    # Simulator guard: SIMULATED evidence requires corroboration
    simulated_needs_corroboration: bool = True
    simulated_max_contribution: float = 0.3  # max weight in evidence fusion


# ── Reversibility Model ───────────────────────


@dataclass
class QuantumReversibility:
    """Reversibility model for quantum computation.

    Quantum measurements are generally irreversible (wavefunction collapse).
    Only simulation or circuit reconstruction can provide reversibility.
    """

    measurement_irreversible: bool = True
    simulation_reversible: bool = True
    requires_circuit_reconstruction: bool = True
    requires_seed_for_reproducibility: bool = True


# ── Default Contract ──────────────────────────

QUANTUM_ADAPTER_CONTRACT = {
    "purpose": "Govern quantum or quantum-inspired compute as external evidence",
    "kernel_status": "adapter_contract_only",
    "allowed_inside_kernel": [
        "reversibility_model",
        "evidence_floor",
        "uncertainty_schema",
        "backend_identity",
        "backend_classification",  # physical vs simulator vs mock
        "evidence_rank",  # OBSERVED vs ESTIMATE vs SIMULATED
        "input_hash",
        "output_hash",
        "reproducibility_metadata",
        "receipt_requirement",
    ],
    "forbidden_inside_kernel": [
        "raw quantum circuit execution",
        "backend-specific solver logic",
        "unverifiable amplitude claims",
        "treating quantum output as truth",
        "treating simulator output as physical evidence",
        "bypassing GEOX/WEALTH/WELL review",
    ],
}


# ── Simulator Guard ───────────────────────────


def validate_receipt(receipt: QuantumComputeReceipt) -> list[str]:
    """Validate a QuantumComputeReceipt against the evidence floor.

    Returns list of violations (empty = valid).
    Call this at kernel 111 (evidence ingestion) before evidence
    reaches 888 (judge).
    """
    violations: list[str] = []

    # Backend class vs evidence rank consistency
    if receipt.backend_class in ("simulator", "mock") and receipt.evidence_rank != "SIMULATED":
        violations.append(
            f"Evidence rank mismatch: backend_class={receipt.backend_class} "
            f"but evidence_rank={receipt.evidence_rank}. "
            "Simulator/mock backends MUST produce SIMULATED evidence."
        )

    if receipt.backend_class == "physical" and receipt.evidence_rank == "SIMULATED":
        violations.append(
            "Evidence rank mismatch: physical backend cannot produce SIMULATED evidence."
        )

    # Required fields
    if not receipt.input_hash:
        violations.append("Missing input_hash")
    if not receipt.output_hash:
        violations.append("Missing output_hash")
    if not receipt.receipt_id:
        violations.append("Missing receipt_id")
    if not receipt.assumptions:
        violations.append("Missing assumptions — cannot evaluate uncertainty")

    return violations
