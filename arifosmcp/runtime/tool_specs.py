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
    "init_anchor",
    "arifOS_kernel",
    "apex_soul",
    "vault_ledger",
    "agi_mind",
    "asi_heart",
    "engineering_memory",
    "physics_reality",
    "math_estimator",
    "code_engine",
    "architect_registry",
]

MEGA_TOOLS: tuple[str, ...] = (
    "init_anchor",
    "arifOS_kernel",
    "apex_soul",
    "vault_ledger",
    "agi_mind",
    "asi_heart",
    "engineering_memory",
    "physics_reality",
    "math_estimator",
    "code_engine",
    "architect_registry",
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
        name="init_anchor",
        stage="000_INIT",
        role="Constitutional Airlock",
        layer="GOVERNANCE",
        description=(
            "Initialize your constitutional session — the entry point to arifOS. "
            "Establishes identity, authority level, and governance context. "
            "Use 'init' to start, 'status' to check session health, 'state' for forensic audit. "
            "Required before using gated tools like kernel, memory, or vault."
        ),
        trinity="PSI Ψ",
        floors=("F11", "F12", "F13"),
        input_schema=_build_mega_schema(
            "init_anchor",
            ["init", "revoke", "refresh", "state", "status"],
            {
                "actor_id": {"type": "string", "minLength": 2, "maxLength": 64},
                "model_soul": {
                    "type": "object",
                    "description": "Deep identity and behavioral contract (V2).",
                    "properties": {
                        "base_identity": {
                            "type": "object",
                            "properties": {
                                "provider": {"type": "string"},
                                "model_family": {"type": "string"},
                                "model_variant": {"type": "string"},
                                "runtime_class": {"type": "string"},
                            },
                        },
                        "runtime_state": {
                            "type": "object",
                            "properties": {
                                "tooling": {"type": "array", "items": {"type": "string"}},
                                "web_access": {"type": "boolean"},
                                "memory_mode": {"type": "string"},
                            },
                        },
                        "capability_map": {
                            "type": "object",
                            "additionalProperties": {"type": "boolean"},
                        },
                        "boundary_map": {
                            "type": "object",
                            "properties": {
                                "identity_claim_policy": {"type": "string"},
                                "tool_claim_policy": {"type": "string"},
                            },
                        },
                        "constitution": {
                            "type": "object",
                            "properties": {
                                "truth_policy": {"type": "string"},
                                "humility_policy": {"type": "string"},
                                "anti_hantu_policy": {"type": "string"},
                            },
                        },
                    },
                },
                "intent": {
                    "oneOf": [
                        {
                            "type": "string",
                            "minLength": 1,
                            "maxLength": 20000,
                            "description": "Legacy string format (auto-normalized to structured object)",
                        },
                        {
                            "type": "object",
                            "properties": {
                                "query": {"type": "string", "minLength": 1, "maxLength": 20000},
                                "task_type": {
                                    "type": "string",
                                    "maxLength": 64,
                                    "enum": [
                                        "general",
                                        "ask",
                                        "audit",
                                        "design",
                                        "decide",
                                        "analyze",
                                        "execute",
                                    ],
                                    "default": "general",
                                },
                                "domain": {"type": "string", "maxLength": 64},
                                "desired_output": {
                                    "type": "string",
                                    "maxLength": 64,
                                    "enum": [
                                        "text",
                                        "json",
                                        "table",
                                        "code",
                                        "report",
                                        "decision",
                                        "mixed",
                                    ],
                                },
                                "reversibility": {
                                    "type": "string",
                                    "enum": ["reversible", "irreversible", "auditable"],
                                    "default": "auditable",
                                },
                            },
                            "required": ["query"],
                            "description": "Structured intent object with query, task_type, domain, desired_output, reversibility",
                        },
                    ],
                    "description": "User intent - accepts string (legacy) or structured object (preferred for governance)",
                },
                "declared_name": {"type": "string", "maxLength": 64},
                "session_id": {"type": "string", "minLength": 8, "maxLength": 128},
                "reason": {"type": "string", "maxLength": 1000},
                "human_approval": {
                    "type": "boolean",
                    "default": False,
                    "description": "Whether human has pre-approved this action (F13 Sovereign override)",
                },
            },
        ),
        default_budget_tier="small",
    ),
    ToolSpec(
        name="arifOS_kernel",
        stage="444_ROUTER",
        role="Stage Conductor",
        layer="GOVERNANCE",
        description=(
            "The main conductor for complex queries — routes through constitutional stages 000-999. "
            "Use for multi-step reasoning, orchestration, and metabolic processing. "
            "Modes: 'kernel' (full reasoning), 'status' (system vitals)."
        ),
        trinity="DELTA/PSI",
        floors=("F4", "F11"),
        input_schema=_build_mega_schema(
            "arifOS_kernel",
            ["kernel", "status"],
            {
                "query": {"type": "string", "minLength": 1, "maxLength": 40000},
                "intent": {
                    "oneOf": [
                        {"type": "string"},
                        {
                            "type": "object",
                            "properties": {"query": {"type": "string"}},
                            "required": ["query"],
                        },
                    ],
                    "description": "Structured intent for governed reasoning.",
                },
                "context": {"type": "string", "maxLength": 100000},
                "max_steps": {"type": "integer", "minimum": 1, "maximum": 50, "default": 13},
                "session_id": {"type": "string"},
                "detail": {"type": "string", "enum": ["brief", "full"], "default": "full"},
            },
        ),
    ),
    ToolSpec(
        name="apex_judge",
        stage="888_JUDGE",
        role="Constitutional Verdict",
        layer="GOVERNANCE",
        description=(
            "Final constitutional authority — judges outputs, validates safety, triggers holds. "
            "Use for: verdict decisions ('judge'), rule audit ('rules'), safety validation ('validate'), "
            "escalation holds ('hold'), injection scanning ('armor'), governance probes ('probe')."
        ),
        trinity="PSI Ψ",
        floors=("F3", "F12", "F13"),
        input_schema=_build_mega_schema(
            "apex_judge",
            ["judge", "rules", "validate", "hold", "armor", "notify", "probe"],
            {
                "candidate": {"type": "string"},
                "hold_id": {"type": "string"},
                "message": {"type": "string"},
                "session_id": {"type": "string"},
                "target_floor": {
                    "type": "string",
                    "description": "Specific floor to probe (e.g. 'F12').",
                },
            },
        ),
    ),
    ToolSpec(
        name="vault_ledger",
        stage="999_VAULT",
        role="Immutable Memory",
        layer="GOVERNANCE",
        description=(
            "Immutable decision ledger — cryptographically seals decisions with BLS signatures. "
            "Use for: recording final verdicts ('seal'), verifying ledger integrity ('verify'). "
            "Requires authenticated session. Decisions are permanently attested with juror quorum."
        ),
        trinity="PSI Ψ",
        floors=("F1", "F13"),
        input_schema=_build_mega_schema(
            "vault_ledger",
            ["seal", "verify"],
            {
                "verdict": {"type": "string"},
                "evidence": {"type": "string"},
                "full_scan": {"type": "boolean", "default": True},
                "session_id": {"type": "string"},
            },
        ),
    ),
    # ─── 🧠 INTELLIGENCE LAYER (I-1 to I-3) ───
    ToolSpec(
        name="agi_mind",
        stage="333_MIND",
        role="Logic & Synthesis",
        layer="INTELLIGENCE",
        description=(
            "Core reasoning engine — first-principles thinking and synthesis. "
            "Use for: structured reasoning ('reason'), self-reflection ('reflect'), "
            "orchestrated creation ('forge'). Analyzes via constitutional floors F2-F8."
        ),
        trinity="DELTA Δ",
        floors=("F2", "F4", "F7", "F8"),
        input_schema=_build_mega_schema(
            "agi_mind",
            ["reason", "reflect", "forge"],
            {
                "query": {"type": "string"},
                "topic": {"type": "string"},
                "session_id": {"type": "string"},
            },
            required_payload=["query"],
        ),
    ),
    ToolSpec(
        name="asi_heart",
        stage="666_HEART",
        role="Ethics & Simulation",
        layer="INTELLIGENCE",
        description=(
            "Safety and ethics critique — adversarial analysis and consequence simulation. "
            "Use for: critiquing drafts for risks ('critique'), simulating scenario outcomes ('simulate'). "
            "Acts as red-team conscience with F5-F9 floor enforcement."
        ),
        trinity="OMEGA Ω",
        floors=("F5", "F6", "F9"),
        input_schema=_build_mega_schema(
            "asi_heart",
            ["critique", "simulate"],
            {"content": {"type": "string"}, "session_id": {"type": "string"}},
            required_payload=["content"],
        ),
    ),
    ToolSpec(
        name="engineering_memory",
        stage="555_MEMORY",
        role="Technical Execution",
        layer="INTELLIGENCE",
        description=(
            "Vector memory and engineering — semantic search, storage, and code generation. "
            "Use for: searching memory ('vector_query'), storing knowledge ('vector_store'), "
            "engineering tasks ('engineer'), local LLM generation ('generate'). "
            "Qdrant-backed with F10/F2 verification."
        ),
        trinity="OMEGA Ω",
        floors=("F10", "F11", "F2"),
        input_schema=_build_mega_schema(
            "engineering_memory",
            ["engineer", "vector_query", "vector_store", "vector_forget", "generate", "query"],
            {
                "task": {"type": "string"},
                "query": {"type": "string"},
                "prompt": {"type": "string"},
                "content": {"type": "string"},
                "session_id": {"type": "string"},
            },
        ),
    ),
    # ─── ⚙️ MACHINE LAYER (M-1 to M-4) ───
    ToolSpec(
        name="physics_reality",
        stage="111_SENSE",
        role="Environmental Grounding",
        layer="MACHINE",
        description="Reality grounding — web search, fact verification, temporal intelligence. "
            "Use for: web search ('search'), content ingestion ('ingest'), "
            "navigation compass ('compass'), domain mapping ('atlas'), current time ('time'). "
            "Grounds AI outputs in observable reality via F2/F3/F10 floors.",
        trinity="DELTA Δ",
        floors=("F2", "F3", "F10"),
        input_schema=_build_mega_schema(
            "physics_reality",
            ["search", "ingest", "compass", "atlas", "time"],
            {
                "input": {"type": "string"},
                "operation": {"type": "string"},
                "session_id": {"type": "string"},
                "top_k": {"type": "integer", "default": 5},
            },
        ),
    ),
    ToolSpec(
        name="math_estimator",
        stage="444_ROUTER",
        role="Thermodynamic Vitals",
        layer="MACHINE",
        description=(
            "System health metrics — thermodynamic vitals, cost estimation, entropy monitoring. "
            "Use for: operation cost estimation ('cost'), health checks ('health'), "
            "real-time vitals ('vitals'), entropy/drift analysis ('entropy')."
        ),
        trinity="DELTA Δ",
        floors=("F4", "F5"),
        input_schema=_build_mega_schema(
            "math_estimator",
            ["cost", "health", "vitals", "entropy"],
            {"action": {"type": "string"}, "session_id": {"type": "string"}},
        ),
    ),
    ToolSpec(
        name="code_engine",
        stage="M-3_EXEC",
        role="Computational Execution",
        layer="MACHINE",
        description=(
            "System-level execution — file inspection, process monitoring, network status. "
            "Use for: filesystem inspection ('fs'), process listing ('process'), "
            "network status ('net'), log tailing ('tail'), trace replay ('replay'). "
            "⚠️ Sovereign VPS only — high-risk ops return 888_HOLD redirect."
        ),
        trinity="ALL",
        floors=("F1",),
        input_schema=_build_mega_schema(
            "code_engine",
            ["fs", "process", "net", "tail", "replay"],
            {
                "path": {"type": "string", "default": "."},
                "limit": {"type": "integer", "default": 50},
                "session_id": {"type": "string"},
            },
        ),
    ),
    ToolSpec(
        name="architect_registry",
        stage="M-4_ARCH",
        role="System Definition",
        layer="MACHINE",
        description="Discovery and registry — list tools, read specs, model catalog, identity verification. "
            "Use for: discovering available tools ('list'), reading tool contracts ('read'), "
            "model registry lookup ('model_catalog'), identity binding ('verify_identity').",
        trinity="DELTA Δ",
        floors=("F10", "F11"),
        input_schema=_build_mega_schema(
            "architect_registry",
            ["register", "list", "read", "context", "model_catalog", "model_profile", "provider_soul", "verify_identity"],
            {
                "uri": {"type": "string"},
                "session_id": {"type": "string"},
                "model_key": {"type": "string", "description": "Provider/family/variant path for model_profile mode"},
                "soul_key": {"type": "string", "description": "Provider soul key for provider_soul mode"},
                "claimed_identity": {"type": "string", "description": "Model identity claim for verify_identity mode"},
                "claimed_provider": {"type": "string", "description": "Optional provider hint for verify_identity mode"},
            },
        ),
    ),
    ToolSpec(
        name="compat_probe",
        stage="M-5_COMPAT",
        role="Interoperability Audit",
        layer="MACHINE",
        description="Verify session portability and enum compatibility between layers. Modes: 'audit', 'probe', 'ping'.",
        trinity="ALL",
        floors=("F11", "F4"),
        input_schema=_build_mega_schema(
            "compat_probe",
            ["audit", "probe", "ping"],
            {"session_id": {"type": "string"}},
        ),
    ),
)

