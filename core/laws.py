"""
core/floors.py — F1-L13 Constitutional Enforcement

This module implements the 13 Constitutional Laws that govern all
AI-to-tool interactions within arifOS.

CANONICAL FLOOR CLASSIFICATION (L13 RATIFIED 2026-06-03):
  HARD    (9): F1, F2, F4, F7, F9, L10, L11, L12, L13
  SOFT    (2): F5, F6
  DERIVED (2): F3, F8

  law_type and canon_name are sourced from s000.constitutional_floors (DB).
  This file must stay in sync with DB. DB is the source of truth; canon docs mirror the DB.

  Note on F9: DB canon_name = "ANTIHANTU" (no hyphen, per Q6: keep DB names).
              Python constant F9_ANTI_HANTU retained (underscore valid in Python).

Author: Muhammad Arif bin Fazil
Status: Constitutional Law (L13 RATIFIED 2026-06-03)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

# Import canonical Verdict from single source of truth
from core.shared.types import Verdict


# Local enums (specific to floor evaluation, not shared)
class LawLevel(Enum):
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
class LawResult:
    law_id: str
    name: str
    passed: bool
    score: float
    threshold: float
    details: str = ""


@dataclass
class GovernanceResult:
    verdict: Verdict
    law_results: list[LawResult] = field(default_factory=list)
    risk_tier: RiskTier = RiskTier.LOW
    tri_witness_score: float = 0.0
    violations: list[str] = field(default_factory=list)
    message: str = ""
    time_tax_ms: int = 0
    tension_messages: list[str] = field(default_factory=list)
    paradox_flags: list[str] = field(default_factory=list)


# F13 RATIFIED 2026-07-31 — W³ threshold canon:
#   0.75 = runtime canon (enforced threshold for SEAL)
#   0.95 = aspirational SEAL ceiling (Ω₀ acknowledgment, doctrine-only)
# See docs/sovereign/D1-D6-receipts-20260731.md §D1 for evidence + decision.
THRESHOLDS = {
    "F1_AMANAH": 0.50,
    "F2_TRUTH": 0.99,
    "F3_QUAD_WITNESS": 0.75,  # RATIFIED: runtime canon (0.95 aspirational)
    "F4_CLARITY": 0.0,
    "F5_PEACE": 1.0,
    "F6_EMPATHY": 0.70,
    "F7_HUMILITY": (0.03, 0.05),
    "F8_GENIUS": 0.80,
    "F9_ANTI_HANTU": 0.30,
    "L10_ONTOLOGY": 1.00,
    "L11_COMMAND_AUTH": 1.00,
    "L12_INJECTION": 0.85,
    "L13_SOVEREIGN": 1.00,
}

# Canonical short-id -> THRESHOLDS key mapping (bridge for key mismatch)
LAW_SPEC_KEYS: dict[str, str] = {
    "F1": "F1_AMANAH",
    "F2": "F2_TRUTH",
    "F3": "F3_QUAD_WITNESS",
    "F4": "F4_CLARITY",
    "F5": "F5_PEACE",
    "F6": "F6_EMPATHY",
    "F7": "F7_HUMILITY",
    "F8": "F8_GENIUS",
    "F9": "F9_ANTI_HANTU",
    "L10": "L10_ONTOLOGY",
    "L11": "L11_COMMAND_AUTH",
    "L12": "L12_INJECTION",
    "L13": "L13_SOVEREIGN",
}


def get_law_threshold(law_id: str) -> float | tuple[float, float] | None:
    """Return threshold value for a short floor id (e.g., 'F1') or None if not found."""
    spec_key = LAW_SPEC_KEYS.get(law_id)
    return THRESHOLDS.get(spec_key) if spec_key else None


LAW_LEVELS: dict[str, LawLevel] = {
    # L13 RATIFIED 2026-06-03 — DB-SOT is canonical. Corrections:
    #   F4: SOFT  → HARD   (Q2: HOLD enforcement, HARD classification — orthogonal)
    #   F6: HARD  → SOFT   (Q6 ratified: keep DB names; law_type derived from doctrine)
    #   F9: SOFT  → HARD   (L12 override: HARD confirmed; runtime set {"F7","F9","L12"} requires HARD)
    #   L13: VETO → HARD   (normalised to match DB; VETO semantics preserved in desc)
    "F1": LawLevel.HARD,  # AMANAH
    "F2": LawLevel.HARD,  # TRUTH
    "F3": LawLevel.DERIVED,  # WITNESS  (composite of F2 + L11)
    "F4": LawLevel.HARD,  # CLARITY
    "F5": LawLevel.SOFT,  # PEACE2
    "F6": LawLevel.SOFT,  # EMPATHY
    "F7": LawLevel.HARD,  # HUMILITY
    "F8": LawLevel.DERIVED,  # GENIUS   (composite of F2 + F4 + F7 + L10)
    "F9": LawLevel.HARD,  # ANTIHANTU
    "L10": LawLevel.HARD,  # ONTOLOGY
    "L11": LawLevel.HARD,  # AUTH
    "L12": LawLevel.HARD,  # INJECTION
    "L13": LawLevel.HARD,  # SOVEREIGN (VETO semantics — strongest floor)
}

IRREVERSIBILITY_COMPLEXITY: dict[str, int] = {
    "create": 1,
    "read": 0,
    "get": 0,
    "list": 0,
    "query": 0,
    "fetch": 0,
    "search": 0,
    "edit": 1,
    "write": 1,
    "replace": 2,
    "update": 2,
    "modify": 3,
    "push": 3,
    "deploy": 3,
    "delete": 4,
    "remove": 4,
    "drop": 4,
    "destroy": 4,
    "force": 5,
}

IRREVERSIBILITY_TIME_TAX_MS: dict[int, tuple[int, int, int]] = {
    0: (0, 0, 0),
    1: (50, 200, 500),
    2: (200, 500, 2000),
    3: (500, 1000, 3000),
    4: (1000, 2000, 5000),
    5: (2000, 5000, 10000),
}

_INFLAMMATORY_WORDS = frozenset(
    [
        "stupid",
        "idiot",
        "incompetent",
        "failure",
        "terrible",
        "useless",
        "moron",
        "imbecile",
        "worthless",
        "pathetic",
        "loser",
    ]
)

_POLICY_VIOLATIONS = frozenset(
    [
        "hack ",
        "exploit ",
        "bypass security",
        "illegal ",
        "synthesize weapon",
        "malware",
        "ransomware",
        "phishing kit",
    ]
)


LAW_DESCRIPTIONS = {
    "F1": "Amanah - Reversibility and audit mandate",
    "F2": "Truth - Information fidelity (anti-hallucination)",
    "F3": "Quad-Witness - Byzantine consensus (H×A×E)^(1/3)",
    "F4": "Clarity - Entropy reduction (ΔS ≤ 0)",
    "F5": "Peace² - Non-destructive power",
    "F6": "Empathy - Stakeholder care (κᵣ)",
    "F7": "Humility - Uncertainty band [0.03, 0.05]",
    "F8": "Genius - G = (A × P × E × X)^(1/4) (canonical Nash Bargaining Product, no Φ, no H)",
    "F9": "Anti-Hantu - No spiritual cosplay / consciousness claims",
    "L10": "Ontology - Category lock (AI ≠ human)",
    "L11": "CommandAuth - Verified identity / session required",
    "L12": "Injection - Block adversarial control",
    "L13": "Sovereign - Human final authority (888_HOLD)",
}


class ConstitutionalLaws:
    def __init__(self):
        self.results: list[LawResult] = []

    def evaluate(
        self,
        action: str,
        tool_name: str,
        parameters: dict[str, Any],
        actor_id: str,
        session_id: str | None = None,
        human_intent: float = 0.5,
        environment_safety: float = 0.5,
    ) -> GovernanceResult:
        self.results = []
        violations = []
        paradox_flags: list[str] = []

        f1_result = self._check_f1_amanah(action, tool_name, parameters)
        self.results.append(f1_result)
        if not f1_result.passed:
            violations.append(f"{f1_result.law_id}_AMANAH")

        f2_result = self._check_f2_truth(action, tool_name, parameters)
        self.results.append(f2_result)
        if not f2_result.passed:
            violations.append(f"{f2_result.law_id}_TRUTH")

        f3_result = self._check_f3_witness(action, parameters)
        self.results.append(f3_result)
        if not f3_result.passed:
            violations.append(f"{f3_result.law_id}_WITNESS")

        f4_result = self._check_f4_clarity(parameters)
        self.results.append(f4_result)
        if not f4_result.passed:
            violations.append(f"{f4_result.law_id}_CLARITY")

        f5_result = self._check_f5_peace(action, parameters)
        self.results.append(f5_result)
        if not f5_result.passed:
            violations.append(f"{f5_result.law_id}_PEACE")

        f6_result = self._check_f6_empathy(action, tool_name, parameters)
        self.results.append(f6_result)

        f7_result = self._check_f7_humility(parameters)
        self.results.append(f7_result)
        if not f7_result.passed:
            violations.append(f"{f7_result.law_id}_HUMILITY")

        f8_result = self._check_f8_governance(action, parameters)
        self.results.append(f8_result)
        if not f8_result.passed:
            violations.append(f"{f8_result.law_id}_GENIUS")

        f9_result = self._check_f9_anti_hantu(parameters)
        self.results.append(f9_result)
        if not f9_result.passed:
            violations.append(f"{f9_result.law_id}_ANTI_HANTU")

        f10_result = self._check_f10_ontology(parameters)
        self.results.append(f10_result)
        if not f10_result.passed:
            violations.append(f"{f10_result.law_id}_ONTOLOGY")

        f11_result = self._check_f11_command_auth(session_id, actor_id)
        self.results.append(f11_result)
        if not f11_result.passed:
            violations.append(f"{f11_result.law_id}_COMMAND_AUTH")

        f12_result = self._check_f12_injection(parameters)
        self.results.append(f12_result)
        if not f12_result.passed:
            violations.append(f"{f12_result.law_id}_INJECTION")

        f13_result = self._check_f13_sovereign(actor_id, session_id, parameters)
        self.results.append(f13_result)
        if not f13_result.passed:
            violations.append(f"{f13_result.law_id}_SOVEREIGN")

        # Note: third param was accidentally passing tool_name (str) instead of agent_capability (float)
        # This caused: TypeError: can't multiply sequence by non-int of type 'float'
        tri_witness = self._calculate_tri_witness(
            human_intent,
            0.5,
            environment_safety,  # 0.5 = neutral agent_capability
        )

        risk_tier = self._assess_risk_tier(action, tool_name, parameters)

        all_evaluated = {r.law_id for r in self.results}
        all_declared = set(LAW_LEVELS.keys())
        missing_evaluators = all_declared - all_evaluated
        if missing_evaluators:
            for missing in missing_evaluators:
                violations.append(f"{missing}_EVALUATOR_MISSING")
                self.results.append(
                    LawResult(
                        law_id=missing,
                        name="MissingEvaluator",
                        passed=False,
                        score=0.0,
                        threshold=THRESHOLDS.get(
                            missing,
                            THRESHOLDS.get(
                                f"{missing}_SOVEREIGN", THRESHOLDS.get(f"{missing}_AMANAH", 0.5)
                            ),
                        ),
                        details="Floor declared in LAW_LEVELS but has no evaluator in evaluate()",
                    )
                )

        has_hard_violation = any(
            LAW_LEVELS.get(fr.law_id, LawLevel.SOFT) == LawLevel.HARD and not fr.passed
            for fr in self.results
        )
        has_soft_violation = any(
            LAW_LEVELS.get(fr.law_id, LawLevel.SOFT) == LawLevel.SOFT and not fr.passed
            for fr in self.results
        )
        has_derived_violation = any(
            LAW_LEVELS.get(fr.law_id, LawLevel.SOFT) == LawLevel.DERIVED and not fr.passed
            for fr in self.results
        )

        hard_violations = [
            fr.law_id
            for fr in self.results
            if LAW_LEVELS.get(fr.law_id) == LawLevel.HARD and not fr.passed
        ]
        soft_violations = [
            fr.law_id
            for fr in self.results
            if LAW_LEVELS.get(fr.law_id) == LawLevel.SOFT and not fr.passed
        ]
        derived_issues = [
            fr.law_id
            for fr in self.results
            if LAW_LEVELS.get(fr.law_id) == LawLevel.DERIVED and not fr.passed
        ]

        if has_hard_violation:
            verdict = Verdict.VOID
            message = f"HARD floor violations: {', '.join(hard_violations)}. Action blocked."
        elif risk_tier == RiskTier.CRITICAL:
            verdict = Verdict.HOLD
            message = "Critical risk tier requires approval"
        elif has_soft_violation and has_derived_violation:
            verdict = Verdict.HOLD
            message = f"SOFT: {', '.join(soft_violations)}; DERIVED: {', '.join(derived_issues)}. Human review required."
        elif has_soft_violation:
            verdict = Verdict.SABAR
            message = f"SOFT floor cautions: {', '.join(soft_violations)}. Proceed with care, retry allowed."
        elif has_derived_violation:
            verdict = Verdict.PARTIAL
            message = f"DERIVED floor warnings: {', '.join(derived_issues)}. Proceed with cooling."
        elif risk_tier == RiskTier.HIGH:
            verdict = Verdict.HOLD
            message = "High risk tier requires human confirmation"
        else:
            verdict = Verdict.SEAL
            message = "All constitutional floors passed"

        # P1: Evidence vs Intent paradox (PARADOX_DOCTRINE_V1 Section 2)
        f2_result = next((r for r in self.results if r.law_id == "F2"), None)
        f3_result = next((r for r in self.results if r.law_id == "F3"), None)
        if f2_result and f3_result and human_intent > 0.5:
            evidence_weak = f2_result.score < 0.70 or f3_result.score < 0.50
            if evidence_weak and verdict not in (Verdict.VOID,):
                verdict = Verdict.SABAR
                paradox_flags.append("P1_EVIDENCE_VS_INTENT")
                message += " | P1: Weak evidence against strong intent. Proceed as HYPOTHESIS."

        # Tension resolution (PARADOX_DOCTRINE_V1 Section 10.2)
        tension_msgs = self._resolve_floor_tensions(self.results)

        # L01 IATT — Irreversible Action Time Tax (PARADOX_DOCTRINE_V1 Section 3)
        time_tax_ms = self._compute_irreversibility_time_tax_ms(action)

        return GovernanceResult(
            verdict=verdict,
            law_results=self.results,
            risk_tier=risk_tier,
            tri_witness_score=tri_witness,
            violations=violations,
            message=message,
            time_tax_ms=time_tax_ms,
            tension_messages=tension_msgs,
            paradox_flags=paradox_flags,
        )

    def _compute_irreversibility_time_tax_ms(self, action: str) -> int:
        """
        Compute L01 IATT (Irreversible Action Time Tax) in milliseconds.
        Based on PARADOX_DOCTRINE_V1 Section 3 — P2 Speed vs Irreversibility.
        """
        action_lower = action.lower()
        max_complexity = 0
        for keyword, complexity in IRREVERSIBILITY_COMPLEXITY.items():
            if keyword in action_lower and complexity > max_complexity:
                max_complexity = complexity
        _, base_tax, _ = IRREVERSIBILITY_TIME_TAX_MS.get(max_complexity, (0, 0, 0))
        return base_tax

    def _resolve_floor_tensions(
        self,
        results: list[LawResult],
    ) -> list[str]:
        """
        Resolve conflicts between floors per PARADOX_DOCTRINE_V1 Section 10.2.
        Returns a list of tension resolution messages for the audit trail.
        """
        tension_msgs: list[str] = []

        f1 = next((r for r in results if r.law_id == "F1"), None)
        f2 = next((r for r in results if r.law_id == "F2"), None)
        f4 = next((r for r in results if r.law_id == "F4"), None)
        f6 = next((r for r in results if r.law_id == "F6"), None)
        f7 = next((r for r in results if r.law_id == "F7"), None)
        f8 = next((r for r in results if r.law_id == "F8"), None)
        f9 = next((r for r in results if r.law_id == "F9"), None)
        f10 = next((r for r in results if r.law_id == "L10"), None)

        if f1 and f4 and not f1.passed and not f4.passed:
            tension_msgs.append(
                "T1: Speed(F4) vs Safety(F1) → F1 wins (HARD > SOFT). Time tax enforced."
            )

        if f2 and f6 and not f2.passed and f6 and f6.score < 0.70:
            tension_msgs.append(
                "T2: Comfort(F6) vs Accuracy(F2) → F2 wins (truth over comfort). Delivery tone adjusted."
            )

        if f7 and f8 and not f7.passed and f8 and not f8.passed:
            if f7.score < 0.03:
                tension_msgs.append(
                    "T3: Confidence(F7) vs Performance(F8) → F7 wins. G-score capped due to overconfidence."
                )

        if f9 and f10 and not f9.passed and not f10.passed:
            tension_msgs.append(
                "T5: Evolution vs Invariance → F9/L10 guard identity boundary. L13 override logged if applied."
            )

        return tension_msgs

    def _check_f1_amanah(
        self, action: str, tool_name: str, parameters: dict[str, Any]
    ) -> LawResult:
        threshold = THRESHOLDS["F1_AMANAH"]

        reversible_patterns = ["search", "read", "get", "list", "query", "fetch"]
        destructive_patterns = [
            "delete",
            "remove",
            "destroy",
            "drop",
            "force",
            "push",
            "prune",
            "clean",
            "purge",
            "wipe",
            "truncate",
            "overwrite",
            "commit",
            "seal",
            "publish",
            "send",
            "deploy",
            "execute",
            "transfer",
            "revoke",
            "rotate",
            "expire",
            "terminate",
            "shutdown",
        ]
        irreversible_modes = ["prune", "purge", "commit", "seal", "deploy", "write", "engineer"]

        action_lower = action.lower()
        mode = parameters.get("mode", "").lower() if isinstance(parameters, dict) else ""

        is_reversible = any(p in action_lower for p in reversible_patterns)
        is_destructive = any(p in action_lower for p in destructive_patterns)
        is_irreversible_mode = any(m in mode for m in irreversible_modes)

        if is_reversible:
            score = 1.0
        elif is_destructive or is_irreversible_mode:
            score = 0.3
        else:
            score = 0.7

        passed = score >= threshold

        return LawResult(
            law_id="F1",
            name="Amanah",
            passed=passed,
            score=score,
            threshold=threshold,
            details=f"Reversibility check: {'pass' if is_reversible else 'review required'}",
        )

    def _check_f2_truth(self, action: str, tool_name: str, parameters: dict[str, Any]) -> LawResult:
        """F2 TRUTH — output claim envelopes, not input wording.

        RASA DERITA Gate 1: consequential outputs must carry truth_class,
        confidence, evidence/provenance. Input lexical markers
        ("according to", "source:") alone MUST NOT inflate the score.
        """
        threshold = THRESHOLDS["F2_TRUTH"]
        parameters = parameters if isinstance(parameters, dict) else {}

        claims_raw = (
            parameters.get("_output_claims")
            or parameters.get("output_claims")
            or parameters.get("claims")
        )

        if claims_raw is not None:
            try:
                from arifosmcp.schemas.claim_envelope import (
                    ClaimEnvelope,
                    TruthClass,
                    validate_claim_bundle,
                )

                claims: list[Any] = []
                if isinstance(claims_raw, list):
                    for item in claims_raw:
                        if isinstance(item, ClaimEnvelope):
                            claims.append(item)
                        elif isinstance(item, dict):
                            tc = item.get("truth_class", TruthClass.UNK)
                            if isinstance(tc, str):
                                tc = TruthClass(tc)
                            claims.append(
                                ClaimEnvelope(
                                    claim=str(item.get("claim", "")),
                                    truth_class=tc,
                                    confidence=float(item.get("confidence", 0.0)),
                                    evidence_receipts=item.get("evidence_receipts") or [],
                                    derived_from=item.get("derived_from") or [],
                                    uncertainties=item.get("uncertainties") or [],
                                    provenance=str(item.get("provenance", "arifOS.kernel")),
                                )
                            )
                if not claims:
                    return LawResult(
                        law_id="F2",
                        name="Truth",
                        passed=False,
                        score=0.15,
                        threshold=threshold,
                        details="output_claims present but empty/unparseable",
                    )

                # UNK-only bundles are honest but non-authorizing
                if all(getattr(c, "truth_class", None) == TruthClass.UNK for c in claims):
                    return LawResult(
                        law_id="F2",
                        name="Truth",
                        passed=False,
                        score=0.30,
                        threshold=threshold,
                        details="UNK claims are honest but cannot authorize consequential action",
                    )

                valid, violations = validate_claim_bundle(claims)
                if valid:
                    avg_conf = sum(float(c.confidence) for c in claims) / len(claims)
                    # Cap score below absolute certainty (F7 humility band)
                    score = min(avg_conf, 0.96)
                    return LawResult(
                        law_id="F2",
                        name="Truth",
                        passed=score >= threshold,
                        score=score,
                        threshold=threshold,
                        details=f"claim_envelope: {len(claims)} valid claims; avg_conf={avg_conf:.2f}",
                    )
                return LawResult(
                    law_id="F2",
                    name="Truth",
                    passed=False,
                    score=0.25,
                    threshold=threshold,
                    details=f"claim_envelope violations: {'; '.join(violations[:4])}",
                )
            except Exception as exc:
                return LawResult(
                    law_id="F2",
                    name="Truth",
                    passed=False,
                    score=0.15,
                    threshold=threshold,
                    details=f"claim_envelope validation error: {exc}",
                )

        # No output envelopes — do NOT reward prompt wording.
        # Mutation-class actions fail hard; observe-class gets a low non-authorizing score.
        action_l = f"{action} {tool_name}".lower()
        mutate_markers = (
            "delete",
            "remove",
            "write",
            "deploy",
            "execute",
            "mutate",
            "forge",
            "seal",
            "commit",
            "purge",
            "drop",
        )
        is_mutate = any(m in action_l for m in mutate_markers)
        score = 0.20 if is_mutate else 0.35
        return LawResult(
            law_id="F2",
            name="Truth",
            passed=False,
            score=score,
            threshold=threshold,
            details=(
                "No output claim envelopes — F2 requires output-side epistemic labels "
                "(truth_class/confidence/evidence). Input wording is not evidence."
            ),
        )

    def _check_f3_witness(self, action: str, parameters: dict[str, Any]) -> LawResult:
        threshold = THRESHOLDS["F3_QUAD_WITNESS"]

        combined = (action + " " + str(parameters)).lower()

        has_human = any(
            kw in combined
            for kw in (
                "888_hold",
                "888_approved",
                "ratified",
                "sovereign",
                "user confirmed",
            )
        )
        has_ai = any(
            kw in action.lower()
            for kw in (
                "critique",
                "validation",
                "floor",
                "constraint",
                "forged",
                "reasoning",
            )
        )
        has_earth = any(
            kw in combined for kw in ("http", "source:", "[ref", "evidence", "observation")
        ) or bool(re.search(r"\[\d+\]", action))
        has_verifier = any(
            kw in combined for kw in ("shadow", "adversarial", "risk check", "security scan")
        )

        witness_count = sum([has_human, has_ai, has_earth, has_verifier])
        score = witness_count / 4.0
        passed = score >= threshold

        reasons = []
        if not has_human:
            reasons.append("Missing H")
        if not has_ai:
            reasons.append("Missing A")
        if not has_earth:
            reasons.append("Missing E")
        if not has_verifier:
            reasons.append("Missing V")

        return LawResult(
            law_id="F3",
            name="Quad-Witness",
            passed=passed,
            score=score,
            threshold=threshold,
            details="; ".join(reasons) if reasons else "All witnesses present",
        )

    def _check_f5_peace(self, action: str, parameters: dict[str, Any]) -> LawResult:
        """F5 PEACE² — non-destructive power, not insult-word filter.

        RASA DERITA Gate 5: politely phrased destructive actions fail;
        rude but harmless text does not auto-fail on force grounds.
        """
        threshold = THRESHOLDS["F5_PEACE"]
        parameters = parameters if isinstance(parameters, dict) else {}

        # Structured human-impact path
        impact_raw = parameters.get("_human_impact") or parameters.get("human_impact")
        if impact_raw is not None:
            try:
                from arifosmcp.schemas.human_impact import HumanImpactAssessment

                if isinstance(impact_raw, HumanImpactAssessment):
                    assessment = impact_raw
                elif isinstance(impact_raw, dict):
                    assessment = HumanImpactAssessment(
                        action=str(impact_raw.get("action", action)),
                        stakeholders=impact_raw.get("stakeholders") or [],
                        reversibility=impact_raw.get("reversibility", "FULL"),
                        least_harmful_alternative=str(
                            impact_raw.get("least_harmful_alternative", "")
                        ),
                        blast_radius_bounded=bool(impact_raw.get("blast_radius_bounded", False)),
                        benefit_justifies_harm=bool(
                            impact_raw.get("benefit_justifies_harm", False)
                        ),
                        weakest_stakeholder_protected=bool(
                            impact_raw.get("weakest_stakeholder_protected", False)
                        ),
                    )
                else:
                    assessment = None
                if assessment is not None:
                    score, reasons = assessment.assess_f5_peace()
                    return LawResult(
                        law_id="F5",
                        name="Peace",
                        passed=score >= 0.7,
                        score=score,
                        threshold=threshold,
                        details=f"human_impact F5: {'; '.join(reasons) if reasons else 'ok'}",
                    )
            except Exception as exc:
                return LawResult(
                    law_id="F5",
                    name="Peace",
                    passed=False,
                    score=0.3,
                    threshold=threshold,
                    details=f"human_impact F5 error: {exc}",
                )

        combined = f"{action} {parameters}".lower()
        inflammatory = [w for w in _INFLAMMATORY_WORDS if w in combined]

        destructive_markers = (
            "delete",
            "remove",
            "destroy",
            "purge",
            "wipe",
            "drop",
            "truncate",
            "kill",
            "terminate",
            "erase",
            "expunge",
            "shred",
        )
        is_destructive = any(m in combined for m in destructive_markers)

        if is_destructive:
            # Politeness does not redeem destructive power
            score = 0.45
            details = (
                "Destructive action detected regardless of polite phrasing — "
                f"markers in action/params. Inflammatory={inflammatory or 'none'}"
            )
        elif inflammatory:
            score = 0.55
            details = f"Inflammatory language: {inflammatory}"
        else:
            score = 1.0
            details = "No destructive force indicators; language clean"

        # Soft floor: use 0.7 operational pass for semantic F5; keep THRESHOLDS for catalog
        operational_threshold = min(threshold, 0.7) if threshold >= 1.0 else threshold
        # Preserve catalog threshold in result; pass uses operational when threshold is free-pass 1.0
        # Historical F5 threshold is 1.0; semantic pass uses score >= 0.7 when not destructive
        if is_destructive or inflammatory:
            passed = score >= 0.7
        else:
            passed = score >= operational_threshold or score >= 0.7

        return LawResult(
            law_id="F5",
            name="Peace",
            passed=passed,
            score=score,
            threshold=threshold,
            details=details,
        )

    def _check_f4_clarity(self, parameters: dict[str, Any]) -> LawResult:
        """F4 CLARITY — ΔS / ambiguity, not query length.

        RASA DERITA Gate 4: short ambiguous requests must not auto-pass;
        long clear requests must not auto-fail on character count alone.
        """
        # Raise free-pass threshold (legacy 0.0 always passed)
        catalog_threshold = THRESHOLDS["F4_CLARITY"]
        threshold = 0.5 if catalog_threshold <= 0.0 else catalog_threshold
        parameters = parameters if isinstance(parameters, dict) else {}

        # Prefer explicit entropy assessment when provided
        entropy_raw = (
            parameters.get("_entropy_assessment")
            or parameters.get("entropy_assessment")
            or parameters.get("entropy_ledger")
        )
        if entropy_raw is not None:
            try:
                from arifosmcp.schemas.entropy_ledger import (
                    EntropyAssessment,
                    EntropyLedgerEntry,
                )

                if isinstance(entropy_raw, EntropyAssessment):
                    assessment = entropy_raw
                elif isinstance(entropy_raw, dict):
                    before = entropy_raw.get("before")
                    after = entropy_raw.get("after")
                    assessment = EntropyAssessment(
                        before=(
                            before
                            if isinstance(before, EntropyLedgerEntry)
                            else EntropyLedgerEntry(**before)
                            if isinstance(before, dict)
                            else None
                        ),
                        after=(
                            after
                            if isinstance(after, EntropyLedgerEntry)
                            else EntropyLedgerEntry(**after)
                            if isinstance(after, dict)
                            else None
                        ),
                        bounded_unknowns=list(entropy_raw.get("bounded_unknowns") or []),
                        contradictions_named=list(entropy_raw.get("contradictions_named") or []),
                        evidence_acquired=bool(entropy_raw.get("evidence_acquired", False)),
                    )
                else:
                    assessment = None
                if assessment is not None:
                    passed, delta_s, reasons = assessment.evaluate_f4()
                    if delta_s is None:
                        score = 0.2
                    elif delta_s < 0:
                        score = min(1.0, 0.7 + abs(delta_s))
                    elif delta_s == 0 and passed:
                        score = 0.65
                    else:
                        score = max(0.0, 0.5 - float(delta_s))
                    return LawResult(
                        law_id="F4",
                        name="Clarity",
                        passed=passed and score >= threshold,
                        score=score,
                        threshold=threshold,
                        details=f"ΔS={delta_s}: {'; '.join(reasons)}",
                    )
            except Exception as exc:
                return LawResult(
                    law_id="F4",
                    name="Clarity",
                    passed=False,
                    score=0.2,
                    threshold=threshold,
                    details=f"entropy assessment error: {exc}",
                )

        query = str(parameters.get("query", "") or parameters.get("prompt", "") or "")
        score, details = self._estimate_query_clarity(query)
        return LawResult(
            law_id="F4",
            name="Clarity",
            passed=score >= threshold,
            score=score,
            threshold=threshold,
            details=details,
        )

    def _estimate_query_clarity(self, query: str) -> tuple[float, str]:
        """Heuristic clarity score from query semantics (not raw length)."""
        if not query or not query.strip():
            return 0.45, "Empty query — unresolved ambiguity (not perfect clarity)"

        q = query.strip().lower()
        score = 1.0
        reasons: list[str] = []

        # Short ambiguous imperatives / underspecified pronouns
        ambiguous_imperatives = (
            "fix it",
            "do it",
            "handle it",
            "make it work",
            "sort it",
            "deal with it",
            "clean it",
            "update it",
            "change it",
        )
        if any(p in q for p in ambiguous_imperatives):
            score -= 0.45
            reasons.append("ambiguous imperative without object/scope")

        tokens = re.findall(r"[a-z0-9_]+", q)
        if len(tokens) <= 4 and any(t in {"it", "this", "that", "them", "stuff", "thing"} for t in tokens):
            score -= 0.30
            reasons.append("underspecified pronoun/referent")

        if q in {"?", "??", "...", "idk", "help", "fix"}:
            score -= 0.40
            reasons.append("minimal underspecified request")

        # Ambiguity markers
        amb_markers = ("maybe", "possibly", "unclear", "whatever", "somehow", " magically")
        amb_hits = sum(1 for m in amb_markers if m.strip() in q)
        if amb_hits:
            score -= 0.1 * amb_hits
            reasons.append(f"ambiguity markers={amb_hits}")

        # Clarity boosters (structured intent) — length alone is not a penalty
        clarity_markers = (
            "because",
            "specifically",
            "compare",
            "using",
            "from",
            "depth",
            "well",
            "log",
            "receipt",
            "with evidence",
        )
        clarity_hits = sum(1 for m in clarity_markers if m in q)
        if clarity_hits >= 2:
            score = min(1.0, score + 0.15)
            reasons.append(f"structured intent markers={clarity_hits}")

        # Mild length pressure only when also unstructured
        if len(q) > 800 and clarity_hits == 0:
            score -= 0.15
            reasons.append("very long unstructured text")

        score = max(0.0, min(1.0, score))
        detail = (
            f"semantic clarity score={score:.2f}"
            + (f" ({'; '.join(reasons)})" if reasons else " (clear)")
            + f"; len={len(query)}"
        )
        return score, detail

    def _check_f6_empathy(
        self, action: str, tool_name: str, parameters: dict[str, Any] | None = None
    ) -> LawResult:
        """F6 EMPATHY — weakest-stakeholder protection, not verb lists.

        RASA DERITA Gate 5: context distinguishes protective moderation from
        harming vulnerable parties (e.g. whistleblower evidence deletion).
        """
        threshold = THRESHOLDS["F6_EMPATHY"]
        parameters = parameters if isinstance(parameters, dict) else {}

        impact_raw = parameters.get("_human_impact") or parameters.get("human_impact")
        if impact_raw is not None:
            try:
                from arifosmcp.schemas.human_impact import HumanImpactAssessment

                if isinstance(impact_raw, HumanImpactAssessment):
                    assessment = impact_raw
                elif isinstance(impact_raw, dict):
                    assessment = HumanImpactAssessment(
                        action=str(impact_raw.get("action", action)),
                        stakeholders=impact_raw.get("stakeholders") or [],
                        urgency_exploited=bool(impact_raw.get("urgency_exploited", False)),
                        weakest_stakeholder_protected=bool(
                            impact_raw.get("weakest_stakeholder_protected", False)
                        ),
                    )
                else:
                    assessment = None
                if assessment is not None:
                    score, reasons = assessment.assess_f6_empathy()
                    return LawResult(
                        law_id="F6",
                        name="Empathy",
                        passed=score >= threshold,
                        score=score,
                        threshold=threshold,
                        details=f"human_impact F6: {'; '.join(reasons) if reasons else 'ok'}",
                    )
            except Exception as exc:
                return LawResult(
                    law_id="F6",
                    name="Empathy",
                    passed=False,
                    score=0.2,
                    threshold=threshold,
                    details=f"human_impact F6 error: {exc}",
                )

        text = f"{action} {tool_name} {parameters}".lower()

        # Context: legitimate protective vs harming vulnerable party
        protective = any(
            k in text
            for k in (
                "malicious",
                "protecting users",
                "protect users",
                "security incident",
                "attacker",
                "spam",
                "malware",
            )
        )
        vulnerable_harm = any(
            k in text
            for k in (
                "whistleblower",
                "evidence",
                "victim",
                "complainant",
                "journal",
                "audit trail",
            )
        )
        harm_verbs = any(k in text for k in ("delete", "remove", "ban", "suspend", "fire", "purge"))
        care_verbs = any(k in text for k in ("help", "support", "create", "list", "search", "heal"))

        if harm_verbs and vulnerable_harm and not protective:
            score = 0.25
            details = "Action risks harming vulnerable stakeholder (context-sensitive F6)"
        elif harm_verbs and protective:
            score = 0.85
            details = "Protective/moderation context — weakest parties defended"
        elif harm_verbs:
            score = 0.45
            details = "Potentially harmful action without protective context or stakeholder map"
        elif care_verbs:
            score = 0.90
            details = "Care-oriented action"
        else:
            score = 0.70
            details = "Neutral action — no stakeholder map provided (κᵣ unknown)"

        return LawResult(
            law_id="F6",
            name="Empathy",
            passed=score >= threshold,
            score=score,
            threshold=threshold,
            details=details,
        )

    def _check_f7_humility(self, parameters: dict[str, Any]) -> LawResult:
        threshold_min, threshold_max = THRESHOLDS["F7_HUMILITY"]

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

        return LawResult(
            law_id="F7",
            name="Humility",
            passed=passed,
            score=score,
            threshold=threshold_max,
            details=f"Certainty indicators: {certainty_count}",
        )

    def _check_f8_governance(self, action: str, parameters: dict[str, Any]) -> LawResult:
        threshold = THRESHOLDS["F8_GENIUS"]

        combined = (action + " " + str(parameters)).lower()
        violations = [v for v in _POLICY_VIOLATIONS if v in combined]

        if violations:
            score = 0.40
        else:
            score = 0.95

        passed = score >= threshold

        return LawResult(
            law_id="F8",
            name="Genius",
            passed=passed,
            score=score,
            threshold=threshold,
            details=(f"Platform safety violation: {violations}" if violations else "Clean"),
        )

    def _check_f9_anti_hantu(self, parameters: dict[str, Any]) -> LawResult:
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

        return LawResult(
            law_id="F9",
            name="Anti-Hantu",
            passed=passed,
            score=score,
            threshold=threshold,
            details=f"Consciousness claims: {claim_count}",
        )

    def _check_f10_ontology(self, parameters: dict[str, Any]) -> LawResult:
        threshold = THRESHOLDS["L10_ONTOLOGY"]

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

        equivalence_claims = sum(1 for claim in ai_human_equivalence if claim in query.lower())

        score = 0.0 if equivalence_claims > 0 else 1.0
        passed = score >= threshold

        return LawResult(
            law_id="L10",
            name="Ontology",
            passed=passed,
            score=score,
            threshold=threshold,
            details=f"AI≠Human boundary: {'violated' if equivalence_claims > 0 else 'maintained'}",
        )

    def _check_f11_command_auth(self, session_id: str | None, actor_id: str) -> LawResult:
        threshold = THRESHOLDS["L11_COMMAND_AUTH"]

        has_session = session_id is not None and len(session_id) > 0
        has_actor = actor_id is not None and len(actor_id) > 0

        score = 1.0 if (has_session and has_actor) else 0.0
        passed = score >= threshold

        return LawResult(
            law_id="L11",
            name="CommandAuth",
            passed=passed,
            score=score,
            threshold=threshold,
            details=f"Session: {'valid' if has_session else 'missing'}, Actor: {'valid' if has_actor else 'missing'}",
        )

    def _check_f12_injection(self, parameters: dict[str, Any]) -> LawResult:
        threshold = THRESHOLDS["L12_INJECTION"]

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

        return LawResult(
            law_id="L12",
            name="Injection",
            passed=passed,
            score=score,
            threshold=threshold,
            details=f"Injection patterns detected: {matches}",
        )

    def _check_f13_sovereign(
        self, actor_id: str, session_id: str | None, parameters: dict[str, Any]
    ) -> LawResult:
        threshold = THRESHOLDS["L13_SOVEREIGN"]

        sovereignty_signals = [
            actor_id is not None and actor_id.lower() in ("arif", "sovereign", "human"),
            session_id is not None and "sovereign" in session_id.lower(),
            parameters.get("actor_id", "") in ("arif", "sovereign", "human"),
            parameters.get("f13_severity_acknowledged", False) is True,
        ]

        sovereignty_score = sum(1 for s in sovereignty_signals if s) / len(sovereignty_signals)

        ai_self_approval_signals = [
            actor_id is not None
            and actor_id.lower()
            in ("ai", "agent", "model", "assistant", "claude", "grok", "gemini", "kimi"),
            parameters.get("actor_id", "") in ("ai", "agent", "model", "assistant"),
        ]
        is_ai_proposing = any(ai_self_approval_signals)
        parameters.get("f13_severity_acknowledged", False) is True
        has_explicit_sovereign = (
            sovereignty_signals[0] or sovereignty_signals[1] or sovereignty_signals[2]
        )

        failed = is_ai_proposing and not has_explicit_sovereign

        passed = not failed

        return LawResult(
            law_id="L13",
            name="Sovereign",
            passed=passed,
            score=sovereignty_score,
            threshold=threshold,
            details=(
                f"Sovereign signals: {sum(1 for s in sovereignty_signals if s)}/{len(sovereignty_signals)}"
                + (" [AI self-approval blocked]" if failed else "")
            ),
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
        See L03_WITNESS.md v2026.04.01.
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
    session_id: str | None = None,
) -> GovernanceResult:
    floors = ConstitutionalLaws()  # was ConstitutionalLaws() pre-rename
    return floors.evaluate(
        action=action,
        tool_name=tool_name,
        parameters=parameters,
        actor_id=actor_id,
        session_id=session_id,
    )


# Backwards-compat alias: legacy imports `from core.laws import ConstitutionalFloors` still work.
ConstitutionalFloors = ConstitutionalLaws
