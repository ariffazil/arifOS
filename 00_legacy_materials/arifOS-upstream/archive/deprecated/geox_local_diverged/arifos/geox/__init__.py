"""
GEOX — Geological Intelligence Coprocessor for arifOS
DITEMPA BUKAN DIBERI

A governed, agentic geological intelligence coprocessor built on arifOS.
Four planes: Earth (LEM) · Perception (VLM) · Language/Agent (LLM via arifOS) · Governance

GEOX plugs into the arifOS Constitutional MCP Kernel (AAA architecture:
Architect · Auditor · Agent) and enforces the 13 Constitutional Floors
as they apply to geological reasoning and prospect evaluation.

Pipeline: 000 INIT → 111 THINK → 333 EXPLORE → 555 HEART →
          777 REASON → 888 AUDIT → 999 SEAL

Verdict vocabulary: SEAL | PARTIAL | SABAR | VOID
arifOS verdicts:    CLAIM | PLAUSIBLE | HYPOTHESIS | ESTIMATE | UNKNOWN
"""

from __future__ import annotations

__version__ = "0.1.0"
__author__ = "GEOX Core Team — arifOS Geological Intelligence Division"
__license__ = "Proprietary — All Rights Reserved"
__description__ = "Geological Intelligence Coprocessor for arifOS"
__url__ = "https://github.com/arifos/geox"
__seal__ = "DITEMPA BUKAN DIBERI"

# ---------------------------------------------------------------------------
# Public API surface
# ---------------------------------------------------------------------------

from arifos.geox.geox_agent import (
    GeoXAgent,
    GeoXConfig,
)
from arifos.geox.geox_memory import (
    GeoMemoryEntry,
    GeoMemoryStore,
)
from arifos.geox.geox_reporter import GeoXReporter
from arifos.geox.geox_schemas import (
    CoordinatePoint,
    GeoInsight,
    GeoPrediction,
    GeoQuantity,
    GeoRequest,
    GeoResponse,
    ProvenanceRecord,
    export_json_schemas,
)
from arifos.geox.geox_tools import (
    BaseTool,
    EarthModelTool,
    EOFoundationModelTool,
    GeoRAGTool,
    GeoToolResult,
    SeismicVLMTool,
    SimulatorTool,
    ToolRegistry,
)
from arifos.geox.geox_validator import (
    AggregateVerdict,
    GeoXValidator,
    ValidationResult,
)

__all__ = [
    # Schemas
    "CoordinatePoint",
    "ProvenanceRecord",
    "GeoQuantity",
    "GeoPrediction",
    "GeoInsight",
    "GeoRequest",
    "GeoResponse",
    "export_json_schemas",
    # Tools
    "GeoToolResult",
    "BaseTool",
    "EarthModelTool",
    "EOFoundationModelTool",
    "SeismicVLMTool",
    "SimulatorTool",
    "GeoRAGTool",
    "ToolRegistry",
    # Validator
    "ValidationResult",
    "AggregateVerdict",
    "GeoXValidator",
    # Agent
    "GeoXConfig",
    "GeoXAgent",
    # Memory
    "GeoMemoryEntry",
    "GeoMemoryStore",
    # Reporter
    "GeoXReporter",
]
