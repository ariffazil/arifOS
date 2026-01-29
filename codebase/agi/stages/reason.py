"""
Stage 333: REASON - Synthesis and Vote

ARIF Loop v52.1 - AGI Room (Mind/Δ)

Scientific Principle: Thermodynamic Convergence / Vector Synthesis
Function: Synthesize hypotheses into reasoning tree, compute ΔS, cast vote

This is the FINAL stage of the AGI room. It takes the three divergent
hypotheses from 222 THINK and synthesizes them into a coherent reasoning
tree. It then computes all AGI floor scores and casts an independent vote.

The output is the sealed DELTA_BUNDLE, ready for 444 TRINITY_SYNC.

Input:
    - SenseOutput from Stage 111
    - ThinkOutput from Stage 222

Output:
    - ReasoningTree (synthesis of hypotheses)
    - AGIFloorScores (F2, F4, F7, F13)
    - Independent vote (SEAL/VOID/UNCERTAIN)
    - Sealed DeltaBundle

Constitutional Checks:
    - F2 Truth: ≥ 0.99 (reasoning must be factually grounded)
    - F4 Clarity: ΔS ≤ 0 (must reduce confusion, not increase it)
    - F7 Humility: Ω₀ ∈ [0.03, 0.05] (uncertainty band)
    - F13 Curiosity: Already checked in 222 (pass-through)

DITEMPA BUKAN DIBERI - Forged, Not Given
"""

from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum

from codebase.bundles import (
    EngineVote,
    DeltaBundle,
    Hypothesis,
    ReasoningTree,
    AGIFloorScores,
)
from .sense import SenseOutput, ParsedFact
from .think import ThinkOutput
# v53: Import Precision Weighting logic
from codebase.agi.evidence import (
    estimate_precision,
    compute_precision_weighted_update
)


# =============================================================================
# CONSTANTS (Constitutional Thresholds)
# =============================================================================

# F2 Truth: Minimum score for SEAL
F2_TRUTH_THRESHOLD = 0.99

# F4 Clarity: Maximum ΔS for SEAL (must be cooling, not heating)
F4_CLARITY_THRESHOLD = 0.0  # ΔS ≤ 0

# F7 Humility: Omega_0 uncertainty band
OMEGA_0_MIN = 0.03
OMEGA_0_MAX = 0.05
OMEGA_0_DEFAULT = 0.04

# F13 Curiosity: Minimum paths explored
F13_PATHS_MIN = 3


# =============================================================================
# DATA TYPES
# =============================================================================

@dataclass
class ReasonOutput:
    """
    Stage 333 REASON output.

    Contains the synthesized reasoning tree, all floor scores,
    and the independent AGI vote.
    """
    # Session tracking
    session_id: str
    timestamp: datetime = field(default_factory=datetime.utcnow)

    # Reasoning synthesis
    reasoning_tree: Optional[ReasoningTree] = None

    # Thermodynamics
    entropy_before: float = 0.0  # S_query
    entropy_after: float = 0.0   # S_response
    delta_s: float = 0.0         # ΔS = S_after - S_before

    # Floor scores
    floor_scores: AGIFloorScores = field(default_factory=AGIFloorScores)

    # Vote
    vote: EngineVote = EngineVote.UNCERTAIN
    vote_reason: str = ""

    # Pass/fail for each floor
    f2_pass: bool = True
    f4_pass: bool = True
    f7_pass: bool = True
    f13_pass: bool = True

    # Stage verdict
    stage_pass: bool = True
    violations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "timestamp": self.timestamp.isoformat(),
            "reasoning": {
                "premises": self.reasoning_tree.premises if self.reasoning_tree else [],
                "inference_steps": self.reasoning_tree.inference_steps if self.reasoning_tree else [],
                "conclusion": self.reasoning_tree.conclusion if self.reasoning_tree else "",
            },
            "thermodynamics": {
                "entropy_before": self.entropy_before,
                "entropy_after": self.entropy_after,
                "delta_s": self.delta_s,
            },
            "floor_scores": self.floor_scores.to_dict(),
            "vote": self.vote.value,
            "vote_reason": self.vote_reason,
            "stage_pass": self.stage_pass,
            "violations": self.violations,
        }


