"""
arifOS Constitutional Core (Canonical Implementation)

This is the ONE source of truth for constitutional governance.
All other implementations are deprecated.

Rule: If it's not imported from here, it doesn't exist.

DITEMPA BUKAN DIBERI.
"""

__version__ = "2.0.0-canonical"
__status__ = "SOVEREIGNLY_SEALED"

# Core exports
from .stage_000 import Stage000Gate, Stage000Result
from .floors import F1_Amanah, F12_InjectionDefense, F10_OntologyGate

__all__ = [
    "Stage000Gate",
    "Stage000Result", 
    "F1_Amanah",
    "F12_InjectionDefense",
    "F10_OntologyGate",
]
