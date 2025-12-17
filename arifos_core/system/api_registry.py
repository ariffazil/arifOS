"""
arifOS API Registry - Stability Level Enforcement

This module provides a code-level mirror of docs/API_STABILITY.md.
It defines stability levels for all public APIs and can be used by
tests to verify that exports match documented stability contracts.

Version: v42.0.0
Canon: docs/API_STABILITY.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set


class StabilityLevel(Enum):
    """API stability classification."""

    STABLE = "STABLE"  # Production-ready, 2-version deprecation
    BETA = "BETA"  # Functional, 1-version warning before changes
    EXPERIMENTAL = "EXPERIMENTAL"  # No stability guarantee
    DEPRECATED = "DEPRECATED"  # Scheduled for removal
    INTERNAL = "INTERNAL"  # Not for external use


@dataclass
class APIEntry:
    """Single API entry with stability metadata."""

    name: str
    stability: StabilityLevel
    kind: str  # "function", "class", "constant", "alias", "module"
    module: str  # Full module path
    description: str = ""
    deprecated_in: Optional[str] = None  # Version when deprecated
    removed_in: Optional[str] = None  # Version when removed
    replacement: Optional[str] = None  # Replacement API if deprecated


@dataclass
class APIRegistry:
    """
    Central registry of all public API entries.

    This mirrors docs/API_STABILITY.md and can be used by tests
    to verify code matches documentation.
    """

    entries: Dict[str, APIEntry] = field(default_factory=dict)
    _version: str = "42.0.0"

    def register(self, entry: APIEntry) -> None:
        """Register an API entry."""
        self.entries[f"{entry.module}.{entry.name}"] = entry

    def get(self, full_path: str) -> Optional[APIEntry]:
        """Get an API entry by full path."""
        return self.entries.get(full_path)

    def get_by_stability(self, stability: StabilityLevel) -> List[APIEntry]:
        """Get all entries with a given stability level."""
        return [e for e in self.entries.values() if e.stability == stability]

    def get_stable(self) -> List[APIEntry]:
        """Get all STABLE APIs."""
        return self.get_by_stability(StabilityLevel.STABLE)

    def get_deprecated(self) -> List[APIEntry]:
        """Get all DEPRECATED APIs."""
        return self.get_by_stability(StabilityLevel.DEPRECATED)

    def get_module_apis(self, module: str) -> List[APIEntry]:
        """Get all APIs from a specific module."""
        return [e for e in self.entries.values() if e.module.startswith(module)]

    def validate_exports(self, module_name: str, actual_exports: Set[str]) -> Dict:
        """
        Validate that actual exports match registry.

        Returns dict with:
        - missing: APIs in registry but not exported
        - undocumented: Exports not in registry (may need documenting)
        - valid: APIs that match
        """
        module_apis = self.get_module_apis(module_name)
        registered_names = {e.name for e in module_apis}

        return {
            "missing": registered_names - actual_exports,
            "undocumented": actual_exports - registered_names,
            "valid": registered_names & actual_exports,
        }


# =============================================================================
# GLOBAL REGISTRY INSTANCE
# =============================================================================

_REGISTRY = APIRegistry()


def get_registry() -> APIRegistry:
    """Get the global API registry."""
    return _REGISTRY


# =============================================================================
# TOP-LEVEL EXPORTS (from arifos_core import ...)
# =============================================================================

# Metrics & Floor Types
_REGISTRY.register(APIEntry(
    name="Metrics",
    stability=StabilityLevel.STABLE,
    kind="dataclass",
    module="arifos_core",
    description="Floor metric container (F1-F9 values)",
))
_REGISTRY.register(APIEntry(
    name="FloorsVerdict",
    stability=StabilityLevel.STABLE,
    kind="dataclass",
    module="arifos_core",
    description="Floor check result",
))
_REGISTRY.register(APIEntry(
    name="ConstitutionalMetrics",
    stability=StabilityLevel.STABLE,
    kind="dataclass",
    module="arifos_core",
    description="Extended constitutional metrics",
))

# APEX PRIME
_REGISTRY.register(APIEntry(
    name="apex_review",
    stability=StabilityLevel.STABLE,
    kind="function",
    module="arifos_core",
    description="Main judiciary entry point",
))
_REGISTRY.register(APIEntry(
    name="ApexVerdict",
    stability=StabilityLevel.STABLE,
    kind="dataclass",
    module="arifos_core",
    description="APEX PRIME verdict result",
))
_REGISTRY.register(APIEntry(
    name="Verdict",
    stability=StabilityLevel.STABLE,
    kind="enum",
    module="arifos_core",
    description="SEAL/PARTIAL/VOID/888_HOLD/SABAR/SUNSET",
))
_REGISTRY.register(APIEntry(
    name="check_floors",
    stability=StabilityLevel.STABLE,
    kind="function",
    module="arifos_core",
    description="Check all 9 floors",
))
_REGISTRY.register(APIEntry(
    name="APEXPrime",
    stability=StabilityLevel.STABLE,
    kind="class",
    module="arifos_core",
    description="Judiciary engine class",
))
_REGISTRY.register(APIEntry(
    name="APEX_VERSION",
    stability=StabilityLevel.STABLE,
    kind="constant",
    module="arifos_core",
    description="Current APEX version string",
))
_REGISTRY.register(APIEntry(
    name="APEX_EPOCH",
    stability=StabilityLevel.STABLE,
    kind="constant",
    module="arifos_core",
    description="Current epoch identifier",
))

# @EYE Sentinel
_REGISTRY.register(APIEntry(
    name="AlertSeverity",
    stability=StabilityLevel.STABLE,
    kind="enum",
    module="arifos_core",
    description="@EYE alert severity levels",
))
_REGISTRY.register(APIEntry(
    name="EyeAlert",
    stability=StabilityLevel.STABLE,
    kind="dataclass",
    module="arifos_core",
    description="@EYE alert structure",
))
_REGISTRY.register(APIEntry(
    name="EyeReport",
    stability=StabilityLevel.STABLE,
    kind="dataclass",
    module="arifos_core",
    description="@EYE report container",
))
_REGISTRY.register(APIEntry(
    name="EyeSentinel",
    stability=StabilityLevel.STABLE,
    kind="class",
    module="arifos_core",
    description="@EYE multi-view sentinel",
))

# Memory
_REGISTRY.register(APIEntry(
    name="log_cooling_entry",
    stability=StabilityLevel.STABLE,
    kind="function",
    module="arifos_core",
    description="Log to cooling ledger",
))

# Guard
_REGISTRY.register(APIEntry(
    name="apex_guardrail",
    stability=StabilityLevel.STABLE,
    kind="function",
    module="arifos_core",
    description="Guard wrapper for LLM calls",
))
_REGISTRY.register(APIEntry(
    name="GuardrailError",
    stability=StabilityLevel.STABLE,
    kind="exception",
    module="arifos_core",
    description="Guardrail exception class",
))

# GENIUS LAW
_REGISTRY.register(APIEntry(
    name="evaluate_genius_law",
    stability=StabilityLevel.STABLE,
    kind="function",
    module="arifos_core",
    description="GENIUS LAW evaluation",
))
_REGISTRY.register(APIEntry(
    name="GeniusVerdict",
    stability=StabilityLevel.STABLE,
    kind="dataclass",
    module="arifos_core",
    description="GENIUS evaluation result",
))
_REGISTRY.register(APIEntry(
    name="compute_genius_index",
    stability=StabilityLevel.STABLE,
    kind="function",
    module="arifos_core",
    description="Compute G index",
))
_REGISTRY.register(APIEntry(
    name="compute_dark_cleverness",
    stability=StabilityLevel.STABLE,
    kind="function",
    module="arifos_core",
    description="Compute C_dark",
))
_REGISTRY.register(APIEntry(
    name="compute_psi_apex",
    stability=StabilityLevel.STABLE,
    kind="function",
    module="arifos_core",
    description="Compute Psi vitality",
))

# AGI·ASI·APEX Trinity
_REGISTRY.register(APIEntry(
    name="AGI",
    stability=StabilityLevel.STABLE,
    kind="class",
    module="arifos_core",
    description="AGI (Delta) engine - cold logic",
))
_REGISTRY.register(APIEntry(
    name="ASI",
    stability=StabilityLevel.STABLE,
    kind="class",
    module="arifos_core",
    description="ASI (Omega) engine - warm logic",
))
_REGISTRY.register(APIEntry(
    name="evaluate_session",
    stability=StabilityLevel.STABLE,
    kind="function",
    module="arifos_core",
    description="Full session evaluation",
))
_REGISTRY.register(APIEntry(
    name="EvaluationResult",
    stability=StabilityLevel.STABLE,
    kind="dataclass",
    module="arifos_core",
    description="Evaluation result",
))
_REGISTRY.register(APIEntry(
    name="SentinelResult",
    stability=StabilityLevel.STABLE,
    kind="dataclass",
    module="arifos_core",
    description="AGI scan result",
))
_REGISTRY.register(APIEntry(
    name="ASIResult",
    stability=StabilityLevel.STABLE,
    kind="dataclass",
    module="arifos_core",
    description="ASI assessment result",
))
_REGISTRY.register(APIEntry(
    name="EvaluationMode",
    stability=StabilityLevel.STABLE,
    kind="enum",
    module="arifos_core",
    description="Evaluation mode flags",
))

# RED_PATTERNS
_REGISTRY.register(APIEntry(
    name="RED_PATTERNS",
    stability=StabilityLevel.STABLE,
    kind="constant",
    module="arifos_core",
    description="Red pattern definitions",
))
_REGISTRY.register(APIEntry(
    name="RED_PATTERN_TO_FLOOR",
    stability=StabilityLevel.STABLE,
    kind="constant",
    module="arifos_core",
    description="Pattern to floor mapping",
))
_REGISTRY.register(APIEntry(
    name="RED_PATTERN_SEVERITY",
    stability=StabilityLevel.STABLE,
    kind="constant",
    module="arifos_core",
    description="Pattern severity levels",
))

# DEPRECATED - Legacy aliases
_REGISTRY.register(APIEntry(
    name="Sentinel",
    stability=StabilityLevel.DEPRECATED,
    kind="alias",
    module="arifos_core",
    description="Alias for AGI",
    deprecated_in="v42.0",
    removed_in="v43.0",
    replacement="AGI",
))
_REGISTRY.register(APIEntry(
    name="Accountant",
    stability=StabilityLevel.DEPRECATED,
    kind="alias",
    module="arifos_core",
    description="Alias for ASI",
    deprecated_in="v42.0",
    removed_in="v43.0",
    replacement="ASI",
))
_REGISTRY.register(APIEntry(
    name="AccountantResult",
    stability=StabilityLevel.DEPRECATED,
    kind="alias",
    module="arifos_core",
    description="Alias for ASIResult",
    deprecated_in="v42.0",
    removed_in="v43.0",
    replacement="ASIResult",
))
_REGISTRY.register(APIEntry(
    name="check_red_patterns",
    stability=StabilityLevel.DEPRECATED,
    kind="function",
    module="arifos_core",
    description="Legacy pattern checker",
    deprecated_in="v42.0",
    removed_in="v43.0",
    replacement="AGI().scan()",
))
_REGISTRY.register(APIEntry(
    name="compute_metrics_from_task",
    stability=StabilityLevel.DEPRECATED,
    kind="function",
    module="arifos_core",
    description="Legacy metric computation",
    deprecated_in="v42.0",
    removed_in="v43.0",
    replacement="ASI().assess()",
))

# =============================================================================
# MODULE-LEVEL APIs
# =============================================================================

# arifos_core.system
_REGISTRY.register(APIEntry(
    name="Pipeline",
    stability=StabilityLevel.STABLE,
    kind="class",
    module="arifos_core.system.pipeline",
    description="000-999 metabolic pipeline",
))
_REGISTRY.register(APIEntry(
    name="PipelineConfig",
    stability=StabilityLevel.STABLE,
    kind="dataclass",
    module="arifos_core.system.pipeline",
    description="Pipeline configuration",
))
_REGISTRY.register(APIEntry(
    name="run_pipeline",
    stability=StabilityLevel.STABLE,
    kind="function",
    module="arifos_core.system.pipeline",
    description="Run pipeline on input",
))
_REGISTRY.register(APIEntry(
    name="TimeGovernor",
    stability=StabilityLevel.STABLE,
    kind="class",
    module="arifos_core.system.kernel",
    description="Time governor for entropy rot",
))
_REGISTRY.register(APIEntry(
    name="check_entropy_rot",
    stability=StabilityLevel.STABLE,
    kind="function",
    module="arifos_core.system.kernel",
    description="Check for entropy rot",
))
_REGISTRY.register(APIEntry(
    name="route_memory",
    stability=StabilityLevel.STABLE,
    kind="function",
    module="arifos_core.system.kernel",
    description="Route verdict to memory band",
))
_REGISTRY.register(APIEntry(
    name="RuntimeManifest",
    stability=StabilityLevel.STABLE,
    kind="class",
    module="arifos_core.system.runtime_manifest",
    description="Runtime manifest",
))
_REGISTRY.register(APIEntry(
    name="get_manifest",
    stability=StabilityLevel.STABLE,
    kind="function",
    module="arifos_core.system.runtime_manifest",
    description="Get current manifest",
))

# arifos_core.enforcement
_REGISTRY.register(APIEntry(
    name="TRUTH_THRESHOLD",
    stability=StabilityLevel.STABLE,
    kind="constant",
    module="arifos_core.enforcement.metrics",
    description="F2 truth threshold (0.99)",
))
_REGISTRY.register(APIEntry(
    name="GENIUS_FLOOR",
    stability=StabilityLevel.STABLE,
    kind="constant",
    module="arifos_core.enforcement.genius_metrics",
    description="F8 genius floor (0.80)",
))
_REGISTRY.register(APIEntry(
    name="DARK_CEILING",
    stability=StabilityLevel.STABLE,
    kind="constant",
    module="arifos_core.enforcement.genius_metrics",
    description="F9 dark ceiling (0.30)",
))

# arifos_core.governance
_REGISTRY.register(APIEntry(
    name="FAG",
    stability=StabilityLevel.STABLE,
    kind="class",
    module="arifos_core.governance.fag",
    description="File Access Guardian",
))
_REGISTRY.register(APIEntry(
    name="compute_merkle_root",
    stability=StabilityLevel.STABLE,
    kind="function",
    module="arifos_core.governance.merkle",
    description="Compute Merkle root",
))
_REGISTRY.register(APIEntry(
    name="get_merkle_proof",
    stability=StabilityLevel.STABLE,
    kind="function",
    module="arifos_core.governance.merkle",
    description="Get Merkle proof for entry",
))

# arifos_core.memory
_REGISTRY.register(APIEntry(
    name="MemoryWritePolicy",
    stability=StabilityLevel.STABLE,
    kind="class",
    module="arifos_core.memory.policy",
    description="Memory write policy engine",
))
_REGISTRY.register(APIEntry(
    name="MemoryBand",
    stability=StabilityLevel.STABLE,
    kind="enum",
    module="arifos_core.memory.bands",
    description="6 memory bands enum",
))
_REGISTRY.register(APIEntry(
    name="EurekaReceipt",
    stability=StabilityLevel.STABLE,
    kind="class",
    module="arifos_core.memory.eureka_receipt",
    description="EUREKA receipt",
))

# arifos_core.waw
_REGISTRY.register(APIEntry(
    name="WAWFederation",
    stability=StabilityLevel.STABLE,
    kind="class",
    module="arifos_core.waw.federation",
    description="W@W Federation router",
))
_REGISTRY.register(APIEntry(
    name="WellFileCare",
    stability=StabilityLevel.STABLE,
    kind="class",
    module="arifos_core.waw.well_file_care",
    description="@WELL file migration",
))
_REGISTRY.register(APIEntry(
    name="create_well_file_care",
    stability=StabilityLevel.STABLE,
    kind="function",
    module="arifos_core.waw.well_file_care",
    description="Create @WELL instance",
))

# arifos_core.mcp (BETA)
_REGISTRY.register(APIEntry(
    name="MCPServer",
    stability=StabilityLevel.BETA,
    kind="class",
    module="arifos_core.mcp.server",
    description="MCP server class",
))
_REGISTRY.register(APIEntry(
    name="arifos_judge",
    stability=StabilityLevel.BETA,
    kind="function",
    module="arifos_core.mcp.tools.judge",
    description="MCP judge tool",
))
_REGISTRY.register(APIEntry(
    name="arifos_recall",
    stability=StabilityLevel.BETA,
    kind="function",
    module="arifos_core.mcp.tools.recall",
    description="MCP recall tool",
))
_REGISTRY.register(APIEntry(
    name="arifos_audit",
    stability=StabilityLevel.BETA,
    kind="function",
    module="arifos_core.mcp.tools.audit",
    description="MCP audit tool",
))
_REGISTRY.register(APIEntry(
    name="arifos_fag_read",
    stability=StabilityLevel.BETA,
    kind="function",
    module="arifos_core.mcp.tools.fag_read",
    description="MCP FAG read tool",
))


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_stable_exports() -> Set[str]:
    """Get all STABLE API names (for testing)."""
    return {e.name for e in _REGISTRY.get_stable()}


def get_deprecated_exports() -> Dict[str, str]:
    """Get deprecated APIs with their replacements."""
    return {
        e.name: e.replacement or "N/A"
        for e in _REGISTRY.get_deprecated()
    }


def check_module_stability(module_name: str, actual_all: List[str]) -> Dict:
    """
    Check a module's __all__ against the registry.

    Args:
        module_name: Full module path (e.g., "arifos_core")
        actual_all: The module's __all__ list

    Returns:
        Dict with validation results
    """
    return _REGISTRY.validate_exports(module_name, set(actual_all))


__all__ = [
    "StabilityLevel",
    "APIEntry",
    "APIRegistry",
    "get_registry",
    "get_stable_exports",
    "get_deprecated_exports",
    "check_module_stability",
]
