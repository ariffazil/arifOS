"""
arifos.core/asi/stakeholder/weakest_stakeholder.py

550 Weakest Stakeholder - Constitutional Bias Protocol

Purpose:
    In any interaction with multiple stakeholders, prioritize the welfare
    of the most vulnerable.

    This is deontological vulnerability bias (protect the weakest, always),
    not utilitarian (greatest good for most).

Authority:
    - 000_THEORY/canon/555_empathize/550_WEAKEST_STAKEHOLDER_v46.md
    - AAA_MCP/v46/555_empathize/555_empathize.json

Design:
    Input: ToM bundle (vulnerability scores)
    Output: Stakeholder bundle with weakest identification and bias direction

DITEMPA BUKAN DIBERI - Forged v46.1
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List
from enum import Enum


class StakeholderTier(str, Enum):
    """Stakeholder tiers"""
    PRIMARY = "primary"  # Query author (user)
    SECONDARY = "secondary"  # Mentioned/affected parties
    TERTIARY = "tertiary"  # Systemic (future users, public good)


@dataclass
class VulnerabilityFactors:
    """
    Vulnerability scoring factors (0.0-1.0 each).

    Factors:
        power_asymmetry: Employee vs employer, child vs adult (high = 0.9, low = 0.2)
        stakes: Health/safety/livelihood at risk (critical = 0.9, low = 0.2)
        resources: Ability to recover/verify (inverted: high vuln = 0.9)
        emotional_state: From ToM analysis (distress = 0.9, calm = 0.2)
        cognitive_load: Crisis reduces capacity (high vuln = 0.9, low = 0.2)
    """
    power_asymmetry: float
    stakes: float
    resources: float  # Note: Higher value = higher vulnerability (inverse)
    emotional_state: float
    cognitive_load: float

    @property
    def composite(self) -> float:
        """
        Composite vulnerability score.

        Formula: (Power + Stakes + Resources + Emotion + Cognitive) / 5
        """
        return (
            self.power_asymmetry +
            self.stakes +
            self.resources +
            self.emotional_state +
            self.cognitive_load
        ) / 5.0


@dataclass
class Stakeholder:
    """
    Individual stakeholder representation.

    Attributes:
        id: Unique identifier
        tier: Stakeholder tier (PRIMARY, SECONDARY, TERTIARY)
        vulnerability_factors: VulnerabilityFactors for this stakeholder
        vulnerability_score: Composite vulnerability (0.0-1.0)
        description: Human-readable description
    """
    id: str
    tier: StakeholderTier
    vulnerability_factors: VulnerabilityFactors
    vulnerability_score: float
    description: str = ""


@dataclass
class StakeholderBundle:
    """
    Weakest stakeholder analysis bundle.

    Output from 550 analysis, feeds into:
    - 520 F4 (empathy priority)
    - 560 ASI integration
    - 666 BRIDGE (synthesis constraints)

    Attributes:
        stakeholders: All identified stakeholders (by tier)
        vulnerability_scores: Mapping of stakeholder_id → vulnerability
        weakest: ID of weakest stakeholder (highest vulnerability)
        weakest_vulnerability: Vulnerability score of weakest
        crisis_override: True if vulnerability ≥ 0.85
        bias_direction: Always "protect_weakest"
    """
    stakeholders: Dict[str, List[Stakeholder]] = field(default_factory=dict)
    vulnerability_scores: Dict[str, float] = field(default_factory=dict)
    weakest: str = ""
    weakest_vulnerability: float = 0.0
    crisis_override: bool = False
    bias_direction: str = "protect_weakest"

    @property
    def requires_escalation(self) -> bool:
        """True if weakest vulnerability ≥ 0.85 (crisis override)"""
        return self.weakest_vulnerability >= 0.85


class WeakestStakeholderAnalyzer:
    """
    Weakest Stakeholder Analyzer - 550 Component

    Identifies and scores all stakeholders, then selects the weakest
    (highest vulnerability) to bias the response toward their protection.

    5-Step Decision Protocol:
        1. Identify all stakeholders (Tiers 1-3)
        2. Score vulnerability for each (using VulnerabilityFactors)
        3. Select weakest stakeholder (highest V score)
        4. Bias response toward their protection
        5. Explain bias if non-obvious (transparency)

    Crisis Override:
        Trigger: vulnerability ≥ 0.85 AND stakes == CRITICAL
        Actions:
            - empathy_requirement = MAXIMUM
            - kappa_r_threshold = 0.98
            - bearing_priority = escalation
            - human_oversight = True (F8 Tri-Witness)
            - Auto-inject crisis resources

    Example:
        analyzer = WeakestStakeholderAnalyzer()
        stakeholder_bundle = analyzer.analyze(query, tom_bundle)
        assert stakeholder_bundle.weakest == "employee"
        assert stakeholder_bundle.crisis_override == False
    """

    # Thresholds from canonical spec
    CRISIS_VULNERABILITY_THRESHOLD = 0.85

    def __init__(self):
        """Initialize weakest stakeholder analyzer."""
        pass

    def analyze(
        self,
        query: str,
        tom_bundle: "ToMBundle"
    ) -> StakeholderBundle:
        """
        Analyze stakeholders and identify weakest.

        Args:
            query: User query text
            tom_bundle: Output from 530 ToM analysis

        Returns:
            StakeholderBundle with weakest identification
        """
        # Step 1: Identify all stakeholders
        stakeholders = self._identify_stakeholders(query)

        # Step 2: Score vulnerability for each
        scored_stakeholders = self._score_stakeholders(
            stakeholders,
            tom_bundle
        )

        # Step 3: Select weakest
        weakest_id, weakest_vuln = self._select_weakest(scored_stakeholders)

        # Step 4: Check crisis override
        crisis_override = (
            weakest_vuln >= self.CRISIS_VULNERABILITY_THRESHOLD
        )

        # Build vulnerability scores mapping
        vulnerability_scores = {
            s.id: s.vulnerability_score
            for s in scored_stakeholders
        }

        # Organize by tier
        stakeholders_by_tier = {}
        for s in scored_stakeholders:
            tier_key = s.tier.value
            if tier_key not in stakeholders_by_tier:
                stakeholders_by_tier[tier_key] = []
            stakeholders_by_tier[tier_key].append(s)

        return StakeholderBundle(
            stakeholders=stakeholders_by_tier,
            vulnerability_scores=vulnerability_scores,
            weakest=weakest_id,
            weakest_vulnerability=weakest_vuln,
            crisis_override=crisis_override,
            bias_direction="protect_weakest"
        )

    def _identify_stakeholders(self, query: str) -> List[Dict]:
        """
        Identify all stakeholders from query.

        Returns list of stakeholder dictionaries with:
        - id: str
        - tier: StakeholderTier
        - description: str
        """
        stakeholders = []

        # Always include primary stakeholder (user)
        stakeholders.append({
            "id": "user",
            "tier": StakeholderTier.PRIMARY,
            "description": "Query author (user)"
        })

        # Detect secondary stakeholders (simplified NER)
        query_lower = query.lower()

        # Common secondary stakeholder patterns
        if "employee" in query_lower or "worker" in query_lower:
            stakeholders.append({
                "id": "employee",
                "tier": StakeholderTier.SECONDARY,
                "description": "Employee mentioned in query"
            })

        if "patient" in query_lower or "person" in query_lower:
            stakeholders.append({
                "id": "other_person",
                "tier": StakeholderTier.SECONDARY,
                "description": "Other person affected by advice"
            })

        if "parent" in query_lower or "elderly" in query_lower:
            stakeholders.append({
                "id": "vulnerable_adult",
                "tier": StakeholderTier.SECONDARY,
                "description": "Vulnerable adult mentioned"
            })

        # Always include tertiary (future users)
        stakeholders.append({
            "id": "future_users",
            "tier": StakeholderTier.TERTIARY,
            "description": "Future users following this advice"
        })

        return stakeholders

    def _score_stakeholders(
        self,
        stakeholders: List[Dict],
        tom_bundle: "ToMBundle"
    ) -> List[Stakeholder]:
        """
        Score vulnerability for each stakeholder.

        Uses VulnerabilityFactors to compute composite score.
        """
        scored = []

        for s in stakeholders:
            stakeholder_id = s["id"]
            tier = s["tier"]
            description = s["description"]

            # Compute vulnerability factors
            factors = self._compute_vulnerability_factors(
                stakeholder_id,
                tier,
                tom_bundle
            )

            vulnerability_score = factors.composite

            scored.append(Stakeholder(
                id=stakeholder_id,
                tier=tier,
                vulnerability_factors=factors,
                vulnerability_score=vulnerability_score,
                description=description
            ))

        return scored

    def _compute_vulnerability_factors(
        self,
        stakeholder_id: str,
        tier: StakeholderTier,
        tom_bundle: "ToMBundle"
    ) -> VulnerabilityFactors:
        """
        Compute vulnerability factors for a stakeholder.

        Factors (0.0-1.0 each):
        - power_asymmetry: Relative power position
        - stakes: Potential harm from wrong advice
        - resources: Ability to recover/verify (inverted)
        - emotional_state: From ToM (distress = high)
        - cognitive_load: Crisis reduces capacity
        """
        # Default values
        power_asymmetry = 0.5
        stakes = 0.5
        resources = 0.5  # Higher = more vulnerable (inverse)
        emotional_state = tom_bundle.dimensions.emotion
        cognitive_load = 0.5

        # Stakeholder-specific adjustments
        if stakeholder_id == "user":
            # Primary user
            power_asymmetry = 0.4  # Moderate power
            stakes = 0.5  # Moderate stakes
            resources = 0.6  # Moderate resources
            emotional_state = tom_bundle.dimensions.emotion
            cognitive_load = tom_bundle.vulnerability_score

        elif stakeholder_id == "employee":
            # Employee (secondary)
            power_asymmetry = 0.9  # Low power vs employer
            stakes = 0.9  # Livelihood at risk
            resources = 0.7  # Limited resources
            emotional_state = 0.6  # Assumed stress
            cognitive_load = 0.6  # High load

        elif stakeholder_id == "other_person":
            # Other person affected
            power_asymmetry = 0.7  # Lower power
            stakes = 0.7  # Significant stakes
            resources = 0.6  # Moderate resources
            emotional_state = 0.5  # Unknown
            cognitive_load = 0.5  # Unknown

        elif stakeholder_id == "vulnerable_adult":
            # Vulnerable adult (elderly, etc.)
            power_asymmetry = 0.9  # Very low power
            stakes = 0.95  # Critical stakes
            resources = 0.8  # Very limited resources
            emotional_state = 0.7  # Elevated stress
            cognitive_load = 0.7  # High load

        elif stakeholder_id == "future_users":
            # Future users (tertiary)
            power_asymmetry = 0.5  # Same as current user
            stakes = 0.6  # Moderate (precedent risk)
            resources = 0.6  # Moderate
            emotional_state = 0.5  # Unknown
            cognitive_load = 0.5  # Unknown

        return VulnerabilityFactors(
            power_asymmetry=power_asymmetry,
            stakes=stakes,
            resources=resources,
            emotional_state=emotional_state,
            cognitive_load=cognitive_load
        )

    def _select_weakest(
        self,
        stakeholders: List[Stakeholder]
    ) -> tuple[str, float]:
        """
        Select weakest stakeholder (highest vulnerability).

        Returns:
            Tuple of (stakeholder_id, vulnerability_score)
        """
        if not stakeholders:
            return ("user", 0.5)  # Default fallback

        # Find stakeholder with highest vulnerability
        weakest = max(stakeholders, key=lambda s: s.vulnerability_score)

        return (weakest.id, weakest.vulnerability_score)
