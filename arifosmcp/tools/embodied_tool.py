"""
arifOS Embodied Tool Base Class
═══════════════════════════════════════════════════════════════════════════════════════

Tools that know their own body.

Every tool:
1. Has a manifest declaring its capabilities, limitations, risk tier
2. Is registered in the tool self-model at startup
3. Goes through embodied pre-flight before execution
4. Returns an EmbodiedToolEnvelope after execution
5. Is witnessed in the witness log

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import logging
import time
from abc import abstractmethod
from typing import Any

from arifosmcp.core.embodied_tool_engine import EmbodiedDecision, EmbodiedToolEngine
from arifosmcp.core.tool_self_model import (
    BlastRadius,
    ToolCapability,
    ToolLimitation,
    ToolManifest,
    get_tool_self_model,
)
from arifosmcp.core.witness_log import get_witness_log
from arifosmcp.schemas.embodied_tool import (
    EmbodiedToolEnvelope,
)

logger = logging.getLogger(__name__)


def register_embodied_tool(
    tool_id: str,
    tool_name: str,
    domain: str,
    description: str = "",
    risk_tier: str = "T1",
    reversibility: str = "reversible",
    blast_radius: str = "low",
    required_permissions: list[str] | None = None,
    capabilities: list[dict[str, str]] | None = None,
    limitations: list[dict[str, str]] | None = None,
    safe_compose_with: list[str] | None = None,
    dangerous_compose_with: list[str] | None = None,
    required_floors: list[str] | None = None,
) -> None:
    """
    Register a tool in the global self-model.

    Call this at module import time for every embodied tool.
    """
    capabilities_obj = (
        [ToolCapability(name=c["name"], description=c["description"]) for c in capabilities]
        if capabilities
        else []
    )
    limitations_obj = (
        [ToolLimitation(name=lim["name"], description=lim["description"]) for lim in limitations]
        if limitations
        else []
    )

    manifest = ToolManifest(
        tool_id=tool_id,
        tool_name=tool_name,
        domain=domain,
        description=description,
        capabilities=capabilities_obj,
        limitations=limitations_obj,
        risk_tier=risk_tier,
        reversibility=reversibility,
        blast_radius=BlastRadius(blast_radius),
        required_permissions=required_permissions or [],
        required_floors=required_floors or [],
        safe_compose_with=safe_compose_with or [],
        dangerous_compose_with=dangerous_compose_with or [],
    )

    get_tool_self_model().register(manifest)
    logger.debug(f"Registered embodied tool: {tool_id} ({domain}, {risk_tier})")


class EmbodiedTool:
    """
    Base class for tools that use the embodied tool pipeline.

    Every tool call goes through:
    1. preflight()  — embodied checks
    2. execute()    — actual tool logic
    3. postflight()  — build envelope + witness

    Subclasses only implement execute().

    Example:
        class ArifMindReasonTool(EmbodiedTool):
            tool_id = "arif_mind_reason"
            tool_name = "arif_mind_reason"
            domain = "AOS"
            risk_tier = "T1"
            reversibility = "reversible"

            async def execute(self, params: dict, ctx) -> dict:
                # Tool logic here
                return {"reasoning": "..."}
    """

    tool_id: str = ""
    tool_name: str = ""
    domain: str = "AOS"  # AOS | WELL | WEALTH | GEOX
    description: str = ""
    risk_tier: str = "T1"
    reversibility: str = "reversible"
    blast_radius: str = "low"
    required_permissions: list[str] = []
    required_floors: list[str] = []
    safe_compose_with: list[str] = []
    dangerous_compose_with: list[str] = []

    _engine: EmbodiedToolEngine | None = None
    _registered: bool = False

    @classmethod
    def manifest(cls) -> ToolManifest:
        """Build this tool's manifest."""
        return ToolManifest(
            tool_id=cls.tool_id,
            tool_name=cls.tool_name,
            domain=cls.domain,
            description=cls.description or cls.tool_name,
            capabilities=[],
            limitations=[],
            risk_tier=cls.risk_tier,
            reversibility=cls.reversibility,
            blast_radius=BlastRadius(cls.blast_radius),
            required_permissions=cls.required_permissions,
            required_floors=cls.required_floors,
            safe_compose_with=cls.safe_compose_with,
            dangerous_compose_with=cls.dangerous_compose_with,
        )

    @classmethod
    def register(cls) -> None:
        """Register this tool in the global self-model."""
        if cls._registered:
            return
        manifest = cls.manifest()
        get_tool_self_model().register(manifest)
        cls._registered = True
        logger.debug(f"Registered embodied tool: {cls.tool_id}")

    @classmethod
    def engine(cls) -> EmbodiedToolEngine:
        """Get the embodied tool engine singleton."""
        if cls._engine is None:
            cls._engine = EmbodiedToolEngine()
        return cls._engine

    @abstractmethod
    async def execute(self, params: dict, ctx: Any) -> dict:
        """
        Implement tool logic here.

        Args:
            params: Validated tool parameters
            ctx: FastMCP context

        Returns:
            Tool-specific result dict
        """
        ...

    async def preflight(
        self,
        params: dict,
        actor_id: str | None,
        session_id: str | None,
    ) -> EmbodiedDecision:
        """
        Stage 1: Embodied pre-flight checks.

        Returns EmbodiedDecision with can_proceed and full reasoning.
        """
        return await self.engine().run_preflight(
            tool_id=self.tool_id,
            params=params,
            actor_id=actor_id,
            session_id=session_id,
        )

    async def postflight(
        self,
        params: dict,
        actor_id: str | None,
        session_id: str | None,
        decision: EmbodiedDecision,
        result: dict,
        latency_ms: float,
        error: str | None = None,
        confidence: float = 0.5,
        reasoning_summary: str = "",
    ) -> EmbodiedToolEnvelope:
        """
        Stage 2: Build EmbodiedToolEnvelope and write witness log.

        Returns the complete envelope.
        """
        envelope = await self.engine().run_postflight(
            tool_id=self.tool_id,
            params=params,
            actor_id=actor_id,
            session_id=session_id,
            decision=decision,
            result=result,
            latency_ms=latency_ms,
            error=error,
            confidence=confidence,
            reasoning_summary=reasoning_summary,
        )

        # Also append to witness log
        witness_log = get_witness_log()
        witness_log.append(
            tool_id=self.tool_id,
            actor_id=actor_id,
            session_id=session_id,
            domain=self.domain,
            risk_tier=decision.risk_tier.value,
            reversibility=decision.reversibility.value,
            status=decision.status,
            confidence=confidence,
            authority_verified=decision.authority_verified,
            input_hash=hashlib.sha256(
                f"{self.tool_id}:{actor_id}:{session_id}:{str(params)}".encode()
            ).hexdigest(),
            reasoning_summary=reasoning_summary,
            error=error,
            next_action=envelope.next_safe_action,
            latency_ms=latency_ms,
        )

        # Also update the self-model — closes the feedback loop
        self.engine().update_self_model_from_outcome(
            tool_id=self.tool_id,
            result=result,
            error=error,
        )

        return envelope

    async def run(
        self,
        params: dict,
        ctx: Any,
        actor_id: str | None = None,
        session_id: str | None = None,
    ) -> EmbodiedToolEnvelope:
        """
        Full embodied tool execution pipeline.

        Returns EmbodiedToolEnvelope — not raw result.

        This is the main entry point called by the MCP server.
        """
        start_time = time.time()
        actor_id = actor_id or getattr(ctx, "actor_id", None)
        session_id = session_id or getattr(ctx, "session_id", None)

        # Stage 1: Preflight
        decision = await self.preflight(params, actor_id, session_id)

        if not decision.can_proceed:
            # Tool is held or void — build envelope without execution
            latency_ms = (time.time() - start_time) * 1000
            return await self.postflight(
                params=params,
                actor_id=actor_id,
                session_id=session_id,
                decision=decision,
                result={},
                latency_ms=latency_ms,
                error=None,
                confidence=0.0,
                reasoning_summary=decision.reason,
            )

        # Stage 2: Execute
        try:
            result = await self.execute(params, ctx)
            error = None
        except Exception as e:
            result = {}
            error = str(e)
            logger.warning(f"Tool {self.tool_id} execution error: {e}")

        latency_ms = (time.time() - start_time) * 1000

        # Stage 3: Postflight
        envelope = await self.postflight(
            params=params,
            actor_id=actor_id,
            session_id=session_id,
            decision=decision,
            result=result,
            latency_ms=latency_ms,
            error=error,
            confidence=0.5,  # TODO: extract from result
            reasoning_summary=(
                "Tool executed successfully" if error is None else f"Tool error: {error}"
            ),
        )

        return envelope


