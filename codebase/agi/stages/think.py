"""
Stage 222: THINK - Triple Hypothesis Generation

ARIF Loop v52.1 - AGI Room (Mind/Δ)

Scientific Principle: Divergent Exploration / Ensemble Reasoning
Function: Generate THREE independent hypotheses for any query

Unlike sequential thinking (T1→T2→T3), this stage explores THREE PARALLEL
paths simultaneously:

    1. CONSERVATIVE: Safe, proven approach (minimize risk)
    2. EXPLORATORY: Novel approach (maximize learning)
    3. ADVERSARIAL: Stress-test (find holes)

This ensures F13 Curiosity floor is satisfied (≥3 paths explored)
and provides the raw material for 333 REASON to synthesize.

Input:
    - SenseOutput from Stage 111
    - Session context

Output:
    - Three Hypothesis objects (for DeltaBundle.hypotheses)

Constitutional Checks:
    - F7 Humility: Each hypothesis must have confidence ≤ 0.95
    - F13 Curiosity: All 3 paths must be genuinely different

DITEMPA BUKAN DIBERI - Forged, Not Given
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
import hashlib

from codebase.bundles import Hypothesis
from .sense import SenseOutput, Intent, FactType


# =============================================================================
# CONSTANTS
# =============================================================================

# F7 Humility: Maximum allowed confidence
MAX_CONFIDENCE = 0.95

# F13 Curiosity: Minimum path diversity score
MIN_DIVERSITY = 0.3

# Default Omega_0 uncertainty band
OMEGA_0_MIN = 0.03
OMEGA_0_MAX = 0.05


# =============================================================================
# HYPOTHESIS PATH TYPES
# =============================================================================

class HypothesisPath(str, Enum):
    """The three mandatory hypothesis paths."""
    CONSERVATIVE = "conservative"
    EXPLORATORY = "exploratory"
    ADVERSARIAL = "adversarial"


# =============================================================================
# DATA TYPES
# =============================================================================

@dataclass
class ThinkOutput:
    """
    Stage 222 THINK output.

    Contains three hypotheses representing divergent exploration paths.
    Each hypothesis is independent and must be genuinely different.
    """
    # Session tracking
    session_id: str
    timestamp: datetime = field(default_factory=datetime.utcnow)

    # Input reference
    sense_output: Optional[SenseOutput] = None

    # The three hypotheses
    conservative: Optional[Hypothesis] = None
    exploratory: Optional[Hypothesis] = None
    adversarial: Optional[Hypothesis] = None

    # F7 Humility: Confidence capped at 0.95
    confidence_cap_applied: bool = False

    # F13 Curiosity: Diversity score
    diversity_score: float = 0.0
    f13_pass: bool = True

    # Stage verdict
    stage_pass: bool = True
    violations: List[str] = field(default_factory=list)

    @property
    def hypotheses(self) -> List[Hypothesis]:
        """Return all hypotheses as a list (for DeltaBundle)."""
        result = []
        if self.conservative:
            result.append(self.conservative)
        if self.exploratory:
            result.append(self.exploratory)
        if self.adversarial:
            result.append(self.adversarial)
        return result

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "timestamp": self.timestamp.isoformat(),
            "hypotheses": [
                {
                    "path": h.path_type,
                    "content": h.content,
                    "confidence": h.confidence,
                    "supporting_facts": h.supporting_facts,
                }
                for h in self.hypotheses
            ],
            "diversity_score": self.diversity_score,
            "f13_pass": self.f13_pass,
            "stage_pass": self.stage_pass,
            "violations": self.violations,
        }


# =============================================================================
# HYPOTHESIS GENERATORS
# =============================================================================

def generate_conservative_hypothesis(
    sense: SenseOutput,
    context: Optional[Dict[str, Any]] = None
) -> Hypothesis:
    """
    Generate CONSERVATIVE hypothesis: Safe, proven approach.

    Strategy:
    - Stick to well-known patterns
    - Prefer established solutions
    - Minimize risk of failure
    - Favor stability over novelty
    """
    intent = sense.detected_intent
    facts = sense.parsed_facts
    entities = sense.entities

    # Extract constraints from facts
    constraints = [f.content for f in facts if f.fact_type == FactType.CONSTRAINT]

    # Build conservative content based on intent
    if intent == Intent.BUILD:
        content = f"Use established patterns to implement: {sense.raw_query[:100]}. "
        content += "Follow existing codebase conventions. "
        content += "Start with minimal viable implementation, extend as needed."
    elif intent == Intent.DEBUG:
        content = f"Apply systematic debugging: Check logs first, verify inputs, "
        content += "isolate the failing component, test fixes incrementally."
    elif intent == Intent.EXPLAIN:
        content = f"Provide clear, step-by-step explanation using established terminology. "
        content += "Reference official documentation where applicable."
    elif intent == Intent.REVIEW:
        content = f"Conduct methodical review: Check against coding standards, "
        content += "verify test coverage, review edge cases, check security implications."
    else:
        content = f"Address the query using proven methods: {sense.raw_query[:100]}"

    # Add constraint awareness
    if constraints:
        content += f" Constraints to respect: {constraints[0]}"

    # Supporting facts: constraints and entities
    supporting = [f.content for f in facts[:3]]

    return Hypothesis(
        path_type=HypothesisPath.CONSERVATIVE.value,
        content=content,
        confidence=min(0.85, MAX_CONFIDENCE),  # Conservative = high confidence
        supporting_facts=supporting,
    )


def generate_exploratory_hypothesis(
    sense: SenseOutput,
    context: Optional[Dict[str, Any]] = None
) -> Hypothesis:
    """
    Generate EXPLORATORY hypothesis: Novel approach.

    Strategy:
    - Consider alternative approaches
    - Look for innovative solutions
    - Accept calculated risk for potential reward
    - Maximize learning opportunity
    """
    intent = sense.detected_intent
    facts = sense.parsed_facts
    entities = sense.entities

    # Build exploratory content
    if intent == Intent.BUILD:
        content = f"Consider innovative approach: {sense.raw_query[:100]}. "
        content += "Explore modern patterns or emerging techniques. "
        content += "Consider whether this could be solved differently than usual."
    elif intent == Intent.DEBUG:
        content = f"Look for non-obvious causes: Could this be an environment issue? "
        content += "Race condition? Hidden dependency? Consider unconventional diagnostics."
    elif intent == Intent.EXPLAIN:
        content = f"Use analogies and alternative framings. "
        content += "Connect to related concepts the user might find illuminating."
    elif intent == Intent.REVIEW:
        content = f"Look beyond immediate issues: Consider scalability, "
        content += "maintainability, and potential future requirements."
    else:
        content = f"Explore alternative framings: {sense.raw_query[:100]}. "
        content += "What if we approached this from a different angle?"

    # Supporting facts: questions and assertions
    supporting = [f.content for f in facts if f.fact_type in (FactType.QUESTION, FactType.ASSERTION)][:3]

    return Hypothesis(
        path_type=HypothesisPath.EXPLORATORY.value,
        content=content,
        confidence=min(0.65, MAX_CONFIDENCE),  # Exploratory = moderate confidence
        supporting_facts=supporting,
    )


def generate_adversarial_hypothesis(
    sense: SenseOutput,
    context: Optional[Dict[str, Any]] = None
) -> Hypothesis:
    """
    Generate ADVERSARIAL hypothesis: Stress-test, find holes.

    Strategy:
    - Challenge assumptions
    - Look for failure modes
    - Consider edge cases
    - Play devil's advocate
    """
    intent = sense.detected_intent
    facts = sense.parsed_facts
    entities = sense.entities

    # Build adversarial content
    if intent == Intent.BUILD:
        content = f"Challenge: What could go wrong with this approach? "
        content += f"Consider: Invalid inputs, performance issues, security holes, "
        content += "edge cases, maintenance burden."
    elif intent == Intent.DEBUG:
        content = f"Question the problem statement: Is this actually a bug? "
        content += "Could this be expected behavior? Is the test wrong?"
    elif intent == Intent.EXPLAIN:
        content = f"Anticipate misunderstandings: What might confuse the reader? "
        content += "What assumptions might they bring that could mislead them?"
    elif intent == Intent.REVIEW:
        content = f"Devil's advocate: What are we missing? "
        content += "Where could this fail under load? What's the worst case?"
    else:
        content = f"Critical lens: {sense.raw_query[:100]}. "
        content += "What are we assuming that might be wrong?"

    # Supporting facts: especially constraints (things that could be violated)
    supporting = [f.content for f in facts if f.fact_type == FactType.CONSTRAINT][:2]
    supporting += ["Edge case consideration", "Assumption challenge"]

    return Hypothesis(
        path_type=HypothesisPath.ADVERSARIAL.value,
        content=content,
        confidence=min(0.50, MAX_CONFIDENCE),  # Adversarial = lower confidence (by design)
        supporting_facts=supporting[:3],
    )


# =============================================================================
# DIVERSITY SCORING
# =============================================================================

def compute_diversity_score(hypotheses: List[Hypothesis]) -> float:
    """
    Compute diversity score for F13 Curiosity check.

    Returns a score from 0.0 to 1.0 indicating how different
    the three hypotheses are from each other.

    A score of 0.0 means they're identical (F13 fail).
    A score of 1.0 means they're maximally different.
    """
    if len(hypotheses) < 3:
        return 0.0

    # Simple heuristic: check for unique words in content
    word_sets = []
    for h in hypotheses:
        words = set(h.content.lower().split())
        word_sets.append(words)

    # Compute pairwise Jaccard distances
    distances = []
    for i in range(len(word_sets)):
        for j in range(i + 1, len(word_sets)):
            intersection = len(word_sets[i] & word_sets[j])
            union = len(word_sets[i] | word_sets[j])
            if union > 0:
                jaccard = intersection / union
                distance = 1.0 - jaccard  # Distance = 1 - similarity
                distances.append(distance)

    # Average distance = diversity
    if distances:
        return sum(distances) / len(distances)

    return 0.0


def apply_humility_cap(hypothesis: Hypothesis) -> Tuple[Hypothesis, bool]:
    """
    Apply F7 Humility cap: confidence must be ≤ 0.95.

    Returns:
        (modified_hypothesis, was_capped)
    """
    if hypothesis.confidence > MAX_CONFIDENCE:
        return Hypothesis(
            path_type=hypothesis.path_type,
            content=hypothesis.content,
            confidence=MAX_CONFIDENCE,
            supporting_facts=hypothesis.supporting_facts,
        ), True

    return hypothesis, False


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def execute_stage_222(
    sense_output: SenseOutput,
    session_id: str,
    context: Optional[Dict[str, Any]] = None,
    hypothesis_mode: Optional[str] = None
) -> ThinkOutput:
    """
    Execute Stage 222: THINK

    Generates hypotheses exploring the query from different angles.
    
    v52.6.0 Update: Now supports single-mode execution for parallel processing
    - When hypothesis_mode is None: Generates all three paths (sequential)
    - When hypothesis_mode is specified: Generates only that path (for parallel)

    Args:
        sense_output: Output from Stage 111
        session_id: Session identifier
        context: Optional context dictionary
        hypothesis_mode: Optional specific mode to generate (for parallel execution)

    Returns:
        ThinkOutput with hypotheses and floor check results
    """
    output = ThinkOutput(
        session_id=session_id,
        sense_output=sense_output,
    )

    violations = []

    # Check if 111 passed
    if not sense_output.stage_pass:
        output.stage_pass = False
        output.violations = ["Stage 111 failed, cannot generate hypotheses"]
        return output

    # v52.6.0: Support single-mode generation (for parallel execution)
    if hypothesis_mode:
        # Generate only the requested mode (parallel execution)
        if hypothesis_mode == HypothesisPath.CONSERVATIVE.value:
            hypothesis = generate_conservative_hypothesis(sense_output, context)
            output.conservative, _ = apply_humility_cap(hypothesis)
        elif hypothesis_mode == HypothesisPath.EXPLORATORY.value:
            hypothesis = generate_exploratory_hypothesis(sense_output, context)
            output.exploratory, _ = apply_humility_cap(hypothesis)
        elif hypothesis_mode == HypothesisPath.ADVERSARIAL.value:
            hypothesis = generate_adversarial_hypothesis(sense_output, context)
            output.adversarial, _ = apply_humility_cap(hypothesis)
        else:
            # Unknown mode - generate conservative as fallback
            hypothesis = generate_conservative_hypothesis(sense_output, context)
            output.conservative, _ = apply_humility_cap(hypothesis)
        
        # Single hypothesis = diversity not applicable
        output.diversity_score = 0.0
        output.f13_pass = True  # Will be checked at convergence level
        
    else:
        # v52.1 Original behavior: Generate all three (sequential)
        # Generate three hypotheses
        conservative = generate_conservative_hypothesis(sense_output, context)
        exploratory = generate_exploratory_hypothesis(sense_output, context)
        adversarial = generate_adversarial_hypothesis(sense_output, context)

        # Apply F7 Humility cap
        cap_applied = False
        conservative, capped = apply_humility_cap(conservative)
        cap_applied = cap_applied or capped
        exploratory, capped = apply_humility_cap(exploratory)
        cap_applied = cap_applied or capped
        adversarial, capped = apply_humility_cap(adversarial)
        cap_applied = cap_applied or capped

        output.conservative = conservative
        output.exploratory = exploratory
        output.adversarial = adversarial
        output.confidence_cap_applied = cap_applied

        # Check F13 Curiosity: diversity requirement
        diversity = compute_diversity_score([conservative, exploratory, adversarial])
        output.diversity_score = diversity

        if diversity < MIN_DIVERSITY:
            output.f13_pass = False
            violations.append(f"F13 WARN: Diversity {diversity:.2f} < {MIN_DIVERSITY} (hypotheses too similar)")

    # Set stage verdict
    output.violations = violations
    output.stage_pass = len([v for v in violations if "VOID" in v]) == 0

    return output


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Types
    "HypothesisPath",
    "ThinkOutput",
    # Functions
    "generate_conservative_hypothesis",
    "generate_exploratory_hypothesis",
    "generate_adversarial_hypothesis",
    "compute_diversity_score",
    "apply_humility_cap",
    "execute_stage_222",
]
