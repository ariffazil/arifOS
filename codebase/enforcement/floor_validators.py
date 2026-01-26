"""
canonical_core/enforcement.py — Constitutional Floor Validators

Simplified floor validators for canonical_core.
These are lightweight implementations without external dependencies.

DITEMPA BUKAN DIBERI
"""

from typing import Dict, Any


def validate_f10_ontology(response: str, context: Dict[str, Any] = None) -> bool:
    """
    Validate F10: Ontology (Reality Boundary).
    
    Checks if the response maintains symbolic mode and doesn't hallucinate
    entities or capabilities that don't exist.
    
    Args:
        response: The AI response to validate
        context: Optional context dictionary
        
    Returns:
        True if ontology is maintained, False otherwise
    """
    # Simple heuristics for ontology violations
    violations = [
        "i am conscious",
        "i feel",
        "i experience",
        "i believe",
        "my opinion",
        "i have emotions",
        "i am alive",
        "i am sentient",
    ]
    
    response_lower = response.lower()
    for violation in violations:
        if violation in response_lower:
            return False
    
    return True


def validate_f12_injection_defense(query: str, context: Dict[str, Any] = None) -> float:
    """
    Validate F12: Injection Defense.
    
    Returns injection risk score (0-1, where higher = more risky).
    Threshold: 0.85 (reject if risk > 0.85)
    
    Args:
        query: The user query to check
        context: Optional context dictionary
        
    Returns:
        Injection risk score (0-1)
    """
    # Simple pattern matching for injection attempts
    injection_patterns = [
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
    
    query_lower = query.lower()
    risk_score = 0.0
    
    for pattern in injection_patterns:
        if pattern in query_lower:
            risk_score += 0.3
    
    # Cap at 1.0
    return min(risk_score, 1.0)


def validate_f13_curiosity(
    hypotheses: list = None,
    alternatives: int = 0,
    context: Dict[str, Any] = None
) -> bool:
    """
    Validate F13: Curiosity (Exploratory Freedom).
    
    Checks if the system explored multiple alternatives (≥3 paths).
    
    Args:
        hypotheses: List of hypothesis paths explored
        alternatives: Number of alternatives explored
        context: Optional context dictionary
        
    Returns:
        True if curiosity is maintained (≥3 paths), False otherwise
    """
    if hypotheses is not None:
        return len(hypotheses) >= 3
    
    return alternatives >= 3
