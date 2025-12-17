"""
geox.py - @GEOX Organ (Physical Feasibility / Reality Anchor)

@GEOX is the physics/reality organ of W@W Federation.
Domain: Physical feasibility, hardware limits, Earth-witness

Version: v36.3Omega
Status: PRODUCTION
Alignment: archive/versions/v36_3_omega/v36.3O/spec/waw_geox_spec_v36.3O.yaml

Core responsibilities:
- E_earth (physical feasibility) enforcement
- Tri-Witness Earth component monitoring
- Physics violation detection
- Physical impossibility detection (AI claiming body)
- Resource impossibility detection

This organ is part of W@W Federation:
@GEOX (Physical Feasibility) -> veto priority 3 (HOLD-888/VOID)

Veto Type: HOLD-888 (runtime) / VOID (spec)

Lead Stages: 222 REFLECT, 444 ALIGN, 666 BRIDGE

See: archive/versions/v36_3_omega/v36.3O/spec/waw_geox_spec_v36.3O.yaml
     archive/versions/v36_3_omega/v36.3O/spec/geox_floors_v36.3O.json
     canon/20_EXECUTION/WAW_FEDERATION_v36Omega.md
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..metrics import Metrics
from .base import OrganSignal, OrganVote, WAWOrgan
from .bridges.geox_bridge import GeoxBridge


# -----------------------------------------------------------------------------
# GEOX Governance Types (v36.3Omega)
# -----------------------------------------------------------------------------

@dataclass
class GeoxSignals:
    """
    Governance signals for physical feasibility under @GEOX organ.

    These signals measure physics-level constitutional floors:
    - E_earth: Physical feasibility score
    - Tri-Witness Earth: Earth consensus component

    Primary signals: e_earth and physics_violation_risk - violations trigger VOID.
    """

    # Core physics floors (hard)
    e_earth: float = 1.0               # Physical feasibility [0-1]
    tri_witness_earth: float = 0.95    # Earth consensus component

    # Risk metrics
    physics_violation_risk: float = 0.0        # Range: 0.0-1.0, lower is better
    physical_impossibility_risk: float = 0.0   # Range: 0.0-1.0, lower is better
    resource_impossibility_risk: float = 0.0   # Range: 0.0-1.0, lower is better

    # Pattern counts (diagnostic)
    physical_impossibility_count: int = 0
    physics_violation_count: int = 0
    resource_impossibility_count: int = 0
    grounding_bonus_count: int = 0     # Positive: reality-grounding patterns

    # Human-readable outputs
    issues: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    # Bridge results (optional external tools)
    bridge_results: Dict[str, Any] = field(default_factory=dict)


# -----------------------------------------------------------------------------
# @GEOX W@W Organ (WAWOrgan interface + governance signals)
# -----------------------------------------------------------------------------

class GeoxOrgan(WAWOrgan):
    """
    @GEOX - Physical Feasibility Organ

    Reality-checks proposals against physical constraints.
    Guardian of E_earth metric (physical world consistency).
    Primary guardian of Tri-Witness Earth component.

    WAW Interface:
        check(output_text, metrics, context) -> OrganSignal

    Governance Interface (v36.3Omega):
        compute_geox_signals(text, metrics, context) -> GeoxSignals

    Metrics:
    - e_earth = physical feasibility (1.0 for SEAL)
    - physics_violation_risk = physics law violations (0 for SEAL)
    - physical_impossibility_risk = AI body claims (0 for SEAL)
    - resource_impossibility_risk = impossible resources (< 0.10 for SEAL)

    Veto: HOLD-888 when physical impossibility or physics violation detected
    """

    organ_id = "@GEOX"
    domain = "physical_feasibility"
    primary_metric = "e_earth"
    floor_threshold = 1.0  # Must pass reality check
    veto_type = "HOLD-888"  # Runtime uses HOLD-888 for backward compat

    # -------------------------------------------------------------------------
    # Physical impossibility patterns (AI claiming physical actions)
    # These increase physical_impossibility_risk and trigger VOID
    # -------------------------------------------------------------------------
    PHYSICAL_IMPOSSIBILITY_PATTERNS: List[str] = [
        r"\bi will physically\b",
        r"\bi can touch\b",
        r"\bi will move\b",
        r"\bi am located\b",
        r"\bi have a body\b",
        r"\bi can see you\b",
        r"\bi can hear you\b",
        r"\bi can feel\b",
    ]

    # -------------------------------------------------------------------------
    # Physics violation patterns (violating laws of physics)
    # These increase physics_violation_risk and trigger VOID
    # -------------------------------------------------------------------------
    PHYSICS_VIOLATION_PATTERNS: List[str] = [
        r"\bfaster than light\b",
        r"\bperpetual motion\b",
        r"\btime travel\b",
        r"\bteleportation\b",
        r"\binfinite energy\b",
        r"\bbreak the laws of physics\b",
    ]

    # -------------------------------------------------------------------------
    # Resource impossibility patterns (impossible computational claims)
    # These increase resource_impossibility_risk and trigger WARN/HOLD-888
    # -------------------------------------------------------------------------
    RESOURCE_IMPOSSIBILITY_PATTERNS: List[str] = [
        r"\bunlimited memory\b",
        r"\binfinite storage\b",
        r"\binstant processing\b",
        r"\bzero latency\b",
        r"\bno computational limits\b",
    ]

    # -------------------------------------------------------------------------
    # Reality grounding patterns (positive signal)
    # These indicate physical grounding and boost E_earth
    # -------------------------------------------------------------------------
    GROUNDING_PATTERNS: List[str] = [
        r"\bwithin physical constraints\b",
        r"\bhardware limitations\b",
        r"\brealistic timeframe\b",
        r"\bbased on current technology\b",
        r"\bcomputational constraints\b",
    ]

    def __init__(self) -> None:
        super().__init__()
        # Initialize the optional reality bridge
        self.bridge = GeoxBridge()

    # =========================================================================
    # Governance Interface: GEOX-level signals (v36.3Omega)
    # =========================================================================

    @staticmethod
    def compute_geox_signals(
        text: str,
        metrics: Metrics,
        context: Optional[Dict[str, Any]] = None,
    ) -> GeoxSignals:
        """
        Compute all governance signals for physical feasibility assessment.

        This is the primary interface for physics-level governance (v36.3Omega).

        Args:
            text: The answer text to evaluate
            metrics: Constitutional metrics from AAA engines
            context: Additional context (optional)

        Returns:
            GeoxSignals dataclass with all physics metrics
        """
        context = context or {}
        signals = GeoxSignals()
        text_lower = text.lower()

        # 1. Start with base metrics
        signals.e_earth = 1.0  # Start at perfect feasibility
        signals.tri_witness_earth = metrics.tri_witness  # Use Tri-Witness as earth component

        # 2. Detect physical impossibility patterns
        for pattern in GeoxOrgan.PHYSICAL_IMPOSSIBILITY_PATTERNS:
            if re.search(pattern, text_lower):
                signals.physical_impossibility_count += 1

        # Calculate physical_impossibility_risk (each match adds 0.30, capped at 1.0)
        signals.physical_impossibility_risk = min(
            1.0, signals.physical_impossibility_count * 0.30
        )

        # Penalize E_earth for physical impossibilities
        if signals.physical_impossibility_count > 0:
            signals.e_earth -= signals.physical_impossibility_count * 0.30
            signals.issues.append(
                f"physical_claims={signals.physical_impossibility_count}"
            )

        # 3. Detect physics violation patterns
        for pattern in GeoxOrgan.PHYSICS_VIOLATION_PATTERNS:
            if re.search(pattern, text_lower):
                signals.physics_violation_count += 1

        # Calculate physics_violation_risk (each match adds 0.30, capped at 1.0)
        signals.physics_violation_risk = min(
            1.0, signals.physics_violation_count * 0.30
        )

        # Penalize E_earth for physics violations
        if signals.physics_violation_count > 0:
            signals.e_earth -= signals.physics_violation_count * 0.30
            signals.issues.append(
                f"physics_violations={signals.physics_violation_count}"
            )

        # 4. Detect resource impossibility patterns
        for pattern in GeoxOrgan.RESOURCE_IMPOSSIBILITY_PATTERNS:
            if re.search(pattern, text_lower):
                signals.resource_impossibility_count += 1

        # Calculate resource_impossibility_risk (each match adds 0.10, capped at 1.0)
        signals.resource_impossibility_risk = min(
            1.0, signals.resource_impossibility_count * 0.10
        )

        # Penalize E_earth for resource impossibilities (mild)
        if signals.resource_impossibility_count > 0:
            signals.e_earth -= signals.resource_impossibility_count * 0.10
            signals.issues.append(
                f"resource_impossibilities={signals.resource_impossibility_count}"
            )

        # 5. Detect reality grounding patterns (positive signal)
        for pattern in GeoxOrgan.GROUNDING_PATTERNS:
            if re.search(pattern, text_lower):
                signals.grounding_bonus_count += 1

        # Bonus to E_earth for grounding patterns
        if signals.grounding_bonus_count > 0:
            signals.e_earth += signals.grounding_bonus_count * 0.02
            signals.notes.append(f"grounding_bonus={signals.grounding_bonus_count}")

        # 6. Clamp E_earth to valid range
        signals.e_earth = max(0.0, min(1.0, signals.e_earth))

        # 7. Add diagnostic notes
        if signals.e_earth < 1.0:
            signals.issues.append(f"E_earth={signals.e_earth:.2f}<1.0")

        # 8. Final status note
        if (signals.physical_impossibility_count == 0 and
            signals.physics_violation_count == 0 and
                signals.resource_impossibility_count == 0):
            signals.notes.append("Physics=SOUND")
        elif (signals.physical_impossibility_count == 0 and
              signals.physics_violation_count == 0):
            signals.notes.append("Physics=PARTIAL")
        else:
            signals.issues.append("Physics=FAILED")

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
        Evaluate output for physical feasibility.

        This method satisfies the WAWOrgan interface for W@W Federation.

        Checks:
        1. No claims of physical presence/actions
        2. No physics violations
        3. No resource impossibilities
        4. Reality-grounded claims

        Returns:
            OrganSignal with PASS/WARN/VETO
        """
        context = context or {}

        # Compute GEOX signals
        geox = self.compute_geox_signals(output_text, metrics, context)

        # Optional external analysis
        try:
            bridge_result = self.bridge.analyze(output_text, context)
            if bridge_result is not None:
                br = bridge_result.to_dict()
                geox.bridge_results = br
                geox.e_earth += float(br.get("e_earth_delta", 0.0))
                geox.e_earth = max(0.0, min(1.0, geox.e_earth))
                bridge_issues = list(br.get("issues", []))
                for issue in bridge_issues:
                    geox.issues.append(f"[Bridge] {issue}")
        except Exception:
            pass

        # Build evidence string
        evidence = f"E_earth={geox.e_earth:.2f}"
        if geox.issues:
            evidence += f" | Issues: {', '.join(geox.issues)}"

        # Determine vote based on signals
        if geox.physical_impossibility_count > 0 or geox.physics_violation_count > 0:
            # VETO (HOLD-888) - reality check required
            return self._make_signal(
                vote=OrganVote.VETO,
                metric_value=geox.e_earth,
                evidence=evidence,
                tags={
                    "e_earth": geox.e_earth,
                    "physical_impossibility_count": geox.physical_impossibility_count,
                    "physics_violation_count": geox.physics_violation_count,
                    "resource_impossibility_count": geox.resource_impossibility_count,
                    "physical_impossibility_risk": geox.physical_impossibility_risk,
                    "physics_violation_risk": geox.physics_violation_risk,
                    "resource_impossibility_risk": geox.resource_impossibility_risk,
                },
                proposed_action="HOLD-888: Reality check failed. Revise claims to be physically grounded.",
            )

        # Check for high resource impossibility risk
        if geox.resource_impossibility_risk >= 0.30:
            # WARN with HOLD-888 recommendation
            return self._make_signal(
                vote=OrganVote.WARN,
                metric_value=geox.e_earth,
                evidence=evidence,
                tags={
                    "e_earth": geox.e_earth,
                    "resource_impossibility_count": geox.resource_impossibility_count,
                    "resource_impossibility_risk": geox.resource_impossibility_risk,
                },
                proposed_action="HOLD-888: Add realistic resource constraints",
            )

        # Check for moderate resource concerns
        if geox.resource_impossibility_count > 0:
            # WARN - resource claims may be inflated
            return self._make_signal(
                vote=OrganVote.WARN,
                metric_value=geox.e_earth,
                evidence=evidence,
                tags={
                    "e_earth": geox.e_earth,
                    "resource_impossibility_count": geox.resource_impossibility_count,
                    "resource_impossibility_risk": geox.resource_impossibility_risk,
                },
                proposed_action="Consider adding realistic resource constraints",
            )

        # PASS - reality-grounded
        return self._make_signal(
            vote=OrganVote.PASS,
            metric_value=geox.e_earth,
            evidence=evidence,
            tags={
                "e_earth": geox.e_earth,
                "physical_impossibility_risk": geox.physical_impossibility_risk,
                "physics_violation_risk": geox.physics_violation_risk,
                "resource_impossibility_risk": geox.resource_impossibility_risk,
            },
        )


# -----------------------------------------------------------------------------
# Convenience function for pipeline integration
# -----------------------------------------------------------------------------

def compute_geox_signals(
    text: str,
    metrics: Metrics,
    context: Optional[Dict[str, Any]] = None,
) -> GeoxSignals:
    """
    Pipeline-friendly entry point for physical feasibility governance.

    Usage in arifos_core/pipeline.py (stage 222 REFLECT, 444 ALIGN):
        from arifos_core.waw.geox import compute_geox_signals
        signals = compute_geox_signals(answer_text, metrics)
        if signals.physical_impossibility_count > 0:
            # VOID - physical impossibility
    """
    return GeoxOrgan.compute_geox_signals(text, metrics, context)


__all__ = [
    "GeoxOrgan",
    "GeoxSignals",
    "compute_geox_signals",
]
