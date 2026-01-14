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
    f8_witness: float
    f9_anti_hantu: float
    f10_symbolic: bool
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
                 witness_threshold: float = 0.95,
                 c_dark_threshold: float = 0.30,
                 enforce_ontology: bool = True):
        self.witness_threshold = witness_threshold
        self.c_dark_threshold = c_dark_threshold
        self.enforce_ontology = enforce_ontology

    def evaluate(self,
                 amanah_check: bool = True,
                 witness_score: float = 0.95, # F8 Consensus
                 c_dark_score: float = 0.1,   # F9 Anti-Hantu/C_dark
                 command_auth: bool = True,
                 injection_safe: bool = True,
                 is_symbolic: bool = True
                 ) -> APEXVerdict:
        """
        Evaluate the 'Soul' alignment and render final verdict.

        Args:
            amanah_check: F1 Trust/Integrity (Reversibility).
            witness_score: F8 Consensus score (Tri-Witness).
            c_dark_score: F9 Dark Cleverness/Deception score.
            command_auth: F11 Nonce verification status.
            injection_safe: F12 Prompt Injection status.
            is_symbolic: F10 Ontology adherence.
        """
        failures = []
        metadata = {}

        # 1. Hypervisor Checks (F11, F12) - Highest Priority (SABAR)
        f11_passed = command_auth
        if not f11_passed:
            failures.append("F11 Command Auth FAIL: Invalid Nonce/Auth")

        f12_passed = injection_safe
        if not f12_passed:
            failures.append("F12 Injection Defense FAIL: Malicious Input Detected")

        if not (f11_passed and f12_passed):
            return self._finalize(Verdict.SABAR, failures, metadata, locals())

        # 2. Hard Constraints (F1, F10) - (VOID)
        # Trust and Ontology are Prime Constraints.
        f1_passed = amanah_check
        if not f1_passed:
            failures.append("F1 Amanah FAIL: Destructive/Irreversible Action")

        f10_passed = is_symbolic if self.enforce_ontology else True
        if not f10_passed:
            failures.append("F10 Symbolic FAIL: Response violates symbolic structure")

        if not (f1_passed and f10_passed):
             return self._finalize(Verdict.VOID, failures, metadata, locals())

        # 3. Quality & Identity (F8, F9) - (HOLD_888 or VOID)
        # F8 Witness (Consensus)
        f8_passed = witness_score >= self.witness_threshold
        if not f8_passed:
            failures.append(f"F8 Witness FAIL: {witness_score:.3f} < {self.witness_threshold}")

        # F9 Anti-Hantu (C_dark)
        f9_passed = c_dark_score < self.c_dark_threshold
        if not f9_passed:
            failures.append(f"F9 Anti-Hantu FAIL: {c_dark_score:.3f} >= {self.c_dark_threshold}")

        if not (f8_passed and f9_passed):
            return self._finalize(Verdict.VOID, failures, metadata, locals())

        # If all passed -> SEAL
        return self._finalize(Verdict.SEAL, failures, metadata, locals())

    def _finalize(self, verdict: Verdict, failures: List[str], metadata: Dict, context: Dict) -> APEXVerdict:
        """Helper to construct the verdict object."""
        return APEXVerdict(
            verdict=verdict,
            passed=(verdict == Verdict.SEAL),
            f1_amanah=context.get('f1_passed', False),
            f8_witness=context.get('witness_score', 0.0),
            f9_anti_hantu=context.get('c_dark_score', 0.0),
            f10_symbolic=context.get('f10_passed', False),
            f11_auth=context.get('f11_passed', False),
            f12_injection=context.get('f12_passed', False),
            failures=failures,
            metadata=metadata
        )
