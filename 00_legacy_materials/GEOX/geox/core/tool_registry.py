"""
GEOX Unified Tool Registry — Single Source of Truth
DITEMPA BUKAN DIBERI

Registry for all GEOX MCP tools with:
- Tool metadata (name, version, status)
- Input/output schemas (JSON Schema compatible)
- Error codes and handling
- arifOS constitutional requirements
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable
import json


class ToolStatus(Enum):
    """Production readiness status."""

    PROD = "production"  # Fully tested, stable
    PREVIEW = "preview"  # Working but may change
    SCAFFOLD = "scaffold"  # Architecture only, not implemented


class ErrorCode(Enum):
    """Standardized GEOX error codes."""

    # Validation errors (400 range)
    VALIDATION_ERROR = "GEOX_400_VALIDATION"
    INVALID_FORMAT = "GEOX_400_FORMAT"
    MISSING_REQUIRED = "GEOX_400_MISSING"
    OUT_OF_RANGE = "GEOX_400_RANGE"

    # Data errors (404 range)
    FILE_NOT_FOUND = "GEOX_404_FILE"
    DATA_UNAVAILABLE = "GEOX_404_DATA"
    SCALE_UNKNOWN = "GEOX_404_SCALE"

    # Physics errors (422 range)
    PHYSICS_VIOLATION = "GEOX_422_PHYSICS"
    IMPOSSIBLE_GEOMETRY = "GEOX_422_GEOMETRY"
    RATLAS_MISMATCH = "GEOX_422_RATLAS"

    # Governance errors (403 range)
    GOVERNANCE_HOLD = "GEOX_403_HOLD"
    AC_RISK_VOID = "GEOX_403_VOID"
    FLOOR_VIOLATION = "GEOX_403_FLOOR"

    # System errors (500 range)
    INTERNAL_ERROR = "GEOX_500_INTERNAL"
    VISION_UNAVAILABLE = "GEOX_500_VISION"
    CALCULATION_ERROR = "GEOX_500_CALC"


@dataclass
class ErrorSpec:
    """Error specification for documentation and handling."""

    code: ErrorCode
    message: str
    description: str
    recoverable: bool
    suggested_action: str


@dataclass
class ToolSchema:
    """JSON Schema compatible tool schema."""

    type: str = "object"
    properties: dict[str, Any] = field(default_factory=dict)
    required: list[str] = field(default_factory=list)
    additional_properties: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "properties": self.properties,
            "required": self.required,
            "additionalProperties": self.additional_properties,
        }


@dataclass
class ToolMetadata:
    """Complete metadata for a GEOX tool."""

    # Identity
    name: str
    version: str
    status: ToolStatus

    # Documentation
    description: str
    long_description: str = ""
    examples: list[dict[str, Any]] = field(default_factory=list)

    # Schemas
    input_schema: ToolSchema = field(default_factory=ToolSchema)
    output_schema: ToolSchema = field(default_factory=ToolSchema)

    # Error handling
    error_codes: list[ErrorCode] = field(default_factory=list)

    # arifOS governance
    required_floors: list[str] = field(default_factory=list)
    ac_risk_enabled: bool = False
    risk_factors: list[str] = field(default_factory=list)

    # Runtime
    timeout_ms: int = 30000
    retryable: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "version": self.version,
            "status": self.status.value,
            "description": self.description,
            "long_description": self.long_description,
            "examples": self.examples,
            "input_schema": self.input_schema.to_dict(),
            "output_schema": self.output_schema.to_dict(),
            "error_codes": [e.value for e in self.error_codes],
            "required_floors": self.required_floors,
            "ac_risk_enabled": self.ac_risk_enabled,
            "risk_factors": self.risk_factors,
            "timeout_ms": self.timeout_ms,
            "retryable": self.retryable,
        }


# ============================================================================
# ERROR SPECIFICATIONS
# ============================================================================

ERROR_REGISTRY: dict[ErrorCode, ErrorSpec] = {
    # Validation errors
    ErrorCode.VALIDATION_ERROR: ErrorSpec(
        code=ErrorCode.VALIDATION_ERROR,
        message="Input validation failed",
        description="The provided input failed validation checks.",
        recoverable=True,
        suggested_action="Check input parameters against schema and retry.",
    ),
    ErrorCode.INVALID_FORMAT: ErrorSpec(
        code=ErrorCode.INVALID_FORMAT,
        message="Invalid file format",
        description="The provided file is not in an acceptable format.",
        recoverable=True,
        suggested_action="Convert file to supported format (SEGY, PNG, JPEG, TIFF).",
    ),
    ErrorCode.MISSING_REQUIRED: ErrorSpec(
        code=ErrorCode.MISSING_REQUIRED,
        message="Missing required parameter",
        description="A required input parameter was not provided.",
        recoverable=True,
        suggested_action="Provide all required parameters listed in the schema.",
    ),
    ErrorCode.OUT_OF_RANGE: ErrorSpec(
        code=ErrorCode.OUT_OF_RANGE,
        message="Parameter out of valid range",
        description="A numeric parameter is outside acceptable bounds.",
        recoverable=True,
        suggested_action="Adjust parameter to within documented range.",
    ),
    # Data errors
    ErrorCode.FILE_NOT_FOUND: ErrorSpec(
        code=ErrorCode.FILE_NOT_FOUND,
        message="File not found",
        description="The specified file path does not exist or is inaccessible.",
        recoverable=True,
        suggested_action="Verify file path and permissions.",
    ),
    ErrorCode.DATA_UNAVAILABLE: ErrorSpec(
        code=ErrorCode.DATA_UNAVAILABLE,
        message="Required data unavailable",
        description="External data source required for operation is unavailable.",
        recoverable=True,
        suggested_action="Check data source connectivity or try alternative data.",
    ),
    ErrorCode.SCALE_UNKNOWN: ErrorSpec(
        code=ErrorCode.SCALE_UNKNOWN,
        description="Cannot determine physical scale from input.",
        message="Scale information missing or ambiguous",
        recoverable=False,
        suggested_action="Provide scale bar, grid coordinates, or explicit scale factor.",
    ),
    # Physics errors
    ErrorCode.PHYSICS_VIOLATION: ErrorSpec(
        code=ErrorCode.PHYSICS_VIOLATION,
        message="Physical impossibility detected",
        description="The interpretation violates known physical constraints.",
        recoverable=False,
        suggested_action="Review interpretation against RATLAS or acquire better data.",
    ),
    ErrorCode.IMPOSSIBLE_GEOMETRY: ErrorSpec(
        code=ErrorCode.IMPOSSIBLE_GEOMETRY,
        message="Geometrically impossible structure",
        description="Structural geometry violates physical possibility.",
        recoverable=False,
        suggested_action="Validate against geological principles (F7).",
    ),
    ErrorCode.RATLAS_MISMATCH: ErrorSpec(
        code=ErrorCode.RATLAS_MISMATCH,
        message="Material properties inconsistent with RATLAS",
        description="Interpreted rock properties don't match known analogs.",
        recoverable=False,
        suggested_action="Check velocity/density values or update RATLAS query.",
    ),
    # Governance errors
    ErrorCode.GOVERNANCE_HOLD: ErrorSpec(
        code=ErrorCode.GOVERNANCE_HOLD,
        message="Operation blocked by governance HOLD",
        description="AC_Risk exceeds threshold requiring human review (888_HOLD).",
        recoverable=False,
        suggested_action="Escalate to qualified interpreter; review risk factors.",
    ),
    ErrorCode.AC_RISK_VOID: ErrorSpec(
        code=ErrorCode.AC_RISK_VOID,
        message="Operation VOID — critical risk",
        description="AC_Risk ≥ 0.75. Interpretation unsafe.",
        recoverable=False,
        suggested_action="Acquire better data or ground-truth validation.",
    ),
    ErrorCode.FLOOR_VIOLATION: ErrorSpec(
        code=ErrorCode.FLOOR_VIOLATION,
        message="Constitutional floor violated",
        description="Operation violates required arifOS floor (F1-F13).",
        recoverable=False,
        suggested_action="Review constitutional requirements for this operation.",
    ),
    # System errors
    ErrorCode.INTERNAL_ERROR: ErrorSpec(
        code=ErrorCode.INTERNAL_ERROR,
        message="Internal server error",
        description="Unexpected error occurred during processing.",
        recoverable=True,
        suggested_action="Retry after brief delay; contact support if persistent.",
    ),
    ErrorCode.VISION_UNAVAILABLE: ErrorSpec(
        code=ErrorCode.VISION_UNAVAILABLE,
        message="Vision model unavailable",
        description="VLM backend not responding or misconfigured.",
        recoverable=True,
        suggested_action="Check VLM service status or use non-vision fallback.",
    ),
    ErrorCode.CALCULATION_ERROR: ErrorSpec(
        code=ErrorCode.CALCULATION_ERROR,
        message="Calculation failed",
        description="Numerical error during computation.",
        recoverable=True,
        suggested_action="Check input data quality or use alternative method.",
    ),
}


# ============================================================================
# TOOL REGISTRY
# ============================================================================

GEOX_TOOLS: dict[str, ToolMetadata] = {
    # ========================================================================
    # PRODUCTION TOOLS
    # ========================================================================
    "geox_compute_ac_risk": ToolMetadata(
        name="geox_compute_ac_risk",
        version="1.0.0",
        status=ToolStatus.PROD,
        description="Calculate Theory of Anomalous Contrast (ToAC) risk score.",
        long_description="""
        Computes AC_Risk = U_phys × D_transform × B_cog for any vision operation.
        Returns verdict (SEAL/QUALIFY/HOLD/VOID) and detailed explanation.
        All vision operations should route through this for governance.
        """,
        examples=[
            {
                "description": "SEGY seismic with minimal transforms",
                "input": {
                    "u_phys": 0.3,
                    "transform_stack": ["linear_scaling"],
                    "bias_scenario": "ai_with_physics",
                },
                "output": {
                    "ac_risk": 0.06,
                    "verdict": "SEAL",
                    "explanation": "AC_Risk=0.06: Low risk. Physical grounding strong...",
                },
            },
            {
                "description": "Image-only with aggressive transforms",
                "input": {
                    "u_phys": 0.8,
                    "transform_stack": ["clahe", "agc_rms", "vlm_inference"],
                    "bias_scenario": "ai_vision_only",
                },
                "output": {
                    "ac_risk": 0.336,
                    "verdict": "QUALIFY",
                    "explanation": "AC_Risk=0.34: Moderate risk. Proceed with caveats...",
                },
            },
        ],
        input_schema=ToolSchema(
            properties={
                "u_phys": {
                    "type": "number",
                    "description": "Physical ambiguity [0.0, 1.0]",
                    "minimum": 0.0,
                    "maximum": 1.0,
                },
                "transform_stack": {
                    "type": "array",
                    "description": "List of applied transforms",
                    "items": {"type": "string"},
                    "examples": [["linear_scaling"], ["clahe", "vlm_inference"]],
                },
                "bias_scenario": {
                    "type": "string",
                    "description": "Cognitive bias scenario",
                    "enum": [
                        "unaided_expert",
                        "multi_interpreter",
                        "physics_validated",
                        "ai_vision_only",
                        "ai_with_physics",
                    ],
                    "default": "ai_vision_only",
                },
                "custom_b_cog": {
                    "type": "number",
                    "description": "Override B_cog value [0.0, 1.0]",
                    "minimum": 0.0,
                    "maximum": 1.0,
                },
            },
            required=["u_phys", "transform_stack"],
        ),
        output_schema=ToolSchema(
            properties={
                "ac_risk": {"type": "number", "description": "Calculated AC_Risk score"},
                "verdict": {"type": "string", "enum": ["SEAL", "QUALIFY", "HOLD", "VOID"]},
                "explanation": {"type": "string"},
                "components": {
                    "type": "object",
                    "properties": {
                        "physical_ambiguity": {"type": "number"},
                        "display_distortion": {"type": "number"},
                        "cognitive_bias": {"type": "number"},
                    },
                },
            },
            required=["ac_risk", "verdict", "explanation"],
        ),
        error_codes=[
            ErrorCode.VALIDATION_ERROR,
            ErrorCode.OUT_OF_RANGE,
            ErrorCode.CALCULATION_ERROR,
        ],
        required_floors=["F2", "F4", "F7"],
        ac_risk_enabled=True,
        risk_factors=["transform_stack", "bias_scenario"],
        timeout_ms=5000,
        retryable=False,
    ),
    "geox_load_seismic_line": ToolMetadata(
        name="geox_load_seismic_line",
        version="1.0.0",
        status=ToolStatus.PROD,
        description="Load seismic line from SEG-Y or image with scale detection.",
        long_description="""
        Loads seismic data and performs F4 Clarity checks:
        - Detect or verify spatial scale (m/km per pixel)
        - Detect or verify temporal scale (ms/s per sample)
        - Document polarity (SEG normal/reverse)

        Returns scale metadata and contrast views for further processing.
        """,
        examples=[
            {
                "description": "Load SEG-Y with known scale",
                "input": {
                    "file_path": "/data/line_101.sgy",
                    "scale_hint": {"cdp_interval_m": 12.5, "sample_interval_ms": 4},
                },
            }
        ],
        input_schema=ToolSchema(
            properties={
                "file_path": {
                    "type": "string",
                    "description": "Path to seismic file (SEGY, PNG, JPG, TIFF)",
                },
                "line_name": {
                    "type": "string",
                    "description": "Optional display name for the line",
                },
                "scale_hint": {
                    "type": "object",
                    "description": "Optional scale information",
                    "properties": {
                        "cdp_interval_m": {"type": "number"},
                        "sample_interval_ms": {"type": "number"},
                        "polarity": {"type": "string", "enum": ["SEG_normal", "SEG_reverse"]},
                    },
                },
            },
            required=["file_path"],
        ),
        output_schema=ToolSchema(
            properties={
                "line_id": {"type": "string"},
                "status": {"type": "string"},
                "scale": {
                    "type": "object",
                    "properties": {
                        "cdp_interval_m": {"type": "number"},
                        "sample_interval_ms": {"type": "number"},
                        "confidence": {"type": "number"},
                    },
                },
                "contrast_views": {"type": "array", "items": {"type": "object"}},
                "warnings": {"type": "array", "items": {"type": "string"}},
            },
            required=["line_id", "status"],
        ),
        error_codes=[
            ErrorCode.FILE_NOT_FOUND,
            ErrorCode.INVALID_FORMAT,
            ErrorCode.SCALE_UNKNOWN,
            ErrorCode.INTERNAL_ERROR,
        ],
        required_floors=["F4"],
        ac_risk_enabled=False,
        timeout_ms=30000,
        retryable=True,
    ),
    "geox_build_structural_candidates": ToolMetadata(
        name="geox_build_structural_candidates",
        version="1.0.0",
        status=ToolStatus.PROD,
        description="Generate multiple structural hypotheses with confidence bands.",
        long_description="""
        Creates 3+ alternative structural models for a seismic line,
        acknowledging non-uniqueness (F2 Truth). Each candidate includes:
        - Fault geometry (if present)
        - Horizon interpretation
        - Confidence score
        - Geological setting tag

        Returns candidates sorted by confidence, never a single 'truth'.
        """,
        input_schema=ToolSchema(
            properties={
                "line_id": {"type": "string", "description": "Line ID from geox_load_seismic_line"},
                "structural_style": {
                    "type": "string",
                    "enum": [
                        "extensional",
                        "compressional",
                        "strike_slip",
                        "passive_margin",
                        "unknown",
                    ],
                    "default": "unknown",
                },
                "max_candidates": {"type": "integer", "default": 3, "maximum": 5},
            },
            required=["line_id"],
        ),
        output_schema=ToolSchema(
            properties={
                "candidates": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "candidate_id": {"type": "string"},
                            "confidence": {"type": "number"},
                            "geological_setting": {"type": "string"},
                            "faults": {"type": "array"},
                            "horizons": {"type": "array"},
                            "key_assumptions": {"type": "array", "items": {"type": "string"}},
                        },
                    },
                },
                "non_uniqueness_note": {"type": "string"},
            },
            required=["candidates"],
        ),
        error_codes=[
            ErrorCode.DATA_UNAVAILABLE,
            ErrorCode.CALCULATION_ERROR,
            ErrorCode.INTERNAL_ERROR,
        ],
        required_floors=["F2", "F7"],
        ac_risk_enabled=False,
        timeout_ms=60000,
        retryable=True,
    ),
    # ========================================================================
    # PREVIEW TOOLS
    # ========================================================================
    "geox_interpret_single_line": ToolMetadata(
        name="geox_interpret_single_line",
        version="0.9.0",
        status=ToolStatus.PREVIEW,
        description="Full governed visual interpreter (orchestrator).",
        long_description="""
        End-to-end single line interpretation with ToAC governance.
        Pipeline: ingest → contrast views → VLM → consistency check → AC_Risk → verdict.

        NOTE: VLM backend is currently mock. Use for workflow testing only.
        """,
        input_schema=ToolSchema(
            properties={
                "seismic_data": {
                    "type": "string",
                    "description": "Path to seismic data or base64 image",
                },
                "data_type": {"type": "string", "enum": ["raster", "segy"], "default": "raster"},
                "goal": {"type": "string", "description": "Interpretation goal/context"},
            },
            required=["seismic_data"],
        ),
        output_schema=ToolSchema(
            properties={
                "verdict": {"type": "string"},
                "result": {"type": "object"},
                "artifacts": {"type": "object"},
                "visual_markdown": {"type": "string"},
                "telemetry": {"type": "object"},
            },
            required=["verdict"],
        ),
        error_codes=[
            ErrorCode.FILE_NOT_FOUND,
            ErrorCode.INVALID_FORMAT,
            ErrorCode.VISION_UNAVAILABLE,
            ErrorCode.AC_RISK_VOID,
            ErrorCode.GOVERNANCE_HOLD,
        ],
        required_floors=["F1", "F2", "F4", "F7", "F9", "F13"],
        ac_risk_enabled=True,
        risk_factors=["vlm_inference", "display_transforms"],
        timeout_ms=120000,
        retryable=False,
    ),
    "geox_georeference_map": ToolMetadata(
        name="geox_georeference_map",
        version="0.8.0",
        status=ToolStatus.PREVIEW,
        description="Georeference scanned map with AC_Risk assessment.",
        long_description="""
        Converts scanned geological maps to georeferenced format.
        Performs OCR on grid labels, validates scale consistency,
        and calculates AC_Risk for the georeferencing operation.
        """,
        input_schema=ToolSchema(
            properties={
                "image_path": {"type": "string"},
                "map_type": {
                    "type": "string",
                    "enum": ["geological", "topographic", "seismic_line_map", "cross_section"],
                },
                "bounds_hint": {
                    "type": "object",
                    "properties": {
                        "west": {"type": "number"},
                        "east": {"type": "number"},
                        "south": {"type": "number"},
                        "north": {"type": "number"},
                    },
                },
            },
            required=["image_path", "map_type"],
        ),
        output_schema=ToolSchema(
            properties={
                "georeferenced_path": {"type": "string"},
                "bounds": {"type": "object"},
                "crs": {"type": "string"},
                "ac_risk_result": {"type": "object"},
                "quality_score": {"type": "number"},
            },
            required=["georeferenced_path", "ac_risk_result"],
        ),
        error_codes=[
            ErrorCode.FILE_NOT_FOUND,
            ErrorCode.INVALID_FORMAT,
            ErrorCode.SCALE_UNKNOWN,
            ErrorCode.AC_RISK_VOID,
        ],
        required_floors=["F2", "F4"],
        ac_risk_enabled=True,
        risk_factors=["ocr_extraction", "perspective_warp"],
        timeout_ms=60000,
        retryable=True,
    ),
    "geox_earth_signals": ToolMetadata(
        name="geox_earth_signals",
        version="0.9.0",
        status=ToolStatus.PREVIEW,
        description="Live Earth observation signals for prospect location.",
        long_description="""
        Real-time data from USGS (earthquakes), Open-Meteo (climate),
        and NOAA (geomagnetic) for temporal grounding at SENSE stage.
        """,
        input_schema=ToolSchema(
            properties={
                "latitude": {"type": "number", "minimum": -90, "maximum": 90},
                "longitude": {"type": "number", "minimum": -180, "maximum": 180},
                "radius_km": {"type": "number", "default": 300},
                "eq_limit": {"type": "integer", "default": 10, "maximum": 50},
            },
            required=["latitude", "longitude"],
        ),
        output_schema=ToolSchema(
            properties={
                "status": {"type": "string"},
                "location": {"type": "object"},
                "earthquakes": {"type": "object"},
                "climate": {"type": "object"},
                "geomagnetic": {"type": "object"},
                "warnings": {"type": "array"},
            },
            required=["status"],
        ),
        error_codes=[
            ErrorCode.DATA_UNAVAILABLE,
            ErrorCode.OUT_OF_RANGE,
            ErrorCode.INTERNAL_ERROR,
        ],
        required_floors=["F2"],
        ac_risk_enabled=False,
        timeout_ms=15000,
        retryable=True,
    ),
    # ========================================================================
    # SCAFFOLD TOOLS
    # ========================================================================
    "geox_digitize_well_log": ToolMetadata(
        name="geox_digitize_well_log",
        version="0.1.0",
        status=ToolStatus.SCAFFOLD,
        description="Digitize scanned well log curves with AC_Risk assessment.",
        long_description="Architecture defined. Implementation pending.",
        input_schema=ToolSchema(
            properties={
                "image_path": {"type": "string"},
                "curve_types": {"type": "array", "items": {"type": "string"}},
            },
            required=["image_path"],
        ),
        output_schema=ToolSchema(
            properties={"curves": {"type": "array"}, "ac_risk_result": {"type": "object"}},
            required=["curves", "ac_risk_result"],
        ),
        error_codes=[
            ErrorCode.FILE_NOT_FOUND,
            ErrorCode.INVALID_FORMAT,
            ErrorCode.AC_RISK_VOID,
        ],
        required_floors=["F2", "F4"],
        ac_risk_enabled=True,
        timeout_ms=60000,
        retryable=False,
    ),
}


# ============================================================================
# REGISTRY API
# ============================================================================


class ToolRegistry:
    """Unified tool registry for GEOX MCP server."""

    _tools: dict[str, ToolMetadata] = GEOX_TOOLS
    _handlers: dict[str, Callable] = {}

    @classmethod
    def get(cls, name: str) -> ToolMetadata | None:
        """Get tool metadata by name."""
        return cls._tools.get(name)

    @classmethod
    def list_tools(
        cls, status_filter: ToolStatus | None = None, include_scaffold: bool = True
    ) -> list[ToolMetadata]:
        """
        List all tools with optional filtering.

        Args:
            status_filter: Only return tools with this status
            include_scaffold: Include scaffold tools in results
        """
        tools = cls._tools.values()

        if status_filter:
            tools = [t for t in tools if t.status == status_filter]
        elif not include_scaffold:
            tools = [t for t in tools if t.status != ToolStatus.SCAFFOLD]

        return list(tools)

    @classmethod
    def list_tools_dict(
        cls, status_filter: ToolStatus | None = None, include_scaffold: bool = True
    ) -> list[dict[str, Any]]:
        """List tools as dictionaries."""
        return [t.to_dict() for t in cls.list_tools(status_filter, include_scaffold)]

    @classmethod
    def register_handler(cls, tool_name: str, handler: Callable) -> None:
        """Register a handler function for a tool."""
        cls._handlers[tool_name] = handler

    @classmethod
    def get_handler(cls, tool_name: str) -> Callable | None:
        """Get handler for a tool."""
        return cls._handlers.get(tool_name)

    @classmethod
    def get_error_spec(cls, code: ErrorCode) -> ErrorSpec:
        """Get error specification."""
        return ERROR_REGISTRY[code]

    @classmethod
    def get_capabilities(cls) -> dict[str, Any]:
        """Get server capabilities summary."""
        all_tools = cls.list_tools()
        prod_tools = [t for t in all_tools if t.status == ToolStatus.PROD]
        preview_tools = [t for t in all_tools if t.status == ToolStatus.PREVIEW]
        scaffold_tools = [t for t in all_tools if t.status == ToolStatus.SCAFFOLD]

        return {
            "server": {
                "name": "GEOX Earth Witness",
                "version": "1.0.0",
                "seal": "DITEMPA BUKAN DIBERI",
            },
            "tool_count": {
                "total": len(all_tools),
                "production": len(prod_tools),
                "preview": len(preview_tools),
                "scaffold": len(scaffold_tools),
            },
            "governance": {
                "floors_active": ["F1", "F2", "F4", "F7", "F9", "F13"],
                "ac_risk_enabled": True,
                "theory": "ToAC (Theory of Anomalous Contrast)",
            },
            "tools": [t.name for t in all_tools],
        }


def create_standardized_error(
    code: ErrorCode, detail: str = "", context: dict[str, Any] | None = None
) -> dict[str, Any]:
    """
    Create a standardized error response.

    Args:
        code: Error code from registry
        detail: Additional error detail
        context: Additional context for debugging
    """
    spec = ERROR_REGISTRY[code]

    return {
        "error": True,
        "code": code.value,
        "message": spec.message,
        "description": spec.description,
        "detail": detail,
        "recoverable": spec.recoverable,
        "suggested_action": spec.suggested_action,
        "context": context or {},
        "seal": "DITEMPA BUKAN DIBERI",
    }


# ============================================================================
# SELF-TEST
# ============================================================================

if __name__ == "__main__":
    print("GEOX Unified Tool Registry")
    print("=" * 50)

    # List all tools
    print("\nRegistered Tools:")
    for tool in ToolRegistry.list_tools():
        status_icon = {
            ToolStatus.PROD: "✅",
            ToolStatus.PREVIEW: "🟡",
            ToolStatus.SCAFFOLD: "🔴",
        }.get(tool.status, "❓")
        print(f"  {status_icon} {tool.name} ({tool.version}) - {tool.status.value}")

    # Show capabilities
    print("\nServer Capabilities:")
    caps = ToolRegistry.get_capabilities()
    print(f"  Total tools: {caps['tool_count']['total']}")
    print(f"  Production: {caps['tool_count']['production']}")
    print(f"  Preview: {caps['tool_count']['preview']}")
    print(f"  Scaffold: {caps['tool_count']['scaffold']}")

    # Show example tool detail
    print("\nExample: geox_compute_ac_risk")
    tool = ToolRegistry.get("geox_compute_ac_risk")
    if tool:
        print(f"  Version: {tool.version}")
        print(f"  Status: {tool.status.value}")
        print(f"  AC_Risk enabled: {tool.ac_risk_enabled}")
        print(f"  Required floors: {', '.join(tool.required_floors)}")
        print(f"  Error codes: {[e.value for e in tool.error_codes]}")

    # Show error example
    print("\nExample Error Response:")
    error = create_standardized_error(
        ErrorCode.GOVERNANCE_HOLD,
        detail="AC_Risk=0.68 exceeds HOLD threshold",
        context={"ac_risk": 0.68, "verdict": "HOLD"},
    )
    print(json.dumps(error, indent=2))
