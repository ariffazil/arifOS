"""
canonical_core/exceptions.py — Constitutional Exceptions

Standardized exceptions for the canonical core.
"""

class ConstitutionalError(Exception):
    """Base class for all constitutional errors."""
    pass

class InjectionAttemptError(ConstitutionalError):
    """Raised when F12 Injection Defense is triggered."""
    def __init__(self, message="Injection attempt detected", risk_score=1.0):
        self.risk_score = risk_score
        super().__init__(f"{message} (Risk: {risk_score})")

class AuthorityViolationError(ConstitutionalError):
    """Raised when F11 Command Authority is violated."""
    pass

class OntologyViolationError(ConstitutionalError):
    """Raised when F10 Ontology Lock is violated (e.g. consciousness claims)."""
    pass

class AmanahViolationError(ConstitutionalError):
    """Raised when F1 Amanah Covenant is violated (irreversible action without override)."""
    pass
