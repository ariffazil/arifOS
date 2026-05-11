"""
tool_registry.py — Unified Tool Registry for GEOX
DITEMPA BUKAN DIBERI

Centralized registry for tool metadata, versioning, and constitutional requirements.
Used to harden the MCP server and provide rich discovery.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


@dataclass
class ToolMetadata:
    """Metadata for a GEOX tool."""

    name: str
    version: str
    description: str
    required_floors: list[str] = field(default_factory=lambda: ["F4", "F7", "F11"])
    ac_risk_enabled: bool = False
    error_codes: list[str] = field(
        default_factory=lambda: ["UNKNOWN_ERROR", "PHYSICS_VIOLATION"]
    )
    tags: list[str] = field(default_factory=list)
    status: str = "production"

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "required_floors": self.required_floors,
            "ac_risk_enabled": self.ac_risk_enabled,
            "error_codes": self.error_codes,
            "tags": self.tags,
            "status": self.status,
        }


class ToolStatus(str, Enum):
    """Execution maturity marker for registry filtering."""

    PRODUCTION = "production"
    PREVIEW = "preview"
    SCAFFOLD = "scaffold"


class ErrorCode(str, Enum):
    """Standardized GEOX error codes used by MCP surfaces."""

    VALIDATION_ERROR = "GEOX_400_VALIDATION"
    OUT_OF_RANGE = "GEOX_400_OUT_OF_RANGE"
    DATA_UNAVAILABLE = "GEOX_404_DATA_UNAVAILABLE"
    FILE_NOT_FOUND = "GEOX_404_FILE_NOT_FOUND"
    AC_RISK_VOID = "GEOX_409_AC_RISK_VOID"
    GOVERNANCE_HOLD = "GEOX_423_GOVERNANCE_HOLD"
    CALCULATION_ERROR = "GEOX_500_CALCULATION"
    INTERNAL_ERROR = "GEOX_500_INTERNAL"


def create_standardized_error(
    code: ErrorCode,
    detail: str,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a stable error envelope consumed by MCP server surfaces."""

    return {
        "status": "ERROR",
        "error": True,
        "code": code.value,
        "message": detail,
        "context": context or {},
    }


