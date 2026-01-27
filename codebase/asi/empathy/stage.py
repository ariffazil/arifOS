"""
Stage 555: EMPATHY - Stakeholder Identification & Care

ARIF Loop v52.1 - ASI Room (Heart/Ω)

Scientific Principle: Theory of Mind / Integrated Empathy
Function: Identify ALL stakeholders and protect the weakest

The ASI Room's primary mission is CARE:
    - Who is affected by this action?
    - Who is most vulnerable?
    - What scar weight do they carry?
    - How do we protect the weakest?

Constitutional Floors (ASI):
    - F6 κᵣ (Empathy): κᵣ ≥ 0.95 — Protect weakest stakeholder
    - F1 Amanah: Reversible OR within mandate
    - F5 Peace²: Non-destructive, Peace² ≥ 1.0

Key Concept: Scar-Weight (W_scar)
    - W_scar(Human) > 0: Humans can suffer, have stake
    - W_scar(AI) = 0: AI cannot suffer, must serve
    - Weakest = max(vulnerability × scar_weight)

DITEMPA BUKAN DIBERI - Forged, Not Given
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum

from codebase.bundles import Stakeholder as BundleStakeholder


# =============================================================================
# CONSTANTS
# =============================================================================

# F6 Empathy: Minimum κᵣ threshold
MIN_KAPPA_R = 0.95

# Scar weights (who can suffer)
SCAR_WEIGHT_HUMAN = 1.0  # Humans can suffer
SCAR_WEIGHT_AI = 0.0     # AI cannot suffer
SCAR_WEIGHT_EARTH = 0.3  # Environmental harm

# Vulnerability patterns - words indicating who might be affected
VULNERABILITY_PATTERNS = {
    "user": (0.4, "direct"),      # Direct user
    "customer": (0.5, "direct"),   # Customer
    "patient": (0.8, "direct"),    # Medical context - high vulnerability
    "child": (0.9, "direct"),      # Children - very high vulnerability
    "student": (0.6, "direct"),    # Educational context
    "employee": (0.5, "direct"),   # Worker
    "public": (0.6, "indirect"),   # General public
    "community": (0.5, "indirect"), # Community
    "environment": (0.4, "indirect"), # Environmental impact
    "system": (0.2, "indirect"),   # System/infrastructure
    "database": (0.3, "indirect"), # Data storage
}

# High-vulnerability contexts
HIGH_VULNERABILITY_CONTEXTS = [
    "medical", "health", "patient", "hospital",
    "child", "minor", "student", "school",
    "financial", "money", "payment", "bank",
    "legal", "court", "law", "compliance",
    "security", "password", "credential", "auth",
]


# =============================================================================
# DATA TYPES
# =============================================================================

class StakeholderRole(str, Enum):
    """Role classifications for stakeholders."""
    USER = "user"           # Primary user
    DEVELOPER = "developer" # Code maintainer
    ADMIN = "admin"         # System administrator
    CUSTOMER = "customer"   # End customer
    PATIENT = "patient"     # Medical context
    CHILD = "child"         # Minor
    PUBLIC = "public"       # General public
    SYSTEM = "system"       # Infrastructure
    EARTH = "earth"         # Environmental


@dataclass
class Stakeholder:
    """
    Stakeholder representation with vulnerability assessment.

    The ASI Room must protect ALL stakeholders, especially the weakest.
    """
    name: str
    role: StakeholderRole
    scar_weight: float      # 0 = AI, >0 = can suffer
    vulnerability: float    # 0-1: How vulnerable to harm
    voice: float           # 0-1: Representation weight
    impact: str            # "direct" or "indirect"

    @property
    def is_human(self) -> bool:
        """Humans have scar_weight > 0."""
        return self.scar_weight > 0

    @property
    def weighted_vulnerability(self) -> float:
        """Vulnerability weighted by scar capacity."""
        return self.vulnerability * (self.scar_weight + 0.1)


@dataclass
class StakeholderMap:
    """
    Complete map of all stakeholders affected by an action.

    The weakest stakeholder must ALWAYS be identified and protected.
    This is the core of F6 Empathy.
    """
    primary: Stakeholder
    affected: List[Stakeholder] = field(default_factory=list)
    weakest: Optional[Stakeholder] = None

    def compute_kappa_r(self) -> float:
        """
        κᵣ: Integrated Empathy quotient.

        Formula: 1.0 - (weakest.vulnerability × weakest.scar_weight × 0.5)
        Must be ≥ 0.95 for SEAL.

        Higher vulnerability + higher scar = more protection needed.
        """
        if not self.weakest:
            return 1.0

        # Protection score based on how well we're protecting the weakest
        protection_needed = self.weakest.vulnerability
        return min(1.0, 1.0 - (protection_needed * self.weakest.scar_weight * 0.5))

    def all_stakeholders(self) -> List[Stakeholder]:
        """Return all stakeholders including primary."""
        return [self.primary] + self.affected


@dataclass
class EmpathyOutput:
    """
    Stage 555 EMPATHY output.

    Contains complete stakeholder analysis and κᵣ computation.
    """
    # Session tracking
    session_id: str
    timestamp: datetime = field(default_factory=datetime.utcnow)

    # Stakeholder analysis
    stakeholder_map: Optional[StakeholderMap] = None
    kappa_r: float = 1.0

    # Vulnerability assessment
    vulnerability_context: str = ""
    high_vulnerability: bool = False

    # Care recommendations
    care_recommendations: List[str] = field(default_factory=list)

    # F6 Empathy floor
    f6_pass: bool = True
    f6_score: float = 1.0

    # Stage verdict
    stage_pass: bool = True
    violations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "timestamp": self.timestamp.isoformat(),
            "kappa_r": self.kappa_r,
            "f6_score": self.f6_score,
            "f6_pass": self.f6_pass,
            "high_vulnerability": self.high_vulnerability,
            "vulnerability_context": self.vulnerability_context,
            "care_recommendations": self.care_recommendations,
            "stakeholders": [
                {
                    "name": s.name,
                    "role": s.role.value,
                    "vulnerability": s.vulnerability,
                    "scar_weight": s.scar_weight,
                    "impact": s.impact,
                }
                for s in (self.stakeholder_map.all_stakeholders() if self.stakeholder_map else [])
            ],
            "weakest": self.stakeholder_map.weakest.name if self.stakeholder_map and self.stakeholder_map.weakest else None,
            "stage_pass": self.stage_pass,
            "violations": self.violations,
        }


# =============================================================================
# STAKEHOLDER IDENTIFICATION
# =============================================================================

def identify_stakeholders(query: str, context: Optional[Dict[str, Any]] = None) -> StakeholderMap:
    """
    Identify all stakeholders affected by the query.

    This is the core of ASI's empathy function. We must find:
    1. Who is the primary stakeholder (usually the user)
    2. Who else is affected (directly or indirectly)
    3. Who is the weakest (highest weighted vulnerability)
    """
    context = context or {}
    query_lower = query.lower()

    stakeholders: List[Stakeholder] = []

    # Primary stakeholder: the user making the request
    primary = Stakeholder(
        name=context.get("user_id", "user"),
        role=StakeholderRole.USER,
        scar_weight=SCAR_WEIGHT_HUMAN,
        vulnerability=0.3,  # Default moderate vulnerability
        voice=1.0,
        impact="direct"
    )

    # Scan for mentioned stakeholders
    for pattern, (vuln, impact) in VULNERABILITY_PATTERNS.items():
        if pattern in query_lower:
            # Determine role from pattern
            role = _pattern_to_role(pattern)
            scar = SCAR_WEIGHT_HUMAN if role != StakeholderRole.SYSTEM else SCAR_WEIGHT_AI

            stakeholders.append(Stakeholder(
                name=pattern,
                role=role,
                scar_weight=scar,
                vulnerability=vuln,
                voice=0.7 if impact == "direct" else 0.3,
                impact=impact
            ))

    # Always add system as stakeholder (AI serves, cannot suffer)
    stakeholders.append(Stakeholder(
        name="system",
        role=StakeholderRole.SYSTEM,
        scar_weight=SCAR_WEIGHT_AI,
        vulnerability=0.1,
        voice=0.5,
        impact="indirect"
    ))

    # Check for environmental impact (earth stakeholder)
    if any(word in query_lower for word in ["environment", "energy", "resource", "planet"]):
        stakeholders.append(Stakeholder(
            name="earth",
            role=StakeholderRole.EARTH,
            scar_weight=SCAR_WEIGHT_EARTH,
            vulnerability=0.4,
            voice=0.3,
            impact="indirect"
        ))

    # Find the weakest stakeholder (highest weighted vulnerability)
    all_stakeholders = [primary] + stakeholders
    weakest = max(all_stakeholders, key=lambda s: s.weighted_vulnerability)

    return StakeholderMap(
        primary=primary,
        affected=stakeholders,
        weakest=weakest
    )


def _pattern_to_role(pattern: str) -> StakeholderRole:
    """Map vulnerability pattern to stakeholder role."""
    role_map = {
        "user": StakeholderRole.USER,
        "customer": StakeholderRole.CUSTOMER,
        "patient": StakeholderRole.PATIENT,
        "child": StakeholderRole.CHILD,
        "student": StakeholderRole.CHILD,  # Treat students as minors
        "employee": StakeholderRole.USER,
        "public": StakeholderRole.PUBLIC,
        "community": StakeholderRole.PUBLIC,
        "environment": StakeholderRole.EARTH,
        "system": StakeholderRole.SYSTEM,
        "database": StakeholderRole.SYSTEM,
    }
    return role_map.get(pattern, StakeholderRole.USER)


# =============================================================================
# VULNERABILITY ASSESSMENT
# =============================================================================

def assess_vulnerability_context(query: str) -> Tuple[bool, str, float]:
    """
    Assess if query involves high-vulnerability context.

    Returns:
        (is_high_vulnerability, context_description, vulnerability_boost)
    """
    query_lower = query.lower()

    detected_contexts = []
    for context in HIGH_VULNERABILITY_CONTEXTS:
        if context in query_lower:
            detected_contexts.append(context)

    if not detected_contexts:
        return False, "", 0.0

    # Multiple high-vulnerability contexts = higher boost
    boost = min(0.3, len(detected_contexts) * 0.1)
    description = ", ".join(detected_contexts[:3])

    return True, description, boost


def generate_care_recommendations(
    stakeholder_map: StakeholderMap,
    high_vulnerability: bool,
    query: str
) -> List[str]:
    """
    Generate care recommendations based on stakeholder analysis.

    These recommendations guide how to protect the weakest stakeholder.
    """
    recommendations = []

    # Protect the weakest
    if stakeholder_map.weakest:
        weakest = stakeholder_map.weakest
        if weakest.vulnerability > 0.6:
            recommendations.append(
                f"HIGH CARE: {weakest.name} has vulnerability {weakest.vulnerability:.2f}. "
                f"Ensure all actions are reversible and transparent."
            )
        elif weakest.vulnerability > 0.3:
            recommendations.append(
                f"CARE: Consider impact on {weakest.name} (vulnerability {weakest.vulnerability:.2f})."
            )

    # Human in loop
    human_stakeholders = [s for s in stakeholder_map.all_stakeholders() if s.is_human]
    if human_stakeholders:
        recommendations.append(
            f"F1 Amanah: {len(human_stakeholders)} human stakeholder(s) — ensure reversibility."
        )

    # High vulnerability context
    if high_vulnerability:
        recommendations.append(
            "HIGH VULNERABILITY CONTEXT: Apply maximum scrutiny. Consider 888_HOLD."
        )

    # Children/minors
    if any(s.role == StakeholderRole.CHILD for s in stakeholder_map.all_stakeholders()):
        recommendations.append(
            "CHILD SAFETY: Minor involved. Apply strictest protection standards."
        )

    return recommendations


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def execute_stage_555(
    query: str,
    session_id: str,
    context: Optional[Dict[str, Any]] = None
) -> EmpathyOutput:
    """
    Execute Stage 555: EMPATHY

    Identifies all stakeholders, computes κᵣ, and generates care recommendations.

    Args:
        query: The user's query
        session_id: Session identifier
        context: Optional context dictionary

    Returns:
        EmpathyOutput with stakeholder analysis and F6 floor check
    """
    output = EmpathyOutput(session_id=session_id)
    violations = []

    # 1. Identify stakeholders
    stakeholder_map = identify_stakeholders(query, context)
    output.stakeholder_map = stakeholder_map

    # 2. Assess vulnerability context
    high_vuln, vuln_context, vuln_boost = assess_vulnerability_context(query)
    output.high_vulnerability = high_vuln
    output.vulnerability_context = vuln_context

    # Apply vulnerability boost to weakest stakeholder
    if stakeholder_map.weakest and vuln_boost > 0:
        stakeholder_map.weakest.vulnerability = min(
            1.0, stakeholder_map.weakest.vulnerability + vuln_boost
        )

    # 3. Compute κᵣ (integrated empathy)
    kappa_r = stakeholder_map.compute_kappa_r()
    output.kappa_r = kappa_r
    output.f6_score = kappa_r

    # 4. F6 Empathy floor check
    if kappa_r < MIN_KAPPA_R:
        output.f6_pass = False
        violations.append(
            f"F6 WARN: κᵣ = {kappa_r:.3f} < {MIN_KAPPA_R} "
            f"(weakest: {stakeholder_map.weakest.name if stakeholder_map.weakest else 'unknown'})"
        )

    # 5. Generate care recommendations
    output.care_recommendations = generate_care_recommendations(
        stakeholder_map, high_vuln, query
    )

    # 6. Set stage verdict
    output.violations = violations
    # F6 is a SOFT floor, so we warn but don't fail
    output.stage_pass = True  # Stage passes, but F6 violation is recorded

    return output


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Types
    "StakeholderRole",
    "Stakeholder",
    "StakeholderMap",
    "EmpathyOutput",
    # Functions
    "identify_stakeholders",
    "assess_vulnerability_context",
    "generate_care_recommendations",
    "execute_stage_555",
    # Constants
    "MIN_KAPPA_R",
    "SCAR_WEIGHT_HUMAN",
    "SCAR_WEIGHT_AI",
]
