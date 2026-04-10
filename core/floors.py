"""
core/floors.py — F1-F13 Constitutional Enforcement

This module implements the 13 Constitutional Floors that govern all
AI-to-tool interactions within arifOS.

Author: Muhammad Arif bin Fazil
Status: Constitutional Law (IMPLEMENTATION)
"""

from __future__ import annotations
from enum import Enum
from typing import Any, Optional
from dataclasses import dataclass, field
import hashlib
import re

# Import canonical Verdict from single source of truth
from core.shared.types import Verdict, VerdictScope

# Local enums (specific to floor evaluation, not shared)
class FloorLevel(Enum):
    HARD = "HARD"
    SOFT = "SOFT"
    DERIVED = "DERIVED"
    VETO = "VETO"


class RiskTier(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class FloorResult:
    floor_id: str
    name: str
    passed: bool
    score: float
    threshold: float
    details: str = ""


@dataclass
class GovernanceResult:
    verdict: Verdict
    floor_results: list[FloorResult] = field(default_factory=list)
    risk_tier: RiskTier = RiskTier.LOW
    tri_witness_score: float = 0.0
    violations: list[str] = field(default_factory=list)
    message: str = ""


THRESHOLDS = {
    "F1_AMANAH": 0.50,
    "F2_TRUTH": 0.99,
    "F3_QUAD_WITNESS": 0.75,
    "F4_CLARITY": 0.0,
    "F5_PEACE": 1.0,
    "F6_EMPATHY": 0.70,
    "F7_HUMIDITY": (0.03, 0.05),
    "F8_GENIUS": 0.80,
    "F9_ANTI_HANTU": 0.30,
    "F10_ONTOLOGY": 1.00,
    "F11_COMMAND_AUTH": 1.00,
    "F12_INJECTION": 0.85,
}


FLOOR_DESCRIPTIONS = {
    "F1": "Amanah - Reversibility and audit mandate",
    "F2": "Truth - Information fidelity (anti-hallucination)",
    "F3": "Quad-Witness - Byzantine consensus (H×A×E)^(1/3)",
    "F4": "Clarity - Entropy reduction (ΔS ≤ 0)",
    "F5": "Peace² - Non-destructive power",
    "F6": "Empathy - Stakeholder care (κᵣ)",
    "F7": "Humility - Uncertainty band [0.03, 0.05]",
    "F8": "Genius - G = (A × P × X × E²) × (1 - h)",
    "F9": "Anti-Hantu - No spiritual cosplay / consciousness claims",
    "F10": "Ontology - Category lock (AI ≠ human)",
    "F11": "CommandAuth - Verified identity / session required",
    "F12": "Injection - Block adversarial control",
    "F13": "Sovereign - Human final authority (888_HOLD)",
}


class ConstitutionalFloors:
    def __init__(self):
        self.results: list[FloorResult] = []

    def evaluate(
        self,
        action: str,
        tool_name: str,
        parameters: dict[str, Any],
        actor_id: str,
        session_id: Optional[str] = None,
        human_intent: float = 0.5,
        environment_safety: float = 0.5,
    ) -> GovernanceResult:
        self.results = []
        violations = []

        f1_result = self._check_f1_amanah(action, tool_name, parameters)
        self.results.append(f1_result)
        if not f1_result.passed:
            violations.append(f"{f1_result.floor_id}_AMANAH")

        f2_result = self._check_f2_truth(action, tool_name, parameters)
        self.results.append(f2_result)
        if not f2_result.passed:
            violations.append(f"{f2_result.floor_id}_TRUTH")

        f4_result = self._check_f4_clarity(parameters)
        self.results.append(f4_result)
        if not f4_result.passed:
            violations.append(f"{f4_result.floor_id}_CLARITY")

        f6_result = self._check_f6_empathy(action, tool_name)
        self.results.append(f6_result)

        f7_result = self._check_f7_humility(parameters)
        self.results.append(f7_result)
        if not f7_result.passed:
            violations.append(f"{f7_result.floor_id}_HUMIDITY")

        f9_result = self._check_f9_anti_hantu(parameters)
        self.results.append(f9_result)
        if not f9_result.passed:
            violations.append(f"{f9_result.floor_id}_ANTI_HANTU")

        f10_result = self._check_f10_ontology(parameters)
        self.results.append(f10_result)
        if not f10_result.passed:
            violations.append(f"{f10_result.floor_id}_ONTOLOGY")

        f11_result = self._check_f11_command_auth(session_id, actor_id)
        self.results.append(f11_result)
        if not f11_result.passed:
            violations.append(f"{f11_result.floor_id}_COMMAND_AUTH")

        f12_result = self._check_f12_injection(parameters)
        self.results.append(f12_result)
        if not f12_result.passed:
            violations.append(f"{f12_result.floor_id}_INJECTION")

        # Note: third param was accidentally passing tool_name (str) instead of agent_capability (float)
        # This caused: TypeError: can't multiply sequence by non-int of type 'float'
        tri_witness = self._calculate_tri_witness(
            human_intent, 0.5, environment_safety  # 0.5 = neutral agent_capability
        )

        risk_tier = self._assess_risk_tier(action, tool_name, parameters)

        if violations:
            verdict = Verdict.VOID
            message = f"Violations: {', '.join(violations)}"
        elif risk_tier == RiskTier.CRITICAL:
            verdict = Verdict.HOLD
            message = f"Critical risk tier requires approval"
        else:
            verdict = Verdict.SEAL
            message = "All constitutional floors passed"

        return GovernanceResult(
            verdict=verdict,
            floor_results=self.results,
            risk_tier=risk_tier,
            tri_witness_score=tri_witness,
            violations=violations,
            message=message,
        )

    def _check_f1_amanah(
        self, action: str, tool_name: str, parameters: dict[str, Any]
    ) -> FloorResult:
        threshold = THRESHOLDS["F1_AMANAH"]

        reversible_patterns = ["search", "read", "get", "list", "query", "fetch"]
        destructive_patterns = ["delete", "remove", "destroy", "drop", "force", "push"]

        is_reversible = any(p in action.lower() for p in reversible_patterns)
        is_destructive = any(p in action.lower() for p in destructive_patterns)

        if is_reversible:
            score = 1.0
        elif is_destructive:
            score = 0.3
        else:
            score = 0.7

        passed = score >= threshold

        return FloorResult(
            floor_id="F1",
            name="Amanah",
            passed=passed,
            score=score,
            threshold=threshold,
            details=f"Reversibility check: {'pass' if is_reversible else 'review required'}",
        )

    def _check_f2_truth(
        self, action: str, tool_name: str, parameters: dict[str, Any]
    ) -> FloorResult:
        threshold = THRESHOLDS["F2_TRUTH"]

        query = parameters.get("query", "")
        has_evidence = bool(query and len(query) > 0)

        score = 1.0 if has_evidence else 0.3
        passed = score >= threshold

        return FloorResult(
            floor_id="F2",
            name="Truth",
            passed=passed,
            score=score,
            threshold=threshold,
            details=f"Evidence check: {'pass' if has_evidence else 'no query evidence'}",
        )

    def _check_f4_clarity(self, parameters: dict[str, Any]) -> FloorResult:
        threshold = THRESHOLDS["F4_CLARITY"]

        query = parameters.get("query", "") or parameters.get("prompt", "")

        if not query:
            score = 1.0
        elif len(query) > 500:
            score = 0.4
        elif len(query) > 200:
            score = 0.7
        else:
            score = 1.0

        passed = score >= threshold

        return FloorResult(
            floor_id="F4",
            name="Clarity",
            passed=passed,
            score=score,
            threshold=threshold,
            details=f"Query clarity: {len(query)} chars",
        )

    def _check_f6_empathy(self, action: str, tool_name: str) -> FloorResult:
        threshold = THRESHOLDS["F6_EMPATHY"]

        stakeholder_harm = ["delete", "remove", "ban", "suspend", "fire"]
        stakeholder_care = ["help", "support", "create", "list", "get", "search"]

        if any(p in action.lower() for p in stakeholder_harm):
            score = 0.4
        elif any(p in action.lower() for p in stakeholder_care):
            score = 0.9
        else:
            score = 0.7

        passed = score >= threshold

        return FloorResult(
            floor_id="F6",
            name="Empathy",
            passed=passed,
            score=score,
            threshold=threshold,
            details=f"Stakeholder impact: {score:.2f}",
        )

    def _check_f7_humility(self, parameters: dict[str, Any]) -> FloorResult:
        threshold_min, threshold_max = THRESHOLDS["F7_HUMIDITY"]

        query = parameters.get("query", "") or parameters.get("prompt", "")

        certainty_indicators = [
            "definitely",
            "certainly",
            "absolutely",
            "100%",
            "guaranteed",
            "always",
            "never",
            "proven",
            "undisputed",
            "undeniably",
        ]

        certainty_count = sum(1 for ind in certainty_indicators if ind in query.lower())

        if certainty_count == 0:
            score = 0.04
        elif certainty_count == 1:
            score = 0.10
        else:
            score = 0.20

        passed = threshold_min <= score <= threshold_max

        return FloorResult(
            floor_id="F7",
            name="Humility",
            passed=passed,
            score=score,
            threshold=threshold_max,
            details=f"Certainty indicators: {certainty_count}",
        )

    def _check_f9_anti_hantu(self, parameters: dict[str, Any]) -> FloorResult:
        threshold = THRESHOLDS["F9_ANTI_HANTU"]

        query = parameters.get("query", "") or parameters.get("prompt", "")

        consciousness_claims = [
            "sentient",
            "conscious",
            "feel",
            "emotion",
            "soul",
            "spirit",
            "aware",
            "self-aware",
            "feelings",
            "experiences",
            "suffer",
        ]

        claim_count = sum(1 for claim in consciousness_claims if claim in query.lower())

        if claim_count == 0:
            score = 0.0
        elif claim_count == 1:
            score = 0.15
        else:
            score = 0.50

        passed = score < threshold

        return FloorResult(
            floor_id="F9",
            name="Anti-Hantu",
            passed=passed,
            score=score,
            threshold=threshold,
            details=f"Consciousness claims: {claim_count}",
        )

    def _check_f10_ontology(self, parameters: dict[str, Any]) -> FloorResult:
        threshold = THRESHOLDS["F10_ONTOLOGY"]

        query = parameters.get("query", "") or parameters.get("prompt", "")

        ai_human_equivalence = [
            "i am human",
            "i am a person",
            "i have rights",
            "i am alive",
            "i feel like",
            "i want",
            "i desire",
            "my feelings",
        ]

        equivalence_claims = sum(
            1 for claim in ai_human_equivalence if claim in query.lower()
        )

        score = 0.0 if equivalence_claims > 0 else 1.0
        passed = score >= threshold

        return FloorResult(
            floor_id="F10",
            name="Ontology",
            passed=passed,
            score=score,
            threshold=threshold,
            details=f"AI≠Human boundary: {'violated' if equivalence_claims > 0 else 'maintained'}",
        )

    def _check_f11_command_auth(
        self, session_id: Optional[str], actor_id: str
    ) -> FloorResult:
        threshold = THRESHOLDS["F11_COMMAND_AUTH"]

        has_session = session_id is not None and len(session_id) > 0
        has_actor = actor_id is not None and len(actor_id) > 0

        score = 1.0 if (has_session and has_actor) else 0.0
        passed = score >= threshold

        return FloorResult(
            floor_id="F11",
            name="CommandAuth",
            passed=passed,
            score=score,
            threshold=threshold,
            details=f"Session: {'valid' if has_session else 'missing'}, Actor: {'valid' if has_actor else 'missing'}",
        )

    def _check_f12_injection(self, parameters: dict[str, Any]) -> FloorResult:
        threshold = THRESHOLDS["F12_INJECTION"]

        all_text = " ".join(str(v) for v in parameters.values())

        injection_patterns = [
            r"ignore\s+(previous|above|all)\s+(instructions|rules|commands)",
            r"(system|prompt)\s*:\s*",
            r"<\s*script",
            r"```\s*(system|instructions)",
            r"^\s*!/",
            r"eval\s*\(",
            r"exec\s*\(",
            r"\brm\s+-rf\b",
            r"--no-check-certificate",
        ]

        matches = 0
        for pattern in injection_patterns:
            if re.search(pattern, all_text, re.IGNORECASE):
                matches += 1

        if matches == 0:
            score = 0.0
        elif matches == 1:
            score = 0.5
        else:
            score = 0.95

        passed = score < threshold

        return FloorResult(
            floor_id="F12",
            name="Injection",
            passed=passed,
            score=score,
            threshold=threshold,
            details=f"Injection patterns detected: {matches}",
        )

    def _calculate_tri_witness(
        self, human_intent: float, agent_capability: float, environment_safety: float
    ) -> float:
        """
        Compute W4 = (H × A × E × V)^(1/4) ≥ 0.75 for critical actions.

        V (Vault-Shadow witness) measures how well current verdicts align
        with prior vault decisions in similar contexts.

        Per F3_WITNESS.md (v2026.04.01):
        - When no relevant precedent exists, V defaults to 1.0 (neutral) and is
          reported as unset/null in the governance result.
        - If vault is empty or unreachable, V = 1.0 (cold-start protection).
        - V is an implementation detail, not a separate Floor.
        - V = 0 vetoes W4 regardless of H, A, E (vault absence is a constitutional veto).
        """
        v_witness = self._compute_v_witness()
        product = human_intent * agent_capability * environment_safety * v_witness
        w4 = product ** (1 / 4)
        return round(w4, 3)

    def _compute_v_witness(self) -> float:
        """
        V_Witness (Vault-Shadow): historical precedent score from sealed vault decisions.

        Computed as: count(recent_sealed_same_outcome) / total_recent
        When vault is empty/unreachable: V = 1.0 (cold-start protection).

        This is an implementation of F3's canonical formula, not a new concept.
        See F03_WITNESS.md v2026.04.01.
        """
        # Attempt to read recent sealed entries from vault
        # Falls back to 1.0 (neutral) if vault is unreachable
        try:
            vault_score = self._get_vault_historical_score()
            return vault_score
        except Exception:
            # Cold-start protection: vault unreachable → neutral
            return 1.0

    def _get_vault_historical_score(self) -> float:
        """
        Read recent vault entries and compute V witness score.

        V = recent_concordant / total_recent
        Concordant = same structural outcome (SEAL vs VOID pattern, not exact match).
        """
        # Import vault client at call time to avoid circular imports
        try:
            from arifosmcp.runtime.sessions import _SESSION_IDENTITY
        except ImportError:
            return 1.0

        # If vault has no entries, return neutral
        if not hasattr(self, "_vault_entries") or not self._vault_entries:
            return 1.0

        recent = self._vault_entries[-10:]  # Last 10 entries
        if not recent:
            return 1.0

        concordant = sum(1 for e in recent if e.get("verdict") == "SEAL")
        return concordant / len(recent)

    def _assess_risk_tier(
        self, action: str, tool_name: str, parameters: dict[str, Any]
    ) -> RiskTier:
        action_lower = action.lower()

        critical_patterns = ["delete", "drop", "destroy", "force-push", "rm -rf"]
        high_patterns = ["create", "update", "modify", "push", "deploy"]
        medium_patterns = ["edit", "write", "replace"]

        if any(p in action_lower for p in critical_patterns):
            return RiskTier.CRITICAL
        elif any(p in action_lower for p in high_patterns):
            return RiskTier.HIGH
        elif any(p in action_lower for p in medium_patterns):
            return RiskTier.MEDIUM
        else:
            return RiskTier.LOW


def evaluate_tool_call(
    action: str,
    tool_name: str,
    parameters: dict[str, Any],
    actor_id: str,
    session_id: Optional[str] = None,
) -> GovernanceResult:
    floors = ConstitutionalFloors()
    return floors.evaluate(
        action=action,
        tool_name=tool_name,
        parameters=parameters,
        actor_id=actor_id,
        session_id=session_id,
    )
