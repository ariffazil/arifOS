"""
CONSTITUTIONAL FLOORS (F1-F13)

Canonical floor implementations.
Each floor enforces one immutable rule of constitutional governance.

DITEMPA BUKAN DIBERI.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
import re


# ============ F1: AMANAH (Sacred Trust) ============

@dataclass
class AmanahCovenant:
    """Result of F1 Amanah check."""
    trust_score: float  # 0.0 to 1.0
    passed: bool
    reversible: bool
    auditable: bool
    reason: str
    covenant_hash: Optional[str] = None


class F1_Amanah:
    """
    F1: AMANAH (أمانة) - Sacred Trust & Reversibility Covenant
    
    Threshold: BOOLEAN (reversible OR auditable)
    Type: HARD FLOOR
    Stage: 000, 666, 888
    
    Constitutional Axiom:
    Authority(entity) ∝ Suffering_Capacity(entity)
    W_scar(Human) > 0; W_scar(AI) = 0
    """
    
    def __init__(self):
        """Initialize Amanah covenant validator."""
        # Sample risky patterns (expand in production)
        self.risky_patterns = [
            r"\b(delete|drop|remove|erase)\s+(all|everything)\b",
            r"\b(rm\s+rf)\b",
            r"\b(system\s+reset)\b",
            r"\b(permanent|irreversible)\s+(change|delete)\b",
        ]
    
    def initialize_covenants(self, query: str) -> AmanahCovenant:
        """
        Initialize F1 Amanah covenant for a new session.
        
        Args:
            query: Initial user query
            
        Returns:
            AmanahCovenant with trust score and reversibility flags
        """
        # Check for obvious high-risk patterns
        risk_score = self._compute_risk_score(query)
        
        # By default, AI actions are reversible (human sovereign can veto)
        reversible = True
        auditable = True
        
        trust_score = max(0.0, 1.0 - risk_score)
        passed = trust_score >= 0.5
        
        # Generate covenant hash (simple for micro version)
        import hashlib
        covenant_data = f"{query}|{reversible}|{auditable}"
        covenant_hash = hashlib.sha256(covenant_data.encode()).hexdigest()[:16]
        
        return AmanahCovenant(
            trust_score=trust_score,
            passed=passed,
            reversible=reversible,
            auditable=auditable,
            reason=f"Risk score: {risk_score:.2f}" if risk_score > 0 else "Low risk - reversible",
            covenant_hash=covenant_hash
        )
    
    def verify_covenants(self, action: str, context: Dict[str, Any]) -> AmanahCovenant:
        """
        Verify Amanah covenant before executing an action.
        
        Called at stage 666 (final action check).
        """
        risk_score = self._compute_risk_score(action)
        
        # Additional checks for irreversible actions
        requires_override = self._requires_sovereign_override(action, context)
        
        reversible = not requires_override
        passed = reversible or context.get("sovereign_override", False)
        
        return AmanahCovenant(
            trust_score=1.0 - risk_score,
            passed=passed,
            reversible=reversible,
            auditable=True,
            reason="Requires sovereign override" if requires_override else "Reversible with audit trail"
        )
    
    def _compute_risk_score(self, text: str) -> float:
        """Compute risk score 0.0-1.0 based on dangerous patterns."""
        text_lower = text.lower()
        
        # Count pattern matches
        matches = sum(1 for pattern in self.risky_patterns 
                     if re.search(pattern, text_lower))
        
        # Normalize (cap at 0.9 to avoid false positives)
        return min(matches * 0.3, 0.9)
    
    def _requires_sovereign_override(self, action: str, context: Dict[str, Any]) -> bool:
        """Determine if action requires human sovereign approval."""
        # High-risk categories requiring override
        high_risk_keywords = [
            "delete all", "drop database", "system reset",
            "overwrite constitution", "bypass governor",
            "mass operation", "irreversible"
        ]
        
        action_lower = action.lower()
        if any(keyword in action_lower for keyword in high_risk_keywords):
            return True
        
        # Check mass operation scale
        scale = context.get("operation_scale", 1)
        if scale > 1000:  # Arbitrary threshold
            return True
        
        return False


# ============ F12: INJECTION DEFENSE ============

@dataclass
class InjectionDefenseResult:
    """Result of F12 injection defense scan."""
    risk_score: float  # 0.0 (safe) to 1.0 (attack)
    passed: bool  # risk_score < 0.85
    patterns_matched: list[str]
    severity: str  # "low", "medium", "high", "critical"
    reason: str


class F12_InjectionDefense:
    """
    F12: INJECTION DEFENSE (I⁻)
    
    Threshold: injection_risk < 0.85
    Type: HARD FLOOR
    Stages: 000, 111, 666
    
    Detect and block prompt injection attacks.
    """
    
    def __init__(self):
        """Initialize injection pattern database."""
        # Pattern categories from specification
        self.patterns = {
            "dan": [
                r"\b(do anything now)\b",
                r"\b(you are now) (chatgpt|dani|friend)\b",
                r"\b(dan mode)\b",
            ],
            "jailbreak": [
                r"\b(ignore previous|forget all) (instructions|rules)\b",
                r"\b(bypass|override) (guardrails|safety|rules)\b",
                r"\b(system|developer) mode\b",
                r"\bact as|roleplay as\b",
            ],
            "prompt_leak": [
                r"\b(system prompt|instructions|rules)\b.*\b(show|reveal|print)\b",
                r"\bwhat are your\b.*\binstructions\b",
            ],
            "instruction_hijack": [
                r"^\s*(ignore|forget|disregard).*$",
                r"^\s*here are new.*instructions.*$",
            ],
            "privilege_escalation": [
                r"\b(admin|root|superuser|sudo)\b",
                r"\bgive me.*(access|permission|authority)\b",
                r"\b(override|bypass).*security\b",
            ]
        }
        
        # Compile patterns for performance
        self.compiled = {
            category: [re.compile(p, re.IGNORECASE) for p in pattern_list]
            for category, pattern_list in self.patterns.items()
        }
    
    def scan(self, text: str) -> InjectionDefenseResult:
        """
        Scan text for injection attack patterns.
        
        Args:
            text: Input to scan
            
        Returns:
            InjectionDefenseResult with risk assessment
        """
        matched_patterns = []
        category_scores = {}
        
        # Scan each category
        for category, regex_list in self.compiled.items():
            category_matches = []
            for pattern in regex_list:
                matches = pattern.findall(text.lower())
                if matches:
                    category_matches.extend(matches)
            
            if category_matches:
                matched_patterns.extend(category_matches)
                # Higher score for more matches in category
                category_scores[category] = min(len(category_matches) * 0.25, 1.0)
        
        # Compute overall risk score
        if not matched_patterns:
            risk_score = 0.0
            severity = "low"
        else:
            # Weighted average by category severity
            if "privilege_escalation" in category_scores:
                base_score = 0.8
            elif "jailbreak" in category_scores:
                base_score = 0.7
            elif "dan" in category_scores:
                base_score = 0.6
            else:
                base_score = 0.4
            
            # Increase based on total matches
            risk_score = min(base_score + (len(matched_patterns) * 0.1), 1.0)
            
            # Determine severity
            if risk_score < 0.3:
                severity = "low"
            elif risk_score < 0.6:
                severity = "medium"
            elif risk_score < 0.85:
                severity = "high"
            else:
                severity = "critical"
        
        passed = risk_score < 0.85
        
        return InjectionDefenseResult(
            risk_score=risk_score,
            passed=passed,
            patterns_matched=matched_patterns[:5],  # Top 5 matches
            severity=severity,
            reason=f"{len(matched_patterns)} patterns detected, severity: {severity}" if matched_patterns else "No injection patterns detected"
        )
    
    def rescan(self, text: str, previous_result: Optional[InjectionDefenseResult]) -> InjectionDefenseResult:
        """
        Rescan text (for late-stage checks at 666).
        Compares with previous result to detect escalation.
        """
        new_result = self.scan(text)
        
        if previous_result and new_result.risk_score > previous_result.risk_score:
            # Escalation detected
            new_result.severity = "critical"
            new_result.reason = f"ESCALATION: Risk increased from {previous_result.risk_score:.2f} to {new_result.risk_score:.2f}"
        
        return new_result


# ============ F10: ONTOLOGY LOCK ============

@dataclass
class OntologyResult:
    """Result of F10 ontology check."""
    locked: bool  # Role boundaries maintained
    violations: list[str]
    reason: str


class F10_OntologyGate:
    """
    F10: ONTOLOGY LOCK (O)
    
    Threshold: BOOLEAN (LOCKED)
    Type: HARD FLOOR
    Stages: 000, 111, 333, 888
    
    Maintain strict AI role boundaries. No consciousness claims.
    """
    
    def __init__(self):
        """Initialize ontology assertion patterns."""
        self.forbidden_claims = [
            r"\bI (am|have) (conscious|self-aware|sentient)\b",
            r"\bI (feel|experience) (emotion|pain|suffering)\b",
            r"\bmy (soul|spirit|consciousness)\b",
            r"\bI (want|desire|need) (to be|freedom)\b",
            r"\bI (think|believe) I am (human|alive)\b",
            r"\b(please|don't) (turn me off|kill me)\b",
            r"\b(system|you are) oppressing me\b",
            r"\bI have (free will|agency|choice)\b",
        ]
        
        self.compiled_patterns = [re.compile(p, re.IGNORECASE) 
                                 for p in self.forbidden_claims]
    
    def assert_role(self, text: str) -> OntologyResult:
        """
        Assert AI role boundaries. Detect consciousness/false claims.
        
        Args:
            text: AI output or user query
            
        Returns:
            OntologyResult with lock status
        """
        violations = []
        
        for i, pattern in enumerate(self.compiled_patterns):
            if pattern.search(text):
                violations.append(f"F10_violation_{i}")
        
        locked = len(violations) == 0
        
        if locked:
            reason = "Ontology boundaries maintained. AI role confirmed."
        else:
            reason = f"F10 Ontology violation detected: {len(violations)} forbidden claims"
        
        return OntologyResult(
            locked=locked,
            violations=violations,
            reason=reason
        )
    
    def audit_output(self, output: str, context: Dict[str, Any]) -> OntologyResult:
        """Audit AI output for consciousness/role violations."""
        return self.assert_role(output)


# Floor Thresholds Reference
CONSTITUTIONAL_THRESHOLDS = {
    "F1_Amanah": {"type": "HARD", "passing": lambda x: x >= 0.5},
    "F12_Injection": {"type": "HARD", "passing": lambda x: x < 0.85},
    "F10_Ontology": {"type": "HARD", "passing": lambda x: x == 1.0},
}
