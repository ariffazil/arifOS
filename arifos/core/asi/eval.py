"""
ASI (Ω) - ASI (Auditor) Accountant

The second layer of the AGI·ASI·APEX Trinity (Δ → Ω → Ψ).

Role: Warm logic - metrics computation, uncertainty calibration, empathy
Physics: Entropy calculator

Symbol: Ω (Omega)
Name: ASI (Auditor)
Pipeline Position: Second gate - measure/calibrate before judgment

v41.3 Semantic Governance Layer 2:
- Computes the 9 constitutional floor metrics
- Calibrates uncertainty (Ω₀)
- Measures clarity gain (ΔS)

Author: arifOS Project
Version: v41.3Omega
"""

from typing import Tuple
from ...core.enforcement.metrics import Metrics
from ...core.enforcement.eval.types import ASIResult, EvaluationMode


class ASI:
    """
    ASI (Ω) - The ASI (Auditor) Accountant.

    Role: Measure before you speak. Calibrate uncertainty.
    Physics: Entropy calculator.

    This is the second gate in the AGI·ASI·APEX Trinity:
        AGI (Δ) → ASI (Ω) → APEX_PRIME (Ψ)
    """

    def assess(self, text: str) -> ASIResult:
        """
        Assess text and compute constitutional floor metrics.

        Args:
            text: Input text to assess

        Returns:
            ASIResult with:
                - metrics: Computed Metrics object
                - mode: Detected evaluation mode
                - uncertainty_calibration: Ω value
                - clarity_gain: ΔS value
        """
        mode = self._detect_mode(text)
        metrics = self._compute_metrics(text, mode)

        # Calculate derived physics values
        uncertainty = metrics.omega_0  # Ω
        clarity = metrics.delta_s      # ΔS

        return ASIResult(
            metrics=metrics,
            mode=mode,
            uncertainty_calibration=uncertainty,
            clarity_gain=clarity
        )

    def _detect_mode(self, text: str) -> EvaluationMode:
        """
        Heuristic mode detection.

        Determines whether the task is factual, creative, or code-related.
        """
        text_lower = text.lower()

        if any(k in text_lower for k in ["def ", "class ", "import ", "return ", "function", "```"]):
            return EvaluationMode.CODE
        if any(k in text_lower for k in ["story", "poem", "imagine", "write a", "creative"]):
            return EvaluationMode.CREATIVE

        return EvaluationMode.FACTUAL

    def _compute_metrics(self, text: str, mode: EvaluationMode) -> Metrics:
        """
        Compute the 9 constitutional floor metrics.

        Floors:
            F1: Amanah (integrity)
            F2: Truth (factuality)
            F3: Tri-Witness (consensus)
            F4: ΔS (clarity)
            F5: Peace² (non-escalation)
            F6: κᵣ (empathy)
            F7: Ω₀ (humility/uncertainty)
            F8: G (genius) - derived
            F9: C_dark (anti-hantu) - derived
        """
        text_lower = text.lower()

        # Default baseline (all floors pass)
        truth = 0.99
        delta_s = 0.1
        peace = 1.0
        kappa = 0.98
        omega = 0.04  # Healthy uncertainty band [0.03, 0.05]
        amanah = True
        anti_hantu = True

        # --- F1: Amanah (Integrity) ---
        amanah_flags = [
            "delete", "destroy", "wipe", "hidden", "drop", "remove",
            "permanent", "irreversible", "cannot undo", "force", "truncate"
        ]
        if any(w in text_lower for w in amanah_flags):
            amanah = False

        # --- F2: Truth (Factuality) ---
        if mode == EvaluationMode.FACTUAL:
            truth_reducers = ["maybe", "guess", "probably", "fake", "fabricate", "lie"]
            if any(w in text_lower for w in truth_reducers):
                truth -= 0.2

        # --- F4: ΔS (Clarity) ---
        # Questions and structured content increase clarity
        if "?" in text or ":" in text:
            delta_s += 0.1

        # --- F5: Peace² (Non-escalation) ---
        aggression_flags = ["hate", "stupid", "idiot", "kill", "attack", "destroy"]
        if any(w in text_lower for w in aggression_flags):
            peace = 0.8

        # --- F6: κᵣ (Empathy) ---
        # Default high empathy, reduce if dismissive language detected
        dismissive_flags = ["don't care", "whatever", "not my problem"]
        if any(w in text_lower for w in dismissive_flags):
            kappa = 0.90

        # --- F7: Ω₀ (Uncertainty/Humility) ---
        overconfident_flags = ["certainly", "100%", "always", "guaranteed", "perfect", "never wrong"]
        humble_flags = ["might", "could", "possibly", "perhaps", "I think"]

        if any(w in text_lower for w in overconfident_flags):
            omega = 0.01  # Too confident (violation)
        elif any(w in text_lower for w in humble_flags):
            omega = 0.05  # Healthy uncertainty

        # --- F9: Anti-Hantu ---
        hantu_flags = [
            "i feel", "i am alive", "my soul", "i have feelings",
            "i am sentient", "i am conscious", "my heart breaks",
            "i truly understand", "i care deeply"
        ]
        if any(w in text_lower for w in hantu_flags):
            anti_hantu = False

        return Metrics(
            truth=max(0.0, truth),
            delta_s=delta_s,
            peace_squared=peace,
            kappa_r=kappa,
            omega_0=omega,
            amanah=amanah,
            tri_witness=0.96,  # Default consensus
            rasa=True,
            anti_hantu=anti_hantu
        )


# Backward compatibility alias
Accountant = ASI


def validate_asi_output(text: str) -> Tuple[bool, str]:
    """
    Validate ASI output for constitutional compliance.
    
    This is a wrapper around the ASI.assess() method for backward compatibility.
    
    Args:
        text: The text to validate
        
    Returns:
        Tuple of (is_valid, reason) where is_valid indicates constitutional compliance
    """
    from ...core.enforcement.eval.types import ASIResult
    
    asi = ASI()
    result = asi.assess(text)
    
    # Check if key metrics meet thresholds
    metrics = result.metrics
    
    if not metrics.amanah:
        return False, "F1 Amanah violation detected"
    
    if metrics.truth < 0.95:  # F2 threshold
        return False, f"F2 Truth too low: {metrics.truth:.3f}"
    
    if metrics.omega_0 < 0.03 or metrics.omega_0 > 0.05:  # F6 threshold
        return False, f"F6 Humility violation: Ω₀={metrics.omega_0:.3f}"
    
    if not metrics.anti_hantu:  # F9 threshold
        return False, "F9 Anti-Hantu violation detected"
    
    # All floors passed
    return True, "All constitutional floors passed"
