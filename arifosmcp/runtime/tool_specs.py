"""
arifosmcp/runtime/tool_specs.py — arifOS MCP Canonical Tool Specifications
══════════════════════════════════════════════════════════════════════════════════════

11 canonical tools.
Clean naming: arifos_{verb} for tools, {noun}_surface for apps.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from dataclasses import dataclass, field
from typing import Any, Literal


@dataclass(frozen=True)
class ToolSpec:
    """Canonical tool specification with visibility control."""

    name: str  # arifos_{verb} format
    stage: str  # Execution stage (documentation only)
    purpose: str  # One-line purpose
    role: str = ""  # Role-based purpose (alias for purpose)
    layer: Literal["GOVERNANCE", "INTELLIGENCE", "MACHINE", "EXECUTION", "SURFACE"] = "MACHINE"
    description: str = ""
    trinity: Literal["Δ", "Ω", "Ψ", "Δ/Ω", "Δ/Ψ", "Ω/Ψ", "ALL"] = "ALL"
    floors: tuple[str, ...] = field(default_factory=tuple)  # F1-F13 that apply
    input_schema: dict[str, Any] = field(default_factory=dict)
    visibility: Literal["public", "internal"] = "internal"
    default_tier: str = "medium"
    default_budget_tier: str = "medium"  # Alias
    min_budget_tier: str = "small"
    max_budget_tier: str = "large"
    overflow_policy: str = "truncate"
    readonly: bool = True
    outputs: dict[str, Any] = field(default_factory=dict)
    # FastMCP v3 / MCP v2 tool annotations
    version: str = "2026.04.16"
    read_only_hint: bool = True
    destructive_hint: bool = False
    open_world_hint: bool = True
    idempotent_hint: bool = False
    timeout: float = 30.0


@dataclass(frozen=True)
class ResourceSpec:
    """Canonical resource specification."""

    uri: str
    name: str
    description: str
    mime_type: str = "application/json"
    is_template: bool = False
    visibility: Literal["public", "internal"] = "internal"


# ═══════════════════════════════════════════════════════════════════════════════════════
# HORIZON 33: CANONICAL TOOL SUITE
# ═══════════════════════════════════════════════════════════════════════════════════════

TOOLS: tuple[ToolSpec, ...] = (
    # ─────────────────────────────────────────────────────────────────────────
    # 1. arifos_init — Architect Registry
    # ─────────────────────────────────────────────────────────────────────────
    ToolSpec(
        name="arifos_init",
        stage="000",
        purpose="Architect registry — Start governed session",
        layer="GOVERNANCE",
        visibility="public",
        description=(
            "Initialize constitutional session with identity binding and telemetry seed. "
            "Modes: init/probe/state/status (safe read modes) | revoke requires human_approval. "
            "probe mode: Session diagnostic checking anchor validity and authority enum compatibility."
        ),
        trinity="Ψ",
        floors=("F11", "F12", "F13"),
        input_schema={
            "type": "object",
            "required": ["actor_id", "intent"],
            "properties": {
                "actor_id": {
                    "type": "string",
                    "minLength": 2,
                    "maxLength": 64,
                    "description": "Identity of the actor initiating this session. Must be unique per operator.",
                },
                "intent": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 20000,
                    "description": "Primary intent or purpose of this session. F1 Amanah commitment.",
                },
                "declared_name": {
                    "type": "string",
                    "maxLength": 64,
                    "description": "Optional human-readable name for this session declaration.",
                },
                "session_id": {
                    "type": "string",
                    "minLength": 8,
                    "maxLength": 128,
                    "description": "Existing session ID to refresh or operate on. If omitted, a new session is created.",
                },
                "risk_tier": {
                    "type": "string",
                    "enum": ["low", "medium", "high", "critical"],
                    "default": "medium",
                    "description": "Risk classification level for this session's operations.",
                },
                "platform": {
                    "type": "string",
                    "enum": ["mcp", "chatgpt_apps", "cursor", "api", "stdio", "unknown"],
                    "default": "unknown",
                    "description": "Platform context from which this session originates.",
                },
                "mode": {
                    "type": "string",
                    "enum": ["init", "refresh", "state", "status", "probe"],
                    "default": "init",
                    "description": "Session operation mode. probe=diagnostic compatibility check. init=new session, refresh=extend existing, state=query current state, status=lightweight health check.",
                },
            },
        },
        read_only_hint=False,
        idempotent_hint=True,
        default_tier="small",
    ),
    # ─────────────────────────────────────────────────────────────────────────
    # 2. arifos_sense — Physics Reality
    # ─────────────────────────────────────────────────────────────────────────
    ToolSpec(
        name="arifos_sense",
        stage="111",
        purpose="Physics reality — Constitutional Reality Sensing",
        layer="MACHINE",
        visibility="public",
        description=(
            "Ground query in physical reality via the 8-stage constitutional sensing protocol: "
            "PARSE → CLASSIFY → DECIDE → PLAN → RETRIEVE → NORMALIZE → GATE → HANDOFF. "
            "Live web search is gated by truth classification — invariants use offline reasoning; "
            "time-sensitive facts trigger live retrieval; ambiguous queries HOLD for narrowing."
        ),
        trinity="Δ",
        floors=("F2", "F3", "F4", "F10"),
        input_schema={
            "type": "object",
            "required": ["query"],
            "properties": {
                "query": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 5000,
                    "description": "Natural language query to ground in physical reality via the 8-stage sensing protocol.",
                },
                "mode": {
                    "type": "string",
                    "enum": ["governed", "search", "ingest", "compass", "atlas", "time"],
                    "default": "governed",
                    "description": "Sensing mode: governed=full constitutional pipeline, search=live web retrieval, ingest=store observation, compass=directional heading, atlas=geospatial grounding, time=temporal context.",
                },
                "session_id": {
                    "type": "string",
                    "description": "Active arifOS session ID. Links this sensing operation to a declared constitutional session.",
                },
                "dry_run": {
                    "type": "boolean",
                    "default": True,
                    "description": "If True, runs the sensing protocol without persisting results or triggering downstream effects.",
                },
            },
        },
    ),
    # ─────────────────────────────────────────────────────────────────────────
    # 3. arifos_mind — Agi Mind
    # ─────────────────────────────────────────────────────────────────────────
    ToolSpec(
        name="arifos_mind",
        stage="333",
        purpose="Agi mind — Structured reasoning with typed cognitive pipeline",
        layer="INTELLIGENCE",
        visibility="public",
        description=(
            "Structured reasoning with typed cognitive pipeline. Modes: "
            "- 'reason' (default): Standard AGI pipeline (sense → mind → heart → judge) "
            "- 'sequential': Constitutionally-governed sequential thinking with templates "
            "- 'step': Add a step to an existing thinking session "
            "- 'branch': Create a reasoning branch from a step "
            "- 'merge': Synthesize insights across branches "
            "- 'review': Review/export a thinking session "
            "Sequential thinking enforces F1-F13 at each step, replacing external Sequential Thinking MCP "
            "with native constitutional governance. Runs the constitutional AGI pipeline producing "
            "a narrow decision_packet for the operator and a full audit_packet for the vault."
        ),
        trinity="Δ",
        floors=("F2", "F4", "F7", "F8"),
        input_schema={
            "type": "object",
            "required": ["query"],
            "properties": {
                "query": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 10000,
                    "description": "Primary query or proposition to reason about. Must be a factual claim, decision, or question.",
                },
                "context": {
                    "type": "string",
                    "description": "Supporting context for the reasoning task. Can be a string narrative, structured JSON object, or array of context strings.",
                },
                "mode": {
                    "type": "string",
                    "enum": [
                        "reason",
                        "sequential",
                        "step",
                        "branch",
                        "merge",
                        "review",
                        "reflect",
                    ],
                    "default": "reason",
                    "description": "Reasoning mode: reason=standard AGI pipeline, sequential=multi-step constitutional chain, step=add a step to existing session, branch=fork a reasoning path, merge=synthesize branches, review=export reasoning, reflect=self-critique.",
                },
                "session_id": {
                    "type": "string",
                    "description": "Active session ID. Required for sequential/step/branch/merge modes to maintain reasoning continuity.",
                },
            },
        },
    ),
    # ─────────────────────────────────────────────────────────────────────────
    # 4. arifos_kernel — Metabolic Router
    # ─────────────────────────────────────────────────────────────────────────
    ToolSpec(
        name="arifos_kernel",
        stage="444",
        purpose="Arifos kernel — Route request to metabolic lane",
        layer="GOVERNANCE",
        visibility="public",
        description="Route request to correct metabolic lane or tool family based on risk and task type.",
        trinity="Δ/Ψ",
        floors=("F4", "F11"),
        input_schema={
            "type": "object",
            "required": ["query"],
            "properties": {
                "query": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 5000,
                    "description": "Primary query string to route to the correct metabolic lane or tool family.",
                },
                "request": {
                    "type": "string",
                    "description": "Alternative query string for backward compatibility with legacy tool aliases.",
                },
                "mode": {
                    "type": "string",
                    "enum": ["kernel", "status"],
                    "default": "kernel",
                    "description": "kernel=route to metabolic lane, status=return current routing decision without executing.",
                },
                "session_id": {
                    "type": "string",
                    "description": "Active session ID for routing context.",
                },
                "actor_id": {
                    "type": "string",
                    "description": "Identity of the requesting actor for authorization checks.",
                },
                "risk_tier": {
                    "type": "string",
                    "enum": ["low", "medium", "high", "critical"],
                    "default": "medium",
                    "description": "Risk tier for this routing decision. Affects which lanes are accessible.",
                },
            },
        },
    ),
    # ─────────────────────────────────────────────────────────────────────────
    # 5. arifos_heart — Red-team Safety
    # ─────────────────────────────────────────────────────────────────────────
    ToolSpec(
        name="arifos_heart",
        stage="666",
        purpose="Arifos heart — Risk simulation and ethical critique",
        layer="INTELLIGENCE",
        visibility="public",
        description="Red-team proposal for ethical risks. Simulate consequences, evaluate against F5, F6, F9.",
        trinity="Ω",
        floors=("F5", "F6", "F9"),
        input_schema={
            "type": "object",
            "required": ["query"],
            "properties": {
                "query": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 5000,
                    "description": "Action, proposal, or policy to ethically evaluate. Must be a concrete statement of intent.",
                },
                "mode": {
                    "type": "string",
                    "enum": ["critique", "simulate"],
                    "default": "critique",
                    "description": "critique=identify risks and violations against F5/F6/F9, simulate=predict downstream consequences.",
                },
                "session_id": {
                    "type": "string",
                    "description": "Active session ID for constitutional context.",
                },
            },
        },
    ),
    # ─────────────────────────────────────────────────────────────────────────
    # 6. arifos_ops — Math Estimator
    # ─────────────────────────────────────────────────────────────────────────
    ToolSpec(
        name="arifos_ops",
        stage="777",
        purpose="Math estimator — Calculate costs and thermodynamics",
        layer="MACHINE",
        visibility="public",
        description="Calculate operation costs, thermodynamics, capacity, and timing with entropy analysis.",
        trinity="Δ",
        floors=("F4", "F5"),
        input_schema={
            "type": "object",
            "required": [],
            "properties": {
                "query": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 2000,
                    "description": "Query or task to estimate thermodynamic and operational cost for.",
                },
                "mode": {
                    "type": "string",
                    "enum": ["cost", "health", "vitals", "entropy", "economic_audit", "metabolism"],
                    "default": "cost",
                    "description": "cost=Landauer gate cost estimate, health=system health gauge, vitals=metabolic telemetry, entropy=information-theoretic entropy analysis, economic_audit=WELL economic thermodynamic audit, metabolism=F1-F13 metabolic dashboard.",
                },
                "session_id": {
                    "type": "string",
                    "description": "Active session ID for context-aware cost estimation.",
                },
            },
        },
    ),
    # ─────────────────────────────────────────────────────────────────────────
    # 7. arifos_judge — Apex Soul (Final Verdict)
    # ─────────────────────────────────────────────────────────────────────────
    ToolSpec(
        name="arifos_judge",
        stage="888",
        purpose="Apex soul — Final constitutional verdict evaluation",
        layer="GOVERNANCE",
        visibility="public",
        description="Final constitutional verdict evaluation. Outputs: SEAL, PARTIAL, VOID, HOLD.",
        trinity="Ψ",
        floors=("F1", "F2", "F3", "F9", "F10", "F12", "F13"),
        input_schema={
            "type": "object",
            "required": ["query", "risk_tier"],
            "properties": {
                "query": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 5000,
                    "description": "Action, decision, or statement to render constitutional verdict on.",
                },
                "risk_tier": {
                    "type": "string",
                    "enum": ["low", "medium", "high", "critical"],
                    "default": "medium",
                    "description": "Risk classification: low=minimal impact, medium=moderate scope, high=significant consequences, critical=irreversible or large-scale harm.",
                },
                "session_id": {
                    "type": "string",
                    "description": "Active session ID linking this verdict to a declared constitutional session.",
                },
            },
        },
        read_only_hint=False,
        idempotent_hint=False,
    ),
    # ─────────────────────────────────────────────────────────────────────────
    # 8. arifos_memory — Engineering Memory
    # ─────────────────────────────────────────────────────────────────────────
    ToolSpec(
        name="arifos_memory",
        stage="555",
        purpose="Engineering memory — Governed context recall",
        layer="INTELLIGENCE",
        visibility="public",
        description="Retrieve governed memory and engineering context from vector store.",
        trinity="Ω",
        floors=("F2", "F10", "F11"),
        input_schema={
            "type": "object",
            "required": ["query"],
            "properties": {
                "query": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 2000,
                    "description": "Semantic query string to search governed memory and engineering context.",
                },
                "mode": {
                    "type": "string",
                    "enum": ["vector_query", "vector_store", "engineer", "query"],
                    "default": "vector_query",
                    "description": "vector_query=semantic search, vector_store=store new memory, engineer=engineering context retrieval, query=exact-match query.",
                },
                "session_id": {
                    "type": "string",
                    "description": "Active session ID for session-scoped memory retrieval.",
                },
            },
        },
    ),
    # ─────────────────────────────────────────────────────────────────────────
    # 9. arifos_vault — Vault Ledger
    # ─────────────────────────────────────────────────────────────────────────
    ToolSpec(
        name="arifos_vault",
        stage="999",
        purpose="Vault ledger — Immutable verdict record (append or read)",
        layer="GOVERNANCE",
        visibility="public",
        description="Append immutable verdict record to Merkle-hashed ledger (mode=append), or query the ledger (mode=read).",
        trinity="Ψ",
        floors=("F1", "F13"),
        input_schema={
            "type": "object",
            "required": [],
            "properties": {
                "verdict": {
                    "type": "string",
                    "enum": ["SEAL", "PARTIAL", "VOID", "HOLD"],
                    "description": "Constitutional verdict to append (mode=append). Ignored in read mode.",
                },
                "evidence": {
                    "type": "string",
                    "description": "Supporting evidence, reasoning chain, or audit trail for this verdict (mode=append).",
                },
                "session_id": {
                    "type": "string",
                    "description": "Session ID this verdict pertains to. Also used as a filter in read mode.",
                },
                "mode": {
                    "type": "string",
                    "enum": ["append", "read"],
                    "default": "append",
                    "description": "append=write a verdict record to the ledger; read=query the ledger with optional filters.",
                },
                "limit": {
                    "type": "integer",
                    "default": 20,
                    "description": "Maximum number of ledger entries to return (read mode only).",
                },
                "since": {
                    "type": "string",
                    "description": "ISO-8601 timestamp — return entries sealed after this time (read mode only).",
                },
                "until": {
                    "type": "string",
                    "description": "ISO-8601 timestamp — return entries sealed before this time (read mode only).",
                },
                "verdict_filter": {
                    "type": "string",
                    "description": "Filter by verdict type: APPROVED, PARTIAL, PAUSE, VOID, HOLD (read mode only).",
                },
            },
        },
        read_only_hint=False,
        idempotent_hint=True,
    ),
    # ─────────────────────────────────────────────────────────────────────────
    # 10. arifos_forge — Code Engine (Execution Bridge)
    # ─────────────────────────────────────────────────────────────────────────
    ToolSpec(
        name="arifos_forge",
        stage="010",
        purpose="Code engine — Delegated Execution Bridge (The 10th Tool)",
        layer="EXECUTION",
        visibility="public",
        description=(
            "Delegated Execution Bridge — The 10th Tool. This tool does NOT execute directly. It: "
            "1. Validates judge verdict is SEAL 2. Constructs signed execution manifest "
            "3. Dispatches to A-FORGE substrate 4. Returns execution receipt. "
            "Constitutional Guarantee: • No execution without judge SEAL • No self-authorization "
            "• All actions logged to vault • Separation of powers preserved."
        ),
        trinity="Δ",
        floors=("F1", "F2", "F7", "F13"),
        input_schema={
            "type": "object",
            "required": ["action", "payload", "session_id", "judge_verdict", "judge_g_star"],
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["shell", "api_call", "contract", "compute"],
                    "description": "Type of execution action: shell=command execution, api_call=REST/GraphQL call, contract=smart contract invocation, compute=distributed computation.",
                },
                "payload": {
                    "type": "object",
                    "description": "Structured execution payload. Format varies by action type: shell takes {command, timeout_ms}, api_call takes {method, url, headers, body}, etc.",
                },
                "session_id": {
                    "type": "string",
                    "description": "Active session ID. Must have a prior arifos_judge SEAL verdict attached.",
                },
                "judge_verdict": {
                    "type": "string",
                    "enum": ["SEAL"],
                    "description": "Must be SEAL. Any other verdict blocks execution. This is the Gate 1 constitutional checkpoint.",
                },
                "judge_g_star": {
                    "type": "number",
                    "description": "Judge G* confidence score from the arifos_judge SEAL verdict. Used for thermodynamic cost accounting.",
                },
                "dry_run": {
                    "type": "boolean",
                    "default": True,
                    "description": "If True, constructs the execution manifest and returns the receipt without dispatching to A-FORGE substrate.",
                },
            },
        },
        read_only_hint=False,
        destructive_hint=True,
        idempotent_hint=False,
    ),
    # ─────────────────────────────────────────────────────────────────────────
    # 11. arifos_gateway — Orthogonality Guard (The 11th Public Tool)
    # ─────────────────────────────────────────────────────────────────────────
    ToolSpec(
        name="arifos_gateway",
        stage="888-Ω",
        purpose="Orthogonality guard — AGI||ASI lane supervisor (Ω_ortho >= 0.95)",
        layer="GOVERNANCE",
        visibility="public",
        description=(
            "Orthogonality Guard — The 11th Public Tool. Supervises AGI||ASI lanes to enforce "
            "Ω_ortho >= 0.95. Computes correlation across tool outputs and model traces; if "
            "correlation exceeds threshold or ontology overlap is detected, returns 888_HOLD. "
            "Prevents physics collapse, governance collapse, and ontology collapse across "
            "arifOS, WEALTH, and GEOX organs."
        ),
        trinity="Ω",
        floors=("F3", "F4", "F9", "F11", "F13"),
        input_schema={
            "type": "object",
            "required": ["session_id"],
            "properties": {
                "session_id": {
                    "type": "string",
                    "description": "Active session ID to evaluate for AGI||ASI orthogonality.",
                },
                "mode": {
                    "type": "string",
                    "enum": ["guard", "audit", "correlate"],
                    "default": "guard",
                    "description": "guard=full orthogonality check and HOLD recommendation, audit=read-only orthogonality report, correlate=compute pairwise tool output correlation matrix.",
                },
                "tool_trace": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "Ordered list of tool call records to evaluate. Each record should have 'name', 'input', and 'output' fields.",
                },
                "correlation_threshold": {
                    "type": "number",
                    "default": 0.95,
                    "description": "Maximum allowed correlation coefficient before 888_HOLD is recommended. Range: 0.0 to 1.0.",
                },
            },
        },
    ),
)


# ═══════════════════════════════════════════════════════════════════════════════════════
# METADATA & UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════════════

TOOL_NAMES = frozenset(t.name for t in TOOLS)
TOOL_COUNT = len(TOOLS)

LEGACY_NAME_MAP: dict[str, str] = {
    "init_anchor": "arifos_init",
    "physics_reality": "arifos_sense",
    "agi_mind": "arifos_mind",
    "asi_heart": "arifos_heart",
    "math_estimator": "arifos_ops",
    "apex_soul": "arifos_judge",
    "engineering_memory": "arifos_memory",
    "vault_ledger": "arifos_vault",
    "architect_registry": "arifos_init",
    "code_engine": "arifos_forge",
}

# ═══════════════════════════════════════════════════════════════════════════════════════
# RESOURCES
# ═══════════════════════════════════════════════════════════════════════════════════════

RESOURCES: tuple[ResourceSpec, ...] = (
    ResourceSpec(
        uri="arifos://doctrine",
        name="Constitutional Doctrine",
        description="The eternal law of arifOS (Ψ).",
        visibility="public",
    ),
    ResourceSpec(
        uri="arifos://vitals",
        name="System Vitals",
        description="Real-time metabolic telemetry (Ω).",
        visibility="public",
    ),
    ResourceSpec(
        uri="arifos://schema",
        name="Complete Blueprint",
        description="Technical schema and ABI definitions (Δ).",
        visibility="public",
    ),
    ResourceSpec(
        uri="arifos://session/{id}",
        name="Ephemeral Instance",
        description="Active session state and governance context.",
        is_template=True,
        visibility="public",
    ),
    ResourceSpec(
        uri="arifos://forge",
        name="Execution Bridge",
        description="Signed execution manifests and receipts.",
        visibility="public",
    ),
)


def normalize_tool_name(name: str) -> str:
    """Normalize tool name (dots to underscores) for arifOS v2."""
    if name.startswith("arifos."):
        return name.replace(".", "_")
    return name


def get_tool_spec(name: str) -> ToolSpec | None:
    """Get tool spec by name."""
    for spec in TOOLS:
        if spec.name == name:
            return spec
    return None


def tool_names() -> tuple[str, ...]:
    """Return all canonical tool names."""
    return tuple(t.name for t in TOOLS)


# Compact compatibility exports
V2_TOOLS = TOOLS
V2_TOOL_NAMES = TOOL_NAMES
PUBLIC_TOOL_SPECS = [t for t in TOOLS if t.visibility == "public"]
PUBLIC_RESOURCE_SPECS = [r for r in RESOURCES if r.visibility == "public"]

__all__ = [
    "ToolSpec",
    "ResourceSpec",
    "TOOLS",
    "RESOURCES",
    "TOOL_NAMES",
    "get_tool_spec",
    "tool_names",
    "PUBLIC_TOOL_SPECS",
    "PUBLIC_RESOURCE_SPECS",
]
