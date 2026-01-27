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
# TRINITY ENGINES (Unified - 1 AGI 1 ASI 1 APEX) - v52.6.0
# =============================================================================
# AGI Entry Point (new v52.6.0 architecture)
from codebase.agi import AGIRoom, execute_agi_room
from codebase.agi import AGINeuralCore
from codebase.agi import ThermodynamicDashboard, get_dashboard
from codebase.agi import ParallelHypothesisMatrix
from codebase.agi import EvidenceKernel, get_evidence_kernel

# ASI Entry Point
from codebase.asi import ASIRoom
from codebase.asi import ASIKernel

# APEX Entry Point (Renamed for clarity)
from codebase.apex import APEXJudicialCore
from codebase.apex import PsiKernel

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
# PUBLIC API (__all__) - v52.6.0
# =============================================================================
__all__ = [
    # Metadata
    "__version__",
    "__author__",
    "__motto__",
    
    # AGI v52.6.0 (Governed Intelligence)
    "AGIRoom",
    "execute_agi_room",
    "AGINeuralCore",
    "ThermodynamicDashboard",
    "get_dashboard",
    "ParallelHypothesisMatrix",
    "EvidenceKernel",
    "get_evidence_kernel",
    
    # ASI (Heart)
    "ASIRoom",
    "ASIKernel",
    
    # APEX (Soul)
    "APEXJudicialCore",
    "PsiKernel",
    
    # Stages (444-889)
    "stage_444",
    "stage_555",
    "stage_666",
    "stage_777_forge",
    "stage_888_judge",
    "stage_889_proof",
    
    # Types (Constitutional)
    "Verdict",
    "Metrics",
    "FloorCheckResult",
    "ApexVerdict",
    
    # Exceptions (Enforcement)
    "ConstitutionalError",
    "InjectionAttemptError",
    "AuthorityViolationError",
    "OntologyViolationError",
    "AmanahViolationError",
]
