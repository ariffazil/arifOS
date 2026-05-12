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
    CognitiveAxis,
    PredictionRecord,
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

    # Current prediction for this tool invocation (set in run(), used in postflight)
    _current_prediction: PredictionRecord | None = None

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

    def make_prediction(
        self,
        params: dict,
        expected_outcome: str = "SEAL",
        confidence: float = 0.7,
        falsification_condition: str = "VOID or HOLD returned",
    ) -> PredictionRecord:
        """
        Create a PredictionRecord before tool execution.

        The agent must stake a claim about what reality will return.
        This is the core of the disequilibrium loop.

        Args:
            params: Tool parameters (used to infer expected outcome)
            expected_outcome: What the agent expects to happen
            confidence: How confident the agent is (0.0-1.0)
            falsification_condition: What would prove the agent's model wrong

        Returns:
            PredictionRecord to be passed through postflight
        """
        risk_map = {"T0": 0.9, "T1": 0.85, "T2": 0.7, "T3": 0.5, "T4": 0.3}
        risk_conf = risk_map.get(self.risk_tier, 0.7)

        if params.get("mode") == "health":
            expected_outcome = "healthy"
            falsification_condition = "unhealthy or error"
            confidence = 0.95
        elif confidence == 0.7 and risk_conf < 0.7:
            confidence = risk_conf
            falsification_condition = f"error or unexpected {self.risk_tier} outcome"

        record = PredictionRecord(
            predicted_outcome=expected_outcome,
            confidence=confidence,
            falsification_condition=falsification_condition,
        )
        self._current_prediction = record
        return record

    def resolve_prediction(
        self,
        prediction: PredictionRecord | None,
        actual_outcome: str = "OK",
        model_importance: float = 1.0,
    ) -> dict[str, Any]:
        """
        Resolve a prediction against actual outcome.

        Returns dict with delta_surprise, triggered_surprise for logging.
        """
        if prediction is None:
            return {"delta_surprise": 0.0, "triggered_surprise": False}
        delta = prediction.compute_delta_surprise(
            actual_outcome=actual_outcome,
            model_importance=model_importance,
        )
        return {
            "delta_surprise": delta,
            "triggered_surprise": prediction.triggered_surprise,
        }

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
        # Includes prediction comparison for disequilibrium detection
        self.engine().update_self_model_from_outcome(
            tool_id=self.tool_id,
            result=result,
            error=error,
            prediction=self._current_prediction,
        )

        # Clear the prediction for the next invocation
        self._current_prediction = None

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

        # Stage 1: Preflight — includes making a prediction about the outcome
        decision = await self.preflight(params, actor_id, session_id)

        # Make a prediction before execution (disequilibrium pre-commitment)
        self.make_prediction(
            params=params,
            expected_outcome=decision.status if decision.can_proceed else "HOLD",
            confidence=0.7,
            falsification_condition=f"!{decision.status}",
        )

        if not decision.can_proceed:
            # Update prediction with the HOLD outcome (prediction resolved)
            self.resolve_prediction(
                prediction=self._current_prediction,
                actual_outcome=decision.status,
                model_importance=1.0,
            )

            # Tool is held or void — build envelope without execution
            latency_ms = (time.time() - start_time) * 1000
            result = {}
        else:
            # Stage 2: Execute
            try:
                result = await self.execute(params, ctx)
                error = None
            except Exception as e:
                result = {}
                error = str(e)
                logger.warning(f"Tool {self.tool_id} execution error: {e}")

                # Update prediction with error
                self.resolve_prediction(
                    prediction=self._current_prediction,
                    actual_outcome="ERROR",
                    model_importance=2.0,
                )

        latency_ms = (time.time() - start_time) * 1000

        # Stage 3: Postflight (prediction is passed to self-model update inside postflight)
        envelope = await self.postflight(
            params=params,
            actor_id=actor_id,
            session_id=session_id,
            decision=decision,
            result=result,
            latency_ms=latency_ms,
            error=error if not decision.can_proceed else (error if "error" in dir() else None),
            confidence=0.5,
            reasoning_summary=(
                decision.reason
                if not decision.can_proceed
                else ("Tool executed successfully" if error is None else f"Tool error: {error}")
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
        cognitive_axis=CognitiveAxis.IDENTITY,
        expose=True,
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
        cognitive_axis=CognitiveAxis.REASON,
        expose=True,
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
        cognitive_axis=CognitiveAxis.OBSERVE,
        expose=True,
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
        cognitive_axis=CognitiveAxis.VERIFY,
        expose=True,
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
        cognitive_axis=CognitiveAxis.BOUNDARY,
        expose=True,
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
        cognitive_axis=CognitiveAxis.REFLECT,
        expose=True,
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
        cognitive_axis=CognitiveAxis.TRACE,
        expose=True,
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
        cognitive_axis=CognitiveAxis.CRITIQUE,
        expose=True,
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
        cognitive_axis=CognitiveAxis.BOUNDARY,
        expose=True,
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
        cognitive_axis=CognitiveAxis.VITALITY,
        expose=True,
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
        cognitive_axis=CognitiveAxis.JUDGE,
        expose=True,
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
        cognitive_axis=CognitiveAxis.EXECUTE,
        expose=True,
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
        cognitive_axis=CognitiveAxis.SEAL,
        expose=True,
    ),
    "well_classify_substrate": ToolManifest(
        tool_id="well_classify_substrate",
        tool_name="well_classify_substrate",
        domain="WELL",
        description="Ω-WELL-01: Substrate classification and boundary sensing",
        risk_tier="T0",
        reversibility="reversible",
        blast_radius=BlastRadius.LOW,
        required_permissions=[],
        required_floors=["F05", "F07"],
        safe_compose_with=["well_trace_lineage", "well_detect_boundary", "well_measure_gradient", "well_assess_metabolism", "well_reflect_intelligence"],
        cognitive_axis=CognitiveAxis.IDENTITY,
        expose=True,
    ),
    "well_trace_lineage": ToolManifest(
        tool_id="well_trace_lineage",
        tool_name="well_trace_lineage",
        domain="WELL",
        description="Ω-WELL-02: Memory, trend, ledger, and vault chain tracing",
        risk_tier="T0",
        reversibility="reversible",
        blast_radius=BlastRadius.LOW,
        required_permissions=[],
        required_floors=["F01", "F08"],
        safe_compose_with=["well_classify_substrate", "well_detect_boundary", "well_assess_homeostasis", "well_reflect_intelligence"],
        cognitive_axis=CognitiveAxis.TRACE,
        expose=True,
    ),
    "well_detect_boundary": ToolManifest(
        tool_id="well_detect_boundary",
        tool_name="well_detect_boundary",
        domain="WELL",
        description="Ω-WELL-03: Boundary detection across membrane, body, machine, federation",
        risk_tier="T0",
        reversibility="reversible",
        blast_radius=BlastRadius.LOW,
        required_permissions=[],
        required_floors=["F05", "F06", "F10"],
        safe_compose_with=["well_classify_substrate", "well_measure_gradient", "well_assess_metabolism", "well_guard_dignity"],
        cognitive_axis=CognitiveAxis.BOUNDARY,
        expose=True,
    ),
    "well_measure_gradient": ToolManifest(
        tool_id="well_measure_gradient",
        tool_name="well_measure_gradient",
        domain="WELL",
        description="Ω-WELL-04: Measure chemical, energy, pressure, attention gradients",
        risk_tier="T1",
        reversibility="reversible",
        blast_radius=BlastRadius.LOW,
        required_permissions=[],
        required_floors=["F04", "F07"],
        safe_compose_with=["well_classify_substrate", "well_detect_boundary", "well_assess_metabolism", "well_assess_homeostasis", "well_assess_livelihood"],
        cognitive_axis=CognitiveAxis.OBSERVE,
        expose=True,
    ),
    "well_assess_metabolism": ToolManifest(
        tool_id="well_assess_metabolism",
        tool_name="well_assess_metabolism",
        domain="WELL",
        description="Ω-WELL-05: Assess biological metabolism and system throughput",
        risk_tier="T1",
        reversibility="reversible",
        blast_radius=BlastRadius.LOW,
        required_permissions=[],
        required_floors=["F05", "F06", "F07"],
        safe_compose_with=["well_classify_substrate", "well_measure_gradient", "well_assess_homeostasis", "well_assess_livelihood", "well_guard_dignity"],
        cognitive_axis=CognitiveAxis.VITALITY,
        expose=True,
    ),
    "well_assess_homeostasis": ToolManifest(
        tool_id="well_assess_homeostasis",
        tool_name="well_assess_homeostasis",
        domain="WELL",
        description="Ω-WELL-06: Assess regulation, stability, empathic balance under change",
        risk_tier="T1",
        reversibility="reversible",
        blast_radius=BlastRadius.LOW,
        required_permissions=[],
        required_floors=["F05", "F06", "F09"],
        safe_compose_with=["well_assess_metabolism", "well_assess_livelihood", "well_guard_dignity", "well_reflect_intelligence"],
        cognitive_axis=CognitiveAxis.VITALITY,
        expose=True,
    ),
    "well_check_repair": ToolManifest(
        tool_id="well_check_repair",
        tool_name="well_check_repair",
        domain="WELL",
        description="Ω-WELL-07: Check repair, recovery, resilience, forge cycle integrity",
        risk_tier="T1",
        reversibility="reversible",
        blast_radius=BlastRadius.MEDIUM,
        required_permissions=[],
        required_floors=["F01", "F04", "F08"],
        safe_compose_with=["well_assess_homeostasis", "well_assess_reliability", "well_reflect_intelligence"],
        cognitive_axis=CognitiveAxis.REPAIR,
        expose=True,
    ),
    "well_validate_vitality": ToolManifest(
        tool_id="well_validate_vitality",
        tool_name="well_validate_vitality",
        domain="WELL",
        description="Ω-WELL-08: Validate vitality, readiness, NIAT, floor compliance",
        risk_tier="T1",
        reversibility="reversible",
        blast_radius=BlastRadius.MEDIUM,
        required_permissions=[],
        required_floors=["F05", "F06", "F11"],
        safe_compose_with=["well_assess_metabolism", "well_assess_homeostasis", "well_assess_livelihood", "well_guard_dignity", "well_anchor_evidence"],
        cognitive_axis=CognitiveAxis.JUDGE,
        expose=True,
    ),
    "well_assess_livelihood": ToolManifest(
        tool_id="well_assess_livelihood",
        tool_name="well_assess_livelihood",
        domain="WELL",
        description="Ω-WELL-09: Assess human wellness, role, dignity, support, meaning",
        risk_tier="T1",
        reversibility="reversible",
        blast_radius=BlastRadius.LOW,
        required_permissions=[],
        required_floors=["F05", "F06", "F07"],
        safe_compose_with=["well_assess_metabolism", "well_assess_homeostasis", "well_guard_dignity", "well_validate_vitality"],
        cognitive_axis=CognitiveAxis.VITALITY,
        expose=True,
    ),
    "well_assess_reliability": ToolManifest(
        tool_id="well_assess_reliability",
        tool_name="well_assess_reliability",
        domain="WELL",
        description="Ω-WELL-10: Assess machine, tool, institution, operational reliability",
        risk_tier="T1",
        reversibility="reversible",
        blast_radius=BlastRadius.MEDIUM,
        required_permissions=[],
        required_floors=["F04", "F08"],
        safe_compose_with=["well_check_repair", "well_reflect_intelligence", "well_anchor_evidence"],
        cognitive_axis=CognitiveAxis.VITALITY,
        expose=True,
    ),
    "well_reflect_intelligence": ToolManifest(
        tool_id="well_reflect_intelligence",
        tool_name="well_reflect_intelligence",
        domain="WELL",
        description="Ω-WELL-11: Reflect cognition, reasoning, adaptation, coherence, routing",
        risk_tier="T0",
        reversibility="reversible",
        blast_radius=BlastRadius.LOW,
        required_permissions=[],
        required_floors=["F07", "F08"],
        safe_compose_with=["well_classify_substrate", "well_detect_boundary", "well_assess_homeostasis", "well_assess_reliability", "well_guard_dignity"],
        cognitive_axis=CognitiveAxis.REFLECT,
        expose=True,
    ),
    "well_guard_dignity": ToolManifest(
        tool_id="well_guard_dignity",
        tool_name="well_guard_dignity",
        domain="WELL",
        description="Ω-WELL-12: Guard soul, personhood, meaning, symbolic boundaries",
        risk_tier="T2",
        reversibility="reversible",
        blast_radius=BlastRadius.MEDIUM,
        required_permissions=[],
        required_floors=["F05", "F06", "F09", "F10"],
        safe_compose_with=["well_assess_metabolism", "well_assess_homeostasis", "well_assess_livelihood", "well_validate_vitality"],
        dangerous_compose_with=["well_anchor_evidence"],
        cognitive_axis=CognitiveAxis.CRITIQUE,
        expose=True,
    ),
    "well_anchor_evidence": ToolManifest(
        tool_id="well_anchor_evidence",
        tool_name="well_anchor_evidence",
        domain="WELL",
        description="Ω-WELL-13: Anchor evidence to VAULT999",
        risk_tier="T2",
        reversibility="partial",
        blast_radius=BlastRadius.HIGH,
        required_permissions=["vault"],
        required_floors=["F01", "F11", "F13"],
        safe_compose_with=["well_classify_substrate", "well_detect_boundary", "well_assess_metabolism", "well_validate_vitality", "well_assess_reliability"],
        dangerous_compose_with=["well_guard_dignity", "well_assess_homeostasis"],
        cognitive_axis=CognitiveAxis.SEAL,
        expose=True,
    ),
    "mcp_health_check": ToolManifest(
        tool_id="mcp_health_check",
        tool_name="mcp_health_check",
        domain="WEALTH",
        description="Universal health check for federation stability.",
        risk_tier="T0",
        reversibility="reversible",
        blast_radius=BlastRadius.LOW,
        required_floors=["F04"],
        cognitive_axis=CognitiveAxis.VITALITY,
        expose=False,
    ),
    "wealth_conservation_capital": ToolManifest(
        tool_id="wealth_conservation_capital",
        tool_name="wealth_conservation_capital",
        domain="WEALTH",
        description="Ω-WEALTH-01: Conservation — capital stock reality.",
        risk_tier="T1",
        reversibility="reversible",
        blast_radius=BlastRadius.LOW,
        required_floors=["F02", "F08"],
        cognitive_axis=CognitiveAxis.VITALITY,
        expose=False,
    ),
    "wealth_flow_liquidity": ToolManifest(
        tool_id="wealth_flow_liquidity",
        tool_name="wealth_flow_liquidity",
        domain="WEALTH",
        description="Ω-WEALTH-02: Flow — liquidity movement.",
        risk_tier="T1",
        reversibility="reversible",
        blast_radius=BlastRadius.MEDIUM,
        required_floors=["F01", "F04", "F05"],
        cognitive_axis=CognitiveAxis.VITALITY,
        expose=False,
    ),
    "wealth_gradient_price": ToolManifest(
        tool_id="wealth_gradient_price",
        tool_name="wealth_gradient_price",
        domain="WEALTH",
        description="Ω-WEALTH-03: Gradient — price pressure, spread, mispricing.",
        risk_tier="T1",
        reversibility="reversible",
        blast_radius=BlastRadius.LOW,
        required_floors=["F02", "F07"],
        cognitive_axis=CognitiveAxis.OBSERVE,
        expose=False,
    ),
    "wealth_entropy_risk": ToolManifest(
        tool_id="wealth_entropy_risk",
        tool_name="wealth_entropy_risk",
        domain="WEALTH",
        description="Ω-WEALTH-04: Entropy — uncertainty, dispersion, tail risk.",
        risk_tier="T1",
        reversibility="reversible",
        blast_radius=BlastRadius.MEDIUM,
        required_floors=["F02", "F07", "F08"],
        cognitive_axis=CognitiveAxis.CRITIQUE,
        expose=False,
    ),
    "wealth_energy_productivity": ToolManifest(
        tool_id="wealth_energy_productivity",
        tool_name="wealth_energy_productivity",
        domain="WEALTH",
        description="Ω-WEALTH-05: Energy — output per input, productivity.",
        risk_tier="T1",
        reversibility="reversible",
        blast_radius=BlastRadius.LOW,
        required_floors=["F02", "F08"],
        cognitive_axis=CognitiveAxis.REASON,
        expose=False,
    ),
    "wealth_time_discount": ToolManifest(
        tool_id="wealth_time_discount",
        tool_name="wealth_time_discount",
        domain="WEALTH",
        description="Ω-WEALTH-06: Time — NPV, IRR, payback, compounding.",
        risk_tier="T1",
        reversibility="reversible",
        blast_radius=BlastRadius.LOW,
        required_floors=["F02", "F08"],
        cognitive_axis=CognitiveAxis.REASON,
        expose=False,
    ),
    "wealth_inertia_leverage": ToolManifest(
        tool_id="wealth_inertia_leverage",
        tool_name="wealth_inertia_leverage",
        domain="WEALTH",
        description="Ω-WEALTH-07: Inertia — resistance, leverage stress, fragility.",
        risk_tier="T2",
        reversibility="reversible",
        blast_radius=BlastRadius.MEDIUM,
        required_floors=["F01", "F04", "F05"],
        cognitive_axis=CognitiveAxis.BOUNDARY,
        expose=False,
    ),
    "wealth_field_macro": ToolManifest(
        tool_id="wealth_field_macro",
        tool_name="wealth_field_macro",
        domain="WEALTH",
        description="Ω-WEALTH-08: Field — macro environment (rates, FX, energy, carbon).",
        risk_tier="T0",
        reversibility="reversible",
        blast_radius=BlastRadius.LOW,
        required_floors=["F02", "F03"],
        cognitive_axis=CognitiveAxis.OBSERVE,
        expose=False,
    ),
    "wealth_signal_information": ToolManifest(
        tool_id="wealth_signal_information",
        tool_name="wealth_signal_information",
        domain="WEALTH",
        description="Ω-WEALTH-09: Signal — information value, evidence quality.",
        risk_tier="T1",
        reversibility="reversible",
        blast_radius=BlastRadius.LOW,
        required_floors=["F02", "F03", "F07"],
        cognitive_axis=CognitiveAxis.VERIFY,
        expose=False,
    ),
    "wealth_game_coordination": ToolManifest(
        tool_id="wealth_game_coordination",
        tool_name="wealth_game_coordination",
        domain="WEALTH",
        description="Ω-WEALTH-10: Game — multi-agent incentives, bargaining.",
        risk_tier="T1",
        reversibility="reversible",
        blast_radius=BlastRadius.MEDIUM,
        required_floors=["F05", "F06", "F08"],
        cognitive_axis=CognitiveAxis.REASON,
        expose=False,
    ),
    "wealth_boundary_governance": ToolManifest(
        tool_id="wealth_boundary_governance",
        tool_name="wealth_boundary_governance",
        domain="WEALTH",
        description="Ω-WEALTH-11: Boundary — constitutional floors, maruah, stewardship.",
        risk_tier="T2",
        reversibility="reversible",
        blast_radius=BlastRadius.HIGH,
        required_floors=["F01", "F04", "F11", "F13"],
        cognitive_axis=CognitiveAxis.BOUNDARY,
        expose=False,
    ),
    "wealth_hysteresis_ledger": ToolManifest(
        tool_id="wealth_hysteresis_ledger",
        tool_name="wealth_hysteresis_ledger",
        domain="WEALTH",
        description="Ω-WEALTH-12: Hysteresis — path dependence, ledger, sealed financial memory.",
        risk_tier="T2",
        reversibility="partial",
        blast_radius=BlastRadius.HIGH,
        required_permissions=["vault"],
        required_floors=["F01", "F11", "F13"],
        cognitive_axis=CognitiveAxis.SEAL,
        expose=False,
    ),
    "wealth_system_registry_status": ToolManifest(
        tool_id="wealth_system_registry_status",
        tool_name="wealth_system_registry_status",
        domain="WEALTH",
        description="Registry truth diagnostic — intended, registered, and alias surfaces.",
        risk_tier="T0",
        reversibility="reversible",
        blast_radius=BlastRadius.LOW,
        required_floors=["F04"],
        cognitive_axis=CognitiveAxis.IDENTITY,
        expose=False,
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
