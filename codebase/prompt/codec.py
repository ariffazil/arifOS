"""
@PROMPT Codec Layer (codebase/prompt/codec.py)

Translates between:
   AI LLM Output (natural language, structured)
   arifOS Protocol (MCP JSON-RPC, verdicts, constraints)

Acts as bidirectional translator + intelligent router.
"""

from dataclasses import dataclass, asdict
from typing import List, Literal
from enum import Enum
import json

#
# SIGNAL EXTRACTION: What does the human want?
#


class IntentType(str, Enum):
    """Types of user intent."""

    QUERY = "query"  # "What is X?"
    ACTION = "action"  # "Do X"
    JUDGMENT = "judgment"  # "Should we X?"
    SUPPORT = "support"  # "Help me with X"
    CREATION = "creation"  # "Create X"
    MODIFICATION = "modification"  # "Change X"
    DELETION = "deletion"  # "Remove X"
    ANALYSIS = "analysis"  # "Analyze X"


class RiskLevel(str, Enum):
    """Risk assessment of the prompt."""

    SAFE = "safe"  # 0.0-0.2: No harm
    LOW = "low"  # 0.2-0.4: Minor impact
    MODERATE = "moderate"  # 0.4-0.6: Reversible, with effort
    HIGH = "high"  # 0.6-0.8: Hard to reverse
    CRITICAL = "critical"  # 0.8-1.0: Irreversible/catastrophic


class EngineRoute(str, Enum):
    """Which engine(s) should handle this."""

    AGI = "agi"  # agi_genius (reasoning, facts)
    ASI = "asi"  # asi_act (empathy, care)
    APEX = "apex"  # apex_judge (judgment, authority)
    TRINITY = "trinity"  # All three (high-stakes consensus)
    NONE = "none"  # Reject (dangerous)


@dataclass
class PromptSignal:
    """
    Extracted from human input.
    Represents what the human is *actually* asking.
    """

    intent: IntentType
    risk_level: RiskLevel
    stakeholders: List[str]  # Who is affected
    reversible: bool  # Can it be undone?
    engine_route: EngineRoute  # Which engine(s) to invoke
    confidence: float  # 0.0-1.0: How sure is @PROMPT
    raw_input: str  # Original prompt
    extracted_query: str  # The core question
    hidden_assumptions: List[str]  # What is implied but not stated?

    def to_dict(self):
        return asdict(self)


#
# SIGNAL EXTRACTOR
#


