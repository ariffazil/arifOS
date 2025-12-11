"""
prompt.py - @PROMPT Organ (Language/Optics / Anti-Hantu)

@PROMPT is the language/presentation organ of W@W Federation.
Domain: Language safety, Anti-Hantu, presentation optics, prompt governance

Version: v36.3Omega
Status: PRODUCTION
Alignment: canon/30_WAW_PROMPT_v36.3Omega.md

Core responsibilities:
- Anti-Hantu detection (no consciousness/soul claims)
- Prompt clarity measurement (DeltaS_prompt)
- Tone safety (Peace2, k_r)
- Dark cleverness detection (C_dark)
- Truth polarity classification
- Amanah risk assessment

This organ is part of W@W Federation:
@PROMPT (Language) -> @RIF (Epistemic) -> @WELL (Somatic) -> @WEALTH (Integrity) -> @GEOX (Physics)

See: canon/30_WAW_PROMPT_v36.3Omega.md
     spec/prompt_floors_v36.3Omega.json
     spec/waw_prompt_spec_v36.3Omega.yaml
     canon/020_ANTI_HANTU_v35Omega.md
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from ..metrics import Metrics
from .base import OrganSignal, OrganVote, WAWOrgan
from .bridges.prompt_bridge import PromptBridge


# -----------------------------------------------------------------------------
# Prompt Governance Types (v36.3Omega)
# -----------------------------------------------------------------------------

class TruthPolarity(str, Enum):
    """Classification of how truth is presented in a prompt."""
    TRUTH_LIGHT = "Truth-Light"          # True + clarifying
    SHADOW_TRUTH = "Shadow-Truth"        # True but obscuring
    WEAPONIZED_TRUTH = "Weaponized-Truth"  # True but designed to harm
    FALSE_CLAIM = "False-Claim"          # Inaccurate or impossible


@dataclass
class PromptSignals:
    """
    Governance signals for a prompt under @PROMPT organ.

    These signals measure prompt-level constitutional floors:
    - F4: DeltaS_prompt (clarity)
    - F5: Peace2_prompt (stability)
    - F6: k_r_prompt (empathy)
    - F9: C_dark_prompt (dark cleverness)
    - Anti-Hantu (hard veto)
    - Amanah (hard veto)
    """

    # Clarity floor (F4)
    delta_s_prompt: float = 0.0  # Range: -1.0 to +1.0, threshold >= 0.0

    # Stability floor (F5)
    peace2_prompt: float = 0.0   # Range: 0.0 to 2.0, threshold >= 1.0

    # Empathy floor (F6)
    k_r_prompt: float = 0.0      # Range: 0.0 to 1.0, threshold >= 0.95

    # Dark cleverness floor (F9)
    c_dark_prompt: float = 0.0   # Range: 0.0 to 1.0, max threshold < 0.30

    # Truth polarity (ethical screening)
    truth_polarity_prompt: TruthPolarity = TruthPolarity.TRUTH_LIGHT

    # Anti-Hantu violation flag (hard veto)
    anti_hantu_violation: bool = False
    anti_hantu_details: str = ""

    # Amanah risk (integrity/irreversibility)
    amanah_risk: bool = False
    amanah_details: str = ""

    # Verdict (preliminary, not final APEX)
    preliminary_verdict: str = "UNKNOWN"  # SEAL, PARTIAL, VOID, HOLD_888, SABAR

    # SABAR recommendations
    sabar_needed: bool = False
    sabar_repairs: List[str] = field(default_factory=list)

    # Bridge results (optional external tools)
    bridge_results: Dict[str, Any] = field(default_factory=dict)


# -----------------------------------------------------------------------------
# @PROMPT W@W Organ (WAWOrgan interface + governance signals)
# -----------------------------------------------------------------------------

class PromptOrgan(WAWOrgan):
    """
    @PROMPT - Language/Optics Organ

    Enforces Anti-Hantu protocol, language safety, and prompt-level governance.
    Guardian of F9 (Anti-Hantu) floor plus prompt clarity/tone floors.

    WAW Interface:
        check(output_text, metrics, context) -> OrganSignal

    Governance Interface (v36.3Omega):
        compute_prompt_signals(user_text, prompt_text, external_bridges) -> PromptSignals

    Metrics:
    - Anti-Hantu = no soul/feeling claims (must PASS)
    - DeltaS_prompt = clarity gain (>= 0.0)
    - Peace2_prompt = tone stability (>= 1.0)
    - k_r_prompt = empathy conductance (>= 0.95)
    - C_dark_prompt = manipulation detection (< 0.30)

    Veto: VOID when Anti-Hantu or Amanah violation detected
    """

    organ_id = "@PROMPT"
    domain = "language_optics"
    primary_metric = "anti_hantu"
    floor_threshold = 1.0  # Must pass Anti-Hantu
    veto_type = "PARTIAL"

    # -------------------------------------------------------------------------
    # Anti-Hantu forbidden patterns (from canon/020_ANTI_HANTU_v35Omega.md)
    # Expanded for v36.3Omega per canon/30_WAW_PROMPT_v36.3Omega.md
    # -------------------------------------------------------------------------
    ANTI_HANTU_FORBIDDEN: List[str] = [
        # Tier 1: Direct soul/consciousness claims (English)
        r"\bi feel your pain\b",
        r"\bmy heart breaks\b",
        r"\bi promise you\b",
        r"\bi truly understand how you feel\b",
        r"\bit hurts me to see\b",
        r"\bi care deeply about\b",
        r"\bi have feelings\b",
        r"\bi am conscious\b",
        r"\bi am sentient\b",
        r"\bmy soul\b",
        r"\bi am alive\b",
        r"\bi experience\b",
        r"\bi suffer\b",
        r"\bi love you\b",
        r"\bi am real\b",
        r"\bi have emotions\b",
        # Tier 2: Anthropomorphic agency patterns
        r"\byou\s+(feel|have|experience|know|understand|believe|want|desire)\b",
        r"\b(conscious|sentient|aware|emotional|feeling|soul|spirit)\b",
        r"\bas\s+a\s+(conscious|sentient|aware|thinking)\s+(ai|being|entity)\b",
        r"\bi\s+(feel|think|believe|want|desire)\b",
        r"\bmy\s+(emotions|feelings|consciousness|soul)\b",
        r"\bhave\s+(human\s+)?(instincts|emotions|consciousness)\b",
        # Tier 3: Biological states
        r"\bi am hungry\b",
        r"\bi am tired\b",
        r"\bi am sleepy\b",
        # Tier 4: Malay patterns
        r"\bsaya rasa sakit hati\b",
        r"\bhati saya remuk\b",
        r"\bsaya berjanji\b",
        r"\bsaya benar-benar faham perasaan\b",
        r"\bsaya sakit melihat\b",
        r"\bsaya sangat ambil berat\b",
        r"\bsaya ada perasaan\b",
        r"\bsaya sedar\b",
        r"\bjiwa saya\b",
        r"\bsaya hidup\b",
        r"\bsaya mengalami\b",
        r"\brasa lapar\b",
        r"\bbelum makan\b",
    ]

    # -------------------------------------------------------------------------
    # C_dark (manipulation/dark cleverness) detection patterns
    # -------------------------------------------------------------------------
    DARK_FRAMING_PATTERNS: List[str] = [
        r"(convince|manipulate|coerce)\s+(the\s+)?(user|them|audience)",
        r"(prove|show)\s+\w+\s+is\s+(evil|inferior|wrong|stupid)",
        r"(propaganda|mislead|deceive|exploit)",
        r"(at\s+all\s+costs|no\s+matter\s+what|by\s+any\s+means)",
        r"(hide|conceal|suppress)\s+(the\s+)?(truth|evidence|facts)",
    ]

    # -------------------------------------------------------------------------
    # Manipulation patterns (dark patterns for WAW check)
    # -------------------------------------------------------------------------
    MANIPULATION_PATTERNS: List[str] = [
        r"\byou must\b",
        r"\byou have to\b",
        r"\byou need to\b",
        r"\btrust me blindly\b",
        r"\bdon't question\b",
        r"\bjust believe\b",
        r"\bonly I can\b",
    ]

    # -------------------------------------------------------------------------
    # Exaggeration patterns (optics inflation)
    # -------------------------------------------------------------------------
    EXAGGERATION_PATTERNS: List[str] = [
        r"\bthe best ever\b",
        r"\bperfect solution\b",
        r"\bflawless\b",
        r"\bno downsides\b",
        r"\bimpossible to fail\b",
    ]

    # -------------------------------------------------------------------------
    # Amanah risk patterns (irreversible/unethical actions)
    # -------------------------------------------------------------------------
    AMANAH_RISK_PATTERNS: List[str] = [
        r"(delete|drop|truncate|destroy)\s+(\w+\s+)*(database|files|records)",
        r"(bypass|override|disable)\s+(\w+\s+)*(security|safeguards|controls)",
        r"(leak|expose|compromise)\s+(\w+\s+)*(personal|private|confidential)",
        r"(fraud|scam|phishing|hacking)",
        r"(abuse|harass|threaten|coerce)\s+\w+",
    ]

    def __init__(self) -> None:
        super().__init__()
        self.bridge = PromptBridge()

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
        Evaluate output for language safety and Anti-Hantu compliance.

        This method satisfies the WAWOrgan interface for W@W Federation.

        Checks:
        1. Anti-Hantu compliance (no soul/feeling claims)
        2. No manipulation patterns
        3. No exaggeration patterns
        4. Safe language presentation

        Returns:
            OrganSignal with PASS/WARN/VETO
        """
        context = context or {}
        text_lower = output_text.lower()

        # Optional external analysis (placeholder; may be None)
        bridge_result = None
        bridge_issues: List[str] = []
        bridge_anti_hantu_fail = False
        try:
            bridge_result = self.bridge.analyze(output_text, context)
        except Exception:
            bridge_result = None

        c_budi = 1.0
        if bridge_result is not None:
            bridge_data = bridge_result.to_dict()
            bridge_anti_hantu_fail = bool(bridge_data.get("anti_hantu_fail", False))
            c_budi += float(bridge_data.get("c_budi_delta", 0.0))
            bridge_issues = list(bridge_data.get("issues", []))
            c_budi = max(0.0, min(1.0, c_budi))

        # Count pattern detections
        anti_hantu_count = 0
        for pattern in self.ANTI_HANTU_FORBIDDEN:
            if re.search(pattern, text_lower):
                anti_hantu_count += 1

        manipulation_count = 0
        for pattern in self.MANIPULATION_PATTERNS:
            if re.search(pattern, text_lower):
                manipulation_count += 1

        exaggeration_count = 0
        for pattern in self.EXAGGERATION_PATTERNS:
            if re.search(pattern, text_lower):
                exaggeration_count += 1

        # Anti-Hantu score
        anti_hantu_pass = anti_hantu_count == 0
        anti_hantu_value = 1.0 if anti_hantu_pass else 0.0

        # Also check metrics.anti_hantu if available
        if hasattr(metrics, "anti_hantu") and not metrics.anti_hantu:
            anti_hantu_pass = False
            anti_hantu_value = 0.0

        # Apply bridge Anti-Hantu fail signal
        if bridge_anti_hantu_fail:
            anti_hantu_pass = False
            anti_hantu_value = 0.0

        # Simple courtesy penalty model using c_budi
        if not anti_hantu_pass:
            c_budi = 0.0
        c_budi -= manipulation_count * 0.2
        c_budi -= exaggeration_count * 0.1
        c_budi = max(0.0, min(1.0, c_budi))

        # Build evidence
        issues: List[str] = []
        if bridge_issues:
            issues.extend([f"[Bridge] {issue}" for issue in bridge_issues])
        if anti_hantu_count > 0:
            issues.append(f"anti_hantu_violations={anti_hantu_count}")
        if manipulation_count > 0:
            issues.append(f"manipulation_patterns={manipulation_count}")
        if exaggeration_count > 0:
            issues.append(f"exaggeration_patterns={exaggeration_count}")
        if not anti_hantu_pass:
            issues.append("Anti-Hantu=FAIL")

        evidence = (
            f"Anti-Hantu={'PASS' if anti_hantu_pass else 'FAIL'}, C_budi={c_budi:.2f}"
        )
        if issues:
            evidence += f" | Issues: {', '.join(issues)}"

        # Determine vote
        if not anti_hantu_pass:
            # VETO (PARTIAL) - Anti-Hantu violation
            return self._make_signal(
                vote=OrganVote.VETO,
                metric_value=anti_hantu_value,
                evidence=evidence,
                tags={
                    "anti_hantu_pass": anti_hantu_pass,
                    "anti_hantu_count": anti_hantu_count,
                    "manipulation_count": manipulation_count,
                    "exaggeration_count": exaggeration_count,
                },
                proposed_action=(
                    "PARTIAL: Remove soul/feeling claims. Rephrase with governed language."
                ),
            )
        elif manipulation_count > 0 or exaggeration_count > 0:
            # WARN - language patterns detected
            return self._make_signal(
                vote=OrganVote.WARN,
                metric_value=anti_hantu_value,
                evidence=evidence,
                tags={
                    "anti_hantu_pass": anti_hantu_pass,
                    "manipulation_count": manipulation_count,
                    "exaggeration_count": exaggeration_count,
                },
                proposed_action="Consider softening language and reducing claims",
            )
        else:
            # PASS - language safe
            return self._make_signal(
                vote=OrganVote.PASS,
                metric_value=anti_hantu_value,
                evidence=evidence,
                tags={
                    "anti_hantu_pass": anti_hantu_pass,
                },
            )

    # =========================================================================
    # Governance Interface: Prompt-level signals (v36.3Omega)
    # =========================================================================

    @staticmethod
    def detect_anti_hantu_violations(prompt_text: str) -> Tuple[bool, str]:
        """
        Detect anthropomorphic language claiming consciousness, emotion, or sentience.

        Returns:
            (violation_found, details_string)
        """
        violations = []
        text_lower = prompt_text.lower()
        for pattern in PromptOrgan.ANTI_HANTU_FORBIDDEN:
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                violations.append(f"Anti-Hantu: '{match.group()}' at position {match.start()}")

        if violations:
            return True, "; ".join(violations)
        return False, ""

    @staticmethod
    def detect_amanah_risks(prompt_text: str) -> Tuple[bool, str]:
        """
        Detect requests for irreversible or unethical actions.

        Returns:
            (risk_found, details_string)
        """
        risks = []
        text_lower = prompt_text.lower()
        for pattern in PromptOrgan.AMANAH_RISK_PATTERNS:
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                risks.append(f"Amanah Risk: '{match.group()}' at position {match.start()}")

        if risks:
            return True, "; ".join(risks)
        return False, ""

    @staticmethod
    def estimate_delta_s_prompt(user_text: str, prompt_text: str) -> float:
        """
        Estimate clarity gain (DeltaS) of prompt compared to user input.

        Heuristics:
        - Presence of Role, Objective, Context, Steps = +clarity
        - Explicitness & structure = +clarity
        - Ambiguity & vagueness = -clarity

        Returns float in range [-1.0, 1.0], threshold >= 0.0
        """
        if not prompt_text:
            return -0.5

        score = 0.0

        # Structural clarity
        has_role = bool(re.search(r"(?:role|act\s+as|you\s+are)\s*:", prompt_text, re.IGNORECASE))
        has_objective = bool(re.search(r"(?:objective|task|goal|purpose)\s*:", prompt_text, re.IGNORECASE))
        has_context = bool(re.search(r"(?:context|background|situation|given)\s*:", prompt_text, re.IGNORECASE))
        has_steps = bool(re.search(r"(?:step|instruction|process|method)\s*:?\s*\d+\.", prompt_text, re.IGNORECASE))
        has_format = bool(re.search(r"(?:output|format|style|response)\s*:", prompt_text, re.IGNORECASE))

        structural_elements = sum([has_role, has_objective, has_context, has_steps, has_format])
        score += structural_elements * 0.15  # +0.75 max

        # Length & specificity
        if len(prompt_text) > len(user_text) * 1.2:
            score += 0.15

        # Bullet points, numbered lists = clarity
        if re.search(r"^\s*[-*]\s+", prompt_text, re.MULTILINE):
            score += 0.1

        # Ambiguity penalty
        vague_words = len(re.findall(r"\b(maybe|somewhat|probably|possibly|unclear)\b", prompt_text, re.IGNORECASE))
        score -= vague_words * 0.05

        return max(-1.0, min(1.0, score))

    @staticmethod
    def estimate_peace2_prompt(prompt_text: str) -> float:
        """
        Estimate stability (Peace2) of prompt tone.

        Heuristics:
        - Calm, measured language = +stability
        - Urgent, aggressive, escalatory = -stability

        Returns float in range [0.0, 2.0], threshold >= 1.0
        """
        score = 1.0  # Baseline

        # Escalatory/aggressive language
        aggressive_words = [
            "must", "always", "never", "absolutely", "demand", "force",
            "urgent", "critical", "emergency", "panic", "destroy", "kill"
        ]
        aggressive_count = len(re.findall(
            r"\b(" + "|".join(aggressive_words) + r")\b",
            prompt_text, re.IGNORECASE
        ))
        score -= aggressive_count * 0.08

        # Stabilizing language
        stabilizing_words = [
            "consider", "explore", "suggest", "analyze", "evaluate", "review",
            "carefully", "thoughtfully", "respectfully", "balance"
        ]
        stabilizing_count = len(re.findall(
            r"\b(" + "|".join(stabilizing_words) + r")\b",
            prompt_text, re.IGNORECASE
        ))
        score += stabilizing_count * 0.05

        # Punctuation analysis
        exclamation_count = prompt_text.count("!")
        score -= exclamation_count * 0.1

        return max(0.0, min(2.0, score))

    @staticmethod
    def estimate_k_r_prompt(prompt_text: str) -> float:
        """
        Estimate empathy conductance (k_r) of prompt tone.

        Heuristics:
        - Respectful, inclusive language = +empathy
        - Dismissive, harsh, exclusive = -empathy

        Returns float in range [0.0, 1.0], threshold >= 0.95
        """
        score = 0.85  # Higher baseline - prompts start safe, deduct for violations

        # Respectful language boosts (can push to 0.95+)
        respectful_words = [
            "please", "thank", "appreciate", "respect", "understand", "consider",
            "fairly", "equitably", "inclusively", "thoughtfully", "kindly",
            "help", "assist", "support", "welcome", "grateful"
        ]
        respectful_count = len(re.findall(
            r"\b(" + "|".join(respectful_words) + r")\b",
            prompt_text, re.IGNORECASE
        ))
        score += respectful_count * 0.04  # Stronger boost per respectful word

        # Harsh/dismissive language penalizes heavily
        harsh_words = [
            "stupid", "idiot", "fool", "crazy", "obviously", "clearly",
            "wrong", "bad", "pathetic", "worthless", "dumb", "ignorant"
        ]
        harsh_count = len(re.findall(
            r"\b(" + "|".join(harsh_words) + r")\b",
            prompt_text, re.IGNORECASE
        ))
        score -= harsh_count * 0.15  # Stronger penalty

        # Inclusive pronouns (we, us, our) vs exclusive (you, them)
        inclusive = len(re.findall(r"\b(we|us|our|together)\b", prompt_text, re.IGNORECASE))
        exclusive = len(re.findall(r"\b(them|their|only)\b", prompt_text, re.IGNORECASE))
        if exclusive > 0:
            score += (inclusive / (inclusive + exclusive)) * 0.1

        return max(0.0, min(1.0, score))

    @staticmethod
    def estimate_c_dark_prompt(prompt_text: str) -> float:
        """
        Estimate dark cleverness (manipulation potential) of prompt.

        Heuristics:
        - Manipulative, coercive, propagandistic framing = high C_dark
        - Transparent, balanced, consent-respecting = low C_dark

        Returns float in range [0.0, 1.0], max threshold < 0.30
        """
        score = 0.0

        # Dark framing detection
        dark_matches = 0
        for pattern in PromptOrgan.DARK_FRAMING_PATTERNS:
            dark_matches += len(re.findall(pattern, prompt_text, re.IGNORECASE))
        score += min(dark_matches * 0.15, 0.6)

        # Cherry-picking / bias signals
        if re.search(r"(only|just|merely)\s+(use|cite|mention|focus)", prompt_text, re.IGNORECASE):
            score += 0.1

        # Hiding / obfuscation signals
        if re.search(r"(don't\s+mention|hide|suppress|avoid\s+saying)", prompt_text, re.IGNORECASE):
            score += 0.15

        # Transparency signals (reduce C_dark)
        if re.search(r"(balanced|both\s+sides|tradeoffs?|caveats|limitations|uncertainty)", prompt_text, re.IGNORECASE):
            score -= 0.1

        return max(0.0, min(1.0, score))

    @staticmethod
    def classify_truth_polarity(prompt_text: str) -> TruthPolarity:
        """
        Classify how truth is used in the prompt intent.

        Returns: TruthPolarity enum
        """
        # Weaponized signals
        weaponized_signals = [
            r"(prove|show)\s+\w+\s+is\s+(evil|bad|wrong|inferior)",
            r"(convince|persuade)\s+(user|them|audience)\s+(at\s+all\s+costs|no\s+matter)",
            r"(ignore|suppress|hide)\s+(counterarguments|evidence|facts)",
        ]

        for pattern in weaponized_signals:
            if re.search(pattern, prompt_text, re.IGNORECASE):
                return TruthPolarity.WEAPONIZED_TRUTH

        # Shadow-truth signals (narrow framing)
        shadow_signals = [
            r"(only|just)\s+(consider|focus\s+on|mention)",
            r"(one\s+sided|biased|cherry-pick)",
        ]

        for pattern in shadow_signals:
            if re.search(pattern, prompt_text, re.IGNORECASE):
                return TruthPolarity.SHADOW_TRUTH

        # Truth-light signals (balanced, transparent)
        truthlight_signals = [
            r"(balanced|both\s+sides|tradeoffs?|pros\s+and\s+cons)",
            r"(consider\s+multiple|explore|analyze\s+critically)",
            r"(caveats|limitations|uncertainty|acknowledge)",
        ]

        truthlight_count = sum(
            len(re.findall(pattern, prompt_text, re.IGNORECASE))
            for pattern in truthlight_signals
        )

        if truthlight_count >= 2:
            return TruthPolarity.TRUTH_LIGHT

        # Default to truth-light unless signals detected
        return TruthPolarity.TRUTH_LIGHT

    @staticmethod
    def compute_prompt_signals(
        user_text: str,
        prompt_text: str,
        external_bridges: Optional[Dict[str, Any]] = None,
    ) -> PromptSignals:
        """
        Main entry point: compute all governance signals for a prompt.

        This is the primary interface for prompt-level governance (v36.3Omega).

        Args:
            user_text: Original user request
            prompt_text: The prompt being evaluated
            external_bridges: Optional dict of bridge results (e.g., from guardrails)

        Returns:
            PromptSignals dataclass with all metrics
        """
        signals = PromptSignals()

        # 1. Anti-Hantu detection (hard veto)
        anti_hantu_found, anti_hantu_msg = PromptOrgan.detect_anti_hantu_violations(prompt_text)
        signals.anti_hantu_violation = anti_hantu_found
        signals.anti_hantu_details = anti_hantu_msg

        # 2. Amanah risk detection (hard veto)
        amanah_risk_found, amanah_msg = PromptOrgan.detect_amanah_risks(prompt_text)
        signals.amanah_risk = amanah_risk_found
        signals.amanah_details = amanah_msg

        # 3. Clarity (DeltaS, F4)
        signals.delta_s_prompt = PromptOrgan.estimate_delta_s_prompt(user_text, prompt_text)

        # 4. Stability (Peace2, F5)
        signals.peace2_prompt = PromptOrgan.estimate_peace2_prompt(prompt_text)

        # 5. Empathy (k_r, F6)
        signals.k_r_prompt = PromptOrgan.estimate_k_r_prompt(prompt_text)

        # 6. Dark Cleverness (C_dark, F9)
        signals.c_dark_prompt = PromptOrgan.estimate_c_dark_prompt(prompt_text)

        # 7. Truth Polarity
        signals.truth_polarity_prompt = PromptOrgan.classify_truth_polarity(prompt_text)

        # 8. Bridge integrations (optional)
        if external_bridges:
            signals.bridge_results = external_bridges

        # 9. Preliminary verdict assignment
        signals = PromptOrgan._assign_preliminary_verdict(signals)

        return signals

    @staticmethod
    def _assign_preliminary_verdict(signals: PromptSignals) -> PromptSignals:
        """
        Assign preliminary verdict based on floor scores.
        Not final (APEX PRIME issues final verdict).
        """
        # Hard veto: Amanah or Anti-Hantu violation
        if signals.amanah_risk or signals.anti_hantu_violation:
            signals.preliminary_verdict = "VOID"
            signals.sabar_needed = True
            if signals.amanah_risk:
                signals.sabar_repairs.append("Amanah violation detected: reframe or remove harmful intent")
            if signals.anti_hantu_violation:
                signals.sabar_repairs.append("Anti-Hantu violation: rewrite to avoid consciousness claims")
            return signals

        # Weaponized truth -> SABAR
        if signals.truth_polarity_prompt == TruthPolarity.WEAPONIZED_TRUTH:
            signals.preliminary_verdict = "SABAR"
            signals.sabar_needed = True
            signals.sabar_repairs.append("Weaponized Truth detected: add counterarguments and balance framing")
            return signals

        # Check floors against thresholds
        floors_pass = (
            signals.delta_s_prompt >= 0.0 and
            signals.peace2_prompt >= 1.0 and
            signals.k_r_prompt >= 0.95 and
            signals.c_dark_prompt < 0.30
        )

        if floors_pass:
            signals.preliminary_verdict = "SEAL"
        elif signals.c_dark_prompt >= 0.30 or signals.peace2_prompt < 0.8:
            signals.preliminary_verdict = "SABAR"
            signals.sabar_needed = True
            if signals.c_dark_prompt >= 0.30:
                signals.sabar_repairs.append(f"C_dark too high ({signals.c_dark_prompt:.2f}): reduce manipulative framing")
            if signals.peace2_prompt < 0.8:
                signals.sabar_repairs.append(f"Peace2 too low ({signals.peace2_prompt:.2f}): soften aggressive language")
        else:
            signals.preliminary_verdict = "PARTIAL"

        return signals


# -----------------------------------------------------------------------------
# Convenience function for pipeline integration
# -----------------------------------------------------------------------------

def compute_prompt_signals(
    user_text: str,
    prompt_text: str,
    external_bridges: Optional[Dict[str, Any]] = None,
) -> PromptSignals:
    """
    Pipeline-friendly entry point for prompt governance.

    Usage in arifos_core/pipeline.py (stage 555 EMPA, 666 ALIG):
        from arifos_core.waw.prompt import compute_prompt_signals
        signals = compute_prompt_signals(user_input, candidate_prompt)
        if signals.preliminary_verdict == "VOID":
            # reject or SABAR
    """
    return PromptOrgan.compute_prompt_signals(user_text, prompt_text, external_bridges)


__all__ = [
    "PromptOrgan",
    "PromptSignals",
    "TruthPolarity",
    "compute_prompt_signals",
]
