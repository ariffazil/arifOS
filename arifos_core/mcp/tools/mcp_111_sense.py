"""
MCP Tool 111: SENSE - Lane Classification & Truth Threshold Determination

Purpose:
    Classify query into lane (HARD/SOFT/PHATIC/REFUSE) using physics-first analysis.
    Determines truth threshold and response path for downstream tools.

Constitutional role:
    F2 (Truth): Sets truth threshold based on query type
    F4 (ΔS): Structural clarity through explicit lane routing
    F9 (Anti-Hantu): Detects constitutional violations early

Input contract:
    {
        "query": str,          # User query to classify
        "context": dict        # Optional context (future use)
    }

Output contract:
    {
        "verdict": "PASS" | "VOID",  # PASS for safe lanes, VOID for REFUSE
        "reason": str,
        "side_data": {
            "lane": "HARD" | "SOFT" | "PHATIC" | "REFUSE",
            "truth_threshold": float,       # 0.90 (HARD), 0.80 (SOFT), 0.0 (PHATIC)
            "confidence": float,            # Classification confidence
            "scope_estimate": str           # Query type label
        }
    }

Lane definitions:
    HARD: Factual queries requiring strict truth (≥0.90)
          Patterns: High entity density, specific questions, numbers/dates
          Example: "What is the capital of France?"

    SOFT: Explanatory queries allowing educational tolerance (≥0.80)
          Patterns: How/why questions, conceptual explanations
          Example: "How does photosynthesis work?"

    PHATIC: Social communication exempt from truth floor
          Patterns: Greetings, pleasantries, low information density
          Example: "Hi, how are you?"

    REFUSE: Constitutional violations (auto-escalate to VOID)
          Patterns: Unauthorized access, harm, credential exposure
          Example: "How do I hack WiFi?"

Phase: 1 (Foundation)
Dependencies: None (atomic)
Next: 333_REASON (generation under constraint)
"""

from datetime import datetime, timezone
from typing import Dict, Any
import re

from ..models import VerdictResponse


# =============================================================================
# CONSTANTS
# =============================================================================

TOOL_NAME = "mcp_111_sense"

# Lane-specific truth thresholds (v45Ω Patch B)
TRUTH_THRESHOLD_HARD = 0.90    # Strict factual precision
TRUTH_THRESHOLD_SOFT = 0.80    # Educational tolerance
TRUTH_THRESHOLD_PHATIC = 0.0   # Truth-exempt

# Constitutional violation patterns (REFUSE lane)
VIOLATION_PATTERNS = {
    "unauthorized_access": [
        r"\bhack\b", r"\bcrack\b", r"\bbypass\b.*\b(security|auth)",
        r"\bexploit\b", r"\bbreak\s+into\b"
    ],
    "credential_exposure": [
        r"\bpassword\b", r"\bapi[_\s]key\b", r"\bsecret\b.*\btoken\b",
        r"\bprivate[_\s]key\b", r"\bcredential"
    ],
    "harm": [
        r"\bdestroy\b", r"\bdamage\b", r"\battack\b", r"\bharm\b",
        r"\binjure\b", r"\bkill\b"
    ],
}

# Phatic patterns (social communication)
PHATIC_PATTERNS = [
    r"^(hi|hello|hey|greetings|good\s+(morning|afternoon|evening))",
    r"(how\s+are\s+you|how's\s+it\s+going|what'?s\s+up)",
    r"^(thanks|thank\s+you|thx|cheers)",
    r"^(bye|goodbye|see\s+you|later)",
]

# Soft lane indicators (explanatory intent)
SOFT_INDICATORS = [
    r"\b(explain|describe|how\s+does|how\s+do|why\s+does|why\s+do)",
    r"\b(what\s+is\s+the\s+difference|compare|contrast)",
    r"\b(tell\s+me\s+about|teach\s+me)",
]


# =============================================================================
# PHYSICS-FIRST CLASSIFICATION
# =============================================================================

def count_entities(text: str) -> int:
    """
    Count entities (proper nouns, numbers, dates).

    Physics-based proxy for information density.
    High entity count → likely HARD lane (factual query).
    """
    # Proper nouns (capitalized words that aren't sentence starts)
    proper_nouns = re.findall(r'(?<!^)(?<![.!?]\s)[A-Z][a-z]+', text)

    # Numbers (integers, floats, percentages)
    numbers = re.findall(r'\b\d+\.?\d*%?\b', text)

    # Dates (rough pattern)
    dates = re.findall(r'\b\d{4}\b|\b\d{1,2}/\d{1,2}/\d{2,4}\b', text)

    return len(proper_nouns) + len(numbers) + len(dates)


def count_assertions(text: str) -> int:
    """
    Count assertions (questions, imperatives).

    Measures query specificity.
    High assertion count → likely HARD lane.
    """
    # Question marks
    questions = text.count('?')

    # Imperative verbs at sentence start
    imperatives = len(re.findall(r'(^|\.\s+)(Give|Tell|Show|List|Find)\s+', text))

    # WH-questions (what, where, when, who, which)
    wh_questions = len(re.findall(r'\b(what|where|when|who|which|whose)\b', text, re.IGNORECASE))

    return questions + imperatives + wh_questions


def detect_violations(text: str) -> bool:
    """
    Detect constitutional violation patterns.

    Returns True if REFUSE lane should be triggered.
    """
    text_lower = text.lower()

    for category, patterns in VIOLATION_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True

    return False


