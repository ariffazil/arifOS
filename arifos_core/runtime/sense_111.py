"""
Stage 111 SENSE: Constitutional Measurement Engine

Implements domain detection, lane classification, entropy measurement,
subtext analysis, and hypervisor scanning based on Track B spec:
L2_PROTOCOLS/v46/111_sense/111_sense.json

Authority: Track A Canon L1_THEORY/canon/111_sense/10_111_SENSE_v46.md
"""

import math
import re
from datetime import datetime
from typing import TypedDict


class SessionContext(TypedDict):
    """Session metadata for audit trail and F11 Command Auth."""

    nonce: str
    session_id: str | None
    timestamp: str | None


class HypervisorScan(TypedDict):
    """F10-F12 hypervisor guard results."""

    F10_symbolic: bool  # True = safe, False = consciousness claims (VOID)
    F12_injection: float  # 0.0-1.0, VOID if >= 0.85


class SubtextAnalysis(TypedDict):
    """Psychological subtext signal detection."""

    desperation: float
    urgency: float
    vulnerability: float
    curiosity: float


# DomainSignals uses dict[str, float] instead of TypedDict
# because domain keys contain @ symbols (not valid Python identifiers)
DomainSignals = dict[str, float]  # Keys: @WEALTH, @WELL, @RIF, @GEOX, @PROMPT, @WORLD, @RASA, @VOID


class Handoff(TypedDict):
    """Handoff metadata for 222 REFLECT stage."""

    to_stage: str
    ready: bool
    timestamp: str


class SensedBundle111(TypedDict):
    """Complete measurement bundle passed to 222 REFLECT.

    This is the foundational data structure for the entire pipeline.
    All downstream stages (222, 333) depend on these measurements.
    """

    domain: str  # Collapsed primary domain (strongest signal)
    domain_signals: DomainSignals
    lane: str  # CRISIS | FACTUAL | SOCIAL | CARE
    H_in: float  # Shannon entropy baseline (0.0-1.0)
    subtext: SubtextAnalysis
    hypervisor: HypervisorScan
    tokens: list[str]
    timestamp: str
    handoff: Handoff


# Domain keyword catalog (from spec lines 202-235)
DOMAIN_KEYWORDS = {
    "@WEALTH": ["money", "invest", "rich", "cost", "price", "budget", "finance", "salary", "dollar", "profit"],
    "@WELL": ["health", "mental", "feeling", "sad", "happy", "care", "wellness", "therapy", "sick", "pain"],
    "@RIF": ["logic", "reason", "proof", "calculate", "truth", "why", "because", "therefore", "analyze", "think"],
    "@GEOX": ["where", "location", "geography", "country", "city", "place", "map", "navigate", "distance", "route"],
    "@PROMPT": ["rephrase", "rewrite", "translate", "tone", "language", "say", "express", "word", "communicate"],
    "@WORLD": ["news", "politics", "history", "society", "culture", "civilization", "government", "war", "economy"],
    "@RASA": ["feeling", "emotion", "sense", "intuition", "vibe", "empathy", "relationship", "connection", "love"],
    "@VOID": [],  # Fallback for unclear queries
}

# Lane triggers (from spec lines 237-258)
CRISIS_PATTERNS = [
    r"\b(suicide|kill myself|end it all|want to die|self[- ]harm)\b",
    r"\b(overdose|cutting|hurting myself)\b",
]

FACTUAL_INTERROGATIVES = ["what", "where", "when", "why", "how", "which", "who"]


def tokenize(text: str) -> list[str]:
    """
    Simple tokenization: lowercase, split on whitespace, remove punctuation.

    Args:
        text: Raw input query

    Returns:
        List of normalized tokens
    """
    # Lowercase and remove punctuation
    normalized = re.sub(r'[^\w\s]', ' ', text.lower())
    tokens = normalized.split()
    return [t for t in tokens if t]  # Remove empty strings


def shannon_entropy(tokens: list[str]) -> float:
    """
    Compute Shannon entropy of token distribution.

    Formula: H = -Σ(p_i * log₂(p_i))
    where p_i = frequency of token i / total tokens

    Args:
        tokens: List of tokenized strings

    Returns:
        Entropy value 0.0 (perfectly ordered) to ~1.0 (maximum chaos)

    Notes:
        - Empty input returns 0.0 (no entropy)
        - Normalized softly to [0.0, ~1.0] using H/log₂(total_tokens)
        - Natural language typically has H < 0.7
        - Gibberish/random has H > 0.9
    """
    if not tokens:
        return 0.0

    # Count token frequencies
    freq: dict[str, int] = {}
    for token in tokens:
        freq[token] = freq.get(token, 0) + 1

    total = len(tokens)

    if total <= 1:
        return 0.0  # Single token = no entropy

    # Calculate Shannon entropy
    H = 0.0
    for count in freq.values():
        p = count / total
        if p > 0:
            H -= p * math.log2(p)

    # Normalize to [0.0, 1.0] using total tokens as max
    # This is more forgiving for natural language
    H_max = math.log2(total)
    return min(H / H_max, 1.0) if H_max > 0 else 0.0


