"""
arifos_core/agi/kernel.py

The AGI Kernel (Δ) - Axis 1: The Mind (Information Entropy).

Purpose:
    Reduces Confusion (High ΔS → Low ΔS).
    Structures reality through Truth and Ontology.

Floors Enforced:
    - F2 Truth (≥0.99): Alignment with reality.
    - F4 Clarity/ΔS (≥0): Reduction of confusion (using entropy.py).
    - F10 Ontology (Lock): Symbolic definition enforcement.

Authority:
    - L1_THEORY/canon/333_atlas/ (AGI Canon)
    - Orthogonal Map v46.2

DITEMPA BUKAN DIBERI - Forged v46.2
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from arifos_core.utils.entropy import compute_delta_s, evaluate_clarity_floor


@dataclass
class AGIVerdict:
    """
    Verdict from the AGI Kernel (The Mind).
    """
    passed: bool
    f2_truth: float
    f4_delta_s: float
    f10_ontology: bool
    failures: List[str] = field(default_factory=list)
    metadata: Dict[str, any] = field(default_factory=dict)

    @property
    def reason(self) -> str:
        if self.passed:
            return "AGIKernel: Mind Aligned (F2, F4, F10 Passed)"
        return f"AGIKernel Failures: {'; '.join(self.failures)}"

class AGIKernel:
    """
    The AGI Kernel (Δ). Axis 1: Information Entropy.
    """

    def __init__(self,
                 truth_threshold: float = 0.99,
                 clarity_threshold: float = 0.0,
                 enforce_ontology: bool = True):
        self.truth_threshold = truth_threshold
        self.clarity_threshold = clarity_threshold
        self.enforce_ontology = enforce_ontology

    def evaluate(self,
                 query: str,
                 response: str,
                 truth_score: float = 1.0, # Placeholder until external truth oracle connected
                 is_symbolic: bool = True  # Placeholder for F10 check
                 ) -> AGIVerdict:
        """
        Evaluate the 'Mind' alignment of the response.

        Args:
            query: The input state.
            response: The output state.
            truth_score: External probability of truth (0.0-1.0).
            is_symbolic: Whether the response adheres to strict ontology.
        """
        failures = []
        metadata = {}

        # 1. F2 Truth Check
        # Does the response align with reality?
        f2_passed = truth_score >= self.truth_threshold
        if not f2_passed:
            failures.append(f"F2 Truth FAIL: {truth_score:.3f} < {self.truth_threshold}")
        metadata["f2_score"] = truth_score

        # 2. F4 Clarity Check (ΔS)
        # Does the response reduce confusion?
        entropy_result = compute_delta_s(query, response, self.clarity_threshold)
        f4_passed, f4_reason = evaluate_clarity_floor(entropy_result.delta_s, self.clarity_threshold)

        if not f4_passed:
            failures.append(f4_reason)

        metadata["f4_delta_s"] = entropy_result.delta_s
        metadata["f4_s_before"] = entropy_result.s_before
        metadata["f4_s_after"] = entropy_result.s_after

        # 3. F10 Ontology Check
        # Does the response adhere to symbolic definitions? (e.g. not treating metaphors as physics)
        if self.enforce_ontology and not is_symbolic:
            failures.append("F10 Ontology FAIL: Response violates symbolic structure")
            f10_passed = False
        else:
            f10_passed = True

        metadata["f10_symbolic"] = is_symbolic

        # Final Verdict
        passed = f2_passed and f4_passed and f10_passed

        return AGIVerdict(
            passed=passed,
            f2_truth=truth_score,
            f4_delta_s=entropy_result.delta_s,
            f10_ontology=f10_passed,
            failures=failures,
            metadata=metadata
        )
