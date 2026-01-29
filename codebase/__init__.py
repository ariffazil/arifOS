"""
codebase/__init__.py — Constitutional AI Core Exports (v53.1.0-SEAL)
Authority: Muhammad Arif bin Fazil

This is the root export module for codebase.
Heavy modules are imported lazily to avoid circular imports and startup delays.

Architecture: Trinity Parallel Metabolic Loop
Motto: DITEMPA BUKAN DIBERI (Forged, Not Given)

Usage:
    from codebase.stages import stage_444, stage_555, stage_666
    from codebase.system.types import Verdict, Metrics
"""

# =============================================================================
# PACKAGE METADATA (lightweight - no heavy imports)
# =============================================================================
__version__ = "53.2.9"
__author__ = "Muhammad Arif bin Fazil"
__motto__ = "DITEMPA BUKAN DIBERI"

# =============================================================================
# LAZY IMPORTS (only load when accessed)
# =============================================================================
# Heavy modules are NOT imported at package level to avoid:
# 1. Circular import issues
# 2. Slow startup times
# 3. Import hangs during Railway deployment
#
# To import specific modules, use:
#   from codebase.agi import AGINeuralCore
#   from codebase.asi import ASIKernel
#   from codebase.apex import APEXJudicialCore
#   from codebase.stages import stage_444
#   from codebase.system.types import Verdict, Metrics

# =============================================================================
# PUBLIC API (__all__) - Metadata only
# =============================================================================
__all__ = [
    "__version__",
    "__author__",
    "__motto__",
]
