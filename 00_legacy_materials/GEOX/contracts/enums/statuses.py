from typing import List, Dict, Any, Optional
from enum import Enum


class Dimension(str, Enum):
    PROSPECT = "prospect"
    WELL = "well"
    EARTH3D = "earth3d"
    MAP = "map"
    CROSS = "cross"
    SECTION = "section"
    TIME4D = "time4d"
    PHYSICS = "physics"
    DASHBOARD = "dashboard"


class ExecutionStatus(str, Enum):
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"
    HALT = "HALT"


class GovernanceStatus(str, Enum):
    APPROVED = "APPROVED"
    QUALIFY = "QUALIFY"
    HOLD = "HOLD"
    VOID = "VOID"
    SEAL = "SEAL"


Verdict = GovernanceStatus


class ArtifactStatus(str, Enum):
    USABLE = "USABLE"
    STAGED = "STAGED"
    REJECTED = "REJECTED"
    INCOMPLETE = "INCOMPLETE"
    DRAFT = "DRAFT"
    VERIFIED = "VERIFIED"
    COMPUTED = "COMPUTED"
    LOADED = "LOADED"
    IN_REVIEW = "IN_REVIEW"


class FloorStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    VOID = "void"
    HALT = "halt"


class Runtime(str, Enum):
    VPS = "vps"
    FASTMCP = "fastmcp"
    LOCAL = "local"


class Transport(str, Enum):
    HTTP = "http"
    MCP = "mcp"
    STDIO = "stdio"
    SSE = "sse"


class ToolCategory(str, Enum):
    FOUNDATION = "foundation"
    PHYSICS = "physics"
    BRIDGE = "bridge"
    DEMO = "demo"
    SYSTEM = "system"


class ProspectVerdict(str, Enum):
    DRO = "DRO"
    DRIL = "DRIL"
    HOLD = "HOLD"
    DROP = "DROP"


class ClaimTag(str, Enum):
    CLAIM = "CLAIM"
    PLAUSIBLE = "PLAUSIBLE"
    HYPOTHESIS = "HYPOTHESIS"


# Type aliases
VerdictCode = GovernanceStatus
FloorCode = str
DimensionCode = str

# Constants
CONSTITUTIONAL_FLOORS = [
    "F1",
    "F2",
    "F3",
    "F4",
    "F5",
    "F6",
    "F7",
    "F8",
    "F9",
    "F10",
    "F11",
    "F12",
    "F13",
]
CANONICAL_TOOLS = []
SEAL = "DITEMPA BUKAN DIBERI"


def get_standard_envelope(
    primary_artifact: Dict[str, Any],
    tool_class: str = "compute",
    execution_status: ExecutionStatus = ExecutionStatus.SUCCESS,
    governance_status: GovernanceStatus = GovernanceStatus.QUALIFY,
    artifact_status: ArtifactStatus = ArtifactStatus.DRAFT,
    uncertainty: str = "Moderate",
    evidence_refs: Optional[List[str]] = None,
    diagnostics: Optional[Dict[str, Any]] = None,
    ui_resource_uri: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Canonical MCP Apps Response Envelope.
    Follows MCP spec + arifOS Governance + MCP Apps UI.
    """
    response = {
        "execution_status": (
            execution_status.value
            if isinstance(execution_status, ExecutionStatus)
            else execution_status
        ),
        "tool_class": tool_class,
        "governance_status": (
            governance_status.value
            if isinstance(governance_status, GovernanceStatus)
            else governance_status
        ),
        "artifact_status": (
            artifact_status.value
            if isinstance(artifact_status, ArtifactStatus)
            else artifact_status
        ),
        "primary_artifact": primary_artifact,
        "uncertainty": uncertainty,
        "evidence_refs": evidence_refs or [],
        "diagnostics": diagnostics or {},
    }

    # MCP Apps UI support
    if ui_resource_uri:
        response["_meta"] = {"ui": {"resourceUri": ui_resource_uri}}

    return response
