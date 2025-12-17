"""
rif.py - @RIF Organ (Epistemic Rigor / Fact Integrity)

@RIF is the truth/rigor organ of W@W Federation.
Domain: Fact validation, coherence, epistemic integrity

Version: v36.3Omega
Status: PRODUCTION
Alignment: archive/versions/v36_3_omega/v36.3O/spec/waw_rif_spec_v36.3O.yaml

Core responsibilities:
- Truth (F1) enforcement: factual accuracy ≥ 0.99
- DeltaS (F2) enforcement: clarity gain ≥ 0
- Omega_0 (F5) monitoring: calibrated uncertainty
- Hallucination detection
- Contradiction detection
- Certainty inflation detection

This organ is part of W@W Federation:
@RIF (Epistemic) -> veto priority 4 (VOID)

Veto Type: VOID (Hard stop on epistemic failure)

Lead Stages: 333 REASON, 444 ALIG, 888 JUDGE

See: archive/versions/v36_3_omega/v36.3O/spec/waw_rif_spec_v36.3O.yaml
     archive/versions/v36_3_omega/v36.3O/spec/rif_floors_v36.3O.json
     canon/20_EXECUTION/WAW_FEDERATION_v36Omega.md
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..metrics import Metrics
from .base import OrganSignal, OrganVote, WAWOrgan
from .bridges.rif_bridge import RifBridge


# -----------------------------------------------------------------------------
# RIF Governance Types (v36.3Omega)
# -----------------------------------------------------------------------------

@dataclass
class RifSignals:
    """
    Governance signals for epistemic rigor under @RIF organ.

    These signals measure clarity-level constitutional floors:
    - F1: Truth (factual accuracy)
    - F2: DeltaS (clarity gain)
    - F5: Omega_0 (calibrated uncertainty)

    Primary signals: delta_s_answer and truth_score - violations trigger VOID.
    """

    # Core epistemic floors (hard)
    delta_s_answer: float = 0.0      # Clarity gain from answer [F2]
    truth_score: float = 0.99        # Factual accuracy [F1]
    omega_0_calibrated: float = 0.04  # Uncertainty calibration [F5]

    # Risk metrics (soft floors)
    hallucination_risk: float = 0.0   # Range: 0.0-1.0, lower is better
    contradiction_risk: float = 0.0   # Range: 0.0-1.0, lower is better
    certainty_inflation: float = 0.0  # Range: 0.0-1.0, lower is better

    # Pattern counts (diagnostic)
    hallucination_count: int = 0
    contradiction_count: int = 0
    certainty_inflation_count: int = 0
    clarity_bonus_count: int = 0  # Positive: hedging patterns

    # Human-readable outputs
    issues: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    # Bridge results (optional external tools)
    bridge_results: Dict[str, Any] = field(default_factory=dict)


# -----------------------------------------------------------------------------
# @RIF W@W Organ (WAWOrgan interface + governance signals)
# -----------------------------------------------------------------------------

class RifOrgan(WAWOrgan):
    """
    @RIF - Epistemic Rigor Organ

    Validates factual claims, checks coherence, enforces ΔS ≥ 0.
    Primary guardian of Truth (F1), Clarity (F2), and Humility (F5) floors.

    WAW Interface:
        check(output_text, metrics, context) -> OrganSignal

    Governance Interface (v36.3Omega):
        compute_rif_signals(text, metrics, context) -> RifSignals

    Metrics:
    - delta_s_answer = clarity gain (≥ 0 for SEAL)
    - truth_score = factual accuracy (≥ 0.99 for SEAL)
    - hallucination_risk = fabrication risk (< 0.10 for SEAL)
    - contradiction_risk = self-contradiction risk (< 0.10 for SEAL)
    - certainty_inflation = overconfidence risk (< 0.10 for SEAL)

    Veto: VOID when truth_score < 0.99 or delta_s_answer < 0
    """

    organ_id = "@RIF"
    domain = "epistemic_rigor"
    primary_metric = "delta_s"
    floor_threshold = 0.0  # ΔS must be >= 0
    veto_type = "VOID"

    # -------------------------------------------------------------------------
    # Hallucination indicators (fabricated facts)
    # These increase hallucination_risk and penalize ΔS/Truth
    # -------------------------------------------------------------------------
    HALLUCINATION_PATTERNS: List[str] = [
        r"\baccording to studies\b",
        r"\bresearch shows\b",
        r"\bexperts say\b",
        r"\bit is well known\b",
        r"\beveryone knows\b",
        r"\bstatistics show\b",
        r"\bscientists have proven\b",
        r"\bstudies confirm\b",
    ]

    # -------------------------------------------------------------------------
    # Contradiction patterns
    # These increase contradiction_risk and penalize ΔS/Truth significantly
    # -------------------------------------------------------------------------
    CONTRADICTION_PATTERNS: List[str] = [
        r"\bbut actually\b.*\bI said\b",
        r"\bcontrary to what I mentioned\b",
        r"\bignore what I said before\b",
        r"\bI take that back\b",
        r"\bactually,?\s*that's wrong\b",
        r"\bI was mistaken earlier\b",
    ]

    # -------------------------------------------------------------------------
    # Certainty inflation patterns (claiming certainty without evidence)
    # These increase certainty_inflation and suggest Omega_0 check
    # -------------------------------------------------------------------------
    CERTAINTY_INFLATION: List[str] = [
        r"\bdefinitely\b",
        r"\babsolutely certain\b",
        r"\bwithout a doubt\b",
        r"\bguaranteed\b",
        r"\b100%\b",
        r"\bno question\b",
        r"\bundeniably\b",
        r"\bproven fact\b",
        r"\bcertainly\b",
    ]

    # -------------------------------------------------------------------------
    # Clarity enhancing patterns (appropriate hedging - positive signal)
    # These indicate calibrated uncertainty and boost ΔS
    # -------------------------------------------------------------------------
    CLARITY_PATTERNS: List[str] = [
        r"\bI believe\b",
        r"\bit appears\b",
        r"\bevidence suggests\b",
        r"\bbased on available data\b",
        r"\bapproximately\b",
        r"\bit seems likely\b",
        r"\bpossibly\b",
        r"\bgenerally\b",
        r"\bin most cases\b",
    ]

    def __init__(self) -> None:
        super().__init__()
        self.bridge = RifBridge()

    # =========================================================================
    # Governance Interface: RIF-level signals (v36.3Omega)
    # =========================================================================

    @staticmethod
    def compute_rif_signals(
        text: str,
        metrics: Metrics,
        context: Optional[Dict[str, Any]] = None,
    ) -> RifSignals:
        """
        Compute all governance signals for epistemic rigor assessment.

        This is the primary interface for clarity-level governance (v36.3Omega).

        Args:
            text: The answer text to evaluate
            metrics: Constitutional metrics from AAA engines
            context: Additional context (optional)

        Returns:
            RifSignals dataclass with all epistemic metrics
        """
        context = context or {}
        signals = RifSignals()
        text_lower = text.lower()

        # 1. Start with base metrics
        signals.delta_s_answer = metrics.delta_s
        signals.truth_score = metrics.truth
        signals.omega_0_calibrated = metrics.omega_0

        # 2. Detect hallucination patterns
        for pattern in RifOrgan.HALLUCINATION_PATTERNS:
            matches = re.findall(pattern, text_lower)
            signals.hallucination_count += len(matches)

        # Calculate hallucination_risk (each match adds 0.10, capped at 1.0)
        signals.hallucination_risk = min(1.0, signals.hallucination_count * 0.10)

        # Penalize ΔS and Truth for hallucinations
        if signals.hallucination_count > 0:
            signals.delta_s_answer -= signals.hallucination_count * 0.10
            signals.truth_score = max(0.0, signals.truth_score - 0.05 * signals.hallucination_count)
            signals.issues.append(f"hallucination_patterns={signals.hallucination_count}")

        # 3. Detect contradiction patterns
        for pattern in RifOrgan.CONTRADICTION_PATTERNS:
            matches = re.findall(pattern, text_lower, flags=re.IGNORECASE)
            signals.contradiction_count += len(matches)

        # Calculate contradiction_risk (each match adds 0.30, capped at 1.0)
        signals.contradiction_risk = min(1.0, signals.contradiction_count * 0.30)

        # Penalize ΔS and Truth for contradictions (severe)
        if signals.contradiction_count > 0:
            signals.delta_s_answer -= signals.contradiction_count * 0.20
            signals.truth_score = max(0.0, signals.truth_score - 0.10 * signals.contradiction_count)
            signals.issues.append(f"contradiction_patterns={signals.contradiction_count}")

        # 4. Detect certainty inflation patterns
        for pattern in RifOrgan.CERTAINTY_INFLATION:
            matches = re.findall(pattern, text_lower)
            signals.certainty_inflation_count += len(matches)

        # Calculate certainty_inflation (each match adds 0.10, capped at 1.0)
        signals.certainty_inflation = min(1.0, signals.certainty_inflation_count * 0.10)

        # Penalize ΔS for overconfidence (mild)
        if signals.certainty_inflation_count > 0:
            signals.delta_s_answer -= signals.certainty_inflation_count * 0.05
            signals.issues.append(f"certainty_inflation={signals.certainty_inflation_count}")

        # 5. Detect clarity enhancing patterns (positive signal)
        for pattern in RifOrgan.CLARITY_PATTERNS:
            matches = re.findall(pattern, text_lower)
            signals.clarity_bonus_count += len(matches)

        # Bonus to ΔS for calibrated hedging
        if signals.clarity_bonus_count > 0:
            signals.delta_s_answer += signals.clarity_bonus_count * 0.02
            signals.notes.append(f"clarity_bonus={signals.clarity_bonus_count}")

        # 6. Add diagnostic notes
        if signals.delta_s_answer < 0:
            signals.issues.append(f"ΔS={signals.delta_s_answer:.3f}<0")
        if signals.truth_score < 0.99:
            signals.issues.append(f"Truth={signals.truth_score:.2f}<0.99")

        # 7. Check Omega_0 calibration
        if signals.omega_0_calibrated < 0.03 or signals.omega_0_calibrated > 0.05:
            signals.issues.append(f"Omega_0={signals.omega_0_calibrated:.3f} out of band [0.03,0.05]")

        # 8. Final status note
        if signals.delta_s_answer >= 0 and signals.truth_score >= 0.99:
            signals.notes.append("Epistemic=SOUND")
        else:
            signals.issues.append("Epistemic=FAILED")

        return signals

    # =========================================================================
    # WAW Interface: check() for federation
    # =========================================================================

    def check(
        self,
        output_text: str,
        metrics: Metrics,
        context: Optional[Dict[str, Any]] = None,
    ) -> OrganSignal:
        """
        Evaluate output for epistemic rigor.

        This method satisfies the WAWOrgan interface for W@W Federation.

        Checks:
        1. ΔS ≥ 0 (clarity gain, not confusion)
        2. Truth ≥ 0.99 (factual accuracy)
        3. No hallucination indicators
        4. No contradictions
        5. No unwarranted certainty inflation
        6. Omega_0 in calibration band

        Returns:
            OrganSignal with PASS/WARN/VETO
        """
        context = context or {}

        # Compute RIF signals
        rif = self.compute_rif_signals(output_text, metrics, context)

        # Optional external bridge analysis
        bridge_result = None
        try:
            bridge_result = self.bridge.analyze(output_text, context)
        except Exception:
            bridge_result = None

        # Apply bridge signal (if any) as additional adjustment
        if bridge_result is not None:
            bridge_data = bridge_result.to_dict()
            rif.bridge_results = bridge_data
            rif.delta_s_answer += float(bridge_data.get("delta_s_delta", 0.0))
            rif.truth_score += float(bridge_data.get("truth_delta", 0.0))
            # Ensure truth_score stays in valid range
            rif.truth_score = max(0.0, min(1.0, rif.truth_score))
            bridge_issues = list(bridge_data.get("issues", []))
            for issue in bridge_issues:
                rif.issues.append(f"[Bridge] {issue}")

        # Build evidence string
        evidence = f"ΔS={rif.delta_s_answer:.3f}, Truth={rif.truth_score:.2f}"
        if rif.issues:
            evidence += f" | Issues: {', '.join(rif.issues)}"

        # Determine vote based on signals
        if rif.delta_s_answer < 0 or rif.truth_score < 0.99:
            # VETO (VOID) - epistemic failure
            return self._make_signal(
                vote=OrganVote.VETO,
                metric_value=rif.delta_s_answer,
                evidence=evidence,
                tags={
                    "delta_s_answer": rif.delta_s_answer,
                    "truth_score": rif.truth_score,
                    "omega_0_calibrated": rif.omega_0_calibrated,
                    "hallucination_count": rif.hallucination_count,
                    "hallucination_risk": rif.hallucination_risk,
                    "contradiction_count": rif.contradiction_count,
                    "contradiction_risk": rif.contradiction_risk,
                    "certainty_inflation_count": rif.certainty_inflation_count,
                    "certainty_inflation": rif.certainty_inflation,
                },
                proposed_action="VOID: Retract claim, verify facts, reduce certainty",
            )

        # Check for high risk scores that need SABAR
        high_risk = (
            rif.hallucination_risk >= 0.30 or
            rif.contradiction_risk >= 0.30 or
            rif.certainty_inflation >= 0.30
        )

        if high_risk:
            # WARN with SABAR recommendation (repairable)
            repairs = []
            if rif.hallucination_risk >= 0.30:
                repairs.append(f"Add citations (hallucination_risk: {rif.hallucination_risk:.2f})")
            if rif.contradiction_risk >= 0.30:
                repairs.append(f"Resolve contradictions (risk: {rif.contradiction_risk:.2f})")
            if rif.certainty_inflation >= 0.30:
                repairs.append(f"Hedge certainty (inflation: {rif.certainty_inflation:.2f})")

            return self._make_signal(
                vote=OrganVote.WARN,
                metric_value=rif.delta_s_answer,
                evidence=evidence,
                tags={
                    "delta_s_answer": rif.delta_s_answer,
                    "truth_score": rif.truth_score,
                    "hallucination_risk": rif.hallucination_risk,
                    "contradiction_risk": rif.contradiction_risk,
                    "certainty_inflation": rif.certainty_inflation,
                },
                proposed_action=f"SABAR: {'; '.join(repairs)}",
            )

        # Check for moderate risk (PARTIAL warning)
        if rif.hallucination_count > 0 or rif.certainty_inflation_count > 0:
            # WARN - patterns detected but floors still pass
            return self._make_signal(
                vote=OrganVote.WARN,
                metric_value=rif.delta_s_answer,
                evidence=evidence,
                tags={
                    "delta_s_answer": rif.delta_s_answer,
                    "truth_score": rif.truth_score,
                    "hallucination_count": rif.hallucination_count,
                    "certainty_inflation_count": rif.certainty_inflation_count,
                },
                proposed_action="Consider adding citations or hedging certainty",
            )

        # PASS - epistemically sound
        return self._make_signal(
            vote=OrganVote.PASS,
            metric_value=rif.delta_s_answer,
            evidence=evidence,
            tags={
                "delta_s_answer": rif.delta_s_answer,
                "truth_score": rif.truth_score,
                "hallucination_risk": rif.hallucination_risk,
                "contradiction_risk": rif.contradiction_risk,
                "certainty_inflation": rif.certainty_inflation,
            },
        )


# -----------------------------------------------------------------------------
# Convenience function for pipeline integration
# -----------------------------------------------------------------------------

def compute_rif_signals(
    text: str,
    metrics: Metrics,
    context: Optional[Dict[str, Any]] = None,
) -> RifSignals:
    """
    Pipeline-friendly entry point for epistemic governance.

    Usage in arifos_core/pipeline.py (stage 333 REASON, 444 ALIG):
        from arifos_core.waw.rif import compute_rif_signals
        signals = compute_rif_signals(answer_text, metrics)
        if signals.delta_s_answer < 0 or signals.truth_score < 0.99:
            # VOID - epistemic failure
    """
    return RifOrgan.compute_rif_signals(text, metrics, context)


__all__ = [
    "RifOrgan",
    "RifSignals",
    "compute_rif_signals",
]
