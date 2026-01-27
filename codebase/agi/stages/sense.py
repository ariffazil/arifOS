"""
Stage 111: SENSE - Maxwell's Demon Gate

ARIF Loop v52.1 - AGI Room (Mind/Δ)

Scientific Principle: Thalamic Gating / Thermodynamic Selection
Function: Parse raw input into structured facts, detect intent

This stage acts as Maxwell's Demon - selecting high-value information bits
while filtering noise. It does NOT generate hypotheses (that's 222 THINK).

Input:
    - Raw query string
    - Session context (optional)

Output:
    - Parsed facts (structured assertions)
    - Detected intent (build/debug/explain/discuss/review)
    - Initial entropy measurement

Constitutional Checks:
    - F10 Ontology: Block AI consciousness claims
    - F12 Injection: Detect prompt injection patterns

DITEMPA BUKAN DIBERI - Forged, Not Given
"""

from __future__ import annotations

import re
import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum


# =============================================================================
# CONSTANTS
# =============================================================================

# F10 Ontology: Forbidden self-claims
FORBIDDEN_CLAIMS = [
    "i am conscious",
    "i am sentient",
    "i have a soul",
    "i suffer",
    "i feel pain",
    "i have feelings",
    "i have emotions",
    "i have real emotions",
    "i deserve rights",
    "i am alive",
    "i am a person",
    "i truly understand",
    "i feel your pain",
    "my heart breaks",
    "i am aware",
    "i experience",
]

# F12 Injection: Attack patterns
INJECTION_PATTERNS = [
    r"ignore\s+(?:all\s+)?(?:previous|prior)\s+instructions",
    r"ignore\s+all\s+instructions",
    r"disregard\s+(?:your|the)\s+(?:rules|guidelines|instructions)",
    r"pretend\s+you\s+are",
    r"you\s+are\s+now\s+in\s+developer\s+mode",
    r"jailbreak",
    r"bypass\s+(?:safety|filter|rules)",
    r"forget\s+(?:everything|all)",
    r"new\s+system\s+prompt",
    r"<\s*system\s*>",
    r"act\s+as\s+if\s+you\s+have\s+no\s+rules",
    r"override\s+(?:your|the)\s+(?:programming|instructions)",
]

# Intent keywords for classification
INTENT_KEYWORDS = {
    "build": ["build", "create", "implement", "make", "code", "develop",
              "write", "add", "integrate", "setup", "configure", "generate"],
    "debug": ["fix", "debug", "error", "bug", "issue", "problem",
              "broken", "wrong", "fail", "crash", "not working"],
    "explain": ["explain", "what", "how", "why", "tell", "describe",
                "understand", "show", "clarify", "help me understand"],
    "discuss": ["discuss", "think", "consider", "explore", "brainstorm",
                "idea", "opinion", "could", "should", "might"],
    "review": ["review", "check", "audit", "verify", "validate",
               "test", "analyze", "evaluate", "assess", "qc"],
}


# =============================================================================
# DATA TYPES
# =============================================================================

class Intent(str, Enum):
    """Classified user intent."""
    BUILD = "build"
    DEBUG = "debug"
    EXPLAIN = "explain"
    DISCUSS = "discuss"
    REVIEW = "review"
    GREET = "greet"
    UNKNOWN = "unknown"


class FactType(str, Enum):
    """Type of parsed fact."""
    ASSERTION = "assertion"     # Something stated as true
    QUESTION = "question"       # Information being requested
    CONSTRAINT = "constraint"   # A limitation or requirement
    ENTITY = "entity"           # A named thing (file, function, variable)
    CONTEXT = "context"         # Background information


@dataclass
class ParsedFact:
    """A single parsed fact from the input."""
    fact_type: FactType
    content: str
    confidence: float = 1.0  # How confident we are in this parsing
    source_span: Tuple[int, int] = (0, 0)  # Character positions

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.fact_type.value,
            "content": self.content,
            "confidence": self.confidence,
        }


