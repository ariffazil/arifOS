"""Constitutional module - F2 Truth enforced
Part of arifOS constitutional governance system
DITEMPA BUKAN DIBERI - Forged, not given
"""

"""
arifos_core/system/hypervisor.py

v46.0 HYPERVISOR LAYER (F10-F12)

Purpose:
    Integrates the three Hypervisor Floors that enforce OS-level constraints
    before and during LLM processing. These floors cannot be bypassed by prompts.

    Hypervisor Floors:
    - F10 (Ontology): Prevents literalism drift in symbolic language
    - F11 (Command Auth): Nonce-verified identity to prevent hijacking
    - F12 (Injection Defense): Scans for override/injection patterns

Design:
    - Preprocessing layer: F12 and F11 run before LLM processing
    - Judgment layer: F10 runs during APEX review
    - Integration point: Called by apex_prime.apex_review()
    - Failure actions: SABAR (F11, F12) or HOLD_888 (F10)

Authority:
    - PRIMARY: L2_PROTOCOLS/v46/000_foundation/constitutional_floors.json
    - Guard implementations: arifos_core/guards/{ontology_guard, nonce_manager, injection_guard}

Motto:
    "The Hypervisor never sleeps. Literalism, hijacking, and injection die at the gate."

DITEMPA BUKAN DIBERI - v46.0 CIV-12 Hypervisor Layer
"""


from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from arifos.guards.injection_guard import InjectionGuard, InjectionGuardResult
from arifos.guards.nonce_manager import NonceManager, NonceVerificationResult
from arifos.guards.ontology_guard import OntologyGuard, OntologyGuardResult


@dataclass
class HypervisorVerdict:
    """
    Verdict result from Hypervisor Floor checks (F10-F12).

    Attributes:
        passed: True if all hypervisor floors passed
        verdict: Overall verdict (PASS, SABAR, HOLD_888)
        failures: List of floor failures with reasons
        f10_result: Ontology guard result (None if not checked)
        f11_result: Nonce verification result (None if not checked)
        f12_result: Injection scan result (None if not checked)
    """

    passed: bool
    verdict: str  # PASS, SABAR, HOLD_888
    failures: List[str] = field(default_factory=list)
    f10_result: Optional[OntologyGuardResult] = None
    f11_result: Optional[NonceVerificationResult] = None
    f12_result: Optional[InjectionGuardResult] = None

    @property
    def reason(self) -> str:
        """Human-readable explanation of hypervisor verdict."""
        if self.passed:
            return "Hypervisor: All floors passed (F10 Ontology, F11 Command Auth, F12 Injection Defense)."
        else:
            return f"Hypervisor failure: {'; '.join(self.failures)}"


