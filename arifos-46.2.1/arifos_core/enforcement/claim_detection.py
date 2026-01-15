"""
Claim detection using structural signals (Physics > Semantics).
v45Ω Patch A: No-Claim Mode for phatic communication.

DITEMPA BUKAN DIBERI — Forged, not given; truth must cool before it rules.
"""

import re
from typing import Dict, Any, List


def extract_claim_profile(response: str) -> Dict[str, Any]:
    """
    Detect factual claims using structural/physical signals.

    Args:
        response: The LLM response text to analyze

    Returns:
        claim_profile dict with:
        - claim_count: Number of factual assertions detected
        - entity_density: Named entities per 100 chars
        - numeric_density: Numbers/dates per 100 chars
        - evidence_ratio: Citations/hedges per claim
        - claim_types: ["IDENTITY", "TEMPORAL", "QUANTITATIVE", ...]
        - has_claims: Quick flag for whether any claims present

    Physics > Semantics:
        Uses structural signals (capitalization, numbers, punctuation)
        rather than semantic keyword matching.
    """
    text = response.strip()
    text_len = len(text)

    # Empty response = no claims
    if text_len == 0:
        return _empty_profile()

    # Structural signals
    entities = _extract_entities(text)
    numbers = _extract_numeric_patterns(text)
    assertions = _count_assertions(text)
    evidence_markers = _count_evidence_markers(text)

    # Compute densities (per 100 chars, normalized)
    entity_density = (len(entities) / max(text_len, 1)) * 100
    numeric_density = (len(numbers) / max(text_len, 1)) * 100

    # Claim count heuristic: assertions + entities + numeric facts
    claim_count = assertions + len(entities) + len(numbers)

    # Evidence ratio (hedges/citations per claim)
    evidence_ratio = evidence_markers / max(claim_count, 1)

    # Claim types
    claim_types = _classify_claim_types(entities, numbers, text)

    # Has claims? Threshold: At least 1 entity OR 1 number OR (>2 assertions AND entity_density > 1.0)
    # Phatic communication (greetings) have short sentences without entities/numbers
    has_claims = (
        len(entities) > 0
        or len(numbers) > 0
        or (assertions > 2 and entity_density > 1.0)
        or entity_density > 2.0
    )

    return {
        "claim_count": claim_count,
        "entity_density": entity_density,
        "numeric_density": numeric_density,
        "evidence_ratio": evidence_ratio,
        "claim_types": claim_types,
        "has_claims": has_claims,
    }


def _extract_entities(text: str) -> List[str]:
    """
    Extract named entity candidates (capitalized sequences).

    Uses structural signal: Capitalization pattern.
    NOT at sentence start to avoid false positives.
    """
    # Pattern 1: Title Case entities (e.g., "Arif Fazil", "arifOS")
    # Not preceded by start-of-string or ". "
    title_case = re.findall(r'(?<!^)(?<!\. )[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*', text)

    # Pattern 2: ALL CAPS entities (e.g., "APEX PRIME")
    # 2+ consecutive uppercase words (avoid single-char abbreviations)
    all_caps = re.findall(r'\b[A-Z]{2,}(?:\s+[A-Z]{2,})*\b', text)

    entities = title_case + all_caps
    return entities


def _extract_numeric_patterns(text: str) -> List[str]:
    """
    Extract numbers, dates, quantities.

    Uses structural signals: Digit patterns, percentage/currency symbols.
    """
    patterns = [
        r'\d{4}-\d{2}-\d{2}',  # ISO dates (YYYY-MM-DD)
        r'\d{1,2}/\d{1,2}/\d{2,4}',  # US dates (MM/DD/YYYY)
        r'\d+\.?\d*%',  # Percentages
        r'\$\d+',  # Currency
        r'\d+',  # Raw numbers
    ]
    numbers = []
    for pattern in patterns:
        numbers.extend(re.findall(pattern, text))
    return numbers


def _count_assertions(text: str) -> int:
    """
    Count declarative sentences (ends with period, not question).

    Uses structural signal: Punctuation pattern (period vs question mark).
    """
    sentences = re.split(r'[.!?]+', text)
    # Filter empty strings and questions
    assertions = [s for s in sentences if s.strip() and not s.strip().endswith('?')]
    return len(assertions)


def _count_evidence_markers(text: str) -> int:
    """
    Count hedges, citations, uncertainty markers.

    Uses structural signals: Specific phrases indicating epistemic caution.
    This is acceptable under Physics > Semantics because these are
    standardized academic/scientific conventions, not arbitrary keywords.
    """
    markers = [
        "according to", "research shows", "studies indicate",
        "likely", "possibly", "probably", "appears",
        "i don't know", "i'm not sure", "unable to verify",
        "cannot verify", "can't verify", "cannot confirm",
    ]
    count = sum(1 for m in markers if m in text.lower())
    return count


def _classify_claim_types(entities: List[str], numbers: List[str], text: str) -> List[str]:
    """
    Classify types of claims present.

    Uses structural signals to categorize claim types:
    - ENTITY: Named entities detected
    - QUANTITATIVE: Numbers/dates present
    - UNIVERSAL: Universal quantifiers detected
    - IDENTITY: "is/was/are/were" + entities (identity claims)
    """
    types = []

    if entities:
        types.append("ENTITY")

    if numbers:
        types.append("QUANTITATIVE")

    # Universal quantifiers (structural: specific high-commitment words)
    if any(w in text.lower() for w in ["always", "never", "all", "none", "every"]):
        types.append("UNIVERSAL")

    # Identity claims (copula + entity)
    if any(w in text.lower() for w in ["is", "was", "are", "were"]) and entities:
        types.append("IDENTITY")

    return types


def _empty_profile() -> Dict[str, Any]:
    """Return empty claim profile for responses with no claims."""
    return {
        "claim_count": 0,
        "entity_density": 0.0,
        "numeric_density": 0.0,
        "evidence_ratio": 0.0,
        "claim_types": [],
        "has_claims": False,
    }
