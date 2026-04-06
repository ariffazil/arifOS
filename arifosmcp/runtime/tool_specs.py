from dataclasses import dataclass
from typing import Any, Literal


@dataclass(frozen=True)
class ToolSpec:
    name: str
    stage: str
    role: str
    layer: str
    description: str
    trinity: str
    floors: tuple[str, ...]
    input_schema: dict[str, Any]
    default_budget_tier: str = "medium"
    min_budget_tier: str = "micro"
    max_budget_tier: str = "large"
    overflow_policy: str = "truncate"
    readonly: bool = True


@dataclass(frozen=True)
class ResourceSpec:
    uri: str
    name: str
    description: str
    mime_type: str = "application/json"
    # Unified flag for resource templates
    is_template: bool = False


@dataclass(frozen=True)
class PromptSpec:
    name: str
    description: str
    arguments: list[dict[str, Any]] = None


MegaToolName = Literal[
    "init_session_anchor",
    "get_tool_registry",
    "sense_reality",
    "reason_synthesis",
    "critique_safety",
    "route_execution",
    "load_memory_context",
    "estimate_ops",
    "judge_verdict",
    "record_vault_entry",
    "execute_vps_task",
]

MEGA_TOOLS: tuple[str, ...] = (
    "init_session_anchor",
    "get_tool_registry",
    "sense_reality",
    "reason_synthesis",
    "critique_safety",
    "route_execution",
    "load_memory_context",
    "estimate_ops",
    "judge_verdict",
    "record_vault_entry",
    "execute_vps_task",
)


def _build_mega_schema(
    tool_name: str,
    modes: list[str],
    payload_properties: dict[str, Any],
    required_payload: list[str] = None,
) -> dict[str, Any]:
    """Helper to build the unified request envelope schema for a mega-tool."""
    return {
        "type": "object",
        "additionalProperties": True,
        "required": ["mode", "payload"],
        "properties": {
            "mode": {
                "type": "string",
                "description": f"Mode selector for {tool_name}.",
                "enum": modes,
            },
            "payload": {
                "type": "object",
                "description": "Mode-specific payload.",
                "required": required_payload or [],
                "properties": payload_properties,
                "additionalProperties": True,
            },
            "auth_context": {
                "type": ["object", "null"],
                "description": "Optional auth context for continuity (F11) and sovereignty (F13).",
                "additionalProperties": True,
            },
            "caller_context": {
                "type": ["object", "null"],
                "description": "Optional caller metadata.",
                "additionalProperties": True,
            },
            "risk_tier": {
                "type": "string",
                "description": "Requested risk posture.",
                "enum": ["low", "medium", "high", "critical"],
                "default": "medium",
            },
            "dry_run": {
                "type": "boolean",
                "description": "If true, compute/plan/validate only.",
                "default": True,
            },
            "allow_execution": {
                "type": "boolean",
                "description": "If true, execution is permitted IF floors pass.",
                "default": False,
            },
            "debug": {
                "type": "boolean",
                "description": "Include additional diagnostics.",
                "default": False,
            },
            "request_id": {
                "type": "string",
                "description": "Client trace ID.",
                "minLength": 8,
                "maxLength": 128,
            },
            "timestamp": {
                "type": "string",
                "description": "ISO 8601 timestamp.",
                "format": "date-time",
            },
        },
    }


