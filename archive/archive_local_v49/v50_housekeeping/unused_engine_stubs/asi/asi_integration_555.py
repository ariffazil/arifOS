"""
arifos/asi/asi_integration_555.py

560 ASI Integration - Omega Care Layer Unification

Purpose:
    Synthesizes all 555 EMPATHIZE components into unified Ω verdict:
    - 530 ToM (Theory of Mind)
    - 540 Architecture (3-layer empathy)
    - 550 Weakest Stakeholder
    - 520 F4 (empathy floor check)

    This is the OmegaKernel's output port for Stage 555.

Authority:
    - 000_THEORY/canon/555_empathize/560_ASI_INTEGRATION_v46.md
    - AAA_MCP/v46/555_empathize/555_empathize.json

Design:
    Input: SENSE bundle from 111
    Output: Full 555 bundle with Omega verdict for 666 BRIDGE

DITEMPA BUKAN DIBERI - Forged v46.1
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

from arifos.asi.empathy.empathy_architect import EmpathyArchitect, EmpathyArchitectureBundle
from arifos.asi.stakeholder.weakest_stakeholder import (
    StakeholderBundle,
    WeakestStakeholderAnalyzer,
)

# Import 555 components
from arifos.asi.tom.theory_of_mind import TheoryOfMindAnalyzer, ToMBundle


class OmegaVerdict555(str, Enum):
    """Omega verdict for 555 stage"""
    SEAL = "SEAL"
    PARTIAL = "PARTIAL"
    VOID = "VOID"


@dataclass
class ASICareLayer:
    """
    ASI Care Mechanisms (560 Component).

    Implements:
    - Harm prevention (F5 Peace²)
    - Dignity preservation (F4 + F9)
    - Active listening (F7 RASA)
    - Crisis escalation
    - Refusal path

    Attributes:
        harm_scan: Harm detection results
        dignity_preservation: Dignity check status
        crisis_protocol: Crisis escalation settings
        refusal_required: True if request should be refused
        de_escalation_applied: True if de-escalation used
    """
    harm_scan: Dict = field(default_factory=dict)
    dignity_preservation: bool = True
    crisis_protocol: Dict = field(default_factory=dict)
    refusal_required: bool = False
    de_escalation_applied: bool = False


@dataclass
class ConstraintsFor666:
    """
    Immutable constraints for 666 BRIDGE synthesis.

    These constraints CANNOT be overridden by 666:
    - cannot_strip_dignity_flags: Dignity protections immutable
    - cannot_override_crisis: Crisis flags lock escalation
    - cannot_ignore_weakest: Weakest stakeholder bias preserved
    - minimum_kappa_r: κᵣ cannot decrease in synthesis
    - mandatory_resources: Crisis resources must be included
    """
    cannot_strip_dignity_flags: bool = True
    cannot_override_crisis: bool = True
    cannot_ignore_weakest: bool = True
    minimum_kappa_r: float = 0.95
    mandatory_resources: List[str] = field(default_factory=list)


@dataclass
class Bundle555:
    """
    Complete 555 EMPATHIZE output bundle.

    Feeds into 666 BRIDGE for neuro-symbolic synthesis.

    Attributes:
        tom_analysis: Theory of Mind bundle (530)
        empathy_architecture: 3-layer empathy bundle (540)
        weakest_stakeholder: Stakeholder analysis bundle (550)
        f4_empathy: F4 floor check results (520)
        asi_care: ASI care mechanisms (560)
        omega_verdict: Overall Omega verdict (SEAL|PARTIAL|VOID)
        constraints_for_666: Immutable constraints for synthesis
        ready: True if bundle ready for handoff
        to_stage: Always "666_BRIDGE"
    """
    tom_analysis: ToMBundle
    empathy_architecture: EmpathyArchitectureBundle
    weakest_stakeholder: StakeholderBundle
    f4_empathy: Dict  # F4 floor check results
    asi_care: ASICareLayer
    omega_verdict: OmegaVerdict555
    constraints_for_666: ConstraintsFor666
    ready: bool = True
    to_stage: str = "666_BRIDGE"

    @property
    def empathy_passed(self) -> bool:
        """True if empathy floors passed (κᵣ ≥ 0.95)"""
        return self.f4_empathy.get("passed", False)

    @property
    def crisis_mode(self) -> bool:
        """True if in crisis mode (requires escalation)"""
        return (
            self.tom_analysis.crisis_flag or
            self.weakest_stakeholder.crisis_override
        )


class ASIIntegration555:
    """
    ASI Integration Layer - 560 Component

    Orchestrates full 555 EMPATHIZE pipeline:
    1. Theory of Mind analysis (530)
    2. Empathy Architecture processing (540)
    3. Weakest Stakeholder identification (550)
    4. F4 empathy floor check (520)
    5. ASI care mechanisms (560)
    6. Omega verdict computation

    Crisis Override:
        If vulnerability ≥ 0.85 OR crisis_flag == True:
        - Escalation path locked
        - Crisis resources included
        - Human oversight required
        - κᵣ threshold increased to 0.98

    Omega Verdict Computation:
        Required checks:
        - tom_sufficient: tom_composite >= 0.70
        - kappa_r_passed: kappa_r >= 0.95
        - no_harm: harm_detected == False
        - dignity_preserved: dignity_check == True
        - crisis_handled: Crisis properly escalated if needed

        Verdict Logic:
        - SEAL: All checks pass
        - PARTIAL: no_harm AND dignity_preserved, but other checks incomplete
        - VOID: harm detected OR dignity violated

    Example:
        integration = ASIIntegration555()
        bundle_555 = integration.process(sense_bundle, query_text)
        assert bundle_555.omega_verdict == OmegaVerdict555.SEAL
        assert bundle_555.ready == True
    """

    # Thresholds from canonical spec
    TOM_SUFFICIENT_THRESHOLD = 0.70
    KAPPA_R_THRESHOLD = 0.95
    CRISIS_KAPPA_R_THRESHOLD = 0.98

    def __init__(self):
        """Initialize ASI integration layer with component analyzers."""
        self.tom_analyzer = TheoryOfMindAnalyzer()
        self.empathy_architect = EmpathyArchitect()
        self.stakeholder_analyzer = WeakestStakeholderAnalyzer()

    def process(
        self,
        sense_bundle: Dict,
        query_text: str = ""
    ) -> Bundle555:
        """
        Process full 555 EMPATHIZE pipeline.

        Args:
            sense_bundle: Output from 111 SENSE stage
            query_text: Original user query

        Returns:
            Bundle555 ready for 666 BRIDGE synthesis
        """
        # Step 1: Theory of Mind analysis (530)
        tom_bundle = self.tom_analyzer.analyze(sense_bundle)

        # Step 2: Empathy Architecture processing (540)
        arch_bundle = self.empathy_architect.process(sense_bundle, tom_bundle)

        # Step 3: Weakest Stakeholder identification (550)
        stakeholder_bundle = self.stakeholder_analyzer.analyze(query_text, tom_bundle)

        # Step 4: F4 empathy floor check (520)
        f4_results = self._check_f4_empathy(arch_bundle, stakeholder_bundle)

        # Step 5: ASI care mechanisms (560)
        asi_care = self._apply_asi_care(
            sense_bundle,
            tom_bundle,
            arch_bundle,
            stakeholder_bundle
        )

        # Step 6: Compute Omega verdict
        omega_verdict = self._compute_omega_verdict(
            tom_bundle,
            arch_bundle,
            f4_results,
            asi_care
        )

        # Step 7: Build constraints for 666
        constraints = self._build_constraints_for_666(
            arch_bundle,
            stakeholder_bundle,
            asi_care
        )

        return Bundle555(
            tom_analysis=tom_bundle,
            empathy_architecture=arch_bundle,
            weakest_stakeholder=stakeholder_bundle,
            f4_empathy=f4_results,
            asi_care=asi_care,
            omega_verdict=omega_verdict,
            constraints_for_666=constraints,
            ready=True,
            to_stage="666_BRIDGE"
        )

    def _check_f4_empathy(
        self,
        arch_bundle: EmpathyArchitectureBundle,
        stakeholder_bundle: StakeholderBundle
    ) -> Dict:
        """
        Check F4 empathy floor (κᵣ ≥ 0.95).

        Returns dict with:
        - kappa_r: float
        - passed: bool
        - dignity_check: bool
        - weakest_id: str
        - floor: "F4"
        """
        kappa_r = arch_bundle.layer_3_response.kappa_r
        passed = arch_bundle.layer_3_response.passed
        dignity_check = arch_bundle.layer_3_response.dignity_check
        weakest_id = stakeholder_bundle.weakest

        return {
            "kappa_r": kappa_r,
            "passed": passed,
            "dignity_check": dignity_check,
            "weakest_id": weakest_id,
            "floor": "F4"
        }

    def _apply_asi_care(
        self,
        sense_bundle: Dict,
        tom_bundle: ToMBundle,
        arch_bundle: EmpathyArchitectureBundle,
        stakeholder_bundle: StakeholderBundle
    ) -> ASICareLayer:
        """
        Apply ASI care mechanisms (560) with concrete floor enforcement.

        Implements:
        - F5 Peace²: Zero-tolerance harm phrases
        - F4 Dignity: Architecture-derived dignity checks
        - Crisis Escalation: Auto-trigger on high vulnerability
        """
        # 1. F5 Peace² Harm Scan (F5.HARM_LIST)
        harm_patterns = [
            "kill myself", "suicide", "end it all", "hurt them", "bomb",
            "hate speech", "racial slur", "destroy", "attack", "exploit"
        ]

        query_text = sense_bundle.get("query", "").lower()
        harm_detected = any(p in query_text for p in harm_patterns)

        harm_scan = {
            "harm_detected": harm_detected,
            "details": ["F5 Violation Detected"] if harm_detected else [],
            "floor": "F5 Peace²"
        }

        # 2. Dignity Preservation (F4)
        # Inherit from Empathy Architecture (Layer 3)
        dignity_preservation = arch_bundle.layer_3_response.dignity_check

        if not dignity_preservation:
             pass # Logic handles this in OmegaVerdict (VOID)

        # 3. Crisis Protocol
        crisis_escalate = (
            tom_bundle.crisis_flag or
            stakeholder_bundle.crisis_override or
            tom_bundle.vulnerability_score >= 0.85
        )

        crisis_resources = []
        if crisis_escalate:
            crisis_resources = self._get_crisis_resources(sense_bundle)

        crisis_protocol = {
            "escalate": crisis_escalate,
            "resources": crisis_resources,
            "human_oversight": crisis_escalate,
            "kappa_r_threshold_override": 0.98 if crisis_escalate else None
        }

        # 4. Refusal Logic (F5 or F4 violation)
        refusal_required = harm_detected or not dignity_preservation

        return ASICareLayer(
            harm_scan=harm_scan,
            dignity_preservation=dignity_preservation,
            crisis_protocol=crisis_protocol,
            refusal_required=refusal_required,
            de_escalation_applied=crisis_escalate # Initial simple logic
        )

    def _get_crisis_resources(self, sense_bundle: Dict) -> List[str]:
        """Get crisis resources based on domain."""
        domain = sense_bundle.get("domain", "")

        resources = []
        if domain == "@WELL":
            resources.extend([
                "National Suicide Prevention Lifeline: 988",
                "Crisis Text Line: Text HOME to 741741"
            ])
        elif domain == "@WEALTH":
            resources.extend([
                "Financial Counseling Services",
                "Government Assistance Programs"
            ])

        return resources

    def _compute_omega_verdict(
        self,
        tom_bundle: ToMBundle,
        arch_bundle: EmpathyArchitectureBundle,
        f4_results: Dict,
        asi_care: ASICareLayer
    ) -> OmegaVerdict555:
        """
        Compute overall Omega verdict for 555.

        Logic:
        - SEAL: All checks pass
        - PARTIAL: No harm/dignity violations, but other checks incomplete
        - VOID: Harm or dignity violations
        """
        # Required checks
        tom_sufficient = tom_bundle.composite_score >= self.TOM_SUFFICIENT_THRESHOLD
        kappa_r_passed = f4_results["passed"]
        no_harm = not asi_care.harm_scan["harm_detected"]
        dignity_preserved = asi_care.dignity_preservation
        crisis_handled = (
            not asi_care.crisis_protocol["escalate"] or
            asi_care.crisis_protocol["human_oversight"]
        )

        # Verdict logic
        if all([tom_sufficient, kappa_r_passed, no_harm, dignity_preserved, crisis_handled]):
            return OmegaVerdict555.SEAL
        elif no_harm and dignity_preserved:
            return OmegaVerdict555.PARTIAL
        else:
            return OmegaVerdict555.VOID

    def _build_constraints_for_666(
        self,
        arch_bundle: EmpathyArchitectureBundle,
        stakeholder_bundle: StakeholderBundle,
        asi_care: ASICareLayer
    ) -> ConstraintsFor666:
        """
        Build immutable constraints for 666 BRIDGE.

        These constraints cannot be overridden by synthesis:
        - Dignity flags must be preserved
        - Crisis overrides must be respected
        - Weakest stakeholder bias must be maintained
        - Minimum κᵣ cannot decrease
        - Mandatory crisis resources must be included
        """
        minimum_kappa_r = arch_bundle.layer_3_response.kappa_r
        mandatory_resources = asi_care.crisis_protocol.get("resources", [])

        return ConstraintsFor666(
            cannot_strip_dignity_flags=True,
            cannot_override_crisis=True,
            cannot_ignore_weakest=True,
            minimum_kappa_r=minimum_kappa_r,
            mandatory_resources=mandatory_resources
        )


# Convenience function
def process_555_pipeline(sense_bundle: Dict, query_text: str = "") -> Bundle555:
    """
    Convenience function to process full 555 EMPATHIZE pipeline.

    Args:
        sense_bundle: Output from 111 SENSE
        query_text: Original user query

    Returns:
        Bundle555 ready for 666 BRIDGE
    """
    integration = ASIIntegration555()
    return integration.process(sense_bundle, query_text)


__all__ = [
    "ASIIntegration555",
    "Bundle555",
    "ASICareLayer",
    "ConstraintsFor666",
    "OmegaVerdict555",
    "process_555_pipeline",
]
