from dataclasses import dataclass, field
from typing import Any


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
    public: bool = False  # Default to internal for safety
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
    is_template: bool = False


@dataclass(frozen=True)
class PromptSpec:
    name: str
    description: str
    arguments: list[dict[str, Any]] = None


def _build_mega_schema(
    tool_name: str,
    modes: list[str],
    payload_properties: dict[str, Any],
    required_payload: list[str] = None,
) -> dict[str, Any]:
    """Unified request envelope for arifOS v2."""
    return {
        "type": "object",
        "required": ["mode", "payload"],
        "properties": {
            "mode": {"type": "string", "enum": modes},
            "payload": {
                "type": "object",
                "required": required_payload or [],
                "properties": payload_properties,
            },
            "session_id": {"type": "string", "minLength": 8},
            "risk_tier": {"type": "string", "enum": ["low", "medium", "high", "critical"], "default": "medium"},
            "dry_run": {"type": "boolean", "default": True},
        },
    }


# ─── ⚖️ arifOS MCP v2 Sovereign Core (Standard Compliant) ─────────────────────

PUBLIC_TOOL_SPECS: tuple[ToolSpec, ...] = (
    ToolSpec(
        name="arifos.init",
        public=True,
        stage="000_INIT",
        role="Init Anchor",
        layer="GOVERNANCE",
        description="Start a governed arifOS session and bind the initial telemetry seed.",
        trinity="PSI Ψ",
        floors=("F11", "F12", "F13"),
        input_schema=_build_mega_schema(
            "arifos.init",
            ["init", "revoke", "status"],
            {
                "actor_id": {"type": "string"},
                "intent": {"type": "string"},
            },
        ),
    ),
    ToolSpec(
        name="arifos.route",
        public=True,
        stage="444_ROUTER",
        role="arifOS Kernel",
        layer="GOVERNANCE",
        description="Execution lane selection and metabolic routing.",
        trinity="DELTA/PSI",
        floors=("F4", "F11"),
        input_schema=_build_mega_schema(
            "arifos.route",
            ["kernel", "status"],
            {"query": {"type": "string"}},
        ),
    ),
    ToolSpec(
        name="arifos.judge",
        public=True,
        stage="888_JUDGE",
        role="Apex Soul",
        layer="GOVERNANCE",
        description="Constitutional verdict engine and final authority enforcement.",
        trinity="PSI Ψ",
        floors=("F3", "F12", "F13"),
        input_schema=_build_mega_schema(
            "arifos.judge",
            ["judge", "validate"],
            {
                "candidate_action": {"type": "string"},
                "telemetry": {"type": "object"},
            },
        ),
    ),
    # ─── Internal Subsystems (Hidden from Public MCP Surface) ───
    ToolSpec(
        name="arifos.sense",
        public=False,
        stage="111_SENSE",
        role="Physics Reality",
        layer="MACHINE",
        description="Reality grounding, time, and evidence verification.",
        trinity="DELTA Δ",
        floors=("F2", "F3"),
        input_schema=_build_mega_schema("arifos.sense", ["search", "time"], {"query": {"type": "string"}}),
    ),
    ToolSpec(
        name="arifos.mind",
        public=False,
        stage="333_MIND",
        role="AGI Mind",
        layer="INTELLIGENCE",
        description="Structured first-principles reasoning and synthesis.",
        trinity="DELTA Δ",
        floors=("F2", "F8"),
        input_schema=_build_mega_schema("arifos.mind", ["reason"], {"query": {"type": "string"}}),
    ),
    ToolSpec(
        name="arifos.heart",
        public=False,
        stage="666_HEART",
        role="ASI Heart",
        layer="INTELLIGENCE",
        description="Safety, dignity, and adversarial critique.",
        trinity="OMEGA Ω",
        floors=("F5", "F6", "F9"),
        input_schema=_build_mega_schema("arifos.heart", ["critique"], {"content": {"type": "string"}}),
    ),
    ToolSpec(
        name="arifos.ops",
        public=False,
        stage="444_ROUTER",
        role="Math Estimator",
        layer="MACHINE",
        description="Calculate operation costs and thermodynamic vitals.",
        trinity="DELTA Δ",
        floors=("F4", "F5"),
        input_schema=_build_mega_schema("arifos.ops", ["cost"], {"action": {"type": "string"}}),
    ),
    ToolSpec(
        name="arifos.memory",
        public=False,
        stage="555_MEMORY",
        role="Engineering Memory",
        layer="INTELLIGENCE",
        description="Governed memory retrieval (Requires Session).",
        trinity="OMEGA Ω",
        floors=("F10", "F11"),
        input_schema=_build_mega_schema("arifos.memory", ["query"], {"query": {"type": "string"}}),
    ),
    ToolSpec(
        name="arifos.vault",
        public=False,
        stage="999_VAULT",
        role="Vault Ledger",
        layer="GOVERNANCE",
        description="Immutable verdict logging (Requires Session).",
        trinity="PSI Ψ",
        floors=("F1", "F13"),
        input_schema=_build_mega_schema("arifos.vault", ["seal"], {"verdict": {"type": "string"}}),
    ),
    # ═══════════════════════════════════════════════════════════════════════════
    # EXECUTION BRIDGE (LAYER 3 — Hardened)
    # ═══════════════════════════════════════════════════════════════════════════
    ToolSpec(
        name="arifos.forge",
        public=True,  # Public but requires HMAC-signed envelope
        stage="FORGE",
        role="Execution Bridge",
        layer="EXECUTION",
        description="Hardened execution bridge — ONLY path for state mutation. Requires HMAC-signed envelope + SEAL verdict.",
        trinity="DELTA Δ",
        floors=("F1", "F11", "F13"),
        input_schema=_build_mega_schema(
            "arifos.forge",
            ["execute"],
            {
                "execution_envelope": {
                    "type": "object",
                    "properties": {
                        "query_hash": {"type": "string"},
                        "verdict": {"type": "string", "enum": ["SEAL", "HOLD", "VOID"]},
                        "actor_id": {"type": "string"},
                        "timestamp": {"type": "string"},
                        "signature": {"type": "string"},
                    },
                    "required": ["query_hash", "verdict", "actor_id", "timestamp", "signature"],
                },
                "action_type": {"type": "string", "enum": ["spawn", "write", "send", "call"]},
                "target": {"type": "string"},
                "constraints": {"type": "object"},
            },
            required=["execution_envelope"],
        ),
    ),
)

PUBLIC_RESOURCE_SPECS: tuple[ResourceSpec, ...] = (
    ResourceSpec(uri="arifos://governance/floors", name="arifOS Floors", description="Canonical F1-F13 thresholds."),
    ResourceSpec(uri="arifos://status/vitals", name="arifOS Vitals", description="System health & telemetry."),
)

PUBLIC_PROMPT_SPECS: tuple[PromptSpec, ...] = ()