PUBLIC_TOOL_SPECS: tuple[ToolSpec, ...] = (
    # ─── ⚖️ GOVERNANCE LAYER (G-1 to G-4) ───
    ToolSpec(
        name="init_session_anchor",
        stage="000_INIT",
        role="Init Anchor",
        layer="GOVERNANCE",
        description="Start a governed session and bind the initial telemetry seed.",
        trinity="PSI Ψ",
        floors=("F11", "F12", "F13"),
        input_schema=_build_mega_schema(
            "init_session_anchor",
            ["init", "revoke", "refresh", "state", "status"],
            {
                "actor_id": {"type": "string", "minLength": 2, "maxLength": 64},
                "intent": {"type": "string", "minLength": 1, "maxLength": 20000},
                "declared_name": {"type": "string", "maxLength": 64},
                "session_id": {"type": "string", "minLength": 8, "maxLength": 128},
            },
        ),
        default_budget_tier="small",
    ),
    ToolSpec(
        name="get_tool_registry",
        stage="M-4_ARCH",
        role="Architect Registry",
        layer="MACHINE",
        description="Discover arifOS tool graph, modes, and model capabilities.",
        trinity="DELTA Δ",
        floors=("F10", "F11"),
        input_schema=_build_mega_schema(
            "get_tool_registry",
            ["list", "read", "context", "model_catalog"],
            {
                "uri": {"type": "string"},
                "session_id": {"type": "string"},
            },
        ),
    ),
    ToolSpec(
        name="sense_reality",
        stage="111_SENSE",
        role="Physics Reality",
        layer="MACHINE",
        description="Time grounding, evidence checks, and reality state verification.",
        trinity="DELTA Δ",
        floors=("F2", "F3", "F10"),
        input_schema=_build_mega_schema(
            "sense_reality",
            ["search", "ingest", "compass", "atlas", "time"],
            {
                "query": {"type": "string"},
                "operation": {"type": "string"},
                "session_id": {"type": "string"},
            },
        ),
    ),
    ToolSpec(
        name="reason_synthesis",
        stage="333_MIND",
        role="AGI Mind",
        layer="INTELLIGENCE",
        description="Multi-source synthesis and structured first-principles reasoning.",
        trinity="DELTA Δ",
        floors=("F2", "F4", "F7", "F8"),
        input_schema=_build_mega_schema(
            "reason_synthesis",
            ["reason", "reflect", "forge"],
            {
                "query": {"type": "string"},
                "context": {"type": "string"},
                "session_id": {"type": "string"},
            },
            required_payload=["query"],
        ),
    ),
    ToolSpec(
        name="critique_safety",
        stage="666_HEART",
        role="ASI Heart",
        layer="INTELLIGENCE",
        description="Safety, dignity, and adversarial critique of content or proposals.",
        trinity="OMEGA Ω",
        floors=("F5", "F6", "F9"),
        input_schema=_build_mega_schema(
            "critique_safety",
            ["critique", "simulate"],
            {"content": {"type": "string"}, "session_id": {"type": "string"}},
            required_payload=["content"],
        ),
    ),
    ToolSpec(
        name="route_execution",
        stage="444_ROUTER",
        role="arifOS Kernel",
        layer="GOVERNANCE",
        description="Route request to the correct metabolic lane or tool family.",
        trinity="DELTA/PSI",
        floors=("F4", "F11"),
        input_schema=_build_mega_schema(
            "route_execution",
            ["kernel", "status"],
            {
                "query": {"type": "string", "minLength": 1},
                "session_id": {"type": "string"},
            },
        ),
    ),
    ToolSpec(
        name="load_memory_context",
        stage="555_MEMORY",
        role="Engineering Memory",
        layer="INTELLIGENCE",
        description="Retrieve governed memory and engineering context from vector store.",
        trinity="OMEGA Ω",
        floors=("F10", "F11", "F2"),
        input_schema=_build_mega_schema(
            "load_memory_context",
            ["vector_query", "vector_store", "engineer", "query"],
            {
                "query": {"type": "string"},
                "session_id": {"type": "string"},
            },
        ),
    ),
    ToolSpec(
        name="estimate_ops",
        stage="444_ROUTER",
        role="Math Estimator",
        layer="MACHINE",
        description="Calculate operation costs, thermodynamics, capacity, and timing.",
        trinity="DELTA Δ",
        floors=("F4", "F5"),
        input_schema=_build_mega_schema(
            "estimate_ops",
            ["cost", "health", "vitals", "entropy"],
            {"action_description": {"type": "string"}, "session_id": {"type": "string"}},
        ),
    ),
    ToolSpec(
        name="judge_verdict",
        stage="888_JUDGE",
        role="Apex Soul",
        layer="GOVERNANCE",
        description="Final constitutional verdict evaluation and hold logic enforcement.",
        trinity="PSI Ψ",
        floors=("F3", "F12", "F13"),
        input_schema=_build_mega_schema(
            "judge_verdict",
            ["judge", "rules", "validate", "hold"],
            {
                "candidate_action": {"type": "string"},
                "risk_tier": {"type": "string", "enum": ["low", "medium", "high", "critical"]},
                "telemetry": {"type": "object"},
                "session_id": {"type": "string"},
            },
        ),
    ),
    ToolSpec(
        name="record_vault_entry",
        stage="999_VAULT",
        role="Vault Ledger",
        layer="GOVERNANCE",
        description="Append immutable verdict record to the Merkle-hashed ledger.",
        trinity="PSI Ψ",
        floors=("F1", "F13"),
        input_schema=_build_mega_schema(
            "record_vault_entry",
            ["seal", "verify"],
            {
                "verdict": {"type": "string"},
                "evidence": {"type": "string"},
                "session_id": {"type": "string"},
            },
        ),
    ),
    ToolSpec(
        name="execute_vps_task",
        stage="M-3_EXEC",
        role="Code Engine",
        layer="MACHINE",
        description="Redirect or dispatch execution tasks to the sovereign VPS executor.",
        trinity="ALL",
        floors=("F1",),
        input_schema=_build_mega_schema(
            "execute_vps_task",
            ["fs", "process", "net", "tail", "replay"],
            {
                "command": {"type": "string"},
                "session_id": {"type": "string"},
            },
        ),
    ),
)

