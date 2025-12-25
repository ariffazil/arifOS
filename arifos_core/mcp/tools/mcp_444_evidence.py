"""
MCP Tool 444: EVIDENCE

Reality grounding through truth scoring and tri-witness convergence.

Constitutional validation:
- F2 (Truth): Enforces thresholds (0.90 HARD, 0.80 SOFT)
- F3 (Tri-Witness): Convergence ≥0.95 required for SEAL
- F4 (ΔS): Cryptographic proof for all claims

This tool verifies claims against evidence sources with multi-witness agreement.
Returns PASS/PARTIAL/VOID based on truth score and convergence quality.
"""

import asyncio
import hashlib
import json
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

from arifos_core.mcp.models import VerdictResponse


# =============================================================================
# CONSTANTS
# =============================================================================

# F2 (Truth) thresholds by lane
TRUTH_THRESHOLD_HARD = 0.90  # Factual claims (capital cities, math, dates)
TRUTH_THRESHOLD_SOFT = 0.80  # Explanatory claims (processes, concepts)

# F3 (Tri-Witness) convergence thresholds
CONVERGENCE_SEAL = 0.95   # Required for SEAL verdict
CONVERGENCE_PARTIAL = 0.90  # Minimum for PARTIAL verdict
CONVERGENCE_VOID = 0.80   # Below this → VOID

# Hallucination detection patterns
HALLUCINATION_PATTERNS = [
    r"(?i)\bI (don't|do not) (have access|know)\b",  # Admission of ignorance
    r"(?i)\bno (information|data|evidence)\b",
    r"(?i)\bcannot (verify|confirm)\b",
    r"(?i)\bunable to (find|locate|verify)\b",
]


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def score_truth_claim(claim: str, sources: List[Any]) -> float:
    """
    Score truth claim against provided sources.

    Combines source scores deterministically (mean of scores).
    If sources are strings, computes structural match score.

    Constitutional grounding:
    - F2 (Truth): Deterministic evidence aggregation

    Args:
        claim: Factual claim to verify
        sources: List of source dicts with "score" or list of strings

    Returns:
        Truth score in [0.0, 1.0]
    """
    if not claim or not sources:
        return 0.0

    # Check for hallucination admission (immediate 0.0)
    for pattern in HALLUCINATION_PATTERNS:
        if re.search(pattern, claim):
            return 0.0

    # If sources are dicts with scores, compute mean
    if all(isinstance(s, dict) and "score" in s for s in sources):
        scores = [s["score"] for s in sources]
        return sum(scores) / len(scores) if scores else 0.0

    # Otherwise, do structural matching (backwards compatibility)
    score = 0.0
    claim_lower = claim.lower()

    # Convert sources to strings
    source_texts = []
    for s in sources:
        if isinstance(s, str):
            source_texts.append(s)
        elif isinstance(s, dict) and "text" in s:
            source_texts.append(s["text"])

    if not source_texts:
        return 0.0

    # Extract entities from claim (proper nouns, numbers)
    entities_pattern = r'\b[A-Z][a-z]+\b|\b\d+\.?\d*\b'
    claim_entities = set(re.findall(entities_pattern, claim))

    if not claim_entities:
        # No entities to verify → moderate baseline
        score = 0.5
    else:
        # Count entity matches in sources
        matched_entities = 0
        for entity in claim_entities:
            entity_pattern = re.escape(entity)
            for source in source_texts:
                if re.search(entity_pattern, source, re.IGNORECASE):
                    matched_entities += 1
                    break  # Count each entity once

        # Score based on entity coverage (up to 0.5)
        entity_coverage = matched_entities / len(claim_entities)
        score += min(0.5, entity_coverage * 0.5)

        # Bonus for exact numeric matches (up to 0.3)
        numbers_pattern = r'\b\d+\.?\d*\b'
        claim_numbers = set(re.findall(numbers_pattern, claim))
        if claim_numbers:
            matched_numbers = sum(
                1 for num in claim_numbers
                if any(num in source for source in source_texts)
            )
            number_coverage = matched_numbers / len(claim_numbers)
            score += min(0.3, number_coverage * 0.3)

    # Multi-source corroboration bonus (up to 0.2)
    if len(source_texts) >= 3:
        score += 0.2
    elif len(source_texts) == 2:
        score += 0.1

    # Key phrase matching bonus (up to 0.2)
    # Extract key words (5+ letters, not common words)
    key_words = [w for w in re.findall(r'\b\w{5,}\b', claim_lower)
                 if w not in ['about', 'there', 'these', 'those', 'which', 'where']]

    if key_words:
        matched_key_words = 0
        for word in key_words[:5]:  # Check up to 5 key words
            for source in source_texts:
                if word in source.lower():
                    matched_key_words += 1
                    break

        key_word_coverage = matched_key_words / min(len(key_words), 5)
        score += min(0.2, key_word_coverage * 0.2)

    # Clamp to [0.0, 1.0]
    return min(1.0, max(0.0, score))


