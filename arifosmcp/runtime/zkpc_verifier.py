"""
arifosmcp/runtime/zkpc_verifier.py
═══════════════════════════════════════════════════════════════════════════════
EUREKA 2: ZKPC Verifier (Zero-Knowledge Proof of Context)

Verifies a context claim against evidence across 7 dimensions.

Each dimension scores 0.0–1.0 based on the presence and quality of evidence.
PASS requires ALL dimensions >= 0.7.

Dimensions:
  - wound_architecture:    Claimant's scar/shadow/history
  - paradox_tolerance:     Ability to hold contradictory truths
  - moral_architecture:    Ethical framework consistency
  - language_register:     Language use matches claimed context
  - sovereign_intent:      Intent traces to human sovereign
  - godel_lock:            System + human awareness co-present
  - anti_behavior_sink:    Refusal to optimise for predictability

Constitutional Floors: F2 (TRUTH), F7 (Humility)

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

DIMENSIONS: list[str] = [
    "wound_architecture",
    "paradox_tolerance",
    "moral_architecture",
    "language_register",
    "sovereign_intent",
    "godel_lock",
    "anti_behavior_sink",
]

PASS_THRESHOLD: float = 0.7


def _score_dimension(dim: str, context_claim: dict, evidence: dict) -> float:
    """
    Score a single ZKPC dimension 0.0–1.0 based on available evidence.

    Strategy:
      - If the evidence dict contains a top-level key matching the dimension,
        its numeric value (0.0–1.0) is taken directly.
      - Otherwise, sub-keys and string-quality heuristics are used.

    This is a reference implementation; production deployments may substitute
    a crypto-accumulator or ML-based scorer.
    """
    # Direct numeric score from evidence
    ev = evidence.get(dim)
    if isinstance(ev, (int, float)) and 0.0 <= ev <= 1.0:
        return float(ev)

    # Structured evidence sub-dict — average of numeric sub-fields
    if isinstance(ev, dict):
        scores = [v for v in ev.values() if isinstance(v, (int, float)) and 0.0 <= v <= 1.0]
        if scores:
            return sum(scores) / len(scores)

    # String evidence — heuristic: longer, more detailed strings score higher
    if isinstance(ev, str) and ev.strip():
        length_score = min(len(ev.strip()) / 500.0, 0.6)
        return length_score

    # Claim-level fallback: if the context_claim mentions this dimension,
    # give a modest baseline (0.3) so partial claims are visible but below PASS
    claim_val = context_claim.get(dim)
    if claim_val is not None:
        if isinstance(claim_val, str) and len(claim_val.strip()) > 10:
            return 0.3
        if isinstance(claim_val, (int, float)) and 0.0 <= claim_val <= 1.0:
            return float(claim_val) * 0.4
        return 0.2

    # No evidence at all
    return 0.0


def verify_zkpc(
    context_claim: dict,
    evidence: dict,
) -> tuple[bool, dict[str, float]]:
    """
    Verify a context claim against evidence across 7 ZKPC dimensions.

    Parameters
    ----------
    context_claim : dict
        The context claim being asserted. May contain dimension-specific
        fields that act as a fallback when evidence is absent.
    evidence : dict
        Evidence payload. May contain:
        - Top-level keys matching dimension names with 0.0–1.0 scores, or
        - Sub-dicts of per-dimension evidence, or
        - Free-form text strings.

    Returns
    -------
    tuple[bool, dict[str, float]]
        ``(True, {dim: score, ...})`` if **all** dimensions >= 0.7, else
        ``(False, {dim: score, ...})`` with the per-dimension breakdown.
    """
    scores: dict[str, float] = {}

    for dim in DIMENSIONS:
        scores[dim] = _score_dimension(dim, context_claim, evidence)

    passed = all(v >= PASS_THRESHOLD for v in scores.values())
    return (passed, scores)
