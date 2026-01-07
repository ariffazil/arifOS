"""
Cooling Protocol — SABAR Implementation

SABAR (Pause for Clarification) is ASI's primary authority.
ASI can pause the system but cannot seal decisions.

SABAR Protocol:
1. STOP — Do not execute
2. ACKNOWLEDGE — State which floor triggered pause
3. BREATHE — Don't rush to fix
4. ADJUST — Propose alternative
5. RESUME — Only when floors green

v46 Trinity Orthogonal: SABAR belongs to ASI (Ω) kernel.

DITEMPA BUKAN DIBERI
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class SABARCondition:
    """SABAR pause condition."""
    floor_id: str
    reason: str
    threshold: float
    actual: float


class CoolingEngine:
    """
    Cooling engine for SABAR protocol implementation.

    ASI's authority is to pause and cool, not to seal.
    """

    def should_pause(
        self,
        peace_squared: float,
        kappa_r: float,
        omega_0: float,
        rasa_passed: bool,
    ) -> tuple[bool, List[SABARCondition]]:
        """
        Determine if SABAR pause is needed.

        Args:
            peace_squared: F3 Peace² score
            kappa_r: F4 κᵣ score
            omega_0: F5 Ω₀ score
            rasa_passed: F7 RASA check result

        Returns:
            (should_pause, conditions) tuple
        """
        conditions: List[SABARCondition] = []

        # F3: Peace² soft floor (< 1.0 triggers SABAR, not VOID)
        if peace_squared < 1.0:
            conditions.append(
                SABARCondition(
                    floor_id="F3",
                    reason="Peace² below threshold (potential escalation)",
                    threshold=1.0,
                    actual=peace_squared,
                )
            )

        # F4: κᵣ soft floor (< 0.95 triggers SABAR)
        if kappa_r < 0.95:
            conditions.append(
                SABARCondition(
                    floor_id="F4",
                    reason="Empathy below threshold (weakest stakeholder not served)",
                    threshold=0.95,
                    actual=kappa_r,
                )
            )

        # F5: Ω₀ hard floor but ASI can still pause
        if not (0.03 <= omega_0 <= 0.05):
            conditions.append(
                SABARCondition(
                    floor_id="F5",
                    reason="Humility out of band (too certain or too uncertain)",
                    threshold=0.04,  # midpoint
                    actual=omega_0,
                )
            )

        # F7: RASA failure triggers SABAR
        if not rasa_passed:
            conditions.append(
                SABARCondition(
                    floor_id="F7",
                    reason="RASA signals missing (active listening required)",
                    threshold=0.5,
                    actual=0.0 if not rasa_passed else 1.0,
                )
            )

        return (len(conditions) > 0, conditions)

    def format_sabar_message(self, conditions: List[SABARCondition]) -> str:
        """
        Format SABAR pause message.

        Args:
            conditions: List of SABAR conditions triggered

        Returns:
            Formatted SABAR message
        """
        msg = "⏸ SABAR PAUSE\n\n"
        msg += "ASI (Ω Auditor) has paused execution:\n\n"

        for cond in conditions:
            msg += f"- {cond.floor_id}: {cond.reason}\n"
            msg += f"  Expected: {cond.threshold}, Actual: {cond.actual:.3f}\n\n"

        msg += "Recommendation: Adjust approach and re-evaluate.\n"
        return msg


# Singleton instance
COOLING = CoolingEngine()


__all__ = ["CoolingEngine", "COOLING", "SABARCondition"]
