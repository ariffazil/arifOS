"""
arifosmcp — The Sovereign Constitutional Intelligence Kernel
═════════════════════════════════════════════════════════════

13 canonical MCP capability tools | 13 Floors (F1–L13) | Trinity ΔΩΨ
DITEMPA BUKAN DIBERI — Intelligence is forged, not given.
"""

# __version__ is DERIVED from installed package metadata — pyproject.toml is the
# single source of truth. A hardcoded string here drifted twice (served
# "2026.07.17", then "2026.06.11-FIQHGEOM", while the wheel said 1!2026.9.6),
# tripping runtime_verify source↔import DRIFT and false HOLDs. F13 order
# 2026-09-30 ("clear DEPLOYMENT_DRIFT"): kill the drift class at the root.
from importlib.metadata import version as _pkg_version, PackageNotFoundError as _PkgNotFound

try:
    __version__ = _pkg_version("arifos")
except _PkgNotFound:  # source tree without installed distribution
    __version__ = "0.0.0.dev0"
__author__ = "Muhammad Arif bin Fazil"
__license__ = "AGPL-3.0-only"

# ── NAMESPACE COLLISION GUARD ──────────────────────────────────────────────
# External consumers (GEOX, WEALTH, WELL) may have their own `core/` package
# that shadows arifOS's core/shared/. Ensure arifOS root is at sys.path[0]
# so `from core.shared.*` resolves to arifOS's core, not the consumer's.
import os as _ns_os
import sys as _ns_sys

_arifos_root = _ns_os.path.dirname(_ns_os.path.dirname(_ns_os.path.abspath(__file__)))
if _arifos_root not in _ns_sys.path or _ns_sys.path.index(_arifos_root) > 0:
    if _arifos_root in _ns_sys.path:
        _ns_sys.path.remove(_arifos_root)
    _ns_sys.path.insert(0, _arifos_root)
# ── END NAMESPACE COLLISION GUARD ──────────────────────────────────────────

try:
    import asyncio

    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

# Embodied Tool Intelligence — runtime tool self-grounding
from arifosmcp.core.embodied_tool_engine import (
    EmbodiedDecision,
    EmbodiedToolEngine,
    embodied_tool,
    get_embodied_tool_engine,
)
from arifosmcp.core.reversibility_engine import (
    ReversibilityClass,
    ReversibilityEngine,
    ReversibilityVerdict,
    classify_tool_base,
)
from arifosmcp.core.tool_self_model import (
    BlastRadius,
    ToolManifest,
    ToolSelfModel,
    ToolSelfModelEntry,
    get_tool_self_model,
    register_tool_in_self_model,
)
from arifosmcp.core.witness_log import (
    WitnessLog,
    WitnessRecord,
    get_witness_log,
    log_witness,
)
from arifosmcp.schemas.embodied_tool import (
    Domain,
    EmbodiedToolEnvelope,
    ExecutionStatus,
    Permission,
    PermissionGap,
    Reversibility,
    RiskTier,
    StateDelta,
    UncertaintyItem,
    WitnessEntry,
    build_embodied_envelope,
)
from arifosmcp.tools.embodied import (
    ARIFOS_TOOL_CHARTERS,
    EmbodiedTool,
    register_all_arifos_tools,
    register_embodied_tool,
)

__all__ = [
    "ARIFOS_TOOL_CHARTERS",
    "BlastRadius",
    "Domain",
    "EmbodiedDecision",
    "EmbodiedTool",
    "EmbodiedToolEngine",
    "EmbodiedToolEnvelope",
    "ExecutionStatus",
    "Permission",
    "PermissionGap",
    "Reversibility",
    "ReversibilityClass",
    "ReversibilityEngine",
    "ReversibilityVerdict",
    "RiskTier",
    "StateDelta",
    "ToolManifest",
    "ToolSelfModel",
    "ToolSelfModelEntry",
    "UncertaintyItem",
    "WitnessEntry",
    "WitnessLog",
    "WitnessRecord",
    "build_embodied_envelope",
    "classify_tool_base",
    "embodied_tool",
    "get_embodied_tool_engine",
    "get_tool_self_model",
    "get_witness_log",
    "log_witness",
    "register_all_arifos_tools",
    "register_embodied_tool",
    "register_tool_in_self_model",
]