# ── Pre-built manifests for arifOS canonical tools ────────────────────────────

ARIFOS_TOOL_CHARTERS = {
    "arif_session_init": ToolManifest(
        tool_id="arif_session_init",
        tool_name="arif_session_init",
        domain="AOS",
        description="Initialize a governed session with constitutional binding",
        risk_tier="T1",
        reversibility="reversible",
        blast_radius=BlastRadius.LOW,
        required_permissions=[],
        required_floors=["F01", "F11", "F12"],
    ),
    "arif_mind_reason": ToolManifest(
        tool_id="arif_mind_reason",
        tool_name="arif_mind_reason",
        domain="AOS",
        description="Structured reasoning with constitutional awareness",
        risk_tier="T1",
        reversibility="reversible",
        blast_radius=BlastRadius.LOW,
        required_permissions=[],
        required_floors=["F02", "F07", "F08", "F10"],
    ),
    "arif_sense_observe": ToolManifest(
        tool_id="arif_sense_observe",
        tool_name="arif_sense_observe",
        domain="AOS",
        description="Reality grounding — web search, URL ingestion, compass, atlas",
        risk_tier="T1",
        reversibility="reversible",
        blast_radius=BlastRadius.LOW,
        required_permissions=[],
        required_floors=["F02", "F07"],
    ),
    "arif_evidence_fetch": ToolManifest(
        tool_id="arif_evidence_fetch",
        tool_name="arif_evidence_fetch",
        domain="AOS",
        description="Evidence-preserving web ingestion with sequential thinking",
        risk_tier="T1",
        reversibility="reversible",
        blast_radius=BlastRadius.LOW,
        required_permissions=[],
        required_floors=["F02", "F03", "F05", "F12"],
    ),
    "arif_kernel_route": ToolManifest(
        tool_id="arif_kernel_route",
        tool_name="arif_kernel_route",
        domain="AOS",
        description="Central orchestration — route intent to correct constitutional stage",
        risk_tier="T2",
        reversibility="reversible",
        blast_radius=BlastRadius.MEDIUM,
        required_permissions=["route"],
        required_floors=["F01", "F04", "F03", "F10"],
    ),
    "arif_reply_compose": ToolManifest(
        tool_id="arif_reply_compose",
        tool_name="arif_reply_compose",
        domain="AOS",
        description="Reply synthesis with F04/F06/F09 governance",
        risk_tier="T1",
        reversibility="reversible",
        blast_radius=BlastRadius.LOW,
        required_permissions=[],
        required_floors=["F04", "F06", "F09"],
    ),
    "arif_memory_recall": ToolManifest(
        tool_id="arif_memory_recall",
        tool_name="arif_memory_recall",
        domain="AOS",
        description="Governed memory — semantic recall, storage, context",
        risk_tier="T1",
        reversibility="reversible",
        blast_radius=BlastRadius.MEDIUM,
        required_permissions=[],
        required_floors=["F01", "F08"],
    ),
    "arif_heart_critique": ToolManifest(
        tool_id="arif_heart_critique",
        tool_name="arif_heart_critique",
        domain="AOS",
        description="Ethical critique, risk assessment, empathy scan",
        risk_tier="T2",
        reversibility="reversible",
        blast_radius=BlastRadius.MEDIUM,
        required_permissions=["heart"],
        required_floors=["F05", "F06", "F09"],
    ),
    "arif_gateway_connect": ToolManifest(
        tool_id="arif_gateway_connect",
        tool_name="arif_gateway_connect",
        domain="AOS",
        description="Federated A2A mesh — agent discovery and handshake",
        risk_tier="T2",
        reversibility="partial",
        blast_radius=BlastRadius.MEDIUM,
        required_permissions=["gateway"],
        required_floors=["F01", "F03"],
    ),
    "arif_ops_measure": ToolManifest(
        tool_id="arif_ops_measure",
        tool_name="arif_ops_measure",
        domain="AOS",
        description="Operational health telemetry and governance vitality metrics",
        risk_tier="T0",
        reversibility="reversible",
        blast_radius=BlastRadius.LOW,
        required_permissions=[],
        required_floors=["F04"],
    ),
    "arif_judge_deliberate": ToolManifest(
        tool_id="arif_judge_deliberate",
        tool_name="arif_judge_deliberate",
        domain="AOS",
        description="Final constitutional arbitration — SEAL, SABAR, HOLD, or VOID",
        risk_tier="T3",
        reversibility="reversible",
        blast_radius=BlastRadius.HIGH,
        required_permissions=["judge"],
        required_floors=["F11", "F13"],
        safe_compose_with=["arif_vault_seal"],
    ),
    "arif_forge_execute": ToolManifest(
        tool_id="arif_forge_execute",
        tool_name="arif_forge_execute",
        domain="AOS",
        description="Metabolic execution — build, deploy, system modification",
        risk_tier="T3",
        reversibility="partial",
        blast_radius=BlastRadius.HIGH,
        required_permissions=["forge"],
        required_floors=["F01", "F11", "F13"],
        dangerous_compose_with=["arif_mind_reason"],
    ),
    "arif_vault_seal": ToolManifest(
        tool_id="arif_vault_seal",
        tool_name="arif_vault_seal",
        domain="AOS",
        description="Immutable ledger anchoring — VAULT999 seal",
        risk_tier="T4",
        reversibility="irreversible",
        blast_radius=BlastRadius.CRITICAL,
        required_permissions=["vault"],
        required_floors=["F01", "F11", "F13"],
    ),
    "well_classify_substrate": ToolManifest(
        tool_id="well_classify_substrate",
        tool_name="well_classify_substrate",
        domain="WELL",
        description="Ω-WELL-01: Substrate classification and boundary sensing — T0 observe only",
        risk_tier="T0",
        reversibility="reversible",
        blast_radius=BlastRadius.LOW,
        required_permissions=[],
        required_floors=["F05", "F07"],
        safe_compose_with=[
            "well_trace_lineage",
            "well_detect_boundary",
            "well_measure_gradient",
            "well_assess_metabolism",
            "well_reflect_intelligence",
        ],
    ),
    "well_trace_lineage": ToolManifest(
        tool_id="well_trace_lineage",
        tool_name="well_trace_lineage",
        domain="WELL",
        description="Ω-WELL-02: Memory, trend, ledger, and vault chain tracing — T0 observe only",
        risk_tier="T0",
        reversibility="reversible",
        blast_radius=BlastRadius.LOW,
        required_permissions=[],
        required_floors=["F01", "F08"],
        safe_compose_with=[
            "well_classify_substrate",
            "well_detect_boundary",
            "well_assess_homeostasis",
            "well_reflect_intelligence",
        ],
    ),
    "well_detect_boundary": ToolManifest(
        tool_id="well_detect_boundary",
        tool_name="well_detect_boundary",
        domain="WELL",
        description=(
            "Ω-WELL-03: Boundary detection across membrane, body, machine, "
            "and federation — T0 observe"
        ),
        risk_tier="T0",
        reversibility="reversible",
        blast_radius=BlastRadius.LOW,
        required_permissions=[],
        required_floors=["F05", "F06", "F10"],
        safe_compose_with=[
            "well_classify_substrate",
            "well_measure_gradient",
            "well_assess_metabolism",
            "well_guard_dignity",
        ],
    ),
    "well_measure_gradient": ToolManifest(
        tool_id="well_measure_gradient",
        tool_name="well_measure_gradient",
        domain="WELL",
        description=(
            "Ω-WELL-04: Measure chemical, energy, pressure, attention gradients " "— T1 reversible"
        ),
        risk_tier="T1",
        reversibility="reversible",
        blast_radius=BlastRadius.LOW,
        required_permissions=[],
        required_floors=["F04", "F07"],
        safe_compose_with=[
            "well_classify_substrate",
            "well_detect_boundary",
            "well_assess_metabolism",
            "well_assess_homeostasis",
            "well_assess_livelihood",
        ],
    ),
    "well_assess_metabolism": ToolManifest(
        tool_id="well_assess_metabolism",
        tool_name="well_assess_metabolism",
        domain="WELL",
        description="Ω-WELL-05: Assess biological metabolism and system throughput — T1 reversible",
        risk_tier="T1",
        reversibility="reversible",
        blast_radius=BlastRadius.LOW,
        required_permissions=[],
        required_floors=["F05", "F06", "F07"],
        safe_compose_with=[
            "well_classify_substrate",
            "well_measure_gradient",
            "well_assess_homeostasis",
            "well_assess_livelihood",
            "well_guard_dignity",
        ],
    ),
    "well_assess_homeostasis": ToolManifest(
        tool_id="well_assess_homeostasis",
        tool_name="well_assess_homeostasis",
        domain="WELL",
        description=(
            "Ω-WELL-06: Assess regulation, stability, empathic balance under change "
            "— T1 reversible"
        ),
        risk_tier="T1",
        reversibility="reversible",
        blast_radius=BlastRadius.LOW,
        required_permissions=[],
        required_floors=["F05", "F06", "F09"],
        safe_compose_with=[
            "well_assess_metabolism",
            "well_assess_livelihood",
            "well_guard_dignity",
            "well_reflect_intelligence",
        ],
    ),
    "well_check_repair": ToolManifest(
        tool_id="well_check_repair",
        tool_name="well_check_repair",
        domain="WELL",
        description=(
            "Ω-WELL-07: Check repair, recovery, resilience, forge cycle integrity "
            "— T1 reversible"
        ),
        risk_tier="T1",
        reversibility="reversible",
        blast_radius=BlastRadius.MEDIUM,
        required_permissions=[],
        required_floors=["F01", "F04", "F08"],
        safe_compose_with=[
            "well_assess_homeostasis",
            "well_assess_reliability",
            "well_reflect_intelligence",
        ],
    ),
    "well_validate_vitality": ToolManifest(
        tool_id="well_validate_vitality",
        tool_name="well_validate_vitality",
        domain="WELL",
        description=(
            "Ω-WELL-08: Validate vitality, readiness, NIAT, floor compliance " "— T1 reversible"
        ),
        risk_tier="T1",
        reversibility="reversible",
        blast_radius=BlastRadius.MEDIUM,
        required_permissions=[],
        required_floors=["F05", "F06", "F11"],
        safe_compose_with=[
            "well_assess_metabolism",
            "well_assess_homeostasis",
            "well_assess_livelihood",
            "well_guard_dignity",
            "well_anchor_evidence",
        ],
    ),
    "well_assess_livelihood": ToolManifest(
        tool_id="well_assess_livelihood",
        tool_name="well_assess_livelihood",
        domain="WELL",
        description=(
            "Ω-WELL-09: Assess human wellness, role, dignity, support, meaning " "— T1 reversible"
        ),
        risk_tier="T1",
        reversibility="reversible",
        blast_radius=BlastRadius.LOW,
        required_permissions=[],
        required_floors=["F05", "F06", "F07"],
        safe_compose_with=[
            "well_assess_metabolism",
            "well_assess_homeostasis",
            "well_guard_dignity",
            "well_validate_vitality",
        ],
    ),
    "well_assess_reliability": ToolManifest(
        tool_id="well_assess_reliability",
        tool_name="well_assess_reliability",
        domain="WELL",
        description=(
            "Ω-WELL-10: Assess machine, tool, institution, operational reliability "
            "— T1 reversible"
        ),
        risk_tier="T1",
        reversibility="reversible",
        blast_radius=BlastRadius.MEDIUM,
        required_permissions=[],
        required_floors=["F04", "F08"],
        safe_compose_with=[
            "well_check_repair",
            "well_reflect_intelligence",
            "well_anchor_evidence",
        ],
    ),
    "well_reflect_intelligence": ToolManifest(
        tool_id="well_reflect_intelligence",
        tool_name="well_reflect_intelligence",
        domain="WELL",
        description=(
            "Ω-WELL-11: Reflect cognition, reasoning, adaptation, coherence, "
            "routing — T0 observe"
        ),
        risk_tier="T0",
        reversibility="reversible",
        blast_radius=BlastRadius.LOW,
        required_permissions=[],
        required_floors=["F07", "F08"],
        safe_compose_with=[
            "well_classify_substrate",
            "well_detect_boundary",
            "well_assess_homeostasis",
            "well_assess_reliability",
            "well_guard_dignity",
        ],
    ),
    "well_guard_dignity": ToolManifest(
        tool_id="well_guard_dignity",
        tool_name="well_guard_dignity",
        domain="WELL",
        description=(
            "Ω-WELL-12: Guard soul, personhood, meaning, symbolic boundaries " "— T2 consequential"
        ),
        risk_tier="T2",
        reversibility="reversible",
        blast_radius=BlastRadius.MEDIUM,
        required_permissions=[],
        required_floors=["F05", "F06", "F09", "F10"],
        safe_compose_with=[
            "well_assess_metabolism",
            "well_assess_homeostasis",
            "well_assess_livelihood",
            "well_validate_vitality",
        ],
        dangerous_compose_with=[
            "well_anchor_evidence",
        ],
    ),
    "well_anchor_evidence": ToolManifest(
        tool_id="well_anchor_evidence",
        tool_name="well_anchor_evidence",
        domain="WELL",
        description="Ω-WELL-13: Anchor evidence to VAULT999 — T2 irreversible once sealed",
        risk_tier="T2",
        reversibility="partial",
        blast_radius=BlastRadius.HIGH,
        required_permissions=["vault"],
        required_floors=["F01", "F11", "F13"],
        safe_compose_with=[
            "well_classify_substrate",
            "well_detect_boundary",
            "well_assess_metabolism",
            "well_validate_vitality",
            "well_assess_reliability",
        ],
        dangerous_compose_with=[
            "well_guard_dignity",
            "well_assess_homeostasis",
        ],
    ),
    "wealth_health_check": ToolManifest(
        tool_id="wealth_health_check",
        tool_name="wealth_health_check",
        domain="WEALTH",
        description=(
            "Pre-flight gate — verify WEALTH MCP is alive, authenticated, "
            "schema-valid, and constitutionally aligned before any computation"
        ),
        risk_tier="T0",
        reversibility="reversible",
        blast_radius=BlastRadius.LOW,
        required_permissions=[],
        required_floors=["F01", "F04"],
    ),
    "wealth_sense_ingest": ToolManifest(
        tool_id="wealth_sense_ingest",
        tool_name="wealth_sense_ingest",
        domain="WEALTH",
        description=(
            "Reality intake — fetch data, snapshot conditions, check source health, "
            "reconcile divergence. Evidence before reasoning (F02 TRUTH)"
        ),
        risk_tier="T0",
        reversibility="reversible",
        blast_radius=BlastRadius.LOW,
        required_permissions=[],
        required_floors=["F02", "F03", "F07"],
        safe_compose_with=[
            "wealth_truth_validate",
            "wealth_present_expect",
            "wealth_future_value",
        ],
    ),
    "wealth_present_expect": ToolManifest(
        tool_id="wealth_present_expect",
        tool_name="wealth_present_expect",
        domain="WEALTH",
        description=(
            "Expected Monetary Value — probability-weighted outcomes under "
            "defined scenarios. Forces explicit probability and payoff."
        ),
        risk_tier="T1",
        reversibility="reversible",
        blast_radius=BlastRadius.LOW,
        required_permissions=[],
        required_floors=["F02", "F07", "F08"],
        safe_compose_with=[
            "wealth_truth_validate",
            "wealth_future_value",
            "wealth_future_simulate",
            "wealth_survival_liquidity",
        ],
    ),
    "wealth_future_value": ToolManifest(
        tool_id="wealth_future_value",
        tool_name="wealth_future_value",
        domain="WEALTH",
        description=(
            "Time-discounted value — NPV, IRR, PI, payback, terminal value. "
            "Time-value witness: future money must survive discounting."
        ),
        risk_tier="T1",
        reversibility="reversible",
        blast_radius=BlastRadius.LOW,
        required_permissions=[],
        required_floors=["F02", "F04", "F08"],
        safe_compose_with=[
            "wealth_truth_validate",
            "wealth_present_expect",
            "wealth_future_simulate",
            "wealth_survival_liquidity",
            "wealth_rule_enforce",
        ],
    ),
    "wealth_future_simulate": ToolManifest(
        tool_id="wealth_future_simulate",
        tool_name="wealth_future_simulate",
        domain="WEALTH",
        description=(
            "Stochastic simulation — Monte Carlo P10/P50/P90, downside probability, "
            "tail risk. Future humility: distribution not point estimate."
        ),
        risk_tier="T1",
        reversibility="reversible",
        blast_radius=BlastRadius.MEDIUM,
        required_permissions=[],
        required_floors=["F02", "F07", "F08"],
        safe_compose_with=[
            "wealth_truth_validate",
            "wealth_present_expect",
            "wealth_future_value",
            "wealth_survival_liquidity",
            "wealth_info_value",
        ],
    ),
    "wealth_survival_liquidity": ToolManifest(
        tool_id="wealth_survival_liquidity",
        tool_name="wealth_survival_liquidity",
        domain="WEALTH",
        description=(
            "Liquidity survival — cashflow, burn rate, runway, triage. "
            "Survival floor: profitable path that dies before payoff is invalid."
        ),
        risk_tier="T2",
        reversibility="reversible",
        blast_radius=BlastRadius.MEDIUM,
        required_permissions=[],
        required_floors=["F01", "F04", "F05"],
        safe_compose_with=[
            "wealth_sense_ingest",
            "wealth_truth_validate",
            "wealth_rule_enforce",
        ],
    ),
    "wealth_survival_leverage": ToolManifest(
        tool_id="wealth_survival_leverage",
        tool_name="wealth_survival_leverage",
        domain="WEALTH",
        description=(
            "Structural load — DSCR, leverage ratio, balance sheet resilience. "
            "Load-bearing test: do not allocate into structures that cannot carry stress."
        ),
        risk_tier="T2",
        reversibility="reversible",
        blast_radius=BlastRadius.MEDIUM,
        required_permissions=[],
        required_floors=["F01", "F04", "F05", "F06"],
        safe_compose_with=[
            "wealth_survival_liquidity",
            "wealth_truth_validate",
            "wealth_rule_enforce",
        ],
    ),
    "wealth_info_value": ToolManifest(
        tool_id="wealth_info_value",
        tool_name="wealth_info_value",
        domain="WEALTH",
        description=(
            "Expected Value of Information — EVOI before spending on data, studies, "
            "seismic, due diligence. Know-before-spend gate."
        ),
        risk_tier="T1",
        reversibility="reversible",
        blast_radius=BlastRadius.LOW,
        required_permissions=[],
        required_floors=["F02", "F07", "F08"],
        safe_compose_with=[
            "wealth_truth_validate",
            "wealth_present_expect",
            "wealth_future_simulate",
        ],
    ),
    "wealth_truth_validate": ToolManifest(
        tool_id="wealth_truth_validate",
        tool_name="wealth_truth_validate",
        domain="WEALTH",
        description=(
            "Epistemic integrity — schema, data quality, correlation, entropy. "
            "Truth gate: bad evidence cannot command good capital (F02)."
        ),
        risk_tier="T1",
        reversibility="reversible",
        blast_radius=BlastRadius.LOW,
        required_permissions=[],
        required_floors=["F02", "F03", "F08"],
        safe_compose_with=[
            "wealth_sense_ingest",
            "wealth_present_expect",
            "wealth_future_value",
            "wealth_future_simulate",
        ],
    ),
    "wealth_rule_enforce": ToolManifest(
        tool_id="wealth_rule_enforce",
        tool_name="wealth_rule_enforce",
        domain="WEALTH",
        description=(
            "Constitutional floors + policy constraints — F1-F13 audit, breach detection, "
            "required mitigations. Return does not outrank rule."
        ),
        risk_tier="T2",
        reversibility="reversible",
        blast_radius=BlastRadius.HIGH,
        required_permissions=[],
        required_floors=["F01", "F04", "F11", "F13"],
        safe_compose_with=[
            "wealth_truth_validate",
            "wealth_allocate_optimize",
            "wealth_future_steward",
        ],
    ),
    "wealth_allocate_optimize": ToolManifest(
        tool_id="wealth_allocate_optimize",
        tool_name="wealth_allocate_optimize",
        domain="WEALTH",
        description=(
            "Capital allocation — rank or optimize under constraints. "
            "Decision synthesis after survival, truth, and rule gates pass."
        ),
        risk_tier="T2",
        reversibility="partial",
        blast_radius=BlastRadius.HIGH,
        required_permissions=[],
        required_floors=["F01", "F05", "F06", "F11"],
        safe_compose_with=[
            "wealth_truth_validate",
            "wealth_rule_enforce",
            "wealth_game_coordinate",
        ],
    ),
    "wealth_game_coordinate": ToolManifest(
        tool_id="wealth_game_coordinate",
        tool_name="wealth_game_coordinate",
        domain="WEALTH",
        description=(
            "Multi-agent coordination — equilibrium, incentives, Shapley, Nash. "
            "Coordination witness: good allocation must remain stable among actors."
        ),
        risk_tier="T1",
        reversibility="reversible",
        blast_radius=BlastRadius.MEDIUM,
        required_permissions=[],
        required_floors=["F05", "F06", "F08"],
        safe_compose_with=[
            "wealth_allocate_optimize",
            "wealth_rule_enforce",
        ],
    ),
    "wealth_past_record": ToolManifest(
        tool_id="wealth_past_record",
        tool_name="wealth_past_record",
        domain="WEALTH",
        description=(
            "VAULT999 ledger — record sessions, events, transactions, snapshots. "
            "Past witness: decisions become auditable memory. F01 irreversible guard."
        ),
        risk_tier="T2",
        reversibility="partial",
        blast_radius=BlastRadius.HIGH,
        required_permissions=["vault"],
        required_floors=["F01", "F11", "F13"],
        safe_compose_with=[
            "wealth_allocate_optimize",
            "wealth_rule_enforce",
            "wealth_truth_validate",
        ],
        dangerous_compose_with=[
            "wealth_allocate_optimize",
        ],
    ),
    "wealth_future_steward": ToolManifest(
        tool_id="wealth_future_steward",
        tool_name="wealth_future_steward",
        domain="WEALTH",
        description=(
            "Long-horizon stewardship — planetary boundaries, civilization continuity, "
            "intergenerational burden. Future witness: do not convert present gain "
            "into future collapse."
        ),
        risk_tier="T2",
        reversibility="reversible",
        blast_radius=BlastRadius.HIGH,
        required_permissions=[],
        required_floors=["F01", "F05", "F06", "F08"],
        safe_compose_with=[
            "wealth_truth_validate",
            "wealth_rule_enforce",
            "wealth_allocate_optimize",
        ],
    ),
}


def register_all_arifos_tools() -> None:
    """Register all arifOS canonical tools in the self-model."""
    model = get_tool_self_model()
    for _tool_id, manifest in ARIFOS_TOOL_CHARTERS.items():
        model.register(manifest)
    logger.info(f"Registered {len(ARIFOS_TOOL_CHARTERS)} arifOS canonical tools")


__all__ = [
    "register_embodied_tool",
    "EmbodiedTool",
    "ARIFOS_TOOL_CHARTERS",
    "register_all_arifos_tools",
]
