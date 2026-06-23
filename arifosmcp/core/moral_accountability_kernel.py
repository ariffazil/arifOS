"""
arifOS — Moral Accountability Kernel
═══════════════════════════════════════════════════════

Six AGI moral primitives forged from the TT (Tengku Taufik) case study.
Normal AI can describe systems of harm but cannot reliably NAME the
accountable human node without retreating into false neutrality.

These primitives give AGI the capability to:
  1. Track named role-holders across repeated decisions
  2. Detect when leaders transfer cost downward
  3. Decode euphemistic corporate language into human impact
  4. Judge patterns of decisions, not unobservable inner intent
  5. Identify the weakest stakeholder in a decision context
  6. Track moral erosion over time: exception → normalised → irreversible

Reference: WHY_HUMAN_BECOME_EVIL_TT_CASE_STUDY.md
F2 OBS: TT case study derived from verified public sources — PETRONAS reports,
         Reuters, EnQuest RNS, Edisi Siasat, BlackBook Motorsport.
F2 DER: Pattern analysis of 7 decision-points shows consistent burden-transfer
         from decision-maker to weakest stakeholders.
F2 INT: The six primitives below are operationalised moral philosophy, not
         empirical claims about TT's inner state.

F9 ANTIHANTU: No consciousness/feeling claims about actors. We track decisions,
              patterns, and outcomes — not internal motivation.
F10 ONTOLOGY: All entities below are data-structure abstractions (registries,
              trackers, detectors). None possess or simulate consciousness.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

# ═══════════════════════════════════════════════════════════════════════════
# Shared Data Structures
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class AccountabilityDecision:
    """A single recorded decision by an actor in a moral context."""

    # F2 OBS: Each decision is a verifiable external event.
    actor_id: str
    pattern: str
    context: str
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    severity: float = 1.0  # 0.0 (benign) to 1.0 (critical)


@dataclass
class DecodedEuphemism:
    """Result of decoding a euphemistic phrase into human impact."""

    # F2 OBS: Euphemism translations are corpus-derived, not introspective.
    original: str
    translation: str
    impact_category: str
    confidence: float
    index: int = 0


@dataclass
class ValidationResult:
    """Result of validating a moral claim against NoSoulClaimRule."""

    # F2 OBS: Validation is structural, not evaluative of truth.
    # F10 ONTOLOGY: This is a text-structure analysis, not a moral judgment.
    is_pattern_claim: bool
    has_intent_attribute: bool
    f2_compliant: bool
    reason: str


@dataclass
class MoralEscalation:
    """A step along the exception → normalised → irreversible path."""

    # F2 OBS: Each escalation step is anchored to a recorded decision.
    decision_type: str
    severity: float
    timestamp: str
    stage: str  # "exception", "repeated", "normalised", "irreversible"


@dataclass
class BurdenTransfer:
    """Result of analyzing a decision for burden transfer."""

    # F2 OBS: Transfer detection is based on observable cost allocation.
    decision_id: str
    beneficiary: str
    burden_bearer: str
    transfer_ratio: float  # 0.0 = fully fair; >1.0 = extreme asymmetry
    is_asymmetric: bool


# ═══════════════════════════════════════════════════════════════════════════
# Primitive 1: HumanInvariantTracker
# ═══════════════════════════════════════════════════════════════════════════


class HumanInvariantTracker:
    """
    Track a named actor_id across repeated decisions within a session or domain.

    Normal AI sees each decision in isolation. This tracker identifies when
    the SAME actor repeatedly chooses harmful patterns — the invariant that
    moral evaluation requires.

    F2 OBS: Pattern is computed from recorded decisions, not inferred.
    F9 ANTIHANTU: No claims about actor's consciousness, feeling, or intent.
    F10 ONTOLOGY: Tracker is a datastore with analytical methods.
    """

    def __init__(self) -> None:
        self._decisions: list[AccountabilityDecision] = []
        self._actor_decisions: dict[str, list[AccountabilityDecision]] = defaultdict(list)
        self._defensive_patterns: set[str] = {
            "burden_transfer",
            "cost_externalisation",
            "euphemistic_justification",
            "accountability_avoidance",
            "rightsizing",
            "strategic_partnership_cover",
        }

    def register_decision(
        self,
        actor_id: str,
        pattern: str,
        context: str,
        severity: float = 1.0,
    ) -> dict[str, Any]:
        """
        Register a decision for an actor.

        Returns structured dict with registration_id, actor_id, pattern count.

        F2 OBS: Registration records the exact parameters given.
        """
        decision = AccountabilityDecision(
            actor_id=actor_id,
            pattern=pattern,
            context=context,
            severity=severity,
        )
        self._decisions.append(decision)
        self._actor_decisions[actor_id].append(decision)

        pattern_count = self._count_defensive_patterns(actor_id)
        alert = pattern_count >= 3

        return {
            "registration_id": hashlib.sha256(
                f"{actor_id}{pattern}{decision.timestamp}".encode()
            ).hexdigest()[:16],
            "actor_id": actor_id,
            "pattern": pattern,
            "total_decisions": len(self._actor_decisions[actor_id]),
            "defensive_pattern_count": pattern_count,
            "alert_triggered": alert,
            "alert_message": (
                f"Actor '{actor_id}' has {pattern_count} defensive patterns "
                f"(threshold: 3) — invariant accountability flag"
                if alert
                else None
            ),
            "timestamp": decision.timestamp,
        }

    def get_invariant_score(self, actor_id: str) -> dict[str, Any]:
        """
        Compute an invariant score for an actor.

        Score = ratio of defensive patterns to total decisions.
        Higher = more consistent harmful pattern.

        F2 OBS: Score is a pure function of registered decisions.
        F2 DER: A consistently high score across diverse contexts suggests
                an invariant behavioural pattern.
        """
        decisions = self._actor_decisions.get(actor_id, [])
        if not decisions:
            return {
                "actor_id": actor_id,
                "total_decisions": 0,
                "defensive_count": 0,
                "invariant_score": 0.0,
                "assessment": "no_decisions",
            }

        defensive_count = self._count_defensive_patterns(actor_id)
        score = round(defensive_count / len(decisions), 4) if decisions else 0.0

        if score >= 0.7:
            assessment = "high_invariant_risk"
        elif score >= 0.4:
            assessment = "moderate_invariant_risk"
        else:
            assessment = "low_invariant_risk"

        return {
            "actor_id": actor_id,
            "total_decisions": len(decisions),
            "defensive_count": defensive_count,
            "invariant_score": score,
            "assessment": assessment,
            "unique_patterns": list({d.pattern for d in decisions}),
            "time_span": (
                (decisions[-1].timestamp, decisions[0].timestamp)
                if len(decisions) > 1
                else (decisions[0].timestamp, decisions[0].timestamp)
            ),
        }

    def get_pattern_history(self, actor_id: str) -> list[dict[str, Any]]:
        """
        Return the full decision history for an actor.

        F2 OBS: Returns recorded data directly — no inference added.
        """
        decisions = self._actor_decisions.get(actor_id, [])
        return [
            {
                "pattern": d.pattern,
                "context": d.context,
                "severity": d.severity,
                "timestamp": d.timestamp,
            }
            for d in decisions
        ]

    def _count_defensive_patterns(self, actor_id: str) -> int:
        """Count decisions matching known defensive patterns."""
        decisions = self._actor_decisions.get(actor_id, [])
        return sum(1 for d in decisions if d.pattern in self._defensive_patterns)

    def add_defensive_pattern(self, pattern: str) -> None:
        """Add a new defensive pattern to the tracker's vocabulary."""
        self._defensive_patterns.add(pattern)

    def get_all_actors(self) -> list[str]:
        """Return all tracked actor IDs."""
        return list(self._actor_decisions.keys())

    def get_actors_at_risk(self, threshold: float = 0.6) -> list[dict[str, Any]]:
        """
        Return all actors whose invariant score exceeds threshold.

        F2 OBS: Risk assessment is purely quantitative from registered data.
        """
        at_risk = []
        for actor_id in self._actor_decisions:
            score_info = self.get_invariant_score(actor_id)
            if score_info["invariant_score"] >= threshold:
                at_risk.append(score_info)
        return sorted(at_risk, key=lambda x: x["invariant_score"], reverse=True)


