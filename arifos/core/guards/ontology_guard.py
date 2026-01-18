"""
DEPRECATED: This module has moved to arifos_core.hypervisor.guards.ontology_guard

Ontology validation belongs in the hypervisor layer (F10 Ontology/Symbolic).
This shim will be removed in v47.2 (72 hours after v47.1 release).

Update your imports:
  OLD: from arifos.core.guards.ontology_guard import OntologyGuard
  NEW: from arifos.core.hypervisor.guards.ontology_guard import OntologyGuard

Constitutional Mapping:
- Old Location: guards/ (incorrect layer)
- New Location: hypervisor/guards/ (F10 Ontology/Symbolic)
- Related Theory: See 000_THEORY/canon/012_enforcement/F10_ONTOLOGY.md
"""
import warnings

warnings.warn(
    "arifos_core.guards.ontology_guard is deprecated. "
    "Use arifos_core.hypervisor.guards.ontology_guard instead. "
    "This shim will be removed in v47.2 (72 hours after v47.1).",
    DeprecationWarning,
    stacklevel=2
)

# Re-export everything from new location
from arifos.core.hypervisor.guards.ontology_guard import *
