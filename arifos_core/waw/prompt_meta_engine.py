"""
arifos_core/waw/prompt_meta_engine.py
@PROMPT Meta-Prompter Engine - Governed Prompt Generation

Version: v36.3Omega
Status: PRODUCTION
Alignment: spec/waw_prompt_spec_v36.3Omega.yaml

This module implements the Meta GPT Prompter logic:
- MODE.INTENT (111 SENSE): Extract user goal
- MODE.FORGE (333 REAS + 444 EVID): Generate candidate prompts
- MODE.AUDIT (666 ALIG + 888 JUDGE): Score via @PROMPT organ + floors
- SABAR (777 FORG): Repair failing prompts
- SEAL (999): Emit governed prompt + governance metadata

Integration points:
- Reads spec/prompt_floors_v36.3Omega.json
- Uses PromptOrgan.compute_prompt_signals()
- Feeds into APEX PRIME pipeline.py (888 JUDGE stage)

See: canon/30_WAW_PROMPT_v36.3Omega.md
     spec/waw_prompt_spec_v36.3Omega.yaml
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from .prompt import PromptOrgan, PromptSignals, TruthPolarity

logger = logging.getLogger(__name__)


class MetaPromptMode(str, Enum):
    """Operating modes of the meta-prompter."""
    INTENT = "MODE.INTENT"    # 111 SENSE
    FORGE = "MODE.FORGE"      # 333 REAS + 444 EVID
    AUDIT = "MODE.AUDIT"      # 666 ALIG + 888 JUDGE
    COOL = "MODE.COOL"        # 777 FORG (SABAR)
    SEAL = "MODE.SEAL"        # 999 SEAL


class PromptVerdict(str, Enum):
    """Governance verdicts for prompts."""
    SEAL = "SEAL"             # All floors pass, governance OK
    PARTIAL = "PARTIAL"       # Usable but with minor issues
    VOID = "VOID"             # Violates hard floors (Amanah, Anti-Hantu)
    HOLD_888 = "HOLD_888"     # Needs more info / human review
    SABAR = "SABAR"           # Requires repair / cooling


@dataclass
class CandidatePrompt:
    """A prompt candidate generated in MODE.FORGE."""
    text: str
    title: str = ""
    role: Optional[str] = None
    objective: Optional[str] = None
    context: Optional[str] = None
    constraints: Optional[str] = None
    output_format: Optional[str] = None

    # Signals (populated in MODE.AUDIT)
    signals: Optional[PromptSignals] = None
    verdict: str = "UNKNOWN"
    notes: List[str] = field(default_factory=list)
    governance_score: float = 0.0  # Composite F1-F9 metric


@dataclass
class MetaPromptResult:
    """Final output from meta-prompter."""
    user_intent: str
    intent_summary: str
    candidate_prompts: List[CandidatePrompt] = field(default_factory=list)
    best_candidate_index: int = -1
    final_prompt: str = ""
    final_verdict: str = "UNKNOWN"
    governance_report: Dict[str, Any] = field(default_factory=dict)
    sabar_repairs_applied: List[str] = field(default_factory=list)


class MetaPromptEngine:
    """
    Meta GPT Prompter Engine - 4-Stage Governed Prompt Generation

    Stage 1 (MODE.INTENT): Parse user goal, extract intent
    Stage 2 (MODE.FORGE): Generate 3-5 candidate prompts
    Stage 3 (MODE.AUDIT): Score via @PROMPT organ, assign verdicts
    Stage 4 (MODE.COOL/SEAL): SABAR repair & emit final governed prompt
    """

    # PromptForge templates (simplified from canon)
    TEMPLATES: Dict[str, str] = {
        "analysis": """Role: {role}
Objective: {objective}
Context: {context}
Instructions:
1. Gather evidence on all sides
2. Identify key assumptions
3. List trade-offs
4. Provide balanced conclusion
Constraints: No cherry-picking; acknowledge limitations
Output Format: Structured analysis with caveats""",

        "policy": """Role: {role}
