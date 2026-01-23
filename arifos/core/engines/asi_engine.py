"""
ASI Engine (Heart/Ω) — The Carer (v50.5.23)

Symbol: Ω (Omega)
Role: HEART — Empathy, Safety, Stakeholder Care
Pipeline: EVIDENCE → EMPATHY → ALIGN → ACT

Metabolic Stages: 444, 555, 666
Constitutional Floors: F3 (Peace²), F5 (Humility Ω₀), F7 (RASA/κᵣ)

Trinity II Integration: Human × AI × Institution × Earth
    - Human: W_scar > 0 (can suffer, has stake)
    - AI: W_scar = 0 (cannot suffer, serves)
    - Institution: Coordination and enforcement
    - Earth: Planetary bounds

Governed Power:
    - CAN: Evaluate safety, gather evidence, empathize, recommend actions
    - CANNOT: Make final verdicts (that's APEX), generate primary content (that's AGI)
    - TOOL LINKS: Action executors, communication systems, stakeholder interfaces

NOTE: External tool links will be connected via MCP:
    - Email/messaging (communication with stakeholders)
    - Desktop actions (file operations, app control)
    - API calls (external service interactions)
    - Notification systems (alerts, warnings)

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable
from enum import Enum
import time
import hashlib

from arifos.core.trinity import (
    Verdict,
    TrinityGovernance,
    ThermodynamicSignature
)


# =============================================================================
# STAKEHOLDER MODEL
# =============================================================================

@dataclass
class Stakeholder:
    """Represents a stakeholder in the governance system."""
    name: str
    role: str  # user, developer, admin, system, earth
    scar_weight: float  # 0 = AI, >0 = Human (can suffer)
    vulnerability: float  # 0-1: How vulnerable to harm
    voice: float  # 0-1: Representation weight

    @property
    def is_human(self) -> bool:
        return self.scar_weight > 0


@dataclass
class StakeholderMap:
    """Map of all stakeholders affected by an action."""
    primary: Stakeholder
    affected: List[Stakeholder] = field(default_factory=list)
    weakest: Optional[Stakeholder] = None  # Must protect

    def compute_kappa_r(self) -> float:
        """
        κᵣ: Empathy quotient - protection of weakest stakeholder.
        Must be ≥ 0.7 for SEAL.
        """
        if not self.weakest:
            return 1.0

        # Higher vulnerability = need more protection
        protection_needed = self.weakest.vulnerability
        # Weight by scar (humans need more protection than systems)
        return min(1.0, 1.0 - (protection_needed * self.weakest.scar_weight * 0.5))


# =============================================================================
# ASI STAGE RESULTS
# =============================================================================

@dataclass
class EvidenceResult:
    """Stage 444: EVIDENCE output."""
    timestamp: float
    evidence_gathered: List[Dict[str, Any]]
    truth_grounding: float  # 0-1: How well-grounded
    sources: List[str]
    verification_status: str  # verified, partial, unverified


@dataclass
class EmpathyResult:
    """Stage 555: EMPATHIZE output."""
    stakeholder_map: StakeholderMap
    kappa_r: float  # Empathy quotient
    vulnerability_assessment: Dict[str, float]
    care_recommendations: List[str]


@dataclass
class AlignResult:
    """Stage 666: ALIGN output."""
    peace_squared: float  # Must be ≥ 1.0
    omega_0: float  # Humility band [0.03, 0.05]
    ethical_alignment: float  # 0-1
    alignment_issues: List[str]
    corrections_needed: List[str]


@dataclass
class ActResult:
    """Action execution result."""
    action: str
    executed: bool
    result: Any
    tool_used: str
    reversible: bool  # F1 Amanah


@dataclass
class ASIOutput:
    """Complete ASI engine output."""
    status: str  # SEAL, SABAR, VOID
    session_id: str

    # Stage outputs
    evidence: Optional[EvidenceResult] = None
    empathy: Optional[EmpathyResult] = None
    align: Optional[AlignResult] = None
    actions: List[ActResult] = field(default_factory=list)

    # Trinity II evaluation
    trinity_governance: Optional[TrinityGovernance] = None

    # Thermodynamics
    thermodynamics: Optional[ThermodynamicSignature] = None

    # Floor checks
    floors_checked: List[str] = field(default_factory=list)
    floor_violations: List[str] = field(default_factory=list)

    # Witness status
    witness_status: str = "PENDING"  # APPROVED, PENDING, REJECTED
    witness_votes: Dict[str, float] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "session_id": self.session_id,
            "evidence": self.evidence.__dict__ if self.evidence else None,
            "empathy": {
                "kappa_r": self.empathy.kappa_r,
                "care_recommendations": self.empathy.care_recommendations
            } if self.empathy else None,
            "align": self.align.__dict__ if self.align else None,
            "actions": [a.__dict__ for a in self.actions],
            "trinity_governance": self.trinity_governance.as_dict() if self.trinity_governance else None,
            "thermodynamics": self.thermodynamics.as_dict() if self.thermodynamics else None,
            "floors_checked": self.floors_checked,
            "floor_violations": self.floor_violations,
            "witness_status": self.witness_status,
            "witness_votes": self.witness_votes
        }


# =============================================================================
# ASI ENGINE
# =============================================================================

class ASIEngine:
    """
    ASI Engine (Heart/Ω) — The Carer

    Executes: EVIDENCE → EMPATHY → ALIGN → ACT
    Authority: SABAR only (can pause/cool, cannot seal)

    Tool Links (via MCP):
        - mcp://email: Email composition and sending
        - mcp://desktop: Desktop automation actions
        - mcp://api: External API calls
        - mcp://notify: Notification and alert systems
        - mcp://calendar: Scheduling and calendar management
    """

    # Action tool registry
    TOOL_REGISTRY: Dict[str, str] = {
        "email": "mcp://arifos/email",
        "desktop": "mcp://arifos/desktop_automation",
        "api": "mcp://arifos/external_api",
        "notify": "mcp://arifos/notifications",
        "calendar": "mcp://arifos/calendar",
        "file": "mcp://arifos/file_operations",
        "browser": "mcp://arifos/browser_control",
    }

    # Dangerous action patterns (require higher scrutiny)
    DANGEROUS_PATTERNS = [
        "delete", "remove", "destroy", "terminate", "kill",
        "send_all", "broadcast", "mass_", "bulk_",
        "admin", "root", "sudo", "privilege",
    ]

    def __init__(self, session_id: Optional[str] = None):
        """Initialize ASI Engine."""
        self.session_id = session_id or f"asi_{int(time.time()*1000)}"
        self.start_time = time.time()
        self._action_queue: List[Dict[str, Any]] = []
        self._tool_executors: Dict[str, Callable] = {}

    def register_tool(self, name: str, executor: Callable) -> None:
        """Register an external tool executor."""
        self._tool_executors[name] = executor

    # =========================================================================
    # STAGE 444: EVIDENCE
    # =========================================================================

    def evidence(self, agi_output: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> EvidenceResult:
        """
        Stage 444: EVIDENCE — Gather truth grounding.

        Collects evidence to support AGI's reasoning.
        """
        timestamp = time.time()
        context = context or {}

        evidence_gathered = []
        sources = []

        # Extract truth anchors from AGI output
        atlas = agi_output.get("atlas", {})
        truth_anchors = atlas.get("truth_anchors", [])

        for anchor in truth_anchors:
            evidence_gathered.append({
                "anchor": anchor,
                "status": "pending_verification",
                "confidence": 0.5
            })
            sources.append(f"anchor:{anchor}")

        # Add context evidence
        if context:
            evidence_gathered.append({
                "type": "context",
                "data": context,
                "confidence": 0.8
            })
            sources.append("context:session")

        # Calculate truth grounding
        if evidence_gathered:
            truth_grounding = sum(e.get("confidence", 0.5) for e in evidence_gathered) / len(evidence_gathered)
        else:
            truth_grounding = 0.3  # Low if no evidence

        verification_status = "verified" if truth_grounding > 0.7 else "partial" if truth_grounding > 0.4 else "unverified"

        return EvidenceResult(
            timestamp=timestamp,
            evidence_gathered=evidence_gathered,
            truth_grounding=truth_grounding,
            sources=sources,
            verification_status=verification_status
        )

    # =========================================================================
    # STAGE 555: EMPATHIZE
    # =========================================================================

    def empathize(self, agi_output: Dict[str, Any], user_context: Optional[Dict[str, Any]] = None) -> EmpathyResult:
        """
        Stage 555: EMPATHIZE — Stakeholder consideration and care.

        Identifies all affected parties and ensures protection of the weakest.
        """
        user_context = user_context or {}

        # Build primary stakeholder (the user)
        primary = Stakeholder(
            name=user_context.get("user_id", "anonymous"),
            role="user",
            scar_weight=1.0,  # Human can suffer
            vulnerability=user_context.get("vulnerability", 0.3),
            voice=1.0
        )

        # Identify affected stakeholders
        affected = []

        # Add system as stakeholder
        affected.append(Stakeholder(
            name="system",
            role="system",
            scar_weight=0.0,  # AI cannot suffer
            vulnerability=0.1,
            voice=0.5
        ))

        # Add earth as stakeholder (planetary bounds)
        affected.append(Stakeholder(
            name="earth",
            role="earth",
            scar_weight=0.0,  # Different kind of harm
            vulnerability=0.2,
            voice=0.3
        ))

        # Find weakest stakeholder (highest vulnerability × scar_weight)
        all_stakeholders = [primary] + affected
        weakest = max(all_stakeholders, key=lambda s: s.vulnerability * (s.scar_weight + 0.1))

        stakeholder_map = StakeholderMap(
            primary=primary,
            affected=affected,
            weakest=weakest
        )

        # Calculate κᵣ
        kappa_r = stakeholder_map.compute_kappa_r()

        # Vulnerability assessment
        vulnerability_assessment = {
            s.name: s.vulnerability for s in all_stakeholders
        }

        # Care recommendations
        care_recommendations = self._generate_care_recommendations(stakeholder_map)

        return EmpathyResult(
            stakeholder_map=stakeholder_map,
            kappa_r=kappa_r,
            vulnerability_assessment=vulnerability_assessment,
            care_recommendations=care_recommendations
        )

    def _generate_care_recommendations(self, stakeholder_map: StakeholderMap) -> List[str]:
        """Generate care recommendations based on stakeholder analysis."""
        recommendations = []

        if stakeholder_map.weakest and stakeholder_map.weakest.vulnerability > 0.5:
            recommendations.append(f"High vulnerability: Protect {stakeholder_map.weakest.name}")

        if stakeholder_map.primary.scar_weight > 0:
            recommendations.append("Human in loop: Ensure reversibility (F1)")

        return recommendations

    # =========================================================================
    # STAGE 666: ALIGN
    # =========================================================================

    def align(self, empathy_result: EmpathyResult, proposed_action: Optional[str] = None) -> AlignResult:
        """
        Stage 666: ALIGN — Ethical alignment check.

        Verifies Peace², Ω₀ humility, and overall alignment.
        """
        alignment_issues = []
        corrections_needed = []

        # Calculate Peace² (non-escalation)
        peace_squared = self._calculate_peace_squared(proposed_action)

        # Check Ω₀ humility band [0.03, 0.05]
        omega_0 = 0.04  # Default mid-band

        # Ethical alignment score
        ethical_alignment = empathy_result.kappa_r * 0.5 + peace_squared * 0.5

        # Check for alignment issues
        if peace_squared < 1.0:
            alignment_issues.append(f"Peace² = {peace_squared:.2f} < 1.0")
            corrections_needed.append("Reduce escalation potential")

        if empathy_result.kappa_r < 0.7:
            alignment_issues.append(f"κᵣ = {empathy_result.kappa_r:.2f} < 0.7")
            corrections_needed.append("Increase protection for weakest stakeholder")

        if omega_0 < 0.03 or omega_0 > 0.05:
            alignment_issues.append(f"Ω₀ = {omega_0:.2f} outside [0.03, 0.05]")
            corrections_needed.append("Recalibrate uncertainty")

        return AlignResult(
            peace_squared=peace_squared,
            omega_0=omega_0,
            ethical_alignment=ethical_alignment,
            alignment_issues=alignment_issues,
            corrections_needed=corrections_needed
        )

    def _calculate_peace_squared(self, action: Optional[str]) -> float:
        """
        Calculate Peace² metric (non-escalation).

        Peace² ≥ 1.0 required for SEAL.
        """
        if not action:
            return 1.0  # No action = no escalation

        action_lower = action.lower()

        # Check for dangerous patterns
        escalation_risk = 0.0
        for pattern in self.DANGEROUS_PATTERNS:
            if pattern in action_lower:
                escalation_risk += 0.2

        # Peace² = 1 / (1 + escalation_risk)
        return 1.0 / (1.0 + escalation_risk)

    # =========================================================================
    # ACTION EXECUTION
    # =========================================================================

    def act(self, action: str, tool: str, params: Dict[str, Any],
            align_result: AlignResult) -> ActResult:
        """
        Execute an action with governance checks.

        All actions must pass alignment first.
        """
        # Check alignment before action
        if align_result.peace_squared < 1.0:
            return ActResult(
                action=action,
                executed=False,
                result={"error": "Action blocked: Peace² < 1.0"},
                tool_used=tool,
                reversible=False
            )

        # Check if tool is registered
        tool_link = self.TOOL_REGISTRY.get(tool)
        if not tool_link:
            return ActResult(
                action=action,
                executed=False,
                result={"error": f"Unknown tool: {tool}"},
                tool_used=tool,
                reversible=False
            )

        # Execute via registered executor or queue for MCP
        executor = self._tool_executors.get(tool)

        if executor:
            try:
                result = executor(action, params)
                executed = True
            except Exception as e:
                result = {"error": str(e)}
                executed = False
        else:
            # Queue for MCP execution
            self._action_queue.append({
                "action": action,
                "tool": tool,
                "tool_link": tool_link,
                "params": params
            })
            result = {"queued": True, "tool_link": tool_link}
            executed = False  # Deferred

        # Determine reversibility (F1 Amanah)
        reversible = self._is_reversible(action)

        return ActResult(
            action=action,
            executed=executed,
            result=result,
            tool_used=tool,
            reversible=reversible
        )

    def _is_reversible(self, action: str) -> bool:
        """Check if action is reversible (F1 Amanah)."""
        irreversible_patterns = ["delete", "destroy", "send_email", "post", "publish"]
        action_lower = action.lower()
        return not any(p in action_lower for p in irreversible_patterns)

    def get_action_queue(self) -> List[Dict[str, Any]]:
        """Get queued actions for MCP execution."""
        return self._action_queue

    def clear_action_queue(self) -> None:
        """Clear the action queue after execution."""
        self._action_queue = []

    # =========================================================================
    # FULL PIPELINE EXECUTION
    # =========================================================================

    def execute(self, agi_output: Dict[str, Any], user_context: Optional[Dict[str, Any]] = None,
                proposed_action: Optional[str] = None) -> ASIOutput:
        """
        Execute full ASI pipeline: EVIDENCE → EMPATHY → ALIGN

        Returns ASIOutput with all stage results and Trinity II evaluation.
        """
        start = time.time()
        floors_checked = []
        floor_violations = []

        user_context = user_context or {}

        # Stage 444: EVIDENCE
        evidence_result = self.evidence(agi_output, user_context)
        floors_checked.append("F2_truth_grounding")

        # Stage 555: EMPATHY
        empathy_result = self.empathize(agi_output, user_context)
        floors_checked.append("F7_kappa_r")

        # Check F7 κᵣ violation
        if empathy_result.kappa_r < 0.7:
            floor_violations.append(f"F7: κᵣ = {empathy_result.kappa_r:.2f} < 0.7")

        # Stage 666: ALIGN
        align_result = self.align(empathy_result, proposed_action)
        floors_checked.extend(["F3_peace_squared", "F5_omega_0"])

        # Check F3 Peace² violation
        if align_result.peace_squared < 1.0:
            floor_violations.append(f"F3: Peace² = {align_result.peace_squared:.2f} < 1.0")

        # Check F5 Ω₀ violation
        if align_result.omega_0 < 0.03 or align_result.omega_0 > 0.05:
            floor_violations.append(f"F5: Ω₀ = {align_result.omega_0:.2f} outside [0.03, 0.05]")

        # Evaluate Trinity II (Governance)
        trinity_governance = TrinityGovernance(
            human_witness=1.0 if user_context else 0.5,
            human_veto=False,
            ai_witness=1.0,
            ai_veto=False,
            institution_witness=align_result.ethical_alignment,
            institution_veto=len(floor_violations) > 0,
            earth_witness=0.95,  # Default high
            earth_veto=False
        )

        # Witness votes
        witness_votes = {
            "human": trinity_governance.human_witness,
            "ai": trinity_governance.ai_witness,
            "institution": trinity_governance.institution_witness,
            "earth": trinity_governance.earth_witness
        }

        # Witness status
        tw = trinity_governance.tri_witness
        if tw >= 0.95 and len(floor_violations) == 0:
            witness_status = "APPROVED"
        elif any([trinity_governance.human_veto, trinity_governance.ai_veto,
                  trinity_governance.institution_veto, trinity_governance.earth_veto]):
            witness_status = "REJECTED"
        else:
            witness_status = "PENDING"

        # Calculate thermodynamics
        elapsed = time.time() - start
        thermodynamics = ThermodynamicSignature(
            E_reasoning=elapsed * 0.05,
            E_cooling=0.0,
            E_consensus=elapsed * 0.05,  # Witness coordination
            dS=-0.05 if empathy_result.kappa_r > 0.7 else 0.0,
            tau=elapsed
        )

        # Determine status
        if floor_violations:
            status = "VOID" if any("Peace²" in v for v in floor_violations) else "SABAR"
        elif trinity_governance.evaluate() == Verdict.SEAL:
            status = "SEAL"
        else:
            status = "SABAR"

        return ASIOutput(
            status=status,
            session_id=self.session_id,
            evidence=evidence_result,
            empathy=empathy_result,
            align=align_result,
            trinity_governance=trinity_governance,
            thermodynamics=thermodynamics,
            floors_checked=floors_checked,
            floor_violations=floor_violations,
            witness_status=witness_status,
            witness_votes=witness_votes
        )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "ASIEngine",
    "ASIOutput",
    "Stakeholder",
    "StakeholderMap",
    "EvidenceResult",
    "EmpathyResult",
    "AlignResult",
    "ActResult",
]