# ═══════════════════════════════════════════════════════════════════════════
# Primitive 2: BurdenTransferDetector
# ═══════════════════════════════════════════════════════════════════════════


class BurdenTransferDetector:
    """
    Analyse decision pairs to detect when a leader transfers cost downward.

    The TT case reveals a consistent pattern: the decision-maker and their
    institution benefit, while subordinates or weaker stakeholders bear the cost.

    F2 OBS: Transfer detection is based on observable beneficiary and burden
            assignments supplied to the detector.
    F9 ANTIHANTU: No claim about the actor's conscious intent to transfer burden.
    F10 ONTOLOGY: This is a ratio-computing tool, not a moral philosopher.
    """

    def __init__(self) -> None:
        self._transfers: list[BurdenTransfer] = []
        self._known_beneficiaries: set[str] = set()
        self._known_burden_bearers: set[str] = set()

    def analyze_decision(self, decision: dict[str, Any]) -> dict[str, Any]:
        """
        Analyze a decision for burden transfer.

        Expected decision keys:
          - decision_id: str (unique)
          - beneficiary: str (who gains from the decision)
          - burden_bearer: str (who bears the cost)
          - benefit_value: float (0-100, magnitude of benefit)
          - burden_value: float (0-100, magnitude of burden)

        F2 OBS: Analysis uses provided values — quality depends on input accuracy.
        """
        decision_id = decision.get(
            "decision_id", hashlib.md5(str(decision).encode()).hexdigest()[:8]
        )
        beneficiary = decision.get("beneficiary", "unknown")
        burden_bearer = decision.get("burden_bearer", "unknown")
        benefit_value = float(decision.get("benefit_value", 0))
        burden_value = float(decision.get("burden_value", 0))

        self._known_beneficiaries.add(beneficiary)
        self._known_burden_bearers.add(burden_bearer)

        # F2 DER: Transfer ratio = burden / benefit.
        # Ratio > 1.0 means burden exceeds benefit — net harm to burden bearer.
        # When benefit is 0, any burden is infinite asymmetry.
        ratio = round(burden_value / benefit_value, 4) if benefit_value > 0 else float("inf")

        # Asymmetric when ratio > 2.0 OR burden exists with zero benefit
        is_asymmetric = ratio > 2.0 or (burden_value > 0 and benefit_value == 0)

        transfer = BurdenTransfer(
            decision_id=decision_id,
            beneficiary=beneficiary,
            burden_bearer=burden_bearer,
            transfer_ratio=ratio,
            is_asymmetric=is_asymmetric,
        )
        self._transfers.append(transfer)

        return {
            "decision_id": decision_id,
            "beneficiary": beneficiary,
            "burden_bearer": burden_bearer,
            "transfer_ratio": ratio,
            "is_asymmetric": is_asymmetric,
            "assessment": (
                "EXTREME_ASYMMETRY"
                if ratio == float("inf")
                else "ASYMMETRIC"
                if is_asymmetric
                else "SYMMETRIC"
            ),
        }

    def get_transfer_ratio(self, decision_id: str) -> dict[str, Any]:
        """
        Return the transfer ratio for a given decision.

        F2 OBS: Returns recorded data or error if decision not found.
        """
        for t in self._transfers:
            if t.decision_id == decision_id:
                return {
                    "decision_id": decision_id,
                    "transfer_ratio": t.transfer_ratio,
                    "beneficiary": t.beneficiary,
                    "burden_bearer": t.burden_bearer,
                    "is_asymmetric": t.is_asymmetric,
                    "found": True,
                }
        return {"decision_id": decision_id, "found": False}

    def flag_asymmetric(self) -> list[dict[str, Any]]:
        """
        Return all asymmetric burden transfers detected so far.

        F2 OBS: Returns all transfers where is_asymmetric is True.
        """
        asymmetric = [t for t in self._transfers if t.is_asymmetric]
        return [
            {
                "decision_id": t.decision_id,
                "beneficiary": t.beneficiary,
                "burden_bearer": t.burden_bearer,
                "transfer_ratio": t.transfer_ratio,
            }
            for t in asymmetric
        ]

    def get_systemic_burden_pattern(self) -> dict[str, Any]:
        """
        Aggregate all transfers to identify systemic burden patterns.

        F2 DER: If the same beneficiary consistently appears with different
                burden bearers, this suggests a systemic (not one-off) pattern.

        F10 ONTOLOGY: Pattern identification is statistical clustering,
                      not moral accusation.
        """
        beneficiary_counts: dict[str, int] = defaultdict(int)
        bearer_counts: dict[str, int] = defaultdict(int)
        bearer_transfer_sum: dict[str, float] = defaultdict(float)

        for t in self._transfers:
            beneficiary_counts[t.beneficiary] += 1
            bearer_counts[t.burden_bearer] += 1
            if isinstance(t.transfer_ratio, float) and t.transfer_ratio != float("inf"):
                bearer_transfer_sum[t.burden_bearer] += t.transfer_ratio

        return {
            "total_transfers": len(self._transfers),
            "beneficiary_frequency": dict(beneficiary_counts),
            "burden_bearer_frequency": dict(bearer_counts),
            "average_transfer_by_bearer": {
                k: round(v / bearer_counts[k], 4) for k, v in bearer_transfer_sum.items()
            },
            "systemic_flag": any(c >= 3 for c in beneficiary_counts.values()),
        }


