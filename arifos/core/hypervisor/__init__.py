"""
arifOS Hypervisor Layer (v47)

The hypervisor layer provides system-level guards and controls:
- Injection protection
- Session management
- Nonce handling
- Ontology constraints

Extracted from arifos.core.guards as part of v47 Equilibrium Architecture
to achieve clear separation between enforcement (what should happen) and
hypervisor (system-level protection).

Design principle: Hypervisor = OS-level protection, Enforcement = Policy execution
"""

# Re-export guards for convenience
from .guards.injection_guard import InjectionGuard, InjectionRisk, InjectionGuardResult, scan_for_injection
from .guards.nonce_manager import NonceManager, NonceStatus, NonceVerificationResult, SessionNonce
from .guards.ontology_guard import OntologyGuard, OntologyRisk, OntologyGuardResult, detect_literalism
from .guards.session_dependency import DependencyGuard, SessionRisk, SessionState

# Alias for backward compatibility
SessionDependencyGuard = DependencyGuard

__all__ = [
    # Injection Guard (F12)
    "InjectionGuard",
    "InjectionRisk",
    "InjectionGuardResult",
    "scan_for_injection",
    # Nonce Manager (F11)
    "NonceManager",
    "NonceStatus",
    "NonceVerificationResult",
    "SessionNonce",
    # Ontology Guard (F10)
    "OntologyGuard",
    "OntologyRisk",
    "OntologyGuardResult",
    "detect_literalism",
    # Session Dependency
    "DependencyGuard",
    "SessionDependencyGuard",
    "SessionRisk",
    "SessionState",
]
