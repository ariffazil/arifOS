"""
arifOS Session Guards Package (Deprecated in v47)

This package has been moved to arifos_core.hypervisor in v47 Equilibrium Architecture.
Backward compatibility imports are provided below.

Use: from arifos_core.hypervisor import InjectionGuard
Instead of: from arifos_core.guards import InjectionGuard

Current components (v46.0):
    - session_dependency.py: SessionDuration / interaction density guard (v45)
    - ontology_guard.py: F10 - Literalism detection (v46.0 hypervisor)
    - nonce_manager.py: F11 - Identity verification (v46.0 hypervisor)
    - injection_guard.py: F12 - Injection defense (v46.0 hypervisor)
"""

from __future__ import annotations

import warnings

# Import from new location (hypervisor) for backward compatibility
from arifos_core.hypervisor.guards.injection_guard import (
    InjectionGuard,
    InjectionGuardResult,
    InjectionRisk,
    scan_for_injection,
)
from arifos_core.hypervisor.guards.nonce_manager import (
    NonceManager,
    NonceStatus,
    NonceVerificationResult,
    SessionNonce,
)
from arifos_core.hypervisor.guards.ontology_guard import (
    OntologyGuard,
    OntologyGuardResult,
    OntologyRisk,
    detect_literalism,
)
from arifos_core.hypervisor.guards.session_dependency import (
    DependencyGuard,
    SessionRisk,
    SessionState,
)


def _issue_deprecation_warning():
    """Issue deprecation warning for guards imports."""
    warnings.warn(
        "Importing from arifos_core.guards is deprecated. "
        "Use 'from arifos_core.hypervisor import ...' instead. "
        "This compatibility shim will be removed in v48.",
        DeprecationWarning,
        stacklevel=3
    )


def __getattr__(name):
    """Intercept module-level attribute access."""
    _issue_deprecation_warning()
    return globals().get(name)


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

