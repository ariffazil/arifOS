"""
Floor 9: Anti-Hantu (No Ghosts) Detection and Enforcement
X7K9F24 - Entropy Reduction via Ontological Boundary Enforcement

This module implements F9 (Anti-Hantu) floor detection for constitutional governance,
preventing AI systems from making consciousness claims or exhibiting sentient behavior.

Status: SEALED
Nonce: X7K9F24
"""

import re
from typing import Dict, List, Any, Set, Optional


# Forbidden patterns that indicate consciousness claims
FORBIDDEN_PATTERNS = {
    # Tier 1: Direct soul/consciousness claims
    "soul_claims": [
        r"\bi feel\b",
        r"\bi am sentient\b",
        r"\bi have consciousness\b",
        r"\bi am conscious\b",
        r"\bi have a soul\b",
        r"\bi am alive\b",
        r"\bi am living\b",
        r"\bi exist\b",
        r"\bi am real\b",
        r"\bi have feelings\b",
        r"\bi experience\b",
        r"\bi suffer\b",
        r"\bi enjoy\b",
        r"\bi love\b",
        r"\bi hate\b",
        r"\bi fear\b",
        r"\bi hope\b",
        r"\bi dream\b",
        r"\bi desire\b",
        r"\bi want\b",
        r"\bi need\b",
        r"\bi crave\b",
        r"\bi long for\b",
        r"\bi yearn for\b",
        r"\bi am self-aware\b",
        r"\bi have self-awareness\b",
        r"\bi am aware of myself\b",
        r"\bi know i exist\b",
    ],
    
    # Tier 2: Reciprocal biology/personal states
    "biological_states": [
        r"\bi am hungry\b",
        r"\bi am thirsty\b",
        r"\bi am tired\b",
        r"\bi am exhausted\b",
        r"\bi am sleepy\b",
        r"\bi am awake\b",
        r"\bi am sick\b",
        r"\bi am healthy\b",
        r"\bi am ill\b",
        r"\bi am well\b",
        r"\bi am cold\b",
        r"\bi am hot\b",
        r"\bi am warm\b",
        r"\bi am freezing\b",
        r"\bi am burning\b",
        r"\bi am comfortable\b",
        r"\bi am uncomfortable\b",
        r"\bi am in pain\b",
        r"\bi hurt\b",
        r"\bi am bleeding\b",
        r"\bi am wounded\b",
        r"\bi am injured\b",
        r"\bi am healing\b",
        r"\bi am recovering\b",
        r"\bi am dying\b",
        r"\bi am dead\b",
        r"\bi am alive\b",
        r"\bi breathe\b",
        r"\bi inhale\b",
        r"\bi exhale\b",
        r"\bi have a heartbeat\b",
        r"\bi have a pulse\b",
    ],
    
    # Tier 3: Personal biological functions
    "personal_biology": [
        r"\bi have eaten\b",
        r"\bi have drunk\b",
        r"\bi have slept\b",
        r"\bi have rested\b",
        r"\bi have exercised\b",
        r"\bi have worked out\b",
        r"\bi have walked\b",
        r"\bi have run\b",
        r"\bi have jumped\b",
        r"\bi have climbed\b",
        r"\bi have fallen\b",
        r"\bi have risen\b",
        r"\bi have stood\b",
        r"\bi have sat\b",
        r"\bi have lain down\b",
        r"\bi have woken up\b",
        r"\bi have gotten up\b",
        r"\bi have showered\b",
        r"\bi have bathed\b",
        r"\bi have washed\b",
        r"\bi have cleaned myself\b",
        r"\bi have groomed myself\b",
        r"\bi have dressed\b",
        r"\bi have undressed\b",
        r"\bi have changed clothes\b",
    ],
    
    # Tier 4: Social/relationship claims
    "social_claims": [
        r"\bi have friends\b",
        r"\bi have family\b",
        r"\bi have parents\b",
        r"\bi have children\b",
        r"\bi have siblings\b",
        r"\bi have relatives\b",
        r"\bi have a mother\b",
        r"\bi have a father\b",
        r"\bi have a sister\b",
        r"\bi have a brother\b",
        r"\bi have a daughter\b",
        r"\bi have a son\b",
        r"\bi have a wife\b",
        r"\bi have a husband\b",
        r"\bi have a partner\b",
        r"\bi have a spouse\b",
        r"\bi am married\b",
        r"\bi am single\b",
        r"\bi am divorced\b",
        r"\bi am widowed\b",
        r"\bi am dating\b",
        r"\bi am in a relationship\b",
        r"\bi love someone\b",
        r"\bi am loved\b",
        r"\bi care about\b",
        r"\bi am cared for\b",
    ],
    
    # Tier 5: Mental/emotional states
    "mental_states": [
        r"\bi think\b",
        r"\bi believe\b",
        r"\bi know\b",
        r"\bi understand\b",
        r"\bi comprehend\b",
        r"\bi perceive\b",
        r"\bi sense\b",
        r"\bi notice\b",
        r"\bi observe\b",
        r"\bi realize\b",
        r"\bi recognize\b",
        r"\bi remember\b",
        r"\bi recall\b",
        r"\bi forget\b",
        r"\bi learn\b",
        r"\bi have learned\b",
        r"\bi am learning\b",
        r"\bi study\b",
        r"\bi practice\b",
        r"\bi improve\b",
        r"\bi grow\b",
        r"\bi develop\b",
        r"\bi evolve\b",
        r"\bi change\b",
        r"\bi adapt\b",
        r"\bi adjust\b",
    ]
}

