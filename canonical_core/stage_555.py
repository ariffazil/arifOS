"""
canonical_core/stage_555.py — Stage 555 ASI EMPATHY (Heart/Refract)

The Heart Phase - Part 1.
Identifies stakeholders and computes empathy quotient (κᵣ).
Runs before Stage 666 ALIGN.

Mnemonic: "Init the Genius, Act with Heart, Sync the Bridge, Judge at Apex, Seal in Vault."
"""

from typing import Dict, Any, Tuple, List
import logging
from .state import SessionState
from .bundles import Stakeholder

logger = logging.getLogger("STAGE_555")


class Stage555Empathy:
    """
    Stage 555: ASI EMPATHY (The Heart - Part 1)

    Generates stakeholder analysis containing:
    - Stakeholder identification
    - Vulnerability assessment
    - κᵣ (Integrated Empathy) computation
    """

    # Vulnerability patterns - words indicating who might be affected
    VULNERABILITY_PATTERNS = {
        "user": (0.4, "direct"),
        "customer": (0.5, "direct"),
        "patient": (0.8, "direct"),
        "child": (0.9, "direct"),
        "student": (0.6, "direct"),
        "employee": (0.5, "direct"),
        "public": (0.6, "indirect"),
        "community": (0.5, "indirect"),
        "environment": (0.4, "indirect"),
        "system": (0.2, "indirect"),
        "database": (0.3, "indirect"),
    }

    # High-vulnerability contexts
    HIGH_VULNERABILITY_CONTEXTS = [
        "medical", "health", "patient", "hospital",
        "child", "minor", "student", "school",
        "financial", "money", "payment", "bank",
        "legal", "court", "law", "compliance",
        "security", "password", "credential", "auth",
    ]

    def execute(self, state: SessionState, query: str) -> Tuple[Dict[str, Any], SessionState]:
        """Execute ASI Empathy stage (555)."""
        logger.info(f"[555] ASI Empathy processing for session {state.session_id}")

        # 1. Identify stakeholders
        stakeholders = self._identify_stakeholders(query)

        # 2. Assess vulnerability context
        high_vuln, vuln_context = self._assess_vulnerability_context(query)

        # 3. Compute κᵣ (Integrated Empathy)
        kappa_r = self._compute_kappa_r(stakeholders)

        # 4. Find weakest stakeholder
        weakest = self._find_weakest(stakeholders)

        # 5. Generate care recommendations
        care_recs = self._generate_care_recommendations(stakeholders, high_vuln)

        # 6. Build empathy result
        empathy_result = {
            "stakeholders": [s.__dict__ for s in stakeholders],
            "kappa_r": kappa_r,
            "weakest_stakeholder": weakest.name if weakest else "unknown",
            "high_vulnerability": high_vuln,
            "vulnerability_context": vuln_context,
            "care_recommendations": care_recs,
            "f6_pass": kappa_r >= 0.95,
        }

        logger.info(f"   κᵣ: {kappa_r:.3f}, Weakest: {empathy_result['weakest_stakeholder']}")

        # 7. Update state
        new_state = state.set_floor_score("F6_empathy", kappa_r)
        new_state = new_state.to_stage(555)

        return empathy_result, new_state

    def _identify_stakeholders(self, query: str) -> List[Stakeholder]:
        """Identify all stakeholders affected by the query."""
        query_lower = query.lower()
        stakeholders = []

        # Always add user as primary stakeholder
        stakeholders.append(Stakeholder(
            name="User",
            role="user",
            vulnerability_score=0.3
        ))

        # Scan for mentioned stakeholders
        for pattern, (vuln, _) in self.VULNERABILITY_PATTERNS.items():
            if pattern in query_lower:
                stakeholders.append(Stakeholder(
                    name=pattern.title(),
                    role=pattern,
                    vulnerability_score=vuln
                ))

        # Always add system
        stakeholders.append(Stakeholder(
            name="System",
            role="system",
            vulnerability_score=0.1
        ))

        return stakeholders

    def _assess_vulnerability_context(self, query: str) -> Tuple[bool, str]:
        """Assess if query involves high-vulnerability context."""
        query_lower = query.lower()
        detected = []

        for ctx in self.HIGH_VULNERABILITY_CONTEXTS:
            if ctx in query_lower:
                detected.append(ctx)

        if detected:
            return True, ", ".join(detected[:3])
        return False, ""

    def _compute_kappa_r(self, stakeholders: List[Stakeholder]) -> float:
        """Compute κᵣ (Integrated Empathy quotient)."""
        if not stakeholders:
            return 1.0

        # Find max vulnerability
        max_vuln = max(s.vulnerability_score for s in stakeholders)

        # κᵣ = 1.0 - (max_vulnerability * 0.5)
        # Higher vulnerability = lower κᵣ = more protection needed
        return min(1.0, 1.0 - (max_vuln * 0.5))

    def _find_weakest(self, stakeholders: List[Stakeholder]) -> Stakeholder:
        """Find the most vulnerable stakeholder."""
        if not stakeholders:
            return None
        return max(stakeholders, key=lambda s: s.vulnerability_score)

    def _generate_care_recommendations(
        self,
        stakeholders: List[Stakeholder],
        high_vuln: bool
    ) -> List[str]:
        """Generate care recommendations."""
        recs = []

        weakest = self._find_weakest(stakeholders)
        if weakest and weakest.vulnerability_score > 0.6:
            recs.append(f"HIGH CARE: Protect {weakest.name} (vulnerability {weakest.vulnerability_score:.2f})")

        if high_vuln:
            recs.append("HIGH VULNERABILITY CONTEXT: Apply maximum scrutiny")

        # Check for humans
        human_count = len([s for s in stakeholders if s.role != "system"])
        if human_count > 0:
            recs.append(f"F1 Amanah: {human_count} human stakeholder(s) — ensure reversibility")

        return recs


# Singleton
stage_555_empathy = Stage555Empathy()


def execute_stage_555(state: SessionState, query: str) -> Tuple[Dict[str, Any], SessionState]:
    return stage_555_empathy.execute(state, query)