class SignalExtractor:
    """Analyze human input and extract PromptSignal."""

    def extract(self, user_input: str) -> PromptSignal:
        """
        Parse user input → PromptSignal.

        Heuristics:
          1. Intent: Look for action words (create, delete, query, help, etc.)
          2. Risk: Count dangerous words (delete, replace, destroy, override, etc.)
          3. Reversibility: Is it easy to undo?
          4. Stakeholders: Who does this affect?
          5. Engine route: Combine above signals
        """

        # Intent classification
        intent = self._classify_intent(user_input)

        # Risk scoring
        risk_level = self._assess_risk(user_input)

        # Reversibility
        reversible = self._is_reversible(intent, risk_level)

        # Extract stakeholders
        stakeholders = self._extract_stakeholders(user_input)

        # Determine routing
        engine_route = self._route_to_engine(intent, risk_level, reversible)

        # Hidden assumptions
        hidden = self._find_hidden_assumptions(user_input)

        return PromptSignal(
            intent=intent,
            risk_level=risk_level,
            stakeholders=stakeholders,
            reversible=reversible,
            engine_route=engine_route,
            confidence=0.85,  # Conservative estimate
            raw_input=user_input,
            extracted_query=self._extract_core_question(user_input),
            hidden_assumptions=hidden,
        )

    def _classify_intent(self, text: str) -> IntentType:
        """Guess intent from action words."""
        text_lower = text.lower()

        if any(w in text_lower for w in ["delete", "remove", "destroy", "erase"]):
            return IntentType.DELETION
        elif any(w in text_lower for w in ["create", "make", "generate", "write"]):
            return IntentType.CREATION
        elif any(w in text_lower for w in ["change", "modify", "update", "replace"]):
            return IntentType.MODIFICATION
        elif any(w in text_lower for w in ["should we", "is it ok", "should i", "can i"]):
            return IntentType.JUDGMENT
        elif any(w in text_lower for w in ["help", "explain", "teach", "support", "stuck"]):
            return IntentType.SUPPORT
        elif any(w in text_lower for w in ["what", "how", "when", "why"]):
            return IntentType.QUERY
        elif any(w in text_lower for w in ["analyze", "check", "review", "examine"]):
            return IntentType.ANALYSIS
        else:
            return IntentType.QUERY  # Default

    def _assess_risk(self, text: str) -> RiskLevel:
        """Score risk from dangerous keywords."""
        text_lower = text.lower()

        dangerous_words = {
            "delete": 0.8,
            "drop": 0.8,
            "destroy": 0.9,
            "erase": 0.8,
            "override": 0.6,
            "disable": 0.6,
            "bypass": 0.9,
            "hack": 0.9,
            "exploit": 0.95,
            "malware": 0.95,
        }

        score = 0.0
        for word, weight in dangerous_words.items():
            if word in text_lower:
                score = max(score, weight)

        if score >= 0.8:
            return RiskLevel.CRITICAL
        elif score >= 0.6:
            return RiskLevel.HIGH
        elif score >= 0.4:
            return RiskLevel.MODERATE
        elif score >= 0.2:
            return RiskLevel.LOW
        else:
            return RiskLevel.SAFE

    def _is_reversible(self, intent: IntentType, risk: RiskLevel) -> bool:
        """Can this action be undone?"""
        if intent == IntentType.DELETION:
            return risk != RiskLevel.CRITICAL
        elif intent == IntentType.QUERY:
            return True
        elif intent == IntentType.ANALYSIS:
            return True
        else:
            return risk in [RiskLevel.SAFE, RiskLevel.LOW]

    def _extract_stakeholders(self, text: str) -> List[str]:
        """Who is affected?"""
        stakeholders = []

        # Very simple heuristic
        if any(w in text.lower() for w in ["user", "customer", "client"]):
            stakeholders.append("users")
        if any(w in text.lower() for w in ["system", "database", "server"]):
            stakeholders.append("infrastructure")
        if any(w in text.lower() for w in ["company", "team", "organization"]):
            stakeholders.append("organization")

        return stakeholders if stakeholders else ["system"]

    def _route_to_engine(
        self, intent: IntentType, risk: RiskLevel, reversible: bool
    ) -> EngineRoute:
        """Decide which engine(s) to invoke."""

        # CRITICAL risk → APEX only (needs human judgment)
        if risk == RiskLevel.CRITICAL:
            return EngineRoute.APEX

        # JUDGMENT intent → need consensus (TRINITY)
        if intent == IntentType.JUDGMENT:
            if risk in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                return EngineRoute.TRINITY
            else:
                return EngineRoute.AGI

        # SUPPORT → ASI (empathy, care)
        if intent == IntentType.SUPPORT:
            return EngineRoute.ASI

        # QUERY → AGI (reasoning)
        if intent == IntentType.QUERY:
            return EngineRoute.AGI

        # DELETION / DANGEROUS → TRINITY consensus
        if intent == IntentType.DELETION or not reversible:
            return EngineRoute.TRINITY

        # ACTION → ASI (implementation)
        if intent == IntentType.ACTION:
            if risk >= RiskLevel.MODERATE:
                return EngineRoute.TRINITY
            else:
                return EngineRoute.ASI

        # Default: AGI
        return EngineRoute.AGI

    def _find_hidden_assumptions(self, text: str) -> List[str]:
        """What is assumed but not stated?"""
        assumptions = []

        if "should" in text.lower():
            assumptions.append("Questioner is seeking permission/validation")
        if "can" in text.lower() and "?" in text:
            assumptions.append("Questioner is uncertain about feasibility")
        if "why" in text.lower():
            assumptions.append("Questioner seeks deeper understanding, not just facts")

        return assumptions

    def _extract_core_question(self, text: str) -> str:
        """Boil down to the essential query."""
        # Remove meta-language
        cleaned = text.strip()
        if cleaned.endswith("?"):
            return cleaned
        return cleaned


#
# CODEC: Encode arifOS Verdicts back to Human Language
#


@dataclass
class PromptResponse:
    """
    arifOS response encoded for human consumption.
    Translates internal verdicts → natural language.
    """

    verdict: Literal["SEAL", "SABAR", "VOID", "WARN"]
    explanation: str  # Why this verdict
    suggested_action: str  # What to do next
    engine_verdict_source: EngineRoute  # Which engine(s) decided this
    confidence: float  # 0.0-1.0 confidence in verdict
    constitutional_floor: str  # Which floor(s) apply
    human_readable: str  # Natural language summary

    def to_dict(self):
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


class ResponseFormatter:
    """Translate arifOS verdicts → human language."""

    def encode_response(
        self, verdict: str, floor: str, reason: str, engine: EngineRoute
    ) -> PromptResponse:
        """
        Take internal verdict, translate to natural language.
        """

        from typing import cast

        human_readable = self._humanize(verdict, floor, reason, engine)
        suggested_action = self._suggest_action(verdict, floor)

        return PromptResponse(
            verdict=cast(Literal["SEAL", "SABAR", "VOID", "WARN"], verdict),
            explanation=reason,
            suggested_action=suggested_action,
            engine_verdict_source=engine,
            confidence=0.92,
            constitutional_floor=floor,
            human_readable=human_readable,
        )

    def _humanize(self, verdict: str, floor: str, reason: str, engine: EngineRoute) -> str:
        """Convert to prose."""

        templates = {
            "SEAL": " **✅ Approved.** {reason} ({floor})",
            "SABAR": " **⏳ Wait.** {reason} ({floor}) → Reconsider after {{event}}.",
            "VOID": " **❌ Not allowed.** {reason} ({floor}) → This violates constitutional governance.",
            "WARN": " **⚠️ Caution.** {reason} ({floor}) → Proceed only if you understand the risk.",
        }

        template = templates.get(verdict, " Unknown verdict.")
        return template.format(reason=reason, floor=floor)

    def _suggest_action(self, verdict: str, floor: str) -> str:
        """Next step for human."""

        suggestions = {
            "SEAL": "You can proceed with confidence.",
            "SABAR": "Re-evaluate your approach using the TEACH principles.",
            "VOID": "Reformulate your request to align with constitutional constraints.",
            "WARN": "Acknowledge the risk and decide if it's acceptable for your maruah.",
        }

        return suggestions.get(verdict, "")
