"""
arifosmcp — The Sovereign Constitutional Intelligence Kernel
═════════════════════════════════════════════════════════════

13 canonical MCP capability tools | 13 Floors (F1–F13) | Trinity ΔΩΨ
DITEMPA BUKAN DIBERI — Intelligence is forged, not given.
"""

__version__ = "2026.05.05-SSCT"
__author__ = "Muhammad Arif bin Fazil"
__license__ = "AGPL-3.0-only"

try:
    import asyncio

    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

# Embodied Tool Intelligence — runtime tool self-awareness
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
