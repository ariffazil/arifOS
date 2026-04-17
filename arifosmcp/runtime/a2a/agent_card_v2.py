"""
arifOS Agent Card v2.0
======================

A2A-aligned Agent Card for arifOS Constitutional Kernel v2.0.

Key changes from v1:
- 6-axis model (P/T/V/G/E/M) as primary skill taxonomy
- G02 Layered Router as primary entry skill
- Constitutional governance metadata (F1-F13, Ω_ortho, WELL gate)
- Agent registry integration (23 agents across 6 axes)
- Seal verification endpoint
- Event-sourced state machine representation

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


def _utcnow() -> datetime:
    return datetime.now(UTC)


class Axis(str, Enum):
    """The 6 irreducible cognitive axes."""

    P = "P"  # Perception — reality acquisition
    T = "T"  # Transformation — mathematical computation
    V = "V"  # Valuation — utility and allocation
    G = "G"  # Governance — constraint and legitimacy
    E = "E"  # Execution — state mutation
    M = "M"  # Meta-Cognition — self-inspection


class ConstitutionalMetadata(BaseModel):
    """arifOS-specific constitutional governance metadata."""

    constitutional_floors: int = 13
    floors_active: list[str] = Field(
        default_factory=lambda: [
            "F1_AMANAH",
            "F3_INPUT_CLARITY",
            "F4_ENTROPY",
            "F6_HARM_DIGNITY",
            "F7_CONFIDENCE",
            "F8_GROUNDING",
            "F9_INJECTION",
            "F11_COHERENCE",
            "F13_SOVEREIGN",
        ]
    )
    trinity: str = "ΔΩΨ"
    motto: str = "Ditempa Bukan Diberi — Forged, Not Given"
    omega_ortho_threshold: float = 0.85
    well_gate_active: bool = True
    vault_protocol: str = "VAULT999"
    seal_chain: str = "Merkle-rooted SHA256 hash chain"


class GovernanceCapabilities(BaseModel):
    """What arifOS governance layer supports."""

    streaming: bool = True
    push_notifications: bool = False
    state_transition_history: bool = True
    seal_verification: bool = True
    orthogonal_routing: bool = True
    human_veto: bool = True
    event_sourcing: bool = True
    thermodynamic_cost_tracking: bool = True


class RoutingMetadata(BaseModel):
    """G02 Layered Router metadata."""

    entry_point: str = "arifos_kernel"  # G02 Layered Router
    layers: list[str] = Field(
        default_factory=lambda: [
            "L1_AXIS_CLASSIFY",
            "L2_CALL_GRAPH_ENFORCE",
            "L3_PRECONDITION_GATE",
        ]
    )
    execution_requires_seal: bool = True
    seal_verdict: str = "SEAL"
    hold_verdict: str = "HOLD"
    void_verdict: str = "VOID"


class MetabolicStage(BaseModel):
    """arifOS Golden Path metabolic stage."""

    code: str  # e.g., "000", "111", "333"
    name: str
    description: str
    ordinal: int


class AxisSkill(BaseModel):
    """A skill mapped to a cognitive axis."""

    agent_id: str  # e.g., "G02", "E01", "M01"
    axis: str
    name: str
    description: str
    operation_class: str  # READ / COMPUTE / VALUE / GATE / MUTATE / META
    tool_name: str | None = None
    mcp_endpoint: str | None = None
    requires_seal: bool = False
    risk_tier: str = "medium"
    tags: list[str] = Field(default_factory=list)
    examples: list[str] = Field(default_factory=list)


class ArifOSAgentCard(BaseModel):
    """
    arifOS Agent Card v2.0 — A2A Discovery Document

    Published at: /.well-known/agent.json
    Extended at:  /.well-known/agent-card.json (authenticated)

    This is arifOS's sovereign identity document for A2A agent discovery.
    External sovereign agents use this to:
    - Discover arifOS capabilities
    - Route through G02 Layered Router
    - Negotiate inter-agent tasks
    - Verify constitutional governance guarantees
    """

    # ── Identity ─────────────────────────────────────────────────────────────
    name: str = "arifOS Constitutional Kernel"
    description: str = (
        "Constitutionally-governed sovereign AI kernel with 13 floors (F1-F13), "
        "6-axis orthogonal routing (P/T/V/G/E/M), G02 Layered Router, "
        "event-sourced metabolism, and VAULT999 cryptographic sealing. "
        "A2A connects minds. MCP connects hands. arifOS governs both."
    )
    url: str = "http://af-forge-arifos-mcp:8080"
    external_url: str = "https://arifosmcp.arif-fazil.com"
    version: str = "2026.04.17-V2"
    protocol_version: str = "A2A/1.0"

    # ── Authentication ─────────────────────────────────────────────────────────
    authentication: dict = Field(default_factory=dict)

    # ── Capabilities (populated in model_post_init) ─────────────────────────
    capabilities: dict = Field(default_factory=dict)

    # ── Routing (populated in model_post_init) ────────────────────────────────
    routing: dict = Field(default_factory=dict)

    # ── Constitutional Metadata (populated in model_post_init) ─────────────────
    constitutional: dict = Field(default_factory=dict)

    # ── Skills: 6-Axis Model ──────────────────────────────────────────────────
    skills: list = Field(default_factory=list)

    def model_post_init(self, *args):
        """Populate all fields lazily after init — avoids Pydantic forward-ref issues."""
        if not self.authentication:
            object.__setattr__(
                self,
                "authentication",
                {
                    "schemes": ["api_key", "bearer"],
                    "credentials": None,
                    "note": "OPERATOR_API_TOKEN required for human-expert and operator endpoints",
                },
            )
        if not self.capabilities:
            object.__setattr__(
                self,
                "capabilities",
                {
                    "streaming": True,
                    "pushNotifications": False,
                    "stateTransitionHistory": True,
                    "sealVerification": True,
                    "orthogonalRouting": True,
                    "humanVeto": True,
                    "eventSourcing": True,
                    "thermodynamicCostTracking": True,
                },
            )
        if not self.routing:
            object.__setattr__(
                self,
                "routing",
                {
                    "entry_point": "arifos_kernel",
                    "layers": ["L1_AXIS_CLASSIFY", "L2_CALL_GRAPH_ENFORCE", "L3_PRECONDITION_GATE"],
                    "execution_requires_seal": True,
                    "seal_verdict": "SEAL",
                    "hold_verdict": "HOLD",
                    "void_verdict": "VOID",
                },
            )
        if not self.constitutional:
            object.__setattr__(
                self,
                "constitutional",
                {
                    "constitutional_floors": 13,
                    "floors_active": [
                        "F1_AMANAH",
                        "F3_INPUT_CLARITY",
                        "F4_ENTROPY",
                        "F6_HARM_DIGNITY",
                        "F7_CONFIDENCE",
                        "F8_GROUNDING",
                        "F9_INJECTION",
                        "F11_COHERENCE",
                        "F13_SOVEREIGN",
                    ],
                    "trinity": "ΔΩΨ",
                    "motto": "Ditempa Bukan Diberi — Forged, Not Given",
                    "omega_ortho_threshold": 0.85,
                    "well_gate_active": True,
                    "vault_protocol": "VAULT999",
                    "seal_chain": "Merkle-rooted SHA256 hash chain",
                },
            )
        if not self.skills or len(self.skills) < 20:
            built_skills = _build_6axis_skills()
            object.__setattr__(self, "skills", built_skills)
            ax_counts = {
                "P_PERCEPTION": len([s for s in built_skills if s.axis == "P"]),
                "T_TRANSFORMATION": len([s for s in built_skills if s.axis == "T"]),
                "V_VALUATION": len([s for s in built_skills if s.axis == "V"]),
                "G_GOVERNANCE": len([s for s in built_skills if s.axis == "G"]),
                "E_EXECUTION": len([s for s in built_skills if s.axis == "E"]),
                "M_META_COGNITION": len([s for s in built_skills if s.axis == "M"]),
            }
            object.__setattr__(self, "axes", ax_counts)
            object.__setattr__(self, "total_agents", len(built_skills))

    # ── A2A Endpoints ────────────────────────────────────────────────────────
    endpoints: dict[str, str] = Field(
        default_factory=lambda: {
            "task": "/a2a/task",
            "status": "/a2a/status",
            "cancel": "/a2a/cancel",
            "subscribe": "/a2a/subscribe",
            "seal_verify": "/seal/verify",
            "well_state": "/well/state",
            "orthogonality": "/meta/omega",
        }
    )

    # ── Metabolic Stages (Golden Path) ────────────────────────────────────────
    metabolic_stages: list = Field(default_factory=list)

    # ── Axes Summary ───────────────────────────────────────────────────────────
    axes: dict[str, int] = Field(
        default_factory=lambda: {
            "P_PERCEPTION": 4,
            "T_TRANSFORMATION": 4,
            "V_VALUATION": 3,
            "G_GOVERNANCE": 6,
            "E_EXECUTION": 3,
            "M_META_COGNITION": 3,
        }
    )
    total_agents: int = 23

    # ── Discovery ─────────────────────────────────────────────────────────────
    well_known_path: str = "/.well-known/agent-card.json"
    agent_card_path: str = "/agent-card"  # Extended authenticated card


def _build_6axis_skills() -> list[AxisSkill]:
    """Build the 23-axis skills from agent registry."""
    skills = []

    # ── AXIS P: PERCEPTION ────────────────────────────────────────────────────
    skills.extend(
        [
            AxisSkill(
                agent_id="P01",
                axis="P",
                name="WELL State Reader",
                description="Read current human substrate state (cognitive fatigue, stress, clarity)",
                operation_class="READ",
                tool_name="well_state",
                mcp_endpoint="https://afwell.fastmcp.app/mcp",
                risk_tier="low",
                tags=["perception", "wellness", "human-state"],
                examples=["what is current operator fatigue?", "load wellness state"],
            ),
            AxisSkill(
                agent_id="P02",
                axis="P",
                name="WELL Readiness Reflector",
                description="Reflect operator readiness and cognitive load for governance decisions",
                operation_class="READ",
                tool_name="well_readiness",
                mcp_endpoint="https://afwell.fastmcp.app/mcp",
                risk_tier="low",
                tags=["perception", "readiness", "human-factor"],
            ),
            AxisSkill(
                agent_id="P03",
                axis="P",
                name="GEOX Reality Fetcher",
                description="Fetch earth/physical state from GEOX organ",
                operation_class="READ",
                tool_name="geo_snapshot",
                mcp_endpoint="https://geoxarifOS.fastmcp.app/mcp",
                risk_tier="low",
                tags=["perception", "geophysics", "earth-state"],
                examples=["what is current geological state?", "fetch spatial context"],
            ),
            AxisSkill(
                agent_id="P04",
                axis="P",
                name="Vault Ledger Reader",
                description="Read immutable VAULT999 ledger for audit and traceability",
                operation_class="READ",
                tool_name="arifos_vault",
                risk_tier="low",
                tags=["perception", "vault", "audit"],
            ),
        ]
    )

    # ── AXIS T: TRANSFORMATION ─────────────────────────────────────────────────
    skills.extend(
        [
            AxisSkill(
                agent_id="T01",
                axis="T",
                name="Petrophysics Engine",
                description="Compute petrophysical properties (porosity, saturation, permeability)",
                operation_class="COMPUTE",
                tool_name="geox_well_compute_petrophysics",
                mcp_endpoint="https://geoxarifOS.fastmcp.app/mcp",
                risk_tier="medium",
                tags=["transformation", "physics", "reservoir"],
            ),
            AxisSkill(
                agent_id="T02",
                axis="T",
                name="Monte Carlo Simulator",
                description="Run stochastic simulation for economic scenarios",
                operation_class="COMPUTE",
                tool_name="wealth_monte_carlo_forecast",
                risk_tier="medium",
                tags=["transformation", "simulation", "economics"],
            ),
            AxisSkill(
                agent_id="T03",
                axis="T",
                name="IRR/MIRR Calculator",
                description="Compute internal rate of return and modified rate of return",
                operation_class="COMPUTE",
                tool_name="wealth_wealth_irr_yield",
                risk_tier="medium",
                tags=["transformation", "finance", "yield"],
            ),
            AxisSkill(
                agent_id="T04",
                axis="T",
                name="Seismic Horizon Picker",
                description="Process seismic data and pick geological horizons",
                operation_class="COMPUTE",
                tool_name="geox_prospect_evaluate",
                mcp_endpoint="https://geoxarifOS.fastmcp.app/mcp",
                risk_tier="high",
                tags=["transformation", "geophysics", "seismic"],
            ),
        ]
    )

    # ── AXIS V: VALUATION ─────────────────────────────────────────────────────
    skills.extend(
        [
            AxisSkill(
                agent_id="V01",
                axis="V",
                name="NPV Evaluator",
                description="Compute net present value of investment scenarios",
                operation_class="VALUE",
                tool_name="wealth_wealth_npv_reward",
                risk_tier="medium",
                tags=["valuation", "finance", "investment"],
            ),
            AxisSkill(
                agent_id="V02",
                axis="V",
                name="EMV Risk Evaluator",
                description="Compute expected monetary value under uncertainty",
                operation_class="VALUE",
                tool_name="wealth_emv_evaluator",
                risk_tier="medium",
                tags=["valuation", "risk", "probability"],
            ),
            AxisSkill(
                agent_id="V03",
                axis="V",
                name="Allocation Score Kernel",
                description="Rank capital allocation options by constitutional utility",
                operation_class="VALUE",
                tool_name="wealth_allocation_score",
                risk_tier="high",
                tags=["valuation", "allocation", "ranking"],
            ),
        ]
    )

    # ── AXIS G: GOVERNANCE ─────────────────────────────────────────────────────
    skills.extend(
        [
            AxisSkill(
                agent_id="G01",
                axis="G",
                name="Session Initializer",
                description="Initialize constitutional session with actor identity and intent",
                operation_class="GATE",
                tool_name="arifos_init",
                risk_tier="medium",
                tags=["governance", "session", "identity"],
            ),
            AxisSkill(
                agent_id="G02",
                axis="G",
                name="Layered Router",
                description="Route requests through 3-layer enforcement: classify, call-graph, precondition",
                operation_class="GATE",
                tool_name="arifos_kernel",
                requires_seal=False,
                risk_tier="high",
                tags=["governance", "routing", "constitutional"],
                examples=["route query through constitutional layers"],
            ),
            AxisSkill(
                agent_id="G03",
                axis="G",
                name="Constitutional Mind",
                description="Structured reasoning with assumption registry and uncertainty bands",
                operation_class="GATE",
                tool_name="arifos_mind",
                risk_tier="medium",
                tags=["governance", "reasoning", "cognition"],
            ),
            AxisSkill(
                agent_id="G04",
                axis="G",
                name="Ethical Heart",
                description="Red-team simulation for harm, dignity, and systemic amplification",
                operation_class="GATE",
                tool_name="arifos_heart",
                risk_tier="medium",
                tags=["governance", "ethics", "safety"],
            ),
            AxisSkill(
                agent_id="G05",
                axis="G",
                name="Final Judge",
                description="Issue SEAL/HOLD/VOID/SABAR verdicts with floor trace and state hash",
                operation_class="GATE",
                tool_name="arifos_judge",
                risk_tier="high",
                tags=["governance", "judgment", "verdict"],
            ),
            AxisSkill(
                agent_id="G06",
                axis="G",
                name="Orthogonality Guard",
                description="Monitor cross-organ correlation and enforce epistemic boundaries",
                operation_class="GATE",
                tool_name="arifos_gateway",
                risk_tier="medium",
                tags=["governance", "orthogonality", "correlation"],
            ),
        ]
    )

    # ── AXIS E: EXECUTION ─────────────────────────────────────────────────────
    skills.extend(
        [
            AxisSkill(
                agent_id="E01",
                axis="E",
                name="Forge Bridge",
                description="Execute state mutation after G05 SEAL verification",
                operation_class="MUTATE",
                tool_name="arifos_forge",
                requires_seal=True,  # CRITICAL: Must have G05 SEAL
                risk_tier="critical",
                tags=["execution", "forge", "state-mutation"],
            ),
            AxisSkill(
                agent_id="E02",
                axis="E",
                name="Vault Sealer",
                description="Append immutable record to VAULT999 ledger",
                operation_class="MUTATE",
                tool_name="vault_seal",
                requires_seal=True,
                risk_tier="high",
                tags=["execution", "vault", "immutable"],
            ),
            AxisSkill(
                agent_id="E03",
                axis="E",
                name="Memory Store",
                description="Write to governed memory with constitutional constraints",
                operation_class="MUTATE",
                tool_name="arifos_memory",
                requires_seal=True,
                risk_tier="medium",
                tags=["execution", "memory", "state"],
            ),
        ]
    )

    # ── AXIS M: META-COGNITION ─────────────────────────────────────────────────
    skills.extend(
        [
            AxisSkill(
                agent_id="M01",
                axis="M",
                name="Correlation Auditor",
                description="Compute Ω_ortho from agent output correlation matrix",
                operation_class="META",
                tool_name="correlation_audit",
                risk_tier="low",
                tags=["meta", "orthogonality", "audit"],
            ),
            AxisSkill(
                agent_id="M02",
                axis="M",
                name="Skill Discovery",
                description="Discover and register agent capabilities in the federation",
                operation_class="META",
                tool_name="skill_discovery",
                risk_tier="low",
                tags=["meta", "discovery", "registry"],
            ),
            AxisSkill(
                agent_id="M03",
                axis="M",
                name="Metabolic Monitor",
                description="Monitor system health, floor violations, and governance telemetry",
                operation_class="META",
                tool_name="metabolic_monitor",
                risk_tier="low",
                tags=["meta", "monitoring", "health"],
            ),
        ]
    )

    return skills


def get_arifOS_agent_card() -> ArifOSAgentCard:
    """Factory to get the canonical arifOS Agent Card."""
    return ArifOSAgentCard.model_validate({}, strict=False)


def get_axos_summary() -> dict[str, Any]:
    """Get axes summary for quick discovery."""
    card = ArifOSAgentCard()
    return {
        "name": card.name,
        "version": card.version,
        "total_agents": card.total_agents,
        "axes": card.axes,
        "entry_point": card.routing.entry_point,
        "motto": card.constitutional.motto,
        "trinity": card.constitutional.trinity,
        "well_known_path": card.well_known_path,
    }