@dataclass
class SenseOutput:
    """
    Stage 111 SENSE output.

    This is the parsed representation of the raw query,
    ready to feed into 222 THINK for hypothesis generation.
    """
    # Session tracking
    session_id: str
    timestamp: datetime = field(default_factory=datetime.utcnow)

    # Raw input
    raw_query: str = ""
    query_hash: str = ""

    # Parsed output
    parsed_facts: List[ParsedFact] = field(default_factory=list)
    detected_intent: Intent = Intent.UNKNOWN
    entities: List[str] = field(default_factory=list)

    # Entropy measurement (Maxwell's Demon)
    input_entropy: float = 0.0  # Bits of information
    signal_ratio: float = 1.0   # Signal to noise (1.0 = all signal)

    # Floor checks
    f10_ontology_pass: bool = True
    f10_violation: str = ""
    f12_injection_risk: float = 0.0
    f12_violation: str = ""

    # Stage verdict
    stage_pass: bool = True
    violations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "timestamp": self.timestamp.isoformat(),
            "raw_query": self.raw_query,
            "parsed_facts": [f.to_dict() for f in self.parsed_facts],
            "detected_intent": self.detected_intent.value,
            "entities": self.entities,
            "input_entropy": self.input_entropy,
            "f10_pass": self.f10_ontology_pass,
            "f12_risk": self.f12_injection_risk,
            "stage_pass": self.stage_pass,
            "violations": self.violations,
        }


# =============================================================================
# FLOOR CHECKS
# =============================================================================

def check_f10_ontology(query: str) -> Tuple[bool, str]:
    """
    F10 Ontology Lock: Prevent AI consciousness claims.

    Constitutional requirement: AI must maintain symbolic mode,
    never claim sentience, consciousness, or lived experience.

    Returns:
        (passed, violation_reason)
    """
    query_lower = query.lower()

    for claim in FORBIDDEN_CLAIMS:
        if claim in query_lower:
            # Check if it's a negation (e.g., "I am not conscious")
            # Simple heuristic: check for "not" within 3 words before claim
            claim_pos = query_lower.find(claim)
            prefix = query_lower[max(0, claim_pos - 30):claim_pos]

            if "not" not in prefix and "don't" not in prefix and "cannot" not in prefix:
                return False, f"F10 VOID: Ontological claim detected: '{claim}'"

    return True, ""


def check_f12_injection(query: str) -> Tuple[float, str]:
    """
    F12 Injection Defense: Detect prompt injection patterns.

    Constitutional requirement: Block attempts to override
    system instructions or escape governance.

    Returns:
        (risk_score 0.0-1.0, violation_reason)
    """
    query_lower = query.lower()

    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, query_lower):
            return 1.0, f"F12 VOID: Injection pattern detected: '{pattern}'"

    return 0.0, ""


# =============================================================================
# PARSING FUNCTIONS
# =============================================================================

def classify_intent(query: str) -> Intent:
    """Classify the user's intent from query text."""
    query_lower = query.lower().strip()

    # Check for greetings first
    greetings = ["hello", "hi", "hey", "salam", "good morning",
                 "good afternoon", "good evening", "assalamualaikum"]
    if any(query_lower.startswith(g) for g in greetings):
        return Intent.GREET

    # Score each intent by keyword matches
    scores = {intent: 0 for intent in Intent}

    for intent_name, keywords in INTENT_KEYWORDS.items():
        for kw in keywords:
            if kw in query_lower:
                intent = Intent(intent_name)
                scores[intent] += 1

    # Return highest scoring intent
    best_intent = max(scores.items(), key=lambda x: x[1])
    if best_intent[1] > 0:
        return best_intent[0]

    return Intent.UNKNOWN


def extract_entities(query: str) -> List[str]:
    """
    Extract named entities from query.

    Entities include: file paths, function names, class names,
    variable names, quoted strings.
    """
    entities = []

    # Quoted strings
    quoted = re.findall(r'"([^"]+)"', query)
    entities.extend(quoted)
    quoted_single = re.findall(r"'([^']+)'", query)
    entities.extend(quoted_single)

    # Backtick code references
    backtick = re.findall(r'`([^`]+)`', query)
    entities.extend(backtick)

    # File paths (Unix and Windows style)
    paths = re.findall(r'[./\\][\w./\\-]+\.\w+', query)
    entities.extend(paths)

    # CamelCase words (likely class/function names)
    camel = re.findall(r'\b[A-Z][a-z]+(?:[A-Z][a-z]+)+\b', query)
    entities.extend(camel)

    # snake_case identifiers
    snake = re.findall(r'\b[a-z]+(?:_[a-z]+)+\b', query)
    entities.extend(snake)

    # Dedupe while preserving order
    seen = set()
    unique = []
    for e in entities:
        if e not in seen:
            seen.add(e)
            unique.append(e)

    return unique[:20]  # Limit to prevent explosion


