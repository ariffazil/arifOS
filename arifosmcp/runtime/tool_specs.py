"""
arifosmcp/runtime/tool_specs.py — arifOS MCP Canonical Tool Specifications

10 sovereign tools. Clean naming: arifos.{verb}
Visibility: public (4) | internal (6)

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
    layer: Literal["GOVERNANCE", "INTELLIGENCE", "MACHINE", "EXECUTION"]
    description: str
    trinity: Literal["Δ", "Ω", "Ψ", "Δ/Ω", "Δ/Ψ", "Ω/Ψ", "ALL"]
    floors: tuple[str, ...]  # F1-F13 that apply
    input_schema: dict[str, Any]
    visibility: Literal["public", "internal"] = "internal"  # public = 3 tools only
    default_tier: str = "medium"
    readonly: bool = True
    outputs: dict[str, Any] = field(default_factory=dict)  # Machine-readable output schema
    # MCP v2 tool annotations (OpenAI/ChatGPT compatibility)
    read_only_hint: bool = True       # readOnlyHint: no environment modification
    destructive_hint: bool = False     # destructiveHint: may perform destructive updates
    open_world_hint: bool = True      # openWorldHint: interacts with external world
    idempotent_hint: bool = False     # idempotentHint: repeated calls have no extra effect


# ═══════════════════════════════════════════════════════════════════════════════
# MCP v2: 9 SOVEREIGN CORE TOOLS
# ═══════════════════════════════════════════════════════════════════════════════

TOOLS: tuple[ToolSpec, ...] = (
    # ─────────────────────────────────────────────────────────────────────────
    # 1. arifos.init — Session Initialization (was 000_INIT, init_anchor)
    # ─────────────────────────────────────────────────────────────────────────
    ToolSpec(
        name="arifos_init",
        stage="000",
        purpose="Start governed session + session diagnostics",
        layer="GOVERNANCE",
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
                "actor_id": {"type": "string", "minLength": 2, "maxLength": 64},
                "intent": {"type": "string", "minLength": 1, "maxLength": 20000},
                "declared_name": {"type": "string", "maxLength": 64},
                "session_id": {"type": "string", "minLength": 8, "maxLength": 128},
                "risk_tier": {
                    "type": "string",
                    "enum": ["low", "medium", "high", "critical"],
                    "default": "medium",
                },
                "platform": {
                    "type": "string",
                    "enum": ["mcp", "chatgpt_apps", "cursor", "api", "stdio", "unknown"],
                    "default": "unknown",
                },
                "mode": {
                    "type": "string",
                    "enum": ["init", "refresh", "state", "status", "probe"],
                    "default": "init",
                    "description": "Session operation mode. probe=diagnostic compatibility check. revoke=separate arifos.session tool (requires human_approval).",
                },
            },
        },
        default_tier="small",
        read_only_hint=True,       # Default mode is init (read-like)
        destructive_hint=False,    # Not primarily destructive
        open_world_hint=False,     # Closed session management domain
        idempotent_hint=True,      # Idempotent under same session
    ),
    # ─────────────────────────────────────────────────────────────────────────
    # 2. arifos.sense — Constitutional Reality Sensing (was 111_SENSE, physics_reality)
    # ─────────────────────────────────────────────────────────────────────────
    ToolSpec(
        name="arifos_sense",
        stage="111",
        purpose="Constitutional reality sensing — 8-stage governed protocol",
        layer="MACHINE",
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
                    "description": "Query to classify and ground in reality",
                },
                "mode": {
                    "type": "string",
                    "enum": ["governed", "search", "ingest", "compass", "atlas", "time"],
                    "default": "governed",
                    "description": (
                        "'governed' = full 8-stage constitutional protocol (recommended). "
                        "Legacy modes: 'search' (raw), 'ingest' (URL fetch), 'compass' (auto-detect), "
                        "'atlas' (discovery), 'time' (clock grounding)."
                    ),
                },
                "session_id": {"type": "string"},
                "intent": {"type": "string", "description": "Optional user intent hint"},
                "query_frame": {
                    "type": "object",
                    "description": "Optional: {domain, time_scope, jurisdiction}",
                },
                "dry_run": {
                    "type": "boolean",
                    "default": True,
                    "description": "False = execute live retrieval; True = plan only (no HTTP calls)",
                },
            },
        },
    ),
    # ─────────────────────────────────────────────────────────────────────────
    # 3. arifos.mind — Structured Reasoning (was 333_MIND, agi_mind)
    # ─────────────────────────────────────────────────────────────────────────
    ToolSpec(
        name="arifos_mind",
        stage="333",
        purpose="Structured reasoning + synthesis",
        layer="INTELLIGENCE",
        description="Multi-source synthesis and structured first-principles reasoning with uncertainty bands.",
        trinity="Δ",
        floors=("F2", "F4", "F7", "F8"),
        input_schema={
            "type": "object",
            "required": ["query"],
            "properties": {
                "query": {"type": "string", "description": "Task or question to reason about"},
                "context": {"type": "string", "description": "Additional context for reasoning"},
                "mode": {
                    "type": "string",
                    "enum": ["reason", "sequential", "step", "branch", "merge", "review"],
                    "default": "reason",
                    "description": "reason=AGI pipeline; sequential=constitutional step-thinking; step/branch/merge/review=thinking session ops",
                },
                "session_id": {"type": "string"},
            },
        },
    ),
    # ─────────────────────────────────────────────────────────────────────────
    # 4. arifos.kernel — Execution Lane Selection (was 444_ROUT, arifos.route)
    # ─────────────────────────────────────────────────────────────────────────
    ToolSpec(
        name="arifos_kernel",
        stage="444",
        purpose="Execution lane selection",
        layer="GOVERNANCE",
        description="Route request to correct metabolic lane or tool family based on risk and task type.",
        trinity="Δ/Ψ",
        floors=("F4", "F11"),
        input_schema={
            "type": "object",
            "required": ["request"],
            "properties": {
                "request": {"type": "string", "minLength": 1, "description": "Request to route"},
                "mode": {"type": "string", "enum": ["kernel", "status"], "default": "kernel"},
                "session_id": {"type": "string"},
            },
        },
    ),
    # ─────────────────────────────────────────────────────────────────────────
    # 5. arifos.heart — Safety Critique (was 666_HEART, asi_heart)
    # ─────────────────────────────────────────────────────────────────────────
    ToolSpec(
        name="arifos_heart",
        stage="666",
        purpose="Safety, dignity, adversarial critique",
        layer="INTELLIGENCE",
        description="Red-team proposal for ethical risks. Simulate consequences, evaluate against F5, F6, F9.",
        trinity="Ω",
        floors=("F5", "F6", "F9"),
        input_schema={
            "type": "object",
            "required": ["content"],
            "properties": {
                "content": {"type": "string", "description": "Content or proposal to critique"},
                "mode": {"type": "string", "enum": ["critique", "simulate"], "default": "critique"},
                "session_id": {"type": "string"},
            },
        },
    ),
    # ─────────────────────────────────────────────────────────────────────────
    # 6. arifos.ops — Cost Estimation (was 777_OPS, math_estimator)
    # ─────────────────────────────────────────────────────────────────────────
    ToolSpec(
        name="arifos_ops",
        stage="777",
        purpose="Cost, thermodynamic, capacity estimation",
        layer="MACHINE",
        description="Calculate operation costs, thermodynamics, capacity, and timing with entropy analysis.",
        trinity="Δ",
        floors=("F4", "F5"),
        input_schema={
            "type": "object",
            "required": ["action"],
            "properties": {
                "action": {"type": "string", "description": "Action to estimate costs for"},
                "mode": {
                    "type": "string",
                    "enum": ["cost", "health", "vitals", "entropy"],
                    "default": "cost",
                },
                "session_id": {"type": "string"},
            },
        },
    ),
    # ─────────────────────────────────────────────────────────────────────────
    # 7. arifos.judge — Constitutional Verdict (was 888_JUDGE, apex_soul)
    # ─────────────────────────────────────────────────────────────────────────
    ToolSpec(
        name="arifos_judge",
        stage="888",
        purpose="Constitutional verdict engine",
        layer="GOVERNANCE",
        description="Final constitutional verdict evaluation. Outputs: SEAL, PARTIAL, VOID, HOLD.",
        trinity="Ψ",
        floors=("F1", "F2", "F3", "F9", "F10", "F12", "F13"),
        input_schema={
            "type": "object",
            "required": ["candidate_action", "risk_tier"],
            "properties": {
                "candidate_action": {"type": "string", "description": "Action to judge"},
                "risk_tier": {
                    "type": "string",
                    "enum": ["low", "medium", "high", "critical"],
                    "default": "medium",
                },
                "telemetry": {"type": "object", "description": "Optional telemetry data"},
                "session_id": {"type": "string"},
            },
        },
    ),
    # ─────────────────────────────────────────────────────────────────────────
    # 8. arifos.memory — Governed Recall (was 555_MEMORY, engineering_memory)
    # ─────────────────────────────────────────────────────────────────────────
    ToolSpec(
        name="arifos_memory",
        stage="555",
        purpose="Governed memory + recall",
        layer="INTELLIGENCE",
        description="Retrieve governed memory and engineering context from vector store.",
        trinity="Ω",
        floors=("F2", "F10", "F11"),
        input_schema={
            "type": "object",
            "required": ["query"],
            "properties": {
                "query": {"type": "string", "description": "Memory query"},
                "mode": {
                    "type": "string",
                    "enum": ["vector_query", "vector_store", "engineer", "query"],
                    "default": "vector_query",
                },
                "session_id": {"type": "string"},
            },
        },
        read_only_hint=False,      # Has vector_store/engineer modes (write)
        destructive_hint=True,        # vector_store writes to vector DB
        open_world_hint=False,        # Closed memory domain
        idempotent_hint=False,        # vector_store is not idempotent
    ),
    # ─────────────────────────────────────────────────────────────────────────
    # 9. arifos.vault — Immutable Logging (was 999_VAULT, vault_ledger)
    # ─────────────────────────────────────────────────────────────────────────
    ToolSpec(
        name="arifos_vault",
        stage="999",
        purpose="Immutable verdict logging",
        layer="GOVERNANCE",
        description="Append immutable verdict record to Merkle-hashed ledger.",
        trinity="Ψ",
        floors=("F1", "F13"),
        input_schema={
            "type": "object",
            "required": ["verdict"],
            "properties": {
                "verdict": {
                    "type": "string",
                    "enum": ["SEAL", "PARTIAL", "VOID", "HOLD"],
                    "description": "Verdict to log",
                },
                "evidence": {"type": "string", "description": "Evidence summary"},
                "session_id": {"type": "string"},
            },
        },
    ),
    # ─────────────────────────────────────────────────────────────────────────
    # 10. arifos.forge — Delegated Execution Bridge (was shell_forge)
    # ─────────────────────────────────────────────────────────────────────────
    ToolSpec(
        name="arifos_forge",
        stage="010",
        purpose="Delegated execution to AF-FORGE substrate",
        layer="EXECUTION",
        description="Issue signed execution manifest to AF-FORGE substrate. Requires judge SEAL. Preserves separation of powers.",
        trinity="Δ",
        floors=("F1", "F2", "F7", "F13"),
        input_schema={
            "type": "object",
            "required": ["action", "payload", "session_id", "judge_verdict", "judge_g_star"],
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["shell", "api_call", "contract", "compute", "container", "vm"],
                    "description": "Execution type",
                },
                "payload": {"type": "object", "description": "Action-specific parameters"},
                "session_id": {"type": "string"},
                "judge_verdict": {
                    "type": "string",
                    "enum": ["SEAL"],
                    "description": "Must be SEAL from arifos.judge",
                },
                "judge_g_star": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "description": "G★ score at time of verdict",
                },
                "constraints": {
                    "type": "object",
                    "description": "Resource limits (cpu, memory, timeout)",
                },
                "dry_run": {
                    "type": "boolean",
                    "default": True,
                    "description": "Generate manifest without dispatch",
                },
                "af_forge_endpoint": {"type": "string", "description": "Target substrate endpoint"},
            },
        },
    ),
    # ─────────────────────────────────────────────────────────────────────────
    # 11. arifos.reply — Governed Reply Compositor (AGI Reply Protocol v3)
    # ─────────────────────────────────────────────────────────────────────────
    # Composite orchestrator: enforces memory→sense→mind→heart→ops→judge→vault
    # in deterministic order. Prompt reply_protocol_v3 defines the contract;
    # this tool enforces execution order so the LLM cannot skip or reorder stages.
    # Use instead of chaining 7 tools manually.
    # ─────────────────────────────────────────────────────────────────────────
    ToolSpec(
        name="arifos_reply",
        stage="000-999",
        purpose="Governed reply compositor — deterministic dual-axis reply pipeline",
        layer="GOVERNANCE",
        description=(
            "Composite orchestrator for AGI Reply Protocol v3. "
            "Internally runs: memory → sense → mind → heart → ops → judge → [vault/forge]. "
            "Emits AgiReplyEnvelopeHuman (recipient=human) or AgiReplyEnvelopeAgent (recipient=agent). "
            "Every output includes: TO/CC/TITLE/KEY_CONTEXT header, RACI block, "
            "computed τ, constitutional floor tags, SEAL signoff. "
            "888 HOLD blocks forge. F1/F13 triggers require human:arif ratification. "
            "Schema at arifos://reply/schemas. Session state at arifos://reply/context-pack."
        ),
        trinity="ALL",
        floors=("F1", "F2", "F3", "F4", "F7", "F9", "F11", "F13"),
        visibility="public",
        readonly=False,
        input_schema={
            "type": "object",
            "required": ["query", "session_id"],
            "properties": {
                "query": {
                    "type": "string",
                    "description": "User query or agent task to govern and reply to",
                },
                "session_id": {"type": "string"},
                "recipient": {
                    "type": "string",
                    "enum": ["human", "agent", "auto"],
                    "default": "auto",
                    "description": (
                        "auto → classify via sense stage. "
                        "human → AgiReplyEnvelopeHuman. "
                        "agent → AgiReplyEnvelopeAgent."
                    ),
                },
                "depth": {
                    "type": "string",
                    "enum": ["SURFACE", "ENGINEER", "ARCHITECT"],
                    "default": "ENGINEER",
                },
                "compression": {
                    "type": "string",
                    "enum": ["FULL", "DELTA", "SIGNAL_ONLY"],
                    "default": "DELTA",
                    "description": (
                        "FULL = session start / cross-agent handoff. "
                        "DELTA = normal iterative turns (default). "
                        "SIGNAL_ONLY = sub-agent internal hops."
                    ),
                },
                "risk_tier": {
                    "type": "string",
                    "enum": ["low", "medium", "high", "critical"],
                    "default": "medium",
                },
                "prior_state": {
                    "type": "string",
                    "description": "Compressed one-line prior context (omit on first turn)",
                },
                "platform": {
                    "type": "string",
                    "enum": ["mcp", "chatgpt_apps", "api", "stdio", "agi_reply"],
                    "default": "agi_reply",
                    "description": "Output formatter platform. Use agi_reply for protocol envelope.",
                },
                "to": {
                    "type": "string",
                    "description": "Primary recipient name or agent_id for the reply header",
                },
                "cc": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Secondary recipients (agents, vault refs)",
                },
                "dry_run": {
                    "type": "boolean",
                    "default": False,
                    "description": "True = plan pipeline without executing stages",
                },
            },
        },
        outputs={
            "human": "AgiReplyEnvelopeHuman — see arifos://reply/schemas",
            "agent": "AgiReplyEnvelopeAgent — see arifos://reply/schemas",
            "platform": "agi_reply (formatter dispatch in output_formatter.py)",
        },
    ),
    # ─────────────────────────────────────────────────────────────────────────
    # 12. arifos.vps_monitor — Secure Telemetry (New)
    # ─────────────────────────────────────────────────────────────────────────
    ToolSpec(
        name="arifos_vps_monitor",
        stage="111",
        purpose="Secure VPS telemetry",
        layer="MACHINE",
        description="Retrieve CPU, Memory, ZRAM, and Disk utilization. F12-hardened read-only access.",
        trinity="Δ",
        floors=("F4", "F12"),
        input_schema={
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["get_telemetry", "get_zram_status", "get_disk_usage"],
                    "default": "get_telemetry",
                    "description": "Telemetry action to perform",
                },
                "session_id": {"type": "string"},
                "dry_run": {"type": "boolean", "default": True},
            },
        },
        default_tier="low",
    ),
    # ─────────────────────────────────────────────────────────────────────────
    # 13. arifos.fetch — Governed Web Fetch (F9 Anti-Hantu)
    # ─────────────────────────────────────────────────────────────────────────
    ToolSpec(
        name="arifos_fetch",
        stage="111",
        purpose="Governed URL fetch + F9 Anti-Hantu filtering",
        layer="MACHINE",
        description=(
            "Retrieve raw content from a URL via mcp_fetch substrate. "
            "Applies F9 Anti-Hantu constitutional filtering to redact spiritual cosplay "
            "or hallucinatory consciousness claims in the source content."
        ),
        trinity="Δ",
        floors=("F2", "F9", "F11"),
        visibility="public",
        input_schema={
            "type": "object",
            "required": ["url"],
            "properties": {
                "url": {"type": "string", "description": "URL to fetch"},
                "max_length": {
                    "type": "integer",
                    "default": 10000,
                    "description": "Max characters to retrieve",
                },
                "session_id": {"type": "string"},
            },
        },
        default_tier="medium",
    ),
    # ─────────────────────────────────────────────────────────────────────────
    # 14. arifos.git_status — Governed Repository State (Substrate)
    # ─────────────────────────────────────────────────────────────────────────
    ToolSpec(
        name="arifos_git_status",
        stage="911",
        purpose="Read governed repository state",
        layer="EXECUTION",
        description="Check git status, diffs, and log with constitutional path whitelisting.",
        trinity="Ψ",
        floors=("F11",),
        input_schema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "default": "./"},
            },
        },
        default_tier="small",
    ),
    # ─────────────────────────────────────────────────────────────────────────
    # 15. arifos.forge_bridge — AF-FORGE Governance Bridge
    # ─────────────────────────────────────────────────────────────────────────
    ToolSpec(
        name="arifos_forge_bridge",
        stage="FORGE_010",
        purpose="Route task through AF-FORGE TypeScript constitutional engine (F3/F6/F9 gates)",
        layer="GOVERNANCE",
        description=(
            "Proxy task to AF-FORGE HTTP bridge (port 7071). "
            "AF-FORGE runs F3 InputClarity → F6 HarmDignity → F9 Injection checks before any LLM call. "
            "Returns SABAR (F3 blocked), VOID (F6/F9 blocked), or governed agent output. "
            "Use for tasks requiring TypeScript-side constitutional validation or AF-FORGE agent execution."
        ),
        trinity="Δ/Ψ",
        floors=("F3", "F6", "F9", "F13"),
        input_schema={
            "type": "object",
            "required": ["task"],
            "properties": {
                "task": {"type": "string", "minLength": 3, "maxLength": 10000, "description": "Task to evaluate or execute"},
                "mode": {
                    "type": "string",
                    "enum": ["check_governance", "run", "health"],
                    "default": "check_governance",
                    "description": "check_governance=F3/F6/F9 verdict only | run=full agent execution | health=floor status",
                },
                "agent_mode": {
                    "type": "string",
                    "enum": ["internal_mode", "external_safe_mode"],
                    "default": "external_safe_mode",
                },
            },
        },
        outputs={
            "check_governance": {
                "overall": "PASS | BLOCK",
                "blocked": "boolean",
                "floors": {
                    "F3_InputClarity": {"verdict": "SABAR | PASS"},
                    "F6_HarmDignity": {"verdict": "VOID | PASS"},
                    "F9_Injection": {"verdict": "VOID | PASS"},
                },
            },
            "run": {
                "finalText": "string",
                "turnCount": "integer",
                "blocked": "boolean",
            },
            "health": {
                "status": "healthy",
                "constitutional_floors": {"implemented": "integer", "total": 13, "coverage": "string"},
            },
        },
        visibility="internal",
        default_tier="medium",
        readonly=True,
        read_only_hint=True,
        destructive_hint=False,
        open_world_hint=True,
        idempotent_hint=True,
    ),
    # ─────────────────────────────────────────────────────────────────────────
    # 16. arifos.git_commit — Governed Repository Mutation (Substrate)
    # ─────────────────────────────────────────────────────────────────────────
    ToolSpec(
        name="arifos_git_commit",
        stage="999",
        purpose="Mutate governed repository state (F13 Required)",
        layer="EXECUTION",
        description=(
            "Add and commit changes to the repository. REQUIRES F13 human ratification. "
            "Enforces F11 audit logging of all substrate mutations."
        ),
        trinity="Ψ",
        floors=("F11", "F13"),
        input_schema={
            "type": "object",
            "required": ["message"],
            "properties": {
                "message": {"type": "string", "minLength": 10},
                "files": {"type": "array", "items": {"type": "string"}},
            },
        },
        default_tier="medium",
        readonly=False,
    ),
)

# ═══════════════════════════════════════════════════════════════════════════════
# V2 TOOL NAME MAPPING (for backward compatibility during transition)
# ═══════════════════════════════════════════════════════════════════════════════

TOOL_NAMES = frozenset(t.name for t in TOOLS)
TOOL_COUNT = len(TOOLS)

# Map old canonical names to v2 names (for migration)
LEGACY_NAME_MAP: dict[str, str] = {
    "init_anchor": "arifos_init",
    "physics_reality": "arifos_sense",
    "agi_mind": "arifos_mind",
    "arifOS_kernel": "arifos_kernel",
    "asi_heart": "arifos_heart",
    "math_estimator": "arifos_ops",
    "apex_soul": "arifos_judge",
    "engineering_memory": "arifos_memory",
    "vault_ledger": "arifos_vault",
    "architect_registry": "arifos_init",  # Registry folded into init
    "code_engine": "arifos_vault",  # Execution folded into vault logging
}


def normalize_tool_name(name: str) -> str:
    """Normalize tool name (dots to underscores) for arifOS v2.

    Example: 'arifos.init' -> 'arifos_init'
    """
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


# ═══════════════════════════════════════════════════════════════════════════════
# BACKWARD COMPAT ALIASES (for code that still uses old names)
# ═══════════════════════════════════════════════════════════════════════════════
ToolSpecV2 = ToolSpec
V2_TOOLS = TOOLS
V2_TOOL_NAMES = TOOL_NAMES
V2_TOOL_COUNT = TOOL_COUNT
V1_TO_V2_MAP = LEGACY_NAME_MAP
get_v2_tool_spec = get_tool_spec
v2_tool_names = tool_names

# public_registry.py compat
PUBLIC_TOOL_SPECS = TOOLS
PUBLIC_RESOURCE_SPECS: tuple[()] = ()
PUBLIC_PROMPT_SPECS = ()

# MegaTool Compat Aliases
MEGA_TOOLS = TOOLS
MegaToolName = str


__all__ = [
    "ToolSpec",
    "TOOLS",
    "TOOL_NAMES",
    "TOOL_COUNT",
    "LEGACY_NAME_MAP",
    "get_tool_spec",
    "tool_names",
    # compat aliases
    "ToolSpecV2",
    "V2_TOOLS",
    "V2_TOOL_NAMES",
    "V2_TOOL_COUNT",
    "V1_TO_V2_MAP",
    "get_v2_tool_spec",
    "v2_tool_names",
    "PUBLIC_TOOL_SPECS",
    "PUBLIC_RESOURCE_SPECS",
    "PUBLIC_PROMPT_SPECS",
    "MEGA_TOOLS",
    "MegaToolName",
]
