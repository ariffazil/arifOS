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

from arifosmcp.specs.contracts import (
    # Enums
    VerdictCode,
    RiskTier,
    SessionState,
    TrinityAspect,
    # Identity
    SessionAnchor,
    ToolAuthContext,
    # Telemetry
    WitnessTriple,
    TelemetryEnvelope,
    ConstitutionalHealthView,
    # Evidence
    EvidenceBundle,
    # Verdict
    VerdictRecord,
    # Tool inputs
    JudgeVerdictInput,
    InitSessionInput,
    SenseRealityInput,
    RouteExecutionInput,
    # Utils
    make_telemetry_seed,
    compute_psi_le,
)

from arifosmcp.specs.tool_specs import (
    ToolSpec,
    CANONICAL_TOOL_SPECS,
    get_tool_spec,
    TOOL_NAMES,
)

from arifosmcp.specs.resource_specs import (
    ResourceSpec,
    CANONICAL_RESOURCE_SPECS,
    get_resource_spec,
    RESOURCE_URIS,
)

from arifosmcp.specs.prompt_specs import (
    PromptSpec,
    CANONICAL_PROMPT_SPECS,
    get_prompt_spec,
    PROMPT_NAMES,
)

from arifosmcp.specs.chatgpt_subset import (
    CHATGPT_TOOL_NAMES,
    CHATGPT_RESOURCE_URIS,
    CHATGPT_PROMPT_NAMES,
    is_chatgpt_safe_tool,
    is_chatgpt_safe_resource,
    is_chatgpt_safe_prompt,
    validate_chatgpt_safety,
    get_chatgpt_manifest,
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
