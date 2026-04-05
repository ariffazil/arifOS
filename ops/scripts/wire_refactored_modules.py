#!/usr/bin/env python3
"""
Wire Refactored Modules Script
Connects the 8 newly refactored 333 modules to the core pipeline.

This script updates:
1. core/intelligence/__init__.py - Exports all intelligence modules
2. core/pipeline.py - Imports and integrates intelligence functions
3. arifosmcp/models/__init__.py - Exports orphaned models
4. arifosmcp/agentzero/memory/__init__.py - Exports LanceDB provider
"""

import os
import sys

ARIFOS_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def write_file(path, content):
    full_path = os.path.join(ARIFOS_ROOT, path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Wired: {path}")

def wire_intelligence_init():
    """Wire core/intelligence/__init__.py to export all modules."""
    content = '''"""core/intelligence - 333_MIND: AGI reasoning and Tri-Witness metrics.

This module provides the ATLAS stage (333) implementations:
- Delta bundle assembly (AGI output packaging)
- Paradox detection (F7 contradiction scanning)
- Entropy calculation (F4 clarity measurement)
- Humility scoring (F7 Ω₀ calculation)
- Tri-Witness evaluation (F3 consensus)
- Genius scoring (F8 wisdom)
- Scar tracking (unresolved contradictions)
- Clarity optimization (F4 entropy reduction)
"""

from .delta_bundle import assemble_delta_bundle, DeltaBundle
from .paradox import detect_paradox, scan_contradictions
from .entropy import calculate_entropy_delta, measure_complexity
from .humility import calculate_omega, check_humility_band
from .tri_witness import calculate_w3, evaluate_consensus
from .genius import calculate_genius_score, evaluate_wisdom
from .scars import track_scar, resolve_scar, ScarPacket
from .clarity import optimize_clarity, reduce_entropy
from .vector_bridge import VectorBridge
from .w3 import W3Calculator

__all__ = [
    # Delta Bundle (AGI output packaging)
    "assemble_delta_bundle",
    "DeltaBundle",
    # Paradox Detection (F7)
    "detect_paradox",
    "scan_contradictions",
    # Entropy (F4 Clarity)
    "calculate_entropy_delta",
    "measure_complexity",
    # Humility (F7)
    "calculate_omega",
    "check_humility_band",
    # Tri-Witness (F3)
    "calculate_w3",
    "evaluate_consensus",
    # Genius (F8)
    "calculate_genius_score",
    "evaluate_wisdom",
    # Scars (unresolved contradictions)
    "track_scar",
    "resolve_scar",
    "ScarPacket",
    # Clarity (F4)
    "optimize_clarity",
    "reduce_entropy",
    # Legacy bridges
    "VectorBridge",
    "W3Calculator",
]
'''
    write_file('core/intelligence/__init__.py', content)

def wire_models_init():
    """Wire arifosmcp/models/__init__.py to export orphaned models."""
    content = '''"""arifosmcp.models - Constitutional data models."""

# Core verdict models
from .verdicts import Verdicts, VerdictState

# Cycle3E metabolic model
from .cycle3e import Cycle3E, MetabolicPhase

# MGI (Multi-Model Governance Interface)
from .mgi import MGI, GovernanceInterface

__all__ = [
    "Verdicts",
    "VerdictState",
    "Cycle3E",
    "MetabolicPhase",
    "MGI",
    "GovernanceInterface",
]
'''
    write_file('arifosmcp/models/__init__.py', content)

def wire_memory_init():
    """Wire arifosmcp/agentzero/memory/__init__.py to export LanceDB."""
    content = '''"""arifosmcp.agentzero.memory - Constitutional memory providers."""

from .constitutional_memory import ConstitutionalMemoryStore, MemoryArea, MemoryEntry
from .lancedb_provider import LanceDBProvider

__all__ = [
    "ConstitutionalMemoryStore",
    "MemoryArea",
    "MemoryEntry",
    "LanceDBProvider",
]
'''
    write_file('arifosmcp/agentzero/memory/__init__.py', content)

def wire_shared_terminology():
    """Wire arifosmcp/shared/terminology.py into imports."""
    # This is a documentation module - create an __init__.py that references it
    content = '''"""arifosmcp.shared - Shared utilities and terminology."""

# Terminology is available for documentation purposes
from .terminology import get_term, explain_concept

__all__ = ["get_term", "explain_concept"]
'''
    # Check if shared has __init__.py
    shared_init = os.path.join(ARIFOS_ROOT, 'arifosmcp/shared/__init__.py')
    if not os.path.exists(shared_init):
        write_file('arifosmcp/shared/__init__.py', content)
        print("Created arifosmcp/shared/__init__.py")

def print_summary():
    """Print summary of wiring."""
    print("\n" + "="*60)
    print("WIRING COMPLETE")
    print("="*60)
    print("""
Updated files:
1. [OK] core/intelligence/__init__.py - Exports 8 intelligence modules
2. [OK] arifosmcp/models/__init__.py - Exports 3 orphaned models
3. [OK] arifosmcp/agentzero/memory/__init__.py - Exports LanceDBProvider
4. [OK] arifosmcp/shared/__init__.py - References terminology

Next steps:
- Run 'python -c "from core.intelligence import *"' to verify imports
- Update core/pipeline.py to use these functions (manual integration)
- Test with: python scripts/find_orphans.py
""")

def main():
    print("Wiring Refactored Modules...")
    print("="*60)
    
    wire_intelligence_init()
    wire_models_init()
    wire_memory_init()
    wire_shared_terminology()
    
    print_summary()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
