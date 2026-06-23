"""
AR-QOCF Rubric — Action-Reflection Quality, Originality, Craft, Functionality

Four-axis scoring rubric for constitutional judgment quality.
Called by the judge before issuing SEAL. All axes >= 0.65 required.

DITEMPA BUKAN DIBERI — Quality is forged, not given.
"""

from __future__ import annotations

from typing import Any

# ── Axis weight defaults (per Reality Engineering §16) ──
AXIS_WEIGHTS = {
    "quality": 0.30,  # Q: Reasoning soundness, evidence grounding
    "originality": 0.15,  # O: Novel insight, non-obvious solution
    "craft": 0.25,  # C: Implementation quality, structural integrity
    "functionality": 0.30,  # F: Does it work? Does it satisfy the intent?
}

# ── Floor thresholds (all axes must meet this to SEAL) ──
AXIS_FLOOR = 0.65
AGGREGATE_FLOOR = 0.70


def score_quality(
    evidence_count: int = 0,
    contradiction_free: bool = True,
    confidence: float = 0.5,
    has_sources: bool = False,
) -> float:
    """Q: Reasoning soundness and evidence grounding.

    Factors:
      - evidence_count / 5 (capped at 1.0): more evidence = higher quality
      - contradiction_free: 1.0 if clean, 0.3 if contradictions found
      - confidence: raw confidence value (capped at 1.0)
      - has_sources: 1.0 if sources cited, 0.5 if not

    Returns float in [0.0, 1.0].
    """
    evidence_score = min(1.0, evidence_count / 5.0)
    contradiction_score = 1.0 if contradiction_free else 0.3
    confidence_score = min(1.0, confidence)
    source_score = 1.0 if has_sources else 0.5

    return (
        0.35 * evidence_score
        + 0.25 * contradiction_score
        + 0.25 * confidence_score
        + 0.15 * source_score
    )


def score_originality(
    novel_insight: bool = False,
    non_obvious: bool = False,
    reuse_count: int = 0,
    domain_shift: bool = False,
) -> float:
    """O: Novel insight and non-obvious solution.

    Factors:
      - novel_insight: 1.0 if genuinely new, 0.5 if incremental, 0.2 if routine
      - non_obvious: 1.0 if surprising, 0.5 if expected
      - reuse_count: how many times this pattern has been used (penalty)
      - domain_shift: 1.0 if cross-domain, 0.5 if same-domain

    Returns float in [0.0, 1.0].
    """
    insight_score = 1.0 if novel_insight else (0.5 if non_obvious else 0.2)
    obviousness_score = 1.0 if non_obvious else 0.5
    reuse_penalty = max(0.0, 1.0 - reuse_count * 0.15)
    shift_score = 1.0 if domain_shift else 0.5

    return (
        0.35 * insight_score + 0.25 * obviousness_score + 0.15 * reuse_penalty + 0.25 * shift_score
    )


def score_craft(
    has_tests: bool = False,
    has_error_handling: bool = False,
    structural_integrity: float = 0.7,
    documentation: bool = False,
) -> float:
    """C: Implementation quality and structural integrity.

    Factors:
      - has_tests: 1.0 if tests exist, 0.3 if not
      - has_error_handling: 1.0 if errors handled, 0.4 if not
      - structural_integrity: raw score (0.0-1.0)
      - documentation: 1.0 if documented, 0.5 if minimal, 0.2 if none

    Returns float in [0.0, 1.0].
    """
    test_score = 1.0 if has_tests else 0.3
    error_score = 1.0 if has_error_handling else 0.4
    structure_score = max(0.0, min(1.0, structural_integrity))
    doc_score = 1.0 if documentation else 0.5

    return 0.30 * test_score + 0.20 * error_score + 0.30 * structure_score + 0.20 * doc_score


def score_functionality(
    verified_working: bool = False,
    satisfies_intent: bool = False,
    reversibility_known: bool = False,
    blast_radius_assessed: bool = False,
) -> float:
    """F: Does it work? Does it satisfy the intent?

    Factors:
      - verified_working: 1.0 if verified, 0.3 if not
      - satisfies_intent: 1.0 if intent met, 0.4 if partial, 0.1 if missed
      - reversibility_known: 1.0 if classified, 0.5 if unknown
      - blast_radius_assessed: 1.0 if assessed, 0.5 if not

    Returns float in [0.0, 1.0].
    """
    verified_score = 1.0 if verified_working else 0.3
    intent_score = 1.0 if satisfies_intent else 0.4
    reversibility_score = 1.0 if reversibility_known else 0.5
    blast_score = 1.0 if blast_radius_assessed else 0.5

    return (
        0.35 * verified_score
        + 0.30 * intent_score
        + 0.20 * reversibility_score
        + 0.15 * blast_score
    )


def compute_rubric(
    *,
    # Quality
    evidence_count: int = 0,
    contradiction_free: bool = True,
    confidence: float = 0.5,
    has_sources: bool = False,
    # Originality
    novel_insight: bool = False,
    non_obvious: bool = False,
    reuse_count: int = 0,
    domain_shift: bool = False,
    # Craft
    has_tests: bool = False,
    has_error_handling: bool = False,
    structural_integrity: float = 0.7,
    documentation: bool = False,
    # Functionality
    verified_working: bool = False,
    satisfies_intent: bool = False,
    reversibility_known: bool = True,
    blast_radius_assessed: bool = True,
) -> dict[str, Any]:
    """Compute the full AR-QOCF rubric and return verdict.

    Returns dict with:
      - axes: {quality, originality, craft, functionality} scores
      - aggregate: weighted sum
      - passed: True if all axes >= AXIS_FLOOR and aggregate >= AGGREGATE_FLOOR
      - failing_axes: list of axes below floor
      - verdict: "SEAL" if passed, "VOID" if failed
    """
    q = score_quality(evidence_count, contradiction_free, confidence, has_sources)
    o = score_originality(novel_insight, non_obvious, reuse_count, domain_shift)
    c = score_craft(has_tests, has_error_handling, structural_integrity, documentation)
    f_val = score_functionality(
        verified_working, satisfies_intent, reversibility_known, blast_radius_assessed
    )

    axes = {
        "quality": round(q, 3),
        "originality": round(o, 3),
        "craft": round(c, 3),
        "functionality": round(f_val, 3),
    }

    aggregate = (
        AXIS_WEIGHTS["quality"] * q
        + AXIS_WEIGHTS["originality"] * o
        + AXIS_WEIGHTS["craft"] * c
        + AXIS_WEIGHTS["functionality"] * f_val
    )

    failing_axes = [name for name, score in axes.items() if score < AXIS_FLOOR]
    passed = len(failing_axes) == 0 and aggregate >= AGGREGATE_FLOOR

    return {
        "axes": axes,
        "aggregate": round(aggregate, 3),
        "passed": passed,
        "failing_axes": failing_axes,
        "verdict": "SEAL" if passed else "VOID",
        "axis_floor": AXIS_FLOOR,
        "aggregate_floor": AGGREGATE_FLOOR,
        "weights": AXIS_WEIGHTS,
    }
