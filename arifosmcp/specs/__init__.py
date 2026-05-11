"""
arifOS MCP Specifications
═══════════════════════════════════════════════════════════════════════════════

Clean separation of MCP primitives:
- contracts: Shared JSON schemas
- tool_specs: 11 canonical executable tools
- resource_specs: 9 read-only context resources
- prompt_specs: 10 workflow templates
- chatgpt_subset: Apps SDK-safe adapter

Import order:
1. contracts (base schemas)
2. tool_specs, resource_specs, prompt_specs (independent)
3. chatgpt_subset (depends on all above)
"""

from arifosmcp.specs.chatgpt_subset import (
    CHATGPT_PROMPT_NAMES,
    CHATGPT_RESOURCE_URIS,
    CHATGPT_TOOL_NAMES,
    get_chatgpt_manifest,
    is_chatgpt_safe_prompt,
    is_chatgpt_safe_resource,
    is_chatgpt_safe_tool,
    validate_chatgpt_safety,
)
from arifosmcp.specs.contracts import (
    ConstitutionalHealthView,
    # Evidence
    EvidenceBundle,
    InitSessionInput,
    # Tool inputs
    JudgeVerdictInput,
    RiskTier,
    RouteExecutionInput,
    SenseRealityInput,
    # Identity
    SessionAnchor,
    SessionState,
    TelemetryEnvelope,
    ToolAuthContext,
    TrinityAspect,
    # Enums
    VerdictCode,
    # Verdict
    VerdictRecord,
    # Telemetry
    WitnessTriple,
    compute_psi_le,
    # Utils
    make_telemetry_seed,
)
from arifosmcp.specs.prompt_specs import (
    CANONICAL_PROMPT_SPECS,
    PROMPT_NAMES,
    PromptSpec,
    get_prompt_spec,
)
from arifosmcp.specs.resource_specs import (
    CANONICAL_RESOURCE_SPECS,
    RESOURCE_URIS,
    ResourceSpec,
    get_resource_spec,
)
from arifosmcp.specs.tool_specs import (
    CANONICAL_TOOL_SPECS,
    TOOL_NAMES,
    ToolSpec,
    get_tool_spec,
)

__all__ = [
    # Contracts
    "VerdictCode",
    "RiskTier",
    "SessionState",
    "TrinityAspect",
    "SessionAnchor",
    "ToolAuthContext",
    "WitnessTriple",
    "TelemetryEnvelope",
    "ConstitutionalHealthView",
    "EvidenceBundle",
    "VerdictRecord",
    "JudgeVerdictInput",
    "InitSessionInput",
    "SenseRealityInput",
    "RouteExecutionInput",
    "make_telemetry_seed",
    "compute_psi_le",
    # Tool specs
    "ToolSpec",
    "CANONICAL_TOOL_SPECS",
    "get_tool_spec",
    "TOOL_NAMES",
    # Resource specs
    "ResourceSpec",
    "CANONICAL_RESOURCE_SPECS",
    "get_resource_spec",
    "RESOURCE_URIS",
    # Prompt specs
    "PromptSpec",
    "CANONICAL_PROMPT_SPECS",
    "get_prompt_spec",
    "PROMPT_NAMES",
    # ChatGPT subset
    "CHATGPT_TOOL_NAMES",
    "CHATGPT_RESOURCE_URIS",
    "CHATGPT_PROMPT_NAMES",
    "is_chatgpt_safe_tool",
    "is_chatgpt_safe_resource",
    "is_chatgpt_safe_prompt",
    "validate_chatgpt_safety",
    "get_chatgpt_manifest",
]