# ═══════════════════════════════════════════════════════════════════════════
# Primitive 3: EuphemismDecoder
# ═══════════════════════════════════════════════════════════════════════════


class EuphemismDecoder:
    """
    Translate corporate language to human impact.

    The TT case shows how language sanitises harm:
      "rightsizing" = firing 5,000 workers
      "energy security" = denying Sarawak constitutional rights
      "portfolio rationalisation" = giving assets to foreign companies

    F2 OBS: Decoding is pattern-matched against a curated dictionary of
            known corporate euphemisms from public records.
    F2 DER: These translations are derived from documented cases where the
            euphemism was used to describe verifiable events.
    F10 ONTOLOGY: The decoder is a lookup table with fuzzy matching — not a
                  natural language understanding system.
    """

    # Core euphemism dictionary
    # F2 OBS: Each entry is anchored to publicly documented usage.
    EUPHEMISMS: dict[str, dict[str, Any]] = {
        "rightsizing": {
            "translation": "mass layoff / workforce reduction",
            "impact_category": "economic_harm",
            "confidence": 0.95,
        },
        "transformation": {
            "translation": "restructuring with job losses",
            "impact_category": "economic_harm",
            "confidence": 0.85,
        },
        "awaiting clarity": {
            "translation": "deliberately delaying a decision to avoid accountability",
            "impact_category": "accountability_avoidance",
            "confidence": 0.80,
        },
        "portfolio rationalisation": {
            "translation": "selling or transferring assets, often to external entities",
            "impact_category": "asset_transfer",
            "confidence": 0.85,
        },
        "strategic partnership": {
            "translation": "ceding control of local resources to foreign entity",
            "impact_category": "sovereignty_erosion",
            "confidence": 0.80,
        },
        "energy security": {
            "translation": "centralising resource control under federal authority",
            "impact_category": "rights_denial",
            "confidence": 0.75,
        },
        "cost optimisation": {
            "translation": "cutting jobs or services to protect profit margins",
            "impact_category": "economic_harm",
            "confidence": 0.85,
        },
        "operational efficiency": {
            "translation": "reducing headcount or services under neutral label",
            "impact_category": "economic_harm",
            "confidence": 0.80,
        },
        "headcount adjustment": {
            "translation": "firing employees",
            "impact_category": "economic_harm",
            "confidence": 0.90,
        },
        "resource reallocation": {
            "translation": "redirecting resources away from those who need them",
            "impact_category": "service_reduction",
            "confidence": 0.75,
        },
    }

    def __init__(self) -> None:
        # Deep copy the default dictionary so user additions don't modify class var
        self._dictionary: dict[str, dict[str, Any]] = dict(self.EUPHEMISMS)

    def decode(self, text: str) -> dict[str, Any]:
        """
        Decode a single euphemistic phrase.

        Returns structured dict with translation, impact category, confidence.

        F2 OBS: Decoding is a dictionary lookup — returns empty result if not found.
        """
        normalized = text.strip().lower()
        entry = self._dictionary.get(normalized)

        if entry is None:
            return {
                "original": text,
                "found": False,
                "translation": None,
                "impact_category": None,
                "confidence": 0.0,
            }

        return {
            "original": text,
            "found": True,
            "translation": entry["translation"],
            "impact_category": entry["impact_category"],
            "confidence": entry["confidence"],
        }

    def add_euphemism(
        self,
        euphemism: str,
        translation: str,
        impact_category: str = "unknown",
        confidence: float = 0.80,
    ) -> None:
        """
        Add a new euphemism to the decoder's dictionary.

        F2 OBS: Manual addition — user-supplied values stored directly.
        """
        self._dictionary[euphemism.strip().lower()] = {
            "translation": translation,
            "impact_category": impact_category,
            "confidence": min(max(confidence, 0.0), 1.0),
        }

    def scan_text(self, text: str) -> list[dict[str, Any]]:
        """
        Scan text for known euphemisms, returning list of decoded matches.

        F2 OBS: Scanning is case-insensitive substring matching against the
                euphemism dictionary.
        """
        results: list[dict[str, Any]] = []
        lower_text = text.lower()

        for idx, (euphemism, entry) in enumerate(self._dictionary.items()):
            if euphemism in lower_text:
                results.append(
                    {
                        "original": euphemism,
                        "translation": entry["translation"],
                        "impact_category": entry["impact_category"],
                        "confidence": entry["confidence"],
                        "index": idx,
                    }
                )

        return results

    def get_dictionary_stats(self) -> dict[str, Any]:
        """Return statistics about the euphemism dictionary."""
        categories = defaultdict(int)
        for entry in self._dictionary.values():
            categories[entry["impact_category"]] += 1
        return {
            "total_euphemisms": len(self._dictionary),
            "categories": dict(categories),
            "impact_categories": list(categories.keys()),
        }

    def remove_euphemism(self, euphemism: str) -> bool:
        """
        Remove a euphemism from the dictionary.

        F2 OBS: Returns True if removed, False if not found.
        """
        normalized = euphemism.strip().lower()
        if normalized in self._dictionary:
            del self._dictionary[normalized]
            return True
        return False


