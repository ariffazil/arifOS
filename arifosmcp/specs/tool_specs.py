"""
arifOS MCP Tool Specifications
═══════════════════════════════════════════════════════════════════════════════

11 canonical executable tools.

Naming convention:
- name: functional verb (machine-stable)
- title: mythic name (human-facing)
- description: clear purpose and usage
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ToolSpec:
    """
    Clean tool specification following MCP protocol.
    
    Fields:
        name: Machine-stable functional name (verb)
        title: Human-facing mythic name
        description: Clear purpose and usage
        input_schema: JSON Schema for inputs
        stage: Constitutional stage (000_INIT, 444_ROUTER, etc.)
        trinity: PSI, DELTA, or OMEGA
        floors: Tuple of F1-F13 floors enforced
        read_only_hint: If True, tool doesn't mutate state
        open_world_hint: If True, tool accesses external systems
        auth_required: Minimum authority level needed
    """
    name: str
    title: str
    description: str
    input_schema: dict[str, Any]
    stage: str
    trinity: str
    floors: tuple[str, ...]
    read_only_hint: bool = False
    open_world_hint: bool = False
    auth_required: str = "anonymous"  # anonymous, anchored, verified, sovereign


def _build_input_schema(
    properties: dict[str, Any],
    required: list[str] | None = None
) -> dict[str, Any]:
    """Helper to build consistent input schemas."""
    return {
        "type": "object",
        "properties": {
            **properties,
            "session_id": {
                "type": "string",
                "description": "Session context (optional, uses current if not provided)"
            },
            "dry_run": {
                "type": "boolean",
                "default": True,
                "description": "If true, simulate without executing"
            }
        },
        "required": required or []
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 11 CANONICAL TOOLS
# ═══════════════════════════════════════════════════════════════════════════════

CANONICAL_TOOL_SPECS: tuple[ToolSpec, ...] = (
    # ═══ GOVERNANCE LAYER ═══
    
    ToolSpec(
        name="init_session_anchor",
        title="Init Anchor",
        description=(
            "Start a governed arifOS session. Establishes identity, "
            "binds telemetry seed, and returns session context. "
            "Required first step before using gated tools."
        ),
        input_schema=_build_input_schema(
            properties={
                "actor_id": {
                    "type": "string",
                    "description": "Identity claim (email, username, etc.)"
                },
                "intent": {
                    "type": "string",
                    "description": "Purpose of this session"
                },
                "session_class": {
                    "type": "string",
                    "enum": ["query", "execute", "elevated", "sovereign"],
                    "default": "execute",
                    "description": "Session permission level"
                },
                "human_approval": {
                    "type": "boolean",
                    "default": False,
                    "description": "Whether human has pre-approved"
                }
            }
        ),
        stage="000_INIT",
        trinity="PSI",
        floors=("F11", "F12", "F13"),
        read_only_hint=False,
        auth_required="anonymous",
    ),
    
    ToolSpec(
        name="get_tool_registry",
        title="Architect Registry",
        description=(
            "Discover available tools, their modes, and requirements. "
            "Returns the complete tool graph for the current session authority level."
        ),
        input_schema=_build_input_schema(
            properties={
                "mode": {
                    "type": "string",
                    "enum": ["list", "detail", "context"],
                    "default": "list",
                    "description": "Discovery mode"
                },
                "tool_name": {
                    "type": "string",
                    "description": "Specific tool to get details for (mode=detail)"
                }
            }
        ),
        stage="M-4_ARCH",
        trinity="DELTA",
        floors=("F10", "F11"),
        read_only_hint=True,
        auth_required="anonymous",
    ),
    
    # ═══ INTELLIGENCE LAYER ═══
    
    ToolSpec(
        name="sense_reality",
        title="Physics Reality",
        description=(
            "Ground reasoning in observable reality. "
            "Search web, ingest content, check temporal state, or navigate domains. "
            "Returns evidence with reality confidence scores."
        ),
        input_schema=_build_input_schema(
            properties={
                "query": {
                    "type": "string",
                    "description": "What to search, verify, or ingest"
                },
                "operation": {
                    "type": "string",
                    "enum": ["search", "ingest", "compass", "atlas", "time"],
                    "default": "search",
                    "description": "Operation type"
                },
                "top_k": {
                    "type": "integer",
                    "default": 5,
                    "minimum": 1,
                    "maximum": 20,
                    "description": "Number of results"
                }
            },
            required=["query"]
        ),
        stage="111_SENSE",
        trinity="DELTA",
        floors=("F2", "F3", "F10"),
        read_only_hint=True,
        open_world_hint=True,
        auth_required="anonymous",
    ),
    
    ToolSpec(
        name="reason_synthesis",
        title="AGI Mind",
        description=(
            "Multi-source synthesis and structured reasoning. "
            "Analyzes via constitutional floors F2-F8. "
            "Modes: reason (analysis), reflect (self-critique), forge (create)."
        ),
        input_schema=_build_input_schema(
            properties={
                "query": {
                    "type": "string",
                    "description": "Question or topic to reason about"
                },
                "mode": {
                    "type": "string",
                    "enum": ["reason", "reflect", "forge"],
                    "default": "reason",
                    "description": "Reasoning mode"
                },
                "context": {
                    "type": "string",
                    "description": "Additional context"
                }
            },
            required=["query"]
        ),
        stage="333_MIND",
        trinity="DELTA",
        floors=("F2", "F4", "F7", "F8"),
        read_only_hint=True,
        auth_required="anchored",
    ),
    
    ToolSpec(
        name="critique_safety",
        title="ASI Heart",
        description=(
            "Safety, dignity, and adversarial critique. "
            "Red-teams outputs for risks, biases, and harms. "
            "Modes: critique (analyze), simulate (scenario modeling)."
        ),
        input_schema=_build_input_schema(
            properties={
                "content": {
                    "type": "string",
                    "description": "Content to critique or scenario to simulate"
                },
                "mode": {
                    "type": "string",
                    "enum": ["critique", "simulate"],
                    "default": "critique",
                    "description": "Critique mode"
                }
            },
            required=["content"]
        ),
        stage="666_HEART",
        trinity="OMEGA",
        floors=("F5", "F6", "F9"),
        read_only_hint=True,
        auth_required="anchored",
    ),
    
    # ═══ ROUTING LAYER ═══
    
    ToolSpec(
        name="route_execution",
        title="arifOS Kernel",
        description=(
            "Route complex requests through constitutional pipeline (000-999). "
            "Metabolic conductor for multi-step execution. "
            "Respects 888_HOLD for high-risk operations."
        ),
        input_schema=_build_input_schema(
            properties={
                "query": {
                    "type": "string",
                    "description": "Request to route"
                },
                "intent_type": {
                    "type": "string",
                    "enum": ["ask", "audit", "design", "decide", "analyze", "execute"],
                    "default": "ask",
                    "description": "Request category"
                },
                "max_steps": {
                    "type": "integer",
                    "default": 13,
                    "minimum": 1,
                    "maximum": 50,
                    "description": "Maximum metabolic steps"
                },
                "allow_execution": {
                    "type": "boolean",
                    "default": False,
                    "description": "Allow actual execution"
                }
            },
            required=["query"]
        ),
        stage="444_ROUTER",
        trinity="DELTA/PSI",
        floors=("F4", "F11"),
        read_only_hint=False,
        auth_required="anchored",
    ),
    
    # ═══ MEMORY LAYER ═══
    
    ToolSpec(
        name="load_memory_context",
        title="Engineering Memory",
        description=(
            "Retrieve governed memory and engineering context. "
            "Vector search with constitutional verification. "
            "Requires anchored session."
        ),
        input_schema=_build_input_schema(
            properties={
                "query": {
                    "type": "string",
                    "description": "Search query"
                },
                "mode": {
                    "type": "string",
                    "enum": ["vector_query", "vector_store", "vector_forget", "engineer", "generate"],
                    "default": "vector_query",
                    "description": "Memory operation"
                },
                "content": {
                    "type": "string",
                    "description": "Content to store"
                },
                "k": {
                    "type": "integer",
                    "default": 5,
                    "description": "Items to retrieve"
                }
            }
        ),
        stage="555_MEMORY",
        trinity="OMEGA",
        floors=("F10", "F11", "F2"),
        read_only_hint=False,
        auth_required="anchored",
    ),
    
    # ═══ ESTIMATION LAYER ═══
    
    ToolSpec(
        name="estimate_ops",
        title="Math Estimator",
        description=(
            "Compute costs, capacity, timing, thermodynamic vitals. "
            "Returns G-score, entropy, capacity metrics."
        ),
        input_schema=_build_input_schema(
            properties={
                "action": {
                    "type": "string",
                    "description": "Operation to estimate"
                },
                "mode": {
                    "type": "string",
                    "enum": ["cost", "health", "vitals", "entropy"],
                    "default": "cost",
                    "description": "Estimation type"
                }
            }
        ),
        stage="777_OPS",
        trinity="DELTA",
        floors=("F4", "F5"),
        read_only_hint=True,
        auth_required="anonymous",
    ),
    
    # ═══ JUDGMENT LAYER ═══
    
    ToolSpec(
        name="judge_verdict",
        title="Apex Soul",
        description=(
            "Final constitutional verdict and hold logic. "
            "Evaluates actions against F1-F13 floors. "
            "Returns SEAL, PARTIAL, VOID, SABAR, or 888_HOLD."
        ),
        input_schema=_build_input_schema(
            properties={
                "candidate_action": {
                    "type": "string",
                    "description": "Action to evaluate"
                },
                "risk_tier": {
                    "type": "string",
                    "enum": ["low", "medium", "high", "critical"],
                    "default": "medium"
                },
                "mode": {
                    "type": "string",
                    "enum": ["judge", "rules", "validate", "hold", "armor", "probe"],
                    "default": "judge"
                }
            },
            required=["candidate_action"]
        ),
        stage="888_JUDGE",
        trinity="PSI",
        floors=("F3", "F12", "F13"),
        read_only_hint=True,
        auth_required="anchored",
    ),
    
    # ═══ VAULT LAYER ═══
    
    ToolSpec(
        name="record_vault_entry",
        title="Vault Ledger",
        description=(
            "Append immutable verdict to Vault999. "
            "Cryptographically sealed with BLS. "
            "Requires verified session. Phase 1: read-only for ChatGPT."
        ),
        input_schema=_build_input_schema(
            properties={
                "verdict": {
                    "type": "string",
                    "enum": ["SEAL", "PARTIAL", "VOID", "SABAR", "HOLD"]
                },
                "evidence": {
                    "type": "string",
                    "description": "Supporting evidence"
                },
                "mode": {
                    "type": "string",
                    "enum": ["seal", "verify"],
                    "default": "seal"
                }
            }
        ),
        stage="999_VAULT",
        trinity="PSI",
        floors=("F1", "F13"),
        read_only_hint=False,
        auth_required="verified",
    ),
    
    # ═══ EXECUTION LAYER ═══
    
    ToolSpec(
        name="execute_vps_task",
        title="Code Engine",
        description=(
            "System-level execution on sovereign VPS. "
            "Returns 888_HOLD redirect for unverified sessions. "
            "Actual execution only on A-FORGE VPS."
        ),
        input_schema=_build_input_schema(
            properties={
                "path": {
                    "type": "string",
                    "default": "."
                },
                "mode": {
                    "type": "string",
                    "enum": ["fs", "process", "net", "tail", "replay"],
                    "default": "fs"
                },
                "limit": {
                    "type": "integer",
                    "default": 50
                }
            }
        ),
        stage="M-3_EXEC",
        trinity="ALL",
        floors=("F1",),
        read_only_hint=True,
        auth_required="sovereign",
    ),
)


# ═══════════════════════════════════════════════════════════════════════════════
# LOOKUP UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

TOOL_NAMES: tuple[str, ...] = tuple(spec.name for spec in CANONICAL_TOOL_SPECS)


def get_tool_spec(name: str) -> ToolSpec | None:
    """Get tool spec by canonical name."""
    for spec in CANONICAL_TOOL_SPECS:
        if spec.name == name:
            return spec
    return None


def tool_spec_to_mcp_schema(spec: ToolSpec) -> dict[str, Any]:
    """Convert ToolSpec to MCP tools/list schema."""
    return {
        "name": spec.name,
        "title": spec.title,
        "description": spec.description,
        "inputSchema": spec.input_schema,
        "annotations": {
            "readOnlyHint": spec.read_only_hint,
            "openWorldHint": spec.open_world_hint,
        }
    }


__all__ = [
    "ToolSpec",
    "CANONICAL_TOOL_SPECS",
    "TOOL_NAMES",
    "get_tool_spec",
    "tool_spec_to_mcp_schema",
]