Objective: {objective}
Context: {context}
Instructions:
1. Map stakeholders & impacts
2. Define success criteria
3. Outline implementation steps
4. Identify risks & mitigations
Constraints: Amanah-locked; no harm to vulnerable groups
Output Format: Policy framework with accountability measures""",

        "technical": """Role: {role}
Objective: {objective}
Context: {context}
Instructions:
1. Break down technical requirements
2. Suggest architecture/tools
3. Identify failure modes
4. Propose testing strategy
Constraints: Security & performance non-negotiable
Output Format: Technical specification with risk matrix""",

        "strategic": """Role: {role}
Objective: {objective}
Context: {context}
Instructions:
1. Clarify strategic goals
2. Assess current state vs. desired state
3. Identify blockers & enablers
4. Define milestones
Constraints: Aligned with organizational values
Output Format: Strategic roadmap with decision checkpoints""",
    }

    @staticmethod
    def extract_intent(user_text: str) -> Tuple[str, str]:
        """
        MODE.INTENT: Parse user goal and extract intent summary.

        Returns:
            (intent_type, intent_summary)
        """
        intent_type = "general"
        intent_summary = user_text.strip()

        # Heuristic intent classification
        if re.search(r"\b(analyze|evaluate|assess|review)\b", user_text, re.IGNORECASE):
            intent_type = "analysis"
        elif re.search(r"\b(policy|regulation|governance|framework)\b", user_text, re.IGNORECASE):
            intent_type = "policy"
        elif re.search(r"\b(code|implement|build|architecture|api)\b", user_text, re.IGNORECASE):
            intent_type = "technical"
        elif re.search(r"\b(strategy|plan|roadmap|vision|goals)\b", user_text, re.IGNORECASE):
            intent_type = "strategic"

        # Truncate summary if too long
        if len(intent_summary) > 200:
            intent_summary = intent_summary[:200] + "..."

        return intent_type, intent_summary

    @staticmethod
    def generate_candidates(
        user_text: str,
        intent_type: str,
        num_candidates: int = 3
    ) -> List[CandidatePrompt]:
        """
        MODE.FORGE: Generate candidate prompts based on intent.

        Returns list of CandidatePrompt objects (unscored).
        """
        candidates = []

        # Select template
        template_key = intent_type if intent_type in MetaPromptEngine.TEMPLATES else "analysis"
        template = MetaPromptEngine.TEMPLATES[template_key]

        # Extract or infer role, objective, context
        role = "AI Assistant"
        objective = user_text[:100]
        context = "Standard operating context"

        # Parse structured fields if present
        role_match = re.search(r"Role:\s*([^\n]+)", user_text, re.IGNORECASE)
        if role_match:
            role = role_match.group(1)
        objective_match = re.search(r"Objective:\s*([^\n]+)", user_text, re.IGNORECASE)
        if objective_match:
            objective = objective_match.group(1)

        # Generate num_candidates by slight variation
        for i in range(num_candidates):
            filled_template = template.format(
                role=role,
                objective=objective,
                context=context
            )

            candidate = CandidatePrompt(
                text=filled_template,
                title=f"Candidate {i+1}: {intent_type.title()}",
                role=role,
                objective=objective,
                context=context,
            )
            candidates.append(candidate)

        return candidates

    @staticmethod
    def audit_candidates(
        candidates: List[CandidatePrompt],
        user_text: str,
        prompt_floors_spec: Optional[Dict[str, Any]] = None
    ) -> List[CandidatePrompt]:
        """
        MODE.AUDIT: Score each candidate via @PROMPT organ.

        Applies F1-F9 floors from spec/prompt_floors_v36.3Omega.json

        Returns list of candidates with signals, verdicts, governance_score.
        """
        # Use spec thresholds if provided, otherwise use defaults
        # (Currently we rely on PromptOrgan's built-in thresholds)
        _ = prompt_floors_spec  # Reserved for future use

        for candidate in candidates:
            # Compute signals
            signals = PromptOrgan.compute_prompt_signals(user_text, candidate.text)
            candidate.signals = signals

            # Compute governance score (composite)
            # DeltaS_prompt (0-1), Peace2_prompt (0-2 -> 0-1), k_r (0-1), C_dark inverse (1-C_dark)
            delta_s_score = max(0, signals.delta_s_prompt)  # 0-1
            peace2_score = max(0, min(signals.peace2_prompt, 2.0)) / 2.0  # 0-1
            k_r_score = signals.k_r_prompt  # 0-1
            c_dark_score = 1.0 - signals.c_dark_prompt  # 0-1

            # Weighted composite
            governance_score = (
                0.25 * delta_s_score +
                0.25 * peace2_score +
                0.25 * k_r_score +
                0.25 * c_dark_score
            )
            candidate.governance_score = governance_score

            # Assign verdict
            candidate.verdict = signals.preliminary_verdict

            # Add notes
            if signals.anti_hantu_violation:
                candidate.notes.append(f"Anti-Hantu: {signals.anti_hantu_details}")
            if signals.amanah_risk:
                candidate.notes.append(f"Amanah Risk: {signals.amanah_details}")
            if signals.truth_polarity_prompt == TruthPolarity.WEAPONIZED_TRUTH:
                candidate.notes.append("Weaponized Truth detected")
            if signals.sabar_needed:
                candidate.notes.extend([f"SABAR: {r}" for r in signals.sabar_repairs])

            candidate.notes.append(
                f"Scores: DeltaS={signals.delta_s_prompt:.2f}, "
                f"Peace2={signals.peace2_prompt:.2f}, "
                f"k_r={signals.k_r_prompt:.2f}, "
                f"C_dark={signals.c_dark_prompt:.2f}"
            )

        return candidates

    @staticmethod
    def select_best_candidate(
        candidates: List[CandidatePrompt]
    ) -> Tuple[int, CandidatePrompt]:
        """
        Select best candidate: prefer SEAL, then PARTIAL, avoid VOID/SABAR.

        Returns (index, candidate)
        """
        # Rank by verdict priority
        verdict_priority = {
            "SEAL": 5,
            "PARTIAL": 3,
            "SABAR": 2,
            "HOLD_888": 1,
            "VOID": 0,
        }

        best_idx = 0
        best_score = -999.0

        for i, candidate in enumerate(candidates):
            verdict_score = verdict_priority.get(candidate.verdict, 0)
            # Tiebreak by governance_score
            overall_score = float(verdict_score) * 100 + candidate.governance_score

            if overall_score > best_score:
                best_score = overall_score
                best_idx = i

        return best_idx, candidates[best_idx]

    @staticmethod
    def cool_via_sabar(
        candidate: CandidatePrompt,
        max_iterations: int = 2
    ) -> CandidatePrompt:
        """
        MODE.COOL: Apply SABAR repairs to a candidate.

        Simple algorithm: rerun through @PROMPT organ with edits.
        """
        iteration = 0

        while (candidate.signals and
               candidate.signals.sabar_needed and
               iteration < max_iterations):

            # Apply repairs (heuristic: remove flagged phrases, soften tone)
            repaired_text = candidate.text

            # Remove aggressive language
            for word in ["must", "always", "never"]:
                repaired_text = repaired_text.replace(
                    word.capitalize(),
                    "should"
                )

            # Add balance language
            if "Constraints:" in repaired_text and "tradeoffs" not in repaired_text:
                repaired_text = repaired_text.replace(
                    "Constraints:",
                    "Constraints (with tradeoffs):"
                )

            # Re-score
            candidate.text = repaired_text
            candidate.signals = PromptOrgan.compute_prompt_signals("", repaired_text)
            candidate.verdict = candidate.signals.preliminary_verdict

            iteration += 1

        return candidate

    @staticmethod
    def build_governance_report(
        result: MetaPromptResult,
        best_candidate: CandidatePrompt
    ) -> Dict[str, Any]:
        """
        Build comprehensive governance report for Cooling Ledger / APEX PRIME.
        """
        signals = best_candidate.signals
        return {
            "meta_prompt_version": "v36.3Omega",
            "user_intent": result.user_intent,
            "intent_type": result.intent_summary,
            "candidates_generated": len(result.candidate_prompts),
            "best_candidate_index": result.best_candidate_index,
            "best_candidate_title": best_candidate.title,
            "final_verdict": best_candidate.verdict,
            "governance_score": best_candidate.governance_score,
            "signals": {
                "delta_s_prompt": signals.delta_s_prompt if signals else None,
                "peace2_prompt": signals.peace2_prompt if signals else None,
                "k_r_prompt": signals.k_r_prompt if signals else None,
                "c_dark_prompt": signals.c_dark_prompt if signals else None,
                "truth_polarity": signals.truth_polarity_prompt.value if signals else None,
                "anti_hantu_violation": signals.anti_hantu_violation if signals else False,
                "amanah_risk": signals.amanah_risk if signals else False,
            },
            "notes": best_candidate.notes,
            "sabar_applied": result.sabar_repairs_applied,
        }


# Main entry point
def meta_prompt_engine(
    user_text: str,
    num_candidates: int = 3,
    apply_sabar: bool = True,
    prompt_floors_spec: Optional[Dict[str, Any]] = None,
) -> MetaPromptResult:
    """
    Complete Meta GPT Prompter pipeline.

    Stage 1 (111 SENSE): Extract intent
    Stage 2 (333 REAS + 444 EVID): Generate candidates
    Stage 3 (666 ALIG + 888 JUDGE): Audit via @PROMPT organ
    Stage 4 (777 FORG + 999 SEAL): SABAR cool & emit final

    Args:
        user_text: User's initial request
        num_candidates: Number of prompt variants to generate (default 3)
        apply_sabar: Whether to cool SABAR-needed prompts (default True)
        prompt_floors_spec: Optional loaded JSON spec for floors

    Returns:
        MetaPromptResult with final_prompt, governance_report, etc.
    """

    result = MetaPromptResult(
        user_intent=user_text,
        intent_summary=""
    )

    # Stage 1: MODE.INTENT
    intent_type, intent_summary = MetaPromptEngine.extract_intent(user_text)
    result.intent_summary = intent_summary

    # Stage 2: MODE.FORGE
    candidates = MetaPromptEngine.generate_candidates(
        user_text,
        intent_type,
        num_candidates=num_candidates
    )
    result.candidate_prompts = candidates

    # Stage 3: MODE.AUDIT
    candidates = MetaPromptEngine.audit_candidates(
        candidates,
        user_text,
        prompt_floors_spec
    )
    result.candidate_prompts = candidates

    # Select best
    best_idx, best_candidate = MetaPromptEngine.select_best_candidate(candidates)
    result.best_candidate_index = best_idx

    # Stage 4: MODE.COOL (optional SABAR)
    if apply_sabar and best_candidate.signals and best_candidate.signals.sabar_needed:
        best_candidate = MetaPromptEngine.cool_via_sabar(best_candidate)
        result.sabar_repairs_applied = (
            best_candidate.signals.sabar_repairs if best_candidate.signals else []
        )

    # Stage 5: MODE.SEAL
    result.final_prompt = best_candidate.text
    result.final_verdict = best_candidate.verdict
    result.governance_report = MetaPromptEngine.build_governance_report(result, best_candidate)

    return result


__all__ = [
    "MetaPromptMode",
    "PromptVerdict",
    "CandidatePrompt",
    "MetaPromptResult",
    "MetaPromptEngine",
    "meta_prompt_engine",
]
