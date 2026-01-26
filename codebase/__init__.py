"""
codebase/__init__.py — Constitutional AI Core Exports (v52.5.1-SEAL)
Authority: Muhammad Arif bin Fazil

This is the root export module for codebase.
All commonly used modules are re-exported here for clean imports.

Architecture: Trinity Parallel Metabolic Loop
Motto: DITEMPA BUKAN DIBERI (Forged, Not Given)

Usage:
    from codebase import stage_444, stage_555, stage_666
    from codebase import Verdict
    from codebase.pipeline import execute_metabolic_loop
"""

# =============================================================================
# PACKAGE METADATA
# =============================================================================
__version__ = "52.5.1"
__author__ = "Muhammad Arif bin Fazil"
__motto__ = "DITEMPA BUKAN DIBERI"

# =============================================================================
# STAGE MODULES (444-889)
# Re-export from stages/ subdirectory for clean imports
# =============================================================================
from codebase.stages import stage_444
from codebase.stages import stage_555
from codebase.stages import stage_666
from codebase.stages import stage_777_forge
from codebase.stages import stage_888_judge
from codebase.stages import stage_889_proof

# =============================================================================
# TYPE DEFINITIONS (verified exports from types.py)
# =============================================================================
from codebase.system.types import (
    Verdict,
    Metrics,
    FloorCheckResult,
    ApexVerdict,
)

# =============================================================================
# EXCEPTIONS (verified exports from exceptions.py)
# =============================================================================
from codebase.exceptions import (
    ConstitutionalError,
    InjectionAttemptError,
    AuthorityViolationError,
    OntologyViolationError,
    AmanahViolationError,
)

# =============================================================================
# PUBLIC API (__all__)
# =============================================================================
__all__ = [
    # Metadata
    "__version__",
    "__author__",
    "__motto__",
    # Stages
    "stage_444",
    "stage_555",
    "stage_666",
    "stage_777_forge",
    "stage_888_judge",
    "stage_889_proof",
    # Types
    "Verdict",
    "Metrics",
    "FloorCheckResult",
    "ApexVerdict",
    # Exceptions
    "ConstitutionalError",
    "InjectionAttemptError",
    "AuthorityViolationError",
    "OntologyViolationError",
    "AmanahViolationError",
]
