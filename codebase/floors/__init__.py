"""
codebase/floors/__init__.py
Constitutional Floor Modules (F1-F13)
v55.0: Exports GeniusCalculator and legacy floor placeholders
"""

from codebase.floors.genius import GeniusCalculator


# Legacy floor placeholders for backward compatibility
# TODO v56: replace with real floor modules once migrated
class F1_Amanah:
    """F1: Trust/Audit (Reversibility) - Placeholder"""

    pass


class AmanahCovenant:
    """Alias shim for legacy imports expecting AmanahCovenant."""

    pass


class F10_OntologyGate:
    """F10: Ontology wall placeholder (legacy import shim)."""

    pass


class OntologyResult:
    """Alias shim for legacy imports expecting OntologyResult."""

    pass


class F12_InjectionDefense:
    """F12: Injection defense placeholder (legacy import shim)."""

    pass


class InjectionDefenseResult:
    """Alias shim for legacy imports expecting InjectionDefenseResult."""

    pass


__all__ = [
    "GeniusCalculator",
    "F1_Amanah",
    "AmanahCovenant",
    "F10_OntologyGate",
    "OntologyResult",
    "F12_InjectionDefense",
    "InjectionDefenseResult",
]