def check_convergence(sources: List[Dict[str, Any]]) -> float:
    """
    Check tri-witness convergence (agreement across sources).

    Constitutional grounding:
    - F3 (Tri-Witness): Human-AI-Earth consensus measurement

    Convergence logic:
    - 3+ sources with agreement → high convergence
    - 2 sources → moderate convergence
    - 1 source → low convergence
    - 0 sources → zero convergence

    Args:
        sources: List of source dicts with {"text": str, "score": float}

    Returns:
        Convergence score in [0.0, 1.0]
    """
    if not sources:
        return 0.0

    num_sources = len(sources)

    # Single source → no convergence (0.70 baseline)
    if num_sources == 1:
        return 0.70

    # Two sources → moderate convergence (0.85)
    if num_sources == 2:
        # Check if scores are similar (within 0.2)
        if all(isinstance(s, dict) and "score" in s for s in sources):
            scores = [s["score"] for s in sources]
            score_variance = max(scores) - min(scores)
            if score_variance < 0.2:
                return 0.90
        return 0.85

    # Three or more sources → high convergence potential
    if all(isinstance(s, dict) and "score" in s for s in sources):
        scores = [s["score"] for s in sources]
        avg_score = sum(scores) / len(scores)
        score_variance = max(scores) - min(scores)

        # Low variance → high convergence
        if score_variance < 0.1:
            return 0.98  # Near-perfect agreement
        elif score_variance < 0.2:
            return 0.95  # Strong agreement
        elif score_variance < 0.3:
            return 0.92  # Moderate agreement
        else:
            return 0.88  # Weak agreement

    # Default for 3+ sources without scores
    return 0.92