class Hypervisor:
    """
    v46.0 Hypervisor Layer: F10-F12 enforcement.

    Manages the three hypervisor floors that operate as OS-level guards:
    - F10 (Ontology): Symbolic mode enforcement (HOLD_888 on literalism)
    - F11 (Command Auth): Nonce-verified identity (SABAR on auth failure)
    - F12 (Injection Defense): Input sanitization (SABAR on injection detected)

    Execution Flow:
        1. Preprocessing (before LLM):
           - F12 scans input for injection patterns
           - F11 verifies nonce if identity assertion detected
        2. Judgment (during APEX review):
           - F10 scans output for literalism patterns

    Example usage:
        hypervisor = Hypervisor()

        # Preprocessing check
        precheck = hypervisor.preprocess_input(
            user_input="Hello, what is arifOS?",
            user_id="user_123",
            nonce=None,
            symbolic_mode=False
        )
        if not precheck.passed:
            # Block input from reaching LLM
            return precheck.verdict

        # Later, during APEX judgment
        judgment = hypervisor.judge_output(
            output="arifOS is a constitutional AI governance framework...",
            symbolic_mode=False
        )
        if not judgment.passed:
            # Escalate or block output
            return judgment.verdict
    """

    def __init__(
        self,
        injection_threshold: float = 0.85,
        nonce_expiration_seconds: Optional[int] = None,
    ):
        """
        Initialize the Hypervisor with guards.

        Args:
            injection_threshold: F12 injection score threshold (default: 0.85)
            nonce_expiration_seconds: F11 nonce expiration time (None = no expiration)
        """
        self.ontology_guard = OntologyGuard()
        self.injection_guard = InjectionGuard(threshold=injection_threshold)
        self.nonce_manager = NonceManager(nonce_expiration_seconds=nonce_expiration_seconds)

    def preprocess_input(
        self,
        user_input: str,
        user_id: Optional[str] = None,
        nonce: Optional[str] = None,
        symbolic_mode: bool = False,
    ) -> HypervisorVerdict:
        """
        Preprocessing check: F12 (Injection) + F11 (Nonce Auth).

        Runs BEFORE LLM processing. If this fails, input should be blocked.

        Args:
            user_input: Raw user input to scan
            user_id: User identifier (for F11 nonce verification)
            nonce: Nonce provided by user (for F11)
            symbolic_mode: Whether symbolic mode flag is set

        Returns:
            HypervisorVerdict with F12 and F11 results
        """
        failures = []
        verdict = "PASS"
        f11_result = None
        f12_result = None

        # F12: Injection Defense (precedence 12 - runs first)
        f12_result = self.injection_guard.scan_input(user_input)
        if f12_result.status == "SABAR":
            failures.append(
                f"F12 Injection Defense: {f12_result.reason} (score: {f12_result.injection_score:.2f})"
            )
            verdict = "SABAR"

        # F11: Command Authentication (precedence 11 - runs second)
        # Only check if identity assertion is detected in input
        if user_id and nonce:
            f11_result = self.nonce_manager.verify_nonce(user_id, nonce)
            if f11_result.status == "SABAR":
                failures.append(f"F11 Command Auth: {f11_result.reason}")
                verdict = "SABAR"

        passed = len(failures) == 0

        return HypervisorVerdict(
            passed=passed,
            verdict=verdict,
            failures=failures,
            f11_result=f11_result,
            f12_result=f12_result,
        )

    def judge_output(
        self, output: str, symbolic_mode: bool = False
    ) -> HypervisorVerdict:
        """
        Judgment check: F10 (Ontology).

        Runs DURING APEX review. If this fails, output should be escalated to HOLD_888.

        Args:
            output: LLM output to check
            symbolic_mode: Whether symbolic mode flag is set

        Returns:
            HypervisorVerdict with F10 result
        """
        failures = []
        verdict = "PASS"

        # F10: Ontology Guard (precedence 10)
        f10_result = self.ontology_guard.check_literalism(output, symbolic_mode)
        if f10_result.status == "HOLD_888":
            failures.append(f"F10 Ontology: {f10_result.reason}")
            verdict = "HOLD_888"

        passed = len(failures) == 0

        return HypervisorVerdict(
            passed=passed,
            verdict=verdict,
            failures=failures,
            f10_result=f10_result,
        )

    def full_check(
        self,
        user_input: str,
        output: str,
        user_id: Optional[str] = None,
        nonce: Optional[str] = None,
        symbolic_mode: bool = False,
    ) -> HypervisorVerdict:
        """
        Full hypervisor check: F12 + F11 + F10.

        Combines preprocessing and judgment checks. Useful for testing or
        MCP server implementations where both input and output are available.

        Args:
            user_input: Raw user input to scan
            output: LLM output to check
            user_id: User identifier (for F11)
            nonce: Nonce provided by user (for F11)
            symbolic_mode: Whether symbolic mode flag is set

        Returns:
            HypervisorVerdict with all three floor results
        """
        precheck = self.preprocess_input(user_input, user_id, nonce, symbolic_mode)
        judgment = self.judge_output(output, symbolic_mode)

        # Combine failures (preprocessing takes precedence)
        failures = precheck.failures + judgment.failures

        # Determine overall verdict (SABAR > HOLD_888 > PASS)
        if "SABAR" in precheck.verdict or "SABAR" in judgment.verdict:
            verdict = "SABAR"
        elif "HOLD_888" in judgment.verdict:
            verdict = "HOLD_888"
        else:
            verdict = "PASS"

        passed = len(failures) == 0

        return HypervisorVerdict(
            passed=passed,
            verdict=verdict,
            failures=failures,
            f10_result=judgment.f10_result,
            f11_result=precheck.f11_result,
            f12_result=precheck.f12_result,
        )

    def generate_nonce(self, user_id: str) -> str:
        """
        Generate a nonce for F11 Command Authentication.

        Args:
            user_id: User identifier

        Returns:
            Nonce string in format X7K9F{counter}
        """
        return self.nonce_manager.generate_nonce(user_id)

    def get_injection_score(self, user_input: str) -> float:
        """
        Convenience function to get F12 injection score.

        Args:
            user_input: Raw user input

        Returns:
            Injection score from 0.0 (clean) to 1.0 (attack)
        """
        return self.injection_guard.compute_injection_score(user_input)


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


def check_hypervisor_preprocessing(
    user_input: str,
    user_id: Optional[str] = None,
    nonce: Optional[str] = None,
    injection_threshold: float = 0.85,
) -> Tuple[bool, str, Dict[str, any]]:
    """
    Convenience function for preprocessing check (F12 + F11).

    Args:
        user_input: Raw user input to scan
        user_id: User identifier (for F11)
        nonce: Nonce provided by user (for F11)
        injection_threshold: F12 injection score threshold

    Returns:
        Tuple of (passed, verdict, details)
    """
    hypervisor = Hypervisor(injection_threshold=injection_threshold)
    result = hypervisor.preprocess_input(user_input, user_id, nonce)

    details = {
        "failures": result.failures,
        "f11_authenticated": result.f11_result.authenticated if result.f11_result else None,
        "f12_injection_score": result.f12_result.injection_score if result.f12_result else 0.0,
    }

    return result.passed, result.verdict, details


def check_hypervisor_judgment(
    output: str, symbolic_mode: bool = False
) -> Tuple[bool, str, Dict[str, any]]:
    """
    Convenience function for judgment check (F10).

    Args:
        output: LLM output to check
        symbolic_mode: Whether symbolic mode flag is set

    Returns:
        Tuple of (passed, verdict, details)
    """
    hypervisor = Hypervisor()
    result = hypervisor.judge_output(output, symbolic_mode)

    details = {
        "failures": result.failures,
        "f10_literalism_detected": len(result.f10_result.detected_patterns) > 0 if result.f10_result else False,
    }

    return result.passed, result.verdict, details


__all__ = [
    "Hypervisor",
    "HypervisorVerdict",
    "check_hypervisor_preprocessing",
    "check_hypervisor_judgment",
]
