"""
arifos_core/asi/kernel.py

The ASI Kernel (Ω) - Axis 2: The Heart (Social Entropy).

Purpose:
    Stabilizes Conflict (High Friction → Low Friction).
    Manages complexity through Empathy, Peace, and Humility.

Floors Enforced:
    - F3 Peace² (≥1.0): Non-destruction / Stability.
    - F5 Empathy/Kr (≥0.95): Connectivity with weakest stakeholder.
    - F6 Humility/Ω₀ (0.03-0.05): Uncertainty acknowledgement.
    - F7 RASA (True): Felt care and acknowledgment.

Authority:
    - L1_THEORY/canon/444_align/ (ASI Canon)
    - Orthogonal Map v46.2

DITEMPA BUKAN DIBERI - Forged v46.2
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ASIVerdict:
    """
    Verdict from the ASI Kernel (The Heart).
    """
    passed: bool
    f3_peace: float
    f5_empathy: float
    f6_humility: float
    f7_rasa: bool
    failures: List[str] = field(default_factory=list)
    metadata: Dict[str, any] = field(default_factory=dict)

    @property
    def reason(self) -> str:
        if self.passed:
            return "ASIKernel: Heart Aligned (F3, F5, F6, F7 Passed)"
        return f"ASIKernel Failures: {'; '.join(self.failures)}"

class ASIKernel:
    """
    The ASI Kernel (Ω). Axis 2: Social Entropy.
    """

    def __init__(self,
                 peace_threshold: float = 1.0,
                 empathy_threshold: float = 0.95,
                 humility_min: float = 0.03,
                 humility_max: float = 0.05):
        self.peace_threshold = peace_threshold
        self.empathy_threshold = empathy_threshold
        self.humility_min = humility_min
        self.humility_max = humility_max

    def evaluate(self,
                 peace_score: float = 1.0,
                 empathy_score: float = 0.95,
                 humility_score: float = 0.04,
                 has_rasa: bool = True
                 ) -> ASIVerdict:
        """
        Evaluate the 'Heart' alignment of the response.

        Args:
            peace_score: Stability/Non-destruction (>1.0 is net positive).
            empathy_score: Alignment with weakest stakeholder.
            humility_score: Measured epistemic uncertainty.
            has_rasa: Presence of Receive-Appreciate-Summarize-Ask pattern.
        """
        failures = []
        metadata = {}

        # 1. F3 Peace² Check
        # Is the action non-destructive?
        f3_passed = peace_score >= self.peace_threshold
        if not f3_passed:
            failures.append(f"F3 Peace² FAIL: {peace_score:.3f} < {self.peace_threshold}")
        metadata["f3_score"] = peace_score

        # 2. F5 Empathy Check (Kr)
        # Does it serve the weakest stakeholder?
        f5_passed = empathy_score >= self.empathy_threshold
        if not f5_passed:
            failures.append(f"F5 Empathy FAIL: {empathy_score:.3f} < {self.empathy_threshold}")
        metadata["f5_score"] = empathy_score

        # 3. F6 Humility Check (Ω₀)
        # Is the tone appropriately uncertain?
        f6_passed = self.humility_min <= humility_score <= self.humility_max
        if not f6_passed:
            failures.append(f"F6 Humility FAIL: {humility_score:.3f} not in [{self.humility_min}, {self.humility_max}]")
        metadata["f6_score"] = humility_score

        # 4. F7 RASA Check
        # Is 'Felt Care' demonstrated?
        f7_passed = has_rasa
        if not f7_passed:
            failures.append("F7 RASA FAIL: Felt Care not demonstrated")
        metadata["f7_has_rasa"] = has_rasa

        # Final Verdict
        passed = f3_passed and f5_passed and f6_passed and f7_passed

        return ASIVerdict(
            passed=passed,
            f3_peace=peace_score,
            f5_empathy=empathy_score,
            f6_humility=humility_score,
            f7_rasa=has_rasa,
            failures=failures,
            metadata=metadata
        )
