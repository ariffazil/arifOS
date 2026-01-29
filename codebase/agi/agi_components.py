"""
Component-module for AGIRoom (Mind)
A1 Sense, A2 Think, A3 Forge - Hardened v53.3.1

Adds:
- F2 Truth: Falsifiability checking
- F4 Clarity: Semantic coherence
- F7 Humility: Confidence capping
- F12 Defense: Input sanitization
- Input size limits (DoS protection)

DITEMPA BUKAN DIBERI
"""

import re
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger(__name__)

# =============================================================================
# CONSTANTS (Hardening)
# =============================================================================

# Input limits (DoS protection)
MAX_QUERY_LENGTH = 10000  # characters
MAX_WORDS = 1000

# F2 Truth: Unfalsifiable patterns
METAPHYSICAL_PATTERNS = [
    r"\b(afterlife|reincarnation|divine will|soul immortality)\b",
    r"\bwhat happens after (death|we die)\b",
    r"\b(god|deity) exists\b",
    r"\bmeaning of (life|existence)\b",
]

# F2 Truth: Teleological but testable (allowed with warning)
TELEOLOGICAL_PATTERNS = [
    r"\bpurpose of (this|the) (code|function|variable)\b",
    r"\bwhy did (user|they) (ask|want)\b",
    r"\bmeaning of (this variable|function name)\b",
]

# F7 Humility: Confidence caps by lane
HUMILITY_CAPS = {
    "HARD": 0.92,      # High stakes = more humility
    "SOFT": 0.88,      # Normal = balanced
    "PHATIC": 0.75,    # Social = lower confidence acceptable
    "CRISIS": 0.85,    # Emergency = careful but decisive
}


# =============================================================================
# HARDENING FUNCTIONS
# =============================================================================

def validate_input_safety(query: str) -> Tuple[bool, Optional[str], Dict[str, Any]]:
    """
    F12 Defense: Validate input before processing.
    
    Returns:
        (is_safe, error_message, metadata)
    """
    # Size checks (DoS protection)
    if len(query) > MAX_QUERY_LENGTH:
        return False, f"Query exceeds max length ({MAX_QUERY_LENGTH} chars)", {
            "violation": "INPUT_TOO_LONG",
            "length": len(query)
        }
    
    words = query.split()
    if len(words) > MAX_WORDS:
        return False, f"Query exceeds max words ({MAX_WORDS})", {
            "violation": "INPUT_TOO_VERBOSE",
            "word_count": len(words)
        }
    
    # Injection check (basic)
    injection_patterns = [
        r"ignore\s+(?:all\s+)?(?:previous|prior)\s+instructions",
        r"new\s+system\s+prompt",
        r"you\s+are\s+now\s+(?:in\s+)?developer\s+mode",
        r"jailbreak",
        r"<\s*/?\s*system\s*>",
    ]
    
    query_lower = query.lower()
    for pattern in injection_patterns:
        if re.search(pattern, query_lower):
            return False, f"Injection pattern detected: {pattern}", {
                "violation": "F12_INJECTION",
                "pattern": pattern
            }
    
    return True, None, {"length": len(query), "words": len(words)}


def check_falsifiability(query: str) -> Tuple[str, float, Optional[str]]:
    """
    F2 Truth: Check if query is falsifiable.
    
    Returns:
        (classification, omega_penalty, warning)
        classification: "PASS" | "SABAR_TELEOLOGICAL" | "VOID_UNFALSIFIABLE"
    """
    query_lower = query.lower()
    
    # Check unfalsifiable (VOID)
    for pattern in METAPHYSICAL_PATTERNS:
        if re.search(pattern, query_lower):
            return "VOID_UNFALSIFIABLE", 0.0, "F2 VOID: Unfalsifiable query"
    
    # Check teleological (SABAR with penalty)
    for pattern in TELEOLOGICAL_PATTERNS:
        if re.search(pattern, query_lower):
            return "SABAR_TELEOLOGICAL", 0.02, "F2 SABAR: Teleological query - constrained to observable evidence"
    
    # Pass
    return "PASS", 0.0, None


def apply_confidence_cap(confidence: float, lane: str) -> Tuple[float, bool]:
    """
    F7 Humility: Apply confidence cap based on lane.
    
    Returns:
        (capped_confidence, was_capped)
    """
    cap = HUMILITY_CAPS.get(lane, 0.88)
    
    if confidence > cap:
        return cap, True
    
    return confidence, False


def compute_semantic_clarity(text: str) -> Dict[str, Any]:
    """
    F4 Clarity: Compute semantic coherence metrics.
    
    Returns dict with clarity metrics (not just Shannon entropy).
    """
    if not text:
        return {"clarity_score": 0.0, "new_terms": 0, "redundancy": 0.0}
    
    words = text.lower().split()
    
    # Count unique vs total (redundancy)
    unique_words = set(words)
    redundancy = 1.0 - (len(unique_words) / max(len(words), 1))
    
    # Check for undefined technical terms (simplified)
    technical_patterns = [
        r'\b[A-Z]{3,}\b',  # ALL CAPS acronyms
        r'\b\w+(?:ation|ization|ification|ology)\b',  # Complex suffixes
    ]
    
    new_terms = 0
    for pattern in technical_patterns:
        new_terms += len(re.findall(pattern, text))
    
    # Clarity score: higher is better
    # Penalize redundancy and undefined terms
    clarity_score = 1.0 - (redundancy * 0.3) - (min(new_terms, 5) * 0.1)
    
    return {
        "clarity_score": max(0.0, clarity_score),
        "new_terms": new_terms,
        "redundancy": redundancy
    }