PUBLIC_RESOURCE_SPECS: tuple[ResourceSpec, ...] = (
    ResourceSpec(
        uri="about://arifos",
        name="arifOS Overview",
        description="What is arifOS? Constitutional AI governance, 13 floors, and the 000-999 metabolic pipe.",
    ),
    ResourceSpec(
        uri="canon://floors",
        name="arifOS Floors",
        description="The 13 Constitutional Floors (F1-F13) — thresholds for truth, safety, humility, and sovereignty.",
    ),
    ResourceSpec(
        uri="canon://contracts",
        name="arifOS Tool Spec",
        description="Detailed contracts for all 11 Mega-Tools — inputs, outputs, floors enforced.",
    ),
    ResourceSpec(
        uri="canon://states",
        name="arifOS States",
        description="Session state ladder: anonymous → claimed → anchored → verified → scoped → approved.",
    ),
    ResourceSpec(
        uri="arifos://governance/floors",
        name="arifOS Governance",
        description="Immutable thresholds and legal doctrine for the 13 Constitutional Floors.",
    ),
    ResourceSpec(
        uri="arifos://status/vitals",
        name="arifOS Vitals",
        description="Real-time system health: thermodynamic metrics, G-score, entropy, metabolic status.",
    ),
    ResourceSpec(
        uri="arifos://bootstrap/guide",
        name="arifOS Bootstrap",
        description="Getting started guide — startup sequence, first session, tool discovery path.",
    ),
    ResourceSpec(
        uri="arifos://agents/skills",
        name="arifOS Skills",
        description="Consolidated guide for AI agents — constitutional behaviors, skills, best practices.",
    ),
    ResourceSpec(
        uri="arifos://caller/state",
        name="arifOS Session Vitals",
        description="Your current session state — identity level, allowed tools, blocked operations.",
    ),
    ResourceSpec(
        uri="arifos://sessions/{session_id}/vitals",
        name="Session Vitals",
        description="Dynamic vitals for a specific governed session.",
        is_template=True,
    ),
    ResourceSpec(
        uri="arifos://tools/{tool_name}/spec",
        name="Tool Specification",
        description="Dynamic contract and schema for a specific arifOS tool.",
        is_template=True,
    ),
    ResourceSpec(
        uri="arifos://floors/{floor_id}/doctrine",
        name="Floor Doctrine",
        description="Dynamic legal and physical doctrine for a specific floor.",
        is_template=True,
    ),
)

