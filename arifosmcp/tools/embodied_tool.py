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

ARIFOS_TOOL_MANIFESTS = {
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
}


def register_all_arifos_tools() -> None:
    """Register all arifOS canonical tools in the self-model."""
    model = get_tool_self_model()
    for _tool_id, manifest in ARIFOS_TOOL_MANIFESTS.items():
        model.register(manifest)
    logger.info(f"Registered {len(ARIFOS_TOOL_MANIFESTS)} arifOS canonical tools")


__all__ = [
    "register_embodied_tool",
    "EmbodiedTool",
    "ARIFOS_TOOL_MANIFESTS",
    "register_all_arifos_tools",
]
