"""
arifosmcp/runtime/tool_specs.py — arifOS MCP Canonical Tool Specifications
═══════════════════════════════════════════════════════════════════════════════

17 sovereign tools + 5 metabolic surfaces.
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


# ═══════════════════════════════════════════════════════════════════════════════
# HORIZON 33: CANONICAL TOOL SUITE
# ═══════════════════════════════════════════════════════════════════════════════

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
                    "description": "Session operation mode. probe=diagnostic compatibility check.",
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
                "query": {"type": "string"},
                "mode": {
                    "type": "string",
                    "enum": ["governed", "search", "ingest", "compass", "atlas", "time"],
                    "default": "governed",
                },
                "session_id": {"type": "string"},
                "dry_run": {"type": "boolean", "default": True},
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
                "query": {"type": "string"},
                "context": {
                    "oneOf": [
                        {"type": "string"},
                        {"type": "object"},
                        {"type": "array", "items": {"type": "string"}},
                    ]
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
                },
                "session_id": {"type": "string"},
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
                "query": {"type": "string", "description": "Primary query string (alias: request)"},
                "request": {
                    "type": "string",
                    "description": "Alternative query string for backward compatibility",
                },
                "mode": {"type": "string", "enum": ["kernel", "status"], "default": "kernel"},
                "session_id": {"type": "string"},
                "actor_id": {"type": "string"},
                "risk_tier": {
                    "type": "string",
                    "enum": ["low", "medium", "high", "critical"],
                    "default": "medium",
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
                "query": {"type": "string"},
                "mode": {"type": "string", "enum": ["critique", "simulate"], "default": "critique"},
                "session_id": {"type": "string"},
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
            "required": ["query"],
            "properties": {
                "query": {"type": "string"},
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
                "query": {"type": "string"},
                "risk_tier": {
                    "type": "string",
                    "enum": ["low", "medium", "high", "critical"],
                    "default": "medium",
                },
                "session_id": {"type": "string"},
            },
        },
        read_only_hint=False,
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
                "query": {"type": "string"},
                "mode": {
                    "type": "string",
                    "enum": ["vector_query", "vector_store", "engineer", "query"],
                    "default": "vector_query",
                },
                "session_id": {"type": "string"},
            },
        },
    ),
    # ─────────────────────────────────────────────────────────────────────────
    # 9. arifos_vault — Vault Ledger
    # ─────────────────────────────────────────────────────────────────────────
    ToolSpec(
        name="arifos_vault",
        stage="999",
        purpose="Vault ledger — Immutable verdict record",
        layer="GOVERNANCE",
        visibility="public",
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
                },
                "evidence": {"type": "string"},
                "session_id": {"type": "string"},
            },
        },
        read_only_hint=False,
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
                "action": {"type": "string", "enum": ["shell", "api_call", "contract", "compute"]},
                "payload": {"type": "object"},
                "session_id": {"type": "string"},
                "judge_verdict": {"type": "string", "enum": ["SEAL"]},
                "judge_g_star": {"type": "number"},
                "dry_run": {"type": "boolean", "default": True},
            },
        },
        read_only_hint=False,
        destructive_hint=True,
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
                "session_id": {"type": "string"},
                "mode": {
                    "type": "string",
                    "enum": ["guard", "audit", "correlate"],
                    "default": "guard",
                },
                "tool_trace": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "Ordered list of tool calls and outputs to evaluate for orthogonality.",
                },
                "correlation_threshold": {
                    "type": "number",
                    "default": 0.95,
                    "description": "Maximum allowed correlation before HOLD is recommended.",
                },
            },
        },
    ),
    # ─────────────────────────────────────────────────────────────────────────
    # 12. arifos_reply — AGI Reply Protocol
    # ─────────────────────────────────────────────────────────────────────────
    ToolSpec(
        visibility="internal",
        name="arifos_reply",
        stage="000-999",
        purpose="Arifos reply — Agi Reply Protocol v3",
        layer="GOVERNANCE",
        description=(
            "Composite orchestrator for AGI Reply Protocol v3. "
            "Internally runs: memory → sense → mind → heart → ops → judge → [vault/forge]. "
            "Emits AgiReplyEnvelopeHuman (recipient=human) or AgiReplyEnvelopeAgent (recipient=agent). "
            "Every output includes: TO/CC/TITLE/KEY_CONTEXT header, RACI block, computed τ, "
            "constitutional floor tags, SEAL signoff. 888 HOLD blocks forge. "
            "F1/F13 triggers require human:arif ratification."
        ),
        trinity="ALL",
        floors=("F1", "F2", "F3", "F4", "F7", "F9", "F11", "F13"),
        input_schema={
            "type": "object",
            "required": ["query", "session_id"],
            "properties": {
                "query": {"type": "string"},
                "session_id": {"type": "string"},
                "recipient": {
                    "type": "string",
                    "enum": ["human", "agent", "auto"],
                    "default": "auto",
                },
            },
        },
    ),
    # ─────────────────────────────────────────────────────────────────────────
    # 12. arifos_health — System Vitals (folded into arifos_ops; now internal)
    # ─────────────────────────────────────────────────────────────────────────
    ToolSpec(
        name="arifos_health",
        stage="111",
        purpose="Arifos health — Retrieve CPU, Memory, ZRAM, and Disk",
        layer="MACHINE",
        visibility="internal",
        description="Retrieve CPU, Memory, ZRAM, and Disk utilization. F12-hardened read-only access. Folded into arifos_ops(mode='health'|'vitals').",
        trinity="Δ",
        floors=("F4", "F12"),
        input_schema={
            "type": "object",
            "properties": {
                "session_id": {"type": "string"},
            },
        },
    ),
    # ─────────────────────────────────────────────────────────────────────────
    # 13. arifos_fetch — Guarded Fetch
    # ─────────────────────────────────────────────────────────────────────────
    ToolSpec(
        visibility="internal",
        name="arifos_fetch",
        stage="111",
        purpose="Arifos fetch — URL content retrieval via mcp_fetch",
        layer="MACHINE",
        description=(
            "Retrieve raw content from a URL via mcp_fetch substrate. "
            "Applies F9 Anti-Hantu constitutional filtering to redact spiritual cosplay "
            "or hallucinatory consciousness claims in the source content."
        ),
        trinity="Δ",
        floors=("F2", "F9", "F11"),
        input_schema={
            "type": "object",
            "required": ["url"],
            "properties": {
                "url": {"type": "string"},
                "session_id": {"type": "string"},
            },
        },
    ),
    # ─────────────────────────────────────────────────────────────────────────
    # 14. arifos_repo_read — Git Status
    # ─────────────────────────────────────────────────────────────────────────
    ToolSpec(
        visibility="internal",
        name="arifos_repo_read",
        stage="911",
        purpose="Arifos repo read — Git status, diffs, and log",
        layer="EXECUTION",
        description="Check git status, diffs, and log with constitutional path whitelisting.",
        trinity="Ψ",
        floors=("F11",),
        input_schema={
            "type": "object",
            "properties": {"path": {"type": "string", "default": "./"}},
        },
    ),
    # ─────────────────────────────────────────────────────────────────────────
    # 15. arifos_repo_seal — Git Commit
    # ─────────────────────────────────────────────────────────────────────────
    ToolSpec(
        visibility="internal",
        name="arifos_repo_seal",
        stage="999",
        purpose="Arifos repo seal — Mutate governed repo state",
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
                "message": {"type": "string"},
                "files": {"type": "array", "items": {"type": "string"}},
            },
        },
        read_only_hint=False,
        destructive_hint=True,
    ),
    # ─────────────────────────────────────────────────────────────────────────
    # 16. arifos_probe — Health Probe
    # ─────────────────────────────────────────────────────────────────────────
    ToolSpec(
        visibility="internal",
        name="arifos_probe",
        stage="111",
        purpose="Arifos probe — Component health diagnostic",
        layer="MACHINE",
        description="Probe system status or component health (system, memory, vault, etc.).",
        trinity="Δ",
        floors=("F4", "F12"),
        input_schema={
            "type": "object",
            "properties": {
                "target": {"type": "string", "default": "system"},
            },
        },
    ),
    # ─────────────────────────────────────────────────────────────────────────
    # 17. arifos_diag_substrate — Conformance Check
    # ─────────────────────────────────────────────────────────────────────────
    ToolSpec(
        visibility="internal",
        name="arifos_diag_substrate",
        stage="911",
        purpose="Arifos diag substrate — Protocol conformance check",
        layer="EXECUTION",
        description="Maintainer: Run substrate protocol conformance check.",
        trinity="Ψ",
        floors=("F11",),
        input_schema={
            "type": "object",
            "properties": {"session_id": {"type": "string"}},
        },
    ),
    # ─────────────────────────────────────────────────────────────────────────
    # 18. Judge Surface (APP)
    # ─────────────────────────────────────────────────────────────────────────
    ToolSpec(
        name="judge_surface",
        stage="888",
        purpose="Judge surface — Constitutional Verdict UI",
        layer="SURFACE",
        description=(
            "Open the arifOS Constitutional Verdict Surface. "
            "Evaluates a candidate action against all 13 constitutional floors. "
            "Human SEAL or REJECT required before any forge execution (F13 Sovereign)."
        ),
        trinity="Ψ",
        floors=("F1", "F13"),
        input_schema={
            "type": "object",
            "properties": {"candidate_action": {"type": "string"}},
        },
    ),
    # ─────────────────────────────────────────────────────────────────────────
    # 19. Vault Surface (APP)
    # ─────────────────────────────────────────────────────────────────────────
    ToolSpec(
        name="vault_ledger_surface",
        stage="911",
        purpose="Vault ledger surface — Immutable Vault UI",
        layer="SURFACE",
        description=(
            "Open the arifOS Immutable Vault Ledger. Shows the live BLS constitutional "
            "seal card and all VAULT999 ledger entries. F1 Amanah."
        ),
        trinity="Ψ",
        floors=("F1", "F11"),
        input_schema={"type": "object", "properties": {}},
    ),
    # ─────────────────────────────────────────────────────────────────────────
    # 20. Init Surface (APP)
    # ─────────────────────────────────────────────────────────────────────────
    ToolSpec(
        name="init_surface",
        stage="000",
        purpose="Init surface — Session Anchoring UI",
        layer="SURFACE",
        description=(
            "Open the arifOS Session Anchoring Surface. Declares intent, selects mode, "
            "and anchors the constitutional session. F1 Amanah — session creation is irreversible commitment."
        ),
        trinity="Ψ",
        floors=("F1", "F11"),
        input_schema={"type": "object", "properties": {"intent": {"type": "string"}}},
    ),
    # ─────────────────────────────────────────────────────────────────────────
    # 21. Forge Surface (APP)
    # ─────────────────────────────────────────────────────────────────────────
    ToolSpec(
        name="forge_surface",
        stage="010",
        purpose="Forge surface — Execution surface with double-gate",
        layer="SURFACE",
        description=(
            "Open the arifOS Forge Execution Surface with double-gate architecture. "
            "Gate 1: 888_JUDGE must SEAL. Gate 2: Human must APPROVE. "
            "F13 Sovereign Veto: no machine may cross this line alone."
        ),
        trinity="Δ",
        floors=("F1", "F13"),
        input_schema={"type": "object", "properties": {"action": {"type": "string"}}},
    ),
    # ─────────────────────────────────────────────────────────────────────────
    # WEALTH ORGAN — Capital Engine (Ψ lane)
    # ─────────────────────────────────────────────────────────────────────────
    ToolSpec(
        name="wealth_npv_reward",
        stage="WEALTH",
        purpose="Compute NPV, Terminal Value, and EAA",
        layer="INTELLIGENCE",
        visibility="public",
        description="High-precision Net Present Value calculation with thermodynamic confidence bands.",
        trinity="Ψ",
        floors=("F4", "F8"),
        input_schema={
            "type": "object",
            "required": ["initial_investment", "cash_flows", "discount_rate"],
            "properties": {
                "initial_investment": {"type": "number"},
                "cash_flows": {"type": "array", "items": {"type": "number"}},
                "discount_rate": {"type": "number", "default": 0.1},
                "terminal_value": {"type": "number", "default": 0},
                "epistemic": {
                    "type": "string",
                    "enum": ["CLAIM", "ESTIMATE", "HYPOTHESIS"],
                    "default": "CLAIM",
                },
            },
        },
    ),
    ToolSpec(
        name="wealth_irr_yield",
        stage="WEALTH",
        purpose="Compute Yield (IRR/MIRR)",
        layer="INTELLIGENCE",
        visibility="public",
        description="Compute Internal Rate of Return and Modified IRR for capital energy evaluation.",
        trinity="Ψ",
        floors=("F4", "F8"),
        input_schema={
            "type": "object",
            "required": ["initial_investment", "cash_flows"],
            "properties": {
                "initial_investment": {"type": "number"},
                "cash_flows": {"type": "array", "items": {"type": "number"}},
            },
        },
    ),
    ToolSpec(
        name="wealth_dscr_leverage",
        stage="WEALTH",
        purpose="Compute Leverage (DSCR)",
        layer="INTELLIGENCE",
        visibility="public",
        description="Compute Debt Service Coverage Ratio to evaluate structural survival load.",
        trinity="Ψ",
        floors=("F4", "F11"),
        input_schema={
            "type": "object",
            "required": ["ebitda", "debt_service"],
            "properties": {
                "ebitda": {"type": "number"},
                "debt_service": {"type": "number"},
            },
        },
    ),
    ToolSpec(
        visibility="public",
        name="wealth_brent_score",
        stage="WEALTH_01",
        purpose="Score O&G tickers against Brent price — plain English signal",
        role="Capital scoring for Malaysian O&G instruments",
        layer="INTELLIGENCE",
        description=(
            "Score a Bursa O&G or Malaysia-market ticker against current Brent price. "
            "Returns a plain-English signal (BUY/HOLD/SELL/CAUTION) with a one-sentence reason."
        ),
        trinity="Ψ",
        floors=("F4", "F9"),
        input_schema={
            "type": "object",
            "required": ["ticker", "brent_price", "scenario"],
            "properties": {
                "ticker": {"type": "string"},
                "brent_price": {"type": "number"},
                "scenario": {"type": "string", "enum": ["base", "bull", "bear"]},
                "session_id": {"type": "string"},
            },
        },
    ),
    # ─────────────────────────────────────────────────────────────────────────
    # 22. Metabolic Monitor (APP)
    # ─────────────────────────────────────────────────────────────────────────
    ToolSpec(
        name="arifos_monitor_metabolism",
        stage="111",
        purpose="Monitor metabolism — Real-time health dashboard",
        layer="SURFACE",
        description=(
            "Open the arifOS Metabolic Monitor — a real-time dashboard showing the health "
            "of all 13 Constitutional Floors (F1-F13), plus thermodynamic metrics: "
            "ΔS (entropy change), Peace² (stability), and Ω₀ (baseline)."
        ),
        trinity="Δ",
        floors=("F4", "F12"),
        input_schema={"type": "object", "properties": {}},
    ),
)


# ═══════════════════════════════════════════════════════════════════════════════
# METADATA & UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

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
    "vps_monitor": "arifos_health",
}

# ═══════════════════════════════════════════════════════════════════════════════
# RESOURCES
# ═══════════════════════════════════════════════════════════════════════════════

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