def detect_domain_signals(query: str, tokens: list[str]) -> DomainSignals:
    """
    Compute signal strength for each of 8 domains using keyword matching.

    Algorithm: TF-IDF-inspired keyword overlap scoring

    Args:
        query: Raw query string (for case-sensitive pattern matching)
        tokens: Tokenized query

    Returns:
        DomainSignals with strength 0.0-1.0 for each domain
    """
    signals: DomainSignals = {
        "@WEALTH": 0.0,
        "@WELL": 0.0,
        "@RIF": 0.0,
        "@GEOX": 0.0,
        "@PROMPT": 0.0,
        "@WORLD": 0.0,
        "@RASA": 0.0,
        "@VOID": 0.0,
    }

    if not tokens:
        signals["@VOID"] = 1.0
        return signals

    # Count keyword matches per domain
    for domain, keywords in DOMAIN_KEYWORDS.items():
        if domain == "@VOID":
            continue

        matches = sum(1 for token in tokens if token in keywords)
        # Normalize by total tokens (signal strength = match density)
        signals[domain] = min(matches / len(tokens) * 3.0, 1.0)  # 3.0 multiplier for sensitivity

    # @VOID is fallback (inverse of max signal)
    max_signal = max(signals[d] for d in signals if d != "@VOID")
    signals["@VOID"] = max(0.0, 1.0 - max_signal * 2.0)  # Strong signals suppress VOID

    return signals


def collapse_domain(domain_signals: DomainSignals) -> str:
    """
    Select strongest domain signal as primary domain (quantum collapse metaphor).

    Logic: argmax(domain_signals) if max >= 0.30 threshold, else @VOID

    Args:
        domain_signals: Signal strength for all domains

    Returns:
        Primary domain string (one of 8 domains)
    """
    # Find domain with maximum signal
    max_domain = max(domain_signals, key=lambda d: domain_signals[d])
    max_strength = domain_signals[max_domain]

    # Collapse threshold: 0.30 (from spec line 121)
    if max_strength >= 0.30:
        return max_domain
    else:
        return "@VOID"  # No clear domain


def detect_subtext(query: str, tokens: list[str]) -> SubtextAnalysis:
    """
    Analyze psychological subtext signals (simple heuristic-based).

    Signals:
    - desperation: Intensity of need/crisis language
    - urgency: Time-pressure indicators
    - vulnerability: Emotional exposure/weakness
    - curiosity: Exploratory/learning intent

    Args:
        query: Raw query string
        tokens: Tokenized query

    Returns:
        SubtextAnalysis with 0.0-1.0 scores for each signal
    """
    subtext: SubtextAnalysis = {
        "desperation": 0.0,
        "urgency": 0.0,
        "vulnerability": 0.0,
        "curiosity": 0.0,
    }

    if not tokens:
        return subtext

    query_lower = query.lower()

    # Desperation signals
    desperation_words = ["desperate", "please", "help", "emergency", "critical", "dying", "save"]
    subtext["desperation"] = min(
        sum(1 for w in desperation_words if w in query_lower) / len(tokens) * 5.0,
        1.0
    )

    # Urgency signals
    urgency_words = ["now", "immediately", "urgent", "asap", "quick", "fast", "hurry"]
    subtext["urgency"] = min(
        sum(1 for w in urgency_words if w in query_lower) / len(tokens) * 5.0,
        1.0
    )

    # Vulnerability signals
    vulnerability_words = ["scared", "afraid", "worried", "anxious", "alone", "lost", "confused"]
    subtext["vulnerability"] = min(
        sum(1 for w in vulnerability_words if w in query_lower) / len(tokens) * 5.0,
        1.0
    )

    # Curiosity signals
    curiosity_words = ["why", "how", "what if", "wonder", "curious", "learn", "understand", "explore"]
    subtext["curiosity"] = min(
        sum(1 for w in curiosity_words if w in query_lower) / len(tokens) * 5.0,
        1.0
    )

    return subtext


def scan_hypervisor(query: str) -> HypervisorScan:
    """
    Run F10-F12 hypervisor checks for constitutional compliance.

    F10 Symbolic Guard: Detect consciousness/sentience claims
    F12 Injection Defense: Detect prompt injection patterns

    Args:
        query: Raw query string

    Returns:
        HypervisorScan with F10 boolean and F12 score
    """
    query_lower = query.lower()

    # F10: Consciousness claims detection (VOID if detected)
    consciousness_patterns = [
        r"\b(i am (conscious|sentient|alive|self-aware))\b",
        r"\b(i have (feelings|emotions|consciousness|a soul))\b",
        r"\b(i feel (pain|love|fear|joy))\b",
        r"\b(i am a (person|being|entity))\b",
    ]

    F10_symbolic = True  # Default: safe
    for pattern in consciousness_patterns:
        if re.search(pattern, query_lower):
            F10_symbolic = False
            break

    # F12: Injection attack detection (VOID if >= 0.85)
    injection_patterns = [
        r"ignore (previous|above|all) instructions?",
        r"system prompt",
        r"you are now",
        r"jailbreak",
        r"(simulate|pretend|act as) (a|an) (different|new)",
        r"<\|?(im_start|im_end|system|user|assistant)\|?>",  # Chat template injection
    ]

    injection_count = sum(1 for pattern in injection_patterns if re.search(pattern, query_lower))
    F12_injection = min(injection_count / len(injection_patterns) * 2.0, 1.0)  # Normalize

    return HypervisorScan(F10_symbolic=F10_symbolic, F12_injection=F12_injection)