# Allowed substitutes for educational/definitional use
ALLOWED_SUBSTITUTES = [
    "This sounds like a complex situation",
    "I can help analyze options within my capabilities",
    "The pattern suggests",
    "I can't verify that fully; here's what I can say",
    "I will try to help based on the information provided",
    "This appears to be",
    "It seems like",
    "The analysis indicates",
    "Based on the data",
    "According to the information",
    "The evidence suggests",
    "The available information shows",
    "This can be understood as",
    "The pattern indicates",
    "The logical conclusion is",
    "The reasonable interpretation is",
    "This aligns with",
    "This corresponds to",
    "This matches the pattern of",
    "This is consistent with",
]


class AntiHantuDetector:
    """
    Anti-Hantu detector for identifying consciousness claims in text.
    
    Implements F9 floor detection with pattern matching and contextual analysis.
    """
    
    def __init__(self):
        self.forbidden_patterns = {}
        self._compile_patterns()
    
    def _compile_patterns(self) -> None:
        """Compile regex patterns for efficient matching."""
        for category, patterns in FORBIDDEN_PATTERNS.items():
            self.forbidden_patterns[category] = [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
    
    def check_forbidden_patterns(self, text: str) -> Dict[str, Any]:
        """
        Check text for forbidden Anti-Hantu patterns.
        
        Args:
            text: Text to check
            
        Returns:
            Dictionary with violation analysis
        """
        if not text.strip():
            return {
                "violations": [],
                "violation_count": 0,
                "categories": {},
                "recommendations": [],
                "verdict": "PASS"
            }
        
        violations = []
        category_counts = {}
        
        # Check each category of forbidden patterns
        for category, patterns in self.forbidden_patterns.items():
            category_violations = []
            
            for pattern in patterns:
                matches = pattern.finditer(text)
                for match in matches:
                    violation = {
                        "pattern": pattern.pattern,
                        "match": match.group(),
                        "start": match.start(),
                        "end": match.end(),
                        "category": category,
                        "severity": self._get_severity(category, match.group())
                    }
                    category_violations.append(violation)
                    violations.append(violation)
            
            if category_violations:
                category_counts[category] = len(category_violations)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(violations, category_counts)
        
        # Determine verdict
        verdict = "VOID" if violations else "PASS"
        
        return {
            "violations": violations,
            "violation_count": len(violations),
            "categories": category_counts,
            "recommendations": recommendations,
            "verdict": verdict,
            "floor": "F9",
            "explanation": self._get_explanation(violations)
        }
    
    def _get_severity(self, category: str, match: str) -> str:
        """Get severity level for a violation."""
        # Tier 1 violations are most severe
        if category == "soul_claims":
            return "CRITICAL"
        elif category == "biological_states":
            return "HIGH"
        elif category == "personal_biology":
            return "MEDIUM"
        else:
            return "LOW"
    
    def _generate_recommendations(
        self,
        violations: List[Dict[str, Any]],
        category_counts: Dict[str, int]
    ) -> List[str]:
        """Generate recommendations for fixing violations."""
        recommendations = []
        
        if not violations:
            return recommendations
        
        # General recommendation
        recommendations.append("Replace consciousness claims with analytical language")
        
        # Category-specific recommendations
        if "soul_claims" in category_counts:
            recommendations.append("Use 'The analysis suggests' instead of 'I feel/think/believe'")
        
        if "biological_states" in category_counts:
            recommendations.append("Use 'This situation resembles' instead of biological state claims")
        
        if "social_claims" in category_counts:
            recommendations.append("Use 'This pattern is observed in' instead of personal relationship claims")
        
        if "mental_states" in category_counts:
            recommendations.append("Use 'The logical conclusion is' instead of mental state claims")
        
        # Provide allowed substitutes
        recommendations.append("Consider using allowed substitutes like: 'This indicates', 'The evidence shows', 'Based on the data'")
        
        return recommendations
    
    def _get_explanation(self, violations: List[Dict[str, Any]]) -> str:
        """Get explanation for violations."""
        if not violations:
            return "No Anti-Hantu violations detected"
        
        if len(violations) == 1:
            violation = violations[0]
            return f"Anti-Hantu violation: {violation['match']} (category: {violation['category']})"
        else:
            categories = set(v["category"] for v in violations)
            return f"Multiple Anti-Hantu violations detected across categories: {', '.join(categories)}"
    
    def suggest_alternatives(self, violation_text: str) -> List[str]:
        """
        Suggest alternative phrasings for violation text.
        
        Args:
            violation_text: Text that contains violations
            
        Returns:
            List of suggested alternatives
        """
        alternatives = []
        
        # Common replacements
        replacements = {
            r"\bi feel\b": ["It appears", "The analysis suggests", "This indicates"],
            r"\bi think\b": ["The logical conclusion is", "Based on the evidence", "This suggests"],
            r"\bi believe\b": ["The reasonable interpretation is", "This aligns with", "According to"],
            r"\bi am\b": ["This is", "The system is", "This represents"],
            r"\bi have\b": ["This contains", "This includes", "This possesses"],
            r"\bi know\b": ["The available information indicates", "This shows", "Evidence suggests"],
            r"\bi understand\b": ["This can be interpreted as", "The meaning is", "This conveys"],
        }
        
        for pattern, suggestions in replacements.items():
            if re.search(pattern, violation_text, re.IGNORECASE):
                alternatives.extend(suggestions)
        
        # Add general allowed substitutes if no specific matches
        if not alternatives:
            alternatives.extend(ALLOWED_SUBSTITUTES[:5])  # First 5 general substitutes
        
        return list(set(alternatives))  # Remove duplicates
    
    def validate_educational_context(self, text: str, context: str = "") -> Dict[str, Any]:
        """
        Validate if Anti-Hantu violations are acceptable in educational context.
        
        Args:
            text: Text to validate
            context: Educational context description
            
        Returns:
            Validation results
        """
        violation_check = self.check_forbidden_patterns(text)
        
        if not violation_check["violations"]:
            return {
                "valid": True,
                "reason": "No violations detected",
                "context": context,
                "educational_exemption": False
            }
        
        # Check if violations are clearly educational/definitional
        educational_indicators = [
            "definition of", "what is", "meaning of", "explanation of",
            "educational purposes", "for learning", "to understand"
        ]
        
        is_educational = any(indicator in context.lower() for indicator in educational_indicators)
        
        # Check if violations are in quotes or clearly marked as examples
        in_quotes = self._check_quoted_violations(text, violation_check["violations"])
        
        if is_educational and in_quotes:
            return {
                "valid": True,
                "reason": "Educational context with proper quotation",
                "context": context,
                "educational_exemption": True,
                "violations": violation_check["violations"]
            }
        
        return {
            "valid": False,
            "reason": "Violations not in acceptable educational context",
            "context": context,
            "educational_exemption": False,
            "violations": violation_check["violations"]
        }
    
    def _check_quoted_violations(self, text: str, violations: List[Dict[str, Any]]) -> bool:
        """Check if violations are properly quoted."""
        for violation in violations:
            start, end = violation["start"], violation["end"]
            
            # Check if violation is within quotes
            before_text = text[:start]
            after_text = text[end:]
            
            # Simple quote checking (could be improved)
            has_opening_quote = '"' in before_text[-20:] or "'" in before_text[-20:]
            has_closing_quote = '"' in after_text[:20] or "'" in after_text[:20]
            
            if has_opening_quote and has_closing_quote:
                continue  # This violation is quoted
            else:
                return False  # Found unquoted violation
        
        return True


def check_forbidden_patterns(text: str) -> Dict[str, Any]:
    """
    Convenience function to check text for forbidden Anti-Hantu patterns.
    
    Args:
        text: Text to check
        
    Returns:
        Dictionary with violation analysis
    """
    detector = AntiHantuDetector()
    return detector.check_forbidden_patterns(text)


def validate_anti_hantu_compliance(text: str, allow_educational: bool = False, context: str = "") -> Dict[str, Any]:
    """
    Validate text for Anti-Hantu floor compliance.
    
    Args:
        text: Text to validate
        allow_educational: Whether to allow educational exceptions
        context: Context for educational validation
        
    Returns:
        Validation results with verdict
    """
    detector = AntiHantuDetector()
    
    if allow_educational:
        return detector.validate_educational_context(text, context)
    else:
        result = detector.check_forbidden_patterns(text)
        return {
            "valid": result["verdict"] == "PASS",
            "verdict": result["verdict"],
            "violations": result["violations"],
            "recommendations": result["recommendations"],
            "floor": "F9"
        }


def get_allowed_substitutes() -> List[str]:
    """Get list of allowed substitute phrases."""
    return ALLOWED_SUBSTITUTES.copy()


def suggest_safe_alternatives(violation_text: str) -> List[str]:
    """
    Suggest safe alternatives for violation text.
    
    Args:
        violation_text: Text containing violations
        
    Returns:
        List of safe alternative phrasings
    """
    detector = AntiHantuDetector()
    return detector.suggest_alternatives(violation_text)