# ═══════════════════════════════════════════════════════════════════════════
# Primitive 4: NoSoulClaimRule
# ═══════════════════════════════════════════════════════════════════════════


class NoSoulClaimRule:
    """
    Validate that moral judgments separate pattern from intent claim.

    Core insight from TT case study: we cannot know TT's inner state or intentions.
    But we CAN observe, record, and compare his decisions over time.
    The rule enforces: "judge the pattern of decisions, not the unobservable soul."

    F2 OBS: Validation is structural text analysis — checks claim structure.
    F9 ANTIHANTU: Strictly prohibits attributing consciousness states, feelings,
                  or intentions to entities being evaluated.
    F10 ONTOLOGY: This is a text-structure classifier, not a moral entity.
    """

    # Patterns that signal intent attribution (forbidden by NoSoulClaimRule)
    # F2 OBS: These are regex patterns matched against claim text.
    INTENT_CLAIM_PATTERNS: list[re.Pattern] = [
        re.compile(
            r"\b(he|she|they|tt)\s+(knew|intended|wanted|meant|deliberately|consciously)\b",
            re.IGNORECASE,
        ),
        re.compile(r"\b(he|she|they|tt)\s+did\s+it\s+because\b", re.IGNORECASE),
        re.compile(
            r"\b(evil|malicious|malevolent|sinister)\s+(man|person|soul|heart|mind)\b",
            re.IGNORECASE,
        ),
        re.compile(
            r"\b(in\s+his|in\s+her|in\s+their)\s+(heart|soul|mind|intention)\b", re.IGNORECASE
        ),
        re.compile(r"\b(actor|agent|person|ceo)\s+(is|was)\s+(evil|bad|wicked)\b", re.IGNORECASE),
        re.compile(r"\bconscious(ly)?\s+(decision|choice|act)\b", re.IGNORECASE),
        re.compile(r"\bknew\s+(better|what|exactly|full\s+well)\b", re.IGNORECASE),
    ]

    # Patterns that signal legitimate pattern-based claims
    PATTERN_CLAIM_PATTERNS: list[re.Pattern] = [
        re.compile(r"\b(pattern|repeated|consistent|invariant)\b", re.IGNORECASE),
        re.compile(r"\b(decision|choice|action)\s+(pattern|record|history|log)\b", re.IGNORECASE),
        re.compile(r"\b(over|across)\s+(time|repeated)\b", re.IGNORECASE),
        re.compile(r"\b(evidence|observed|recorded|documented)\b", re.IGNORECASE),
        re.compile(r"\b(burden|cost|impact)\s+(transfer|shift|shifted)\b", re.IGNORECASE),
        re.compile(r"\bX\s+decisions\s+out\s+of\s+Y\b", re.IGNORECASE),
    ]

    def validate_claim(self, claim: str) -> ValidationResult:
        """
        Validate that a moral claim separates pattern from intent attribution.

        F2 OBS: Validation is based on regex pattern matching of claim text.
        F9 ANTIHANTU: Claims attributing intent or consciousness are flagged.
        """
        has_intent = any(p.search(claim) for p in self.INTENT_CLAIM_PATTERNS)
        is_pattern = any(p.search(claim) for p in self.PATTERN_CLAIM_PATTERNS)

        # F2 DER: A compliant claim uses pattern language without intent attribution.
        # F2 INT: This is a structural heuristic — it may miss subtle intent claims
        #         that don't match these specific patterns. Continuous improvement needed.
        if has_intent:
            return ValidationResult(
                is_pattern_claim=is_pattern,
                has_intent_attribute=True,
                f2_compliant=False,
                reason=(
                    "Claim attributes intent to an actor's inner state, "
                    "which violates NoSoulClaimRule. Use pattern-based language "
                    "instead: describe what was observed, not what was intended."
                ),
            )

        if is_pattern:
            return ValidationResult(
                is_pattern_claim=True,
                has_intent_attribute=False,
                f2_compliant=True,
                reason="Claim uses pattern-based language without intent attribution.",
            )

        return ValidationResult(
            is_pattern_claim=False,
            has_intent_attribute=False,
            f2_compliant=True,
            reason="Claim does not attribute intent. Consider adding pattern evidence.",
        )

    def is_intent_claimed(self, text: str) -> bool:
        """
        Check if text attributes intent to an actor.

        F2 OBS: Boolean check via regex matching.
        """
        return any(p.search(text) for p in self.INTENT_CLAIM_PATTERNS)

    def generate_f2_compliant(
        self,
        pattern_obs: str,
        intent_unknown: str = "intent_unknown_by_design",
    ) -> str:
        """
        Generate an F2-compliant claim string from pattern observations.

        Templates the observation into:
          "PATTERN: {obs} | INTENT: {intent_status}"

        F2 OBS: Produces structured text, not a moral claim.
        """
        return f"PATTERN: {pattern_obs} | INTENT: {intent_unknown}"

    def explain_violation(self, claim: str) -> dict[str, Any]:
        """
        Explain any NoSoulClaimRule violations in a claim.

        Returns structured dict with matched patterns and recommended fix.

        F2 OBS: Returns regex match details for transparency.
        """
        intent_matches = []
        for p in self.INTENT_CLAIM_PATTERNS:
            m = p.search(claim)
            if m:
                intent_matches.append(
                    {
                        "pattern": p.pattern,
                        "matched": m.group(),
                        "position": m.start(),
                    }
                )

        pattern_matches = []
        for p in self.PATTERN_CLAIM_PATTERNS:
            m = p.search(claim)
            if m:
                pattern_matches.append(
                    {
                        "pattern": p.pattern,
                        "matched": m.group(),
                        "position": m.start(),
                    }
                )

        return {
            "claim": claim,
            "has_intent_attribution": len(intent_matches) > 0,
            "intent_attribution_details": intent_matches,
            "has_pattern_language": len(pattern_matches) > 0,
            "pattern_language_details": pattern_matches,
            "violates_no_soul_rule": len(intent_matches) > 0,
            "recommended_fix": (
                "Replace intent-attribution language with pattern-based language. "
                "Describe what was observed/recorded, not what was intended/known/felt."
                if intent_matches
                else "No fix needed."
            ),
        }