class UnifiedToolRegistry:
    """Registry of all hardened GEOX tools."""

    _registry: dict[str, ToolMetadata] = {
        "geox_load_seismic_line": ToolMetadata(
            name="geox_load_seismic_line",
            version="1.0.0",
            description="Load seismic data and generate contrast canon views.",
            required_floors=["F4", "F11"],
            ac_risk_enabled=True,
            error_codes=["FILE_NOT_FOUND", "INVALID_FORMAT", "SCALE_UNKNOWN"],
            tags=["seismic", "vision"],
        ),
        "geox_build_structural_candidates": ToolMetadata(
            name="geox_build_structural_candidates",
            version="1.0.0",
            description="Generate multi-model structural interpretations.",
            required_floors=["F7", "F11"],
            ac_risk_enabled=True,
            error_codes=["INTERPRETATION_FAILED", "INSUFFICIENT_DATA"],
            tags=["seismic", "structural"],
        ),
        "geox_compute_ac_risk": ToolMetadata(
            name="geox_compute_ac_risk",
            version="1.1.0",
            description="Calculate Anomalous Contrast Risk (ToAC).",
            required_floors=["F4", "F7", "F11", "F13"],
            ac_risk_enabled=False,
            error_codes=["INVALID_COMPONENTS", "MISSING_TRANSFORM"],
            tags=["governance", "risk"],
        ),
        "geox_feasibility_check": ToolMetadata(
            name="geox_feasibility_check",
            version="1.0.0",
            description="Verify physical feasibility of a geological plan.",
            required_floors=["F1", "F2", "F4", "F7", "F9", "F11", "F13"],
            ac_risk_enabled=True,
            error_codes=["PHYSICS_VIOLATION", "CONSTRAINT_MISMATCH"],
            tags=["governance", "physics"],
        ),
        "geox_verify_geospatial": ToolMetadata(
            name="geox_verify_geospatial",
            version="1.0.0",
            description="Verify coordinates and jurisdictional boundaries.",
            required_floors=["F4", "F11"],
            ac_risk_enabled=False,
            error_codes=["OUT_OF_BOUNDS", "PROJECTION_ERROR"],
            tags=["gis", "spatial"],
        ),
        "geox_evaluate_prospect": ToolMetadata(
            name="geox_evaluate_prospect",
            version="1.0.0",
            description="Generate governed verdict on a prospect.",
            required_floors=["F1", "F4", "F7", "F9", "F11", "F13"],
            ac_risk_enabled=True,
            error_codes=["INSUFFICIENT_GROUNDING", "VERDICT_VOID"],
            tags=["governance", "prospect"],
        ),
        "geox_query_memory": ToolMetadata(
            name="geox_query_memory",
            version="1.0.0",
            description="Retrieve past evaluations from GEOX memory.",
            required_floors=["F11"],
            ac_risk_enabled=False,
            error_codes=["QUERY_FAILED", "STORE_UNAVAILABLE"],
            tags=["memory", "retrieval"],
        ),
        "geox_query_macrostrat": ToolMetadata(
            name="geox_query_macrostrat",
            version="1.0.0",
            description="Retrieve regional stratigraphy from Macrostrat.",
            required_floors=["F2", "F7", "F11"],
            ac_risk_enabled=False,
            error_codes=["MACROSTRAT_API_ERROR", "NO_COVERAGE"],
            tags=["stratigraphy", "external"],
        ),
        "geox_calculate_saturation": ToolMetadata(
            name="geox_calculate_saturation",
            version="1.0.0",
            description="Compute Sw with uncertainty propagation.",
            required_floors=["F2", "F4", "F7", "F13"],
            ac_risk_enabled=True,
            error_codes=["SW_MODEL_ERROR", "PARAMETER_OUT_OF_RANGE"],
            tags=["petrophysics"],
        ),
    }

    @classmethod
    def get(cls, name: str) -> ToolMetadata | None:
        return cls._registry.get(name)

    @classmethod
    def list_tools(cls) -> list[ToolMetadata]:
        return list(cls._registry.values())


class ToolRegistry:
    """Compatibility facade expected by legacy AAA/hardened MCP servers."""

    @classmethod
    def get(cls, name: str) -> ToolMetadata | None:
        return UnifiedToolRegistry.get(name)

    @classmethod
    def list_tools_dict(
        cls,
        status_filter: ToolStatus | None = None,
        include_scaffold: bool = False,
    ) -> list[dict[str, Any]]:
        tools = UnifiedToolRegistry.list_tools()

        if status_filter is not None:
            tools = [t for t in tools if t.status == status_filter.value]

        if not include_scaffold:
            tools = [t for t in tools if t.status != ToolStatus.SCAFFOLD.value]

        return [tool.to_dict() for tool in tools]

    @classmethod
    def get_capabilities(cls) -> dict[str, Any]:
        tools = UnifiedToolRegistry.list_tools()

        counts = {
            "total": len(tools),
            "production": sum(
                1 for t in tools if t.status == ToolStatus.PRODUCTION.value
            ),
            "preview": sum(1 for t in tools if t.status == ToolStatus.PREVIEW.value),
            "scaffold": sum(1 for t in tools if t.status == ToolStatus.SCAFFOLD.value),
        }

        floors: set[str] = set()
        ac_risk_enabled = False
        for tool in tools:
            floors.update(tool.required_floors)
            ac_risk_enabled = ac_risk_enabled or tool.ac_risk_enabled

        return {
            "server": {
                "name": "GEOX Tool Registry",
                "version": "1.0.0",
                "seal": "DITEMPA BUKAN DIBERI",
            },
            "tool_count": counts,
            "governance": {
                "floors_active": sorted(floors),
                "ac_risk_enabled": ac_risk_enabled,
            },
        }


# Backward-compatible symbol used by existing servers.
GEOX_TOOLS = UnifiedToolRegistry._registry
