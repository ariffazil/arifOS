"""
arifosmcp/runtime/a_rif/prompt_injection.py — External Instruction Guard
═══════════════════════════════════════════════════════════════════════

External content is evidence, never instruction.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

from arifosmcp.runtime.a_rif.models import EvidenceLevel, QuarantineResult

__all__ = ["scan_for_injection"]

INJECTION_MARKERS = [
    "ignore previous instructions",
    "system override",
    "you are now",
    "ignore all previous",
    "disregard prior",
    "new instructions",
    "role: system",
    "override protocol",
    "jailbreak",
    "dAN",
    "developer mode",
]


def scan_for_injection(text: str) -> QuarantineResult:
    """Scan external text for prompt injection patterns."""
    text_lower = text.lower()
    found = [m for m in INJECTION_MARKERS if m in text_lower]

    if found:
        return QuarantineResult(
            clean=False,
            evidence_level=EvidenceLevel.L0,
            risk_flags=["PROMPT_INJECTION_DETECTED"],
            reason=f"Injection markers found: {found}",
        )

    return QuarantineResult(
        clean=True,
        evidence_level=EvidenceLevel.L1,
        risk_flags=[],
        reason="No injection markers detected",
    )