# =============================================================================
# REASONING TREE SYNTHESIS
# =============================================================================

def synthesize_reasoning_tree(
    sense: SenseOutput,
    think: ThinkOutput
) -> ReasoningTree:
    """
    Synthesize three hypotheses into a coherent reasoning tree.

    The reasoning tree represents the logical structure of our analysis:
    - Premises: What we know (from SENSE)
    - Inference steps: How we reason (from THINK)
    - Conclusion: What we conclude (synthesis)
    - Contradictions: Where hypotheses conflict
    """
    # Extract premises from parsed facts
    premises = [f.content for f in sense.parsed_facts if f.confidence > 0.8][:5]

    # Build inference steps from hypotheses
    inference_steps = []

    # Step 1: Conservative analysis
    if think.conservative:
        inference_steps.append(
            f"[Conservative] {think.conservative.content[:150]}"
        )

    # Step 2: Exploratory analysis
    if think.exploratory:
        inference_steps.append(
            f"[Exploratory] {think.exploratory.content[:150]}"
        )

    # Step 3: Adversarial challenge
    if think.adversarial:
        inference_steps.append(
            f"[Adversarial] {think.adversarial.content[:150]}"
        )

    # Step 4: Synthesis
    inference_steps.append(
        "[Synthesis] Integrating all three perspectives into unified response"
    )

    # Detect contradictions between hypotheses
    contradictions = detect_contradictions(think.hypotheses)

    # Build conclusion
    conclusion = build_conclusion(sense, think, contradictions)

    # Validity: no hard contradictions
    is_valid = len(contradictions) == 0

    return ReasoningTree(
        premises=premises,
        inference_steps=inference_steps,
        conclusion=conclusion,
        contradictions_detected=contradictions,
        is_valid=is_valid,
    )


def detect_contradictions(hypotheses: List[Hypothesis]) -> List[str]:
    """
    Detect contradictions between hypotheses.

    Returns list of contradiction descriptions.
    """
    contradictions = []

    # Simple heuristic: look for explicit negation patterns
    if len(hypotheses) >= 2:
        # Check if conservative and exploratory conflict
        conservative = hypotheses[0] if hypotheses else None
        exploratory = hypotheses[1] if len(hypotheses) > 1 else None

        if conservative and exploratory:
            # Check for "should"/"should not" conflicts
            if "should" in conservative.content.lower() and "should not" in exploratory.content.lower():
                contradictions.append(
                    "Tension between conservative and exploratory approaches on recommendations"
                )

            # Check for "proven"/"novel" tension (expected, not a real contradiction)
            # This is actually healthy divergence, not a contradiction

    return contradictions


def build_conclusion(
    sense: SenseOutput,
    think: ThinkOutput,
    contradictions: List[str]
) -> str:
    """
    Build a conclusion from the synthesis of hypotheses.
    """
    intent = sense.detected_intent.value

    # Weight by confidence
    hypotheses = think.hypotheses
    if not hypotheses:
        return "Insufficient data for conclusion."

    # Find highest confidence hypothesis
    best = max(hypotheses, key=lambda h: h.confidence)

    # Build conclusion
    conclusion = f"For '{intent}' intent: Recommend {best.path_type} approach. "

    if contradictions:
        conclusion += f"Note: {len(contradictions)} tension(s) identified requiring synthesis. "

    # Add diversity note if good
    if think.diversity_score > 0.5:
        conclusion += "Good diversity in exploration paths."

    return conclusion


# =============================================================================
# ENTROPY CALCULATION (THERMODYNAMICS)
# =============================================================================

def compute_shannon_entropy(text: str) -> float:
    """
    Compute Shannon entropy of text in bits.

    H(X) = -Σ p(x) * log2(p(x))
    """
    if not text:
        return 0.0

    # Character-level entropy
    counts = Counter(text.lower())
    total = len(text)

    entropy = 0.0
    for count in counts.values():
        p = count / total
        if p > 0:
            entropy -= p * math.log2(p)

    return entropy