PUBLIC_PROMPT_SPECS: tuple[PromptSpec, ...] = (
    PromptSpec(name="init_anchor", description="Initialize anchor — constitutional session setup and identity binding."),
    PromptSpec(name="arifOS_kernel", description="ArifOS kernel — metabolic conductor prompt for complex orchestration."),
    PromptSpec(
        name="agi_mind", description="AGI mind — first-principles reasoning, synthesis, and reflection prompt."
    ),
    PromptSpec(
        name="asi_heart", description="ASI heart — ethical critique, safety simulation, adversarial analysis prompt."
    ),
    PromptSpec(name="apex_soul", description="Apex soul — sovereign judgment, verdict rendering, constitutional audit prompt."),
    PromptSpec(name="vault_ledger", description="Vault ledger — immutable decision recording and cryptographic sealing prompt."),
    PromptSpec(
        name="physics_reality", description="Physics reality — earth-witness grounding, fact-checking, temporal awareness prompt."
    ),
    PromptSpec(
        name="code_engine", description="Code engine — system execution, file inspection, process monitoring prompt."
    ),
    PromptSpec(
        name="engineering_memory", description="Engineering memory — vector search, knowledge storage, code generation prompt."
    ),
    PromptSpec(
        name="math_estimator", description="Math estimator — thermodynamic vitals, cost estimation, entropy analysis prompt."
    ),
)