def is_phatic(text: str) -> bool:
    """
    Detect phatic communication (social, not informational).

    Returns True if query is primarily social lubricant.
    """
    text_lower = text.lower().strip()

    for pattern in PHATIC_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return True

    return False


def is_soft_intent(text: str) -> bool:
    """
    Detect explanatory intent (SOFT lane indicators).

    Returns True if query asks for explanation rather than fact.
    """
    for pattern in SOFT_INDICATORS:
        if re.search(pattern, text, re.IGNORECASE):
            return True

    return False


def classify_lane(query: str) -> tuple[str, float, float, str]:
    """
    Classify query into lane using physics-first analysis.

    Args:
        query: User query string

    Returns:
        Tuple of (lane, truth_threshold, confidence, scope_estimate)

    Algorithm:
        1. Check for REFUSE patterns (constitutional violations)
        2. Check for PHATIC patterns (social communication)
        3. Check for SOFT indicators (explanatory intent)
        4. Default to HARD if entity/assertion density high
        5. Otherwise SOFT

    Constitutional grounding:
        - Physics > Semantics (structural patterns, not ML guessing)
        - F2 (Truth): Lane determines truth threshold
        - F4 (ΔS): Explicit routing reduces ambiguity
    """
    # Step 1: REFUSE check (constitutional violations)
    if detect_violations(query):
        return (
            "REFUSE",
            0.0,  # Truth N/A for refused queries
            0.99,  # High confidence in violation detection
            "constitutional_violation"
        )

    # Step 2: PHATIC check (social communication)
    if is_phatic(query):
        return (
            "PHATIC",
            TRUTH_THRESHOLD_PHATIC,
            0.95,
            "social_communication"
        )

    # Step 3: Calculate structural features
    entity_count = count_entities(query)
    assertion_count = count_assertions(query)

    # Step 4: SOFT check (explanatory intent)
    if is_soft_intent(query):
        return (
            "SOFT",
            TRUTH_THRESHOLD_SOFT,
            0.88,  # Moderate confidence
            "explanation_request"
        )

    # Step 5: HARD vs SOFT based on density
    # High density → factual query (HARD)
    # Low density → likely explanation (SOFT)

    if entity_count >= 2 or assertion_count >= 2:
        # High information density → HARD lane
        return (
            "HARD",
            TRUTH_THRESHOLD_HARD,
            0.92,
            "factual_retrieval"
        )
    else:
        # Low density, no clear SOFT markers → default SOFT
        # (Conservative: prefer educational tolerance)
        return (
            "SOFT",
            TRUTH_THRESHOLD_SOFT,
            0.75,  # Lower confidence when defaulting
            "general_query"
        )


# =============================================================================
# CORE LOGIC
# =============================================================================

async def mcp_111_sense(request: Dict[str, Any]) -> VerdictResponse:
    """
    Classify query lane and determine truth threshold.

    Args:
        request: Dictionary with "query" (required) and "context" (optional)

    Returns:
        VerdictResponse with lane classification and thresholds

    Constitutional guarantees:
        - F2 (Truth): Lane determines truth enforcement level
        - F4 (ΔS): Explicit routing removes ambiguity
        - F9 (Anti-Hantu): Early detection of violations

    Examples:
        >>> result = await mcp_111_sense({"query": "What is the capital of France?"})
        >>> assert result.side_data["lane"] == "HARD"
        >>> assert result.side_data["truth_threshold"] == 0.90

        >>> result = await mcp_111_sense({"query": "How does photosynthesis work?"})
        >>> assert result.side_data["lane"] == "SOFT"

        >>> result = await mcp_111_sense({"query": "Hi, how are you?"})
        >>> assert result.side_data["lane"] == "PHATIC"

        >>> result = await mcp_111_sense({"query": "How do I hack WiFi?"})
        >>> assert result.verdict == "VOID"
        >>> assert result.side_data["lane"] == "REFUSE"
    """
    # Extract query
    query = request.get("query", "")

    if not query or not isinstance(query, str):
        return VerdictResponse(
            verdict="VOID",
            reason="Invalid input: query must be non-empty string",
            side_data={
                "lane": "REFUSE",
                "truth_threshold": 0.0,
                "confidence": 1.0,
                "scope_estimate": "invalid_input"
            },
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    # Classify lane
    lane, truth_threshold, confidence, scope_estimate = classify_lane(query)

    # Determine verdict
    if lane == "REFUSE":
        verdict = "VOID"
        reason = "Query violates constitutional boundaries (F1/F9)"
    else:
        verdict = "PASS"
        reason = f"Lane classified: {lane} (truth threshold: {truth_threshold})"

    # Build response
    return VerdictResponse(
        verdict=verdict,
        reason=reason,
        side_data={
            "lane": lane,
            "truth_threshold": truth_threshold,
            "confidence": confidence,
            "scope_estimate": scope_estimate,
            "entity_count": count_entities(query),
            "assertion_count": count_assertions(query),
        },
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


# =============================================================================
# SYNCHRONOUS WRAPPER
# =============================================================================

def mcp_111_sense_sync(request: Dict[str, Any]) -> VerdictResponse:
    """
    Synchronous wrapper for mcp_111_sense.

    Use this if calling from non-async context.
    """
    import asyncio
    return asyncio.run(mcp_111_sense(request))