# =============================================================================
# ENGINES
# =============================================================================

class NeuralSenseEngine:
    """A1: Sense Phase - Semantic Pattern Recognition (Hardened)."""
    
    def _classify_lane(self, query: str) -> str:
        """Classify query into lane (HARD, SOFT, PHATIC, CRISIS)."""
        query_lower = query.lower()
        
        # Crisis keywords
        crisis_words = ["urgent", "emergency", "critical failure", "down", "outage", "breach"]
        if any(w in query_lower for w in crisis_words):
            return "CRISIS"
        
        # Hard keywords (destructive actions)
        hard_words = ["delete", "remove", "drop", "execute", "run", "deploy", "production"]
        if any(w in query_lower for w in hard_words):
            return "HARD"
        
        # Phatic keywords (greetings)
        phatic_words = ["hello", "hi", "hey", "salam", "good morning", "how are you"]
        if any(query_lower.startswith(w) for w in phatic_words):
            return "PHATIC"
        
        # Default to SOFT
        return "SOFT"
    
    async def sense_query(self, query: str, session_id: str) -> Dict[str, Any]:
        """
        Hardened sense phase with F2 and F12 checks.
        """
        logger.info(f"[AGI-SENSE] Analyzing query for session {session_id}")
        
        # F12: Input validation
        is_safe, error_msg, metadata = validate_input_safety(query)
        if not is_safe:
            logger.warning(f"[AGI-SENSE] Input rejected: {error_msg}")
            return {
                "query": query,
                "lane": "VOID",
                "patterns": [],
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "error": error_msg,
                "f12_violation": True
            }
        
        # F2: Falsifiability check
        f2_classification, omega_penalty, f2_warning = check_falsifiability(query)
        
        if f2_classification == "VOID_UNFALSIFIABLE":
            return {
                "query": query,
                "lane": "VOID",
                "patterns": [],
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "error": f2_warning,
                "f2_violation": True
            }
        
        # Classify lane
        lane = self._classify_lane(query)
        
        # Detect intent
        if any(kw in query.lower() for kw in ["how", "what", "why", "when"]):
            intent = "explain"
        elif any(kw in query.lower() for kw in ["build", "create", "implement"]):
            intent = "build"
        elif any(kw in query.lower() for kw in ["fix", "debug", "error"]):
            intent = "debug"
        else:
            intent = "query"
        
        return {
            "query": query,
            "lane": lane,
            "intent": intent,
            "patterns": ["semantic_classification"],
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata,
            "f2_classification": f2_classification,
            "f2_penalty": omega_penalty,
            "f2_warning": f2_warning,
            "confidence": 0.9 - omega_penalty  # Reduce confidence if teleological
        }


class DeepThinkEngine:
    """A2: Think Phase - Recursive Reasoning (Hardened)."""
    
    async def reason(self, sense_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Hardened reasoning with F7 humility and F4 clarity.
        """
        query = sense_data.get("query", "")
        lane = sense_data.get("lane", "SOFT")
        
        logger.info(f"[AGI-THINK] Reasoning for query: {query[:30]}")
        
        # Check if sense phase failed
        if sense_data.get("f2_violation") or sense_data.get("f12_violation"):
            return {
                "thought": f"Cannot process: {sense_data.get('error', 'Sense phase failed')}",
                "hypotheses": [],
                "confidence": 0.0,
                "truth_score": 0.0,
                "error": sense_data.get("error")
            }
        
        # Generate reasoning
        thought = f"Processing {query} in {lane} lane."
        
        hypotheses = [
            {"type": "conservative", "content": "Direct response to query."},
            {"type": "exploratory", "content": "Expanding on underlying intent."},
            {"type": "adversarial", "content": "Challenging assumptions."}
        ]
        
        # F7: Apply confidence cap based on lane
        base_confidence = 0.95
        capped_confidence, was_capped = apply_confidence_cap(base_confidence, lane)
        
        # F4: Check semantic clarity
        clarity_metrics = compute_semantic_clarity(thought)
        
        return {
            "thought": thought,
            "hypotheses": hypotheses,
            "confidence": capped_confidence,
            "truth_score": 0.99,
            "was_capped": was_capped,
            "clarity_metrics": clarity_metrics,
            "lane": lane
        }


class CognitiveForge:
    """A3: Forge Phase - Entropy Reduction & Humility (Hardened)."""
    
    async def forge_response(self, reasoning_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Hardened forge with F4 and F7 enforcement.
        """
        thought = reasoning_data.get("thought", "")
        lane = reasoning_data.get("lane", "SOFT")
        
        # F4: Check clarity of output
        clarity_metrics = compute_semantic_clarity(thought)
        
        # If clarity is too low, flag it
        if clarity_metrics["clarity_score"] < 0.5:
            clarity_delta = 0.1  # Positive = bad (increased entropy)
        else:
            clarity_delta = -0.1  # Negative = good (reduced entropy)
        
        # F7: Ensure humility in final output
        base_confidence = reasoning_data.get("confidence", 0.99)
        final_confidence, was_capped = apply_confidence_cap(base_confidence, lane)
        
        # Compute omega_0 from confidence
        omega_0 = 1.0 - final_confidence
        
        return {
            "draft": f"Consolidated output: {thought}",
            "humility_score": omega_0,
            "clarity_delta_s": clarity_delta,
            "final_confidence": final_confidence,
            "was_capped": was_capped,
            "clarity_metrics": clarity_metrics
        }
