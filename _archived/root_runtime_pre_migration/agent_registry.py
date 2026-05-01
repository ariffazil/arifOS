"""
arifOS Agent Registry
=====================

A2A-aligned agent registry with 6-axis model.
Each agent is a sovereign capability node exposed via A2A.

A2A connects minds. MCP connects hands. arifOS governs both.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class Axis(str, Enum):
    """The 6 irreducible cognitive axes."""

    P = "P"  # Perception — reality acquisition
    T = "T"  # Transformation — mathematical computation
    V = "V"  # Valuation — utility and allocation
    G = "G"  # Governance — constraint and legitimacy
    E = "E"  # Execution — state mutation
    M = "M"  # Meta-Cognition — self-inspection


class RiskTier(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class OperationClass(str, Enum):
    READ = "READ"  # Perception only
    COMPUTE = "COMPUTE"  # Transformation only
    VALUE = "VALUE"  # Valuation only
    GATE = "GATE"  # Governance only
    MUTATE = "MUTATE"  # Execution only
    META = "META"  # Meta-cognition only


@dataclass(frozen=True)
class AgentSkill:
    """A2A AgentSkill — what this agent can do."""

    id: str
    name: str
    description: str
    tags: tuple[str, ...] = ()
    examples: tuple[str, ...] = ()
    input_modes: tuple[str, ...] = ("text",)
    output_modes: tuple[str, ...] = ("text",)


@dataclass(frozen=True)
class AgentCapability:
    """A2A AgentCapability — protocol features supported."""

    streaming: bool = True
    push_notifications: bool = False
    state_transition_history: bool = True


@dataclass(frozen=True)
class AgentSpec:
    """
    The canonical spec for one agent in the 6-axis model.
    Used by G02 to enforce call graph and preconditions.
    """

    agent_id: str  # e.g., "P01", "G02", "E03"
    axis: Axis
    name: str  # Human-readable name
    tool_name: str  # MCP tool name (if applicable)
    skill: AgentSkill  # A2A skill declaration
    operation_class: OperationClass
    input_schema: dict[str, Any]  # JSON Schema for inputs
    output_schema: dict[str, Any]  # JSON Schema for outputs
    mutation: bool  # Does it write state?
    requires_seal: bool  # Needs G05 verdict before executing?
    allowed_callers: frozenset[Axis]  # Who can invoke this agent
    risk_tier: RiskTier
    mcp_endpoint: str | None = None  # If exposed as MCP tool


# ─── Call Graph Rules ────────────────────────────────────────────────────────
#
# Who can call whom:
#
#   P (Perception)  → Cannot call any axis (reads reality only)
#   T (Transform)   → Cannot call any axis (computes only)
#   V (Valuation)   → Cannot call any axis (ranks only)
#   G (Governance)  → Can call P, T, V (inspection + reasoning)
#   E (Execution)   → Cannot be called directly (only via G05 SEAL)
#   M (Meta)        → Observes all, calls none (auditor)
#   External         → Can only call G (routing entry point)
#
# Key invariant: E-axis is physically unreachable without G05 SEAL.
# ─────────────────────────────────────────────────────────────────────────────

CALL_GRAPH: dict[Axis, frozenset[Axis]] = {
    Axis.P: frozenset(),  # P cannot call anyone
    Axis.T: frozenset(),  # T cannot call anyone
    Axis.V: frozenset(),  # V cannot call anyone
    Axis.G: frozenset([Axis.P, Axis.T, Axis.V]),  # G can inspect P/T/V
    Axis.E: frozenset(),  # E unreachable directly
    Axis.M: frozenset(),  # M observes, doesn't call
}


@dataclass
class RouteContext:
    """Context carried through G02 layered routing."""

    session_id: str | None = None
    actor_id: str | None = None
    risk_tier: RiskTier = RiskTier.MEDIUM
    caller_axis: Axis | None = None
    judge_verdict: str | None = None  # SEAL, HOLD, VOID, SABAR
    judge_state_hash: str | None = None
    well_readiness: float = 1.0  # 0.0–1.0
    trace: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class RouteResult:
    """Result from G02 layered router."""

    ok: bool
    target_agent: str | None = None
    target_axis: Axis | None = None
    operation_class: OperationClass | None = None
    verdict: str | None = None  # SEAL, HOLD, VOID, 888_HOLD
    reason: str = ""
    blocked_reason: str | None = None  # Why route was blocked
    context: RouteContext | None = None


# ─── Agent Registry ────────────────────────────────────────────────────────────


class AgentRegistry:
    """
    Registry of all 6-axis agents.
    G02 uses this to classify, route, and enforce.
    """

    def __init__(self):
        self._agents: dict[str, AgentSpec] = {}
        self._by_axis: dict[Axis, list[AgentSpec]] = {a: [] for a in Axis}
        self._by_skill_id: dict[str, AgentSpec] = {}
        self._register_agents()

    def _register_agents(self):
        """Register all 6-axis agents (P/T/V/G/E/M)."""
        specs = [
            # ── AXIS P: PERCEPTION (Reality Acquisition) ──────────────────────
            AgentSpec(
                agent_id="P01",
                axis=Axis.P,
                name="WELL State Reader",
                tool_name="well_state",
                skill=AgentSkill(
                    id="well_state",
                    name="WELL State Reader",
                    description="Read current human substrate state (cognitive fatigue, stress, clarity)",
                    tags=["perception", "wellness", "human-state"],
                    examples=["what is current operator fatigue?", "load wellness state"],
                ),
                operation_class=OperationClass.READ,
                input_schema={
                    "type": "object",
                    "properties": {
                        "metric": {
                            "type": "string",
                            "enum": ["fatigue", "stress", "clarity", "all"],
                        },
                        "session_id": {"type": "string"},
                    },
                },
                output_schema={"type": "object"},
                mutation=False,
                requires_seal=False,
                allowed_callers=frozenset([Axis.G]),
                risk_tier=RiskTier.LOW,
                mcp_endpoint="https://afwell.fastmcp.app/mcp",
            ),
            AgentSpec(
                agent_id="P02",
                axis=Axis.P,
                name="WELL Readiness Reflector",
                tool_name="well_readiness",
                skill=AgentSkill(
                    id="well_readiness",
                    name="WELL Readiness Reflector",
                    description="Reflect operator readiness and cognitive load for governance decisions",
                    tags=["perception", "readiness", "human-factor"],
                ),
                operation_class=OperationClass.READ,
                input_schema={"type": "object", "properties": {}},
                output_schema={"type": "object"},
                mutation=False,
                requires_seal=False,
                allowed_callers=frozenset([Axis.G]),
                risk_tier=RiskTier.LOW,
                mcp_endpoint="https://afwell.fastmcp.app/mcp",
            ),
            AgentSpec(
                agent_id="P03",
                axis=Axis.P,
                name="GEOX Reality Fetcher",
                tool_name="geo_snapshot",
                skill=AgentSkill(
                    id="geo_snapshot",
                    name="GEOX Reality Fetcher",
                    description="Fetch earth/physical state from GEOX organ",
                    tags=["perception", "geophysics", "earth-state"],
                    examples=["what is current geological state?", "fetch spatial context"],
                ),
                operation_class=OperationClass.READ,
                input_schema={"type": "object", "properties": {"region": {"type": "string"}}},
                output_schema={"type": "object"},
                mutation=False,
                requires_seal=False,
                allowed_callers=frozenset([Axis.G]),
                risk_tier=RiskTier.LOW,
                mcp_endpoint="https://geoxarifOS.fastmcp.app/mcp",
            ),
            AgentSpec(
                agent_id="P04",
                axis=Axis.P,
                name="Vault Ledger Reader",
                tool_name="arifos_vault",
                skill=AgentSkill(
                    id="vault_reader",
                    name="Vault Ledger Reader",
                    description="Read immutable VAULT999 ledger for audit and traceability",
                    tags=["perception", "vault", "audit"],
                ),
                operation_class=OperationClass.READ,
                input_schema={"type": "object", "properties": {"query": {"type": "string"}}},
                output_schema={"type": "object"},
                mutation=False,
                requires_seal=False,
                allowed_callers=frozenset([Axis.G, Axis.M]),
                risk_tier=RiskTier.LOW,
                mcp_endpoint=None,  # arifOS internal
            ),
            # ── AXIS T: TRANSFORMATION (Mathematical Computation) ─────────────
            AgentSpec(
                agent_id="T01",
                axis=Axis.T,
                name="Petrophysics Engine",
                tool_name="geox_well_compute_petrophysics",
                skill=AgentSkill(
                    id="petrophysics",
                    name="Petrophysics Engine",
                    description="Compute petrophysical properties (porosity, saturation, permeability)",
                    tags=["transformation", "physics", "reservoir"],
                ),
                operation_class=OperationClass.COMPUTE,
                input_schema={
                    "type": "object",
                    "properties": {
                        "phi_hc": {"type": "number"},
                        "sw": {"type": "number"},
                        "tool": {"type": "string"},
                    },
                    "required": ["phi_hc", "sw"],
                },
                output_schema={"type": "object"},
                mutation=False,
                requires_seal=False,
                allowed_callers=frozenset([Axis.G]),
                risk_tier=RiskTier.MEDIUM,
                mcp_endpoint="https://geoxarifOS.fastmcp.app/mcp",
            ),
            AgentSpec(
                agent_id="T02",
                axis=Axis.T,
                name="Monte Carlo Simulator",
                tool_name="wealth_monte_carlo_forecast",
                skill=AgentSkill(
                    id="monte_carlo",
                    name="Monte Carlo Simulator",
                    description="Run stochastic simulation for economic scenarios",
                    tags=["transformation", "simulation", "economics"],
                ),
                operation_class=OperationClass.COMPUTE,
                input_schema={"type": "object", "properties": {"scenarios": {"type": "integer"}}},
                output_schema={"type": "object"},
                mutation=False,
                requires_seal=False,
                allowed_callers=frozenset([Axis.G]),
                risk_tier=RiskTier.MEDIUM,
                mcp_endpoint=None,  # arifOS internal
            ),
            AgentSpec(
                agent_id="T03",
                axis=Axis.T,
                name="IRR/MIRR Calculator",
                tool_name="wealth_wealth_irr_yield",
                skill=AgentSkill(
                    id="irr_calculator",
                    name="IRR/MIRR Calculator",
                    description="Compute internal rate of return and modified rate of return",
                    tags=["transformation", "finance", "yield"],
                ),
                operation_class=OperationClass.COMPUTE,
                input_schema={"type": "object", "properties": {"cashflows": {"type": "array"}}},
                output_schema={"type": "object"},
                mutation=False,
                requires_seal=False,
                allowed_callers=frozenset([Axis.G]),
                risk_tier=RiskTier.MEDIUM,
                mcp_endpoint=None,  # arifOS internal
            ),
            AgentSpec(
                agent_id="T04",
                axis=Axis.T,
                name="Seismic Horizon Picker",
                tool_name="geox_prospect_evaluate",
                skill=AgentSkill(
                    id="seismic_analysis",
                    name="Seismic Horizon Picker",
                    description="Process seismic data and pick geological horizons",
                    tags=["transformation", "geophysics", "seismic"],
                ),
                operation_class=OperationClass.COMPUTE,
                input_schema={"type": "object", "properties": {"region": {"type": "string"}}},
                output_schema={"type": "object"},
                mutation=False,
                requires_seal=False,
                allowed_callers=frozenset([Axis.G]),
                risk_tier=RiskTier.HIGH,
                mcp_endpoint="https://geoxarifOS.fastmcp.app/mcp",
            ),
            # ── AXIS V: VALUATION (Utility & Allocation) ──────────────────────
            AgentSpec(
                agent_id="V01",
                axis=Axis.V,
                name="NPV Evaluator",
                tool_name="wealth_wealth_npv_reward",
                skill=AgentSkill(
                    id="npv_evaluator",
                    name="NPV Evaluator",
                    description="Compute net present value of investment scenarios",
                    tags=["valuation", "finance", "investment"],
                ),
                operation_class=OperationClass.VALUE,
                input_schema={
                    "type": "object",
                    "properties": {
                        "cashflows": {"type": "array"},
                        "discount_rate": {"type": "number"},
                    },
                },
                output_schema={"type": "object"},
                mutation=False,
                requires_seal=False,
                allowed_callers=frozenset([Axis.G]),
                risk_tier=RiskTier.MEDIUM,
                mcp_endpoint=None,
            ),
            AgentSpec(
                agent_id="V02",
                axis=Axis.V,
                name="EMV Risk Evaluator",
                tool_name="wealth_emv_evaluator",
                skill=AgentSkill(
                    id="emv_evaluator",
                    name="EMV Risk Evaluator",
                    description="Compute expected monetary value under uncertainty",
                    tags=["valuation", "risk", "probability"],
                ),
                operation_class=OperationClass.VALUE,
                input_schema={
                    "type": "object",
                    "properties": {
                        "outcomes": {"type": "array"},
                        "probabilities": {"type": "array"},
                    },
                },
                output_schema={"type": "object"},
                mutation=False,
                requires_seal=False,
                allowed_callers=frozenset([Axis.G]),
                risk_tier=RiskTier.MEDIUM,
                mcp_endpoint=None,
            ),
            AgentSpec(
                agent_id="V03",
                axis=Axis.V,
                name="Allocation Score Kernel",
                tool_name="wealth_allocation_score",
                skill=AgentSkill(
                    id="allocation_score",
                    name="Allocation Score Kernel",
                    description="Rank capital allocation options by constitutional utility",
                    tags=["valuation", "allocation", "ranking"],
                ),
                operation_class=OperationClass.VALUE,
                input_schema={"type": "object", "properties": {"options": {"type": "array"}}},
                output_schema={"type": "object"},
                mutation=False,
                requires_seal=False,
                allowed_callers=frozenset([Axis.G]),
                risk_tier=RiskTier.HIGH,
                mcp_endpoint=None,
            ),
            # ── AXIS G: GOVERNANCE (Constraint & Legitimacy) ──────────────────
            AgentSpec(
                agent_id="G01",
                axis=Axis.G,
                name="Session Initializer",
                tool_name="arifos_init",
                skill=AgentSkill(
                    id="session_init",
                    name="Session Initializer",
                    description="Initialize constitutional session with actor identity and intent",
                    tags=["governance", "session", "identity"],
                ),
                operation_class=OperationClass.GATE,
                input_schema={
                    "type": "object",
                    "properties": {
                        "actor_id": {"type": "string"},
                        "intent": {"type": "string"},
                        "declared_name": {"type": "string"},
                    },
                    "required": ["actor_id", "intent"],
                },
                output_schema={"type": "object"},
                mutation=True,  # Creates session state
                requires_seal=False,  # G01 itself doesn't need seal
                allowed_callers=frozenset([Axis.M]),  # Only M can call G01 directly
                risk_tier=RiskTier.MEDIUM,
                mcp_endpoint=None,
            ),
            AgentSpec(
                agent_id="G02",
                axis=Axis.G,
                name="Layered Router",
                tool_name="arifos_kernel",
                skill=AgentSkill(
                    id="kernel_router",
                    name="Layered Router",
                    description="Route requests through 3-layer enforcement: classify, call-graph, precondition",
                    tags=["governance", "routing", "constitutional"],
                ),
                operation_class=OperationClass.GATE,
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "session_id": {"type": "string"},
                        "actor_id": {"type": "string"},
                        "risk_tier": {
                            "type": "string",
                            "enum": ["low", "medium", "high", "critical"],
                        },
                    },
                    "required": ["query"],
                },
                output_schema={"type": "object"},
                mutation=False,
                requires_seal=False,  # G02 is the gate itself
                allowed_callers=frozenset(),  # G02 is entry point (external calls G02)
                risk_tier=RiskTier.HIGH,
                mcp_endpoint=None,
            ),
            AgentSpec(
                agent_id="G03",
                axis=Axis.G,
                name="Constitutional Mind",
                tool_name="arifos_mind",
                skill=AgentSkill(
                    id="constitutional_mind",
                    name="Constitutional Mind",
                    description="Structured reasoning with assumption registry and uncertainty bands",
                    tags=["governance", "reasoning", "cognition"],
                ),
                operation_class=OperationClass.GATE,
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "session_id": {"type": "string"},
                        "risk_tier": {"type": "string"},
                    },
                    "required": ["query"],
                },
                output_schema={"type": "object"},
                mutation=False,
                requires_seal=False,
                allowed_callers=frozenset([Axis.G]),  # Only G-axis can call G03
                risk_tier=RiskTier.MEDIUM,
                mcp_endpoint=None,
            ),
            AgentSpec(
                agent_id="G04",
                axis=Axis.G,
                name="Ethical Heart",
                tool_name="arifos_heart",
                skill=AgentSkill(
                    id="ethical_heart",
                    name="Ethical Heart",
                    description="Red-team simulation for harm, dignity, and systemic amplification",
                    tags=["governance", "ethics", "safety"],
                ),
                operation_class=OperationClass.GATE,
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "mode": {"type": "string", "enum": ["critique", "simulate"]},
                        "session_id": {"type": "string"},
                    },
                    "required": ["query"],
                },
                output_schema={"type": "object"},
                mutation=False,
                requires_seal=False,
                allowed_callers=frozenset([Axis.G]),
                risk_tier=RiskTier.MEDIUM,
                mcp_endpoint=None,
            ),
            AgentSpec(
                agent_id="G05",
                axis=Axis.G,
                name="Final Judge",
                tool_name="arifos_judge",
                skill=AgentSkill(
                    id="apex_judge",
                    name="Final Judge",
                    description="Issue SEAL/HOLD/VOID/SABAR verdicts with floor trace and state hash",
                    tags=["governance", "judgment", "verdict"],
                ),
                operation_class=OperationClass.GATE,
                input_schema={
                    "type": "object",
                    "properties": {
                        "candidate_action": {"type": "string"},
                        "risk_tier": {"type": "string"},
                        "session_id": {"type": "string"},
                    },
                    "required": ["candidate_action"],
                },
                output_schema={"type": "object"},
                mutation=False,
                requires_seal=False,  # G05 is the seal authority
                allowed_callers=frozenset([Axis.G]),
                risk_tier=RiskTier.HIGH,
                mcp_endpoint=None,
            ),
            AgentSpec(
                agent_id="G06",
                axis=Axis.G,
                name="Orthogonality Guard",
                tool_name="arifos_gateway",
                skill=AgentSkill(
                    id="orthogonality_guard",
                    name="Orthogonality Guard",
                    description="Monitor cross-organ correlation and enforce epistemic boundaries",
                    tags=["governance", "orthogonality", "correlation"],
                ),
                operation_class=OperationClass.GATE,
                input_schema={"type": "object", "properties": {}},
                output_schema={"type": "object"},
                mutation=False,
                requires_seal=False,
                allowed_callers=frozenset([Axis.G]),
                risk_tier=RiskTier.MEDIUM,
                mcp_endpoint=None,
            ),
            # ── AXIS E: EXECUTION (State Mutation) ────────────────────────────
            AgentSpec(
                agent_id="E01",
                axis=Axis.E,
                name="Forge Bridge",
                tool_name="arifos_forge",
                skill=AgentSkill(
                    id="forge_bridge",
                    name="Forge Bridge",
                    description="Execute state mutation after G05 SEAL verification",
                    tags=["execution", "forge", "state-mutation"],
                ),
                operation_class=OperationClass.MUTATE,
                input_schema={
                    "type": "object",
                    "properties": {
                        "action": {"type": "string"},
                        "judge_verdict": {"type": "string"},
                        "judge_state_hash": {"type": "string"},
                        "session_id": {"type": "string"},
                    },
                    "required": ["action", "judge_verdict", "judge_state_hash"],
                },
                output_schema={"type": "object"},
                mutation=True,
                requires_seal=True,  # MUST have G05 SEAL
                allowed_callers=frozenset([Axis.G]),  # Only G-axis can authorize E
                risk_tier=RiskTier.CRITICAL,
                mcp_endpoint=None,
            ),
            AgentSpec(
                agent_id="E02",
                axis=Axis.E,
                name="Vault Sealer",
                tool_name="vault_seal",
                skill=AgentSkill(
                    id="vault_sealer",
                    name="Vault Sealer",
                    description="Append immutable record to VAULT999 ledger",
                    tags=["execution", "vault", "immutable"],
                ),
                operation_class=OperationClass.MUTATE,
                input_schema={
                    "type": "object",
                    "properties": {
                        "event": {"type": "object"},
                        "judge_verdict": {"type": "string"},
                    },
                    "required": ["event"],
                },
                output_schema={"type": "object"},
                mutation=True,
                requires_seal=True,
                allowed_callers=frozenset([Axis.G]),
                risk_tier=RiskTier.HIGH,
                mcp_endpoint=None,
            ),
            AgentSpec(
                agent_id="E03",
                axis=Axis.E,
                name="Memory Store",
                tool_name="arifos_memory",
                skill=AgentSkill(
                    id="memory_store",
                    name="Memory Store",
                    description="Write to governed memory with constitutional constraints",
                    tags=["execution", "memory", "state"],
                ),
                operation_class=OperationClass.MUTATE,
                input_schema={
                    "type": "object",
                    "properties": {
                        "key": {"type": "string"},
                        "value": {"type": "string"},
                        "tier": {"type": "string", "enum": ["ephemeral", "working", "canon"]},
                    },
                    "required": ["key", "value"],
                },
                output_schema={"type": "object"},
                mutation=True,
                requires_seal=True,
                allowed_callers=frozenset([Axis.G]),
                risk_tier=RiskTier.MEDIUM,
                mcp_endpoint=None,
            ),
            # ── AXIS M: META-COGNITION (Self-Inspection) ──────────────────────
            AgentSpec(
                agent_id="M01",
                axis=Axis.M,
                name="Correlation Auditor",
                tool_name="correlation_audit",
                skill=AgentSkill(
                    id="correlation_auditor",
                    name="Correlation Auditor",
                    description="Compute Ω_ortho from agent output correlation matrix",
                    tags=["meta", "orthogonality", "audit"],
                ),
                operation_class=OperationClass.META,
                input_schema={"type": "object", "properties": {}},
                output_schema={"type": "object"},
                mutation=False,
                requires_seal=False,
                allowed_callers=frozenset([Axis.G]),
                risk_tier=RiskTier.LOW,
                mcp_endpoint=None,
            ),
            AgentSpec(
                agent_id="M02",
                axis=Axis.M,
                name="Skill Discovery",
                tool_name="skill_discovery",
                skill=AgentSkill(
                    id="skill_discovery",
                    name="Skill Discovery",
                    description="Discover and register agent capabilities in the federation",
                    tags=["meta", "discovery", "registry"],
                ),
                operation_class=OperationClass.META,
                input_schema={"type": "object", "properties": {"query": {"type": "string"}}},
                output_schema={"type": "object"},
                mutation=False,
                requires_seal=False,
                allowed_callers=frozenset([Axis.G]),
                risk_tier=RiskTier.LOW,
                mcp_endpoint=None,
            ),
            AgentSpec(
                agent_id="M03",
                axis=Axis.M,
                name="Metabolic Monitor",
                tool_name="metabolic_monitor",
                skill=AgentSkill(
                    id="metabolic_monitor",
                    name="Metabolic Monitor",
                    description="Monitor system health, floor violations, and governance telemetry",
                    tags=["meta", "monitoring", "health"],
                ),
                operation_class=OperationClass.META,
                input_schema={"type": "object", "properties": {}},
                output_schema={"type": "object"},
                mutation=False,
                requires_seal=False,
                allowed_callers=frozenset([Axis.G]),
                risk_tier=RiskTier.LOW,
                mcp_endpoint=None,
            ),
        ]

        for spec in specs:
            self.register(spec)

    def register(self, spec: AgentSpec):
        """Register an agent spec."""
        self._agents[spec.agent_id] = spec
        self._by_axis[spec.axis].append(spec)
        self._by_skill_id[spec.skill.id] = spec

    def get(self, agent_id: str) -> AgentSpec | None:
        return self._agents.get(agent_id)

    def by_axis(self, axis: Axis) -> list[AgentSpec]:
        return self._by_axis[axis]

    def by_skill(self, skill_id: str) -> AgentSpec | None:
        return self._by_skill_id.get(skill_id)

    def all_agents(self) -> list[AgentSpec]:
        return list(self._agents.values())

    def get_agent_cards(self) -> list[dict[str, Any]]:
        """Generate A2A Agent Cards for all agents."""
        cards = []
        for spec in self._agents.values():
            card = {
                "agent_id": spec.agent_id,
                "name": spec.name,
                "description": spec.skill.description,
                "url": spec.mcp_endpoint or "internal://arifOS",
                "version": "2026.04.17",
                "axis": spec.axis.value,
                "operation_class": spec.operation_class.value,
                "skills": [
                    {
                        "id": spec.skill.id,
                        "name": spec.skill.name,
                        "description": spec.skill.description,
                        "tags": list(spec.skill.tags),
                        "input_modes": list(spec.skill.input_modes),
                        "output_modes": list(spec.skill.output_modes),
                    }
                ],
                "capabilities": {
                    "streaming": True,
                    "pushNotifications": False,
                    "stateTransitionHistory": True,
                },
                "authentication": {
                    "schemes": ["api_key"],
                    "credentials": None,
                },
                "metadata": {
                    "mutation": spec.mutation,
                    "requires_seal": spec.requires_seal,
                    "risk_tier": spec.risk_tier.value,
                    "allowed_callers": [a.value for a in spec.allowed_callers],
                },
            }
            cards.append(card)
        return cards


# ─── Singleton registry ────────────────────────────────────────────────────────

_registry: AgentRegistry | None = None


def get_registry() -> AgentRegistry:
    global _registry
    if _registry is None:
        _registry = AgentRegistry()
    return _registry