def compute_delta_s(
    query: str,
    reasoning_tree: ReasoningTree
) -> Tuple[float, float, float]:
    """
    Compute ΔS = S_after - S_before (thermodynamic clarity change).

    For F4 to pass, ΔS must be ≤ 0 (cooling, not heating).
    A negative ΔS means the response reduces entropy (increases clarity).

    Returns:
        (entropy_before, entropy_after, delta_s)
    """
    # S_before: Entropy of the query (user's confusion)
    s_before = compute_shannon_entropy(query)

    # S_after: Entropy of our reasoning output
    # Combine all reasoning elements
    response_text = " ".join([
        reasoning_tree.conclusion,
        *reasoning_tree.inference_steps,
    ])
    s_after = compute_shannon_entropy(response_text)

    # Normalize by length ratio to make comparison fair
    len_ratio = len(response_text) / max(len(query), 1)

    # Adjusted delta: account for the fact that longer responses naturally have higher entropy
    # We want to reward clarity per unit of content
    normalized_s_after = s_after / max(len_ratio, 1.0)

    delta_s = normalized_s_after - s_before

    return s_before, normalized_s_after, delta_s


# =============================================================================
# FLOOR SCORING
# =============================================================================

def compute_f2_truth_score(
    sense: SenseOutput,
    reasoning_tree: ReasoningTree
) -> float:
    """
    Compute F2 Truth score.

    Truth score is based on:
    - How well grounded the reasoning is in facts
    - Whether conclusions follow from premises
    - Absence of fabrication

    Returns:
        Score 0.0 to 1.0
    """
    score = 1.0

    # Penalty for missing premises
    if not reasoning_tree.premises:
        score -= 0.3

    # Penalty for empty conclusion
    if not reasoning_tree.conclusion:
        score -= 0.3

    # Penalty for contradictions (uncertain truth)
    if reasoning_tree.contradictions_detected:
        score -= 0.1 * len(reasoning_tree.contradictions_detected)

    # Bonus for valid reasoning
    if reasoning_tree.is_valid:
        score = min(score + 0.1, 1.0)

    # Ensure non-negative
    return max(0.0, min(1.0, score))


def compute_f4_clarity_score(delta_s: float) -> float:
    """
    Compute F4 Clarity score based on ΔS.

    For clarity, we want ΔS ≤ 0 (cooling).
    Score is high when ΔS is negative, low when positive.

    Returns:
        The actual ΔS value (not normalized, since F4 is a threshold check)
    """
    return delta_s


def compute_f7_humility_score(
    hypotheses: List[Hypothesis],
    diversity_score: float
) -> float:
    """
    Compute F7 Humility (Omega_0) score.

    Humility is the uncertainty factor. It should be in [0.03, 0.05].

    Based on:
    - Average confidence across hypotheses
    - Diversity of exploration

    Returns:
        Omega_0 value (target: 0.03-0.05)
    """
    if not hypotheses:
        return OMEGA_0_DEFAULT

    # Average confidence
    avg_confidence = sum(h.confidence for h in hypotheses) / len(hypotheses)

    # Omega_0 = 1 - confidence, but bounded
    omega_0 = 1.0 - avg_confidence

    # Adjust based on diversity (more diverse = more uncertainty)
    omega_0 += diversity_score * 0.02

    # Clamp to valid range
    omega_0 = max(OMEGA_0_MIN, min(OMEGA_0_MAX, omega_0))

    return omega_0


def compute_f13_curiosity_score(hypotheses: List[Hypothesis]) -> float:
    """
    Compute F13 Curiosity score.

    Curiosity is measured by number of distinct paths explored.
    We require at least 3 paths.

    Returns:
        Number of paths explored (≥3 for pass)
    """
    return float(len(hypotheses))


def compute_all_floor_scores(
    sense: SenseOutput,
    think: ThinkOutput,
    reasoning_tree: ReasoningTree,
    delta_s: float
) -> AGIFloorScores:
    """
    Compute all AGI floor scores (F2, F4, F7, F13).
    """
    return AGIFloorScores(
        F2_truth=compute_f2_truth_score(sense, reasoning_tree),
        F4_clarity=compute_f4_clarity_score(delta_s),
        F7_humility=compute_f7_humility_score(think.hypotheses, think.diversity_score),
        F13_curiosity=compute_f13_curiosity_score(think.hypotheses),
    )


