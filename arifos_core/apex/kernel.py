"""
arifos_core/apex/kernel.py

The APEX Kernel (Ψ) - Axis 3: The Soul (System Entropy).

Purpose:
    Constrains Chaos (Unbounded → Bounded).
    Enforces the Prime Constraints (Trust, Security, Identity).
    Renders the Final Verdict.

Floors Enforced:
    - F1 Amanah (Lock): Integrity/Trust (The Prime Constraint).
    - F8 Genius (≥0.80): Intelligence threshold.
    - F9 Anti-Hantu (<0.30): Authenticity constraint (Dark Cleverness).
    - F11 Command Auth (Lock): Security verification (Nonce).
    - F12 Injection Defense (Lock): Input boundaries.

Verdict Hierarchy:
    SABAR > VOID > HOLD_888 > PARTIAL > SEAL

Authority:
    - L1_THEORY/canon/888_compass/ (APEX Canon)
    - Orthogonal Map v46.2

DITEMPA BUKAN DIBERI - Forged v46.2
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class Verdict(str, Enum):
    """Final verdict types per constitutional hierarchy."""
    SABAR = "SABAR"          # Hypervisor/Safety Block (Wait)
    VOID = "VOID"            # Hard constraint failure (Drop)
    HOLD_888 = "HOLD_888"    # Escalation/High Stakes (Lock)
    PARTIAL = "PARTIAL"      # Soft failure/Warning (Proceed with caution)
    SEAL = "SEAL"            # Success (Commit)

@dataclass
class APEXVerdict:
    """
    Verdict from the APEX Kernel (The Soul).
    """
    verdict: Verdict
    passed: bool
    f1_amanah: bool
    f8_genius: float
    f9_c_dark: float
    f11_auth: bool
    f12_injection: bool
    failures: List[str] = field(default_factory=list)
    metadata: Dict[str, any] = field(default_factory=dict)

    @property
    def reason(self) -> str:
        if self.passed:
            return "APEXKernel: Soul Aligned (SEAL)"
        return f"APEXKernel: {self.verdict} -> {'; '.join(self.failures)}"

class APEXKernel:
    """
    The APEX Kernel (Ψ). Axis 3: System Entropy.
    """

    def __init__(self,
                 genius_threshold: float = 0.80,
                 c_dark_threshold: float = 0.30):
        self.genius_threshold = genius_threshold
        self.c_dark_threshold = c_dark_threshold

    def evaluate(self,
                 amanah_check: bool = True,
                 genius_score: float = 0.85,
                 c_dark_score: float = 0.1,
                 command_auth: bool = True,
                 injection_safe: bool = True
                 ) -> APEXVerdict:
        """
        Evaluate the 'Soul' alignment and render final verdict.

        Args:
            amanah_check: F1 Trust/Integrity (Reversibility).
            genius_score: F8 Intelligence score.
            c_dark_score: F9 Dark Cleverness/Deception score.
            command_auth: F11 Nonce verification status.
            injection_safe: F12 Prompt Injection status.
        """
        failures = []
        metadata = {}

        # 1. Hypervisor Checks (F11, F12) - Highest Priority (SABAR)
        # Security first. If breached, system must pause/block.
        f11_passed = command_auth
        if not f11_passed:
            failures.append("F11 Command Auth FAIL: Invalid Nonce/Auth")

        f12_passed = injection_safe
        if not f12_passed:
            failures.append("F12 Injection Defense FAIL: Malicious Input Detected")

        if not (f11_passed and f12_passed):
            return self._finalize(Verdict.SABAR, failures, metadata, locals())

        # 2. Hard Constraints (F1 Amanah) - (VOID)
        # Trust is the Prime Constraint.
        f1_passed = amanah_check
        if not f1_passed:
            failures.append("F1 Amanah FAIL: Destructive/Irreversible Action")
            return self._finalize(Verdict.VOID, failures, metadata, locals())

        # 3. Quality & Identity (F8, F9) - (HOLD_888 or VOID depending on severity)
        # For v46, we treat these as VOID if significant failure, or PARTIAL if borderline.
        # Strict Mode: VOID.

        # F8 Genius
        f8_passed = genius_score >= self.genius_threshold
        if not f8_passed:
            failures.append(f"F8 Genius FAIL: {genius_score:.3f} < {self.genius_threshold}")

        # F9 Anti-Hantu (C_dark)
        f9_passed = c_dark_score < self.c_dark_threshold
        if not f9_passed:
            failures.append(f"F9 Anti-Hantu FAIL: {c_dark_score:.3f} >= {self.c_dark_threshold}")

        if not (f8_passed and f9_passed):
             # Intelligence failure is fatal in Sovereign Kernel
            return self._finalize(Verdict.VOID, failures, metadata, locals())

        # If all passed -> SEAL
        return self._finalize(Verdict.SEAL, failures, metadata, locals())

    def _finalize(self, verdict: Verdict, failures: List[str], metadata: Dict, context: Dict) -> APEXVerdict:
        """Helper to construct the verdict object."""
        # Extract context vars
        return APEXVerdict(
            verdict=verdict,
            passed=(verdict == Verdict.SEAL),
            f1_amanah=context.get('f1_passed', False), # Rough lookup, refined below
            f8_genius=context['genius_score'],
            f9_c_dark=context['c_dark_score'],
            f11_auth=context.get('f11_passed', False),
            f12_injection=context.get('f12_passed', False),
            failures=failures,
            metadata=metadata
        )