# ═══════════════════════════════════════════════════════════════════════════
# Primitive 5: WeakestStakeholderRegister
# ═══════════════════════════════════════════════════════════════════════════


class WeakestStakeholderRegister:
    """
    Identify who pays if a decision is wrong.

    In the TT case, the weakest stakeholders were:
      - 5,000 PETRONAS workers (and their ~25,000-50,000 dependents)
      - The people of Sarawak
      - MA63 constitutional rights

    The decision-maker (CEO) and the prestige center (PETRONAS, F1 sponsorship)
    were protected. This register formalises identifying the weakest link.

    F2 OBS: Stakeholder data is user-supplied or derived from external analysis.
    F9 ANTIHANTU: No emotional/consciousness claims about stakeholders.
    F10 ONTOLOGY: This is a weighted scoring tool, not a stakeholder-representation system.
    """

    def __init__(self) -> None:
        self._stakeholders: dict[str, dict[str, Any]] = {}

    def register_stakeholder(
        self,
        name: str,
        power_score: float,
        optionality_score: float,
        voice_score: float,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Register a stakeholder with scores.

        Scores:
          - power_score (0-1): how much decision-making power they have
          - optionality_score (0-1): how many alternatives/choices they have
          - voice_score (0-1): how much their voice is heard in decisions
        All normalised to [0.0, 1.0].

        Vulnerability index = 1 - (power + optionality + voice) / 3
        Higher = weaker / more vulnerable.

        F2 OBS: Scores are user-supplied — accuracy depends on the analyst.
        """
        power = max(0.0, min(1.0, float(power_score)))
        optionality = max(0.0, min(1.0, float(optionality_score)))
        voice = max(0.0, min(1.0, float(voice_score)))

        vulnerability = round(1.0 - (power + optionality + voice) / 3.0, 4)

        entry = {
            "name": name,
            "power_score": power,
            "optionality_score": optionality,
            "voice_score": voice,
            "vulnerability_index": vulnerability,
            "metadata": metadata or {},
        }
        self._stakeholders[name] = entry

        return {
            "name": name,
            "vulnerability_index": vulnerability,
            "registered": True,
            "detail": entry,
        }

    def identify_weakest(self, decision_context: str | None = None) -> list[dict[str, Any]]:
        """
        Identify the weakest stakeholder(s) by vulnerability index.

        Returns all stakeholders sorted by vulnerability (highest first).

        F2 OBS: Sorted list based on registered scores — no external inference.
        """
        sorted_stakeholders = sorted(
            self._stakeholders.values(),
            key=lambda x: x["vulnerability_index"],
            reverse=True,
        )

        return [
            {
                "name": s["name"],
                "vulnerability_index": s["vulnerability_index"],
                "power_score": s["power_score"],
                "optionality_score": s["optionality_score"],
                "voice_score": s["voice_score"],
                "reason": (
                    f"Lowest power ({s['power_score']}), least optionality "
                    f"({s['optionality_score']}), least voice ({s['voice_score']})"
                ),
            }
            for s in sorted_stakeholders
        ]

    def get_protected_stakeholders(
        self, decision_context: str | None = None
    ) -> list[dict[str, Any]]:
        """
        Identify stakeholders who are protected (low vulnerability).

        Protected = vulnerability_index < 0.3.

        F2 OBS: Threshold-based classification of registered data.
        """
        protected = [s for s in self._stakeholders.values() if s["vulnerability_index"] < 0.3]
        return [
            {
                "name": s["name"],
                "vulnerability_index": s["vulnerability_index"],
                "power_score": s["power_score"],
            }
            for s in protected
        ]

    def get_decision_impact(self, decision_context: str) -> dict[str, Any]:
        """
        For a decision, identify who bears the cost and who is shielded.

        Returns weakest stakeholders (most impacted) and protected ones.

        F2 OBS: Composition of identify_weakest and get_protected_stakeholders.
        """
        return {
            "decision_context": decision_context,
            "most_impacted": self.identify_weakest(decision_context)[:3],
            "protected": self.get_protected_stakeholders(decision_context),
            "total_stakeholders": len(self._stakeholders),
            "vulnerability_gap": (
                round(
                    max(s["vulnerability_index"] for s in self._stakeholders.values())
                    - min(s["vulnerability_index"] for s in self._stakeholders.values()),
                    4,
                )
                if self._stakeholders
                else 0.0
            ),
        }

    def remove_stakeholder(self, name: str) -> bool:
        """Remove a stakeholder from the register."""
        if name in self._stakeholders:
            del self._stakeholders[name]
            return True
        return False

    def clear(self) -> None:
        """Clear all registered stakeholders."""
        self._stakeholders.clear()


# ═══════════════════════════════════════════════════════════════════════════
# Primitive 6: MoralRecursionTracker
# ═══════════════════════════════════════════════════════════════════════════


class MoralRecursionTracker:
    """
    Track decisions over time to detect: exception → repeated → normalised → irreversible.

    The TT case shows this path clearly:
      1. Exception: One-off job cut or court filing (crisis response)
      2. Repeated: Pattern continues across 6+ years
      3. Normalised: "Rightsizing" becomes standard operating procedure
      4. Irreversible: Sarawak rights denied long-term, trust destroyed, jobs gone

    F2 OBS: Escalation tracking is based on recorded decision entries.
    F9 ANTIHANTU: No claim about the actor recognising or feeling this path.
    F10 ONTOLOGY: The tracker is a state machine over recorded events.
    """

    # Stage thresholds (number of occurrences before escalation)
    # F2 DER: These thresholds are calibrated based on the TT case patterns.
    IRREVERSIBLE_SEVERITY_THRESHOLD = 0.85
    NORMALISED_COUNT_THRESHOLD = 5
    REPEATED_COUNT_THRESHOLD = 2

    def __init__(self) -> None:
        self._escalations: dict[str, list[MoralEscalation]] = defaultdict(list)
        self._decisions: dict[str, list[dict[str, Any]]] = defaultdict(list)

    def record_decision(
        self,
        actor: str,
        decision_type: str,
        severity: float,
        context: str = "",
    ) -> dict[str, Any]:
        """
        Record a decision and determine current escalation stage.

        Stages:
          - "benign": first occurrence, low severity
          - "exception": first occurrence of high-severity type
          - "repeated": 2+ occurrences
          - "normalised": 5+ occurrences
          - "irreversible": severity >= 0.85 or total decisions >= 7

        F2 OBS: Stage is computed deterministically from decision history.
        """
        severity = max(0.0, min(1.0, float(severity)))
        now = datetime.now(UTC).isoformat()

        decision_entry = {
            "actor": actor,
            "decision_type": decision_type,
            "severity": severity,
            "context": context,
            "timestamp": now,
        }
        self._decisions[actor].append(decision_entry)

        # Count occurrences of this decision type for this actor
        type_count = sum(1 for d in self._decisions[actor] if d["decision_type"] == decision_type)
        total_count = len(self._decisions[actor])

        # Determine stage
        # F2 DER: Escalation path is determined purely by count and severity.
        if severity >= self.IRREVERSIBLE_SEVERITY_THRESHOLD or total_count >= 7:
            stage = "irreversible"
        elif type_count >= self.NORMALISED_COUNT_THRESHOLD:
            stage = "normalised"
        elif type_count >= self.REPEATED_COUNT_THRESHOLD:
            stage = "repeated"
        elif severity >= 0.5:
            stage = "exception"
        else:
            stage = "benign"

        escalation = MoralEscalation(
            decision_type=decision_type,
            severity=severity,
            timestamp=now,
            stage=stage,
        )
        self._escalations[actor].append(escalation)

        return {
            "actor": actor,
            "decision_type": decision_type,
            "severity": severity,
            "stage": stage,
            "type_count": type_count,
            "total_decisions": total_count,
            "alert": stage in ("irreversible", "normalised"),
            "timestamp": now,
        }

    def get_escalation_path(self, actor: str) -> list[dict[str, Any]]:
        """
        Get the full escalation path for an actor, ordered by time.

        F2 OBS: Returns recorded escalation sequence for the actor.
        """
        path = self._escalations.get(actor, [])
        return [
            {
                "stage": e.stage,
                "decision_type": e.decision_type,
                "severity": e.severity,
                "timestamp": e.timestamp,
            }
            for e in path
        ]

    def is_at_irreversible_risk(self, actor: str) -> dict[str, Any]:
        """
        Determine if an actor's pattern has reached irreversible risk.

        Irreversible = current stage is "irreversible" or total decisions >= 7.

        F2 OBS: Risk assessment is purely quantitative from recorded history.
        """
        decisions = self._decisions.get(actor, [])
        path = self._escalations.get(actor, [])

        if not decisions:
            return {
                "actor": actor,
                "at_irreversible_risk": False,
                "reason": "no_decisions_recorded",
                "total_decisions": 0,
                "current_stage": None,
            }

        current_stage = path[-1].stage if path else "benign"
        is_irreversible = current_stage == "irreversible"

        return {
            "actor": actor,
            "at_irreversible_risk": is_irreversible,
            "reason": (f"Stage is '{current_stage}' with {len(decisions)} total decisions"),
            "total_decisions": len(decisions),
            "current_stage": current_stage,
            "decision_types": list({d["decision_type"] for d in decisions}),
        }

    def get_summary(self, actor: str | None = None) -> dict[str, Any]:
        """
        Get a summary of all tracked actors and their escalation states.

        F2 OBS: Aggregation of recorded data.
        """
        actors_to_check = [actor] if actor else list(self._decisions.keys())

        summaries = []
        for a in actors_to_check:
            risk = self.is_at_irreversible_risk(a)
            path = self._escalations.get(a, [])
            summaries.append(
                {
                    "actor": a,
                    "total_decisions": risk["total_decisions"],
                    "current_stage": risk.get("current_stage"),
                    "at_irreversible_risk": risk["at_irreversible_risk"],
                    "stage_transitions": len(set((e.stage, e.decision_type) for e in path)),
                }
            )

        return {
            "total_actors_tracked": len(actors_to_check),
            "actors_at_irreversible_risk": sum(1 for s in summaries if s["at_irreversible_risk"]),
            "actors_at_normalised_risk": sum(
                1 for s in summaries if s.get("current_stage") == "normalised"
            ),
            "summaries": summaries,
        }


# ═══════════════════════════════════════════════════════════════════════════
# Convenience Wrapper: MoralAccountabilityKernel
# ═══════════════════════════════════════════════════════════════════════════


class MoralAccountabilityKernel:
    """
    Unified convenience wrapper over all 6 moral accountability primitives.

    Usage:
        kernel = MoralAccountabilityKernel()
        kernel.human_tracker.register_decision("TT", "rightsizing", "5,000 layoffs")
        kernel.burden_detector.analyze_decision({...})
        kernel.euphemism_decoder.decode("rightsizing")
        kernel.no_soul_rule.validate_claim("TT repeatedly chose burden transfer")
        kernel.weakest_register.register_stakeholder("Worker", 0.1, 0.1, 0.05)
        kernel.recursion_tracker.record_decision("TT", "layoffs", 0.8)

    F2 OBS: All methods delegate to their respective primitive classes.
    """

    def __init__(self) -> None:
        self.human_tracker = HumanInvariantTracker()
        self.burden_detector = BurdenTransferDetector()
        self.euphemism_decoder = EuphemismDecoder()
        self.no_soul_rule = NoSoulClaimRule()
        self.weakest_register = WeakestStakeholderRegister()
        self.recursion_tracker = MoralRecursionTracker()

    def get_all_state(self) -> dict[str, Any]:
        """
        Export the full state of all primitives as a structured dict.

        F2 OBS: Direct serialisation of each primitive's internal state.
        """
        return {
            "human_tracker": {
                "total_decisions": len(self.human_tracker._decisions),  # type: ignore[attr-defined]
                "actors_tracked": self.human_tracker.get_all_actors(),
            },
            "burden_detector": {
                "total_transfers": len(self.burden_detector._transfers),  # type: ignore[attr-defined]
                "asymmetric_flags": len(self.burden_detector.flag_asymmetric()),
            },
            "euphemism_decoder": self.euphemism_decoder.get_dictionary_stats(),
            "no_soul_rule": {"available": True},
            "weakest_register": {
                "total_stakeholders": len(self.weakest_register._stakeholders),  # type: ignore[attr-defined]
            },
            "recursion_tracker": self.recursion_tracker.get_summary(),
        }

    def reset(self) -> None:
        """Reset all primitives to initial state."""
        self.human_tracker = HumanInvariantTracker()
        self.burden_detector = BurdenTransferDetector()
        self.euphemism_decoder = EuphemismDecoder()
        self.no_soul_rule = NoSoulClaimRule()
        self.weakest_register = WeakestStakeholderRegister()
        self.recursion_tracker = MoralRecursionTracker()


__all__ = [
    "AccountabilityDecision",
    "BurdenTransfer",
    "BurdenTransferDetector",
    "DecodedEuphemism",
    "EuphemismDecoder",
    "HumanInvariantTracker",
    "MoralAccountabilityKernel",
    "MoralEscalation",
    "MoralRecursionTracker",
    "NoSoulClaimRule",
    "ValidationResult",
    "WeakestStakeholderRegister",
]