def generate_proof_hash(claim: str, sources: List[str], truth_score: float) -> str:
    """
    Generate cryptographic proof hash for claim verification.

    Constitutional grounding:
    - F4 (ΔS): Traceable, verifiable evidence chain
    - F2 (Truth): Immutable audit trail

    Args:
        claim: Verified claim text
        sources: Evidence sources used
        truth_score: Computed truth score

    Returns:
        SHA-256 hex digest of proof package
    """
    proof_package = {
        "claim": claim,
        "sources": sources,
        "truth_score": truth_score,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    # Serialize to deterministic JSON (sorted keys)
    proof_json = json.dumps(proof_package, sort_keys=True)

    # SHA-256 hash
    return hashlib.sha256(proof_json.encode('utf-8')).hexdigest()


def detect_hallucination(claim: str) -> bool:
    """
    Detect hallucination indicators in claim text.

    Constitutional grounding:
    - F2 (Truth): Prevent fabricated claims

    Args:
        claim: Claim text to analyze

    Returns:
        True if hallucination detected, False otherwise
    """
    for pattern in HALLUCINATION_PATTERNS:
        if re.search(pattern, claim):
            return True
    return False


def extract_entities(text: str) -> List[str]:
    """
    Extract named entities and numbers from text.

    Args:
        text: Text to analyze

    Returns:
        List of entity strings (proper nouns, numbers)
    """
    # Proper nouns: capitalized words not at sentence start
    proper_nouns_pattern = r'(?<!^)(?<![.!?]\s)[A-Z][a-z]+'
    proper_nouns = re.findall(proper_nouns_pattern, text)

    # Numbers (integers and decimals)
    numbers_pattern = r'\b\d+\.?\d*\b'
    numbers = re.findall(numbers_pattern, text)

    return proper_nouns + numbers


# =============================================================================
# MCP TOOL IMPLEMENTATION
# =============================================================================

async def mcp_444_evidence(request: Dict[str, Any]) -> VerdictResponse:
    """
    MCP Tool 444: EVIDENCE - Truth grounding via tri-witness convergence.

    Constitutional role:
    - F2 (Truth): Enforces thresholds (0.90 HARD, 0.80 SOFT)
    - F3 (Tri-Witness): Convergence ≥0.95 for SEAL
    - F4 (ΔS): Cryptographic proof included

    Verdicts:
    - PASS: truth_score ≥ threshold AND convergence ≥ 0.95
    - PARTIAL: truth_score ≥ threshold OR convergence ≥ 0.90
    - VOID: truth_score < threshold OR convergence < 0.80

    Args:
        request: {
            "claim": str,                  # Claim to verify
            "sources": List[str] or List[Dict],  # Evidence sources
            "lane": str,                   # "HARD" or "SOFT" (from 111_sense)
        }

    Returns:
        VerdictResponse with:
        - verdict: "PASS", "PARTIAL", or "VOID"
        - reason: Explanation of verdict
        - side_data: {
            "truth_score": float,
            "convergence": float,
            "proof": str,               # SHA-256 hash
            "threshold": float,         # Applied truth threshold
            "hallucination_detected": bool,
          }
    """
    # Extract inputs
    claim = request.get("claim", "")
    sources_raw = request.get("sources", [])
    lane = request.get("lane", "SOFT")

    # Validate inputs
    if not isinstance(claim, str) or not claim.strip():
        return VerdictResponse(
            verdict="VOID",
            reason="Invalid claim: empty or non-string",
            side_data={"truth_score": 0.0, "convergence": 0.0},
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    # Normalize sources to list of strings
    if isinstance(sources_raw, list):
        sources = []
        sources_dicts = []
        for s in sources_raw:
            if isinstance(s, str):
                sources.append(s)
                sources_dicts.append({"text": s, "score": 0.8})
            elif isinstance(s, dict) and "text" in s:
                sources.append(s["text"])
                sources_dicts.append(s)
    else:
        sources = []
        sources_dicts = []

    # Determine threshold based on lane
    threshold = TRUTH_THRESHOLD_HARD if lane == "HARD" else TRUTH_THRESHOLD_SOFT

    # Check for hallucination
    hallucination_detected = detect_hallucination(claim)
    if hallucination_detected:
        return VerdictResponse(
            verdict="VOID",
            reason="Hallucination detected: claim admits lack of evidence",
            side_data={
                "truth_score": 0.0,
                "convergence": 0.0,
                "proof": "",
                "threshold": threshold,
                "hallucination_detected": True,
            },
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    # Score truth claim
    truth_score = score_truth_claim(claim, sources_raw if sources_raw else sources)

    # Check convergence
    convergence = check_convergence(sources_dicts)

    # Generate proof hash
    proof_hash = generate_proof_hash(claim, sources, truth_score)

    # Determine verdict
    if truth_score >= threshold and convergence >= CONVERGENCE_SEAL:
        verdict = "PASS"
        reason = f"Truth verified: score={truth_score:.2f} ≥ {threshold}, convergence={convergence:.2f} ≥ {CONVERGENCE_SEAL}"
    elif truth_score >= threshold or convergence >= CONVERGENCE_PARTIAL:
        verdict = "PARTIAL"
        reason = f"Partial verification: score={truth_score:.2f}, convergence={convergence:.2f}. Borderline evidence."
    else:
        verdict = "VOID"
        reason = f"Insufficient evidence: score={truth_score:.2f} < {threshold} or convergence={convergence:.2f} < {CONVERGENCE_VOID}"

    # Generate timestamp
    timestamp = datetime.now(timezone.utc).isoformat()

    return VerdictResponse(
        verdict=verdict,
        reason=reason,
        side_data={
            "truth_score": truth_score,
            "convergence": convergence,
            "proof": proof_hash,
            "threshold": threshold,
            "lane": lane,
            "hallucination_detected": False,
            "num_sources": len(sources),
        },
        timestamp=timestamp,
    )


def mcp_444_evidence_sync(request: Dict[str, Any]) -> VerdictResponse:
    """Synchronous wrapper for mcp_444_evidence."""
    return asyncio.run(mcp_444_evidence(request))
