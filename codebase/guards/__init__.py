"""
arifOS Session Guards Package

This package contains guards that operate over longer horizons
than a single model invocation (for example, session-level
dependency and usage rhythm).

Current components (v46.0):
    - session_dependency.py: SessionDuration / interaction density guard (v45)
    - ontology_guard.py: F10 - Literalism detection (v46.0 hypervisor)
    - nonce_manager.py: F11 - Identity verification (v46.0 hypervisor)
    - injection_guard.py: F12 - Injection defense (v46.0 hypervisor)
"""

from __future__ import annotations

from codebase.guards.injection_guard import (
    InjectionGuard,
    InjectionGuardResult,
    InjectionRisk,
    scan_for_injection,
)
from codebase.guards.nonce_manager import (
    NonceManager,
    NonceStatus,
    NonceVerificationResult,
    SessionNonce,
)
from codebase.guards.ontology_guard import (
    OntologyGuard,
    OntologyGuardResult,
    OntologyRisk,
    detect_literalism,
)
from codebase.guards.session_dependency import DependencyGuard, SessionRisk, SessionState

__all__ = [
    # Session dependency (v45)
    "DependencyGuard",
    "SessionRisk",
    "SessionState",
    # F10: Ontology (v46.0)
    "OntologyGuard",
    "OntologyGuardResult",
    "OntologyRisk",
    "detect_literalism",
    # F11: Nonce Auth (v46.0)
    "NonceManager",
    "NonceStatus",
    "NonceVerificationResult",
    "SessionNonce",
    # F12: Injection Defense (v46.0)
    "InjectionGuard",
    "InjectionGuardResult",
    "InjectionRisk",
    "scan_for_injection",
]

