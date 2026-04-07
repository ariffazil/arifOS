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
    name: str  # arifos.{verb} format
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


# ═══════════════════════════════════════════════════════════════════════════════
# MCP v2: 9 SOVEREIGN CORE TOOLS
# ═══════════════════════════════════════════════════════════════════════════════

TOOLS: tuple[ToolSpec, ...] = (
    # ─────────────────────────────────────────────────────────────────────────
    # 1. arifos.init — Session Initialization (was 000_INIT, init_anchor)
    # ─────────────────────────────────────────────────────────────────────────
    ToolSpec(
        name="arifos.init",
        stage="000",
        purpose="Start governed session",
        layer="GOVERNANCE",
        description="Initialize constitutional session with identity binding and telemetry seed.",
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
                "risk_tier": {"type": "string", "enum": ["low", "medium", "high", "critical"], "default": "medium"},
            },
        },
        default_tier="small",
    ),

    # ─────────────────────────────────────────────────────────────────────────
    # 2. arifos.sense — Constitutional Reality Sensing (was 111_SENSE, physics_reality)
    # ─────────────────────────────────────────────────────────────────────────
    ToolSpec(
        name="arifos.sense",
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
                "query": {"type": "string", "description": "Query to classify and ground in reality"},
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
        name="arifos.mind",
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
                "mode": {"type": "string", "enum": ["reason", "reflect", "forge"], "default": "reason"},
                "session_id": {"type": "string"},
            },
        },
    ),

    # ─────────────────────────────────────────────────────────────────────────
    # 4. arifos.route — Execution Lane Selection (was 444_ROUT, arifOS_kernel)
    # ─────────────────────────────────────────────────────────────────────────
    ToolSpec(
        name="arifos.route",
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
        name="arifos.heart",
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
        name="arifos.ops",
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
                "mode": {"type": "string", "enum": ["cost", "health", "vitals", "entropy"], "default": "cost"},
                "session_id": {"type": "string"},
            },
        },
    ),

    # ─────────────────────────────────────────────────────────────────────────
    # 7. arifos.judge — Constitutional Verdict (was 888_JUDGE, apex_soul)
    # ─────────────────────────────────────────────────────────────────────────
    ToolSpec(
        name="arifos.judge",
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
                "risk_tier": {"type": "string", "enum": ["low", "medium", "high", "critical"], "default": "medium"},
                "telemetry": {"type": "object", "description": "Optional telemetry data"},
                "session_id": {"type": "string"},
            },
        },
    ),

    # ─────────────────────────────────────────────────────────────────────────
    # 8. arifos.memory — Governed Recall (was 555_MEMORY, engineering_memory)
    # ─────────────────────────────────────────────────────────────────────────
    ToolSpec(
        name="arifos.memory",
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
                "mode": {"type": "string", "enum": ["vector_query", "vector_store", "engineer", "query"], "default": "vector_query"},
                "session_id": {"type": "string"},
            },
        },
    ),

    # ─────────────────────────────────────────────────────────────────────────
    # 9. arifos.vault — Immutable Logging (was 999_VAULT, vault_ledger)
    # ─────────────────────────────────────────────────────────────────────────
    ToolSpec(
        name="arifos.vault",
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
                "verdict": {"type": "string", "enum": ["SEAL", "PARTIAL", "VOID", "HOLD"], "description": "Verdict to log"},
                "evidence": {"type": "string", "description": "Evidence summary"},
                "session_id": {"type": "string"},
            },
        },
    ),

    # ─────────────────────────────────────────────────────────────────────────
    # 10. arifos.forge — Delegated Execution Bridge (was shell_forge)
    # ─────────────────────────────────────────────────────────────────────────
    ToolSpec(
        name="arifos.forge",
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
                "action": {"type": "string", "enum": ["shell", "api_call", "contract", "compute", "container", "vm"], "description": "Execution type"},
                "payload": {"type": "object", "description": "Action-specific parameters"},
                "session_id": {"type": "string"},
                "judge_verdict": {"type": "string", "enum": ["SEAL"], "description": "Must be SEAL from arifos.judge"},
                "judge_g_star": {"type": "number", "minimum": 0.0, "maximum": 1.0, "description": "G★ score at time of verdict"},
                "constraints": {"type": "object", "description": "Resource limits (cpu, memory, timeout)"},
                "dry_run": {"type": "boolean", "default": True, "description": "Generate manifest without dispatch"},
                "af_forge_endpoint": {"type": "string", "description": "Target substrate endpoint"},
            },
        },
    ),

    # ─────────────────────────────────────────────────────────────────────────
    # 11. arifos.vps_monitor — Secure Telemetry (New)
    # ─────────────────────────────────────────────────────────────────────────
    ToolSpec(
        name="arifos.vps_monitor",
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
                    "description": "Telemetry action to perform"
                },
                "session_id": {"type": "string"},
                "dry_run": {"type": "boolean", "default": True},
            },
        },
        default_tier="low",
    ),
)

# ═══════════════════════════════════════════════════════════════════════════════
# V2 TOOL NAME MAPPING (for backward compatibility during transition)
# ═══════════════════════════════════════════════════════════════════════════════

TOOL_NAMES = frozenset(t.name for t in TOOLS)
TOOL_COUNT = len(TOOLS)

# Map old canonical names to v2 names (for migration)
LEGACY_NAME_MAP: dict[str, str] = {
    "init_anchor": "arifos.init",
    "physics_reality": "arifos.sense",
    "agi_mind": "arifos.mind",
    "arifOS_kernel": "arifos.route",
    "asi_heart": "arifos.heart",
    "math_estimator": "arifos.ops",
    "apex_soul": "arifos.judge",
    "engineering_memory": "arifos.memory",
    "vault_ledger": "arifos.vault",
    "architect_registry": "arifos.init",  # Registry folded into init
    "code_engine": "arifos.vault",  # Execution folded into vault logging
}


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
PUBLIC_PROMPT_SPECS: tuple[()] = ()


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
]
