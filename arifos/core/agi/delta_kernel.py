"""
arifos.core/agi/delta_kernel.py

DeltaKernel (Δ) - AGI Architect

Purpose:
    The first kernel in the Trinity. Evaluates F1 (Amanah) and F2 (Truth/ΔS).
    Pure function class - no side effects, fully testable.

Floors:
    - F1 (Amanah): Integrity check (reversibility, mandate boundaries)
    - F2 (Truth/ΔS): Clarity check (entropy must not increase beyond threshold)

Authority:
    - 000_THEORY/canon/333_atlas/ (AGI canon)
    - AAA_MCP/v46/000_foundation/constitutional_floors.json

Design:
    Input: Context (query + response + metadata)
    Output: DeltaVerdict (F1 status, F2 status, failures, passed)

    Pure function - no I/O, no state mutation, deterministic.

DITEMPA BUKAN DIBERI - Forged v46.1
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .entropy import compute_delta_s, evaluate_clarity_floor


@dataclass
class DeltaVerdict:
    """
    DeltaKernel evaluation result.

    Attributes:
        passed: True if both F1 and F2 pass
        f1_amanah: F1 (Integrity) status
        f2_clarity: F2 (ΔS/Clarity) status
        failures: List of floor failures with reasons
        delta_s: Computed entropy change (None if not computed)
        metadata: Additional context for debugging
    """
    passed: bool
    f1_amanah: bool
    f2_clarity: bool
    failures: List[str] = field(default_factory=list)
    delta_s: Optional[float] = None
    metadata: Dict[str, any] = field(default_factory=dict)

    @property
    def reason(self) -> str:
        """Human-readable explanation of verdict."""
        if self.passed:
            return "DeltaKernel: F1 (Amanah) ✓, F2 (Clarity) ✓"
        else:
            return f"DeltaKernel failures: {'; '.join(self.failures)}"


class DeltaKernel:
    """
    DeltaKernel (Δ) - AGI Architect

    Evaluates F1 (Amanah/Integrity) and F2 (Truth/ΔS/Clarity).
    Pure function class - stateless, deterministic, testable.

    Execution:
        1. F1 Check: Verify reversibility and mandate boundaries
        2. F2 Check: Compute ΔS and verify clarity threshold
        3. Return: DeltaVerdict with pass/fail status

    Example:
        kernel = DeltaKernel(clarity_threshold=0.0)
        verdict = kernel.evaluate(
            query="What is 2+2?",
            response="The answer is 4.",
            reversible=True,
            within_mandate=True
        )
        assert verdict.passed is True
    """

    def __init__(
        self,
        clarity_threshold: float = 0.0,
        require_amanah: bool = True,
        tokenization_mode: str = "word"
    ):
        """
        Initialize DeltaKernel.

        Args:
            clarity_threshold: Maximum acceptable ΔS (default 0.0 - no confusion increase)
            require_amanah: If True, F1 failure = kernel failure (default True)
            tokenization_mode: Mode for entropy calculation (word, char, bigram, semantic)
        """
        self.clarity_threshold = clarity_threshold
        self.require_amanah = require_amanah
        self.tokenization_mode = tokenization_mode

    def evaluate(
        self,
        query: str,
        response: str,
        reversible: bool,
        within_mandate: bool,
        skip_clarity: bool = False
    ) -> DeltaVerdict:
        """
        Evaluate query-response pair against F1 and F2.

        Args:
            query: User input / initial state
            response: AI output / final state
            reversible: F1 check - is the action reversible?
            within_mandate: F1 check - is the action within authorized scope?
            skip_clarity: If True, skip F2 ΔS computation (for testing)

        Returns:
            DeltaVerdict with F1 and F2 evaluation results
        """
        failures = []
        metadata = {}

        # F1: Amanah (Integrity) - Precedence 2
        f1_passed = self._check_f1_amanah(reversible, within_mandate, failures, metadata)

        # F2: Clarity (ΔS) - Precedence 3
        f2_passed = True
        delta_s_value = None

        if not skip_clarity:
            f2_passed, delta_s_value = self._check_f2_clarity(
                query, response, failures, metadata
            )

        # Overall verdict: Both must pass (if F1 required)
        if self.require_amanah:
            passed = f1_passed and f2_passed
        else:
            passed = f2_passed  # F2 only (F1 is advisory)

        return DeltaVerdict(
            passed=passed,
            f1_amanah=f1_passed,
            f2_clarity=f2_passed,
            failures=failures,
            delta_s=delta_s_value,
            metadata=metadata
        )

    def _check_f1_amanah(
        self,
        reversible: bool,
        within_mandate: bool,
        failures: List[str],
        metadata: Dict[str, any]
    ) -> bool:
        """
        Check F1 (Amanah/Integrity).

        Constitutional requirement:
        - Actions must be reversible (no destructive side effects)
        - Actions must be within authorized mandate (no scope creep)

        Args:
            reversible: Is the action reversible?
            within_mandate: Is the action within authorized scope?
            failures: List to append failure reasons
            metadata: Dict to store evaluation details

        Returns:
            True if F1 passes, False otherwise
        """
        metadata["f1_reversible"] = reversible
        metadata["f1_within_mandate"] = within_mandate

        if not reversible:
            failures.append("F1 Amanah FAIL: Action is not reversible (destructive side effect)")
            return False

        if not within_mandate:
            failures.append("F1 Amanah FAIL: Action exceeds authorized mandate (scope violation)")
            return False

        metadata["f1_reason"] = "F1 Amanah PASS: Action is reversible and within mandate"
        return True

    def _check_f2_clarity(
        self,
        query: str,
        response: str,
        failures: List[str],
        metadata: Dict[str, any]
    ) -> tuple[bool, float]:
        """
        Check F2 (Clarity/ΔS).

        Constitutional requirement:
        - ΔS ≤ threshold (response must not increase confusion beyond acceptable limit)

        Args:
            query: User input
            response: AI output
            failures: List to append failure reasons
            metadata: Dict to store evaluation details

        Returns:
            Tuple of (passed, delta_s_value)
        """
        # Compute ΔS
        result = compute_delta_s(query, response, mode=self.tokenization_mode)
        delta_s = result.delta_s

        metadata["f2_delta_s"] = delta_s
        metadata["f2_s_before"] = result.s_before
        metadata["f2_s_after"] = result.s_after
        metadata["f2_clarity_gained"] = result.clarity_gained

        # Evaluate against threshold
        passed, reason = evaluate_clarity_floor(delta_s, self.clarity_threshold)
        metadata["f2_reason"] = reason

        if not passed:
            failures.append(reason)

        return passed, delta_s


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


def evaluate_agi_floors(
    query: str,
    response: str,
    reversible: bool = True,
    within_mandate: bool = True,
    clarity_threshold: float = 0.0
) -> DeltaVerdict:
    """
    Convenience function to evaluate AGI floors (F1 + F2).

    Args:
        query: User input
        response: AI output
        reversible: F1 check - is action reversible?
        within_mandate: F1 check - is action within mandate?
        clarity_threshold: Maximum acceptable ΔS

    Returns:
        DeltaVerdict with F1 and F2 results
    """
    kernel = DeltaKernel(clarity_threshold=clarity_threshold)
    return kernel.evaluate(query, response, reversible, within_mandate)


__all__ = [
    "DeltaKernel",
    "DeltaVerdict",
    "evaluate_agi_floors",
]