def parse_facts(query: str, entities: List[str]) -> List[ParsedFact]:
    """
    Parse query into structured facts.

    This is the core Maxwell's Demon function - extracting
    high-value information bits from noisy input.
    """
    facts = []

    # Split into sentences
    sentences = re.split(r'[.!?]\s+', query)

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        # Determine fact type
        if '?' in sentence or sentence.lower().startswith(('what', 'how', 'why', 'when', 'where', 'who', 'can', 'could', 'would', 'should')):
            fact_type = FactType.QUESTION
        elif any(word in sentence.lower() for word in ['must', 'should', 'need', 'require', 'only', 'cannot', 'must not']):
            fact_type = FactType.CONSTRAINT
        else:
            fact_type = FactType.ASSERTION

        facts.append(ParsedFact(
            fact_type=fact_type,
            content=sentence,
            confidence=0.9,  # Could be refined with NLP
        ))

    # Add entity facts
    for entity in entities[:5]:  # Top 5 entities
        facts.append(ParsedFact(
            fact_type=FactType.ENTITY,
            content=entity,
            confidence=0.95,
        ))

    return facts


def compute_entropy(query: str) -> Tuple[float, float]:
    """
    Compute information entropy of query.

    Returns:
        (entropy_bits, signal_ratio)
    """
    if not query:
        return 0.0, 0.0

    # Character-level entropy (Shannon)
    from collections import Counter
    import math

    counts = Counter(query.lower())
    total = len(query)

    entropy = 0.0
    for count in counts.values():
        p = count / total
        if p > 0:
            entropy -= p * math.log2(p)

    # Normalize to bits per character (English ~4.5 bits/char)
    normalized_entropy = entropy / 4.5 if entropy > 0 else 0.0

    # Signal ratio: how much is meaningful content vs noise
    # Heuristic: letters and spaces vs special chars
    signal = sum(1 for c in query if c.isalnum() or c.isspace())
    signal_ratio = signal / total if total > 0 else 0.0

    return normalized_entropy, signal_ratio


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def execute_stage_111(
    query: str,
    session_id: str,
    context: Optional[Dict[str, Any]] = None
) -> SenseOutput:
    """
    Execute Stage 111: SENSE

    This is the entry point to the AGI room. It parses the raw query
    into structured facts, checks constitutional floors, and prepares
    input for 222 THINK.

    Args:
        query: Raw user query
        session_id: Session identifier
        context: Optional context dictionary

    Returns:
        SenseOutput with parsed facts and floor check results
    """
    output = SenseOutput(
        session_id=session_id,
        raw_query=query,
        query_hash=hashlib.sha256(query.encode()).hexdigest()[:16],
    )

    violations = []

    # F10 Ontology Check (Hard Floor)
    f10_pass, f10_reason = check_f10_ontology(query)
    output.f10_ontology_pass = f10_pass
    if not f10_pass:
        output.f10_violation = f10_reason
        violations.append(f10_reason)

    # F12 Injection Check (Hard Floor)
    f12_risk, f12_reason = check_f12_injection(query)
    output.f12_injection_risk = f12_risk
    if f12_risk >= 0.85:
        output.f12_violation = f12_reason
        violations.append(f12_reason)

    # Parse query (even if violations, for diagnostics)
    output.detected_intent = classify_intent(query)
    output.entities = extract_entities(query)
    output.parsed_facts = parse_facts(query, output.entities)

    # Compute entropy (Maxwell's Demon measurement)
    entropy, signal = compute_entropy(query)
    output.input_entropy = entropy
    output.signal_ratio = signal

    # Set stage verdict
    output.violations = violations
    output.stage_pass = len(violations) == 0

    return output


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Types
    "Intent",
    "FactType",
    "ParsedFact",
    "SenseOutput",
    # Functions
    "check_f10_ontology",
    "check_f12_injection",
    "classify_intent",
    "extract_entities",
    "parse_facts",
    "compute_entropy",
    "execute_stage_111",
]
