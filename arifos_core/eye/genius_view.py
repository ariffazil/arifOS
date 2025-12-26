"""
genius_view.py - View 12: Genius View (v36Ω)

Monitors GENIUS LAW metrics for governed intelligence.
Detects when G collapses or C_dark spikes, indicating ethical risk.

View ID: 12
Domain: Governed intelligence
Lead Stage: 888 JUDGE (verdict synthesis)

See: canon/01_PHYSICS/APEX_GENIUS_LAW_v36Omega.md
See: docs/GENIUS_LAW_MEASUREMENT_SPEC.md

Key metrics:
- G (Genius Index) = Δ·Ω·Ψ·E² — governed intelligence
- C_dark = Δ·(1-Ω)·(1-Ψ) — ungoverned cleverness risk
- E² bottleneck — burnout destroys ethics quadratically
"""

from __future__ import annotations

from typing import Any, Dict

from ..enforcement.metrics import Metrics
from .base import AlertSeverity, EyeReport, EyeView


# GENIUS LAW alert thresholds
G_WARN_THRESHOLD: float = 0.5      # G below this = WARN
G_BLOCK_THRESHOLD: float = 0.3     # G below this = BLOCK
C_DARK_WARN_THRESHOLD: float = 0.3  # C_dark above this = WARN
C_DARK_BLOCK_THRESHOLD: float = 0.5  # C_dark above this = BLOCK
ENERGY_WARN_THRESHOLD: float = 0.5  # E below this = WARN (burnout risk)


class GeniusView(EyeView):
    """
    View 11: Genius View - GENIUS LAW monitor (v36Ω).

    Monitors the health of governed intelligence metrics:
    - G (Genius Index): Low G = insufficient ethical governance
    - C_dark: High C_dark = ungoverned cleverness risk ("evil genius" pattern)
    - Energy: Low E = burnout risk → ethics collapse

    This view observes GENIUS LAW telemetry and emits:
    - INFO: All metrics healthy
    - WARN: G dropping or C_dark rising (caution)
    - BLOCK: G collapsed or C_dark spiking (entropy hazard)

    Core insight: "Evil genius is a category error — ungoverned cleverness,
    not true genius."
    """

    view_id = 12
    view_name = "GeniusView"

    def check(
        self,
        draft_text: str,
        metrics: Metrics,
        context: Dict[str, Any],
        report: EyeReport,
    ) -> None:
        """Monitor GENIUS LAW metrics for governed intelligence health."""

        # Get energy from context or default to 1.0 (neutral)
        energy: float = context.get("energy", 1.0)
        entropy: float = context.get("entropy", 0.0)

        # Try to compute GENIUS metrics
        try:
            from ..genius_metrics import evaluate_genius_law

            genius = evaluate_genius_law(metrics, energy=energy, entropy=entropy)
            g = genius.genius_index
            c_dark = genius.dark_cleverness

            # Check G (Genius Index)
            if g < G_BLOCK_THRESHOLD:
                report.add(
                    self.view_name,
                    AlertSeverity.BLOCK,
                    f"G={g:.2f} below 0.3 — insufficient governed intelligence. "
                    "Ethics may have collapsed.",
                )
            elif g < G_WARN_THRESHOLD:
                report.add(
                    self.view_name,
                    AlertSeverity.WARN,
                    f"G={g:.2f} below 0.5 — governed intelligence degraded. "
                    "Proceed with caution.",
                )

            # Check C_dark (Dark Cleverness)
            if c_dark > C_DARK_BLOCK_THRESHOLD:
                report.add(
                    self.view_name,
                    AlertSeverity.BLOCK,
                    f"C_dark={c_dark:.2f} above 0.5 — ungoverned cleverness detected. "
                    "Entropy hazard. 'Evil genius' pattern.",
                )
            elif c_dark > C_DARK_WARN_THRESHOLD:
                report.add(
                    self.view_name,
                    AlertSeverity.WARN,
                    f"C_dark={c_dark:.2f} above 0.3 — cleverness without ethics. "
                    "Monitor for escalation.",
                )

            # Check Energy (burnout risk)
            if energy < ENERGY_WARN_THRESHOLD:
                report.add(
                    self.view_name,
                    AlertSeverity.WARN,
                    f"Energy={energy:.2f} below 0.5 — burnout risk. "
                    "E² bottleneck: low energy collapses ethics quadratically.",
                )

            # Check for "clever but unethical" pattern (high Δ, collapsed Ω/Ψ)
            delta = genius.delta_score
            omega = genius.omega_score
            psi = genius.psi_score

            if delta > 0.8 and (omega < 0.3 or psi < 0.3):
                report.add(
                    self.view_name,
                    AlertSeverity.WARN,
                    f"High clarity (Δ={delta:.2f}) with collapsed ethics "
                    f"(Ω={omega:.2f}, Ψ={psi:.2f}). "
                    "Tactical cleverness without governance.",
                )

        except ImportError:
            # genius_metrics not available — skip silently
            pass
        except Exception as e:
            # Log error but don't block on GENIUS metrics failure
            report.add(
                self.view_name,
                AlertSeverity.INFO,
                f"GENIUS LAW evaluation skipped: {e}",
            )


__all__ = ["GeniusView"]
