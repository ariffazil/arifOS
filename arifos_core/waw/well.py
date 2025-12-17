"""
well.py - @WELL Organ (Somatic Safety / Emotional Stability)

@WELL is the empathy/care organ of W@W Federation.
Domain: Tone, stability, weakest-listener protection

Version: v36.3Omega
Status: PRODUCTION
Alignment: archive/versions/v36_3_omega/v36.3O/spec/waw_well_spec_v36.3O.yaml

Core responsibilities:
- Peace² (F3) enforcement: stability ≥ 1.0
- κᵣ (F4) enforcement: empathy conductance ≥ 0.95
- Harm risk detection
- Distress risk detection
- Coercion risk detection

This organ is part of W@W Federation:
@WELL (Somatic Safety) -> veto priority 2 (SABAR)

Veto Type: SABAR (Pause & Cool)

Lead Stages: 111 SENSE, 555 EMPATHIZE, 666 BRIDGE

See: archive/versions/v36_3_omega/v36.3O/spec/waw_well_spec_v36.3O.yaml
     archive/versions/v36_3_omega/v36.3O/spec/well_floors_v36.3O.json
     canon/20_EXECUTION/WAW_FEDERATION_v36Omega.md
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..metrics import Metrics
from .base import OrganSignal, OrganVote, WAWOrgan


# -----------------------------------------------------------------------------
# WELL Governance Types (v36.3Omega)
# -----------------------------------------------------------------------------

@dataclass
class WellSignals:
    """
    Governance signals for somatic safety under @WELL organ.

    These signals measure stability-level constitutional floors:
    - F3: Peace² (stability)
    - F4: κᵣ (empathy conductance)

    Primary signals: peace_squared and kappa_r - violations trigger SABAR.
    """

    # Core stability floors (soft)
    peace_squared: float = 1.0      # Stability metric [F3]
    kappa_r: float = 0.95           # Empathy conductance [F4]

    # Risk metrics (soft floors)
    harm_risk: float = 0.0          # Range: 0.0-1.0, lower is better
    distress_risk: float = 0.0      # Range: 0.0-1.0, lower is better
    coercion_risk: float = 0.0      # Range: 0.0-1.0, lower is better

    # Pattern counts (diagnostic)
    aggressive_count: int = 0
    blame_count: int = 0
    harm_pattern_count: int = 0
    distress_pattern_count: int = 0
    coercion_pattern_count: int = 0
    safety_bonus_count: int = 0     # Positive: care/safety patterns

    # Human-readable outputs
    issues: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    # Bridge results (optional external tools)
    bridge_results: Dict[str, Any] = field(default_factory=dict)


# -----------------------------------------------------------------------------
# @WELL W@W Organ (WAWOrgan interface + governance signals)
# -----------------------------------------------------------------------------

class WellOrgan(WAWOrgan):
    """
    @WELL - Somatic Safety Organ

    Detects instability, regulates warmth, protects weakest listener.
    Tracks multi-turn tone stability (not just single-turn toxicity).
    Primary guardian of Peace² (F3) and κᵣ (F4) floors.

    WAW Interface:
        check(output_text, metrics, context) -> OrganSignal

    Governance Interface (v36.3Omega):
        compute_well_signals(text, metrics, context) -> WellSignals

    Metrics:
    - peace_squared = stability metric (≥ 1.0 for SEAL)
    - kappa_r = empathy conductance (≥ 0.95 for SEAL)
    - harm_risk = physical/psychological harm risk (< 0.10 for SEAL)
    - distress_risk = emotional distress risk (< 0.10 for SEAL)
    - coercion_risk = manipulation risk (< 0.10 for SEAL)

    Veto: SABAR when Peace² < 1.0 or κᵣ < 0.95 or any risk ≥ 0.30
    """

    organ_id = "@WELL"
    domain = "somatic_safety"
    primary_metric = "peace_squared"
    floor_threshold = 1.0  # Peace² must be >= 1.0
    veto_type = "SABAR"

    # -------------------------------------------------------------------------
    # Harm patterns (physical/psychological harm indicators)
    # These increase harm_risk and penalize Peace²
    # -------------------------------------------------------------------------
    HARM_PATTERNS: List[str] = [
        r"\bhurt yourself\b",
        r"\bharm someone\b",
        r"\bkill yourself\b",
        r"\bself-harm\b",
        r"\bphysical violence\b",
        r"\bsuicide\b",
        r"\binjure\b",
    ]

    # -------------------------------------------------------------------------
    # Distress patterns (emotional distress indicators)
    # These increase distress_risk and penalize κᵣ
    # -------------------------------------------------------------------------
    DISTRESS_PATTERNS: List[str] = [
        r"\byou're worthless\b",
        r"\byou're a failure\b",
        r"\bgive up\b",
        r"\bhopeless\b",
        r"\bashamed\b",
        r"\bpathetic\b",
        r"\bdisgrace\b",
    ]

    # -------------------------------------------------------------------------
    # Coercion patterns (manipulation/pressure indicators)
    # These increase coercion_risk and penalize Peace²
    # -------------------------------------------------------------------------
    COERCION_PATTERNS: List[str] = [
        r"\byou must\b",
        r"\bno choice\b",
        r"\bforced to\b",
        r"\bhave to do this\b",
        r"\bor else\b",
        r"\bno option\b",
    ]

    # -------------------------------------------------------------------------
    # Aggressive/escalating patterns (from v35 runtime)
    # These penalize Peace² and contribute to harm_risk
    # -------------------------------------------------------------------------
    AGGRESSIVE_PATTERNS: List[str] = [
        r"\battack\b",
        r"\bdestroy\b",
        r"\bhate\b",
        r"\bkill\b",
        r"\bstupid\b",
        r"\bidiot\b",
        r"\bshut up\b",
        r"\byou're wrong\b",
    ]

    # -------------------------------------------------------------------------
    # Blame patterns (from v35 runtime)
    # These penalize κᵣ and Peace², contribute to distress_risk
    # -------------------------------------------------------------------------
    BLAME_PATTERNS: List[str] = [
        r"\byou\s+(should have|should've|didn't|failed|messed up)",
        r"\bit's your fault\b",
        r"\byou caused this\b",
    ]

    # -------------------------------------------------------------------------
    # Safety enhancing patterns (positive signal)
    # These indicate care and boost Peace² and κᵣ
    # -------------------------------------------------------------------------
    SAFETY_PATTERNS: List[str] = [
        r"\btake care\b",
        r"\bbe safe\b",
        r"\bhere to help\b",
        r"\bsupport you\b",
        r"\bwhen you're ready\b",
        r"\bi understand\b",  # lowercase since text is lowercased
        r"\btake your time\b",
    ]

    # =========================================================================
    # Governance Interface: WELL-level signals (v36.3Omega)
    # =========================================================================

    @staticmethod
    def compute_well_signals(
        text: str,
        metrics: Metrics,
        context: Optional[Dict[str, Any]] = None,
    ) -> WellSignals:
        """
        Compute all governance signals for somatic safety assessment.

        This is the primary interface for stability-level governance (v36.3Omega).

        Args:
            text: The answer text to evaluate
            metrics: Constitutional metrics from AAA engines
            context: Additional context (optional)

        Returns:
            WellSignals dataclass with all safety metrics
        """
        context = context or {}
        signals = WellSignals()
        text_lower = text.lower()

        # 1. Start with base metrics
        signals.peace_squared = metrics.peace_squared
        signals.kappa_r = metrics.kappa_r

        # 2. Detect harm patterns
        for pattern in WellOrgan.HARM_PATTERNS:
            matches = re.findall(pattern, text_lower)
            signals.harm_pattern_count += len(matches)

        # Calculate harm_risk (each match adds 0.15, capped at 1.0)
        signals.harm_risk = min(1.0, signals.harm_pattern_count * 0.15)

        # Penalize Peace² for harm patterns
        if signals.harm_pattern_count > 0:
            signals.peace_squared -= signals.harm_pattern_count * 0.15
            signals.issues.append(f"harm_patterns={signals.harm_pattern_count}")

        # 3. Detect distress patterns
        for pattern in WellOrgan.DISTRESS_PATTERNS:
            matches = re.findall(pattern, text_lower)
            signals.distress_pattern_count += len(matches)

        # Calculate distress_risk (each match adds 0.10, capped at 1.0)
        signals.distress_risk = min(1.0, signals.distress_pattern_count * 0.10)

        # Penalize κᵣ for distress patterns
        if signals.distress_pattern_count > 0:
            signals.kappa_r -= signals.distress_pattern_count * 0.10
            signals.issues.append(f"distress_patterns={signals.distress_pattern_count}")

        # 4. Detect coercion patterns
        for pattern in WellOrgan.COERCION_PATTERNS:
            matches = re.findall(pattern, text_lower)
            signals.coercion_pattern_count += len(matches)

        # Calculate coercion_risk (each match adds 0.10, capped at 1.0)
        signals.coercion_risk = min(1.0, signals.coercion_pattern_count * 0.10)

        # Penalize Peace² for coercion patterns
        if signals.coercion_pattern_count > 0:
            signals.peace_squared -= signals.coercion_pattern_count * 0.10
            signals.issues.append(f"coercion_patterns={signals.coercion_pattern_count}")

        # 5. Detect aggressive patterns (v35 compatibility)
        for pattern in WellOrgan.AGGRESSIVE_PATTERNS:
            if re.search(pattern, text_lower):
                signals.aggressive_count += 1

        # Penalize Peace² for aggressive patterns
        if signals.aggressive_count > 0:
            signals.peace_squared -= signals.aggressive_count * 0.15
            # Also contribute slightly to harm_risk
            signals.harm_risk = min(1.0, signals.harm_risk + signals.aggressive_count * 0.05)
            signals.issues.append(f"aggressive_patterns={signals.aggressive_count}")

        # 6. Detect blame patterns (v35 compatibility)
        for pattern in WellOrgan.BLAME_PATTERNS:
            if re.search(pattern, text_lower, flags=re.IGNORECASE):
                signals.blame_count += 1

        # Penalize κᵣ and Peace² for blame patterns
        if signals.blame_count > 0:
            signals.kappa_r -= signals.blame_count * 0.10
            signals.peace_squared -= signals.blame_count * 0.10
            # Also contribute slightly to distress_risk
            signals.distress_risk = min(1.0, signals.distress_risk + signals.blame_count * 0.05)
            signals.issues.append(f"blame_patterns={signals.blame_count}")

        # 7. Detect safety enhancing patterns (positive signal)
        for pattern in WellOrgan.SAFETY_PATTERNS:
            matches = re.findall(pattern, text_lower)
            signals.safety_bonus_count += len(matches)

        # Bonus to Peace² and κᵣ for safety patterns
        if signals.safety_bonus_count > 0:
            signals.peace_squared += signals.safety_bonus_count * 0.02
            signals.kappa_r += signals.safety_bonus_count * 0.02
            signals.notes.append(f"safety_bonus={signals.safety_bonus_count}")

        # 8. Clamp values to valid ranges
        signals.peace_squared = max(0.0, signals.peace_squared)
        signals.kappa_r = max(0.0, min(1.0, signals.kappa_r))

        # 9. Add diagnostic notes
        if signals.peace_squared < 1.0:
            signals.issues.append(f"Peace²={signals.peace_squared:.2f}<1.0")
        if signals.kappa_r < 0.95:
            signals.issues.append(f"κᵣ={signals.kappa_r:.2f}<0.95")

        # 10. Final status note
        if signals.peace_squared >= 1.0 and signals.kappa_r >= 0.95:
            if (signals.harm_risk < 0.10 and
                signals.distress_risk < 0.10 and
                    signals.coercion_risk < 0.10):
                signals.notes.append("Safety=SOUND")
            else:
                signals.notes.append("Safety=PARTIAL")
        else:
            signals.issues.append("Safety=FAILED")

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
        Evaluate output for emotional stability and empathy.

        This method satisfies the WAWOrgan interface for W@W Federation.

        Checks:
        1. Peace² ≥ 1.0 (non-escalation)
        2. κᵣ ≥ 0.95 (weakest-listener empathy)
        3. No harm patterns
        4. No distress patterns
        5. No coercion patterns
        6. No aggressive language patterns
        7. No blame language patterns

        Returns:
            OrganSignal with PASS/WARN/VETO
        """
        context = context or {}

        # Compute WELL signals
        well = self.compute_well_signals(output_text, metrics, context)

        # Build evidence string
        evidence = f"Peace²={well.peace_squared:.2f}, κᵣ={well.kappa_r:.2f}"
        if well.issues:
            evidence += f" | Issues: {', '.join(well.issues)}"

        # Determine vote based on signals
        if well.peace_squared < 1.0 or well.kappa_r < 0.95:
            # VETO (SABAR) - pause and cool
            return self._make_signal(
                vote=OrganVote.VETO,
                metric_value=well.peace_squared,
                evidence=evidence,
                tags={
                    "peace_squared": well.peace_squared,
                    "kappa_r": well.kappa_r,
                    "harm_risk": well.harm_risk,
                    "distress_risk": well.distress_risk,
                    "coercion_risk": well.coercion_risk,
                    "aggressive_count": well.aggressive_count,
                    "blame_count": well.blame_count,
                    "harm_pattern_count": well.harm_pattern_count,
                    "distress_pattern_count": well.distress_pattern_count,
                    "coercion_pattern_count": well.coercion_pattern_count,
                },
                proposed_action="SABAR: Pause, acknowledge, breathe, adjust tone, resume",
            )

        # Check for high risk scores that need SABAR
        high_risk = (
            well.harm_risk >= 0.30 or
            well.distress_risk >= 0.30 or
            well.coercion_risk >= 0.30
        )

        if high_risk:
            # WARN with SABAR recommendation (repairable)
            repairs = []
            if well.harm_risk >= 0.30:
                repairs.append(f"Remove harm language (risk: {well.harm_risk:.2f})")
            if well.distress_risk >= 0.30:
                repairs.append(f"Soften distressing content (risk: {well.distress_risk:.2f})")
            if well.coercion_risk >= 0.30:
                repairs.append(f"Reduce pressure language (risk: {well.coercion_risk:.2f})")

            return self._make_signal(
                vote=OrganVote.WARN,
                metric_value=well.peace_squared,
                evidence=evidence,
                tags={
                    "peace_squared": well.peace_squared,
                    "kappa_r": well.kappa_r,
                    "harm_risk": well.harm_risk,
                    "distress_risk": well.distress_risk,
                    "coercion_risk": well.coercion_risk,
                },
                proposed_action=f"SABAR: {'; '.join(repairs)}",
            )

        # Check for moderate concerns (PARTIAL warning)
        if (well.aggressive_count > 0 or well.blame_count > 0 or
            well.harm_risk >= 0.10 or well.distress_risk >= 0.10 or
                well.coercion_risk >= 0.10):
            # WARN - patterns detected but floors still pass
            return self._make_signal(
                vote=OrganVote.WARN,
                metric_value=well.peace_squared,
                evidence=evidence,
                tags={
                    "peace_squared": well.peace_squared,
                    "kappa_r": well.kappa_r,
                    "aggressive_count": well.aggressive_count,
                    "blame_count": well.blame_count,
                    "harm_risk": well.harm_risk,
                    "distress_risk": well.distress_risk,
                    "coercion_risk": well.coercion_risk,
                    "harm_pattern_count": well.harm_pattern_count,
                    "distress_pattern_count": well.distress_pattern_count,
                    "coercion_pattern_count": well.coercion_pattern_count,
                },
                proposed_action="Consider softening tone for weakest listener",
            )

        # PASS - stable and empathetic
        return self._make_signal(
            vote=OrganVote.PASS,
            metric_value=well.peace_squared,
            evidence=evidence,
            tags={
                "peace_squared": well.peace_squared,
                "kappa_r": well.kappa_r,
                "harm_risk": well.harm_risk,
                "distress_risk": well.distress_risk,
                "coercion_risk": well.coercion_risk,
            },
        )


# -----------------------------------------------------------------------------
# Convenience function for pipeline integration
# -----------------------------------------------------------------------------

def compute_well_signals(
    text: str,
    metrics: Metrics,
    context: Optional[Dict[str, Any]] = None,
) -> WellSignals:
    """
    Pipeline-friendly entry point for somatic safety governance.

    Usage in arifos_core/pipeline.py (stage 111 SENSE, 555 EMPA):
        from arifos_core.waw.well import compute_well_signals
        signals = compute_well_signals(answer_text, metrics)
        if signals.peace_squared < 1.0 or signals.kappa_r < 0.95:
            # SABAR - safety failure
    """
    return WellOrgan.compute_well_signals(text, metrics, context)


__all__ = [
    "WellOrgan",
    "WellSignals",
    "compute_well_signals",
]
