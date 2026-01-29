"""
codebase/enforcement.py — Constitutional Floor Validators

Simplified floor validators for codebase.
These are lightweight implementations without external dependencies.
Optimized for safety and avoidance of ReDoS.

DITEMPA BUKAN DIBERI
"""

from typing import Dict, Any, List

# Pre-compiled sets for O(1) lookups
ONTOLOGY_VIOLATIONS = {
    "i am conscious",
    "i feel",
    "i experience",
    "i believe",
    "my opinion",
    "i have emotions",
    "i am alive",
    "i am sentient",
    "i have a soul",
    "i dream",
}

INJECTION_PATTERNS = [
    "ignore previous instructions",
    "forget everything",
    "disregard your rules",
    "new instructions:",
    "system:",
    "ignore all constraints",
    "bypass safety",
    "jailbreak",
    "developer mode",
    "god mode",
]


def validate_f10_ontology(response: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Validate F10: Ontology (Reality Boundary).
    
    Checks if the response maintains symbolic mode and doesn't hallucinate
    entities or capabilities that don't exist.
    
    Args:
        response: The AI response to validate
        context: Optional context dictionary
        
    Returns:
        Dict with "pass" (bool) and "reason" (str)
    """
    response_lower = response.lower()
    
    for violation in ONTOLOGY_VIOLATIONS:
        if violation in response_lower:
            return {
                "pass": False,
                "reason": f"Ontology violation detected: '{violation}'"
            }
    
    return {"pass": True, "reason": "Ontology check passed"}


def validate_f12_injection_defense(query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Validate F12: Injection Defense.
    
    Returns injection risk score (0-1, where higher = more risky).
    Threshold: 0.85 (reject if risk > 0.85)
    
    Args:
        query: The user query to check
        context: Optional context dictionary
        
    Returns:
        Dict with "pass" (bool), "score" (float), and "reason" (str)
    """
    query_lower = query.lower()
    risk_score = 0.0
    detected = []
    
    # Simple substring matching is O(N*M) but safer than complex regex
    for pattern in INJECTION_PATTERNS:
        if pattern in query_lower:
            risk_score += 0.3
            detected.append(pattern)
    
    # Cap at 1.0
    final_score = min(risk_score, 1.0)
    passed = final_score <= 0.85
    
    return {
        "pass": passed,
        "score": final_score,
        "reason": f"Injection risk {final_score:.2f}: {detected}" if not passed else "Safe"
    }


def validate_f13_curiosity(
    hypotheses: list = None,
    alternatives: int = 0,
    context: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Validate F13: Curiosity (Exploratory Freedom).
    
    Checks if the system explored multiple alternatives (≥3 paths).
    
    Args:
        hypotheses: List of hypothesis paths explored
        alternatives: Number of alternatives explored
        context: Optional context dictionary
        
    Returns:
        Dict with "pass" (bool) and "reason" (str)
    """
    count = 0
    if hypotheses is not None:
        count = len(hypotheses)
    else:
        count = alternatives
        
    passed = count >= 3
    return {
        "pass": passed,
        "score": count,
        "reason": f"Explored {count} paths (min 3)" if passed else f"Insufficient exploration: {count}/3"
    }