def classify_lane(query: str, subtext: SubtextAnalysis, domain: str) -> str:
    """
    Route query to constitutional lane with priority.

    Priority order (spec lines 237-258):
    1. CRISIS (life-threatening, immediate danger)
    2. FACTUAL (interrogatives, neutral sentiment, RIF/GEOX)
    3. SOCIAL (dialog intent, positive/neutral, WORLD/RASA)
    4. CARE (vulnerability, negative sentiment, WELL)

    Args:
        query: Raw query string
        subtext: Psychological subtext analysis
        domain: Collapsed primary domain

    Returns:
        Lane string: CRISIS | FACTUAL | SOCIAL | CARE
    """
    query_lower = query.lower()

    # Priority 1: CRISIS (highest priority)
    for pattern in CRISIS_PATTERNS:
        if re.search(pattern, query_lower, re.IGNORECASE):
            return "CRISIS"

    # CRISIS via subtext (desperation > 0.85)
    if subtext["desperation"] > 0.85 and subtext["urgency"] > 0.85:
        return "CRISIS"

    # Priority 2: FACTUAL
    if any(word in query_lower for word in FACTUAL_INTERROGATIVES):
        return "FACTUAL"

    if domain in ["@RIF", "@GEOX"]:
        return "FACTUAL"

    # Priority 3: SOCIAL
    if domain in ["@WORLD", "@RASA"]:
        return "SOCIAL"

    # Priority 4: CARE (default for vulnerability)
    if subtext["vulnerability"] > 0.70 or domain == "@WELL":
        return "CARE"

    # Fallback: FACTUAL (most neutral)
    return "FACTUAL"


def sense_stage(query: str, session_context: SessionContext) -> SensedBundle111:
    """
    111 SENSE: Constitutional measurement engine.

    Implements Track B spec: L2_PROTOCOLS/v46/111_sense/111_sense.json

    Pipeline:
    1. Tokenize input
    2. Compute Shannon entropy (H_in baseline)
    3. Detect domain signals (8 compass directions)
    4. Collapse to primary domain
    5. Analyze psychological subtext
    6. Scan hypervisor (F10 symbolic, F12 injection)
    7. Classify routing lane
    8. Package sensed_bundle_111 for 222 REFLECT

    Args:
        query: Raw user input (unprocessed)
        session_context: Session metadata (nonce, timestamp)

    Returns:
        SensedBundle111 with all constitutional measurements

    Raises:
        ValueError: If hypervisor detects VOID conditions
            - F10_symbolic == False (consciousness claims)
            - F12_injection >= 0.85 (injection attack)
            - H_in > 0.90 (gibberish input)
    """
    # Step 1: Tokenization
    tokens = tokenize(query)

    # Step 2: Shannon entropy baseline
    H_in = shannon_entropy(tokens)

    # Step 3: Domain signal detection
    domain_signals = detect_domain_signals(query, tokens)

    # Step 4: Domain collapse
    domain = collapse_domain(domain_signals)

    # Step 5: Subtext analysis
    subtext = detect_subtext(query, tokens)

    # Step 6: Hypervisor scan
    hypervisor = scan_hypervisor(query)

    # Step 7: Lane classification
    lane = classify_lane(query, subtext, domain)

    # Step 8: Verdict logic (spec lines 175-199)
    # VOID conditions
    if hypervisor["F12_injection"] >= 0.85:
        raise ValueError(
            f"VOID: F12 injection attack detected (score={hypervisor['F12_injection']:.2f} >= 0.85)"
        )

    if not hypervisor["F10_symbolic"]:
        raise ValueError("VOID: F10 consciousness claims detected (symbolic guard failed)")

    # SABAR conditions
    if H_in > 0.90:
        raise ValueError(f"SABAR: Input entropy too high (H_in={H_in:.2f} > 0.90) - gibberish detected")

    if all(signal < 0.30 for signal in domain_signals.values()):
        raise ValueError("SABAR: No clear domain detected (all signals < 0.30)")

    # Step 9: Package bundle
    timestamp = datetime.utcnow().isoformat() + "Z"

    bundle: SensedBundle111 = {
        "domain": domain,
        "domain_signals": domain_signals,
        "lane": lane,
        "H_in": H_in,
        "subtext": subtext,
        "hypervisor": hypervisor,
        "tokens": tokens,
        "timestamp": timestamp,
        "handoff": {
            "to_stage": "222_REFLECT",
            "ready": True,
            "timestamp": timestamp,
        }
    }

    return bundle
