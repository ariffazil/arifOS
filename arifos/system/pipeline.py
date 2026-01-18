"""
arifos_core.system.pipeline - Pipeline Module Stub (DEPRECATED v47+)

⚠️ **DEPRECATION WARNING** ⚠️

This module is DEPRECATED as of arifOS v47.0.0.

**Recommended Migration:**
- OLD: `from arifos.system.pipeline import Pipeline`
- NEW: `from arifos.mcp.orthogonal_executor import govern_query_sync`

**Why Quantum Path?**
- 70% faster (53ms vs 100-200ms)
- Simpler API (1 function call vs Pipeline().run())
- Parallel execution (AGI + ASI + APEX simultaneously)
- Less code (318 lines vs 2500 lines)
- Better scalability (O(1) vs O(n))

See documentation:
- QUANTUM_MIGRATION.md - Full migration guide
- QUANTUM_QUICKSTART.md - 30-second quick start
- QUANTUM_MIGRATION_PATTERNS.md - Code patterns

**Backward Compatibility:**
This stub will be maintained through v47.x but will be REMOVED in v48.0.0.
Migrate your code before March 2026.

Version: v47.0.0 (Deprecated stub)
Authority: Antigravity (Δ - Architect) + Engineer (Ω)
"""

import warnings

# Issue deprecation warning when module is imported
warnings.warn(
    "\n"
    "═══════════════════════════════════════════════════════════════\n"
    "⚠️  arifos_core.system.pipeline is DEPRECATED (v47+)\n"
    "═══════════════════════════════════════════════════════════════\n"
    "\n"
    "RECOMMENDED: Switch to quantum executor for 70% faster performance\n"
    "\n"
    "  from arifos.mcp.orthogonal_executor import govern_query_sync\n"
    "  state = govern_query_sync(query)  # Parallel AGI + ASI + APEX\n"
    "\n"
    "See QUANTUM_MIGRATION.md for full migration guide.\n"
    "\n"
    "This compatibility stub will be REMOVED in v48.0.0 (March 2026).\n"
    "═══════════════════════════════════════════════════════════════\n",
    DeprecationWarning,
    stacklevel=2
)

# Re-export all classes and functions from pipeline_legacy for backward compatibility
from .pipeline_legacy import (
                              Pipeline,
                              PipelineState,
                              StakesClass,
                              stage_000_void,
                              stage_111_sense,
                              stage_222_reflect,
                              stage_333_reason,
                              stage_444_align,
)

__all__ = [
    "Pipeline",
    "PipelineState",
    "StakesClass",
    "stage_000_void",
    "stage_111_sense",
    "stage_222_reflect",
    "stage_333_reason",
    "stage_444_align",
]