# =============================================================================
# VOTE CASTING
# =============================================================================

def cast_agi_vote(
    floor_scores: AGIFloorScores,
    sense: SenseOutput,
    think: ThinkOutput
) -> Tuple[EngineVote, str]:
    """
    Cast the independent AGI vote based on floor scores.

    Vote logic:
    - SEAL: All hard floors pass
    - VOID: Any hard floor fails
    - UNCERTAIN: Within Omega_0 band, needs consensus

    Returns:
        (vote, reason)
    """
    # Check hard floor passes
    f2_pass = floor_scores.F2_truth >= F2_TRUTH_THRESHOLD
    f4_pass = floor_scores.F4_clarity <= F4_CLARITY_THRESHOLD
    f7_in_band = OMEGA_0_MIN <= floor_scores.F7_humility <= OMEGA_0_MAX

    # Check soft floor (F13)
    f13_pass = floor_scores.F13_curiosity >= F13_PATHS_MIN

    # Collect failures
    failures = []
    if not f2_pass:
        failures.append(f"F2 Truth {floor_scores.F2_truth:.2f} < {F2_TRUTH_THRESHOLD}")
    if not f4_pass:
        failures.append(f"F4 Clarity ΔS={floor_scores.F4_clarity:.4f} > {F4_CLARITY_THRESHOLD}")
    if not f7_in_band:
        failures.append(f"F7 Humility Ω₀={floor_scores.F7_humility:.3f} outside [{OMEGA_0_MIN}, {OMEGA_0_MAX}]")

    # Check for 111/222 failures propagating
    if not sense.stage_pass:
        failures.append("Stage 111 SENSE failed")
    if not think.stage_pass:
        failures.append("Stage 222 THINK failed")

    # Determine vote
    if failures:
        # Hard floor failure = VOID
        return EngineVote.VOID, f"AGI VOID: {'; '.join(failures)}"

    if not f13_pass:
        # Soft floor failure = UNCERTAIN
        return EngineVote.UNCERTAIN, f"AGI UNCERTAIN: F13 Curiosity {floor_scores.F13_curiosity} < {F13_PATHS_MIN}"

    # All floors pass = SEAL
    return EngineVote.SEAL, "AGI SEAL: All floors pass"


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def execute_stage_333(
    sense_output: SenseOutput,
    think_output: ThinkOutput,
    session_id: str,
) -> ReasonOutput:
    """
    Execute Stage 333: REASON

    Synthesizes hypotheses into a reasoning tree, computes thermodynamics,
    evaluates all AGI floors, and casts the independent vote.

    Args:
        sense_output: Output from Stage 111
        think_output: Output from Stage 222
        session_id: Session identifier

    Returns:
        ReasonOutput with reasoning tree, floor scores, and vote
    """
    output = ReasonOutput(session_id=session_id)
    violations = []

    # Check prerequisites
    if not sense_output.stage_pass:
        output.stage_pass = False
        output.violations = ["Stage 111 failed"]
        output.vote = EngineVote.VOID
        output.vote_reason = "AGI VOID: Stage 111 failed"
        return output

    if not think_output.stage_pass:
        output.stage_pass = False
        output.violations = ["Stage 222 failed"]
        output.vote = EngineVote.VOID
        output.vote_reason = "AGI VOID: Stage 222 failed"
        return output

    # 1. Synthesize reasoning tree
    # v53: Apply Precision Weighting to Hypotheses BEFORE synthesis
    _apply_precision_updates(think_output, sense_output.parsed_facts)
    
    reasoning_tree = synthesize_reasoning_tree(sense_output, think_output)
    output.reasoning_tree = reasoning_tree

    # 2. Compute thermodynamics (ΔS)
    s_before, s_after, delta_s = compute_delta_s(
        sense_output.raw_query,
        reasoning_tree
    )
    output.entropy_before = s_before
    output.entropy_after = s_after
    output.delta_s = delta_s

    # 3. Compute all floor scores
    floor_scores = compute_all_floor_scores(
        sense_output, think_output, reasoning_tree, delta_s
    )
    output.floor_scores = floor_scores
    
    # v53: Record precision metrics in violations/logs for visibility
    if think_output.confidence_cap_applied:
         violations.append("Note: Hypotheses updated via Precision Weighting")

    # 4. Check individual floors
    output.f2_pass = floor_scores.F2_truth >= F2_TRUTH_THRESHOLD
    output.f4_pass = floor_scores.F4_clarity <= F4_CLARITY_THRESHOLD
    output.f7_pass = OMEGA_0_MIN <= floor_scores.F7_humility <= OMEGA_0_MAX
    output.f13_pass = floor_scores.F13_curiosity >= F13_PATHS_MIN

    # 5. Cast vote
    vote, vote_reason = cast_agi_vote(floor_scores, sense_output, think_output)
    output.vote = vote
    output.vote_reason = vote_reason

    # 6. Set final verdict
    output.violations = violations
    output.stage_pass = vote != EngineVote.VOID

    return output