# Subset for ChatGPT Apps
CHATGPT_APP_TOOL_NAMES = {
    "get_constitutional_health",
    "render_vault_seal",
    "list_recent_verdicts",
}

PUBLIC_RESOURCE_SPECS: tuple[ResourceSpec, ...] = (
    ResourceSpec(
        uri="arifos://bootstrap",
        name="arifOS Bootstrap",
        description="Startup path, canonical sequence, and system entry guide.",
    ),
    ResourceSpec(
        uri="arifos://governance/floors",
        name="arifOS Governance",
        description="Constitutional F1-F13 thresholds, doctrine, and formal criteria.",
    ),
    ResourceSpec(
        uri="arifos://status/vitals",
        name="arifOS Vitals",
        description="Current server health, deployment info, and version status.",
    ),
    ResourceSpec(
        uri="arifos://sessions/{session_id}/vitals",
        name="Session Vitals",
        description="Session-specific telemetry snapshot and thermodynamic state.",
        is_template=True,
    ),
    ResourceSpec(
        uri="arifos://agents/skills",
        name="arifOS Skills",
        description="Consolidated agent skills and atomic competence registry.",
    ),
    ResourceSpec(
        uri="arifos://tools/{tool_name}",
        name="Tool Contract",
        description="Detailed contract, examples, and auth requirements for a specific tool.",
        is_template=True,
    ),
    ResourceSpec(
        uri="arifos://vault/recent",
        name="Recent Verdicts",
        description="Read-only summary of the most recent constitutional verdict ledger.",
    ),
    ResourceSpec(
        uri="ui://arifos/vault-seal-widget.html",
        name="Vault Seal Widget",
        description="HTML resource for ChatGPT Apps widget rendering.",
        mime_type="text/html",
    ),
)

PUBLIC_PROMPT_SPECS: tuple[PromptSpec, ...] = (
    PromptSpec(
        name="prompt_init_anchor",
        description="Start a governed arifOS session template.",
        arguments=[{"name": "actor_id", "required": True}, {"name": "intent", "required": True}],
    ),
    PromptSpec(
        name="prompt_sense_reality",
        description="Gather evidence and ground in present reality template.",
        arguments=[{"name": "query", "required": True}],
    ),
    PromptSpec(
        name="prompt_reason_synthesis",
        description="Structured reasoning with uncertainty bands template.",
        arguments=[{"name": "task", "required": True}],
    ),
    PromptSpec(
        name="prompt_critique_safety",
        description="Safety, dignity, and adversarial critique template.",
        arguments=[{"name": "proposal", "required": True}],
    ),
    PromptSpec(
        name="prompt_route_kernel",
        description="Choose metabolic tool path and next lane template.",
        arguments=[{"name": "request", "required": True}],
    ),
    PromptSpec(
        name="prompt_memory_recall",
        description="Pull governed memory for engineering tasks template.",
        arguments=[{"name": "query", "required": True}],
    ),
    PromptSpec(
        name="prompt_estimate_ops",
        description="Compute costs, capacity, and timelines template.",
        arguments=[{"name": "action", "required": True}],
    ),
    PromptSpec(
        name="prompt_judge_verdict",
        description="Produce final constitutional verdict block template.",
        arguments=[
            {"name": "task", "required": True},
            {"name": "risk_tier", "required": True},
            {"name": "telemetry_json", "required": False},
        ],
    ),
    PromptSpec(
        name="prompt_human_explainer",
        description="Translate machine verdict into plain human explanation template.",
        arguments=[{"name": "verdict", "required": True}, {"name": "reasoning", "required": True}],
    ),
    PromptSpec(
        name="prompt_vault_record",
        description="Prepare immutable vault logging narrative and JSON template.",
        arguments=[{"name": "decision", "required": True}, {"name": "evidence", "required": True}],
    ),
)