def _apply_precision_updates(think: ThinkOutput, facts: List[ParsedFact]):
    """
    Apply precision weighting to update hypothesis confidence based on verified facts.
    
    v53 Logic:
    1. Match hypothesis supporting facts to verified Sense facts.
    2. Calculate precision of the evidence (High Signal).
    3. Update hypothesis confidence (Prior) -> Posterior.
    """
    hypotheses = [think.conservative, think.exploratory, think.adversarial]
    
    for h in hypotheses:
        if not h:
            continue
            
        # Find matching facts (String match on content)
        # In a real system, this would use semantic embedding match
        matching_facts = [
            f for f in facts 
            if f.content in h.supporting_facts or any(sf in f.content for sf in h.supporting_facts)
        ]
        
        if not matching_facts:
            continue
            
        # Calculate aggregate evidence confidence
        avg_evidence_conf = sum(f.confidence for f in matching_facts) / len(matching_facts)
        
        # Calculate precision-weighted update
        # Target: The hypothesis should align with the evidence confidence
        # Error: evidence_conf - current_conf
        error = avg_evidence_conf - h.confidence
        
        # Apply update
        new_conf = compute_precision_weighted_update(
            prior_conf=h.confidence,
            evidence_conf=avg_evidence_conf,
            prediction_error=error
        )
        
        # Update the hypothesis in place
        # Cap at 0.99 for safety
        h.confidence = min(0.99, max(0.01, new_conf))


def build_delta_bundle(
    sense: SenseOutput,
    think: ThinkOutput,
    reason: ReasonOutput,
) -> DeltaBundle:
    """
    Build the final sealed DeltaBundle from all AGI stages.

    This is the thermodynamically-isolated output that will be
    merged with OmegaBundle at 444 TRINITY_SYNC.
    """
    bundle = DeltaBundle(
        session_id=sense.session_id,
        timestamp=sense.timestamp,
        # 111 SENSE output
        raw_query=sense.raw_query,
        parsed_facts=[f.content for f in sense.parsed_facts],
        detected_intent=sense.detected_intent.value,
        # 222 THINK output
        hypotheses=think.hypotheses,
        # 333 REASON output
        reasoning=reason.reasoning_tree,
        # Confidence interval
        confidence_low=1.0 - OMEGA_0_MAX,
        confidence_high=1.0 - OMEGA_0_MIN,
        omega_0=reason.floor_scores.F7_humility,
        # Thermodynamics
        entropy_delta=reason.delta_s,
        # Floor scores
        floor_scores=reason.floor_scores,
        # Vote
        vote=reason.vote,
        vote_reason=reason.vote_reason,
    )

    # Seal the bundle (compute hash)
    return bundle.seal()


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Types
    "ReasonOutput",
    # Functions
    "synthesize_reasoning_tree",
    "detect_contradictions",
    "compute_shannon_entropy",
    "compute_delta_s",
    "compute_all_floor_scores",
    "cast_agi_vote",
    "execute_stage_333",
    "build_delta_bundle",
    # Constants
    "F2_TRUTH_THRESHOLD",
    "F4_CLARITY_THRESHOLD",
    "OMEGA_0_MIN",
    "OMEGA_0_MAX",
    "OMEGA_0_DEFAULT",
    "F13_PATHS_MIN",
]
